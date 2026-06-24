#!/usr/bin/env python3
"""Generate composed loop-library specs (LSS 1.0 + composition block)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from composition_templates import orchestrator_shell  # noqa: E402

OUT = ROOT / "loop-library" / "compositions"

SPECS = [
    {
        "name": "research-to-writing",
        "objective": "Synthesize research into a publication-ready document via sequential research then writing loops.",
        "level": 3,
        "les": 81,
        "pass_threshold": 0.84,
        "max_iterations": 15,
        "cumulative_usd": 6.0,
        "composition": {
            "type": "sequential",
            "children": [
                {"id": "research", "ref": "../research-agent.yaml", "role": "stage"},
                {"id": "writing", "ref": "../writing-assistant.yaml", "role": "stage"},
            ],
            "adapters": [
                {
                    "from": "children.research.outputs.synthesizer",
                    "to": "children.writing.inputs.task",
                },
            ],
        },
    },
    {
        "name": "startup-to-strategy",
        "objective": "Validate startup hypotheses then produce strategy memo from falsification ledger.",
        "level": 3,
        "les": 77,
        "pass_threshold": 0.82,
        "max_iterations": 12,
        "cumulative_usd": 5.0,
        "composition": {
            "type": "sequential",
            "children": [
                {"id": "validate", "ref": "../startup-validator.yaml", "role": "stage"},
                {"id": "strategy", "ref": "../business-strategy-agent.yaml", "role": "stage"},
            ],
            "adapters": [
                {
                    "from": "children.validate.outputs.judge",
                    "to": "children.strategy.inputs.task",
                },
            ],
        },
    },
    {
        "name": "code-debug-repair",
        "objective": "Implement a change with coding-agent; on test failure invoke nested autonomous-debugger until suite passes.",
        "level": 4,
        "les": 86,
        "pass_threshold": 0.88,
        "max_iterations": 18,
        "cumulative_usd": 7.0,
        "composition": {
            "type": "nested",
            "children": [
                {"id": "build", "ref": "../coding-agent.yaml", "role": "outer"},
                {
                    "id": "repair",
                    "ref": "../autonomous-debugger.yaml",
                    "role": "inner",
                    "trigger": "children.build.evaluators.test_suite.failed",
                },
            ],
            "adapters": [
                {
                    "from": "children.build.outputs.implementer",
                    "to": "children.repair.inputs.task",
                },
            ],
        },
    },
    {
        "name": "research-code-nest",
        "objective": "Research a technical approach then nest coding-agent to produce a verified prototype implementation.",
        "level": 4,
        "les": 84,
        "pass_threshold": 0.86,
        "max_iterations": 16,
        "cumulative_usd": 7.5,
        "composition": {
            "type": "nested",
            "children": [
                {"id": "research", "ref": "../research-agent.yaml", "role": "outer"},
                {
                    "id": "implement",
                    "ref": "../coding-agent.yaml",
                    "role": "inner",
                    "trigger": "children.research.evaluators.coherence_rubric.passed",
                },
            ],
            "adapters": [
                {
                    "from": "children.research.outputs.synthesizer",
                    "to": "children.implement.inputs.task",
                },
            ],
        },
    },
    {
        "name": "scenario-swarm-rehearsal",
        "objective": (
            "Rehearse a high-stakes decision by running parallel worldview branches "
            "(falsifier, evidence, operator) then merge into a forecast brief with dissent preserved."
        ),
        "level": 4,
        "les": 83,
        "pass_threshold": 0.80,
        "max_iterations": 14,
        "cumulative_usd": 8.0,
        "composition": {
            "type": "parallel",
            "merge": {
                "strategy": "consensus_rubric",
                "min_branches_pass": 2,
                "preserve_dissent": True,
            },
            "children": [
                {
                    "id": "falsifier",
                    "ref": "../startup-validator.yaml",
                    "role": "branch",
                    "lens": "Pre-mortem branch: assume the plan FAILS. Design falsification experiments and kill criteria.",
                },
                {
                    "id": "evidence",
                    "ref": "../research-agent.yaml",
                    "role": "branch",
                    "lens": "Evidence branch: gather sourced facts, counter-narratives, and uncertainty bounds.",
                },
                {
                    "id": "operator",
                    "ref": "../business-strategy-agent.yaml",
                    "role": "branch",
                    "lens": "Operator branch: produce a 90-day action memo regardless of optimism level.",
                },
            ],
            "adapters": [],
        },
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for cfg in SPECS:
        comp = cfg["composition"]
        yaml_text = orchestrator_shell(
            cfg["name"],
            cfg["objective"],
            cfg["level"],
            cfg["les"],
            comp,
            pass_threshold=cfg["pass_threshold"],
            max_iterations=cfg["max_iterations"],
            cumulative_usd=cfg["cumulative_usd"],
        )
        path = OUT / f"{cfg['name']}.yaml"
        path.write_text(yaml_text, encoding="utf-8")
        print(f"Wrote {path.name} ({comp['type']}, {len(comp['children'])} children)")


if __name__ == "__main__":
    main()
