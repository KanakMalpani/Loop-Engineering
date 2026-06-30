#!/usr/bin/env python3
"""Track 2027 adoption signals (LoopBench, discussions, PyPI, good-first issues)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# Submitters that do not count as external adoption
INTERNAL_SUBMITTER_MARKERS = (
    "loop engineering maintainer",
    "team thorough",
    "team fast",
    "golden",
    "local-dev",
)

MAINTAINER_AUTHORS = (
    "kanakmalpani",
    "github-actions[bot]",
)

GOOD_FIRST_ISSUES = {
    4: "Non-maintainer LoopBench row (LB-CR-1)",
    7: "External case study (new org)",
    8: "Cursor case study extension",
    9: "LoopNet explore histograms",
    12: "Practitioner exam v0.2 pilots",
}

DISCUSSIONS = {
    10: "Reproduction challenge — external report",
    11: "RFC LSS 1.1 — framework feedback",
}

PYPI_MIN_LOOPBENCH = (0, 2, 0)
PYPI_MIN_LOOPGYM = (0, 1, 2)
PYPI_MIN_LOOPFORGE = (0, 5, 0)
PYPI_MIN_LOOPCTL = (0, 5, 0)
PYPI_MIN_LOOPSTACK = (0, 4, 0)
PYPI_LOOPGYM_URL = "https://pypi.org/pypi/loopgym/json"
PYPI_LOOPFORGE_URL = "https://pypi.org/pypi/le-loopforge/json"
PYPI_LOOPCTL_URL = "https://pypi.org/pypi/le-loopctl/json"
PYPI_LOOPSTACK_URL = "https://pypi.org/pypi/le-loop-stack/json"
LEADERBOARD_URL = (
    "https://raw.githubusercontent.com/KanakMalpani/LoopBench/main/leaderboard/entries.json"
)
PYPI_URL = "https://pypi.org/pypi/loopbench/json"
ISSUES_API = "https://api.github.com/repos/KanakMalpani/Loop-Engineering/issues/{n}"
CORE_LSS_STABLE_URL = (
    "https://raw.githubusercontent.com/KanakMalpani/Loop-Core-Engineering/main/specs/lss-1.1.md"
)
LOOPBENCH_LIVE_MD_URL = (
    "https://raw.githubusercontent.com/KanakMalpani/LoopBench/main/leaderboard/LIVE.md"
)


@dataclass
class Signal:
    id: str
    name: str
    status: str  # green | yellow | red
    detail: str
    link: str = ""


def fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "loop-engineering-tracker"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any] | None:
    payload = json.dumps({"query": query, "variables": variables})
    try:
        result = subprocess.run(
            ["gh", "api", "graphql", "--input", "-"],
            input=payload,
            text=True,
            capture_output=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    if data.get("errors"):
        return None
    return data.get("data")


def parse_version(version: str) -> tuple[int, ...]:
    parts = re.match(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version.strip())
    if not parts:
        return (0,)
    return tuple(int(x) for x in parts.groups() if x is not None)


def is_internal_submitter(name: str) -> bool:
    lower = (name or "").lower()
    return any(marker in lower for marker in INTERNAL_SUBMITTER_MARKERS)


def check_loopbench_leaderboard() -> Signal:
    try:
        board = fetch_json(LEADERBOARD_URL)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "external_loopbench",
            "Non-maintainer LoopBench row",
            "red",
            f"Could not fetch leaderboard: {exc}",
            "https://github.com/KanakMalpani/LoopBench/tree/main/leaderboard",
        )

    entries = board.get("entries") or []
    external = [
        e.get("submitter", "?")
        for e in entries
        if not is_internal_submitter(str(e.get("submitter", "")))
    ]
    if external:
        return Signal(
            "external_loopbench",
            "Non-maintainer LoopBench row",
            "green",
            f"External submitters: {', '.join(external)}",
            "https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json",
        )
    submitters = ", ".join(str(e.get("submitter", "?")) for e in entries[:6])
    return Signal(
        "external_loopbench",
        "Non-maintainer LoopBench row",
        "yellow",
        f"No external rows yet ({len(entries)} entries: {submitters})",
        "https://github.com/KanakMalpani/Loop-Engineering/issues/4",
    )


def check_pypi_loopforge() -> Signal:
    try:
        data = fetch_json(PYPI_LOOPFORGE_URL)
        version = data.get("info", {}).get("version", "0.0.0")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "pypi_loopforge",
            "le-loopforge on PyPI (>= 0.2.0)",
            "yellow",
            f"PyPI unreachable: {exc}",
            "https://pypi.org/project/le-loopforge/",
        )

    ok = parse_version(version) >= PYPI_MIN_LOOPFORGE
    return Signal(
        "pypi_loopforge",
        "le-loopforge on PyPI (>= 0.2.0)",
        "green" if ok else "yellow",
        f"PyPI version: {version}",
        "https://pypi.org/project/le-loopforge/",
    )


def check_pypi_loopctl() -> Signal:
    try:
        data = fetch_json(PYPI_LOOPCTL_URL)
        version = data.get("info", {}).get("version", "0.0.0")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "pypi_loopctl",
            "le-loopctl on PyPI (>= 0.1.0)",
            "yellow",
            f"PyPI unreachable: {exc}",
            "https://pypi.org/project/le-loopctl/",
        )

    ok = parse_version(version) >= PYPI_MIN_LOOPCTL
    return Signal(
        "pypi_loopctl",
        "le-loopctl on PyPI (>= 0.2.0)",
        "green" if ok else "yellow",
        f"PyPI version: {version}",
        "https://pypi.org/project/le-loopctl/",
    )


def check_pypi_loop_stack() -> Signal:
    try:
        data = fetch_json(PYPI_LOOPSTACK_URL)
        version = data.get("info", {}).get("version", "0.0.0")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "pypi_loop_stack",
            "le-loop-stack on PyPI (>= 0.1.0)",
            "yellow",
            f"PyPI unreachable: {exc}",
            "https://pypi.org/project/le-loop-stack/",
        )

    ok = parse_version(version) >= PYPI_MIN_LOOPSTACK
    return Signal(
        "pypi_loop_stack",
        "le-loop-stack on PyPI (>= 0.1.0)",
        "green" if ok else "yellow",
        f"PyPI version: {version}",
        "https://pypi.org/project/le-loop-stack/",
    )


def check_pypi_loopgym() -> Signal:
    try:
        data = fetch_json(PYPI_LOOPGYM_URL)
        version = data.get("info", {}).get("version", "0.0.0")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "pypi_loopgym",
            "loopgym on PyPI (>= 0.1.1)",
            "yellow",
            f"PyPI unreachable: {exc}",
            "https://pypi.org/project/loopgym/",
        )

    ok = parse_version(version) >= PYPI_MIN_LOOPGYM
    return Signal(
        "pypi_loopgym",
        "loopgym on PyPI (>= 0.1.1)",
        "green" if ok else "yellow",
        f"PyPI version: {version}",
        "https://pypi.org/project/loopgym/",
    )


def check_pypi_loopbench() -> Signal:
    try:
        data = fetch_json(PYPI_URL)
        version = data.get("info", {}).get("version", "0.0.0")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(
            "pypi_loopbench",
            "loopbench on PyPI (>= 0.1.1)",
            "yellow",
            f"PyPI unreachable: {exc}",
            "https://pypi.org/project/loopbench/",
        )

    ok = parse_version(version) >= PYPI_MIN_LOOPBENCH
    return Signal(
        "pypi_loopbench",
        "loopbench on PyPI (>= 0.1.1)",
        "green" if ok else "yellow",
        f"PyPI version: {version}",
        "https://pypi.org/project/loopbench/",
    )


def check_exam_pilot() -> Signal:
    link = "https://github.com/KanakMalpani/Loop-Engineering/issues/12"
    try:
        comments = fetch_json(
            "https://api.github.com/repos/KanakMalpani/Loop-Engineering/issues/12/comments"
        )
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal("exam_pilot", "Exam pilot reports (#12)", "yellow", str(exc), link)
    external = [
        c
        for c in comments
        if (c.get("user") or {}).get("login", "").lower() not in MAINTAINER_AUTHORS
    ]
    if external:
        return Signal(
            "exam_pilot",
            "Exam pilot reports (#12)",
            "green",
            f"{len(external)} external pilot report(s)",
            link,
        )
    n = len(comments)
    return Signal(
        "exam_pilot",
        "Exam pilot reports (#12)",
        "yellow",
        f"No external pilots yet ({n} maintainer/bot comment(s))",
        link,
    )


def check_issue(n: int, label: str) -> Signal:
    url = ISSUES_API.format(n=n)
    try:
        issue = fetch_json(url)
    except urllib.error.HTTPError as exc:
        return Signal(f"issue_{n}", label, "red", f"HTTP {exc.code}", f"https://github.com/KanakMalpani/Loop-Engineering/issues/{n}")
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        return Signal(f"issue_{n}", label, "yellow", str(exc), f"https://github.com/KanakMalpani/Loop-Engineering/issues/{n}")

    state = issue.get("state", "unknown")
    title = issue.get("title", "")
    status = "green" if state == "closed" else "yellow"
    detail = f"{state}: {title[:80]}"
    return Signal(f"issue_{n}", label, status, detail, issue.get("html_url", ""))


def discussion_comment_stats(number: int) -> tuple[int, int, str]:
    """Return (total_comments, external_comments, error_or_empty)."""
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        discussion(number: $number) {
          comments(first: 50) {
            nodes { author { login } }
          }
        }
      }
    }
    """
    data = gh_graphql(query, {"owner": "KanakMalpani", "name": "Loop-Engineering", "number": number})
    if not data:
        return 0, 0, "gh unavailable"

    nodes = (
        data.get("repository", {})
        .get("discussion", {})
        .get("comments", {})
        .get("nodes", [])
    )
    if nodes is None:
        return 0, 0, "discussion not found"

    total = len(nodes)
    external = 0
    for node in nodes:
        login = (node.get("author") or {}).get("login", "").lower()
        if login and login not in MAINTAINER_AUTHORS:
            external += 1
    return total, external, ""


