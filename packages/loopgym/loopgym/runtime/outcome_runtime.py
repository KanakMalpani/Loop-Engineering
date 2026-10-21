"""Real-outcome runtime for code-repair loops.

Score = hidden-test pass rate of the worker's patch (evaluators.test_pass_rate), nothing else:
no self-reported critique score, no per-iteration bonus. Spec fields honoured:
  workers[0].role / system_prompt -> LLM instruction argument (not user-prompt text)
  workers[0].model.temperature -> forwarded only if the client accepts it; never prompt text
  inputs -> prompt contents
  feedback_channels (source evaluators.test_runner -> workers.<id>) -> next-iteration prompt
  evaluators (needs a deterministic evaluators.test_pass_rate; otherwise score 0 / fail)
  termination_conditions (success value + consecutive, max_iterations, stall)
  cost_limits.per_iteration_usd / cumulative_usd and workers[].cost_budget_usd -> halt = fail
Hidden tests and reference fixes are never placed in a prompt or the model's working copy.
"""

from __future__ import annotations

import json
from typing import Any

from loopgym.evaluators.sandbox_tests import Fixture, test_pass_rate
from loopgym.runtime.loop_runtime import (
    LLMClient,
    LoopRuntime,
    LoopState,
    _get_quality_threshold,
    invoke_llm,
    worker_instruction,
    worker_temperature,
)

USD_PER_TOKEN = 0.000002  # same blended rate SimEnv already uses for trace cost


def _worker(spec: dict[str, Any]) -> dict[str, Any]:
    ws = spec.get("workers") or []
    return ws[0] if ws else {"id": "implementer", "role": "implementer"}


def _test_evaluator(spec: dict[str, Any]) -> dict[str, Any] | None:
    for ev in spec.get("evaluators") or []:
        if ev.get("type") == "deterministic" and ev.get("implementation") == "evaluators.test_pass_rate":
            return ev
    return None


def _success_rule(spec: dict[str, Any]) -> tuple[float, int]:
    term = spec.get("termination_conditions") or {}
    if isinstance(term, dict):
        for s in term.get("success") or []:
            if s.get("value") is not None:
                return float(s["value"]), int(s.get("consecutive", 1) or 1)
    return _get_quality_threshold(spec), 1


def _max_iterations(spec: dict[str, Any]) -> int:
    term = spec.get("termination_conditions") or {}
    if isinstance(term, dict):
        for f in term.get("failure") or []:
            if f.get("type") == "max_iterations":
                return int(f.get("value", 1))
    return 1


def _stall(spec: dict[str, Any]) -> dict[str, Any] | None:
    term = spec.get("termination_conditions") or {}
    if isinstance(term, dict):
        for s in term.get("stall") or []:
            return s
    return None


def _input_refs(worker: dict[str, Any]) -> set[str]:
    refs = set()
    for item in worker.get("inputs") or []:
        src = item.get("from", "") if isinstance(item, dict) else str(item)
        if src.startswith("inputs."):
            refs.add(src.split(".", 1)[1])
    return refs


