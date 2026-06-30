"""Tests for loopforge.combine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loopforge.combine import LoopChain, combine_loops, compose_specs_many
from loopforge.compact import estimate_tokens, token_compare, to_minjson


def test_compose_specs_many_sequential():
    a = {"loop_name": "a", "workers": [{"id": "w1"}], "optimization_strategy": {"max_steps": 2}}
    b = {"loop_name": "b", "workers": [{"id": "w2"}], "optimization_strategy": {"max_steps": 3}}
    out = compose_specs_many([a, b], mode="sequential")
    assert len(out["workers"]) == 2
    assert out["optimization_strategy"]["max_steps"] == 5


def test_combine_library_flat():
    spec, meta = combine_loops(
        "test-combine",
        "Smoke objective for combine test",
        library_names=["research-agent", "coding-agent"],
        flatten=True,
        compact=True,
        validate=False,
    )
    assert meta["flatten"] is True
    assert len(spec.get("workers") or []) >= 2
    assert estimate_tokens(spec) > 0


def test_loop_chain():
    spec, meta = (
        LoopChain("chain", "Plan react verify")
        .then_pattern("plan")
        .then_pattern("react")
        .then_pattern("verification")
        .build(flatten=True, compact=True, validate=False)
    )
    assert meta["method"] == "chain"
    assert spec.get("loop_name") == "chain"


def test_token_budget():
    spec, meta = combine_loops(
        "budget-test",
        "Objective for token budget enforcement test",
        library_names=["research-agent", "coding-agent", "autonomous-debugger"],
        flatten=True,
        compact=True,
        validate=False,
        max_tokens=2000,
    )
    assert meta.get("token_budget")
    assert estimate_tokens(spec) <= 2000


def test_to_minjson():
    spec, _ = combine_loops(
        "minjson-test",
        "Objective for minjson export test",
        library_names=["research-agent"],
        flatten=True,
        compact=True,
        validate=False,
    )
    mj = to_minjson(spec)
    assert mj.get("loop_name")
    assert mj.get("workers")
    assert "metadata" not in mj


def test_token_compare_saves_on_compact():
    _, flat_compact = combine_loops(
        "t",
        "Objective text for token compare test run",
        library_names=["research-agent", "coding-agent"],
        flatten=True,
        compact=True,
        validate=False,
    )
    _, flat_verbose = combine_loops(
        "t",
        "Objective text for token compare test run",
        library_names=["research-agent", "coding-agent"],
        flatten=True,
        compact=False,
        validate=False,
    )
    cmp = token_compare(flat_verbose, flat_compact)
    assert cmp["after"] <= cmp["before"]
