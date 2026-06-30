#!/usr/bin/env python3
"""Adoption wave 14 — unified le-loop-stack 0.2 + agent map + popular LoopBench tasks."""

from __future__ import annotations

DISCUSSION_10 = """## Adoption wave 14 — one install, any agent, compact JSON

```bash
pip install "le-loop-stack>=0.2.0"

# 10-second path (token-efficient compact JSON out)
loop quick "Fix failing tests from CI" --agent aider

# Full agent map + export
loopctl agent map --harness langgraph --intent "Parallel branches with merge" -o graph.yaml --export --json

# New LoopBench tasks for popular patterns
loopctl bench run --task LB-REACT-1 --spec mapped.yaml --seeds 0,1,2,3,4 -o results.json
loopctl bench run --task LB-GRAPH-1 --spec graph.yaml --seeds 0,1,2,3,4 -o results.json
loopctl bench run --task LB-CREW-1 --spec crew.yaml --seeds 0,1,2,3,4 -o results.json
```

**New tasks:** LB-REACT-1 · LB-GRAPH-1 · LB-CREW-1 · LB-REFLEX-1 · LB-AUTO-1

**Agents:** `loopctl agent list` — langgraph, crewai, react, reflexion, dspy, aider, openhands, smolagents, …

No repo clone required — loop library bundled in PyPI.
"""

ISSUE_4 = """## Wave 14 — popular loop tasks + agent map CLI

LoopBench now scores ReAct, LangGraph routing, CrewAI crews, Reflexion memory, and long-horizon autonomy:

| Task | Pattern | Agent preset |
|------|---------|--------------|
| LB-REACT-1 | tool-loop | `react`, `smolagents`, `openai_agents` |
| LB-GRAPH-1 | state-graph | `langgraph` |
| LB-CREW-1 | sequential crew | `crewai` |
| LB-REFLEX-1 | episodic memory | `reflexion` |
| LB-AUTO-1 | plan-execute | `openhands`, `autogpt` |

```bash
pip install "le-loop-stack>=0.2.0"
loopctl agent map --harness react --intent "Tool loop until goal" -o spec.yaml --json
loopctl bench run --task LB-REACT-1 --spec spec.yaml --seeds 0,1,2,3,4 -o results.json
```

First **non-maintainer** row on any task counts.
"""


def main() -> int:
    print("=== Discussion #10 ===\n", DISCUSSION_10)
    print("=== Issue #4 ===\n", ISSUE_4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
