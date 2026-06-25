#!/usr/bin/env python3
"""Ecosystem digest: poll LoopBench + adoption tracker; update pinned ops issue on change."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from leaderboard_common import LEADERBOARD_URL, flatten_entries, load_entries_from_url  # noqa: E402

STATUS_FILE = ROOT / "docs" / "maintainer" / "COMMUNITY_PLATFORM_STATUS.md"
AUTOMATION_START = "<!-- AUTOMATION-LOG:START -->"
AUTOMATION_END = "<!-- AUTOMATION-LOG:END -->"

OUTREACH_ISSUES = (
    ("OpenAutoCoder/Agentless", 86),
    ("Aider-AI/aider", 5328),
    ("OpenHands/OpenHands", 14984),
)


def fetch_json(url: str, token: str | None = None) -> Any:
    headers = {"User-Agent": "loop-engineering-digest", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_tracker_json() -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out = Path(tmp.name)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "track_adoption_signals.py"), "--json", str(out)],
        check=True,
        cwd=ROOT,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    out.unlink(missing_ok=True)
    return data


def digest_hash(leaderboard: dict, tracker: dict, outreach: list[dict[str, str]] | None = None) -> str:
    payload = {
        "leaderboard_updated": leaderboard.get("updated"),
        "entry_count": len(leaderboard.get("entries") or []),
        "external_submitters": sorted(
            {r.submitter for r in flatten_entries(leaderboard) if r.is_external}
        ),
        "signals": {
            s["id"]: s["status"]
            for s in tracker.get("signals", [])
            if s.get("id") in ("external_loopbench", "community_platform_v1")
        },
        "outreach_replies": [
            f"{o['repo']}#{o['issue']}:{o['author']}"
            for o in (outreach or [])
            if o.get("author") and o["author"] != "_no external replies_"
        ],
    }
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def fetch_open_prs(token: str | None) -> list[dict[str, str]]:
    if not token:
        return []
    prs: list[dict[str, str]] = []
    # LoopBench: PRs touching entries.json
    lb_url = (
        "https://api.github.com/search/issues?q="
        "repo:KanakMalpani/LoopBench+is:pr+is:open+entries.json"
    )
    try:
        data = fetch_json(lb_url, token)
        for item in data.get("items", [])[:5]:
            prs.append(
                {
                    "repo": "KanakMalpani/LoopBench",
                    "title": item.get("title", ""),
                    "url": item.get("html_url", ""),
                }
            )
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        pass

    le_url = (
        "https://api.github.com/search/issues?q="
        "repo:KanakMalpani/Loop-Engineering+is:pr+is:open+"
        "(case-study+OR+reproduction+OR+loopbench+OR+BEAT)"
    )
    try:
        data = fetch_json(le_url, token)
        for item in data.get("items", [])[:5]:
            prs.append(
                {
                    "repo": "KanakMalpani/Loop-Engineering",
                    "title": item.get("title", ""),
                    "url": item.get("html_url", ""),
                }
            )
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        pass
    return prs[:10]


def fetch_outreach_activity(token: str | None) -> list[dict[str, str]]:
    """Comments on wave-11 outreach issues (excluding repo owner bot noise)."""
    if not token:
        return []
    activity: list[dict[str, str]] = []
    for repo, num in OUTREACH_ISSUES:
        url = f"https://api.github.com/repos/{repo}/issues/{num}/comments?per_page=30"
        try:
            comments = fetch_json(url, token)
        except (urllib.error.URLError, json.JSONDecodeError):
            continue
        external = [
            c
            for c in comments
            if c.get("user", {}).get("type") != "Bot"
            and c.get("user", {}).get("login") not in ("KanakMalpani", "github-actions[bot]")
        ]
        if external:
            latest = external[-1]
            activity.append(
                {
                    "repo": repo,
                    "issue": str(num),
                    "author": latest.get("user", {}).get("login", "?"),
                    "url": latest.get("html_url", ""),
                    "preview": (latest.get("body") or "")[:80].replace("\n", " "),
                }
            )
        else:
            activity.append({"repo": repo, "issue": str(num), "author": "_no external replies_", "url": "", "preview": ""})
    return activity


def render_dashboard(
    when: datetime,
    leaderboard: dict,
    tracker: dict,
    prs: list[dict[str, str]],
    outreach: list[dict[str, str]],
    *,
    previous_hash: str | None,
    current_hash: str,
) -> str:
    rows = flatten_entries(leaderboard)
    external = sorted({r.submitter for r in rows if r.is_external})
    signals = {s["id"]: s for s in tracker.get("signals", [])}

    lines = [
        "# Loop Engineering ops dashboard",
        "",
        "_Auto-updated on change only. Do not comment — use linked issues._",
        "",
        f"**Last digest:** {when.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Leaderboard",
        "",
        f"- Updated: `{leaderboard.get('updated', '?')}`",
        f"- Entries: {len(leaderboard.get('entries') or [])}",
        f"- External submitters: {', '.join(external) if external else '_none yet_'}",
        f"- [entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json)",
        f"- [LIVE.md](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/LIVE.md)",
        "",
        "## Adoption signals",
        "",
    ]
    for sid in ("external_loopbench", "community_platform_v1"):
        sig = signals.get(sid)
        if sig:
            lines.append(f"- **{sig['name']}:** {sig['status'].upper()} — {sig['detail'][:120]}")
    lines.extend(["", "## Open adoption PRs", ""])
    if prs:
        for pr in prs:
            lines.append(f"- [{pr['repo']}] [{pr['title']}]({pr['url']})")
    else:
        lines.append("_None flagged._")
    lines.extend(["", "## Outreach responses (wave 11)", ""])
    for item in outreach:
        if item.get("url"):
            lines.append(
                f"- [{item['repo']}#{item['issue']}] @{item['author']}: "
                f"[comment]({item['url']}) — _{item.get('preview', '')}_"
            )
        else:
            lines.append(f"- [{item['repo']}#{item['issue']}]: {item['author']}")
    lines.extend(
        [
            "",
            "## Links",
            "",
            "- [Loop Playground](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md)",
            "- [Community platform status](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/maintainer/COMMUNITY_PLATFORM_STATUS.md)",
            "- [Adoption tracker](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/adoption-tracker/latest.md)",
            "",
            f"_Digest hash: `{current_hash[:12]}`"
            + (f" (changed from `{previous_hash[:12]}`)" if previous_hash and previous_hash != current_hash else ""),
            "",
        ]
    )
    return "\n".join(lines)


def append_automation_log(line: str) -> None:
    if not STATUS_FILE.exists():
        return
    text = STATUS_FILE.read_text(encoding="utf-8")
    if AUTOMATION_START not in text or AUTOMATION_END not in text:
        return
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"- {stamp}: {line}\n"
    pattern = re.compile(
        re.escape(AUTOMATION_START) + r"([\s\S]*?)" + re.escape(AUTOMATION_END)
    )

    def replacer(m: re.Match[str]) -> str:
        inner = m.group(1)
        return f"{AUTOMATION_START}{inner}{entry}{AUTOMATION_END}"

    STATUS_FILE.write_text(pattern.sub(replacer, text, count=1), encoding="utf-8")


def update_github_issue(token: str, issue_number: int, body: str) -> None:
    url = "https://api.github.com/repos/KanakMalpani/Loop-Engineering/issues/" + str(issue_number)
    payload = json.dumps({"body": body}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "loop-engineering-digest",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status not in (200, 201):
            raise RuntimeError(f"Issue update failed: {resp.status}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ecosystem digest")
    parser.add_argument("--cache-file", type=Path, help="Previous digest hash file")
    parser.add_argument("--write-cache", type=Path, help="Write current hash")
    parser.add_argument("--issue", type=int, help="Ops dashboard issue number")
    parser.add_argument("--append-log", action="store_true", help="Append to status automation log")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    when = datetime.now(timezone.utc)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    issue_num = args.issue or int(os.environ.get("OPS_DASHBOARD_ISSUE_NUMBER", "0") or "0")

    leaderboard = load_entries_from_url(LEADERBOARD_URL)
    tracker = run_tracker_json()
    outreach = fetch_outreach_activity(token)
    current_hash = digest_hash(leaderboard, tracker, outreach)

    previous_hash: str | None = None
    if args.cache_file and args.cache_file.exists():
        previous_hash = args.cache_file.read_text(encoding="utf-8").strip()

    changed = previous_hash != current_hash
    prs = fetch_open_prs(token)
    body = render_dashboard(
        when, leaderboard, tracker, prs, outreach, previous_hash=previous_hash, current_hash=current_hash
    )

    if args.dry_run:
        print(body)
        print(f"\nchanged={changed} hash={current_hash}")
        return 0

    if changed:
        if issue_num and token:
            update_github_issue(token, issue_num, body)
            print(f"Updated issue #{issue_num}")
        elif issue_num:
            print(f"Issue #{issue_num} configured but no GITHUB_TOKEN — skipping issue edit")
        if args.append_log:
            external = sorted({r.submitter for r in flatten_entries(leaderboard) if r.is_external})
            detail = f"digest changed; external={external or 'none'}"
            append_automation_log(detail)
            print("Appended automation log")
    else:
        print("No digest change — skipping issue update")

    if args.write_cache:
        args.write_cache.parent.mkdir(parents=True, exist_ok=True)
        args.write_cache.write_text(current_hash + "\n", encoding="utf-8")
        print(f"Wrote cache {args.write_cache}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
