# CrewAI integration pack (Phase 10)

| LSS `composition.type` | CrewAI pattern |
|------------------------|----------------|
| `sequential` | `Process.sequential` task chain |
| `parallel` | Multiple agents + merge task |
| `nested` | Hierarchical crew (manager + workers) |

## Quick path

```bash
pip install "le-loopforge>=0.2.1" "le-loopctl>=0.1.1" loopgym
python examples/integrate-crewai/run_demo.py
```

Case study: [crewai-composition-bridge.md](../../case-studies/crewai-composition-bridge.md)

RFC: [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11)
