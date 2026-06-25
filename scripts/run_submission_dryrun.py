#!/usr/bin/env python3
"""End-to-end submission dry-run: intent → trace → observed LES."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "submission-dry-run"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    spec = OUT / "dry-run-external.yaml"
    trace = OUT / "trace.json"
    les = OUT / "observed-les.json"
    loopnet = OUT / "loopnet-row.json"

    run(
        [
            sys.executable,
            "-m",
            "loopforge",
            "intent",
            "Fix failing unit tests from CI logs",
            "-o",
            str(spec),
            "--suggest-level",
        ]
    )
    run([sys.executable, "-m", "loopctl", "validate", str(spec)])
    run([sys.executable, "scripts/generate_trace_demo.py"])
    run([sys.executable, "-m", "loopctl", "trace", "validate", str(trace)])
    run([sys.executable, "tools/observed_les.py", str(trace), "--spec", str(spec), "--json"])
    # Capture observed LES
    result = subprocess.run(
        [sys.executable, "tools/observed_les.py", str(trace), "--spec", str(spec), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    les.write_text(result.stdout, encoding="utf-8")
    run([sys.executable, "scripts/loopnet_export_trace.py", str(trace), "-o", str(loopnet)])

    summary = {
        "spec": str(spec.relative_to(ROOT)),
        "trace": str(trace.relative_to(ROOT)),
        "observed_les": json.loads(les.read_text()),
        "loopnet_row": json.loads(loopnet.read_text()),
        "note": "Maintainer dry-run — not counted as external adoption",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
