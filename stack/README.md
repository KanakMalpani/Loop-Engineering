# le-loop-stack

One-line PyPI install for the Loop Engineering practitioner stack:

```bash
pip install "le-loop-stack>=0.1.0"
```

Installs:

- **`le-loopforge`** — intent, compose, export (`loopforge`)
- **`le-loopctl`** — validate, score, trace, pipeline (`loopctl`)
- **`loopgym`** — Sim/Live/Replay runtime + Loop Trace 1.0

## Optional extras

```bash
pip install "le-loop-stack[bench]"      # loopbench CLI
pip install "le-loop-stack[langgraph]"  # LangGraph export runtime
pip install "le-loop-stack[crewai]"     # CrewAI export runtime
pip install "le-loop-stack[all]"
```

## Quickstart

```bash
loopforge intent "Summarize user feedback into themes" -o my-loop.yaml
loopctl validate my-loop.yaml
loopctl score --spec my-loop.yaml --json
```

Golden Path: [contributions/GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md)

PyPI naming: [contributions/PYPI_NAMING.md](../contributions/PYPI_NAMING.md)
