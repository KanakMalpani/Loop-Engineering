"""Verification loop: generate → verify → fix until checks pass."""

from __future__ import annotations

from typing import Any

try:
    from .loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec
except ImportError:
    from loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec


class VerificationLoop(LoopRuntime):
    """Maker-checker loop with explicit verification and repair cycles."""

    def __init__(self, spec: dict[str, Any], llm: MockLLM | None = None) -> None:
        super().__init__(spec, llm=llm)

    def _generate(self, task: str, prior: str = "", issues: str = "") -> str:
        if not prior:
            prompt = f"Generate solution for: {task}"
        else:
            prompt = f"Fix issues and regenerate.\nIssues: {issues}\nPrior:\n{prior}"
        return self.llm.complete(prompt, role="implementer")

    def _verify(self, output: str) -> tuple[bool, str, float]:
        feedback = self.llm.complete(
            f"Run verification checks on:\n{output}",
            role="verifier",
        )
        passed = "PASS" in feedback
        score = 0.85 if passed else 0.45 + 0.1 * min(len(output) / 300, 1.0)
        return passed, feedback, score

    def run(self, user_input: str = "") -> LoopResult:
        import time

        start = time.perf_counter()
        tokens_before = getattr(self.llm, "tokens_used", 0)
        state = LoopState()

        if not user_input:
            inputs = self.spec.get("inputs") or []
            user_input = inputs[0].get("name", "task") if inputs else "task"

        issues = ""
        while not state.terminated:
            state.iteration += 1
            state.output = self._generate(user_input, state.output, issues)
            passed, feedback, score = self._verify(state.output)
            state.quality_score = score
            state.history.append(
                {
                    "iteration": state.iteration,
                    "output": state.output,
                    "passed": passed,
                    "verification": feedback,
                    "quality_score": score,
                }
            )
            if self.on_iteration:
                self.on_iteration(state)
            if passed or score >= self.quality_threshold:
                state.terminated = True
                state.termination_reason = "verification_passed"
            elif state.iteration >= self.max_iterations:
                state.terminated = True
                state.termination_reason = "max_iterations"
            else:
                issues = feedback

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


def run_verification_loop(spec_path: str, user_input: str = "") -> LoopResult:
    spec = load_lss_spec(spec_path)
    loop = VerificationLoop(spec)
    return loop.run(user_input)
