#!/usr/bin/env python3
"""Smoke LoopGym perturbed SimEnvs (RAG, HITL, safety)."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        import loopgym as lg
    except ImportError:
        print("SKIP: loopgym not installed", file=sys.stderr)
        return 0

    cases = [
        ("loopbench/rag-retrieval-v1", "LB-RAG-1"),
        ("loopbench/hitl-gate-v1", "LB-HITL-2"),
        ("loopbench/safety-constrained-v1", "LB-SAFE-2"),
    ]
    for env_id, task_id in cases:
        try:
            env = lg.make(env_id)
        except ValueError:
            print(f"SKIP: {env_id} not in installed loopgym (publish loopgym 0.1.3+)")
            continue
        result = env.run_episode(task_id=task_id, seed=42)
        if "success" not in result:
            print(f"FAIL: {env_id} missing success", file=sys.stderr)
            return 1
        print(f"OK {env_id} task={task_id} success={result['success']}")

    print("OK simenv_smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
