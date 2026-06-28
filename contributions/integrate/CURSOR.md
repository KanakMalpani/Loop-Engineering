# Integrate Cursor agent loops

Map the Cursor agent loop to LSS without replacing your IDE workflow.

## Tuple mapping

| LSS | Cursor agent |
|-----|----------------|
| **S** | Chat context + open files + terminal state |
| **A** | Tool calls (edit, run, search) |
| **O** | Tool results + linter/test output |
| **E** | User accept, CI, or rubric you define |
| **M** | Session + `.cursor/rules` persistence |
| **τ** | Max turns, budget, user stop |

Starter case study: [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md)

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Fix failing tests from CI with minimal diff" -o cursor-mapped.yaml --suggest-level
loopctl validate cursor-mapped.yaml
loopctl score --spec cursor-mapped.yaml --json
```

Optional trace from LoopGym when validating scoring logic:

```bash
loopctl pipeline --intent "Fix failing tests from CI" -o cursor-mapped.yaml --run-loopgym --json
```

## Cursor rules

| Rule | Purpose |
|------|---------|
| [.cursor/rules/loop-engineering.mdc](../../.cursor/rules/loop-engineering.mdc) | Map agent loops to LSS in chat |
| [.cursor/rules/agent-loop-engineering.mdc](../../.cursor/rules/agent-loop-engineering.mdc) | Full repo agent context (scoped) |
| [AGENT_BRIEFS.md](../../docs/maintainer/AGENT_BRIEFS.md) | Multi-repo delegation — `All about loops/AGENT_BRIEFS/` |

North star: [NORTH_STAR.md](../NORTH_STAR.md)
