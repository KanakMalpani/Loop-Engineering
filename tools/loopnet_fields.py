"""Shared LoopNet v0.2 field helpers and pattern→level oracle for LE-OP-11."""

from __future__ import annotations

from collections import Counter

# Expert oracle: primary pattern → taxonomy level (from patterns/ + taxonomy docs)
PATTERN_LEVEL: dict[str, str] = {
    "reflection-loop": "2",
    "critique-loop": "2",
    "verification-loop": "2",
    "planning-loop": "2",
    "research-loop": "2",
    "memory-augmented-loop": "2",
    "human-in-the-loop": "3",
    "multi-agent-coordination": "3",
    "debate-loop": "3",
    "exploration-loop": "4",
    "recursive-improvement-loop": "4",
    "optimization-loop": "4",
    "simulation-loop": "4",
    "safety-constrained-loop": "4",
}


def primary_pattern(row: dict) -> str:
    patterns = row.get("patterns") or row.get("loop_spec.extensions.patterns") or []
    if patterns:
        return str(patterns[0])
    return "unknown"


def iteration_count(row: dict) -> int:
    if row.get("metadata.iteration_count") is not None:
        return int(row["metadata.iteration_count"])
    trajectory = row.get("trajectory")
    if isinstance(trajectory, list):
        return len(trajectory)
    return 0


def oracle_level(row: dict) -> str:
    return PATTERN_LEVEL.get(primary_pattern(row), "2")


def iter_bucket(n: int) -> str:
    if n <= 2:
        return "short"
    if n <= 5:
        return "medium"
    return "long"


def field_histogram(rows: list[dict], field_fn) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts[str(field_fn(row))] += 1
    return counts
