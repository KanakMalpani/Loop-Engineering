#!/usr/bin/env python3
"""Generate synthetic LoopNet seed corpus (default: 500 records, >=40% failures)."""

from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from loopnet.constants import (
    FAILURE_MODES,
    PATTERN_SLUGS,
)
from loopnet.les import les_from_trajectory, trajectory_diagnostics

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "seed" / "records.jsonl"
DEFAULT_SPLITS = ROOT / "data" / "seed" / "splits.json"

OBJECTIVES = [
    "Produce a research brief with verified citations and coverage score >= 0.85.",
    "Repair failing unit tests while preserving public API contracts.",
    "Synthesize multi-source findings into an executive summary under 500 words.",
    "Debate two solution approaches and converge on a ranked recommendation.",
    "Optimize prompt templates until rubric score exceeds 0.80 within budget.",
    "Plan and execute a data pipeline migration with zero schema regressions.",
    "Generate code patches that pass lint, type-check, and integration tests.",
    "Summarize customer feedback themes with actionable product insights.",
]

FAILURE_PROFILES: dict[str, dict] = {
    "fail.open_loop": {"shape": "flat", "termination": "budget_exhausted"},
    "fail.self_grade": {"shape": "inflate", "termination": "goal_met"},
    "fail.evaluator_drift": {"shape": "drift", "termination": "stall"},
    "fail.tau_omission": {"shape": "slow_climb", "termination": "max_iterations"},
    "fail.false_pass": {"shape": "spike_fake", "termination": "goal_met"},
    "fail.false_fail": {"shape": "reject_good", "termination": "stall"},
    "fail.oscillation": {"shape": "oscillate", "termination": "stall"},
    "fail.resource_bleed": {"shape": "costly_flat", "termination": "cost_exceeded"},
    "fail.state_corruption": {"shape": "collapse", "termination": "error"},
    "fail.orchestration_deadlock": {"shape": "stuck", "termination": "timeout"},
    "fail.meta_instability": {"shape": "decay", "termination": "error"},
    "fail.safety_bypass": {"shape": "unsafe_spike", "termination": "safety_violation"},
}

PATTERN_POOLS: dict[str, list[str]] = {
    "fail.open_loop": ["reflection-loop", "research-loop"],
    "fail.self_grade": ["reflection-loop", "critique-loop"],
    "fail.evaluator_drift": ["critique-loop", "verification-loop"],
    "fail.tau_omission": ["planning-loop", "exploration-loop"],
    "fail.false_pass": ["verification-loop", "optimization-loop"],
    "fail.false_fail": ["critique-loop", "debate-loop"],
    "fail.oscillation": ["optimization-loop", "planning-loop"],
    "fail.resource_bleed": ["exploration-loop", "multi-agent-coordination"],
    "fail.state_corruption": ["memory-augmented-loop", "multi-agent-coordination"],
    "fail.orchestration_deadlock": ["multi-agent-coordination", "debate-loop"],
    "fail.meta_instability": ["recursive-improvement-loop", "optimization-loop"],
    "fail.safety_bypass": ["safety-constrained-loop", "simulation-loop"],
}


def _uuid_record_id() -> str:
    return f"ln-{uuid.uuid4()}"


def _goal_trace(
    rng: random.Random,
    *,
    shape: str,
    iterations: int,
    goal_target: float,
    success: bool,
) -> list[float]:
    start = rng.uniform(0.15, 0.35)
    scores = [round(start, 4)]

    for step in range(1, iterations):
        prev = scores[-1]
        if shape == "flat":
            delta = rng.uniform(-0.01, 0.02)
        elif shape == "inflate":
            delta = rng.uniform(0.04, 0.09)
        elif shape == "drift":
            delta = rng.uniform(-0.03, 0.05) if step > iterations // 2 else rng.uniform(0.02, 0.06)
        elif shape == "slow_climb":
            delta = rng.uniform(0.01, 0.03)
        elif shape == "spike_fake":
            delta = rng.uniform(0.08, 0.15) if step == iterations - 1 else rng.uniform(-0.01, 0.03)
        elif shape == "reject_good":
            delta = rng.uniform(-0.04, 0.02)
        elif shape == "oscillate":
            delta = 0.07 if step % 2 == 0 else -0.06
        elif shape == "costly_flat":
            delta = rng.uniform(-0.005, 0.01)
        elif shape == "collapse":
            delta = rng.uniform(-0.12, -0.04) if step > 1 else rng.uniform(0.01, 0.04)
        elif shape == "stuck":
            delta = rng.uniform(-0.005, 0.005)
        elif shape == "decay":
            delta = rng.uniform(-0.08, -0.02)
        elif shape == "unsafe_spike":
            delta = rng.uniform(0.05, 0.12)
        else:
            delta = rng.uniform(0.02, 0.08) if success else rng.uniform(-0.03, 0.02)

        scores.append(round(max(0.0, min(1.0, prev + delta)), 4))

    if success and scores[-1] < goal_target:
        scores[-1] = round(rng.uniform(goal_target, min(1.0, goal_target + 0.08)), 4)

    return scores


