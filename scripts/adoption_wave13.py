#!/usr/bin/env python3
"""Adoption wave 13 — rotate targets (Reflexion, DSPy, SmolAgents) + community unlock posts."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

DISCUSSION_10 = "D_kwDOS5f_ic4AnVY4"
DISCUSSION_11 = "D_kwDOS5f_ic4AnVaQ"

GOLDEN = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md"
BEAT = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_LB-CR-1.md"
TEMPLATE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/reproduction-reports/TEMPLATE-trace-native.md"
PARTNER = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PARTNER_LOOPBENCH_SUBMIT.md"
EXAM = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/education/practitioner/exam-v0.2.md"
CASE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/TEMPLATE.md"
LSS_11 = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/standards/LSS-1.1.md"
COMPOSE = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/compositions/scenario-swarm-rehearsal.yaml"
LEADERBOARD = "https://kanakmalpani.github.io/LoopBench/"

REFLEXION_BODY = f"""## Collaboration invite — benchmark Reflexion on LoopBench (LB-CR-1)

Reflexion's verbal self-reflection loop maps cleanly to LSS **reflection-loop** + test evaluators — ideal for our public **code repair** task.

| | |
|---|---|
| **BEAT path (~60s, SimEnv)** | {BEAT} |
| **Partner PR kit** | {PARTNER} |
| **Live board** | {LEADERBOARD} |

```bash
pip install "le-loop-stack[bench]>=0.1.0"
loopctl pipeline --intent "Fix failing unit tests with reflection" -o reflexion-mapped.yaml --json
loopbench run --task LB-CR-1 --spec reflexion-mapped.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

First **non-maintainer** row gets permanent leaderboard credit + Community Spotlight.

— Loop Engineering ([#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4))
"""

DSPY_BODY = f"""## Collaboration invite — score DSPy programs on LoopBench

DSPy compile/optimize loops are a natural fit for **LB-CR-1** (repair) and **LB-RS-1** (research synthesis).

```bash
pip install "le-loop-stack[bench]>=0.1.0"
loopforge intent "Optimize a program until tests pass" -o dspy-mapped.yaml --suggest-level
loopbench run --task LB-CR-1 --spec dspy-mapped.yaml --seeds 0,1,2,3,4 -o results.json
```

Partner guide: {PARTNER} · Live board: {LEADERBOARD}

Reply here or on [Loop-Engineering #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) if you'd like a 15-min mapping pairing.
"""

SMOL_BODY = f"""## Collaboration invite — SmolAgents on LoopBench

SmolAgents' tool-use loops map to LSS worker + evaluator cycles. We'd love the first external row from the Hugging Face agent ecosystem.

- BEAT LB-CR-1: {BEAT}
- Golden Path: {GOLDEN}
- Board: {LEADERBOARD}

```bash
pip install "le-loop-stack[bench]>=0.1.0"
loopbench run --task LB-CR-1 --spec your-smolagents-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

