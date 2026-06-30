"""Combine multiple loops into one spec — flatten for token-efficient single-file output."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Literal

import yaml

from loopforge.compact import compact_spec, dump_compact_yaml, estimate_tokens, apply_token_budget
from loopforge.library import load_library_spec
from loopforge.mix import (
    mix_spec,
    normalize_pattern,
    resolve_mix_inputs,
    save_mixed_spec,
)
from loopforge.validate import validate_spec

ComposeMode = Literal["sequential", "parallel", "nested"]


def _worker_list(spec: dict[str, Any]) -> list[dict[str, Any]]:
    workers = spec.get("workers")
    return list(workers) if isinstance(workers, list) else []


def _max_steps(spec: dict[str, Any]) -> int:
    opt = spec.get("optimization_strategy") or {}
    return int(opt.get("max_steps") or 0) if isinstance(opt, dict) else 0


def compose_specs(
    spec_a: dict[str, Any],
    spec_b: dict[str, Any],
    *,
    mode: Literal["sequential", "parallel"] = "sequential",
) -> dict[str, Any]:
    """Merge two LSS dicts into one flat spec (no external child refs)."""
    a, b = copy.deepcopy(spec_a), copy.deepcopy(spec_b)
    name_a = a.get("loop_name") or a.get("loop_id") or "a"
    name_b = b.get("loop_name") or b.get("loop_id") or "b"

    composed: dict[str, Any] = {
        "loop_name": f"{name_a}-{name_b}",
        "version": a.get("version") or b.get("version") or "1.0.0",
        "objective": a.get("objective") or b.get("objective") or "",
        "metadata": {
            "schema_version": "1.0",
            "composed_from": [name_a, name_b],
            "compose_mode": mode,
        },
    }

    if mode == "sequential":
        composed["workers"] = _worker_list(a) + _worker_list(b)
        steps = _max_steps(a) + _max_steps(b)
    else:
        composed["workers"] = [
            {
                "id": "parallel_group",
                "role": "Run branches in parallel",
                "branches": [_worker_list(a), _worker_list(b)],
            }
        ]
        steps = max(_max_steps(a), _max_steps(b))

    eval_a = a.get("evaluators") or []
    eval_b = b.get("evaluators") or []
    composed["evaluators"] = list(eval_a) + list(eval_b) if isinstance(eval_a, list) else list(eval_b)

    composed["optimization_strategy"] = {
        **(a.get("optimization_strategy") or {}),
        "max_steps": steps or 8,
    }
    composed["termination_conditions"] = b.get("termination_conditions") or a.get("termination_conditions")
    composed["metrics"] = list(a.get("metrics") or []) + list(b.get("metrics") or [])
    composed["feedback_channels"] = list(a.get("feedback_channels") or []) + list(b.get("feedback_channels") or [])
    composed["safety_constraints"] = list(a.get("safety_constraints") or []) + list(b.get("safety_constraints") or [])

    cost_a = a.get("cost_limits") or {}
    cost_b = b.get("cost_limits") or {}
    if isinstance(cost_a, dict) or isinstance(cost_b, dict):
        merged_cost = {**(cost_a if isinstance(cost_a, dict) else {}), **(cost_b if isinstance(cost_b, dict) else {})}
        merged_cost["per_iteration_usd"] = float(cost_a.get("per_iteration_usd") or 0) + float(cost_b.get("per_iteration_usd") or 0)
        merged_cost["cumulative_usd"] = float(cost_a.get("cumulative_usd") or 0) + float(cost_b.get("cumulative_usd") or 0)
        merged_cost.setdefault("on_exceed", {"action": "halt"})
        composed["cost_limits"] = merged_cost

    composed["memory"] = a.get("memory") or b.get("memory") or {"type": "ephemeral"}
    composed["inputs"] = a.get("inputs") or b.get("inputs") or {"schema": {"task": {"type": "string", "required": True}}}
    return composed


def compose_specs_many(
    specs: list[dict[str, Any]],
    *,
    mode: Literal["sequential", "parallel"] = "sequential",
) -> dict[str, Any]:
    """Fold N specs into one flat LSS document."""
    if not specs:
        raise ValueError("compose_specs_many requires at least one spec")
    if len(specs) == 1:
        return copy.deepcopy(specs[0])

    if mode == "sequential":
        acc = copy.deepcopy(specs[0])
        for spec in specs[1:]:
            acc = compose_specs(acc, spec, mode="sequential")
        return acc

    layer = [copy.deepcopy(s) for s in specs]
    while len(layer) > 1:
        nxt: list[dict[str, Any]] = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                nxt.append(compose_specs(layer[i], layer[i + 1], mode="parallel"))
            else:
                nxt.append(layer[i])
        layer = nxt
    return layer[0]


class LoopChain:
    """Fluent builder: chain library forks, patterns, or specs with one `.build()`."""

    def __init__(self, loop_name: str, objective: str, *, mode: ComposeMode = "sequential") -> None:
        self.loop_name = loop_name
        self.objective = objective
        self.mode = mode
        self._patterns: list[str] = []
        self._forks: list[str | None] = []
        self._specs: list[dict[str, Any]] = []

    def then_pattern(self, pattern: str) -> LoopChain:
        self._patterns.append(normalize_pattern(pattern))
        self._forks.append(None)
        return self

    def then_fork(self, fork: str) -> LoopChain:
        self._patterns.append("")
        self._forks.append(fork)
        return self

    def then_spec(self, spec: dict[str, Any]) -> LoopChain:
        self._specs.append(spec)
        return self

    def with_mode(self, mode: ComposeMode) -> LoopChain:
        self.mode = mode
        return self

    def build(
        self,
        *,
        flatten: bool = True,
        compact: bool = True,
        validate: bool = True,
        max_tokens: int | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if self._specs:
            specs = list(self._specs)
            meta = {"method": "chain", "mode": self.mode, "child_count": len(specs), "flatten": flatten}
            if flatten:
                out = compose_specs_many(specs, mode="sequential" if self.mode == "nested" else self.mode)
                out["loop_name"] = self.loop_name
                out["objective"] = self.objective
            else:
                out, meta = mix_spec(
                    loop_name=self.loop_name,
                    objective=self.objective,
                    patterns=self._patterns or None,
                    forks=[f for f in self._forks if f] or None,
                    mode=self.mode,
                    flatten=False,
                )
            if compact:
                out = compact_spec(out)
            out, meta = _finalize_combined(out, meta, validate=validate, max_tokens=max_tokens)
            return out, meta

        patterns = [p for p in self._patterns if p] or None
        forks = [f for f in self._forks if f] or None
        out, meta = combine_loops(
            self.loop_name,
            self.objective,
            patterns=patterns,
            forks=forks,
            mode=self.mode,
            flatten=flatten,
            compact=compact,
            validate=validate,
            max_tokens=max_tokens,
        )
        meta["method"] = "chain"
        return out, meta


def _finalize_combined(
    spec: dict[str, Any],
    meta: dict[str, Any],
    *,
    validate: bool,
    max_tokens: int | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if max_tokens:
        spec, budget_meta = apply_token_budget(spec, max_tokens)
        meta["token_budget"] = budget_meta
    if validate:
        ver = "1.1" if spec.get("composition") else "1.0"
        errors = validate_spec(spec, lss_version=ver)
        if errors and not spec.get("composition"):
            raise ValueError(errors[0])
    meta["estimated_tokens"] = estimate_tokens(spec)
    return spec, meta


def combine_loops(
    loop_name: str,
    objective: str,
    *,
    recipe_id: str | None = None,
    patterns: list[str] | None = None,
    forks: list[str] | None = None,
    library_names: list[str] | None = None,
    spec_paths: list[Path | str] | None = None,
    mode: ComposeMode | None = None,
    flatten: bool = True,
    compact: bool = True,
    validate: bool = True,
    max_tokens: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Combine loops from recipes, patterns, forks, library names, or YAML paths."""
    child_specs: list[dict[str, Any]] = []

    if library_names:
        for name in library_names:
            child_specs.append(load_library_spec(name))

    if spec_paths:
        for raw in spec_paths:
            path = Path(raw)
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
            if isinstance(data, dict):
                child_specs.append(data)

    if child_specs and not (recipe_id or patterns or forks):
        meta: dict[str, Any] = {
            "method": "combine",
            "mode": mode or "sequential",
            "child_count": len(child_specs),
            "flatten": flatten,
            "sources": library_names or [str(p) for p in (spec_paths or [])],
        }
        if flatten:
            spec = compose_specs_many(child_specs, mode=meta["mode"] if meta["mode"] != "nested" else "sequential")
            spec["loop_name"] = loop_name
            spec["objective"] = objective
        else:
            from loopforge.composition import build_composition_spec
            import tempfile

            with tempfile.TemporaryDirectory(prefix="loopforge-combine-") as tmp:
                work = Path(tmp)
                refs: list[tuple[str, Path, str]] = []
                for i, s in enumerate(child_specs):
                    cid = s.get("loop_name") or f"child-{i + 1}"
                    path = work / f"{cid}.yaml"
                    path.write_text(yaml.safe_dump(s, sort_keys=False), encoding="utf-8")
                    refs.append((cid, path, ""))
                out_stub = work / f"{loop_name}.yaml"
                spec = build_composition_spec(loop_name, objective, meta["mode"], refs, output_path=out_stub)

        if compact:
            spec = compact_spec(spec, aggressive=True)
        return _finalize_combined(spec, meta, validate=validate, max_tokens=max_tokens)

    spec, meta = mix_spec(
        loop_name=loop_name,
        objective=objective,
        recipe_id=recipe_id,
        patterns=patterns,
        forks=forks,
        mode=mode,
        flatten=flatten,
    )
    meta["method"] = "combine"
    meta["flatten"] = flatten
    if compact:
        spec = compact_spec(spec)
    return _finalize_combined(spec, meta, validate=validate, max_tokens=max_tokens)


def save_combined_spec(
    spec: dict[str, Any],
    path: Path,
    *,
    compact: bool = True,
    validate: bool = True,
) -> dict[str, Any]:
    """Write combined spec; returns token stats."""
    save_mixed_spec(spec, path, validate=validate, compact=compact)
    text = path.read_text(encoding="utf-8")
    return {"path": str(path), "bytes": len(text), "estimated_tokens": estimate_tokens(spec)}
