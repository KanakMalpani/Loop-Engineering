#!/usr/bin/env python3
"""Validate LoopNet records against loopnet-record-v1.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "loopnet-record-v1.json"


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_records(path: Path) -> list[dict]:
    if path.suffix == ".jsonl":
        records = []
        with path.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_no}: invalid JSON — {exc}") from exc
        return records

    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "records" in payload:
        return payload["records"]
    raise ValueError(f"{path}: expected JSONL, JSON array, or object with 'records' key")


def validate_records(
    records: list[dict],
    *,
    schema: dict | None = None,
    enforce_failure_ratio: bool = True,
) -> list[str]:
    schema = schema or load_schema()
    validator = Draft202012Validator(schema)
    errors: list[str] = []

    seen_ids: set[str] = set()
    failure_count = 0

    for index, record in enumerate(records):
        prefix = f"record[{index}]"
        record_id = record.get("record_id", "<missing>")
        prefix = f"{prefix} ({record_id})"

        for error in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
            path = ".".join(str(part) for part in error.path)
            location = f"{prefix}.{path}" if path else prefix
            errors.append(f"{location}: {error.message}")

        rid = record.get("record_id")
        if isinstance(rid, str):
            if rid in seen_ids:
                errors.append(f"{prefix}: duplicate record_id")
            seen_ids.add(rid)

        if record.get("outcome") == "failure":
            failure_count += 1

    if records and enforce_failure_ratio:
        failure_ratio = failure_count / len(records)
        if failure_ratio < 0.40:
            errors.append(
                f"corpus: failed loops are {failure_ratio:.1%} "
                f"({failure_count}/{len(records)}); require >= 40%"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[ROOT / "data" / "seed" / "records.jsonl"],
        help="JSONL files or directories containing *.jsonl records",
    )
    parser.add_argument(
        "--require-count",
        type=int,
        default=None,
        help="Fail if total record count differs from expected value",
    )
    parser.add_argument(
        "--skip-corpus-policy",
        action="store_true",
        help="Skip corpus-level failure-ratio check (for single captured files)",
    )
    args = parser.parse_args(argv)

    targets: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            targets.extend(sorted(path.glob("*.jsonl")))
        else:
            targets.append(path)

    if not targets:
        print("No record files found.", file=sys.stderr)
        return 1

    schema = load_schema()
    all_records: list[dict] = []
    for target in targets:
        if not target.exists():
            print(f"Missing file: {target}", file=sys.stderr)
            return 1
        all_records.extend(load_records(target))

    if args.require_count is not None and len(all_records) != args.require_count:
        print(
            f"Expected {args.require_count} records, found {len(all_records)}.",
            file=sys.stderr,
        )
        return 1

    errors = validate_records(
        all_records,
        schema=schema,
        enforce_failure_ratio=not args.skip_corpus_policy,
    )
    if errors:
        print(f"Validation failed ({len(errors)} issue(s)):", file=sys.stderr)
        for error in errors[:50]:
            print(f"  - {error}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        return 1

    failures = sum(1 for record in all_records if record.get("outcome") == "failure")
    print(
        f"OK: {len(all_records)} record(s) validated "
        f"({failures} failures, {failures / len(all_records):.1%})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
