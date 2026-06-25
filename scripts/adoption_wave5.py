#!/usr/bin/env python3
"""Adoption wave 5 — LoopForge-first external submission outreach."""

from __future__ import annotations

GOLDEN_PATH = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
BEAT_TEMPLATE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_TEMPLATE.md"
LOOPFORGE = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/loopforge"

ISSUE_4_COMMENT = f"""## Adoption wave 5 — LoopForge-first submissions

External LoopBench rows are now **one command away** from a valid spec:

```bash
pip install loopforge loopbench
loopforge fork --from autonomous-debugger --name my-submission -o my-loop.yaml --suggest-level
loopbench run --task LB-CR-1 --spec my-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

- Golden Path: {GOLDEN_PATH}
- BEAT template: {BEAT_TEMPLATE}
- LoopForge: {LOOPFORGE}
"""

DISCUSSION_10_COMMENT = f"""## Updated reproduction path (LoopForge)

Step 0 is now LoopForge — scaffold before hand-editing YAML:

```bash
pip install loopforge
loopforge new --pattern reflection --name my-repro --objective "..." -o my-loop.yaml
python -m loopctl validate my-loop.yaml
```

Full guide: {GOLDEN_PATH}
"""

ISSUE_7_COMMENT = f"""## Case study starter — map any agent loop to LSS

1. Pick pattern: [patterns/README](https://github.com/KanakMalpani/Loop-Engineering/blob/main/patterns/README.md)
2. Scaffold: `loopforge new --pattern ... -o case-study-loop.yaml`
3. Map workers/evaluators to the real system
4. Score: `loopctl score --spec case-study-loop.yaml`

Practitioner path: {GOLDEN_PATH}
"""


def main() -> int:
    print("Adoption wave 5 — copy these comments to GitHub (manual or gh cli):\n")
    print("=== Issue #4 ===")
    print(ISSUE_4_COMMENT)
    print("=== Discussion #10 ===")
    print(DISCUSSION_10_COMMENT)
    print("=== Issue #7 ===")
    print(ISSUE_7_COMMENT)
    print("\nHF dataset card: add LoopForge link to loopnet-v0.2 card (manual).")
    print("LoopBench Discussions: post BEAT_TEMPLATE link (manual).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
