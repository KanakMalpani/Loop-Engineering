#!/usr/bin/env python3
"""Post reproduction report to GitHub Discussion #10."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCUSSION_ID = "D_kwDOS5f_ic4AnVY4"
BODY_PATH = ROOT / "docs" / "reproduction-reports" / "discussion-comment.md"

QUERY = """
mutation($id: ID!, $body: String!) {
  addDiscussionComment(input: {discussionId: $id, body: $body}) {
    comment { url }
  }
}
"""


def main() -> int:
    body = BODY_PATH.read_text(encoding="utf-8")
    payload = json.dumps({"query": QUERY, "variables": {"id": DISCUSSION_ID, "body": body}})
    result = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return 1
    data = json.loads(result.stdout)
    if "errors" in data:
        print(json.dumps(data["errors"], indent=2), file=sys.stderr)
        return 1
    url = data["data"]["addDiscussionComment"]["comment"]["url"]
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
