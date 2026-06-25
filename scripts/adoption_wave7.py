#!/usr/bin/env python3
"""Adoption wave 7 — PyPI naming + trace-native LoopBench outreach."""

from __future__ import annotations

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
BEAT = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_TEMPLATE.md"
LOOPNET = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/loopnet/CONTRIBUTING-v0.3.md"
DRYRUN = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/docs/submission-dry-run"
EXAM = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/education/practitioner/exam-v0.1.md"

ISSUE_4 = f"""## Adoption wave 7 — trace-native LoopBench row

PyPI packages (note names — `loopforge` on PyPI is a different project):

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench

loopforge intent "Fix failing tests from CI" -o my-loop.yaml --suggest-level
loopctl validate my-loop.yaml

python -c "
import loopgym as lg
env = lg.make('loopbench/code-repair-v1')
env.run_episode(task_id='cr-001', seed=42, trace_path='trace.json')
"

loopctl trace validate trace.json
loopctl observed trace.json --spec my-loop.yaml --json
loopbench run --task LB-CR-1 --spec my-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

- Golden Path: {GOLDEN}
- BEAT template: {BEAT}
- LoopNet v0.3: {LOOPNET}
- Maintainer dry-run: {DRYRUN}
- External template row: https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/submission-dry-run/external-template-row.json
"""

DISCUSSION_10 = f"""## Reproduction v3 — PyPI install names

Use **`le-loopforge`** and **`le-loopctl`** on PyPI (CLI commands remain `loopforge` / `loopctl`).

Required artifacts:
1. LoopForge command output
2. `loopctl validate` pass
3. Loop Trace 1.0 JSON
4. Observed LES composite
5. Optional LoopBench results

Reference dry-run: {DRYRUN}
"""

ISSUE_7 = f"""## Case study + practitioner exam pilot

Map your agent harness with LoopForge intent, then submit a case study:

```bash
pip install le-loopforge le-loopctl
loopforge intent "YOUR AGENT LOOP DESCRIPTION" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
```

Template: [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md)
Exam pilot volunteers: {EXAM}
"""


def main() -> int:
    print("=== Issue #4 ===\n", ISSUE_4)
    print("=== Discussion #10 ===\n", DISCUSSION_10)
    print("=== Issue #7 ===\n", ISSUE_7)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
