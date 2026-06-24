# LE-OP-21 — Multi-Harness Structural LES Pilot (v0.1)

**Status:** Pilot artifact (June 2026)  
**Artifact:** [le-op-21-harness-compare-v0.1.json](../benchmarks/results/le-op-21-harness-compare-v0.1.json)

---

## Goal

Compare **structural LES** for the same research-loop LSS spec as mapped through three agent harness narratives (Cursor, LangGraph, CrewAI).

---

## Reproduce

```bash
python tools/harness_compare.py
python tools/harness_compare.py --output benchmarks/results/le-op-21-harness-compare-v0.1.json
```

---

## Harness mappings

| Harness | LSS proxy spec | Case study |
|---------|----------------|------------|
| Cursor Agent | [coding-agent.yaml](../loop-library/coding-agent.yaml) | [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md) |
| LangGraph | [research-agent.yaml](../loop-library/research-agent.yaml) | [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md) |
| CrewAI | [research-agent.yaml](../loop-library/research-agent.yaml) | [crewai-composition-bridge.md](../case-studies/crewai-composition-bridge.md) |

Composition extensions (LB-COMP-1) are documented in bridge case studies; this pilot uses atomic specs for apples-to-apples structural comparison.

---

## Next steps (LE-OP-21 full)

- Observed LES via LiveEnv per harness
- Composition-aware harness specs (parallel branches)
- Cross-harness benchmark on LB-COMP-1

See [RESEARCH_ROADMAP.md](../contributions/RESEARCH_ROADMAP.md) · [open-problems.md](open-problems.md).
