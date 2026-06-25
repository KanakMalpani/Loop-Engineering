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

## Cursor rule

Enable [.cursor/rules/loop-engineering.mdc](../../.cursor/rules/loop-engineering.mdc) in this repo (or copy into your project).

North star: [NORTH_STAR.md](../NORTH_STAR.md)
