#!/usr/bin/env python3
"""Validate LSS YAML specifications against specs/lss-1.0.schema.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonschema
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "specs" / "lss-1.0.schema.json"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Root element must be a mapping: {path}")
    return data


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_spec(spec: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda e: list(e.absolute_path))
    messages: list[str] = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        messages.append(f"{path}: {err.message}")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an LSS YAML file against specs/lss-1.0.schema.json",
    )
    parser.add_argument("spec", type=Path, help="Path to LSS YAML file")
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help="Path to JSON Schema",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if not args.spec.exists():
        print(f"Error: spec not found: {args.spec}", file=sys.stderr)
        return 2
    if not args.schema.exists():
        print(f"Error: schema not found: {args.schema}", file=sys.stderr)
        return 2

    try:
        spec = load_yaml(args.spec)
        schema = load_schema(args.schema)
        errors = validate_spec(spec, schema)
    except (yaml.YAMLError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    valid = len(errors) == 0
    if args.json:
        print(
            json.dumps(
                {
                    "valid": valid,
                    "spec": str(args.spec),
                    "schema": str(args.schema),
                    "loop_name": spec.get("loop_name"),
                    "errors": errors,
                },
                indent=2,
            )
        )
    elif valid:
        print(f"VALID: {args.spec}")
        print(f"  loop_name: {spec.get('loop_name')}")
        print(f"  version:   {spec.get('version')}")
    else:
        print(f"INVALID: {args.spec}", file=sys.stderr)
        for msg in errors:
            print(f"  - {msg}", file=sys.stderr)

    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
