"""Deterministic evaluator implementations."""

from __future__ import annotations

import re
from typing import Any


def run_deterministic(implementation: str, output: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run a deterministic evaluator by implementation reference."""
    ctx = context or {}
    if implementation == "evaluators.word_count_max":
        max_words = int(ctx.get("max_words", 100))
        count = len(output.split())
        passed = count <= max_words
        return {
            "passed": passed,
            "score": min(1.0, max_words / max(count, 1)),
            "word_count": count,
            "failure_codes": [] if passed else ["fail.false_fail"],
        }
    if implementation == "evaluators.test_pass_rate":
        from loopgym.evaluators.sandbox_tests import test_pass_rate as _real_tpr

        fixture = ctx.get("fixture")
        if fixture is None:
            # No real fixture -> no real outcome. Never fall back to an unset mock rate.
            return {"passed": False, "score": 0.0, "test_pass_rate": 0.0,
                    "failure_codes": ["fail.no_fixture"]}
        res = _real_tpr(fixture, output, timeout=int(ctx.get("timeout", 30)))
        rate = res["test_pass_rate"]
        passed = rate >= float(ctx.get("threshold", 1.0))
        return {
            **res,
            "passed": passed,
        }
    if implementation == "evaluators.citation_count_min":
        citations = len(re.findall(r"\[[\d]+\]|\(\d{4}\)", output))
        min_citations = int(ctx.get("min_citations", 3))
        passed = citations >= min_citations
        return {
            "passed": passed,
            "score": min(1.0, citations / min_citations),
            "citation_count": citations,
            "failure_codes": [] if passed else ["fail.false_fail"],
        }
    return {"passed": True, "score": 1.0, "failure_codes": []}
