# LE-OP-21 — Multi-Harness LES Comparison Pilot

**Status:** v0.2 artifact (June 2026)  
**Artifacts:**
- Structural: [le-op-21-harness-compare-v0.1.json](../benchmarks/results/le-op-21-harness-compare-v0.1.json)
- Structural + observed proxy: [le-op-21-harness-compare-v0.2.json](../benchmarks/results/le-op-21-harness-compare-v0.2.json)

---

## Reproduce

```bash
python tools/harness_compare.py
python tools/harness_compare.py --v01   # structural only
```

---

## Harness mappings

| Harness | LSS proxy spec | Observed proxy |
|---------|----------------|----------------|
| Cursor Agent | [coding-agent.yaml](../loop-library/coding-agent.yaml) | `loopbench/code-repair-v1` SimEnv episode |
| LangGraph | [research-agent.yaml](../loop-library/research-agent.yaml) | [langgraph/run.py](../implementations/langgraph/run.py) smoke |
| CrewAI | [research-agent.yaml](../loop-library/research-agent.yaml) | [crewai/run.py](../implementations/crewai/run.py) smoke |

See case studies: [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md) · [crewai-composition-bridge.md](../case-studies/crewai-composition-bridge.md)

---

## Next steps (LE-OP-21 full)

- LiveEnv observed LES per harness
- LB-COMP-1 cross-harness comparison
- Cross-org comparability report (2028 roadmap)

See [RESEARCH_ROADMAP.md](../contributions/RESEARCH_ROADMAP.md).
