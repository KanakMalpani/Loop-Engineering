# Integrate Devin / OpenHands / SWE-agent

Map autonomous software-engineering harnesses to LSS (map-and-score; no runtime replacement).

## Tuple mapping

| LSS | Devin-class harness |
|-----|---------------------|
| **S** | Repo + issue + environment snapshot |
| **A** | Plan, code, run shell, browse |
| **O** | Test results, logs, screenshots |
| **E** | Test suite, human escalation |
| **M** | Run transcript, artifacts |
| **τ** | Time/cost budget |

See harness survey: [autonomous-coding-agents.md](../../case-studies/autonomous-coding-agents.md)

## 15-minute path

```bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "Resolve GitHub issue with passing tests" -o swe-mapped.yaml --suggest-level
loopctl score --spec swe-mapped.yaml --json
```

Loop library profile: [autonomous-debugger.yaml](../../loop-library/autonomous-debugger.yaml)

North star: [NORTH_STAR.md](../NORTH_STAR.md)
