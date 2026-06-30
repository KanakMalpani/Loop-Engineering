#!/usr/bin/env python3
"""Adoption wave 16 — combine v0.5 + external LoopBench outreach."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"
REPO = "KanakMalpani/Loop-Engineering"

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
PARTNER = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PARTNER_LOOPBENCH_SUBMIT.md"
FLAT = "https://github.com/KanakMalpani/Loop-Engineering/tree/main/loop-library/compositions/flat"
LEADERBOARD = "https://kanakmalpani.github.io/LoopBench/"

DISCUSSION_10_BODY = f"""## Adoption wave 16 — combine v0.5 (token-efficient)

```bash
pip install "le-loop-stack>=0.4.0"

# Zero-compose path (pre-merged flat specs)
loopctl score --spec loop-library/compositions/flat/debug-repair-flat.yaml --json

# Runtime combine
loop combine --library research-agent,autonomous-debugger --intent "Research then fix tests" --json
loop quick "Fix CI" --library research-agent,coding-agent --max-tokens 800 --json

# LSS-min JSON for agent system prompts
loopctl spec minify my-loop.yaml -o my-loop.min.json
```

**New:** flat pre-merged compositions · `loop combine` · `--max-tokens` · LSS-min JSON export

- Golden Path v6: {GOLDEN}
- Partner submit (LB-CR-1 or suite): {PARTNER}
- Pre-merged specs: {FLAT}
- Live board: {LEADERBOARD}

First **non-maintainer** row still open — combine lowers the barrier.
"""

ISSUE_4_BODY = """## Wave 16 — combine v0.5 external row invite

Partners can submit via **either** path:

| Path | Steps |
|------|-------|
| **Easy** | Fork partner stub → `loopbench run --task LB-CR-1` → PR to LoopBench |
| **Preferred** | `loop combine --library …` or flat spec → `loopbench run --suite suite-repair` → PR with `grand_composite` |

```bash
pip install "le-loop-stack>=0.4.0"
loop combine --library research-agent,autonomous-debugger -o partner.yaml --json
loopbench run --suite suite-repair --spec partner.yaml --seeds 0,1,2,3,4 -o results.json
```

Dry-run templates: `docs/submission-dry-run/partner/`  
Maintainer review required — see ROW_SCHEMA.md.
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
    parser = argparse.ArgumentParser(description="Adoption wave 16 — combine v0.5 outreach")
    parser.add_argument("--post", action="store_true", help="Post to GitHub via gh CLI")
    args = parser.parse_args()

    print("=== Discussion #10 ===\n", DISCUSSION_10_BODY)
    print("=== Issue #4 ===\n", ISSUE_4_BODY)

    if not args.post:
        return 0

    stamp = f"\n\n_Posted {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC via adoption_wave16.py_"
    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": DISCUSSION_10_BODY + stamp})
    if data:
        print("Discussion comment:", data["addDiscussionComment"]["comment"]["url"])
    gh_issue_comment(4, ISSUE_4_BODY + stamp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
