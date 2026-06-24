#!/usr/bin/env python3
"""Validate loop-library atomic and composed specs. Exit 1 on any failure."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "loop-library"
COMP = LIB / "compositions"
VALIDATOR = ROOT / "tools" / "loop_validator.py"
COMP_VALIDATOR = ROOT / "tools" / "composition_validator.py"


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out


def main() -> int:
    if not VALIDATOR.exists():
        print(f"Error: validator not found: {VALIDATOR}", file=sys.stderr)
        return 2

    yaml_files = sorted(LIB.glob("*.yaml"))
    comp_files = sorted(COMP.glob("*.yaml")) if COMP.is_dir() else []
    all_files = yaml_files + comp_files

    if not all_files:
        print(f"Error: no YAML files in {LIB}", file=sys.stderr)
        return 2

    failed: list[str] = []
    for path in all_files:
        code, out = run([sys.executable, str(VALIDATOR), str(path)])
        if code != 0:
            failed.append(path.name)
            print(out)

    if COMP_VALIDATOR.exists() and comp_files:
        code, out = run([sys.executable, str(COMP_VALIDATOR), "--library"])
        if code != 0:
            failed.append("composition-graph")
            print(out)

    if failed:
        print(f"\nFAILED: {len(failed)}/{len(all_files)} specs invalid", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1

    n_comp = len(comp_files)
    print(f"OK: {len(yaml_files)} atomic + {n_comp} composed specs valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
