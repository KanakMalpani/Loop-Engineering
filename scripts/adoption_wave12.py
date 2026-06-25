#!/usr/bin/env python3
"""Adoption wave 12 — follow-up on wave 11 outreach with partner submission guide."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone

PARTNER_GUIDE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PARTNER_LOOPBENCH_SUBMIT.md"
BEAT = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md"
LEADERBOARD = "https://kanakmalpani.github.io/LoopBench/"

FOLLOWUP_BODY = f"""## Follow-up — partner submission pack (30 min)

Thanks again for considering a LoopBench row. We shipped a **fork-and-PR kit** since the initial invite:

**Partner guide:** {PARTNER_GUIDE}

```bash
pip install "le-loop-stack[bench]>=0.1.0"
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
python scripts/run_submission_dryrun.py --partner agentless   # or aider / openhands
loopbench run --task LB-CR-1 --spec docs/submission-dry-run/partner-*-lb-cr-1.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
# → Fork LoopBench, add row to leaderboard/entries.json, open PR
```

- BEAT path: {BEAT}
- Live board: {LEADERBOARD}
- Maintainer pairing offered — reply here or on [Loop-Engineering #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

First **non-maintainer** merge gets permanent leaderboard credit.
"""

OUTREACH = [
    ("OpenAutoCoder/Agentless", 86),
    ("Aider-AI/aider", 5328),
    ("OpenHands/OpenHands", 14984),
]


def gh_issue_comment(repo: str, num: int, body: str) -> bool:
    result = subprocess.run(
        ["gh", "issue", "comment", str(num), "--repo", repo, "--body", body],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return False
    print(f"Commented {repo}#{num}")
    return True


def main() -> int:
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = FOLLOWUP_BODY + f"\n\n_Posted {when} UTC via adoption_wave12.py_"
    ok = True
    for repo, num in OUTREACH:
        if not gh_issue_comment(repo, num, body):
            ok = False
    gh_issue_comment(
        "KanakMalpani/Loop-Engineering",
        4,
        f"## Wave 12 follow-up posted\n\nPartner guide linked on Agentless, Aider, and OpenHands outreach issues.\n\nGuide: {PARTNER_GUIDE}",
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
