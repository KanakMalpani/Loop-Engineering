#!/usr/bin/env python3
"""Load LoopNet v0.2 from Hugging Face and print corpus summary stats."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets", file=sys.stderr)
        return 1

    print("Loading KanakMalpani/loopnet-v0.2 from Hugging Face...")
    ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")

    n = len(ds)
    print(f"\n=== LoopNet v0.2 Tier 1 ===")
    print(f"Records: {n}")

    if n == 0:
        print("Empty dataset split.")
        return 0

    cols = ds.column_names
    print(f"Columns: {', '.join(cols)}")

    # Summarize common fields when present
    for field in ("pattern", "taxonomy_level", "termination_reason"):
        if field in cols:
            values = ds[field]
            uniq = {}
            for v in values:
                key = str(v)
                uniq[key] = uniq.get(key, 0) + 1
            top = sorted(uniq.items(), key=lambda x: -x[1])[:8]
            print(f"\n{field} (top):")
            for k, c in top:
                print(f"  {k}: {c}")

    if "iterations" in cols:
        lengths = [len(row) if row else 0 for row in ds["iterations"]]
        if lengths:
            avg = sum(lengths) / len(lengths)
            print(f"\nIteration count: min={min(lengths)}, max={max(lengths)}, avg={avg:.1f}")

    print("\nDone. See research/LOOPNET.md for full guide.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
