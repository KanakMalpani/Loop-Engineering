# Integrate GitHub Copilot / Copilot Workspace

Map **Copilot** agent loops (IDE chat, Workspace tasks) to LSS for scoring and comparison.

## Tuple mapping

| LSS | Copilot / Workspace |
|-----|---------------------|
| **S** | Open files, repo context, issue/PR description |
| **A** | Suggested edits, terminal commands |
| **O** | Build/test output, PR diff |
| **E** | CI, reviewer, quality gates |
| **M** | Session + PR history |
| **τ** | Workspace step budget |

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "Implement issue fix with passing CI" -o copilot-mapped.yaml --suggest-level
loopctl validate copilot-mapped.yaml
loopctl score --spec copilot-mapped.yaml --json
```

Contribute external case study: [Issue #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7)

North star: [NORTH_STAR.md](../NORTH_STAR.md)
