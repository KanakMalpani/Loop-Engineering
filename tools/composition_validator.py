#!/usr/bin/env python3
"""Validate composition blocks in LSS specs (LSS 1.1 draft)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "loop-library"
COMP_TYPES = {"sequential", "parallel", "nested"}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping: {path}")
    return data


def resolve_ref(spec_path: Path, ref: str) -> Path:
    raw = ref.strip()
    if raw.startswith("loop-library/"):
        return ROOT / raw
    return (spec_path.parent / raw).resolve()


def validate_composition(spec_path: Path, spec: dict) -> list[str]:
    comp = spec.get("composition")
    if not comp:
        return []

    errors: list[str] = []
    ctype = comp.get("type")
    if ctype not in COMP_TYPES:
        errors.append(f"composition.type must be one of {sorted(COMP_TYPES)}")
        return errors

    children = comp.get("children")
    if not isinstance(children, list) or len(children) < 2:
        errors.append("composition.children must list at least 2 child refs")
        return errors

    ids: set[str] = set()
    roles: dict[str, str] = {}
    for i, child in enumerate(children):
        if not isinstance(child, dict):
            errors.append(f"composition.children[{i}] must be a mapping")
            continue
        cid = child.get("id")
        ref = child.get("ref")
        if not cid or not ref:
            errors.append(f"composition.children[{i}] requires id and ref")
            continue
        if cid in ids:
            errors.append(f"duplicate child id: {cid}")
        ids.add(cid)
        role = child.get("role", "stage")
        roles[cid] = role
        target = resolve_ref(spec_path, ref)
        if not target.exists():
            errors.append(f"child ref not found: {ref} -> {target}")
        elif target.suffix in {".yaml", ".yml"}:
            try:
                child_spec = load_yaml(target)
                if not child_spec.get("loop_name"):
                    errors.append(f"child {cid} missing loop_name: {ref}")
            except (yaml.YAMLError, ValueError) as exc:
                errors.append(f"child {cid} unreadable: {exc}")

    if ctype == "nested":
        outer = [c for c in children if c.get("role") == "outer"]
        inner = [c for c in children if c.get("role") == "inner"]
        if len(outer) != 1 or len(inner) < 1:
            errors.append("nested composition requires exactly one outer and >=1 inner child")

    adapters = comp.get("adapters") or []
    if ctype == "sequential" and len(adapters) < len(children) - 1:
        errors.append(
            f"sequential composition should declare >= {len(children) - 1} adapters "
            f"(got {len(adapters)})"
        )
    if ctype == "nested" and not adapters:
        errors.append("nested composition requires at least one adapter (outer -> inner)")

    for j, adapter in enumerate(adapters):
        if not isinstance(adapter, dict):
            errors.append(f"composition.adapters[{j}] must be a mapping")
            continue
        if not adapter.get("from") or not adapter.get("to"):
            errors.append(f"composition.adapters[{j}] requires from and to")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate LSS composition blocks")
    parser.add_argument("spec", type=Path, nargs="?", help="Single spec path")
    parser.add_argument(
        "--library",
        action="store_true",
        help="Validate all loop-library/compositions/*.yaml",
    )
    args = parser.parse_args()

    paths: list[Path] = []
    if args.library:
        comp_dir = LIB / "compositions"
        paths = sorted(comp_dir.glob("*.yaml"))
    elif args.spec:
        paths = [args.spec]
    else:
        parser.error("Provide a spec path or --library")

    failed = 0
    for path in paths:
        try:
            spec = load_yaml(path)
            errors = validate_composition(path, spec)
        except (yaml.YAMLError, ValueError) as exc:
            errors = [str(exc)]
        if errors:
            failed += 1
            print(f"INVALID: {path}", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
        elif spec.get("composition"):
            print(f"OK: {path.name} ({spec['composition'].get('type')})")

    if failed:
        print(f"\nFAILED: {failed}/{len(paths)}", file=sys.stderr)
        return 1
    print(f"OK: {len(paths)} composition spec(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
