#!/usr/bin/env python3
"""Adoption wave 6 — trace + observed LES submission outreach."""

from __future__ import annotations

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
BEAT = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_TEMPLATE.md"
TRACE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/standards/LOOP-TRACE-1.0.md"
DRYRUN = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/docs/submission-dry-run"

ISSUE_4 = f"""## Adoption wave 6 — trace + observed LES submissions

Loop Trace 1.0 + observed LES are live. Full submission path:

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" loopbench
loopforge intent "Fix failing tests from CI" -o my-loop.yaml --suggest-level
python scripts/generate_trace_demo.py   # or LoopGym trace when available
loopctl trace validate docs/submission-dry-run/trace.json
loopctl observed docs/submission-dry-run/trace.json --json
loopbench run --task LB-CR-1 --spec my-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

- Golden Path: {GOLDEN}
- BEAT template: {BEAT}
- Trace spec: {TRACE}
- Maintainer dry-run: {DRYRUN}
"""

DISCUSSION_10 = f"""## Reproduction v2 — include trace + observed LES

Post these artifacts with your report:

1. LoopForge command (`loopforge new` / `fork` / `intent`)
2. `loopctl validate` output
3. `trace.json` (Loop Trace 1.0)
4. `loopctl observed trace.json` composite
5. Optional LoopBench `results.json`

Dry-run reference: {DRYRUN}
"""

ISSUE_7 = f"""## Case study — LoopForge mapping section added

Extend [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md):

```bash
loopforge intent "IDE agent with tool calls and test verification" -o cursor-mapped.yaml
loopctl validate cursor-mapped.yaml
```

Template: [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md) (LoopForge section)
Practitioner exam: [education/practitioner/exam-v0.1.md](../education/practitioner/exam-v0.1.md)
"""


def main() -> int:
    print("=== Issue #4 ===\n", ISSUE_4)
    print("=== Discussion #10 ===\n", DISCUSSION_10)
    print("=== Issue #7 ===\n", ISSUE_7)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
