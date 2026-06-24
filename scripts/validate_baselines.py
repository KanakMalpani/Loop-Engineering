#!/usr/bin/env python3
"""Ensure LoopBench baseline JSON files include les_observed and les_structural."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = sorted((ROOT / "benchmarks" / "results").glob("lb-*-baseline.json"))


def check(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("results") or {}
    agg = results.get("aggregate") or {}
    if "les_observed" not in agg:
        errors.append(f"{path.name}: missing results.aggregate.les_observed")
    if "les_structural" not in results:
        errors.append(f"{path.name}: missing results.les_structural")
    else:
        structural = results["les_structural"]
        if "composite" not in structural and "source" not in structural:
            errors.append(f"{path.name}: les_structural needs composite or source")
    return errors


def main() -> int:
    if not BASELINES:
        print("No lb-*-baseline.json files found", file=sys.stderr)
        return 1
    all_errors: list[str] = []
    for path in BASELINES:
        all_errors.extend(check(path))
    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1
    print(f"OK: {len(BASELINES)} baseline files pass LES audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
