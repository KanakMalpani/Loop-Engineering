"""Fork existing loop-library templates."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def library_root(custom: Path | None = None) -> Path:
    if custom is not None:
        return custom
    return repo_root() / "loop-library"


def resolve_library_path(name: str, library_dir: Path | None = None) -> Path:
    root = library_root(library_dir)
    stem = name.removesuffix(".yaml").removesuffix(".yml")
    for candidate in (root / f"{stem}.yaml", root / f"{stem}.yml", root / "compositions" / f"{stem}.yaml"):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Library template not found: {name} (searched {root})")


def load_library_spec(name: str, library_dir: Path | None = None) -> dict:
    path = resolve_library_path(name, library_dir)
    with path.open(encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    if not isinstance(spec, dict):
        raise ValueError(f"Invalid library spec: {path}")
    return spec


def fork_spec(source_name: str, new_name: str, *, library_dir: Path | None = None) -> dict:
    spec = deepcopy(load_library_spec(source_name, library_dir))
    spec["loop_name"] = new_name
    meta = spec.setdefault("metadata", {})
    if isinstance(meta, dict):
        meta["forked_from"] = source_name
    return spec
