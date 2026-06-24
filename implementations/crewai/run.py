#!/usr/bin/env python3
"""Smoke test for CrewAI composition bridge (no API keys)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "implementations" / "crewai"))

from parallel_crew import run_parallel_crew  # noqa: E402


def main() -> int:
    result = run_parallel_crew(
        task="Should we ship composed-loop beta to 10% of users?",
        quality_threshold=0.75,
    )
    print(f"success={result['success']} branches={len(result['branches'])} score={result['quality_score']:.2f}")
    print(f"dissent={result.get('dissent', [])}")
    print("LSS 1.1 mapping: agents->workers, tasks->sequential children, parallel crews->composition.parallel")
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