class CodeRepairRuntime(LoopRuntime):
    def __init__(self, spec: dict[str, Any], llm: LLMClient, fixture: Fixture, **kw: Any) -> None:
        if llm is None:
            raise ValueError("CodeRepairRuntime needs an explicit LLM (never builds MockLLM)")
        super().__init__(spec, llm=llm, **kw)
        self.fixture = fixture
        self.worker = _worker(spec)
        self.worker_id = str(self.worker.get("id") or self.worker.get("role") or "implementer")
        self.test_eval = _test_evaluator(spec)
        self.quality_threshold, self.consecutive = _success_rule(spec)
        self.max_iterations = _max_iterations(spec)
        self.stall = _stall(spec)
        self.feedback_fields = self._feedback_fields()
        cl = spec.get("cost_limits") or {}
        self.cap_cumulative = cl.get("cumulative_usd")
        self.cap_iteration = cl.get("per_iteration_usd")
        self.cap_worker = self.worker.get("cost_budget_usd")
        self.prompts: list[str] = []

    def _feedback_fields(self) -> list[str] | None:
        if self.test_eval is None:
            return None
        src = f"evaluators.{self.test_eval.get('id', 'test_runner')}"
        for ch in self.spec.get("feedback_channels") or []:
            if ch.get("source") == src and ch.get("destination") == f"workers.{self.worker_id}":
                return list(ch.get("fields") or ["failure_codes", "remediation_hints"])
        return None

    # ---- prompt -------------------------------------------------------------------------
    def build_prompt(self, state: LoopState) -> str:
        refs = _input_refs(self.worker)
        parts = [f"Objective: {self.spec.get('objective', '').strip()}"]
        if refs:
            if "bug_description" in refs:
                parts.append(f"Bug description:\n{self.fixture.bug_description}")
            # the module under repair is the subject of any task input (bug_description or repo_snapshot)
            parts.append(
                f"Module under repair ({self.fixture.module_name}):\n```\n{self.fixture.source}```"
            )
        parts.append("Return the full corrected module in one fenced code block.")
        if state.iteration > 1 and self.feedback_fields is not None and state.history:
            last = state.history[-1]
            ev = last.get("evaluation") or {}
            fb = {k: ev.get(k) for k in self.feedback_fields if k in ev}
            parts.append(f"Your previous reply:\n{last.get('output', '')}")
            parts.append(f"Feedback from {self.test_eval.get('id')} on that reply:\n"
                         f"{json.dumps(fb, indent=2)}\nRevise accordingly.")
        return "\n\n".join(parts)

    # ---- evaluation ---------------------------------------------------------------------
    def _evaluate(self, state: LoopState, prompt: str = "") -> tuple[float, str]:
        if self.test_eval is None:
            ev = {"test_pass_rate": 0.0, "score": 0.0,
                  "failure_codes": ["fail.no_real_outcome_evaluator"]}
        else:
            ev = test_pass_rate(self.fixture, state.output)
        state.metadata["last_evaluation"] = ev
        return float(ev["score"]), json.dumps({k: ev.get(k) for k in
                                                ("test_pass_rate", "failure_codes", "failures")})

    def _cost(self, prompt: str, output: str, tokens_delta: int) -> tuple[float, int]:
        toks = tokens_delta if tokens_delta > 0 else (len(prompt) + len(output)) // 4
        return toks * USD_PER_TOKEN, toks

    def step_once(self, state: LoopState, user_input: str = "") -> LoopState:
        if state.terminated:
            return state
        state.iteration += 1
        prompt = self.build_prompt(state)
        self.prompts.append(prompt)
        before = int(getattr(self.llm, "tokens_used", 0) or 0)
        output = invoke_llm(
            self.llm,
            prompt,
            role=worker_instruction(self.worker),
            temperature=worker_temperature(self.worker),
        )
        cost, toks = self._cost(prompt, output, int(getattr(self.llm, "tokens_used", 0) or 0) - before)
        spent = state.metadata.get("cost_usd", 0.0) + cost
        state.metadata["cost_usd"] = spent
        state.metadata["tokens"] = state.metadata.get("tokens", 0) + toks
        state.output = output
        record: dict[str, Any] = {"iteration": state.iteration, "output": output,
                                  "cost_usd": round(cost, 6), "tokens": toks}
        over = None
        if self.cap_iteration is not None and cost > float(self.cap_iteration):
            over = f"per_iteration_usd ({cost:.5f} > {self.cap_iteration})"
        elif self.cap_cumulative is not None and spent > float(self.cap_cumulative):
            over = f"cumulative_usd ({spent:.5f} > {self.cap_cumulative})"
        elif self.cap_worker is not None and spent > float(self.cap_worker):
            over = f"worker cost_budget_usd ({spent:.5f} > {self.cap_worker})"
        if over:
            state.quality_score = 0.0
            record.update(quality_score=0.0, feedback="cost cap exceeded", evaluation={})
            state.history.append(record)
            state.terminated, state.termination_reason = True, f"cost_limit {over}: fail"
            state.metadata["cost_halt"] = True
            return state
        state.quality_score, fb = self._evaluate(state)
        record.update(quality_score=state.quality_score, feedback=fb,
                      evaluation=state.metadata["last_evaluation"])
        state.history.append(record)
        if self.on_iteration:
            self.on_iteration(state)
        self._check_termination(state)
        return state

    def _check_termination(self, state: LoopState) -> bool:
        if self.test_eval is None:
            state.terminated = True
            state.termination_reason = "no deterministic test evaluator: no real-outcome score (fail)"
            return True
        scores = [h.get("quality_score", 0.0) for h in state.history]
        tail = scores[-self.consecutive:]
        if len(tail) == self.consecutive and all(s >= self.quality_threshold for s in tail):
            state.terminated = True
            state.termination_reason = f"success ({state.quality_score:.2f} >= {self.quality_threshold}" \
                                       f" x{self.consecutive})"
            return True
        if state.iteration >= self.max_iterations:
            state.terminated = True
            state.termination_reason = f"max_iterations ({self.max_iterations})"
            return True
        if self.stall and len(scores) > int(self.stall.get("window_iterations", 3)):
            w = int(self.stall.get("window_iterations", 3))
            if max(scores[-w:]) - scores[-w - 1] < float(self.stall.get("min_improvement", 0.0)):
                state.terminated = True
                state.termination_reason = f"stall ({w} iterations without improvement)"
                return True
        return False

    def is_success(self, state: LoopState) -> bool:
        return (not state.metadata.get("cost_halt") and self.test_eval is not None
                and state.quality_score >= self.quality_threshold)

    def run(self, user_input: str = ""):  # type: ignore[override]
        raise NotImplementedError("use SimEnv/LiveEnv.run_episode")
