#!/usr/bin/env python3
"""Smoke test PyPI-native loopforge export (Phase 10)."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loopforge.export import export_stub  # noqa: E402

SPEC = ROOT / "loop-library" / "research-agent.yaml"
TARGETS = ("generic", "langgraph", "crewai")


def main() -> int:
    if not SPEC.exists():
        print(f"MISSING: {SPEC}", file=sys.stderr)
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="export-smoke-"))
    try:
        for target in TARGETS:
            out = tmp / target
            export_stub(SPEC, out, target)
            run_py = out / "run.py"
            readme = out / "README.md"
            spec = out / "spec.yaml"
            if not all(p.exists() for p in (run_py, readme, spec)):
                print(f"FAIL {target}: missing files", file=sys.stderr)
                return 1
            if "loopgym" not in run_py.read_text(encoding="utf-8"):
                print(f"FAIL {target}: run.py should reference loopgym", file=sys.stderr)
                return 1
            print(f"OK: export {target}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK: {len(TARGETS)} export target(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
