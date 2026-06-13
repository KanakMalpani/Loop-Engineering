# LangGraph Implementation

Reflection and verification loops as [LangGraph](https://github.com/langchain-ai/langgraph) state graphs.

---

## Install

```bash
pip install -r implementations/langgraph/requirements.txt
```

Optional: `langgraph` for live graphs; mock path works without it.

---

## Files

| File | Description |
|------|-------------|
| `reflection_graph.py` | Level-2 reflection loop as StateGraph |
| `requirements.txt` | Pin langgraph, langchain-core |

---

## Usage

```python
from reflection_graph import build_reflection_graph, run_reflection_graph

graph = build_reflection_graph(max_iterations=3, quality_threshold=0.8)
result = run_reflection_graph(
    graph,
    task="Summarize loop engineering",
    objective="Clear, accurate summary",
)
print(result.output, result.quality_score)
```

---

## LSS Mapping

| LSS | LangGraph |
|-----|-----------|
| workers | graph nodes |
| evaluators | conditional edges / eval nodes |
| memory | graph state (TypedDict) |
| termination_conditions | edge to END |

Generate diagram from spec:

```bash
python tools/loop_diagram_generator.py standards/examples/minimal-loop.yaml -o out.mmd
```

See [generic/loop_runtime.py](../generic/loop_runtime.py) for spec-first development.
