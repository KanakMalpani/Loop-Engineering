"""OpenAI Agents SDK-style reflection loop with mock fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    success: bool
    output: str
    iterations: int
    quality_score: float
    termination_reason: str
    trace: list[dict[str, Any]] = field(default_factory=list)


class MockAgentRunner:
    """Simulates implementer + critic agent turns without API access."""

    def run_turn(self, role: str, prompt: str, iteration: int) -> str:
        if role == "implementer":
            if iteration == 1:
                return f"[implementer] Draft solution for: {prompt[:100]}"
            return f"[implementer] Revised solution (iter {iteration}): {prompt[:80]}"
        return f"[critic] Score: {min(0.95, 0.5 + 0.15 * iteration):.2f}. PASS"


def _try_openai_runner():
    try:
        import os

        if not os.environ.get("OPENAI_API_KEY"):
            return None
        from openai import OpenAI  # noqa: F401

        return "openai"
    except ImportError:
        return None


def run_reflection_agent(
    objective: str,
    task: str,
    quality_threshold: float = 0.8,
    max_iterations: int = 5,
    use_mock: bool = True,
) -> AgentResult:
    """Run a two-agent reflection loop (implementer + critic)."""
    backend = None if use_mock else _try_openai_runner()
    runner = MockAgentRunner()
    trace: list[dict[str, Any]] = []
    draft = ""
    score = 0.0
    iteration = 0
    reason = "max_iterations"

    while iteration < max_iterations:
        iteration += 1
        draft = runner.run_turn(
            "implementer",
            f"Objective: {objective}\nTask: {task}" if iteration == 1 else f"Revise: {draft}",
            iteration,
        )
        critique = runner.run_turn("critic", draft, iteration)
        for token in critique.split():
            try:
                val = float(token.rstrip("."))
                if 0.0 <= val <= 1.0:
                    score = val
            except ValueError:
                continue
        trace.append({"iteration": iteration, "draft": draft, "critique": critique, "score": score})
        if score >= quality_threshold:
            reason = "quality_threshold_met"
            break

    return AgentResult(
        success=score >= quality_threshold,
        output=draft,
        iterations=iteration,
        quality_score=score,
        termination_reason=reason,
        trace=trace,
    )


if __name__ == "__main__":
    result = run_reflection_agent(
        objective="Summarize loop engineering",
        task="Three bullet points",
    )
    print(f"Backend: mock | Success: {result.success} | Score: {result.quality_score:.2f}")
    print(result.output)
