#!/usr/bin/env python3
"""Adoption wave 15 — LoopBench suites + loop mixing."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"
REPO = "KanakMalpani/Loop-Engineering"

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
BEAT_REPAIR = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_suite-repair.md"
LEADERBOARD = "https://kanakmalpani.github.io/LoopBench/"

DISCUSSION_10_BODY = f"""## Adoption wave 15 — suites + mix recipes

```bash
pip install "le-loop-stack>=0.3.0"

loop mix dev-agent --intent "Fix CI tests" --json
loopbench suite list
loopbench run --suite suite-repair --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopctl pipeline --recipe dev-agent --intent "Repair flaky tests" --suite suite-repair --compact --json
```

**Suites:** `suite-repair` · `suite-agent` · `suite-knowledge` · `suite-rigor`  
**Recipes:** `dev-agent` · `research-pipeline` · `swarm-review` · `safe-repair` · `full-stack`

- Golden Path v5: {GOLDEN}
- BEAT suite-repair: {BEAT_REPAIR}
- Live board: {LEADERBOARD}

Leaderboard ranks **generalist** (grand mean of suite scores) + per-suite tabs.
"""

ISSUE_4_BODY = """## Wave 15 — comparison suites + N-way loop mix

LoopBench v0.2: **19 micro-tasks** → **4 comparison suites**.

| Suite | Mix recipe |
|-------|------------|
| suite-repair | `dev-agent` |
| suite-agent | `swarm-review` |
| suite-knowledge | `research-pipeline` |
| suite-rigor | `safe-repair` |

```bash
pip install "le-loop-stack>=0.3.0"
loop mix swarm-review --intent "Parallel research and debate" -o spec.yaml --json
loopbench run --suite suite-agent --spec spec.yaml --seeds 0,1,2,3,4 -o results.json
```

Submit JSON with `suite_scores` + `grand_composite`. Dual-track: LB-CR-1 still valid for first external row.
"""

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


def gh_issue_comment(num: int, body: str) -> bool:
    result = subprocess.run(
        ["gh", "issue", "comment", str(num), "--repo", REPO, "--body", body],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return False
    print(f"Commented {REPO}#{num}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Adoption wave 15 outreach")
    parser.add_argument("--post", action="store_true", help="Post to GitHub via gh CLI")
    args = parser.parse_args()

    print("=== Discussion #10 ===\n", DISCUSSION_10_BODY)
    print("=== Issue #4 ===\n", ISSUE_4_BODY)

    if not args.post:
        return 0

    stamp = f"\n\n_Posted {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC via adoption_wave15.py_"
    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": DISCUSSION_10_BODY + stamp})
    if data:
        print("Discussion comment:", data["addDiscussionComment"]["comment"]["url"])
    gh_issue_comment(4, ISSUE_4_BODY + stamp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
