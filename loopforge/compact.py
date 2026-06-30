"""Compact LSS specs and reports for token-efficient agent workflows."""

from __future__ import annotations

import json
import re
from typing import Any

import yaml

_STRIP_KEYS = frozenset({"metadata"})
_STRIP_WHEN_COMPACT = frozenset({"examples", "extensions", "x_loopforge"})
_SHORTEN_ROLES = True
_MAX_ROLE_LEN = 72


def estimate_tokens(spec: dict[str, Any] | str, *, chars_per_token: float = 4.0) -> int:
    """Rough token estimate for YAML/JSON spec (chars / 4 by default)."""
    if isinstance(spec, dict):
        text = dump_compact_yaml(spec)
    else:
        text = spec
    return max(1, int(len(text) / chars_per_token))


def compact_spec(spec: dict[str, Any], *, aggressive: bool = False) -> dict[str, Any]:
    """Drop verbose optional fields; keep scoring-relevant structure."""
    saved_meta = spec.get("metadata") if isinstance(spec.get("metadata"), dict) else {}
    out = _compact_value(spec, aggressive=aggressive)
    if isinstance(out, dict):
        meta = saved_meta or out.pop("metadata", None)
        if isinstance(meta, dict):
            if meta.get("forked_from"):
                out["forked_from"] = meta["forked_from"]
            if meta.get("composed_from"):
                out["composed_from"] = meta["composed_from"]
            if meta.get("compose_mode"):
                out["compose_mode"] = meta["compose_mode"]
            if meta.get("compose_certificates"):
                out["compose_certificates"] = meta["compose_certificates"]
            if meta.get("compose_valid") is not None:
                out["compose_valid"] = meta["compose_valid"]
            if meta.get("proof_source"):
                out["proof_source"] = meta["proof_source"]
        if aggressive and out.get("composition"):
            comp = out["composition"]
            if isinstance(comp, dict) and comp.get("children"):
                out["composition"] = {
                    "type": comp.get("type"),
                    "children": [
                        {k: v for k, v in ch.items() if k in ("id", "ref", "role")}
                        for ch in comp["children"]
                        if isinstance(ch, dict)
                    ],
                }
    return out


