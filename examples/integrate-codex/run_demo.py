#!/usr/bin/env python3
"""OpenAI Codex integration smoke (Phase 11)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from integrate_smoke_common import run_map_score_demo  # noqa: E402


def main() -> int:
    return run_map_score_demo(
        "codex",
        "Repair failing unit tests with minimal code changes",
    )


if __name__ == "__main__":
    raise SystemExit(main())
