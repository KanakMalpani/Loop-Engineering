#!/usr/bin/env python3
"""Generate token-optimized flat pre-merged compositions for loop-library."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "loop-library" / "compositions" / "flat"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PRESETS = [
    {
        "file": "research-to-writing-flat.yaml",
        "loop_name": "research-to-writing-flat",
        "objective": "Synthesize research into a publication-ready document (flat pre-merge).",
        "library": ["research-agent", "writing-assistant"],
        "mode": "sequential",
        "source_composition": "research-to-writing",
    },
    {
        "file": "debug-repair-flat.yaml",
        "loop_name": "debug-repair-flat",
        "objective": "Implement change then auto-debug until tests pass (flat pre-merge).",
        "library": ["coding-agent", "autonomous-debugger"],
        "mode": "sequential",
        "source_composition": "code-debug-repair",
    },
    {
        "file": "scenario-swarm-rehearsal-flat.yaml",
        "loop_name": "scenario-swarm-rehearsal-flat",
        "objective": "Parallel worldview rehearsal then merged forecast (flat pre-merge).",
        "library": ["startup-validator", "research-agent", "business-strategy-agent"],
        "mode": "sequential",
        "source_composition": "scenario-swarm-rehearsal",
        "note": "Linearized flat merge of swarm branches (parallel composition refs remain in compositions/)",
    },
]


def main() -> int:
    from loopforge.combine import combine_loops, save_combined_spec
    from loopforge.validate import validate_spec

    OUT.mkdir(parents=True, exist_ok=True)
    for preset in PRESETS:
        spec, meta = combine_loops(
            preset["loop_name"],
            preset["objective"],
            library_names=preset["library"],
            mode=preset["mode"],
            flatten=True,
            compact=True,
            validate=False,
        )
        meta_block = spec.setdefault("metadata", {})
        if isinstance(meta_block, dict):
            meta_block["pre_merged"] = True
            meta_block["flat_source"] = preset["source_composition"]
            meta_block["estimated_tokens"] = meta.get("estimated_tokens")
        errors = validate_spec(spec, lss_version="1.0")
        if errors:
            print(f"WARN {preset['file']}: {errors[0]}", file=sys.stderr)
        path = OUT / preset["file"]
        save_combined_spec(spec, path, compact=True, validate=False)
        print(f"Wrote {path} (~{meta.get('estimated_tokens')} tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
