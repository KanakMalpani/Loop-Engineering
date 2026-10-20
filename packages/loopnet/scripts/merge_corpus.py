#!/usr/bin/env python3
"""Merge LoopNet seed corpus with captured real trajectories for v0.2 releases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "data" / "seed" / "records.jsonl"
DEFAULT_CAPTURED_DIR = ROOT / "data" / "captured"
DEFAULT_COMMUNITY_DIR = ROOT / "submissions" / "community"
DEFAULT_OUTPUT = ROOT / "data" / "v0.2" / "records.jsonl"
DEFAULT_SPLITS = ROOT / "data" / "v0.2" / "splits.json"


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def write_splits(records: list[dict], path: Path) -> None:
    splits = {
        "train": [r["record_id"] for r in records if r.get("split") == "train"],
        "val": [r["record_id"] for r in records if r.get("split") == "val"],
        "test": [r["record_id"] for r in records if r.get("split") == "test"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(splits, handle, indent=2)
        handle.write("\n")


def collect_jsonl_dir(directory: Path) -> list[dict]:
    records: list[dict] = []
    if not directory.exists():
        return records
    for path in sorted(directory.glob("*.jsonl")):
        if path.name.startswith("_"):
            continue
        records.extend(load_jsonl(path))
    return records


def collect_captured(captured_dir: Path) -> list[dict]:
    return collect_jsonl_dir(captured_dir)


def merge(seed: list[dict], *groups: list[dict]) -> list[dict]:
    seen = {r["record_id"] for r in seed}
    merged = list(seed)
    for group in groups:
        for record in group:
            if record["record_id"] in seen:
                raise ValueError(f"duplicate record_id: {record['record_id']}")
            seen.add(record["record_id"])
            merged.append(record)
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--captured-dir", type=Path, default=DEFAULT_CAPTURED_DIR)
    parser.add_argument(
        "--no-community",
        action="store_true",
        help="Skip submissions/community/*.jsonl",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--validate", action="store_true", help="Run validate_record.py on output")
    args = parser.parse_args(argv)

    if not args.seed.exists():
        print(f"Missing seed corpus: {args.seed}", file=sys.stderr)
        return 1

    seed = load_jsonl(args.seed)
    captured = collect_captured(args.captured_dir)
    community = [] if args.no_community else collect_jsonl_dir(DEFAULT_COMMUNITY_DIR)
    merged = merge(seed, captured, community)

    write_jsonl(merged, args.output)
    write_splits(merged, args.splits)

    failures = sum(1 for r in merged if r.get("outcome") == "failure")
    print(
        f"Merged {len(merged)} records -> {args.output} "
        f"(seed={len(seed)}, captured={len(captured)}, community={len(community)}, "
        f"failures={failures / len(merged):.1%})"
    )

    if args.validate:
        import subprocess

        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_record.py"),
                str(args.output),
            ],
            check=False,
        )
        if proc.returncode != 0:
            return proc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
