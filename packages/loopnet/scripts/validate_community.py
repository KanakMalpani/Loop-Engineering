#!/usr/bin/env python3
"""Validate community LoopNet submissions (submissions/community/*.jsonl)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "submissions" / "community"

# Obvious secret / path leak patterns
_FORBIDDEN = re.compile(
    r"(api[_-]?key|secret|password|Bearer\s|sk-[a-zA-Z0-9]{10,}|"
    r"[A-Za-z]:\\Users\\|/home/[a-z]+/)",
    re.IGNORECASE,
)


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
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


def check_community_policy(records: list[dict], *, path: Path) -> list[str]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    if _FORBIDDEN.search(raw):
        errors.append(f"{path}: possible secret or local path in file content")

    for index, record in enumerate(records):
        prefix = f"{path.name} record[{index}] ({record.get('record_id', '?')})"
        if record.get("source") != "community":
            errors.append(f"{prefix}: source must be 'community'")
        contributor = record.get("contributor") or {}
        handle = contributor.get("handle") if isinstance(contributor, dict) else None
        if not handle or not str(handle).strip():
            errors.append(f"{prefix}: missing contributor.handle")
        if record.get("split") not in ("train", "val", "test"):
            errors.append(f"{prefix}: split must be train, val, or test")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[DEFAULT_DIR],
        help="JSONL files or directory (default: submissions/community)",
    )
    args = parser.parse_args(argv)

    targets: list[Path] = []
    for path in args.paths:
        if path.is_dir():
            targets.extend(sorted(path.glob("*.jsonl")))
        else:
            targets.append(path)

    targets = [p for p in targets if p.name != "README.md" and not p.name.startswith("_")]
    if not targets:
        print("No community JSONL files found.", file=sys.stderr)
        return 1

    sys.path.insert(0, str(ROOT / "scripts"))
    from validate_record import load_records, load_schema, validate_records

    schema = load_schema()
    failed = False
    total = 0

    for target in targets:
        if not target.exists():
            print(f"Missing: {target}", file=sys.stderr)
            return 1
        records = load_records(target)
        total += len(records)
        schema_errors = validate_records(records, schema=schema, enforce_failure_ratio=False)
        policy_errors = check_community_policy(records, path=target)
        errors = schema_errors + policy_errors
        if errors:
            failed = True
            print(f"INVALID: {target} ({len(errors)} issue(s))", file=sys.stderr)
            for err in errors[:30]:
                print(f"  - {err}", file=sys.stderr)
        else:
            print(f"OK: {target} ({len(records)} community record(s))")

    if failed:
        return 1
    print(f"All {total} community record(s) passed validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
