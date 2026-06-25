# LangGraph ↔ LSS 1.1 Composition Bridge

**Runnable pack (Phase 10):** [examples/integrate-langgraph/](../examples/integrate-langgraph/) — `python examples/integrate-langgraph/run_demo.py`

**System:** LangGraph StateGraph reflection loop  
**Pattern:** reflection-loop (Level 2) · composable to LSS 1.1 `composition` blocks  
**Harness:** [implementations/langgraph/](../implementations/langgraph/)

---

## Tuple L = (S, A, O, T, E, M, τ)

| Component | LangGraph | LSS 1.0 / 1.1 |
|-----------|-----------|----------------|
| **S** State | `ReflectionState` TypedDict | `workers[].state_schema` |
| **A** Actors | `act`, `reflect` nodes | `workers` |
| **O** Observation | node outputs in state | `evaluators[].inputs` |
| **T** Transition | `add_edge`, `add_conditional_edges` | `composition.adapters` |
| **E** Evaluator | `_should_continue` → END | `evaluators` + `termination_conditions` |
| **M** Memory | `history` list in state | `memory` block |
| **τ** Termination | quality threshold or max iterations | `termination_conditions` |

---

## LSS 1.1 composition mapping (RFC #11)

For multi-node graphs, map to:

```yaml
composition:
  type: sequential
  children:
    - id: act
      ref: loop-library/coding-agent.yaml
      role: stage
    - id: reflect
      ref: loop-library/research-agent.yaml
      role: stage
  adapters:
    - from: children.act.outputs.draft
      to: children.reflect.inputs.task
```

| LangGraph concept | LSS 1.1 field |
|-------------------|---------------|
| `StateGraph` nodes | `composition.children` |
| Edges / routing | `composition.adapters` |
| Parallel branches | `type: parallel` + `merge` |
| Subgraph | `type: nested` |

See [RFC-LSS-1.1-composition.md](../contributions/RFC-LSS-1.1-composition.md) · [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11).

---

## LES (structural)

| Dimension | Score (0–1) | Notes |
|-----------|-------------|-------|
| Effectiveness | 0.85 | Mock LLM; replace with LiveEnv for LES_obs |
| Speed | 0.90 | 2-node graph, low fan-out |
| Cost | 0.95 | No API keys in smoke path |
| Autonomy | 0.80 | Conditional loop until threshold |
| **Composite (structural)** | **~82** | Run `les_calculator` on mapped YAML |

---

## Reproduce (no API keys)

```bash
pip install -r implementations/langgraph/requirements.txt
python implementations/langgraph/run.py
python implementations/langgraph/reflection_graph.py
```

---

## LoopBench path

After mapping your LangGraph harness to LSS YAML:

```bash
pip install "loopbench>=0.1.1"
loopbench run --task LB-CR-1 --spec your-mapped.yaml --seeds 0,1,2,3,4 -o results.json
```

See [BEAT_LB-CR-1.md](../contributions/BEAT_LB-CR-1.md).

---

## References

- [cursor-agent-loop.md](cursor-agent-loop.md) — Cursor IDE mapping
- [BRIDGE_AGENT_HARNESSES.md](../contributions/BRIDGE_AGENT_HARNESSES.md)
- LangGraph outreach: [#8186](https://github.com/langchain-ai/langgraph/issues/8186)
