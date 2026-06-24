#!/usr/bin/env python3
"""LE-OP-21 pilot: structural + observed LES across harness mappings."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HARNESS_SPECS = {
    "cursor": {
        "harness": "Cursor Agent",
        "spec": ROOT / "loop-library" / "coding-agent.yaml",
        "case_study": "case-studies/cursor-agent-loop.md",
        "bridge": "contributions/BRIDGE_AGENT_HARNESSES.md#cursor-agent",
        "observed_cmd": [
            sys.executable,
            "-c",
            "import loopgym as lg; r=lg.make('loopbench/code-repair-v1').run_episode(task_id='cr-001', seed=0); print(r['quality_score'])",
        ],
    },
    "langgraph": {
        "harness": "LangGraph",
        "spec": ROOT / "loop-library" / "research-agent.yaml",
        "case_study": "case-studies/langgraph-composition-bridge.md",
        "bridge": "implementations/langgraph/",
        "observed_cmd": [sys.executable, str(ROOT / "implementations" / "langgraph" / "run.py")],
    },
    "crewai": {
        "harness": "CrewAI",
        "spec": ROOT / "loop-library" / "research-agent.yaml",
        "case_study": "case-studies/crewai-composition-bridge.md",
        "bridge": "implementations/crewai/",
        "observed_cmd": [sys.executable, str(ROOT / "implementations" / "crewai" / "run.py")],
    },
}


def les_for_spec(spec_path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "les_calculator.py"), "--spec", str(spec_path), "--json"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def observed_les_proxy(meta: dict) -> float | None:
    cmd = meta.get("observed_cmd")
    if not cmd:
        return None
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        return None
    out = (result.stdout or "") + (result.stderr or "")
    if "observed_cmd" in meta and meta["harness"] == "Cursor Agent":
        try:
            return round(float(out.strip()) * 100, 1)
        except ValueError:
            pass
    match = re.search(r"score=([0-9.]+)", out)
    if match:
        return round(float(match.group(1)) * 100, 1)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="LE-OP-21 multi-harness LES comparison")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "benchmarks" / "results" / "le-op-21-harness-compare-v0.2.json",
    )
    parser.add_argument("--v01", action="store_true", help="Write v0.1 structural-only artifact")
    args = parser.parse_args()
    if args.v01:
        args.output = ROOT / "benchmarks" / "results" / "le-op-21-harness-compare-v0.1.json"

    entries = []
    for key, meta in HARNESS_SPECS.items():
        spec_path = meta["spec"]
        if not spec_path.exists():
            print(f"Missing spec: {spec_path}", file=sys.stderr)
            return 2
        les = les_for_spec(spec_path)
        entry = {
            "harness_id": key,
            "harness_name": meta["harness"],
            "lss_spec": str(spec_path.relative_to(ROOT)).replace("\\", "/"),
            "case_study": meta["case_study"],
            "bridge_doc": meta["bridge"],
            "les_structural": les["les"],
            "categories": les["categories"],
        }
        if not args.v01:
            obs = observed_les_proxy(meta)
            if obs is not None:
                entry["les_observed_proxy"] = obs
                entry["observed_source"] = "smoke_runner_or_loopgym_episode"
        entries.append(entry)

    pilot_id = "LE-OP-21-harness-compare-v0.1" if args.v01 else "LE-OP-21-harness-compare-v0.2"
    method = "tools/les_calculator.py --spec (structural LES-1.0)"
    if not args.v01:
        method += " + smoke runner quality_score proxy"

    payload = {
        "pilot_id": pilot_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "note": "LangGraph/CrewAI smoke scores; Cursor via code-repair-v1 SimEnv episode.",
        "harnesses": entries,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for e in entries:
        obs = e.get("les_observed_proxy")
        extra = f" obs={obs:.1f}" if obs is not None else ""
        print(f"  {e['harness_name']:12s} LES={e['les_structural']:.1f}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
