# Benchmark Results

Published maintainer baselines for LoopBench 0.1.0 (SimEnv, seeds 0–4).

**Submit new results:** [LoopBench](https://github.com/KanakMalpani/LoopBench) or the benchmark submission issue template.

---

## Published baselines

| Task ID | Name | LSS spec | LES observed | Artifact |
|---------|------|----------|--------------|----------|
| LB-CR-1 | Code Repair | autonomous-debugger | 86.7 | [lb-cr-1-baseline.json](./lb-cr-1-baseline.json) |
| LB-RS-1 | Research Synthesis | research-agent | 81.9 | [lb-rs-1-baseline.json](./lb-rs-1-baseline.json) |
| LB-MA-1 | Multi-Agent Debate | coding-agent | 86.5 | [lb-ma-1-baseline.json](./lb-ma-1-baseline.json) |

Full submissions: `lb-*-run.json` in this directory.

---

## Reproduce

```bash
pip install loopbench
loopbench run --task LB-CR-1 --spec loop-library/autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json
loopbench run --task LB-RS-1 --spec loop-library/research-agent.yaml --seeds 0,1,2,3,4 -o results.json
loopbench run --task LB-MA-1 --spec loop-library/coding-agent.yaml --seeds 0,1,2,3,4 -o results.json
```

See [contributions/REPRODUCE.md](../../contributions/REPRODUCE.md).

---

## Leaderboard

[LoopBench on GitHub](https://github.com/KanakMalpani/LoopBench)

---

## Next

- Composed-loop benchmark (scenario-swarm-rehearsal)
- External submissions on leaderboard

See [All about loops/NEXT_STEPS.md](../../All%20about%20loops/NEXT_STEPS.md).
