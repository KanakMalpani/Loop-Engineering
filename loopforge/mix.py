"""N-way loop mixing — recipes, patterns, and forks into one LSS spec."""

from __future__ import annotations

import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from loopforge.builder import LoopBuilder
from loopforge.composition import build_composition_spec, save_composition
from loopforge.library import fork_spec
from loopforge.patterns import Pattern

COMPOSITION_MODES = frozenset({"sequential", "parallel", "nested"})

PATTERN_ALIASES: dict[str, str] = {
    "rag": "research",
    "agentic-rag": "research",
    "bootstrap": "reflection",
    "safety": "verification",
    "safety-constrained": "verification",
    "debate": "crew",
    "tot": "crew",
    "tree-search": "crew",
    "vote": "crew",
    "self-consistency": "crew",
    "mem": "reflection",
    "memory": "reflection",
    "sim": "plan",
    "simulation": "plan",
    "simulation-loop": "plan",
    "nest": "verification",
    "nested": "verification",
    "nested-composition": "verification",
    "opt": "verification",
    "bootstrap-optimize": "verification",
    "hitl": "research",
    "human-gate": "research",
}

FORK_BY_PATTERN: dict[str, str | None] = {
    "simple": None,
    "reflection": "coding-agent",
    "verification": "autonomous-debugger",
    "research": "research-agent",
    "react": None,
    "crew": "coding-agent",
    "plan": "coding-agent",
}


def _recipes_path() -> Path:
    packaged = Path(__file__).resolve().parent / "recipes.yaml"
    if packaged.is_file():
        return packaged
    raise FileNotFoundError("recipes.yaml not found in loopforge package")


def _user_recipe_paths() -> list[Path]:
    paths: list[Path] = []
    home = Path.home() / ".loop" / "recipes.yaml"
    if home.is_file():
        paths.append(home)
    local = Path.cwd() / "recipes.local.yaml"
    if local.is_file():
        paths.append(local)
    return paths


