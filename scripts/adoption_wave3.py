#!/usr/bin/env python3
"""Phase 3 adoption campaign: BEAT quad + stale-issue ping on #4/#7."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"

WAVE3_BODY = """## Phase 3 — BEAT all four LoopBench tasks

All four maintainer baselines now have one-command guides:

| Task | Guide | Target LES |
|------|-------|------------|
| LB-CR-1 | [BEAT_LB-CR-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md) | 86.7 |
| LB-RS-1 | [BEAT_LB-RS-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-RS-1.md) | 81.9 |
| LB-MA-1 | [BEAT_LB-MA-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-MA-1.md) | 86.5 |
| LB-COMP-1 | [BEAT_LB-COMP-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-COMP-1.md) | 77.4 |

**Composed loop:** `loopgym.make("loopbench/composed-swarm-v1")` now ships in LoopGym.

One-pager: [ADOPTION.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/ADOPTION.md)

Post your row / repro / case study below (non-maintainer accounts only)."""

STALE_BODY = """**Adoption ping (Phase 3):** This issue is still open. Fastest path to flip the [adoption tracker](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/adoption-tracker/latest.md) green:

- **#4:** Any [BEAT guide](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/ADOPTION.md) -> LoopBench PR
- **#7:** [Case study template](https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/TEMPLATE.md) -> PR

Questions welcome on Discussion #10."""

COMMENT_MUTATION = """
mutation($id: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $id, body: $body}) {
    comment { url }
  }
}
"""


def gh_graphql(query: str, variables: dict) -> dict | None:
    payload = json.dumps({"query": query, "variables": variables})
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return None
    data = json.loads(result.stdout)
    if data.get("errors"):
        print(json.dumps(data["errors"], indent=2), file=sys.stderr)
        return None
    return data.get("data")


def main() -> int:
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = WAVE3_BODY + f"\n\n_Posted {when} UTC via adoption_wave3.py_"
    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": body})
    if not data:
        return 1
    print(data["addDiscussionComment"]["comment"]["url"])

    for num in (4, 7):
        result = subprocess.run(
            ["gh", "issue", "comment", str(num), "--repo", "KanakMalpani/Loop-Engineering", "--body", STALE_BODY],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Stale ping: issue #{num}")
        else:
            print(result.stderr or result.stdout, file=sys.stderr)

    print("Adoption wave 3 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
