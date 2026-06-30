"""Resolve bundled loop-library paths (PyPI-native, no repo clone required)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def bundled_library_root() -> Path:
    return Path(__file__).resolve().parent / "loop_library"


def repo_library_root() -> Path | None:
    root = Path(__file__).resolve().parents[1]
    lib = root / "loop-library"
    return lib if lib.is_dir() else None


def library_root(custom: Path | None = None) -> Path:
    if custom is not None:
        return custom
    env = os.environ.get("LOOP_LIBRARY_DIR")
    if env:
        return Path(env)
    repo = repo_library_root()
    if repo is not None:
        return repo
    bundled = bundled_library_root()
    if bundled.is_dir() and any(bundled.glob("*.yaml")):
        return bundled
    return bundled
