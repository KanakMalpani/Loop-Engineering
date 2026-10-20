"""Registry constants aligned with 01-loop-engineering-core/specs/loop-ids.md."""

from __future__ import annotations

PATTERN_SLUGS: tuple[str, ...] = (
    "reflection-loop",
    "critique-loop",
    "planning-loop",
    "verification-loop",
    "research-loop",
    "simulation-loop",
    "debate-loop",
    "exploration-loop",
    "optimization-loop",
    "memory-augmented-loop",
    "human-in-the-loop",
    "safety-constrained-loop",
    "multi-agent-coordination",
    "recursive-improvement-loop",
)

FAILURE_MODES: tuple[str, ...] = (
    "fail.open_loop",
    "fail.self_grade",
    "fail.evaluator_drift",
    "fail.tau_omission",
    "fail.false_pass",
    "fail.false_fail",
    "fail.oscillation",
    "fail.resource_bleed",
    "fail.state_corruption",
    "fail.orchestration_deadlock",
    "fail.meta_instability",
    "fail.safety_bypass",
)

TERMINATION_REASONS: tuple[str, ...] = (
    "goal_met",
    "budget_exhausted",
    "human_stop",
    "error",
    "stall",
    "safety_violation",
    "timeout",
    "max_iterations",
    "cost_exceeded",
    "evaluator_error",
)

LES_CATEGORIES: tuple[str, ...] = (
    "effectiveness",
    "speed",
    "cost",
    "robustness",
    "scalability",
    "safety",
    "adaptability",
    "autonomy",
)

LES_WEIGHTS: dict[str, float] = {
    "effectiveness": 0.20,
    "speed": 0.15,
    "cost": 0.12,
    "robustness": 0.13,
    "scalability": 0.10,
    "safety": 0.12,
    "adaptability": 0.10,
    "autonomy": 0.08,
}

FAILURE_TO_TERMINATION: dict[str, str] = {
    "fail.open_loop": "budget_exhausted",
    "fail.self_grade": "goal_met",
    "fail.evaluator_drift": "stall",
    "fail.tau_omission": "max_iterations",
    "fail.false_pass": "goal_met",
    "fail.false_fail": "stall",
    "fail.oscillation": "stall",
    "fail.resource_bleed": "cost_exceeded",
    "fail.state_corruption": "error",
    "fail.orchestration_deadlock": "timeout",
    "fail.meta_instability": "error",
    "fail.safety_bypass": "safety_violation",
}
