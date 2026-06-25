#!/usr/bin/env python3
"""Compute Loop Engineering Score (LES-1.0) from an LSS spec or interactive input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "loopctl"))
sys.path.insert(0, str(ROOT))

from loopctl.scoring.structural import (  # noqa: E402
    CATEGORY_LABELS,
    LES_WEIGHTS,
    compute_les,
    format_report,
    load_spec,
)


def interactive_scores() -> dict[str, float]:
    print("Enter normalized scores (0.0–1.0) for each LES category.")
    scores: dict[str, float] = {}
    for category in LES_WEIGHTS:
        label = CATEGORY_LABELS[category]
        while True:
            raw = input(f"  {label} [{category}]: ").strip()
            if not raw:
                scores[category] = 0.5
                break
            try:
                val = float(raw)
                if 0.0 <= val <= 1.0:
                    scores[category] = val
                    break
            except ValueError:
                pass
            print("    Enter a number between 0.0 and 1.0")
    return scores


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute Loop Engineering Score (LES-1.0) from an LSS spec or interactive input",
    )
    parser.add_argument("--spec", type=Path, help="Path to LSS YAML specification")
    parser.add_argument(
        "--interactive", action="store_true", help="Enter category scores interactively"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.interactive:
        scores = interactive_scores()
        composite = sum(LES_WEIGHTS[c] * scores[c] for c in LES_WEIGHTS)
        les = round(composite * 100, 1)
        if args.json:
            print(json.dumps({"les": les, "categories": scores, "source": "interactive"}, indent=2))
        else:
            print(format_report("interactive", les, scores, "interactive input"))
        return 0

    if not args.spec:
        parser.error("Provide --spec PATH or use --interactive")

    spec = load_spec(args.spec)
    les, categories = compute_les(spec)
    loop_name = spec.get("loop_name", args.spec.stem)

    if args.json:
        print(
            json.dumps(
                {
                    "loop_name": loop_name,
                    "les": les,
                    "categories": categories,
                    "weights": LES_WEIGHTS,
                    "source": str(args.spec),
                },
                indent=2,
            )
        )
    else:
        print(format_report(loop_name, les, categories, str(args.spec)))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
