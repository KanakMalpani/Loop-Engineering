"""Build LSS 1.1 composition blocks."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from loopforge.validate import validate_spec


COMPOSITION_MODES = ("sequential", "parallel", "nested")


def _child_ref(spec_path: Path, child_path: Path) -> str:
    try:
        return str(child_path.relative_to(spec_path.parent)).replace("\\", "/")
    except ValueError:
        return str(child_path)


def build_composition_spec(
    loop_name: str,
    objective: str,
    mode: str,
    child_specs: list[tuple[str, Path, str]],
    *,
    output_path: Path,
    quality_threshold: float = 0.80,
) -> dict[str, Any]:
    if mode not in COMPOSITION_MODES:
        raise ValueError(f"mode must be one of {COMPOSITION_MODES}")

    children: list[dict[str, Any]] = []
    for child_id, child_path, lens in child_specs:
        role = "branch" if mode == "parallel" else ("outer" if mode == "nested" and child_id == child_specs[0][0] else "stage")
        if mode == "nested" and child_id != child_specs[0][0]:
            role = "inner"
        if mode == "sequential":
            role = "stage"
        entry: dict[str, Any] = {
            "id": child_id,
            "ref": _child_ref(output_path, child_path),
            "role": role,
        }
        if lens:
            entry["lens"] = lens
        children.append(entry)

    merge: dict[str, Any] | None = None
    if mode == "parallel":
        merge = {
            "strategy": "synthesize",
            "min_branches_pass": min(2, len(children)),
            "preserve_dissent": True,
            "synthesizer": "workers.orchestrator",
        }

    spec: dict[str, Any] = {
        "loop_name": loop_name,
        "version": "1.0.0",
        "objective": (
            f"{objective.rstrip()}\n"
            f"Achieve composite_quality >= {quality_threshold:.2f} within cost_limits."
        ),
        "inputs": {
            "schema": {
                "task": {
                    "type": "string",
                    "description": "Top-level task for the composed pipeline",
                    "required": True,
                }
            },
            "examples": [{"task": "Run the composed loop pipeline on this objective."}],
        },
        "memory": {"type": "ephemeral"},
        "workers": [
            {
                "id": "orchestrator",
                "role": f"Coordinate {mode} child loops and merge outputs",
                "model": {"provider": "openai", "name": "gpt-4.1-mini", "temperature": 0.2},
                "inputs": [{"from": "inputs.task"}],
                "outputs": {"name": "OrchestratorOutput", "format": "text"},
                "timeout_seconds": 180,
                "retries": 1,
                "cost_budget_usd": 0.50,
            }
        ],
        "evaluators": [
            {
                "id": "composite_gate",
                "type": "llm_rubric",
                "runs_after": ["orchestrator"],
                "rubric": {
                    "dimensions": [
                        {
                            "name": "pipeline_quality",
                            "weight": 1.0,
                            "scale": [0, 1],
                            "criteria": "Merged child outputs meet the composed objective",
                        }
                    ],
                    "pass_threshold": quality_threshold,
                },
                "model": {"provider": "openai", "name": "gpt-4.1-mini", "temperature": 0},
            }
        ],
        "feedback_channels": [
            {
                "id": "composite_to_orchestrator",
                "source": "evaluators.composite_gate",
                "destination": "workers.orchestrator",
                "format": "structured",
                "fields": ["failure_codes", "dimension_scores", "remediation_hints"],
                "max_tokens": 600,
                "when": "score < pass_threshold",
            }
        ],
        "optimization_strategy": {
            "type": "prompt_refinement",
            "max_steps": 10,
            "config": {"refinement_target": "workers.orchestrator"},
            "rollback": {"on_metric_drop": 0.05, "on_safety_failure": True},
        },
        "termination_conditions": {
            "success": [
                {
                    "metric": "composite_quality",
                    "operator": "gte",
                    "value": quality_threshold,
                    "consecutive": 1,
                }
            ],
            "failure": [
                {"type": "safety_violation", "action": "halt"},
                {"type": "max_iterations", "value": 12, "action": "halt"},
            ],
        },
        "metrics": [
            {
                "name": "composite_quality",
                "primary": True,
                "definition": "Quality of merged composition output",
                "source": "evaluators.composite_gate",
                "unit": "ratio",
                "target": quality_threshold,
            },
            {
                "name": "cost_usd",
                "definition": "Cumulative spend across child loops",
                "source": "telemetry.cost",
                "unit": "usd",
                "target": 4.0,
            },
        ],
        "safety_constraints": [
            {
                "id": "composition-guard",
                "type": "injection_detect",
                "scope": "pre_worker",
                "applies_to": ["orchestrator"],
                "action": "quarantine",
                "severity": "S1",
                "on_error": "halt",
            }
        ],
        "cost_limits": {
            "per_iteration_usd": 0.50,
            "cumulative_usd": 8.0,
            "token_soft_cap": 20000,
            "on_exceed": {"action": "halt"},
        },
        "composition": {
            "type": mode,
            "children": children,
            "adapters": [],
        },
        "metadata": {
            "schema_version": "1.1",
            "composition_type": mode,
            "child_loops": [c[0] for c in child_specs],
        },
    }
    if merge:
        spec["composition"]["merge"] = merge
    return spec


def parse_child_arg(raw: str, base_dir: Path) -> tuple[str, Path, str]:
    parts = raw.split(":", 2)
    if len(parts) == 1:
        path = Path(parts[0])
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        return path.stem, path, ""
    if len(parts) == 2:
        child_id, ref = parts
        path = Path(ref)
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        return child_id, path, ""
    child_id, ref, lens = parts
    path = Path(ref)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return child_id, path, lens


def save_composition(
    spec: dict[str, Any],
    path: Path,
    *,
    validate: bool = True,
    strict_composition: bool = False,
) -> None:
    if validate:
        errors = validate_spec(spec, lss_version="1.1")
        if errors:
            preview = "\n".join(f"  - {e}" for e in errors[:5])
            raise ValueError(f"Composition spec failed LSS validation:\n{preview}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(spec, fh, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)

    if strict_composition:
        import sys

        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from tools.composition_validator import validate_composition

        comp_errors, _ = validate_composition(path, spec)
        if comp_errors:
            raise ValueError(f"Composition graph invalid: {comp_errors[0]}")
