#!/usr/bin/env python3
"""Validate all LSS example YAML files under examples/."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"

# Import sibling module
sys.path.insert(0, str(REPO_ROOT / "tools"))
from validate_lss import DEFAULT_SCHEMA, load_schema, load_yaml, validate_spec  # noqa: E402


def main() -> int:
    schema = load_schema(DEFAULT_SCHEMA)
    yaml_files = sorted(EXAMPLES_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files in {EXAMPLES_DIR}", file=sys.stderr)
        return 1

    failed = 0
    for path in yaml_files:
        spec = load_yaml(path)
        errors = validate_spec(spec, schema)
        if errors:
            failed += 1
            print(f"INVALID: {path}", file=sys.stderr)
            for msg in errors:
                print(f"  - {msg}", file=sys.stderr)
        else:
            print(f"VALID: {path} ({spec.get('loop_name')})")

    if failed:
        print(f"\n{failed}/{len(yaml_files)} example(s) failed validation", file=sys.stderr)
        return 1

    print(f"\nAll {len(yaml_files)} example(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
