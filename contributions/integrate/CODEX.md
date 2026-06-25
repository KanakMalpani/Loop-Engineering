# Integrate OpenAI Codex agent loops

Map **Codex CLI** / coding-agent loops to LSS for structural scoring and LoopBench comparison.

## Tuple mapping

| LSS | Codex / coding agent |
|-----|----------------------|
| **S** | Repo tree, failing tests, task spec, terminal output |
| **A** | Edit files, run tests, search codebase |
| **O** | Test pass/fail, linter, diff stats |
| **E** | Test suite + optional human review |
| **M** | Session transcript, git diff history |
| **τ** | Step/token budget, sandbox limits |

Related: [autonomous-debugger.yaml](../../loop-library/autonomous-debugger.yaml) · [autonomous-coding-agents.md](../../case-studies/autonomous-coding-agents.md)

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Repair failing unit tests with minimal code changes" -o codex-mapped.yaml --suggest-level
loopctl validate codex-mapped.yaml
loopctl score --spec codex-mapped.yaml --json
```

Export a runnable stub (LoopGym fallback when Codex runtime unavailable):

```bash
loopforge export --spec codex-mapped.yaml --target generic --out ./codex-export/
python codex-export/run.py --json --trace trace.json
loopctl observed trace.json --spec codex-mapped.yaml --json
```

## LoopBench path

```bash
loopbench run --task LB-CR-1 --spec codex-mapped.yaml --seeds 0,1,2,3,4 -o results.json
```

North star: [NORTH_STAR.md](../NORTH_STAR.md)
