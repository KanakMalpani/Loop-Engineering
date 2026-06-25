#!/usr/bin/env python3
"""Adoption wave 8 — LSS 1.1 stable + composition mapping outreach."""

from __future__ import annotations

LSS_11 = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/standards/LSS-1.1.md"
COMPOSE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/compositions/scenario-swarm-rehearsal.yaml"
BRIDGE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BRIDGE_AGENT_HARNESSES.md"
INTENT = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/All%20about%20loops/LOOP_FORGE.md"
PYPI = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PYPI_NAMING.md"

DISCUSSION_11 = f"""## Adoption wave 8 — LSS 1.1 composition mapping feedback

We stabilized **LSS 1.1** composition blocks (`sequential`, `parallel`, `nested`) and would like framework-specific feedback on how you map them today.

**Reference spec:** [scenario-swarm-rehearsal.yaml]({COMPOSE})  
**Standard:** [LSS-1.1.md]({LSS_11})  
**Bridge doc:** [BRIDGE_AGENT_HARNESSES.md]({BRIDGE})

### Quick map exercise

1. Pick a multi-agent workflow in your framework (LangGraph, CrewAI, AutoGen, custom).
2. Label each subgraph as sequential stage, parallel branch, or nested inner loop.
3. Note where **merge** / **adapter** semantics differ from LSS 1.1.
4. Reply here with: framework, 3–5 bullet mapping, one friction point.

### Tooling (optional)

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0"
loopforge intent "Parallel research and coding branches" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
python tools/composition_validator.py mapped.yaml
```

PyPI naming: {PYPI}  
Intent compiler: {INTENT}

**Done when:** first non-maintainer mapping comment on this thread.
"""

LANGGRAPH_8186 = f"""## LSS 1.1 composition <-> LangGraph subgraph mapping (wave 8)

Following up with a concrete composed spec: [scenario-swarm-rehearsal.yaml]({COMPOSE}).

We map:
- **parallel** → fan-out Send/API nodes + join reducer
- **sequential** → linear StateGraph edges with adapter-shaped state picks
- **nested** → subgraph node with inner compile()

RFC thread: https://github.com/KanakMalpani/Loop-Engineering/discussions/11

Happy to adjust the bridge doc if your team uses different merge semantics.
"""

CREWAI_6316 = f"""## LSS 1.1 composition <-> CrewAI crew mapping (wave 8)

CrewAI hierarchical vs sequential crews map cleanly to LSS `nested` vs `sequential` — see [BRIDGE_AGENT_HARNESSES.md]({BRIDGE}).

Example composed LSS: [scenario-swarm-rehearsal.yaml]({COMPOSE})  
RFC feedback welcome: https://github.com/KanakMalpani/Loop-Engineering/discussions/11
"""


def main() -> int:
    print("=== Discussion #11 ===\n", DISCUSSION_11)
    print("=== LangGraph #8186 ===\n", LANGGRAPH_8186)
    print("=== CrewAI #6316 ===\n", CREWAI_6316)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
