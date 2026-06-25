#!/usr/bin/env python3
"""Preview LoopBench leaderboard markdown for spotlight drafts (read-only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from leaderboard_common import (  # noqa: E402
    flatten_entries,
    load_entries_from_file,
    load_entries_from_url,
    rank_by_task,
    render_live_markdown,
)


def render_spotlight_draft(board: dict) -> str:
    rows = flatten_entries(board)
    external = [r for r in rows if r.is_external]
    ranked = rank_by_task(external, top_n=5, external_only=True)

    lines = [
        "# Spotlight draft (external only)",
        "",
        "_Generated for maintainer review — not auto-published._",
        "",
    ]
    if not external:
        lines.append("No external submitters yet. See LOOP_PLAYGROUND.md outreach.")
        lines.append("")
        return "\n".join(lines)

    for task_id, task_rows in ranked.items():
        if not task_rows:
            continue
        lines.append(f"## {task_id}")
        lines.append("")
        for i, row in enumerate(task_rows, 1):
            lines.append(
                f"{i}. **{row.submitter}** — LES {row.les_display:.1f} · "
                f"[spec]({row.spec_path}) · `{row.repro_command}`"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview LoopBench leaderboard")
    parser.add_argument("--url", action="store_true", help="Fetch live entries.json")
    parser.add_argument("--entries", type=Path, help="Local entries.json")
    parser.add_argument("--spotlight", action="store_true", help="External-only spotlight draft")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    if args.entries:
        board = load_entries_from_file(args.entries)
    else:
        board = load_entries_from_url()

    text = render_spotlight_draft(board) if args.spotlight else render_live_markdown(board)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
