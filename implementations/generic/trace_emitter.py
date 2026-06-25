"""Build Loop Trace 1.0 JSON from loop runtime results (LoopGym contract reference)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_trace(
    spec: dict[str, Any],
    *,
    loop_id: str | None = None,
    success: bool,
    iterations: int,
    termination_reason: str,
    history: list[dict[str, Any]],
    total_cost_usd: float = 0.0,
    started_at: str | None = None,
    ended_at: str | None = None,
    spec_path: str = "",
) -> dict[str, Any]:
    """Emit a Loop Trace 1.0 document from run history."""
    worker_ids = [w.get("id", w.get("role", "worker")) for w in (spec.get("workers") or [])]
    default_worker = worker_ids[0] if worker_ids else "worker"
    started = started_at or _utc_now()
    ended = ended_at or _utc_now()

    trace_iterations: list[dict[str, Any]] = []
    for rec in history:
        iter_num = int(rec.get("iteration", len(trace_iterations)))
        score = float(rec.get("quality_score", 0.0))
        trace_iterations.append(
            {
                "iteration": iter_num - 1 if iter_num > 0 else 0,
                "timestamp": started,
                "worker_id": rec.get("worker_id", default_worker),
                "worker_output": str(rec.get("output", ""))[:2000],
                "evaluator_scores": {"quality": score},
                "cost_usd": round(total_cost_usd / max(len(history), 1), 4),
                "feedback": [str(rec.get("feedback", ""))[:500]] if rec.get("feedback") else [],
            }
        )

    if not trace_iterations:
        trace_iterations.append(
            {
                "iteration": 0,
                "timestamp": started,
                "worker_id": default_worker,
                "evaluator_scores": {},
                "cost_usd": 0.0,
            }
        )

    return {
        "trace_version": "1.0",
        "loop_id": loop_id or str(uuid4()),
        "loop_name": spec.get("loop_name", "unknown"),
        "spec_path": spec_path,
        "started_at": started,
        "ended_at": ended,
        "success": success,
        "termination_reason": termination_reason,
        "total_cost_usd": round(total_cost_usd, 4),
        "iterations": trace_iterations,
        "metadata": {"runtime": "generic/loop_runtime"},
    }
