# Benchmark Results

Published baseline runs for LoopBench tasks.

**Submit new results:** [LoopBench](https://github.com/KanakMalpani/LoopBench) or the benchmark submission issue template.

---

## Published baselines

| Task ID | Name | Harness | Date | Success@k | LES observed | Artifact |
|---------|------|---------|------|-----------|--------------|----------|
| LB-CR-1 | Code Repair | loopbench sim + autonomous-debugger | 2026-06-17 | 1.0 | 86.7 | [lb-cr-1-baseline.json](./lb-cr-1-baseline.json) |

Full submission: [lb-cr-1-run.json](./lb-cr-1-run.json)

---

## Reproduce

```bash
pip install loopbench
loopbench run --task LB-CR-1 --spec loop-library/autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json
```

See [contributions/REPRODUCE.md](../../contributions/REPRODUCE.md).

---

## Leaderboard

[LoopBench on GitHub](https://github.com/KanakMalpani/LoopBench) — maintainer PR #1 pending merge.

---

## Pending baselines

- LB-RS-1 Research Synthesis
- LB-MA-1 Multi-Agent Debate

See [contributions/GOOD_FIRST_ISSUES.md](../../contributions/GOOD_FIRST_ISSUES.md).
