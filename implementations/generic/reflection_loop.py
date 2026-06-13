"""Level-2 reflective loop: act → evaluate → reflect → revise."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, _worker_ids, load_lss_spec
except ImportError:
    from loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, _worker_ids, load_lss_spec


@dataclass
class ReflectionConfig:
    critique_depth: int = 1
    min_improvement_delta: float = 0.05


class ReflectionLoop(LoopRuntime):
    """Reflective loop with explicit critique and revision phases."""

    def __init__(
        self,
        spec: dict[str, Any],
        llm: MockLLM | None = None,
        config: ReflectionConfig | None = None,
    ) -> None:
        super().__init__(spec, llm=llm)
        self.config = config or ReflectionConfig()

    def _reflect(self, state: LoopState) -> str:
        critique = self.llm.complete(
            f"Critique the following output for objective '{self.spec.get('objective')}':\n"
            f"{state.output}\n"
            f"Provide specific improvements.",
            role="critic",
        )
        reflection = self.llm.complete(
            f"Reflect on critique and plan revision:\n{critique}",
            role="critic",
        )
        return f"{critique}\n\nReflection plan: {reflection}"

    def _act(self, state: LoopState, user_input: str) -> str:
        if state.iteration == 0:
            return self.llm.complete(
                f"Objective: {self.spec.get('objective')}\nTask: {user_input}",
                role="implementer",
            )
        feedback = state.history[-1].get("reflection", "") if state.history else ""
        return self.llm.complete(
            f"Revise based on reflection:\n{feedback}\nPrior:\n{state.output}",
            role="implementer",
        )

    def run(self, user_input: str = "") -> LoopResult:
        start_quality = 0.0
        state = LoopState()
        tokens_before = getattr(self.llm, "tokens_used", 0)

        if not user_input:
            inputs = self.spec.get("inputs") or []
            user_input = inputs[0].get("name", "task") if inputs else "task"

        import time

        start = time.perf_counter()

        while not state.terminated:
            state.iteration += 1
            state.output = self._act(state, user_input)
            score, eval_feedback = self._evaluate(state, user_input)
            reflection = self._reflect(state)
            prev = state.quality_score
            state.quality_score = max(score, prev + self.config.min_improvement_delta)
            state.history.append(
                {
                    "iteration": state.iteration,
                    "output": state.output,
                    "quality_score": state.quality_score,
                    "evaluation": eval_feedback,
                    "reflection": reflection,
                }
            )
            if self.on_iteration:
                self.on_iteration(state)
            if state.quality_score >= self.quality_threshold:
                state.terminated = True
                state.termination_reason = "quality_threshold_met"
            elif state.iteration >= self.max_iterations:
                state.terminated = True
                state.termination_reason = "max_iterations"

        elapsed = time.perf_counter() - start
        tokens_after = getattr(self.llm, "tokens_used", 0)

        return LoopResult(
            success=state.quality_score >= self.quality_threshold,
            output=state.output,
            iterations=state.iteration,
            quality_score=state.quality_score,
            termination_reason=state.termination_reason,
            history=state.history,
            elapsed_seconds=elapsed,
            tokens_used=tokens_after - tokens_before,
        )


def run_reflection_loop(spec_path: str, user_input: str = "") -> LoopResult:
    spec = load_lss_spec(spec_path)
    loop = ReflectionLoop(spec)
    return loop.run(user_input)
