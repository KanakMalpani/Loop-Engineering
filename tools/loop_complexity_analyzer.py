#!/usr/bin/env python3
"""Estimate token and time complexity from an LSS loop specification."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

TOKENS_PER_WORKER_CALL = 2500
TOKENS_PER_EVALUATOR = 1200
TOKENS_PER_FEEDBACK = 400
TOKENS_PER_REFLECTION = 1800
SECONDS_PER_1K_TOKENS = 2.5


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def _max_iterations(spec: dict[str, Any]) -> int:
    term = spec.get("termination_conditions")
    if isinstance(term, dict):
        for failure in term.get("failure") or []:
            if failure.get("type") == "max_iterations":
                return int(failure.get("value", 10))
    if isinstance(term, list):
        for cond in term:
            if cond.get("type") == "max_iterations":
                return int(cond.get("value", 10))
    cost = spec.get("cost_limits") or {}
    opt = spec.get("optimization_strategy") or {}
    return int(cost.get("max_iterations") or opt.get("max_steps") or 10)


def analyze_complexity(spec: dict[str, Any]) -> dict[str, Any]:
    workers = spec.get("workers") or []
    evaluators = spec.get("evaluators") or []
    feedback = spec.get("feedback_channels") or []
    level = int(spec.get("taxonomy_level", 2))
    max_iter = _max_iterations(spec)

    tokens_per_iteration = (
        len(workers) * TOKENS_PER_WORKER_CALL
        + len(evaluators) * TOKENS_PER_EVALUATOR
        + len(feedback) * TOKENS_PER_FEEDBACK
    )
    if level >= 2:
        tokens_per_iteration += TOKENS_PER_REFLECTION
    if level >= 3:
        tokens_per_iteration += len(workers) * 800
    if level >= 4:
        tokens_per_iteration *= 3

    cost_limits = spec.get("cost_limits") or {}
    budget_tokens = cost_limits.get("token_soft_cap") or cost_limits.get("max_total_tokens")
    expected_iterations = min(max_iter, max(1, round(max_iter * 0.6)))
    expected_total_tokens = tokens_per_iteration * expected_iterations
    worst_case_tokens = tokens_per_iteration * max_iter

    if budget_tokens:
        budget_tokens = int(budget_tokens)
        budget_limited_iterations = max(1, budget_tokens // max(tokens_per_iteration, 1))
    else:
        budget_limited_iterations = max_iter

    seconds_per_iteration = (tokens_per_iteration / 1000) * SECONDS_PER_1K_TOKENS
    expected_seconds = seconds_per_iteration * expected_iterations
    worst_case_seconds = seconds_per_iteration * max_iter

    # Structural complexity score (0–100) for quick tiering
    structural = min(
        100,
        len(workers) * 8
        + len(evaluators) * 10
        + level * 5
        + len(spec.get("safety_constraints") or []) * 3
        + len(feedback) * 3,
    )
    if structural < 25:
        tier = "low"
    elif structural < 55:
        tier = "medium"
    elif structural < 80:
        tier = "high"
    else:
        tier = "critical"

    complexity_class = "O(n)"
    if level >= 4:
        complexity_class = "O(g × n) population × iterations"
    elif level >= 3:
        complexity_class = "O(w × n) workers × iterations"
    elif level >= 2:
        complexity_class = "O(n) with reflection overhead"

    return {
        "loop_name": spec.get("loop_name"),
        "taxonomy_level": level,
        "max_iterations": max_iter,
        "expected_iterations": expected_iterations,
        "workers": len(workers),
        "evaluators": len(evaluators),
        "feedback_channels": len(feedback),
        "tokens_per_iteration": tokens_per_iteration,
        "expected_total_tokens": expected_total_tokens,
        "worst_case_tokens": worst_case_tokens,
        "budget_tokens": budget_tokens,
        "budget_limited_iterations": budget_limited_iterations,
        "expected_wall_clock_seconds": round(expected_seconds, 1),
        "worst_case_wall_clock_seconds": round(worst_case_seconds, 1),
        "complexity_class": complexity_class,
        "structural_score": structural,
        "complexity_tier": tier,
    }


def format_report(analysis: dict[str, Any]) -> str:
    lines = [
        f"Complexity Analysis: {analysis.get('loop_name', 'unknown')}",
        "=" * 50,
        f"Taxonomy level:        L{analysis['taxonomy_level']}",
        f"Complexity class:      {analysis['complexity_class']}",
        f"Structural score:      {analysis['structural_score']}/100 ({analysis['complexity_tier']})",
        f"Max iterations:        {analysis['max_iterations']}",
        f"Expected iterations:   {analysis['expected_iterations']}",
        "",
        "Token estimates:",
        f"  Per iteration:       {analysis['tokens_per_iteration']:,}",
        f"  Expected total:      {analysis['expected_total_tokens']:,}",
        f"  Worst case:          {analysis['worst_case_tokens']:,}",
    ]
    if analysis["budget_tokens"]:
        lines.extend(
            [
                f"  Budget cap:          {analysis['budget_tokens']:,}",
                f"  Budget-limited iters:{analysis['budget_limited_iterations']}",
            ]
        )
    lines.extend(
        [
            "",
            "Time estimates (heuristic):",
            f"  Expected wall clock: {analysis['expected_wall_clock_seconds']}s",
            f"  Worst case:          {analysis['worst_case_wall_clock_seconds']}s",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate token and time complexity from an LSS loop specification",
    )
    parser.add_argument("spec", type=Path, help="Path to LSS YAML file")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"Error: file not found: {args.spec}", file=sys.stderr)
        return 2

    try:
        spec = load_spec(args.spec)
        analysis = analyze_complexity(spec)
    except (yaml.YAMLError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
