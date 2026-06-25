# LangGraph integration pack (Phase 10)

Map LSS 1.1 composition to LangGraph **StateGraph** nodes:

| LSS `composition.type` | LangGraph pattern |
|------------------------|-------------------|
| `sequential` | Linear edges between nodes; state picks adapter fields |
| `parallel` | Fan-out Send / branch nodes + join reducer |
| `nested` | Subgraph node compiling inner graph |

## Quick path

```bash
pip install "le-loopforge>=0.2.1" "le-loopctl>=0.1.1" loopgym
python examples/integrate-langgraph/run_demo.py
```

Or manually:

```bash
loopforge intent "Draft and critique with reflection" -o loop.yaml --suggest-level
loopforge export --spec loop.yaml --target langgraph --out ./my-graph/
python my-graph/run.py --json
```

Reference spec: [scenario-swarm-rehearsal.yaml](../../loop-library/compositions/scenario-swarm-rehearsal.yaml)

Case study: [langgraph-composition-bridge.md](../../case-studies/langgraph-composition-bridge.md)

RFC feedback: [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11)
