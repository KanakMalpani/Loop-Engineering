#!/usr/bin/env python3
"""Adoption wave 11 — invite external loop repo owners to submit first LoopBench row."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"

PLAYGROUND = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md"
BEAT_CR = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md"
LEADERBOARD = "https://kanakmalpani.github.io/LoopBench/"
ROW_SCHEMA = "https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/ROW_SCHEMA.md"
BRIDGE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BRIDGE_AGENT_HARNESSES.md"
LANGGRAPH = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/langgraph-composition-bridge.md"
AIDER = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/integrate/AIDER.md"

AGENTLESS_BODY = f"""## Collaboration invite — benchmark your repair loop on LoopBench

Hi @OpenAutoCoder maintainers — Agentless solves software repair with a closed **locate → patch → verify** loop, which maps cleanly to our public **LB-CR-1** (code repair) task.

We run a fixed-seed, no-API-key scoreboard for comparable loop engineering:

| | |
|---|---|
| **Live board** | {LEADERBOARD} |
| **Task** | LB-CR-1 — fix broken code under test-suite pressure |
| **60-second path** | {BEAT_CR} |
| **Row schema** | {ROW_SCHEMA} |

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopbench>=0.1.1" "loopgym>=0.1.2"
loopbench run --task LB-CR-1 --spec your-agentless-loop.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
# → PR to KanakMalpani/LoopBench leaderboard/entries.json
```

**What we need:** one maintainer or contributor PR with your loop mapped to LSS YAML + observed LES. First **non-maintainer** row gets permanent leaderboard credit and a shout-out on Loop Engineering.

Happy to pair on the LSS mapping (`workers` / `evaluators` / `termination_conditions`) if useful. Playground hub: {PLAYGROUND}

— Loop Engineering community ([issue #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4))
"""

AIDER_BODY = f"""## Collaboration invite — score Aider loops on LoopBench (LB-CR-1)

Hi @paul-gauthier — Aider's edit-test loop is a natural fit for our public **code repair** benchmark.

| | |
|---|---|
| **Integration guide** | {AIDER} |
| **BEAT path (~60s, SimEnv, no API keys)** | {BEAT_CR} |
| **Live leaderboard** | {LEADERBOARD} |

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopbench>=0.1.1" "loopgym>=0.1.2"
loopforge intent "Implement feature with tests passing" -o aider-mapped.yaml --suggest-level
loopbench run --task LB-CR-1 --spec aider-mapped.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

Submit via PR on [LoopBench `entries.json`](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json). First external row gets named credit on the live board.

No runtime swap required — map-and-score only. Bridge patterns: {BRIDGE}

— Loop Engineering ([#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4))
"""

OPENHANDS_BODY = f"""## Collaboration invite — benchmark OpenHands on LoopBench

Hi @All-Hands-AI — OpenHands runs autonomous dev loops (plan → edit → test → iterate). We'd love the **first external row** on our public loop scoreboard.

| | |
|---|---|
| **Playground** | {PLAYGROUND} |
| **Code repair task (LB-CR-1)** | {BEAT_CR} |
| **Live board** | {LEADERBOARD} |

Map your harness to LSS YAML, run five fixed seeds in SimEnv (no API keys on v0.1), open a PR on `leaderboard/entries.json`.

We're especially interested in how OpenHands maps to:
- **S** — repo + task state
- **E** — test / verify evaluators
- **τ** — iteration / cost limits

Happy to help with the mapping. Tracking: [Loop-Engineering #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)
"""

LANGGRAPH_BODY = f"""## LoopBench invite (in addition to RFC #11)

Following up on LSS 1.1 composition — if you have a **LangGraph code-repair or reflection loop**, you can now score it on the public board:

- Bridge: {LANGGRAPH}
- BEAT LB-CR-1: {BEAT_CR}
- Live: {LEADERBOARD}

```bash
pip install "le-loopforge>=0.2.0" loopbench loopgym
loopforge export --spec loop.yaml --target langgraph --out ./graph/
loopbench run --task LB-CR-1 --spec loop.yaml --seeds 0,1,2,3,4 -o results.json
```

First external PR on [LoopBench entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) gets permanent credit. RFC feedback still welcome on [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11).
"""

CREWAI_BODY = f"""## LoopBench invite (in addition to RFC #11)

If you have a **CrewAI repair or debate loop**, you can benchmark it publicly:

- Bridge: https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/crewai-composition-bridge.md
- Tasks: LB-CR-1 (repair) · LB-MA-1 (multi-agent)
- Live: {LEADERBOARD}

```bash
pip install "le-loopforge>=0.2.0" loopbench loopgym
loopbench run --task LB-CR-1 --spec your-crew.yaml --seeds 0,1,2,3,4 -o results.json
```

First external row on [entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) — we're looking for the first non-maintainer submitter. Thanks!
"""

DISCUSSION_10_BODY = f"""## Adoption wave 11 — repo owners: submit the first external LoopBench row

We're inviting maintainers of **code-repair and agent-loop repos** to map their loop to LSS and open a PR on [LoopBench](https://github.com/KanakMalpani/LoopBench).

**Outreach sent (2026-06-25):**
- [OpenAutoCoder/Agentless](https://github.com/OpenAutoCoder/Agentless/issues) — repair loop ↔ LB-CR-1
- [paul-gauthier/aider](https://github.com/paul-gauthier/aider/issues) — edit-test loop ↔ LB-CR-1
- [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands/issues) — autonomous dev loop
- LangGraph + CrewAI RFC threads — LoopBench invite added

**Your turn (~30 min, no API keys):**
1. [LOOP_PLAYGROUND.md]({PLAYGROUND})
2. [BEAT_LB-CR-1.md]({BEAT_CR})
3. PR → `leaderboard/entries.json`
4. Comment here with your row link

First **non-maintainer** submission flips the adoption tracker green.
"""

ISSUE_4_BODY = f"""## Wave 11 — outreach to loop repo owners (2026-06-25)

Invited external maintainers to submit the first LoopBench row:

| Repo | Fit | Issue |
|------|-----|-------|
| **Agentless** | Repair loop → LB-CR-1 | OpenAutoCoder/Agentless |
| **Aider** | Edit-test loop → LB-CR-1 | paul-gauthier/aider |
| **OpenHands** | Dev agent loop → LB-CR-1 | All-Hands-AI/OpenHands |
| **LangGraph / CrewAI** | Composition + repair | Existing RFC issues updated |

Live board: {LEADERBOARD}

Community path unchanged: {BEAT_CR} → validate → LoopBench PR.
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


def gh_issue_create(repo: str, title: str, body: str) -> str | None:
    result = subprocess.run(
        ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return None
    url = result.stdout.strip()
    print(f"Created {repo}: {url}")
    return url


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
    stamp = f"\n\n_Posted {when} UTC via adoption_wave11.py_"

    urls: list[str] = []

    u = gh_issue_create(
        "OpenAutoCoder/Agentless",
        "[Collaboration] Benchmark your repair loop on LoopBench (LB-CR-1)",
        AGENTLESS_BODY + stamp,
    )
    if u:
        urls.append(u)

    u = gh_issue_create(
        "paul-gauthier/aider",
        "[Collaboration] Score Aider loops on public LoopBench (LB-CR-1)",
        AIDER_BODY + stamp,
    )
    if u:
        urls.append(u)

    u = gh_issue_create(
        "All-Hands-AI/OpenHands",
        "[Collaboration] First external row on LoopBench — map OpenHands loop",
        OPENHANDS_BODY + stamp,
    )
    if u:
        urls.append(u)

    gh_issue_comment("langchain-ai/langgraph", 8186, LANGGRAPH_BODY + stamp)
    gh_issue_comment("crewAIInc/crewAI", 6316, CREWAI_BODY + stamp)

    data = gh_graphql(COMMENT_MUTATION, {"id": DISCUSSION_10, "body": DISCUSSION_10_BODY + stamp})
    if data:
        print("Discussion #10:", data["addDiscussionComment"]["comment"]["url"])

    gh_issue_comment("KanakMalpani/Loop-Engineering", 4, ISSUE_4_BODY + stamp)

    print("\nAdoption wave 11 complete.")
    for url in urls:
        print(" ", url)
    return 0 if urls else 1


if __name__ == "__main__":
    raise SystemExit(main())