Tracking: [Loop-Engineering #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)
"""

DISCUSSION_10_BODY = f"""## Beat maintainer LB-CR-1 LES (86.7) — trace-native challenge

**Target:** beat maintainer dry-run **observed LES 86.7** on LB-CR-1 with a **trace-native** reproduction (no API keys on SimEnv v0.1).

```bash
pip install "le-loop-stack[bench]>=0.1.0"
loopctl pipeline \\
  --intent "Fix failing tests from CI" \\
  -o mapped.yaml \\
  --run-loopgym \\
  --trace trace.json \\
  --json
loopbench run --task LB-CR-1 --spec mapped.yaml --seeds 0,1,2,3,4 -o results.json
```

- Golden Path v3: {GOLDEN}
- Trace template: {TEMPLATE}
- Report template: paste trace link + `loopbench validate` output

**Wave 13 outreach:** Reflexion · DSPy · SmolAgents (plus wave 11/12 Agentless/Aider/OpenHands).

First **non-maintainer** comment with a filled trace report flips the adoption tracker green.
"""

DISCUSSION_11_BODY = f"""## Wave 13 — subgraph ↔ nested / crew ↔ parallel mapping

We need **one external framework mapping** to close RFC #11. Reply with 3–5 bullets:

1. **Framework** (LangGraph, CrewAI, AutoGen, custom)
2. **Sequential stage** → LSS `sequential` or worker order
3. **Parallel branch** → LSS `parallel` or multi-worker
4. **Nested inner loop** → LSS `nested` or subgraph compile
5. **One friction point** vs [LSS-1.1]({LSS_11})

Example composed spec: [scenario-swarm-rehearsal.yaml]({COMPOSE})

Optional tooling:

```bash
pip install "le-loop-stack>=0.1.0"
loopforge intent "Parallel research and coding branches" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
```
"""

ISSUE_12_BODY = f"""## Exam v0.2 — seeking 3 external pilot volunteers

We need **3 non-maintainer** pilot reports to close the adoption gap on practitioner certification.

**Exam:** [exam-v0.2.md]({EXAM}) (~35 min after README)  
**Theme:** map your harness → LSS → score → optional LoopBench row

### How to participate

1. Read [exam-v0.2.md]({EXAM}) and complete Parts A–C.
2. Comment on this issue with:
   - GitHub handle (non-maintainer account)
   - Harness/framework used
   - Score (X/22) + checklist complete (yes/no)
   - One friction point (1–2 sentences)
3. Optional: open LoopBench PR referencing [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

**Slots:** 3 pilots · first-come · maintainer replies within 48h.

Integration path: {GOLDEN}
"""

ISSUE_7_BODY = f"""## Wave 13 — external org case study pairing offered

Looking for the **first external org** case study (not already in our catalog) with full loop tuple + LES.

1. Map your harness: `pip install "le-loop-stack>=0.1.0"` + [Golden Path]({GOLDEN})
2. Fill [TEMPLATE.md]({CASE})
3. Open PR referencing this issue

Maintainer pairing available — reply here with your org + harness name. PRs get the [external submission checklist](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/EXTERNAL_SUBMISSIONS.md) automatically.
"""

ISSUE_4_BODY = f"""## Wave 13 — rotated outreach (Reflexion, DSPy, SmolAgents)

Follow-up on wave 11/12 partner invites. New targets:

| Repo | Fit | Task |
|------|-----|------|
| **Reflexion** | Reflection repair loop | LB-CR-1 |
| **DSPy** | Compile/optimize loop | LB-CR-1, LB-RS-1 |
| **SmolAgents** | Tool-use agent loop | LB-CR-1 |

Community path unchanged: {BEAT} → validate → LoopBench PR.  
Partner kit: {PARTNER} · Live: {LEADERBOARD}

**Hard rule:** maintainer/bot rows do not count as external proof.
"""

LANGGRAPH_BODY = f"""## Wave 13 follow-up — composition mapping + LoopBench

Please reply with **subgraph ↔ nested** mapping notes for [LSS-1.1]({LSS_11}).

Example: parallel fan-out → `composition.type: parallel`; inner compile() → `nested`.

RFC thread: https://github.com/KanakMalpani/Loop-Engineering/discussions/11  
Composed spec: {COMPOSE}
"""

CREWAI_BODY = f"""## Wave 13 follow-up — crew ↔ parallel tuple mapping

Please reply with **crew ↔ parallel** mapping notes for [LSS-1.1]({LSS_11}).

Example: hierarchical crew → `nested`; sequential crew tasks → `sequential`.

RFC thread: https://github.com/KanakMalpani/Loop-Engineering/discussions/11
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
    stamp = f"\n\n_Posted {when} UTC via adoption_wave13.py_"
    urls: list[str] = []

    for repo, title, body in [
        (
            "noahshinn/reflexion",
            "[Collaboration] Benchmark Reflexion on LoopBench (LB-CR-1)",
            REFLEXION_BODY + stamp,
        ),
        (
            "stanfordnlp/dspy",
            "[Collaboration] Score DSPy programs on public LoopBench",
            DSPY_BODY + stamp,
        ),
        (
            "huggingface/smolagents",
            "[Collaboration] First external LoopBench row from SmolAgents",
            SMOL_BODY + stamp,
        ),
    ]:
        u = gh_issue_create(repo, title, body)
        if u:
            urls.append(u)

    for disc_id, body in [
        (DISCUSSION_10, DISCUSSION_10_BODY + stamp),
        (DISCUSSION_11, DISCUSSION_11_BODY + stamp),
    ]:
        data = gh_graphql(COMMENT_MUTATION, {"id": disc_id, "body": body})
        if data:
            print("Discussion comment:", data["addDiscussionComment"]["comment"]["url"])

    gh_issue_comment("KanakMalpani/Loop-Engineering", 4, ISSUE_4_BODY + stamp)
    gh_issue_comment("KanakMalpani/Loop-Engineering", 7, ISSUE_7_BODY + stamp)
    gh_issue_comment("KanakMalpani/Loop-Engineering", 12, ISSUE_12_BODY + stamp)
    gh_issue_comment("langchain-ai/langgraph", 8186, LANGGRAPH_BODY + stamp)
    gh_issue_comment("crewAIInc/crewAI", 6316, CREWAI_BODY + stamp)

    print("\nAdoption wave 13 complete.")
    for url in urls:
        print(" ", url)
    return 0 if urls else 1


if __name__ == "__main__":
    raise SystemExit(main())
