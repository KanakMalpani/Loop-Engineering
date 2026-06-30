# le-loop-stack

**The only install you need for loop engineering** — declare, validate, score, run, benchmark, and map any popular AI agent.

```bash
pip install "le-loop-stack>=0.4.0"
```

Includes:

| Package | CLI | Role |
|---------|-----|------|
| **le-loopforge** | `loopforge` | Intent → LSS YAML, **combine**, `LoopChain`, loop library, export stubs |
| **le-loopctl** | `loopctl` / `loop` | Validate, score, pipeline, **combine**, **quick**, **mix**, **bench** |
| **loopgym** | (API) | Sim/Live/Replay + Loop Trace 1.0 |
| **loopbench** | `loopbench` | Public leaderboard (19 tasks, 4 suites) |

## 10-second start (token-efficient)

```bash
# Combine library loops → one compact YAML + JSON metadata
loop combine --library research-agent,autonomous-debugger \
  --intent "Research then fix tests" -o pipeline.yaml --json

# Or recipe mix (flatten + compact by default)
loop mix dev-agent --intent "Fix failing tests from CI" --json

# Single agent quick path
loop quick "Fix failing tests from CI" --agent aider
```

Optional extras: `pip install "le-loop-stack[math,agents,bench]"` — proof-carrying compose when loopmath installed.

## Supported agents

`loopctl agent list` — langgraph, crewai, react, reflexion, dspy, aider, openhands, claude_code, codex, smolagents, autogpt, openai_agents

## Optional runtime extras

```bash
pip install "le-loop-stack[agents]"   # LangGraph + CrewAI runtimes for export stubs
pip install "le-loop-stack[bench]"    # loopbench CLI
pip install "le-loop-stack[all]"
```

## Full pipeline

```bash
loopctl pipeline --recipe dev-agent --intent "Repair CI" --suite suite-repair --compact --json
```

Golden Path: [contributions/GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md)