def _trim_role(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= _MAX_ROLE_LEN:
        return text
    return text[: _MAX_ROLE_LEN - 1].rstrip() + "…"


def _compact_value(value: Any, *, aggressive: bool = False, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {
            k: _compact_value(v, aggressive=aggressive, key=k)
            for k, v in value.items()
            if v is not None and v != [] and v != {} and k not in (_STRIP_KEYS | (_STRIP_WHEN_COMPACT if aggressive else frozenset()))
        }
    if isinstance(value, list):
        return [_compact_value(v, aggressive=aggressive) for v in value]
    if isinstance(value, str) and aggressive and key == "role":
        return _trim_role(value)
    return value


def dump_compact_yaml(spec: dict[str, Any], *, aggressive: bool = False) -> str:
    return yaml.safe_dump(
        compact_spec(spec, aggressive=aggressive),
        sort_keys=False,
        default_flow_style=True,
        width=120,
        allow_unicode=True,
    )


def token_compare(spec_a: dict[str, Any], spec_b: dict[str, Any]) -> dict[str, Any]:
    """Compare estimated tokens before/after compaction or flatten."""
    return {
        "before": estimate_tokens(spec_a),
        "after": estimate_tokens(spec_b),
        "saved": estimate_tokens(spec_a) - estimate_tokens(spec_b),
        "ratio": round(estimate_tokens(spec_b) / max(1, estimate_tokens(spec_a)), 3),
    }


def compact_pipeline_report(report: dict[str, Any]) -> dict[str, Any]:
    """Minimal JSON for LLM/agent consumption."""
    out: dict[str, Any] = {
        "ok": report.get("valid", True),
        "pattern": report.get("pattern"),
        "method": report.get("method"),
        "spec": report.get("spec_path"),
        "lss": report.get("lss_version"),
    }
    if agent := report.get("agent"):
        out["agent"] = agent
    if struct := report.get("structural_les"):
        les = struct.get("les") or struct.get("composite")
        if les is not None:
            out["les"] = round(float(les), 1)
    if obs := report.get("observed_les"):
        oles = obs.get("observed_les")
        if oles is not None:
            out["observed_les"] = round(float(oles), 1)
    if bench := report.get("bench_task"):
        out["bench_task"] = bench
        out["bench_cmd"] = report.get("bench_cmd")
    if suite := report.get("suite") or report.get("bench_suite"):
        out["suite"] = suite
        if report.get("bench_cmd"):
            out["bench_cmd"] = report.get("bench_cmd")
    if export := report.get("export"):
        out["export"] = export.get("dir") or export.get("target")
    if tokens := report.get("estimated_tokens"):
        out["tokens"] = tokens
    if saved := report.get("tokens_saved"):
        out["tokens_saved"] = saved
    return out


def dumps_compact_json(data: dict[str, Any]) -> str:
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


_MINJSON_WORKER_KEYS = frozenset({"id", "role", "inputs", "outputs", "model"})
_MINJSON_EVAL_KEYS = frozenset({"id", "type", "runs_after", "rubric", "implementation", "pass_threshold"})


def to_minjson(spec: dict[str, Any]) -> dict[str, Any]:
    """JSON subset for agent system prompts — workers, evaluators, termination only."""
    objective = str(spec.get("objective") or "")
    out: dict[str, Any] = {
        "loop_name": spec.get("loop_name"),
        "objective": objective.split("\n")[0].strip()[:280],
        "workers": [
            {k: v for k, v in w.items() if k in _MINJSON_WORKER_KEYS}
            for w in (spec.get("workers") or [])
            if isinstance(w, dict)
        ],
        "evaluators": [
            {k: v for k, v in e.items() if k in _MINJSON_EVAL_KEYS}
            for e in (spec.get("evaluators") or [])
            if isinstance(e, dict)
        ],
        "termination_conditions": spec.get("termination_conditions"),
    }
    opt = spec.get("optimization_strategy")
    if isinstance(opt, dict):
        out["optimization_strategy"] = {
            k: opt[k] for k in ("type", "max_steps") if k in opt
        }
    if safety := spec.get("safety_constraints"):
        out["safety_constraints"] = [
            {k: c[k] for k in ("id", "type", "action", "severity") if k in c}
            for c in safety
            if isinstance(c, dict)
        ][:4]
    return out


def dumps_minjson(spec: dict[str, Any]) -> str:
    return json.dumps(to_minjson(spec), separators=(",", ":"), ensure_ascii=False)


def apply_token_budget(spec: dict[str, Any], max_tokens: int, *, chars_per_token: float = 4.0) -> tuple[dict[str, Any], dict[str, Any]]:
    """Progressively compact until estimate_tokens <= max_tokens."""
    from copy import deepcopy

    if max_tokens <= 0:
        return spec, {"budget": max_tokens, "applied": False}

    working = deepcopy(spec)
    meta: dict[str, Any] = {
        "budget": max_tokens,
        "before": estimate_tokens(working, chars_per_token=chars_per_token),
        "steps": [],
    }

    def fits(s: dict[str, Any]) -> bool:
        return estimate_tokens(s, chars_per_token=chars_per_token) <= max_tokens

    if fits(working):
        meta["after"] = meta["before"]
        meta["applied"] = False
        return working, meta

    working = compact_spec(working, aggressive=True)
    meta["steps"].append("aggressive_compact")
    if fits(working):
        meta["after"] = estimate_tokens(working, chars_per_token=chars_per_token)
        meta["applied"] = True
        return working, meta

    evals = working.get("evaluators") or []
    if isinstance(evals, list) and len(evals) > 1:
        primary = next((e for e in evals if isinstance(e, dict) and e.get("type") in ("test_suite", "deterministic")), evals[0])
        working["evaluators"] = [primary] if isinstance(primary, dict) else evals[:1]
        meta["steps"].append("drop_secondary_evaluators")

    for w in working.get("workers") or []:
        if isinstance(w, dict) and isinstance(w.get("role"), str):
            w["role"] = _trim_role(w["role"])

    meta["steps"].append("trim_roles")
    working = compact_spec(working, aggressive=True)

    workers = working.get("workers") or []
    while not fits(working) and isinstance(workers, list) and len(workers) > 1:
        workers = workers[:-1]
        working["workers"] = workers
        meta["steps"].append("drop_workers")
        working = compact_spec(working, aggressive=True)

    evals = working.get("evaluators") or []
    if isinstance(evals, list):
        for ev in evals:
            if isinstance(ev, dict) and isinstance(ev.get("rubric"), dict):
                dims = ev["rubric"].get("dimensions") or []
                if isinstance(dims, list) and len(dims) > 1:
                    ev["rubric"]["dimensions"] = dims[:1]
                    meta["steps"].append("trim_rubric")

    for w in working.get("workers") or []:
        if isinstance(w, dict) and isinstance(w.get("model"), dict):
            w["model"] = {"name": w["model"].get("name", "gpt-4.1-mini")}
        if isinstance(w, dict):
            w.pop("timeout_seconds", None)
            w.pop("retries", None)
            w.pop("cost_budget_usd", None)

    working = compact_spec(working, aggressive=True)

    if not fits(working):
        obj = str(working.get("objective") or "")
        if len(obj) > 120:
            working["objective"] = obj.split("\n")[0][:120].rstrip() + "…"
            meta["steps"].append("truncate_objective")

    meta["after"] = estimate_tokens(working, chars_per_token=chars_per_token)
    meta["applied"] = meta["after"] <= max_tokens
    return working, meta
