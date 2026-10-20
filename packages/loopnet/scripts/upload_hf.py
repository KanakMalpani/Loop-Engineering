#!/usr/bin/env python3
"""Prepare LoopNet corpus for HuggingFace Hub upload (optional)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSONL = ROOT / "data" / "seed" / "records.jsonl"
DEFAULT_PARQUET = ROOT / "data" / "seed" / "records.parquet"
DEFAULT_README = ROOT / "data" / "seed" / "README.md"


def write_dataset_card(
    readme_path: Path, *, repo_id: str, record_count: int | None = None
) -> None:
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    is_v02 = "v0.2" in repo_id or "loopnet-v0.2" in repo_id
    title = "LoopNet v0.2" if is_v02 else "LoopNet Seed v0.1"
    blurb = (
        "Seed corpus plus captured LoopGym trajectories for [LoopNet]"
        if is_v02
        else "Synthetic seed corpus for [LoopNet]"
    )
    cite_key = "loopnet_v02" if is_v02 else "loopnet_seed_v01"

    readme_path.write_text(
        f"""---
language:
- en
license: cc-by-4.0
task_categories:
- text-classification
- other
tags:
- loop-engineering
- agents
- benchmarks
size_categories:
- n<1K
---

# {title}

{blurb}(https://github.com/KanakMalpani/loopnet).

## Load

```python
from datasets import load_dataset

ds = load_dataset("{repo_id}", split="train")
```

Or from JSONL in this repo:

```python
ds = load_dataset("json", data_files="records.jsonl", split="train")
```

## Schema

Records conform to `ln/record-v1` (see `schema/loopnet-record-v1.json`).

## Records

{record_count or "See records.jsonl"} records in this release.

## Citation

```bibtex
@dataset{{{cite_key},
  title={{{title}}},
  year={{2026}},
  publisher={{Loop Engineering}}
}}
```
""",
        encoding="utf-8",
    )
    print(f"Wrote dataset card to {readme_path}")


def export_parquet(jsonl_path: Path, parquet_path: Path) -> None:
    try:
        import pandas as pd
    except ImportError as exc:
        raise SystemExit(
            "pandas and pyarrow required: pip install -e '.[dev]'"
        ) from exc

    records = []
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    frame = pd.json_normalize(records, sep=".")
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(parquet_path, index=False)
    print(f"Wrote {len(records)} records to {parquet_path}")


def upload_to_hub(
    repo_id: str,
    jsonl_path: Path,
    parquet_path: Path | None,
    readme_path: Path,
    *,
    private: bool,
) -> None:
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise SystemExit(
            "huggingface_hub required: pip install -e '.[dev]'"
        ) from exc

    api = HfApi()
    api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)

    api.upload_file(
        path_or_fileobj=str(jsonl_path),
        path_in_repo="records.jsonl",
        repo_id=repo_id,
        repo_type="dataset",
    )
    if parquet_path and parquet_path.exists():
        api.upload_file(
            path_or_fileobj=str(parquet_path),
            path_in_repo="records.parquet",
            repo_id=repo_id,
            repo_type="dataset",
        )
    api.upload_file(
        path_or_fileobj=str(readme_path),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset",
    )
    print(f"Uploaded dataset to https://huggingface.co/datasets/{repo_id}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL)
    parser.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--export-parquet", action="store_true")
    parser.add_argument("--upload", action="store_true")
    parser.add_argument("--repo-id", default="KanakMalpani/loopnet-seed-v0.1")
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args(argv)

    if not args.jsonl.exists():
        print(f"Missing JSONL file: {args.jsonl}", file=sys.stderr)
        return 1

    record_count = sum(
        1 for line in args.jsonl.read_text(encoding="utf-8").splitlines() if line.strip()
    )
    if args.parquet == DEFAULT_PARQUET and args.jsonl != DEFAULT_JSONL:
        args.parquet = args.jsonl.with_suffix(".parquet")
    if args.readme == DEFAULT_README and args.jsonl != DEFAULT_JSONL:
        args.readme = args.jsonl.parent / "README.md"

    write_dataset_card(args.readme, repo_id=args.repo_id, record_count=record_count)

    if args.export_parquet or args.upload:
        export_parquet(args.jsonl, args.parquet)

    if args.upload:
        upload_to_hub(
            args.repo_id,
            args.jsonl,
            args.parquet if args.parquet.exists() else None,
            args.readme,
            private=args.private,
        )
    else:
        print("Prepared local HuggingFace assets. Pass --upload to push to the Hub.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
