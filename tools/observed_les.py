#!/usr/bin/env python3
"""Compute observed LES dimensions from Loop Trace 1.0 JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loopctl.scoring.observed import score_trace  # noqa: E402
from loopctl.scoring.structural import load_spec  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Observed LES from Loop Trace 1.0 JSON")
    parser.add_argument("trace", type=Path, help="Trace JSON path")
    parser.add_argument("--spec", type=Path, help="Optional LSS spec for structural comparison")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trace = json.loads(args.trace.read_text(encoding="utf-8"))
    spec = load_spec(args.spec) if args.spec else None

    report = score_trace(trace, spec)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Observed LES: {report['observed_les']:.1f}")
        if report.get("structural_les") is not None:
            print(f"Structural LES: {report['structural_les']:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
