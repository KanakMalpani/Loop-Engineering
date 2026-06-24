#!/usr/bin/env python3
"""Push a local file to a GitHub repo via Contents API."""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path


def gh_json(args: list[str]) -> dict | list | None:
    result = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout) if result.stdout.strip() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args()

    content = args.file.read_text(encoding="utf-8")
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")

    meta = gh_json([f"repos/KanakMalpani/{args.repo}/contents/{args.path}"])
    body: dict = {"message": args.message, "content": b64}
    if isinstance(meta, dict) and meta.get("sha"):
        body["sha"] = meta["sha"]

    payload_path = Path("_gh_push_payload.json")
    payload_path.write_text(json.dumps(body), encoding="utf-8")
    result = subprocess.run(
        ["gh", "api", "-X", "PUT", f"repos/KanakMalpani/{args.repo}/contents/{args.path}", "--input", str(payload_path)],
        text=True,
        capture_output=True,
    )
    payload_path.unlink(missing_ok=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return 1
    print(f"OK: {args.repo}/{args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
