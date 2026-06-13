"""Level-2 research loop: gather → synthesize → verify."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec
except ImportError:
    from loop_runtime import LoopResult, LoopRuntime, LoopState, MockLLM, load_lss_spec


@dataclass
class ResearchConfig:
    max_sources: int = 3
    synthesis_passes: int = 2


class ResearchLoop(LoopRuntime):
    """Research-oriented loop with gather, synthesize, and verify phases."""

    def __init__(
        self,
        spec: dict[str, Any],
        llm: MockLLM | None = None,
        config: ResearchConfig | None = None,
    ) -> None:
        super().__init__(spec, llm=llm)
        self.config = config or ResearchConfig()

    def _gather(self, query: str) -> list[str]:
        findings = []
        for i in range(self.config.max_sources):
            finding = self.llm.complete(
                f"Research source {i + 1} for query: {query}",
                role="researcher",
            )
            findings.append(finding)
        return findings

    def _synthesize(self, query: str, findings: list[str]) -> str:
        combined = "\n".join(f"- {f}" for f in findings)
        draft = self.llm.complete(
            f"Synthesize research on '{query}':\n{combined}",
            role="implementer",
        )
        for _ in range(self.config.synthesis_passes - 1):
            draft = self.llm.complete(
                f"Refine synthesis:\n{draft}",
                role="implementer",
            )
        return draft

    def _verify(self, output: str) -> tuple[float, str]:
        feedback = self.llm.complete(
            f"Verify factual consistency and completeness:\n{output}",
            role="verifier",
        )
        score = 0.55 + 0.15 * min(len(output) / 500, 1.0)
        if "PASS" in feedback:
            score = min(0.95, score + 0.25)
        return score, feedback

    def run(self, user_input: str = "") -> LoopResult:
        import time

        start = time.perf_counter()
        tokens_before = getattr(self.llm, "tokens_used", 0)
        state = LoopState()

        if not user_input:
            inputs = self.spec.get("inputs") or []
            user_input = inputs[0].get("name", "research topic") if inputs else "research topic"

        while not state.terminated:
            state.iteration += 1
            findings = self._gather(user_input)
            state.output = self._synthesize(user_input, findings)
            score, verification = self._verify(state.output)
            state.quality_score = max(state.quality_score, score + 0.1 * state.iteration)
            state.history.append(
                {
                    "iteration": state.iteration,
                    "findings_count": len(findings),
                    "output": state.output,
                    "quality_score": state.quality_score,
                    "verification": verification,
                }
            )
            if self.on_iteration:
                self.on_iteration(state)
            if state.quality_score >= self.quality_threshold:
                state.terminated = True
                state.termination_reason = "research_quality_met"
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


def run_research_loop(spec_path: str, user_input: str = "") -> LoopResult:
    spec = load_lss_spec(spec_path)
    loop = ResearchLoop(spec)
    return loop.run(user_input)
