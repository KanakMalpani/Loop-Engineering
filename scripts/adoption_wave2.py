#!/usr/bin/env python3
# Superseded by adoption_wave7.py — kept for history.
"""Phase 2 adoption campaign: Discussion #10 checklist, outreach pings, issue labels."""

from __future__ import annotations

import json
import subprocess
import sys

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"

CHECKLIST = """## First external submitter checklist (Phase 2)

**Goal:** flip the adoption tracker green for non-maintainer contributions.

### LoopBench row (fastest win)
1. `pip install "loopbench>=0.1.1" loopgym`
2. Follow [BEAT_LB-CR-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md) (or [RS-1](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-RS-1.md) / [MA-1](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-MA-1.md))
3. PR your row to [LoopBench leaderboard](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json)

### Reproduction report (~60 min)
[REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md) → post below from a **non-maintainer** account.

### Case study
[TEMPLATE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/TEMPLATE.md) → PR → [#7](https://github.com/KanakMalpani/Loop-Engineering/issues/7)

Full pack: [EXTERNAL_SUBMISSIONS.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/EXTERNAL_SUBMISSIONS.md)"""

FOLLOWUPS = [
    ("langchain-ai/langgraph", 8186),
    ("crewAIInc/crewAI", 6316),
]

FOLLOWUP_BODY = """Friendly follow-up on LSS 1.1 composition mapping ([Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11)).

**Stable spec:** [Loop-Core lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md)

A one-paragraph note on whether `composition.children` + `adapters` matches your graph topology would help us close the RFC. No PR required — comment on Discussion #11 is enough. Thanks!"""

PIN_MUTATION = ""  # GitHub GraphQL pinDiscussion not available on all plans; skip

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
    # Pin Discussion #10 (skipped — API not available on all repos)
    if PIN_MUTATION.strip():
        pin = gh_graphql(PIN_MUTATION, {"id": DISCUSSION_10})
        if pin:
            print("Pinned Discussion #10")

    # Checklist comment
    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": CHECKLIST})
    if not data:
        return 1
    print(data["addDiscussionComment"]["comment"]["url"])

    # Issue labels
    for num in (4, 7):
        subprocess.run(
            ["gh", "issue", "edit", str(num), "--repo", "KanakMalpani/Loop-Engineering",
             "--add-label", "good-first", "--add-label", "adoption"],
            check=False,
        )

    # Outreach follow-ups
    for repo, num in FOLLOWUPS:
        result = subprocess.run(
            ["gh", "issue", "comment", str(num), "--repo", repo, "--body", FOLLOWUP_BODY],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Follow-up: {repo}#{num}")
        else:
            print(result.stderr or result.stdout, file=sys.stderr)

    print("Adoption wave 2 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
