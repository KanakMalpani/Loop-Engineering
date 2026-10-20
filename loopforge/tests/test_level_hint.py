"""Tests for loopforge.level_hint."""

from __future__ import annotations

from loopforge.level_hint import suggest_level


def test_suggest_level_heuristic_when_load_records_system_exits(monkeypatch):
    def _missing_datasets():
        raise SystemExit("Install: pip install datasets")

    monkeypatch.setattr("tools.level_recommender.load_records", _missing_datasets)
    hint = suggest_level({"workers": [{"id": "w1"}]}, source_name="coding-agent")
    assert hint["confidence"] == "heuristic"
