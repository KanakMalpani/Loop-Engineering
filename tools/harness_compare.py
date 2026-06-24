#!/usr/bin/env python3
"""LE-OP-21 pilot: structural LES comparison across agent harness mappings."""

from __future__ import annotations

import argparse
import json
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
    },
    "langgraph": {
        "harness": "LangGraph",
        "spec": ROOT / "loop-library" / "research-agent.yaml",
        "case_study": "case-studies/langgraph-composition-bridge.md",
        "bridge": "implementations/langgraph/",
    },
    "crewai": {
        "harness": "CrewAI",
        "spec": ROOT / "loop-library" / "research-agent.yaml",
        "case_study": "case-studies/crewai-composition-bridge.md",
        "bridge": "implementations/crewai/",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="LE-OP-21 multi-harness structural LES pilot")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "benchmarks" / "results" / "le-op-21-harness-compare-v0.1.json",
    )
    args = parser.parse_args()

    entries = []
    for key, meta in HARNESS_SPECS.items():
        spec_path = meta["spec"]
        if not spec_path.exists():
            print(f"Missing spec: {spec_path}", file=sys.stderr)
            return 2
        les = les_for_spec(spec_path)
        entries.append(
            {
                "harness_id": key,
                "harness_name": meta["harness"],
                "lss_spec": str(spec_path.relative_to(ROOT)).replace("\\", "/"),
                "case_study": meta["case_study"],
                "bridge_doc": meta["bridge"],
                "les_structural": les["les"],
                "categories": les["categories"],
            }
        )

    payload = {
        "pilot_id": "LE-OP-21-harness-compare-v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "tools/les_calculator.py --spec (structural LES-1.0)",
        "note": "LangGraph and CrewAI mapped to research-agent.yaml; see case studies for composition extensions.",
        "harnesses": entries,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    for e in entries:
        print(f"  {e['harness_name']:12s} LES={e['les_structural']:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
