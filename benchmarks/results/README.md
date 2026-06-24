# Benchmark Results

Published baseline runs for the Agent Loop Standard (ALS) suite. Full task definitions: [suite-overview.md](../suite-overview.md).

**Submit new results:** LoopBench repository or GitHub issue template `benchmark-submission.md`.

---

## Published baselines

| Task ID | Name | Harness | Date | Success rate | LES (structural) | Artifact |
|---------|------|---------|------|--------------|------------------|----------|
| ALS-T2 | Code Repair | reflection-loop + autonomous-debugger LSS | 2026-06-17 | 100% (5/5) | 70.4 | [als-t2-code-repair-baseline.json](./als-t2-code-repair-baseline.json) |

---

## Reproduce ALS-T2 maintainer baseline

```bash
python examples/reflection-loop/run.py
python tools/les_calculator.py --spec loop-library/autonomous-debugger.yaml --json
```

See [contributions/REPRODUCE.md](../../contributions/REPRODUCE.md) for the full one-hour path.

---

## Leaderboard

Canonical public leaderboard: [LoopBench on GitHub](https://github.com/KanakMalpani/LoopBench)

---

## Pending baselines (good first issues)

- ALS-T1 Research Synthesis
- ALS-T3 Multi-Agent Debate

See [contributions/GOOD_FIRST_ISSUES.md](../../contributions/GOOD_FIRST_ISSUES.md).
