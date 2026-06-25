#!/usr/bin/env python3
"""Adoption wave 10 — platform gravity (Phase 11)."""

from __future__ import annotations

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
HUB = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/README.md"
CLAUDE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/CLAUDE_CODE.md"
CODEX = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/CODEX.md"
TEMPLATE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/reproduction-reports/TEMPLATE-trace-native.md"

DISCUSSION_10 = f"""## Adoption wave 10 — one-line install + score (PyPI-only)

```bash
pip install "le-loop-stack>=0.1.0"

loopctl pipeline \\
  --intent "YOUR EXISTING LOOP IN ENGLISH" \\
  -o mapped.yaml \\
  --export generic \\
  --run-loopgym \\
  --json
```

- Integration hub: {HUB}
- Golden Path v3: {GOLDEN}
- Trace template: {TEMPLATE}
"""

ISSUE_4 = f"""## Wave 10 — LoopBench from pip-only pipeline

No repo clone required for structural LES:

```bash
pip install "le-loop-stack[bench]>=0.1.0"
loopctl pipeline --intent "Fix failing tests" -o sub.yaml --run-loopgym --trace trace.json --json
loopbench run --task LB-CR-1 --spec sub.yaml --seeds 0,1,2,3,4 -o results.json
```
"""

ISSUE_7 = f"""## Wave 10 — map Claude Code / Codex / your harness

1. Pick a pack: {HUB}
2. `loopctl score --spec mapped.yaml --json`
3. PR case study referencing this issue

Claude Code: {CLAUDE}
Codex: {CODEX}
"""

DISCUSSION_11 = f"""## Wave 10 — LSS 1.1 + new harness bridges

New integration packs (map-and-score, no runtime swap):
- Claude Code, Codex, Aider, Gemini CLI, OpenAI Agents SDK

Hub: {HUB}

Reply with your framework tuple mapping (3-5 bullets).
"""

CLAUDE_COMMUNITY = f"""## Loop Engineering × Claude Code

Map your Claude Code session to a scored LSS spec in ~15 minutes:

```bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "Fix failing tests from CI" -o mapped.yaml --suggest-level
loopctl score --spec mapped.yaml --json
```

Guide: {CLAUDE}
"""

CODEX_COMMUNITY = f"""## Loop Engineering × Codex / coding agents

Score your test-driven coding loop structurally:

```bash
pip install "le-loop-stack>=0.1.0"
loopctl pipeline --intent "Repair failing unit tests" -o mapped.yaml --json
```

Guide: {CODEX}
"""

AIDER_COMMUNITY = f"""## Loop Engineering × Aider

Map pair-programming loops to LSS for LoopBench comparison:

{HUB}
"""


def main() -> int:
    sections = [
        ("Discussion #10", DISCUSSION_10),
        ("Issue #4", ISSUE_4),
        ("Issue #7", ISSUE_7),
        ("Discussion #11", DISCUSSION_11),
        ("Claude Code communities", CLAUDE_COMMUNITY),
        ("Codex communities", CODEX_COMMUNITY),
        ("Aider GitHub", AIDER_COMMUNITY),
    ]
    for title, body in sections:
        print(f"=== {title} ===\n", body, "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
