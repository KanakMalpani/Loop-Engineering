#!/usr/bin/env python3
"""Phase 4 adoption campaign: HF + LoopBench Discussions + framework pings."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"

WAVE4_BODY = """## Phase 4 — LB-COMP-1 on real composed env

LoopBench **LB-COMP-1** now runs via `loopbench/composed-swarm-v1` (not MA-1 proxy).

| Task | Guide | Target LES |
|------|-------|------------|
| LB-CR-1 | [BEAT_LB-CR-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md) | 86.7 |
| LB-RS-1 | [BEAT_LB-RS-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-RS-1.md) | 81.9 |
| LB-MA-1 | [BEAT_LB-MA-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-MA-1.md) | 86.5 |
| LB-COMP-1 | [BEAT_LB-COMP-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-COMP-1.md) | 80.3 |

```bash
pip install "loopbench>=0.1.1" "loopgym>=0.1.1"
loopbench run --task LB-COMP-1 --spec loop-library/compositions/scenario-swarm-rehearsal.yaml --seeds 0,1,2,3,4 -o results.json
```

One-pager: [ADOPTION.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/ADOPTION.md)

Non-maintainer accounts only for tracker credit."""

LOOPBENCH_DISCUSSION = """## Beat maintainer LES on LB-COMP-1 (composed env)

LB-COMP-1 now uses `loopbench/composed-swarm-v1`. Guide: [BEAT_LB-COMP-1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-COMP-1.md) (target **80.3**).

Open a PR on `leaderboard/entries.json` after `loopbench validate results.json`."""

HF_DATASET_TOPIC = """## LoopBench BEAT path for loopnet researchers

Reproduce LoopNet explore + run any LoopBench task:

- [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md)
- [BEAT guides](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/ADOPTION.md)

Post your reproduction on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)."""

CREWAI_BODY = """Follow-up: we shipped a CrewAI ↔ LSS 1.1 composition mapping case study:

https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/crewai-composition-bridge.md

Runnable smoke (no API keys): `python implementations/crewai/run.py`

A short note on whether `composition.children` + parallel crews matches your model would help close [RFC Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11). Thanks!"""

LANGGRAPH_BODY = """Friendly 14-day follow-up on LSS 1.1 composition mapping ([Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11)).

**Bridge case study:** https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/langgraph-composition-bridge.md

**Stable spec:** [Loop-Core lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md)

One paragraph on graph nodes vs `composition.children` is enough — comment on Discussion #11."""

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


def gh_issue_comment(repo: str, num: int, body: str) -> bool:
    result = subprocess.run(
        ["gh", "issue", "comment", str(num), "--repo", repo, "--body", body],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return False
    return True


def main() -> int:
    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = WAVE4_BODY + f"\n\n_Posted {when} UTC via adoption_wave4.py_"
    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": body})
    if not data:
        return 1
    print("Discussion #10:", data["addDiscussionComment"]["comment"]["url"])

    # LoopBench repo discussion (create comment on first discussion if exists)
    lb_disc = subprocess.run(
        ["gh", "api", "repos/KanakMalpani/LoopBench/discussions", "--jq", ".[0].number"],
        capture_output=True,
        text=True,
    )
    if lb_disc.returncode == 0 and lb_disc.stdout.strip():
        num = lb_disc.stdout.strip()
        subprocess.run(
            [
                "gh",
                "api",
                f"repos/KanakMalpani/LoopBench/discussions/{num}/comments",
                "-f",
                f"body={LOOPBENCH_DISCUSSION}",
            ],
            capture_output=True,
            text=True,
        )
        print(f"LoopBench discussion #{num}: commented")

    # HF dataset forum via discussion API (best-effort)
    subprocess.run(
        [
            "gh",
            "api",
            "-X",
            "POST",
            "huggingface.co/api/datasets/KanakMalpani/loopnet-v0.2/discussions",
            "-f",
            "title=LoopBench BEAT path for researchers",
            "-f",
            f"description={HF_DATASET_TOPIC[:500]}",
        ],
        capture_output=True,
        text=True,
    )
    print("HF dataset discussion: attempted (best-effort)")

    gh_issue_comment("crewAIInc/crewAI", 6316, CREWAI_BODY)
    print("CrewAI #6316: commented")
    gh_issue_comment("langchain-ai/langgraph", 8186, LANGGRAPH_BODY)
    print("LangGraph #8186: commented")

    print("Adoption wave 4 complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
