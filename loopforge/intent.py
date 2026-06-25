"""LE-OP-15 v0.5: classify natural-language intent → LoopForge pattern or composition."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from loopforge.builder import LoopBuilder
from loopforge.composition import build_composition_spec
from loopforge.library import fork_spec
from loopforge.patterns import Pattern

COMPOSE_MODES = frozenset({"sequential", "parallel", "nested"})

COMPOSE_RULES: list[tuple[str, str]] = [
    (
        r"\b(parallel|concurr(?:ent|ently)?|simultaneous(?:ly)?|"
        r"(?:run|fan).{0,16}(?:branch(?:es)?|swarm)|"
        r"(?:branch(?:es)?|swarm).{0,16}(?:parallel|concurr|merge))\b",
        "parallel",
    ),
    (
        r"\b(nested|sub.?loop|"
        r"(?:inner|outer).{0,12}(?:loop|debug|agent)|"
        r"wrap(?:ped)?\s+(?:inside|within))\b",
        "nested",
    ),
    (
        r"\b(sequential\s+pipeline|pipeline\s+of\s+stages?|"
        r"(?:stage|step)s?\s+(?:in\s+)?(?:sequence|series)|"
        r"chain\s+(?:from|through|of)|"
        r"followed\s+by\s+(?:a\s+)?(?:writing|research|polish|draft))\b",
        "sequential",
    ),
]

INTENT_RULES: list[tuple[str, Pattern, str | None]] = [
    (r"\b(research|literature|sources?|cite|citation|brief|synthesize|hypothesis|papers?)\b", Pattern.RESEARCH, "research-agent"),
    (r"\b(test|verify|debug|fix|failing|ci|lint|suite|patch|regression|flaky|validate)\b", Pattern.VERIFICATION, "autonomous-debugger"),
    (r"\b(reflect|critique|review|feedback|revise|draft|peer|iterate|clarity)\b", Pattern.REFLECTION, None),
    (r"\b(code|implement|feature|diff|caching|security)\b", Pattern.VERIFICATION, "coding-agent"),
    (r"\b(summarize|summary|themes?|simple|single|one-shot|meeting|changelog|extract|interview)\b", Pattern.SIMPLE, None),
]

FORK_DEFAULTS = {
    Pattern.RESEARCH: "research-agent",
    Pattern.VERIFICATION: "autonomous-debugger",
    Pattern.REFLECTION: "coding-agent",
    Pattern.SIMPLE: None,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def classify_compose_mode(text: str) -> str | None:
    lower = text.lower()
    for pattern, mode in COMPOSE_RULES:
        if re.search(pattern, lower):
            return mode
    return None


def classify_pattern(text: str) -> tuple[Pattern, str | None]:
    lower = text.lower()
    for pattern, ptype, fork in INTENT_RULES:
        if re.search(pattern, lower):
            return ptype, fork
    return Pattern.REFLECTION, None


def classify_intent(text: str) -> tuple[str, str | None]:
    """Return (label, fork_source). label is pattern.value or a compose mode."""
    compose = classify_compose_mode(text)
    if compose:
        return compose, None
    pattern, fork = classify_pattern(text)
    return pattern.value, fork


def slug_from_intent(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())[:4]
    return "-".join(words) or "intent-loop"


def _child_specs_for_mode(mode: str) -> list[tuple[str, Path, str]]:
    lib = repo_root() / "loop-library"
    if mode == "parallel":
        return [
            ("research", lib / "research-agent.yaml", "research"),
            ("coding", lib / "coding-agent.yaml", "code"),
        ]
    if mode == "sequential":
        return [
            ("research", lib / "research-agent.yaml", ""),
            ("writing", lib / "writing-assistant.yaml", ""),
        ]
    return [
        ("outer", lib / "coding-agent.yaml", ""),
        ("inner", lib / "autonomous-debugger.yaml", ""),
    ]


def compile_intent(
    intent: str,
    *,
    loop_name: str | None = None,
    use_fork: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (spec, meta) from natural language intent."""
    label, fork_source = classify_intent(intent)
    name = loop_name or slug_from_intent(intent)

    if label in COMPOSE_MODES:
        out_stub = repo_root() / "loop-library" / "compositions" / f"{name}.yaml"
        child_specs = _child_specs_for_mode(label)
        spec = build_composition_spec(
            name,
            intent,
            label,
            child_specs,
            output_path=out_stub,
        )
        meta = {"pattern": label, "method": "compose", "fork_source": None}
        return spec, meta

    pattern = Pattern(label)
    if use_fork and fork_source:
        try:
            spec = fork_spec(fork_source, name)
            spec["objective"] = f"{intent.rstrip()}\nAchieve primary_quality >= 0.80 within cost_limits with zero safety violations."
            meta = {"pattern": pattern.value, "method": "fork", "fork_source": fork_source}
            return spec, meta
        except FileNotFoundError:
            pass

    spec = (
        LoopBuilder(name, intent)
        .from_pattern(pattern)
        .build()
    )
    meta = {"pattern": pattern.value, "method": "scaffold", "fork_source": None}
    return spec, meta
