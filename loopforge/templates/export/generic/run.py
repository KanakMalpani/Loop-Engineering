#!/usr/bin/env python3
"""Generated stub — run via LoopGym SimEnv (pip install loopgym)."""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run {loop_name} via LoopGym")
    parser.add_argument("--task-id", default="cr-001")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--trace", default="trace.json", help="Write Loop Trace 1.0 JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        import loopgym as lg
    except ImportError:
        print("Install: pip install loopgym", file=sys.stderr)
        return 1

    env = lg.make("loopbench/code-repair-v1")
    try:
        result = env.run_episode(task_id=args.task_id, seed=args.seed, trace_path=args.trace)
    except TypeError:
        result = env.run_episode(task_id=args.task_id, seed=args.seed)
    payload = {
        "loop_name": "{loop_name}",
        "success": result.get("success"),
        "iterations": len(result.get("iterations") or []),
        "trace_path": args.trace,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"success={payload['success']} iterations={payload['iterations']} trace={args.trace}")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
