#!/usr/bin/env python3
"""
Reflection Loop — Level 2 (Reflective)
Act → Evaluate → Revise until rubric passes or max iterations.

LSS mapping:
  loop_name: reflection-loop-example
  workers: [generator, critic]
  evaluators: [rubric_threshold]
  termination: threshold | max_iterations
"""

from __future__ import annotations

import dataclasses
from typing import Callable


@dataclasses.dataclass
class LoopState:
    question: str
    draft: str = ""
    feedback: str = ""
    iteration: int = 0
    scores: list[float] = dataclasses.field(default_factory=list)


THRESHOLD = 0.85
MAX_ITERATIONS = 6


def mock_generator(state: LoopState) -> str:
    """Simulates improving drafts across iterations."""
    base = f"Answer to '{state.question}': "
    quality_layers = [
        "vague response.",
        "partial answer with missing detail.",
        "good answer but lacks structure.",
        "structured answer with key points.",
        "comprehensive answer with examples and clear conclusion.",
    ]
    idx = min(state.iteration, len(quality_layers) - 1)
    if state.feedback:
        idx = min(idx + 1, len(quality_layers) - 1)
    return base + quality_layers[idx]


def mock_critic(draft: str) -> tuple[float, str]:
    """Rubric: length, structure keywords, completeness."""
    score = 0.0
    feedback_parts: list[str] = []

    if len(draft) > 80:
        score += 0.25
    else:
        feedback_parts.append("Expand with more detail.")

    keywords = ["structured", "examples", "conclusion", "comprehensive"]
    hits = sum(1 for k in keywords if k in draft.lower())
    score += hits * 0.15

    if "vague" in draft or "partial" in draft:
        score += 0.05
        feedback_parts.append("Replace vague language with specifics.")
    elif "good answer" in draft:
        score += 0.35
        feedback_parts.append("Add structure and examples.")
    elif "structured" in draft:
        score += 0.55
        feedback_parts.append("Add examples and a conclusion.")
    elif "comprehensive" in draft:
        score = 0.92

    score = min(score, 1.0)
    feedback = " ".join(feedback_parts) if feedback_parts else "Acceptable quality."
    return score, feedback


def run_reflection_loop(
    question: str,
    generator: Callable[[LoopState], str] = mock_generator,
    critic: Callable[[str], tuple[float, str]] = mock_critic,
    threshold: float = THRESHOLD,
    max_iterations: int = MAX_ITERATIONS,
) -> LoopState:
    state = LoopState(question=question)

    while state.iteration < max_iterations:
        state.iteration += 1
        state.draft = generator(state)
        score, state.feedback = critic(state.draft)
        state.scores.append(score)

        print(f"[iter {state.iteration}] score={score:.2f} | {state.feedback[:60]}...")

        if score >= threshold:
            print(f"\n[OK] Terminated: rubric threshold ({threshold}) met")
            break
    else:
        print(f"\n[WARN] Terminated: max_iterations ({max_iterations}) reached")

    return state


def main() -> None:
    question = "What is Loop Engineering?"
    final = run_reflection_loop(question)

    print("\n--- Final Draft ---")
    print(final.draft)
    print(f"\nMetrics: iterations={final.iteration}, final_score={final.scores[-1]:.2f}")


if __name__ == "__main__":
    main()
