#!/usr/bin/env python3
"""Validate Loop Trace 1.0 export rows against schema/record-v0.3.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "record-v0.3.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate LoopNet v0.3 trace export row JSON")
    parser.add_argument("row", type=Path, help="Row JSON file from loopnet_export_trace.py")
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    row = json.loads(args.row.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(row), key=lambda e: list(e.path))
    if errors:
        for err in errors:
            path = ".".join(str(p) for p in err.path)
            loc = path or "<root>"
            print(f"INVALID {loc}: {err.message}", file=sys.stderr)
        return 1
    print(f"OK: {args.row.name} (schema_version={row.get('metadata.schema_version')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
