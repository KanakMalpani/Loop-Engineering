#!/usr/bin/env python3
"""Run REPRODUCE.md steps and write a markdown report."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "reproduction-reports"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    return result.returncode, combined.strip()


def main() -> int:
    started = time.time()
    py = sys.executable
    sections: list[str] = []

    sections.append(f"# Reproduction report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    sections.append("")
    sections.append("**Source:** [REPRODUCE.md](../../contributions/REPRODUCE.md) independent replay")
    sections.append(f"**Python:** `{sys.version.split()[0]}`")
    sections.append("")

    rc, out = run([py, "--version"])
    sections.append("## Environment")
    sections.append("```")
    sections.append(out)
    rc2, pip_out = run([py, "-m", "pip", "show", "pyyaml", "jsonschema", "loopgym", "loopbench"])
    sections.append(pip_out or "(pip show empty)")
    sections.append("```")
    sections.append("")

    rc, out = run([py, "scripts/validate_loop_library.py"])
    sections.append("## Step 3 — validate_loop_library")
    sections.append("```")
    sections.append(out)
    sections.append("```")
    sections.append(f"Exit: {rc}")
    sections.append("")

    rc, out = run([py, "examples/reflection-loop/run.py"])
    sections.append("## Step 4 — reflection-loop")
    sections.append("```")
    sections.append(out[-1200:] if len(out) > 1200 else out)
    sections.append("```")
    sections.append(f"Exit: {rc}")
    sections.append("")

    les_path = OUT_DIR / "les-autonomous-debugger.json"
    rc, out = run(
        [py, "tools/les_calculator.py", "--spec", "loop-library/autonomous-debugger.yaml", "--json"]
    )
    if rc == 0:
        les_path.write_text(out + "\n", encoding="utf-8")
    sections.append("## Step 5 — LES JSON")
    sections.append("```json")
    sections.append(out[:2000] if out else "{}")
    sections.append("```")
    sections.append("")

    rc, out = run([py, "examples/loopnet-explore/explore.py"])
    sections.append("## Step 7 — LoopNet explore (optional)")
    sections.append("```")
    sections.append(out[-800:] if len(out) > 800 else out)
    sections.append("```")
    sections.append(f"Exit: {rc}")
    sections.append("")

    loopbench_exe = "loopbench"
    rc, out = run(
        [
            loopbench_exe,
            "run",
            "--task",
            "LB-CR-1",
            "--spec",
            "loop-library/autonomous-debugger.yaml",
            "--seeds",
            "0",
            "-o",
            str(OUT_DIR / "lb-cr-1-seed0.json"),
        ]
    )
    sections.append("## Step 6 — LoopBench LB-CR-1 (seed 0)")
    sections.append("```")
    sections.append(out)
    sections.append("```")
    sections.append(f"Exit: {rc}")
    sections.append("")

    elapsed = int(time.time() - started)
    all_ok = all(
        x == 0
        for x in [
            rc2 if False else 0,
            run([py, "scripts/validate_loop_library.py"])[0],
            run([py, "examples/reflection-loop/run.py"])[0],
        ]
    )
    val_rc = run([py, "scripts/validate_loop_library.py"])[0]
    refl_rc = run([py, "examples/reflection-loop/run.py"])[0]
    success = val_rc == 0 and refl_rc == 0 and les_path.exists()

    sections.append("## Summary")
    sections.append(f"- **Elapsed:** ~{elapsed // 60}m {elapsed % 60}s")
    sections.append(f"- **Success criteria met:** {'yes' if success else 'no'}")
    sections.append("- Validate LSS: " + ("pass" if val_rc == 0 else "fail"))
    sections.append("- Reflection loop: " + ("pass" if refl_rc == 0 else "fail"))
    sections.append("- LES JSON: " + ("pass" if les_path.exists() else "fail"))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = OUT_DIR / f"{stamp}-independent-replay.md"
    report_path.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(report_path)
    print("SUCCESS" if success else "PARTIAL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
