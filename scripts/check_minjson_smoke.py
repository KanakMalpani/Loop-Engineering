#!/usr/bin/env python3
"""Smoke LSS-min JSON export and token budget on combine."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from loopforge.combine import combine_loops
    from loopforge.compact import estimate_tokens, to_minjson
    from loopforge.export import export_minjson

    spec, meta = combine_loops(
        "budget-smoke",
        "Fix tests with minimal tokens",
        library_names=["research-agent", "coding-agent", "autonomous-debugger"],
        flatten=True,
        compact=True,
        validate=False,
        max_tokens=1200,
    )
    if not meta.get("token_budget"):
        print("FAIL: expected token_budget metadata", file=sys.stderr)
        return 1
    if estimate_tokens(spec) > 1200:
        print(f"FAIL: tokens {estimate_tokens(spec)} exceed budget 1200", file=sys.stderr)
        return 1

    minjson = to_minjson(spec)
    if not minjson.get("workers") or not minjson.get("evaluators"):
        print("FAIL: minjson missing core fields", file=sys.stderr)
        return 1
    full_len = len(json.dumps(spec))
    min_len = len(json.dumps(minjson))
    if min_len >= full_len:
        print(f"WARN: minjson not smaller ({min_len} vs {full_len})")

    with tempfile.TemporaryDirectory() as tmp:
        yaml_path = Path(tmp) / "spec.yaml"
        import yaml

        yaml_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
        out = export_minjson(yaml_path)
        if not out.is_file():
            print("FAIL: export_minjson", file=sys.stderr)
            return 1

    print(f"OK minjson_smoke tokens={estimate_tokens(spec)} min_ratio={round(min_len/max(1,full_len),2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
