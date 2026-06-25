#!/usr/bin/env python3
"""Adoption wave 9 — integrate your existing loop in 15 minutes."""

from __future__ import annotations

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
NORTH = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/NORTH_STAR.md"
CURSOR = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/CURSOR.md"
LG = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/examples/integrate-langgraph"
CREW = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/examples/integrate-crewai"
TEMPLATE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/reproduction-reports/TEMPLATE-trace-native.md"

DISCUSSION_10 = f"""## Adoption wave 9 - integrate in 15 minutes

You do **not** need to rewrite your agent. Map it, score it, export it:

```bash
pip install "le-loopforge>=0.2.1" "le-loopctl>=0.1.1" loopgym

loopctl pipeline \\
  --intent "YOUR EXISTING LOOP IN ENGLISH" \\
  -o mapped.yaml \\
  --export langgraph \\
  --run-loopgym \\
  --json
```

- North star: {NORTH}
- Golden Path v2: {GOLDEN}
- Trace template: {TEMPLATE}
"""

ISSUE_4 = f"""## Wave 9 - trace-native LoopBench from pipeline

```bash
loopctl pipeline --intent "Fix failing tests from CI" -o sub.yaml --run-loopgym --trace trace.json --json
loopbench run --task LB-CR-1 --spec sub.yaml --seeds 0,1,2,3,4 -o results.json
```

Template: https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/submission-dry-run/external-template-row.json
"""

ISSUE_7 = f"""## Wave 9 - case study from your harness

1. `loopctl pipeline --intent "..." -o mapped.yaml --json`
2. Fill [TEMPLATE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/TEMPLATE.md)
3. PR referencing this issue

Cursor path: {CURSOR}
"""

DISCUSSION_11 = f"""## Wave 9 - LSS 1.1 integration packs

Runnable examples:
- LangGraph: {LG}
- CrewAI: {CREW}

Reply with your framework mapping (3-5 bullets).
"""


def main() -> int:
    print("=== Discussion #10 ===\n", DISCUSSION_10)
    print("=== Issue #4 ===\n", ISSUE_4)
    print("=== Issue #7 ===\n", ISSUE_7)
    print("=== Discussion #11 ===\n", DISCUSSION_11)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
