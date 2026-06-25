#!/usr/bin/env python3
"""Fail if canonical docs use wrong PyPI install names (loopforge/loopctl without le- prefix)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN_FILES = [
    ROOT / "README.md",
    ROOT / "contributions" / "GOLDEN_PATH.md",
    ROOT / "contributions" / "BEAT_TEMPLATE.md",
    ROOT / "contributions" / "EXTERNAL_SUBMISSIONS.md",
    ROOT / "contributions" / "REPRODUCE.md",
    ROOT / "standards" / "CANONICAL-SOURCE.md",
    ROOT / "ECOSYSTEM_VERSIONS.md",
]

BAD_PATTERNS = [
    re.compile(r"pip install loopforge\b"),
    re.compile(r"pip install loopctl\b"),
    re.compile(r'pip install "loopforge'),
    re.compile(r'pip install "loopctl'),
]


def main() -> int:
    errors: list[str] = []
    for path in SCAN_FILES:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "le-loopforge" in line or "le-loopctl" in line:
                continue
            for pat in BAD_PATTERNS:
                if pat.search(line):
                    errors.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:80]}")
                    break

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        print("See contributions/PYPI_NAMING.md", file=sys.stderr)
        return 1

    print(f"OK: PyPI naming guard passed ({len(SCAN_FILES)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
