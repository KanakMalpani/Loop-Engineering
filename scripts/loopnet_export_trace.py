#!/usr/bin/env python3
"""Convert Loop Trace 1.0 JSON to LoopNet v0.3 draft row format."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def trace_to_loopnet_row(trace: dict, *, pattern: str = "reflection-loop") -> dict:
    iters = trace.get("iterations") or []
    scores = []
    for rec in iters:
        ev = rec.get("evaluator_scores") or {}
        if ev:
            scores.append(sum(float(v) for v in ev.values()) / len(ev))
    return {
        "metadata.loop_id": trace.get("loop_id"),
        "metadata.loop_name": trace.get("loop_name"),
        "metadata.pattern": pattern,
        "metadata.worker_count": 1,
        "metadata.iteration_count": len(iters),
        "metadata.success": trace.get("success"),
        "metadata.total_cost_usd": trace.get("total_cost_usd"),
        "metadata.termination_reason": trace.get("termination_reason"),
        "metadata.schema_version": "0.3-draft",
        "metadata.source": "loop-trace-1.0",
        "trajectory.final_quality": scores[-1] if scores else None,
        "trajectory.trace_path": trace.get("spec_path"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Loop Trace to LoopNet row JSON")
    parser.add_argument("trace", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    parser.add_argument("--pattern", default="reflection-loop")
    args = parser.parse_args()

    trace = json.loads(args.trace.read_text(encoding="utf-8"))
    row = trace_to_loopnet_row(trace, pattern=args.pattern)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote LoopNet draft row to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
