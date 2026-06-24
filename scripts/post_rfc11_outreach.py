#!/usr/bin/env python3
"""Post RFC #11 outreach comments to LangGraph and CrewAI GitHub repos."""

from __future__ import annotations

import json
import subprocess
import sys

DISCUSSION_URL = "https://github.com/KanakMalpani/Loop-Engineering/discussions/11"
RFC_URL = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/RFC-LSS-1.1-composition.md"

TARGETS = [
    {
        "repo": "langchain-ai/langgraph",
        "title": "RFC feedback: LSS 1.1 composition blocks vs graph topology",
        "body": f"""Hi LangGraph maintainers — we're stabilizing **LSS 1.1** (Loop Specification Standard) composition syntax and would value a quick mapping check.

**Question:** Does this model match how you think about LangGraph graphs?

```yaml
composition:
  type: sequential | parallel | nested
  children:
    - ref: loop-library/research-agent.yaml
  adapters:
    - from: children[0].outputs.Result
      to: children[1].inputs.task
```

- **Nodes** → `composition.children`
- **Edges / state routing** → `adapters`
- **Parallel branches** → `type: parallel` + `merge` block

Full RFC: {RFC_URL}
Comment thread: {DISCUSSION_URL}

No action required — a short "maps / doesn't map because …" comment on the discussion would unblock our stable release. Thanks!""",
    },
    {
        "repo": "crewAIInc/crewAI",
        "title": "RFC feedback: LSS 1.1 composition vs CrewAI crew topology",
        "body": f"""Hi CrewAI maintainers — stabilizing **LSS 1.1** composition blocks for agent loops. Seeking framework maintainer feedback.

**Question:** Does `composition.children` + `adapters` cover your crew/task handoff model?

- **Roles / agents** → `children`
- **Task output → next task input** → `adapters`
- **Parallel crews** → `type: parallel` + `merge`

RFC: {RFC_URL}
Discussion: {DISCUSSION_URL}

A brief mapping note on the discussion thread helps us finalize the spec. Thank you!""",
    },
]


def gh_json(args: list[str]) -> dict | list | None:
    result = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return None
    return json.loads(result.stdout) if result.stdout.strip() else None


def find_or_create_issue(owner: str, repo: str, title: str, body: str) -> str | None:
    q = f"repo:{owner}/{repo} is:issue in:title \"RFC feedback: LSS 1.1\""
    search = subprocess.run(
        ["gh", "search", "issues", q, "--json", "url,title", "--limit", "5"],
        capture_output=True,
        text=True,
    )
    if search.returncode == 0 and search.stdout.strip():
        items = json.loads(search.stdout)
        for item in items:
            if "LSS 1.1" in item.get("title", ""):
                return item["url"]

    payload = json.dumps({"title": title, "body": body})
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/issues", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return None
    data = json.loads(result.stdout)
    return data.get("html_url")


def main() -> int:
    urls: list[str] = []
    for target in TARGETS:
        owner, repo = target["repo"].split("/", 1)
        url = find_or_create_issue(owner, repo, target["title"], target["body"])
        if url:
            print(url)
            urls.append(url)
        else:
            print(f"FAILED: {target['repo']}", file=sys.stderr)
            return 1
    print(f"\nPosted/linked {len(urls)} outreach issue(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
