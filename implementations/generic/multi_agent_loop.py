"""Level-3 multi-agent loop: specialize → coordinate → merge."""

from __future__ import annotations

from typing import Any

try:
    from .loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec
except ImportError:
    from loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec


class MultiAgentLoop(LoopRuntime):
    """Multi-agent loop coordinating specialist workers via an orchestrator."""

    def __init__(self, spec: dict[str, Any], llm: MockLLM | None = None) -> None:
        super().__init__(spec, llm=llm)

    def _specialist_outputs(self, task: str) -> dict[str, str]:
        outputs: dict[str, str] = {}
        for worker in self.spec.get("workers", []):
            role = worker.get("id") or worker.get("role", "worker")
            if role == "orchestrator":
                continue
            outputs[str(role)] = self.llm.complete(
                f"As {role}, contribute to task: {task}",
                role=str(role),
            )
        return outputs

    def _merge(self, task: str, specialist_outputs: dict[str, str]) -> str:
        combined = "\n".join(f"[{role}]: {text}" for role, text in specialist_outputs.items())
        return self.llm.complete(
            f"Merge specialist outputs for task '{task}':\n{combined}",
            role="orchestrator",
        )

    def _consensus_score(self, specialist_outputs: dict[str, str], merged: str) -> float:
        feedback = self.llm.complete(
            f"Score consensus quality:\n{merged}\nSpecialists:\n{specialist_outputs}",
            role="evaluator",
        )
        base = 0.5 + 0.1 * len(specialist_outputs)
        if "PASS" in feedback:
            base += 0.25
        return min(0.98, base + 0.08 * len(specialist_outputs))

    def run(self, user_input: str = "") -> LoopResult:
        import time

        start = time.perf_counter()
        tokens_before = getattr(self.llm, "tokens_used", 0)
        state = LoopState()

        if not user_input:
            inputs = self.spec.get("inputs") or []
            user_input = inputs[0].get("name", "collaborative task") if inputs else "collaborative task"

        while not state.terminated:
            state.iteration += 1
            specialists = self._specialist_outputs(user_input)
            state.output = self._merge(user_input, specialists)
            state.quality_score = self._consensus_score(specialists, state.output)
            state.history.append(
                {
                    "iteration": state.iteration,
                    "specialists": specialists,
                    "merged_output": state.output,
                    "quality_score": state.quality_score,
                }
            )
            if self.on_iteration:
                self.on_iteration(state)
            if state.quality_score >= self.quality_threshold:
                state.terminated = True
                state.termination_reason = "consensus_reached"
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


def run_multi_agent_loop(spec_path: str, user_input: str = "") -> LoopResult:
    spec = load_lss_spec(spec_path)
    loop = MultiAgentLoop(spec)
    return loop.run(user_input)
