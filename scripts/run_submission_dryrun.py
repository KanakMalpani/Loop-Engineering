#!/usr/bin/env python3
"""End-to-end submission dry-run: intent → trace → observed LES."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "submission-dry-run"
PARTNER_DIR = OUT / "partner"

PARTNER_SPECS = {
    "agentless": "agentless-lb-cr-1.yaml",
    "aider": "aider-lb-cr-1.yaml",
    "openhands": "openhands-lb-cr-1.yaml",
}


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def partner_dryrun(partner: str) -> int:
    if partner not in PARTNER_SPECS:
        print(f"Unknown partner: {partner}. Choose: {', '.join(PARTNER_SPECS)}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    src = PARTNER_DIR / PARTNER_SPECS[partner]
    spec = OUT / f"partner-{partner}-lb-cr-1.yaml"
    row_out = OUT / f"partner-{partner}-row.json"
    shutil.copy(src, spec)

    run([sys.executable, "-m", "loopctl", "validate", str(spec)])

    template = json.loads((PARTNER_DIR / "entries-row-template.json").read_text(encoding="utf-8"))
    template["harness"] = partner
    template["notes"] = f"Partner stub ({partner}) — fill submitter, spec_path, spec_hash, results after loopbench run"
    template["repro_command"] = (
        f"loopbench run --task LB-CR-1 --spec {spec.name} --seeds 0,1,2,3,4 -o results.json"
    )
    row_out.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    summary = {
        "partner": partner,
        "spec": str(spec.relative_to(ROOT)),
        "entries_row_template": str(row_out.relative_to(ROOT)),
        "next_steps": [
            "loopbench run --task LB-CR-1 --spec " + spec.name + " --seeds 0,1,2,3,4 -o results.json",
            "loopbench validate results.json",
            "Fork LoopBench → add row to leaderboard/entries.json → open PR",
        ],
        "guide": "contributions/PARTNER_LOOPBENCH_SUBMIT.md",
        "note": "Partner dry-run — not counted as external adoption until non-maintainer merges",
    }
    (OUT / f"partner-{partner}-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Submission dry-run")
    parser.add_argument(
        "--partner",
        choices=sorted(PARTNER_SPECS),
        help="Use partner LSS stub (agentless, aider, openhands)",
    )
    args = parser.parse_args()

    if args.partner:
        return partner_dryrun(args.partner)

    OUT.mkdir(parents=True, exist_ok=True)
    spec = OUT / "dry-run-external.yaml"
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
    run([sys.executable, "scripts/generate_loopgym_trace_demo.py"])
    loopgym_trace = OUT / "trace-loopgym.json"
    trace = loopgym_trace if loopgym_trace.exists() else OUT / "trace.json"
    if not trace.exists():
        run([sys.executable, "scripts/generate_trace_demo.py"])
        trace = OUT / "trace.json"
    run([sys.executable, "-m", "loopctl", "trace", "validate", str(trace)])
    result = subprocess.run(
        [sys.executable, "tools/observed_les.py", str(trace), "--spec", str(spec), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    les.write_text(result.stdout, encoding="utf-8")
    run([sys.executable, "scripts/loopnet_export_trace.py", str(trace), "-o", str(loopnet)])

    loopnet_repo = ROOT.parent / "loopnet"
    validator = loopnet_repo / "scripts" / "validate_trace_export.py"
    if validator.exists():
        run([sys.executable, str(validator), str(loopnet)])
    else:
        print(f"skip loopnet validate (not found: {validator})")

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
