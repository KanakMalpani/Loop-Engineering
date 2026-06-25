#!/usr/bin/env python3
"""Aider integration smoke (Phase 11)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from integrate_smoke_common import run_map_score_demo  # noqa: E402


def main() -> int:
    return run_map_score_demo(
        "aider",
        "Implement feature from issue with tests passing",
    )


if __name__ == "__main__":
    raise SystemExit(main())
