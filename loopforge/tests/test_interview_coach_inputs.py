"""Tests for interview-coach library inputs."""

from __future__ import annotations

from pathlib import Path

import yaml

from loopforge.validate import validate_yaml_file

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "loop-library" / "interview-coach.yaml"
OPTIONAL_FIELDS = ("target_role", "interview_type", "seniority", "job_description")


def _load_spec() -> dict:
    with SPEC_PATH.open(encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    assert isinstance(spec, dict)
    return spec


def test_optional_interview_inputs():
    schema = _load_spec()["inputs"]["schema"]
    assert schema["task"]["type"] == "string"
    assert schema["task"]["required"] is True
    for field in OPTIONAL_FIELDS:
        assert field in schema
        assert schema[field]["type"] == "string"
        assert schema[field]["required"] is False


def test_every_example_has_a_task():
    examples = _load_spec()["inputs"]["examples"]
    assert examples
    for example in examples:
        assert "task" in example
        assert example["task"]


def test_interview_coach_spec_validates():
    assert validate_yaml_file(SPEC_PATH) == []
