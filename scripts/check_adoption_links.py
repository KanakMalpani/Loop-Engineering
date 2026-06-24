#!/usr/bin/env python3
"""Verify canonical adoption URLs appear in discipline and ecosystem-sync docs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ADOPTION_PATH = "github.com/KanakMalpani/Loop-Engineering/discussions/10"
REPRODUCE_PATH = "github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md"

LOCAL_FILES = [
    ROOT / "README.md",
    ROOT / "contributions" / "REPRODUCE.md",
    ROOT / "contributions" / "BRIDGE_AGENT_HARNESSES.md",
    ROOT / "research" / "LOOPNET.md",
    ROOT / "examples" / "loopnet-explore" / "README.md",
    ROOT / "docs" / "hf-loopnet-v0.2-README.md",
    ROOT / "docs" / "ecosystem-sync" / "LoopBench-README.md",
    ROOT / "docs" / "ecosystem-sync" / "loopnet-README.md",
    ROOT / "docs" / "ecosystem-sync" / "LoopGym-README.md",
    ROOT / "docs" / "ecosystem-sync" / "Loop-Core-Engineering-README.md",
]

ECOSYSTEM_SYNC = ROOT / "docs" / "ecosystem-sync"


def check_file(path: Path, needle: str) -> str | None:
    if not path.exists():
        return f"missing file: {path.relative_to(ROOT)}"
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        return f"missing {needle!r} in {path.relative_to(ROOT)}"
    return None


def main() -> int:
    errors: list[str] = []

    for path in LOCAL_FILES:
        err = check_file(path, ADOPTION_PATH)
        if err:
            errors.append(err)

    for path in LOCAL_FILES:
        if path.name.endswith("README.md") and "ecosystem-sync" in str(path):
            err = check_file(path, REPRODUCE_PATH)
            if err and "Loop-Core" not in path.name:
                errors.append(err.replace(ADOPTION_PATH, REPRODUCE_PATH))

    if not ECOSYSTEM_SYNC.is_dir():
        errors.append("missing docs/ecosystem-sync/ directory")

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print(f"OK: adoption links present in {len(LOCAL_FILES)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
