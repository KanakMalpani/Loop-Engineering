#!/usr/bin/env python3
"""Compute Loop Engineering Score (LES-1.0) from runtime metrics or LSS spec inference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

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

CATEGORY_LABELS = {
    "effectiveness": "Effectiveness",
    "speed": "Speed",
    "cost": "Cost",
    "robustness": "Robustness",
    "scalability": "Scalability",
    "safety": "Safety",
    "adaptability": "Adaptability",
    "autonomy": "Autonomy",
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _infer_effectiveness(spec: dict[str, Any]) -> float:
    score = 0.4
    evaluators = spec.get("evaluators") or []
    score += min(0.25, 0.08 * len(evaluators))
    for ev in evaluators:
        rubric = ev.get("rubric") or {}
        if rubric.get("pass_threshold") is not None:
            score += 0.05
        if rubric.get("dimensions"):
            score += 0.05
    metrics = spec.get("metrics") or []
    score += min(0.15, 0.05 * len(metrics))
    term = spec.get("termination_conditions")
    if isinstance(term, dict) and term.get("success"):
        score += 0.1
    return _clamp(score)


def _infer_speed(spec: dict[str, Any]) -> float:
    max_iter = None
    term = spec.get("termination_conditions")
    if isinstance(term, dict):
        for failure in term.get("failure") or []:
            if failure.get("type") == "max_iterations":
                max_iter = failure.get("value")
    if max_iter is None:
        opt = spec.get("optimization_strategy") or {}
        max_iter = opt.get("max_steps")
    if max_iter is None:
        return 0.5
    max_iter = int(max_iter)
    if max_iter <= 3:
        return 0.95
    if max_iter <= 5:
        return 0.85
    if max_iter <= 10:
        return 0.70
    if max_iter <= 20:
        return 0.55
    return 0.40


def _infer_cost(spec: dict[str, Any]) -> float:
    cost = spec.get("cost_limits") or {}
    score = 0.5
    if cost.get("token_soft_cap"):
        tokens = int(cost["token_soft_cap"])
        if tokens <= 10000:
            score += 0.25
        elif tokens <= 50000:
            score += 0.15
        elif tokens <= 100000:
            score += 0.05
        else:
            score -= 0.1
    if cost.get("cumulative_usd") is not None:
        usd = float(cost["cumulative_usd"])
        if usd <= 0.5:
            score += 0.2
        elif usd <= 2.0:
            score += 0.1
        elif usd <= 10.0:
            score += 0.0
        else:
            score -= 0.15
    workers = len(spec.get("workers") or [])
    score -= min(0.2, 0.04 * max(0, workers - 2))
    return _clamp(score)


def _infer_robustness(spec: dict[str, Any]) -> float:
    score = 0.35
    score += min(0.2, 0.07 * len(spec.get("evaluators") or []))
    score += min(0.15, 0.05 * len(spec.get("feedback_channels") or []))
    if spec.get("memory"):
        score += 0.1
    opt = spec.get("optimization_strategy") or {}
    if opt.get("type") in ("prompt_refinement", "parameter_search"):
        score += 0.1
    term = spec.get("termination_conditions")
    if isinstance(term, dict) and term.get("stall"):
        score += 0.05
    return _clamp(score)


def _infer_scalability(spec: dict[str, Any]) -> float:
    score = 0.45
    inputs = spec.get("inputs")
    input_count = len(inputs.get("schema") or {}) if isinstance(inputs, dict) else 0
    score += min(0.2, 0.05 * input_count)
    if spec.get("feedback_channels"):
        score += 0.1
    if len(spec.get("workers") or []) >= 2:
        score += 0.1
    cost = spec.get("cost_limits") or {}
    if cost.get("cumulative_usd") is not None:
        score += 0.05
    return _clamp(score)


def _infer_safety(spec: dict[str, Any]) -> float:
    constraints = spec.get("safety_constraints") or []
    if not constraints:
        return 0.35
    score = 0.5 + min(0.35, 0.12 * len(constraints))
    for c in constraints:
        if c.get("action") in ("halt", "quarantine"):
            score += 0.05
    return _clamp(score)


def _infer_adaptability(spec: dict[str, Any]) -> float:
    score = 0.4
    inputs = spec.get("inputs")
    input_count = len(inputs.get("schema") or {}) if isinstance(inputs, dict) else 0
    score += min(0.25, 0.06 * input_count)
    opt = spec.get("optimization_strategy") or {}
    if opt.get("type") in ("prompt_refinement", "parameter_search", "memory_update"):
        score += 0.1
    return _clamp(score)


def _infer_autonomy(spec: dict[str, Any]) -> float:
    score = 0.5
    score += min(0.25, 0.06 * len(spec.get("workers") or []))
    for c in spec.get("safety_constraints") or []:
        if c.get("action") in ("escalate_human",):
            score -= 0.1
    return _clamp(score)


INFERENCE_MAP = {
    "effectiveness": _infer_effectiveness,
    "speed": _infer_speed,
    "cost": _infer_cost,
    "robustness": _infer_robustness,
    "scalability": _infer_scalability,
    "safety": _infer_safety,
    "adaptability": _infer_adaptability,
    "autonomy": _infer_autonomy,
}


def compute_category_scores(spec: dict[str, Any]) -> dict[str, float]:
    """Return normalized [0,1] scores for each LES category."""
    explicit = spec.get("les_scores") or {}
    scores: dict[str, float] = {}
    for category in LES_WEIGHTS:
        if category in explicit and explicit[category] is not None:
            scores[category] = _clamp(float(explicit[category]))
        else:
            scores[category] = INFERENCE_MAP[category](spec)
    return scores


def compute_les(spec: dict[str, Any]) -> tuple[float, dict[str, float]]:
    """
    Compute composite LES (canonical [0, 1] per les-1.0.md).
    Returns (les_normalized, category_scores).
    """
    categories = compute_category_scores(spec)
    composite = sum(LES_WEIGHTS[cat] * categories[cat] for cat in LES_WEIGHTS)
    return round(composite, 4), categories


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def format_report(
    loop_name: str,
    les_normalized: float,
    categories: dict[str, float],
    source: str,
    display_scale: bool,
) -> str:
    les_display = round(les_normalized * 100, 1)
    lines = [
        "Loop Engineering Score (LES-1.0)",
        "=" * 40,
        f"Loop:   {loop_name}",
        f"Source: {source}",
        f"LES:    {les_normalized:.4f} (normalized)",
    ]
    if display_scale:
        lines.append(f"        {les_display:.1f} / 100 (display)")
    lines.extend(["", "Category breakdown (normalized [0, 1]):"])
    for cat, weight in LES_WEIGHTS.items():
        norm = categories[cat]
        weighted = weight * norm
        bar = "#" * int(norm * 20)
        lines.append(f"  {CATEGORY_LABELS[cat]:14s}  {norm:.2f}  (w={weight:.2f}, +{weighted:.3f})  {bar}")
    lines.append("")
    threshold = les_display if display_scale else les_normalized
    cutoffs = (90, 75, 60, 40) if display_scale else (0.90, 0.75, 0.60, 0.40)
    if threshold >= cutoffs[0]:
        lines.append("Interpretation: Production-grade loop")
    elif threshold >= cutoffs[1]:
        lines.append("Interpretation: Strong loop — targeted improvements possible")
    elif threshold >= cutoffs[2]:
        lines.append("Interpretation: Functional loop — structural changes likely needed")
    elif threshold >= cutoffs[3]:
        lines.append("Interpretation: Fragile loop — high regression risk")
    else:
        lines.append("Interpretation: Non-viable loop — redesign required")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute LES-1.0 from an LSS spec or explicit scores")
    parser.add_argument("--spec", type=Path, help="Path to LSS YAML specification")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--display",
        action="store_true",
        help="Include 0-100 display scale in text output (canonical remains [0,1])",
    )
    args = parser.parse_args()

    if not args.spec:
        parser.error("Provide --spec PATH")

    spec = load_spec(args.spec)
    les_normalized, categories = compute_les(spec)
    loop_name = spec.get("loop_name", args.spec.stem)
    les_display = round(les_normalized * 100, 1)

    if args.json:
        print(
            json.dumps(
                {
                    "loop_name": loop_name,
                    "les_normalized": les_normalized,
                    "les_display": les_display,
                    "categories": categories,
                    "weights": LES_WEIGHTS,
                    "source": str(args.spec),
                    "mode": "spec_inference",
                },
                indent=2,
            )
        )
    else:
        print(format_report(loop_name, les_normalized, categories, str(args.spec), args.display))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