def check_discussion(number: int, label: str) -> Signal:
    total, external, err = discussion_comment_stats(number)
    link = f"https://github.com/KanakMalpani/Loop-Engineering/discussions/{number}"
    if err:
        return Signal(f"discussion_{number}", label, "yellow", err, link)
    if external >= 1:
        return Signal(
            f"discussion_{number}",
            label,
            "green",
            f"{external} external comment(s) ({total} total)",
            link,
        )
    return Signal(
        f"discussion_{number}",
        label,
        "yellow",
        f"No external comments yet ({total} maintainer/bot comment(s))",
        link,
    )


def check_lss_11_stable() -> Signal:
    try:
        req = urllib.request.Request(
            CORE_LSS_STABLE_URL,
            method="HEAD",
            headers={"User-Agent": "loop-engineering-tracker"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            ok = resp.status == 200
    except urllib.error.HTTPError as exc:
        ok = exc.code == 200
    except (urllib.error.URLError, TimeoutError) as exc:
        return Signal(
            "lss_11_stable",
            "LSS 1.1 stable in Loop-Core",
            "yellow",
            str(exc),
            "https://github.com/KanakMalpani/Loop-Core-Engineering/tree/main/specs",
        )

    if ok:
        return Signal(
            "lss_11_stable",
            "LSS 1.1 stable in Loop-Core",
            "green",
            "specs/lss-1.1.md present",
            CORE_LSS_STABLE_URL.replace("raw.githubusercontent.com/KanakMalpani/", "github.com/KanakMalpani/").replace("/main/", "/blob/main/"),
        )
    return Signal(
        "lss_11_stable",
        "LSS 1.1 stable in Loop-Core",
        "yellow",
        "Only lss-1.1-draft.md (stable not promoted)",
        "https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1-draft.md",
    )


def check_community_platform_v1() -> Signal:
    playground = ROOT / "contributions" / "LOOP_PLAYGROUND.md"
    digest_wf = ROOT / ".github" / "workflows" / "ecosystem-digest.yml"
    status_doc = ROOT / "docs" / "maintainer" / "COMMUNITY_PLATFORM_STATUS.md"
    link = "https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/maintainer/COMMUNITY_PLATFORM_STATUS.md"

    missing = [
        name
        for path, name in (
            (playground, "LOOP_PLAYGROUND.md"),
            (digest_wf, "ecosystem-digest.yml"),
            (status_doc, "COMMUNITY_PLATFORM_STATUS.md"),
        )
        if not path.is_file()
    ]
    if missing:
        return Signal(
            "community_platform_v1",
            "Community platform v1 (playground + digest)",
            "yellow",
            f"Missing: {', '.join(missing)}",
            link,
        )

    live_ok = False
    try:
        req = urllib.request.Request(
            LOOPBENCH_LIVE_MD_URL,
            method="HEAD",
            headers={"User-Agent": "loop-engineering-tracker"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            live_ok = resp.status == 200
    except urllib.error.HTTPError as exc:
        live_ok = exc.code == 200
    except (urllib.error.URLError, TimeoutError) as exc:
        return Signal(
            "community_platform_v1",
            "Community platform v1 (playground + digest)",
            "yellow",
            f"LoopBench LIVE.md check failed: {exc}",
            link,
        )

    if live_ok:
        return Signal(
            "community_platform_v1",
            "Community platform v1 (playground + digest)",
            "green",
            "Playground + digest workflow + LoopBench LIVE.md live",
            link,
        )
    return Signal(
        "community_platform_v1",
        "Community platform v1 (playground + digest)",
        "yellow",
        "LE shipped; push LoopBench sync pack for LIVE.md (see ecosystem-sync/LoopBench/)",
        link,
    )


def collect_signals() -> list[Signal]:
    signals: list[Signal] = [
        check_loopbench_leaderboard(),
        check_community_platform_v1(),
        check_discussion(10, DISCUSSIONS[10]),
        check_discussion(11, DISCUSSIONS[11]),
        check_pypi_loopbench(),
        check_pypi_loopgym(),
        check_pypi_loopforge(),
        check_pypi_loopctl(),
        check_pypi_loop_stack(),
        check_lss_11_stable(),
        check_exam_pilot(),
    ]
    for num, label in GOOD_FIRST_ISSUES.items():
        signals.append(check_issue(num, label))
    return signals


def render_markdown(signals: list[Signal], when: datetime) -> str:
    green = sum(1 for s in signals if s.status == "green")
    yellow = sum(1 for s in signals if s.status == "yellow")
    red = sum(1 for s in signals if s.status == "red")

    lines = [
        f"# Adoption tracker — {when.strftime('%Y-%m-%d')} UTC",
        "",
        f"**Summary:** {green} green · {yellow} yellow · {red} red",
        "",
        "Automated by `scripts/track_adoption_signals.py` (daily with [daily-checkin.yml](../.github/workflows/daily-checkin.yml)).",
        "",
        "| Signal | Status | Detail |",
        "|--------|--------|--------|",
    ]
    for s in signals:
        mark = s.status.upper()
        link = f" [{s.id}]({s.link})" if s.link else ""
        detail = s.detail.replace("|", "\\|")[:100]
        lines.append(f"| {s.name}{link} | **{mark}** | {detail} |")

    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```bash",
            "python scripts/track_adoption_signals.py",
            "python scripts/daily_checkin.py --output docs/checkins/latest.md",
            "```",
            "",
            f"_Generated at {when.isoformat()}_",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Track Loop Engineering adoption signals")
    parser.add_argument("--output", type=Path, help="Write markdown report")
    parser.add_argument("--json", type=Path, help="Write JSON snapshot")
    args = parser.parse_args()

    when = datetime.now(timezone.utc)
    signals = collect_signals()

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": when.isoformat(),
            "signals": [asdict(s) for s in signals],
        }
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {args.json}")

    report = render_markdown(signals, when)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(report)

    for s in signals:
        icon = {"green": "OK", "yellow": "PEND", "red": "FAIL"}[s.status]
        print(f"[{icon}] {s.id}: {s.detail[:80]}")

    # Tracker never fails CI — adoption gaps are expected
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