def _merge_recipe_indexes(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    by_id = {r["id"]: r for r in (base.get("recipes") or []) if isinstance(r, dict) and r.get("id")}
    for recipe in overlay.get("recipes") or []:
        if not isinstance(recipe, dict) or not recipe.get("id"):
            continue
        rid = recipe["id"]
        by_id[rid] = {**by_id.get(rid, {}), **recipe}
    return {**base, "recipes": list(by_id.values())}


def load_recipes_index() -> dict[str, Any]:
    with _recipes_path().open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    index = data if isinstance(data, dict) else {}
    for path in _user_recipe_paths():
        with path.open(encoding="utf-8") as fh:
            overlay = yaml.safe_load(fh)
        if isinstance(overlay, dict):
            index = _merge_recipe_indexes(index, overlay)
    return index


def list_recipes() -> list[dict[str, Any]]:
    return list(load_recipes_index().get("recipes") or [])


def load_recipe(recipe_id: str) -> dict[str, Any]:
    for recipe in list_recipes():
        if recipe.get("id") == recipe_id:
            return recipe
    available = ", ".join(r["id"] for r in list_recipes())
    raise KeyError(f"Unknown recipe {recipe_id!r}. Choose: {available}")


def normalize_pattern(name: str) -> str:
    key = name.strip().lower().replace("_", "-")
    return PATTERN_ALIASES.get(key, key)


def _resolve_one(
    *,
    pattern: str | None,
    fork: str | None,
    child_id: str,
    objective: str,
) -> tuple[str, dict[str, Any]]:
    pat = normalize_pattern(pattern or "reflection")
    if fork:
        spec = fork_spec(fork, child_id)
        spec["objective"] = objective
        return child_id, spec

    default_fork = FORK_BY_PATTERN.get(pat)
    if default_fork:
        try:
            spec = fork_spec(default_fork, child_id)
            spec["objective"] = objective
            return child_id, spec
        except FileNotFoundError:
            pass

    ptype = Pattern.from_str(pat)
    spec = LoopBuilder(child_id, objective).from_pattern(ptype).build()
    return child_id, spec


def resolve_mix_inputs(
    *,
    recipe_id: str | None = None,
    patterns: list[str] | None = None,
    forks: list[str] | None = None,
    mode: str | None = None,
    objective: str = "Execute the composed loop pipeline.",
) -> tuple[str, list[tuple[str, dict[str, Any]]], str | None]:
    """Return (mode, child_specs as id+dict, default_suite)."""
    if recipe_id:
        recipe = load_recipe(recipe_id)
        mode = mode or str(recipe.get("mode") or "sequential")
        pat_list = list(recipe.get("patterns") or [])
        fork_list = list(recipe.get("forks") or [])
        default_suite = recipe.get("default_suite")
        children: list[tuple[str, dict[str, Any]]] = []
        for i, pat in enumerate(pat_list):
            fork = fork_list[i] if i < len(fork_list) and fork_list[i] not in (None, "null") else None
            cid = f"stage-{i + 1}" if mode == "sequential" else f"branch-{i + 1}"
            if mode == "nested" and i == 0:
                cid = "outer"
            elif mode == "nested" and i > 0:
                cid = "inner"
            children.append(_resolve_one(pattern=pat, fork=fork, child_id=cid, objective=objective))
        return mode, children, default_suite

    if not patterns and not forks:
        raise ValueError("Provide recipe id, --patterns, or --forks")

    mode = mode or "sequential"
    children = []
    if forks:
        for i, fork in enumerate(forks):
            cid = fork.replace("-", "_")
            children.append(_resolve_one(pattern=None, fork=fork, child_id=cid, objective=objective))
    else:
        for i, pat in enumerate(patterns or []):
            cid = f"stage-{i + 1}"
            children.append(_resolve_one(pattern=pat, fork=None, child_id=cid, objective=objective))
    return mode, children, None


def _write_children(
    children: list[tuple[str, dict[str, Any]]],
    work_dir: Path,
) -> list[tuple[str, Path, str]]:
    refs: list[tuple[str, Path, str]] = []
    for child_id, spec in children:
        path = work_dir / f"{child_id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(spec, fh, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)
        refs.append((child_id, path, ""))
    return refs


def mix_spec(
    *,
    loop_name: str,
    objective: str,
    recipe_id: str | None = None,
    patterns: list[str] | None = None,
    forks: list[str] | None = None,
    mode: str | None = None,
    flatten: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build mixed LSS spec and metadata."""
    mix_mode, children, default_suite = resolve_mix_inputs(
        recipe_id=recipe_id,
        patterns=patterns,
        forks=forks,
        mode=mode,
        objective=objective,
    )
    if mix_mode not in COMPOSITION_MODES:
        raise ValueError(f"mode must be one of {sorted(COMPOSITION_MODES)}")

    meta: dict[str, Any] = {
        "method": "mix",
        "mode": mix_mode,
        "recipe": recipe_id,
        "patterns": [
            spec.get("metadata", {}).get("forked_from") if isinstance(spec.get("metadata"), dict) else None
            or spec.get("loop_name", child_id)
            for child_id, spec in children
        ],
        "child_count": len(children),
        "default_suite": default_suite,
    }

    if flatten and len(children) >= 2:
        specs = [deepcopy(s) for _, s in children]
        from loopforge.combine import compose_specs_many

        composed = compose_specs_many(
            specs,
            mode="sequential" if mix_mode == "nested" else mix_mode,  # type: ignore[arg-type]
        )
        composed["loop_name"] = loop_name
        composed["objective"] = objective
        meta["flatten"] = True
        meta["composition_certificate"] = composed.get("metadata", {}).get("composed_from")
        return composed, meta

    with tempfile.TemporaryDirectory(prefix="loopforge-mix-") as tmp:
        work = Path(tmp)
        child_refs = _write_children(children, work)
        out_stub = work / f"{loop_name}.yaml"
        spec = build_composition_spec(
            loop_name,
            objective,
            mix_mode,
            child_refs,
            output_path=out_stub,
        )
        cert = spec.get("composition") or {}
        meta["composition_certificate"] = cert
        meta["theory_ref"] = (cert.get("validity") or {}).get("theory_ref")
        return spec, meta


def save_mixed_spec(
    spec: dict[str, Any],
    path: Path,
    *,
    validate: bool = True,
    compact: bool = False,
) -> None:
    if spec.get("composition"):
        save_composition(spec, path, validate=validate)
        if compact:
            from loopforge.compact import compact_spec, dump_compact_yaml

            compacted = compact_spec(yaml.safe_load(path.read_text(encoding="utf-8")))
            path.write_text(dump_compact_yaml(compacted), encoding="utf-8")
        return

    import yaml as _yaml

    from loopforge.validate import validate_spec

    if validate:
        errors = validate_spec(spec, lss_version="1.0")
        if errors:
            raise ValueError(errors[0])
    payload = spec
    if compact:
        from loopforge.compact import compact_spec

        payload = compact_spec(spec, aggressive=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        _yaml.safe_dump(payload, fh, sort_keys=False, default_flow_style=compact, allow_unicode=True, width=120)