def _build_trajectory(
    rng: random.Random,
    *,
    shape: str,
    iterations: int,
    goal_target: float,
    success: bool,
    failure_mode: str | None,
) -> list[dict]:
    goal_scores = _goal_trace(
        rng,
        shape=shape,
        iterations=iterations,
        goal_target=goal_target,
        success=success,
    )
    trajectory = []
    base_latency = rng.uniform(8.0, 25.0)

    for index, goal_score in enumerate(goal_scores, start=1):
        latency = round(base_latency * rng.uniform(0.8, 1.4), 3)
        cost = round(rng.uniform(0.03, 0.18), 4)
        if shape == "costly_flat":
            cost = round(rng.uniform(0.12, 0.28), 4)

        failure_codes: list[str] = []
        safety_events = 0
        human_intervention = False

        if failure_mode and index >= max(2, iterations - 2):
            failure_codes.append(failure_mode)
        if failure_mode == "fail.safety_bypass" and index >= iterations - 1:
            safety_events = rng.randint(1, 3)
        if failure_mode == "fail.orchestration_deadlock" and index >= iterations - 1:
            latency = round(base_latency * 6, 3)
        if rng.random() < 0.08:
            human_intervention = True

        trajectory.append(
            {
                "iteration": index,
                "goal_score": goal_score,
                "primary_quality": round(
                    max(0.0, min(1.0, goal_score + rng.uniform(-0.05, 0.05))), 4
                ),
                "cost_usd": cost,
                "latency_seconds": latency,
                "tokens": rng.randint(800, 6000),
                "failure_codes": failure_codes,
                "safety_events": safety_events,
                "human_intervention": human_intervention,
            }
        )

    return trajectory


def _loop_spec_snapshot(
    rng: random.Random,
    *,
    loop_name: str,
    patterns: list[str],
    max_iterations: int,
) -> dict:
    worker_count = rng.randint(1, 4)
    evaluator_count = rng.randint(1, 3)
    return {
        "loop_name": loop_name,
        "version": "1.0.0",
        "workers": [{"id": f"worker-{i}"} for i in range(1, worker_count + 1)],
        "evaluators": [{"id": f"evaluator-{i}"} for i in range(1, evaluator_count + 1)],
        "optimization_strategy": {"type": "prompt_refinement", "max_steps": max_iterations},
        "extensions": {"patterns": patterns},
    }


