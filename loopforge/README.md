# LoopForge

Scaffold and **combine** valid [LSS](https://github.com/KanakMalpani/Loop-Core-Engineering) loop specifications from patterns, recipes, or the bundled loop library.

```bash
pip install "le-loopforge>=0.5.0"

loopforge list-patterns
loopforge new --pattern reflection --name my-loop --objective "Your goal" -o my-loop.yaml

# Combine library templates (flat + compact — saves tokens)
loopforge combine --library research-agent,coding-agent -o pipeline.yaml --json

# Mix a named recipe
loopforge mix dev-agent -o agent.yaml
```

## Python API

```python
from loopforge import LoopChain, combine_loops, estimate_tokens

spec, meta = (
    LoopChain("my-pipeline", "Fix CI")
    .then_fork("autonomous-debugger")
    .then_fork("coding-agent")
    .build(flatten=True, compact=True)
)
print(meta["estimated_tokens"])
```

See [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) and [00-planning/LOOP_FORGE.md](../00-planning/LOOP_FORGE.md).
