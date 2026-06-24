#!/usr/bin/env python3
"""Load LoopNet v0.2 from Hugging Face and print corpus summary stats."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.loopnet_fields import (  # noqa: E402
    field_histogram,
    iteration_count,
    oracle_level,
    primary_pattern,
)


def save_histograms(rows: list[dict], out_dir: Path) -> list[Path]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Install optional plots: pip install matplotlib") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    charts = [
        (lambda r: oracle_level(r), "LoopNet v0.2 — taxonomy level (pattern oracle)", "taxonomy_level.png"),
        (lambda r: str(r.get("termination_reason", "unknown")), "LoopNet v0.2 — termination reason", "termination_reason.png"),
        (primary_pattern, "LoopNet v0.2 — primary pattern (top 12)", "pattern.png"),
    ]

    for field_fn, title, filename in charts:
        counts = field_histogram(rows, field_fn)
        items = counts.most_common(12 if "pattern" in filename else 20)
        if not items:
            continue
        labels, values = zip(*items)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(range(len(labels)), values, color="#4a7c59")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.set_title(title)
        ax.set_ylabel("count")
        fig.tight_layout()
        path = out_dir / filename
        fig.savefig(path, dpi=120)
        plt.close(fig)
        written.append(path)

    lengths = [iteration_count(r) for r in rows]
    if lengths:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(lengths, bins=min(20, max(5, len(set(lengths)))), color="#3d5a80", edgecolor="white")
        ax.set_title("LoopNet v0.2 — iteration count per record")
        ax.set_xlabel("iterations")
        ax.set_ylabel("records")
        fig.tight_layout()
        path = out_dir / "iteration_length.png"
        fig.savefig(path, dpi=120)
        plt.close(fig)
        written.append(path)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Explore LoopNet v0.2 corpus stats")
    parser.add_argument(
        "--plot-dir",
        type=Path,
        default=None,
        help="Write histogram PNGs here (requires matplotlib)",
    )
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError:
        print("Install: pip install datasets", file=sys.stderr)
        return 1

    print("Loading KanakMalpani/loopnet-v0.2 from Hugging Face...")
    ds = load_dataset("KanakMalpani/loopnet-v0.2", split="train")
    rows = [dict(row) for row in ds]

    n = len(rows)
    print(f"\n=== LoopNet v0.2 Tier 1 ===")
    print(f"Records: {n}")

    if n == 0:
        print("Empty dataset split.")
        return 0

    print(f"Columns: {', '.join(ds.column_names)}")

    for label, field_fn in (
        ("primary pattern", primary_pattern),
        ("taxonomy level (oracle)", oracle_level),
        ("termination_reason", lambda r: str(r.get("termination_reason", "?"))),
    ):
        counts = field_histogram(rows, field_fn)
        top = counts.most_common(8)
        print(f"\n{label} (top):")
        for k, c in top:
            print(f"  {k}: {c}")

    lengths = [iteration_count(r) for r in rows]
    if lengths:
        avg = sum(lengths) / len(lengths)
        print(f"\nIteration count: min={min(lengths)}, max={max(lengths)}, avg={avg:.1f}")

    if args.plot_dir is not None:
        try:
            paths = save_histograms(rows, args.plot_dir)
            if paths:
                print(f"\nWrote {len(paths)} histogram(s) to {args.plot_dir}/")
                for p in paths:
                    print(f"  {p.name}")
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    print("\nDone. See research/LOOPNET.md for full guide.")
    print(
        "\nNext steps:\n"
        "  Beat maintainer LES: contributions/BEAT_LB-CR-1.md\n"
        "  Reproduction report: https://github.com/KanakMalpani/Loop-Engineering/discussions/10\n"
        "  LoopBench submit: https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