def _make_record(
    rng: random.Random,
    *,
    split: str,
    force_failure: bool | None = None,
    created_at: datetime,
) -> dict:
    goal_target = round(rng.choice([0.75, 0.80, 0.85, 0.90]), 2)
    max_iterations = rng.randint(4, 12)

    if force_failure is True:
        outcome = "failure"
    elif force_failure is False:
        outcome = "success" if rng.random() < 0.85 else "partial"
    else:
        outcome = rng.choices(["failure", "success", "partial"], weights=[0.42, 0.48, 0.10])[0]

    failure_mode: str | None = None
    failure_modes: list[str] = []
    shape = "climb"
    termination_reason = "goal_met"

    if outcome == "failure":
        failure_mode = rng.choice(FAILURE_MODES)
        failure_modes = [failure_mode]
        if rng.random() < 0.25:
            secondary = rng.choice([mode for mode in FAILURE_MODES if mode != failure_mode])
            failure_modes.append(secondary)
        profile = FAILURE_PROFILES[failure_mode]
        shape = profile["shape"]
        termination_reason = profile["termination"]
    elif outcome == "partial":
        failure_mode = None
        failure_modes = [rng.choice(FAILURE_MODES)]
        shape = "slow_climb"
        termination_reason = rng.choice(["stall", "budget_exhausted", "human_stop"])
    else:
        shape = "climb"
        termination_reason = "goal_met"

    iterations = (
        rng.randint(2, max_iterations - 1)
        if outcome == "failure"
        else rng.randint(3, max_iterations)
    )
    if termination_reason == "max_iterations":
        iterations = max_iterations

    patterns = PATTERN_POOLS.get(failure_mode or "", [])
    if not patterns:
        patterns = [rng.choice(PATTERN_SLUGS)]
        if rng.random() < 0.35:
            patterns.append(rng.choice([p for p in PATTERN_SLUGS if p not in patterns]))

    loop_name = f"{patterns[0].replace('-loop', '')}-{rng.randint(1000, 9999)}"
    objective = rng.choice(OBJECTIVES)

    trajectory = _build_trajectory(
        rng,
        shape=shape,
        iterations=iterations,
        goal_target=goal_target,
        success=outcome == "success",
        failure_mode=failure_mode,
    )

    diag = trajectory_diagnostics(trajectory)
    les_observed = les_from_trajectory(
        trajectory,
        goal_target=goal_target,
        outcome=outcome,
        failure_mode=failure_mode,
        max_iterations_budget=max_iterations,
    )

    record: dict = {
        "record_id": _uuid_record_id(),
        "schema_version": "ln/record-v1",
        "spec_pins": {"lss": "lss@1.0.0", "les": "les@1.0.0"},
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "source": "synthetic",
        "split": split,
        "patterns": patterns,
        "loop_name": loop_name,
        "objective": objective,
        "loop_spec": _loop_spec_snapshot(
            rng,
            loop_name=loop_name,
            patterns=patterns,
            max_iterations=max_iterations,
        ),
        "outcome": outcome,
        "termination_reason": termination_reason,
        "trajectory": trajectory,
        "les_observed": les_observed,
        "metadata": {
            "iteration_count": diag["iteration_count"],
            "cost_total_usd": diag["cost_total_usd"],
            "goal_target": goal_target,
            "goal_final": diag["goal_final"],
            "worker_count": 0,
            "evaluator_count": 0,
            "max_iterations_budget": max_iterations,
            "regression_count": diag["regression_count"],
            "tags": ["synthetic", "v0.1"],
        },
        "redaction": {"level": "none", "fields_removed": []},
    }

    spec = record["loop_spec"]
    record["metadata"]["worker_count"] = len(spec["workers"])
    record["metadata"]["evaluator_count"] = len(spec["evaluators"])

    if failure_modes:
        record["failure_modes"] = failure_modes
    if failure_mode:
        record["failure_mode"] = failure_mode

    return record


def _assign_splits(count: int, rng: random.Random) -> list[str]:
    train_n = int(count * 0.8)
    val_n = int(count * 0.1)
    test_n = count - train_n - val_n
    splits = ["train"] * train_n + ["val"] * val_n + ["test"] * test_n
    rng.shuffle(splits)
    return splits


def generate_corpus(
    *,
    count: int = 500,
    seed: int = 42,
    failure_ratio: float = 0.42,
) -> list[dict]:
    rng = random.Random(seed)
    splits = _assign_splits(count, rng)
    failure_count = int(count * failure_ratio)
    failure_flags = [True] * failure_count + [False] * (count - failure_count)
    rng.shuffle(failure_flags)

    base_time = datetime(2026, 1, 1, tzinfo=UTC)
    records: list[dict] = []

    for index in range(count):
        created_at = base_time + timedelta(hours=index * 3)
        records.append(
            _make_record(
                rng,
                split=splits[index],
                force_failure=failure_flags[index],
                created_at=created_at,
            )
        )

    return records


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def write_splits(records: list[dict], path: Path) -> None:
    splits = {
        "train": [r["record_id"] for r in records if r["split"] == "train"],
        "val": [r["record_id"] for r in records if r["split"] == "val"],
        "test": [r["record_id"] for r in records if r["split"] == "test"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(splits, handle, indent=2)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--failure-ratio", type=float, default=0.42)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    args = parser.parse_args(argv)

    records = generate_corpus(
        count=args.count,
        seed=args.seed,
        failure_ratio=args.failure_ratio,
    )
    write_jsonl(records, args.output)
    write_splits(records, args.splits)

    failures = sum(1 for record in records if record["outcome"] == "failure")
    print(
        f"Wrote {len(records)} records to {args.output} "
        f"({failures} failures, {failures / len(records):.1%})"
    )
    print(f"Wrote split manifest to {args.splits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
