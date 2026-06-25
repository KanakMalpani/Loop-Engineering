"""LE-OP-15 v0.3: classify natural-language intent → LoopForge pattern."""

from __future__ import annotations

import re
from typing import Any

from loopforge.builder import LoopBuilder
from loopforge.library import fork_spec
from loopforge.patterns import Pattern

INTENT_RULES: list[tuple[str, Pattern, str | None]] = [
    (r"\b(research|literature|sources?|cite|citation|brief|synthesize)\b", Pattern.RESEARCH, "research-agent"),
    (r"\b(test|verify|debug|fix|failing|ci|lint|suite)\b", Pattern.VERIFICATION, "autonomous-debugger"),
    (r"\b(reflect|critique|review|feedback|revise|draft)\b", Pattern.REFLECTION, None),
    (r"\b(code|implement|feature|patch|diff)\b", Pattern.VERIFICATION, "coding-agent"),
    (r"\b(summarize|summary|themes?|simple|single)\b", Pattern.SIMPLE, None),
]

FORK_DEFAULTS = {
    Pattern.RESEARCH: "research-agent",
    Pattern.VERIFICATION: "autonomous-debugger",
    Pattern.REFLECTION: "coding-agent",
    Pattern.SIMPLE: None,
}


def classify_intent(text: str) -> tuple[Pattern, str | None]:
    lower = text.lower()
    for pattern, ptype, fork in INTENT_RULES:
        if re.search(pattern, lower):
            return ptype, fork
    return Pattern.REFLECTION, None


def slug_from_intent(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())[:4]
    return "-".join(words) or "intent-loop"


def compile_intent(
    intent: str,
    *,
    loop_name: str | None = None,
    use_fork: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (spec, meta) from natural language intent."""
    pattern, fork_source = classify_intent(intent)
    name = loop_name or slug_from_intent(intent)

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
