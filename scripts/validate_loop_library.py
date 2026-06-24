#!/usr/bin/env python3
"""Validate all loop-library/*.yaml against LSS 1.0 schema. Exit 1 on any failure."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "loop-library"
VALIDATOR = ROOT / "tools" / "loop_validator.py"


def main() -> int:
    if not VALIDATOR.exists():
        print(f"Error: validator not found: {VALIDATOR}", file=sys.stderr)
        return 2

    yaml_files = sorted(LIB.glob("*.yaml"))
    if not yaml_files:
        print(f"Error: no YAML files in {LIB}", file=sys.stderr)
        return 2

    failed: list[str] = []
    for path in yaml_files:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failed.append(path.name)
            print(result.stdout or result.stderr)

    if failed:
        print(f"\nFAILED: {len(failed)}/{len(yaml_files)} specs invalid", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1

    print(f"OK: all {len(yaml_files)} loop-library specs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
