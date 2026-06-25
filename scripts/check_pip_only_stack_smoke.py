#!/usr/bin/env python3
"""Smoke test le-loop-stack meta install (Phase 11)."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    spec = ROOT / "loopctl" / "schemas" / "minimal-loop.yaml"
    with tempfile.TemporaryDirectory(prefix="le-stack-smoke-") as tmp:
        venv = Path(tmp) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        pip = venv / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
        py = venv / ("Scripts" if sys.platform == "win32" else "bin") / "python"

        steps = [
            [str(pip), "install", "-q", "-e", str(ROOT / "loopforge"), "-e", str(ROOT / "loopctl"), "loopgym"],
            [str(pip), "install", "-q", "-e", str(ROOT / "stack")],
            [str(py), "-m", "loopforge", "demo"],
            [str(py), "-m", "loopctl", "validate", str(spec)],
        ]
        for cmd in steps:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"FAIL: {' '.join(cmd)}", file=sys.stderr)
                print(proc.stderr or proc.stdout, file=sys.stderr)
                return proc.returncode

    print("OK: pip_only_stack_smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
