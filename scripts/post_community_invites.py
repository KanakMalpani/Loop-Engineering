#!/usr/bin/env python3
"""Post community invitation comments on Discussions #10 and #11."""

from __future__ import annotations

import json
import subprocess
import sys

DISCUSSIONS = {
    "D_kwDOS5f_ic4AnVY4": "https://github.com/KanakMalpani/Loop-Engineering/discussions/10",
    "D_kwDOS5f_ic4AnVaQ": "https://github.com/KanakMalpani/Loop-Engineering/discussions/11",
}

BODIES = {
    "D_kwDOS5f_ic4AnVY4": """## Community call — external reproduction reports wanted

Maintainer dry-run is posted; we need **your** fork → validate → run → LES report to flip the adoption tracker green.

**Pack:** [EXTERNAL_SUBMISSIONS.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/EXTERNAL_SUBMISSIONS.md) §2  
**Guide:** [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md) (~60 min)

Post below with fork URL, validator output, and one benchmark or LoopGym replay snippet. Non-maintainer accounts only — thanks!""",
    "D_kwDOS5f_ic4AnVaQ": """## Framework maintainers — LSS 1.1 composition mapping

RFC synthesis is merged; **LangGraph / CrewAI / Cursor** users: does this topology match your harness?

```yaml
composition:
  type: parallel
  children: [...]
  adapters: [...]
  merge: { strategy: synthesize }
```

**RFC:** [RFC-LSS-1.1-composition.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/RFC-LSS-1.1-composition.md)  
**Bridge guide:** [BRIDGE_AGENT_HARNESSES.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BRIDGE_AGENT_HARNESSES.md)

One paragraph on what maps / what doesn't is enough to unblock stable promotion.""",
}

QUERY = """
mutation($id: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $id, body: $body}) {
    comment { url }
  }
}
"""


def post(discussion_id: str, body: str) -> str | None:
    payload = json.dumps({"query": QUERY, "variables": {"id": discussion_id, "body": body}})
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
    return data["data"]["addDiscussionComment"]["comment"]["url"]


def main() -> int:
    for did, body in BODIES.items():
        url = post(did, body)
        if not url:
            return 1
        print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
