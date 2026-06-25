# Integrate Aider pair-programming loops

Map [Aider](https://aider.chat/) edit-test loops to LSS.

## Tuple mapping

| LSS | Aider |
|-----|-------|
| **S** | Git repo + chat context + `/add` files |
| **A** | LLM edits + shell commands |
| **O** | Diff, test output, linter |
| **E** | Tests pass / user accept |
| **M** | Chat history + git commits |
| **τ** | `/quit`, cost limits |

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Implement feature from issue with tests passing" -o aider-mapped.yaml --suggest-level
loopctl validate aider-mapped.yaml
loopctl score --spec aider-mapped.yaml --json
```

Post your Aider → LSS mapping on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10).

North star: [NORTH_STAR.md](../NORTH_STAR.md)
