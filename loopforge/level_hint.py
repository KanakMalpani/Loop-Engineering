"""LE-OP-11 taxonomy level hints for scaffolded specs."""

from __future__ import annotations

from typing import Any

NAME_TO_PATTERN: dict[str, str] = {
    "research-agent": "research-loop",
    "coding-agent": "reflection-loop",
    "autonomous-debugger": "verification-loop",
    "interview-coach": "human-in-the-loop",
    "writing-assistant": "reflection-loop",
    "business-strategy-agent": "multi-agent-coordination",
    "startup-validator": "planning-loop",
    "learning-coach": "reflection-loop",
    "scientific-discovery-agent": "exploration-loop",
}


def infer_pattern(spec: dict, source_name: str | None = None) -> str:
    meta = spec.get("metadata") or {}
    patterns = meta.get("patterns")
    if patterns:
        return str(patterns[0] if isinstance(patterns, list) else patterns)
    name = source_name or spec.get("loop_name") or ""
    stem = str(name).removesuffix(".yaml")
    if stem in NAME_TO_PATTERN:
        return NAME_TO_PATTERN[stem]
    workers = len(spec.get("workers") or [])
    if spec.get("composition"):
        return "multi-agent-coordination"
    if workers >= 3:
        return "multi-agent-coordination"
    if workers == 2:
        return "reflection-loop"
    return "reflection-loop"


def worker_count(spec: dict) -> int:
    return max(len(spec.get("workers") or []), 1)


def heuristic_level(spec: dict, source_name: str | None = None) -> str:
    workers = worker_count(spec)
    if spec.get("composition"):
        ctype = (spec.get("composition") or {}).get("type")
        if ctype == "parallel":
            return "4"
        if ctype == "nested":
            return "4"
        return "3"
    if workers >= 4:
        return "3"
    if workers >= 2:
        return "2"
    return "2"


def suggest_level(spec: dict, source_name: str | None = None) -> dict[str, Any]:
    pattern = infer_pattern(spec, source_name)
    workers = worker_count(spec)
    iter_len = 3
    term = spec.get("termination_conditions") or {}
    for block in term.get("failure") or []:
        if block.get("type") == "max_iterations" and block.get("value"):
            iter_len = int(block["value"])
            break

    level = heuristic_level(spec, source_name)
    confidence = "heuristic"
    try:
        import sys
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from tools.level_recommender import LevelRecommender, load_records

        records = load_records()
        if records:
            model = LevelRecommender()
            model.fit(records[: int(len(records) * 0.8)])
            level = model.predict(pattern, iter_len, workers)
            confidence = "loopnet-v0.2"
    except Exception:
        pass

    return {
        "taxonomy_level": level,
        "pattern": pattern,
        "workers": workers,
        "confidence": confidence,
    }


def apply_level_hint(spec: dict, source_name: str | None = None) -> dict[str, Any]:
    hint = suggest_level(spec, source_name)
    spec.setdefault("x_loopforge", {})["level_hint"] = hint
    meta = spec.setdefault("metadata", {})
    if isinstance(meta, dict) and "taxonomy_level" not in meta:
        meta["taxonomy_level"] = int(hint["taxonomy_level"])
    return hint
