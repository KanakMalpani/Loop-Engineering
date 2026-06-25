"""Validate LSS dicts against bundled or repo JSON Schema."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

import jsonschema
import yaml

SCHEMA_FILES = {
    "1.0": "lss-1.0.schema.json",
    "1.1": "lss-1.1-composition.schema.json",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def bundled_schema_path(lss_version: str = "1.0") -> Path:
    filename = SCHEMA_FILES.get(lss_version, SCHEMA_FILES["1.0"])
    try:
        ref = resources.files("loopforge.schemas").joinpath(filename)
        with resources.as_file(ref) as path:
            return path
    except (ModuleNotFoundError, FileNotFoundError, TypeError):
        pass
    # Dev checkout: loopforge/schemas/ or repo standards/
    local = Path(__file__).resolve().parent / "schemas" / filename
    if local.exists():
        return local
    if lss_version == "1.1":
        alt = repo_root() / "standards" / "schema" / "lss-1.1-composition.schema.json"
        if alt.exists():
            return alt
    return repo_root() / "standards" / "schema" / "lss-1.0.schema.json"


def default_schema_path(lss_version: str = "1.0") -> Path:
    return bundled_schema_path(lss_version)


def load_schema(path: Path | None = None, *, lss_version: str = "1.0") -> dict:
    schema_path = path or default_schema_path(lss_version)
    with schema_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_spec(spec: dict, schema: dict | None = None, *, lss_version: str = "1.0") -> list[str]:
    schema_data = schema if schema is not None else load_schema(lss_version=lss_version)
    validator = jsonschema.Draft202012Validator(schema_data)
    errors = sorted(validator.iter_errors(spec), key=lambda e: list(e.absolute_path))
    messages: list[str] = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        messages.append(f"{path}: {err.message}")
    return messages


def validate_yaml_file(path: Path, schema: dict | None = None, *, lss_version: str = "1.0") -> list[str]:
    with path.open(encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    if not isinstance(spec, dict):
        return [f"Root element must be a mapping: {path}"]
    version = "1.1" if spec.get("composition") else lss_version
    meta = spec.get("metadata") or {}
    if meta.get("schema_version") == "1.1":
        version = "1.1"
    return validate_spec(spec, schema=schema, lss_version=version)
