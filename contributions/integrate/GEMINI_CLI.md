# Integrate Google Gemini CLI

Map **Gemini CLI** agent loops to LSS.

## Tuple mapping

| LSS | Gemini CLI |
|-----|------------|
| **S** | Project context + `@` file references |
| **A** | Tool use (edit, run, search) |
| **O** | Command output, file diffs |
| **E** | User confirmation, test pass |
| **M** | Session history |
| **τ** | Turn limits, API quota |

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Summarize codebase architecture with citations" -o gemini-mapped.yaml --suggest-level
loopctl validate gemini-mapped.yaml
loopctl score --spec gemini-mapped.yaml --json
```

North star: [NORTH_STAR.md](../NORTH_STAR.md)
