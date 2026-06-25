"""Observed LES from Loop Trace 1.0 JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from loopctl.scoring.structural import LES_WEIGHTS, compute_les, load_spec


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def observed_from_trace(trace: dict[str, Any]) -> dict[str, float]:
    iters = trace.get("iterations") or []
    n = max(len(iters), 1)
    success = bool(trace.get("success"))
    total_cost = float(trace.get("total_cost_usd") or 0.0)

    scores: list[float] = []
    for rec in iters:
        ev = rec.get("evaluator_scores") or {}
        if ev:
            scores.append(sum(float(v) for v in ev.values()) / len(ev))
    final_quality = scores[-1] if scores else (0.85 if success else 0.4)

    effectiveness = _clamp(final_quality)
    if n <= 2:
        speed = 0.9
    elif n <= 5:
        speed = 0.75
    elif n <= 10:
        speed = 0.55
    else:
        speed = 0.35

    if total_cost <= 0.1:
        cost = 0.9
    elif total_cost <= 0.5:
        cost = 0.75
    elif total_cost <= 2.0:
        cost = 0.55
    else:
        cost = 0.35

    if success and scores:
        var = max(scores) - min(scores)
        robustness = _clamp(0.7 + (0.2 if var < 0.15 else 0.05))
    else:
        robustness = 0.45

    scalability = 0.6
    safety = 0.65 if success else 0.5
    adaptability = _clamp(0.5 + 0.05 * n)
    autonomy = 0.7 if success else 0.45

    return {
        "effectiveness": effectiveness,
        "speed": speed,
        "cost": cost,
        "robustness": robustness,
        "scalability": scalability,
        "safety": safety,
        "adaptability": adaptability,
        "autonomy": autonomy,
    }


def composite(categories: dict[str, float]) -> float:
    return round(sum(LES_WEIGHTS[k] * categories[k] for k in LES_WEIGHTS) * 100, 1)


def score_trace(trace: dict[str, Any], spec: dict[str, Any] | None = None) -> dict[str, Any]:
    observed = observed_from_trace(trace)
    structural_les = None
    structural_cats = None
    if spec:
        structural_les, structural_cats = compute_les(spec)

    obs_les = composite(observed)
    return {
        "loop_name": trace.get("loop_name"),
        "loop_id": trace.get("loop_id"),
        "observed_les": obs_les,
        "observed_categories": observed,
        "structural_les": structural_les,
        "structural_categories": structural_cats,
        "weights": LES_WEIGHTS,
        "source": "loop-trace-1.0",
    }


def score_trace_files(trace_path: Path, spec_path: Path | None = None) -> dict[str, Any]:
    import json

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    spec = load_spec(spec_path) if spec_path else None
    return score_trace(trace, spec)
