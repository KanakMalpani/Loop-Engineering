"""Fluent builder for LSS 1.0 loop specifications."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from loopforge.level_hint import apply_level_hint
from loopforge.library import fork_spec
from loopforge.patterns import Pattern
from loopforge.validate import validate_spec


class LoopBuilder:
    """Build and export valid LSS YAML from pattern presets."""

    def __init__(
        self,
        loop_name: str,
        objective: str,
        *,
        version: str = "1.0.0",
    ) -> None:
        self.loop_name = loop_name
        self.objective = objective
        self.version = version
        self._pattern: Pattern | None = None
        self._inputs: dict[str, dict[str, Any]] = {
            "task": {
                "type": "string",
                "description": "Primary task description or domain context",
                "required": True,
            }
        }
        self._input_examples: list[dict[str, str]] = [
            {"task": "Complete the declared objective for this loop profile."}
        ]
        self._quality_threshold = 0.80
        self._max_iterations = 8
        self._max_optimization_steps = 5
        self._model = {
            "provider": "openai",
            "name": "gpt-4.1-mini",
            "temperature": 0.2,
        }
        self._eval_model = {
            "provider": "openai",
            "name": "gpt-4.1-mini",
            "temperature": 0,
        }
        self._per_iteration_usd = 0.15
        self._cumulative_usd = 0.50
        self._forked_spec: dict[str, Any] | None = None
        self._lss_version = "1.0"

    @classmethod
    def from_library(
        cls,
        source_name: str,
        new_name: str,
        *,
        objective: str | None = None,
        library_dir: Path | None = None,
    ) -> LoopBuilder:
        spec = fork_spec(source_name, new_name, library_dir=library_dir)
        builder = cls(new_name, objective or str(spec.get("objective", "")).split("\n")[0])
        builder._forked_spec = spec
        builder.version = str(spec.get("version", "1.0.0"))
        return builder

    def with_lss_version(self, version: str) -> LoopBuilder:
        self._lss_version = version
        return self

    def from_pattern(self, pattern: Pattern | str) -> LoopBuilder:
        if isinstance(pattern, str):
            pattern = Pattern.from_str(pattern)
        self._pattern = pattern
        return self

    def with_input(
        self,
        name: str,
        *,
        type: str = "string",
        description: str = "",
        required: bool = True,
        example: str | None = None,
    ) -> LoopBuilder:
        self._inputs[name] = {
            "type": type,
            "description": description or f"Input field: {name}",
            "required": required,
        }
        if example is not None:
            self._input_examples = [{name: example}]
        return self

    def with_quality_threshold(self, threshold: float) -> LoopBuilder:
        self._quality_threshold = threshold
        return self

    def with_max_iterations(self, value: int) -> LoopBuilder:
        self._max_iterations = value
        return self

    def with_model(
        self,
        provider: str,
        name: str,
        *,
        temperature: float = 0.2,
    ) -> LoopBuilder:
        self._model = {
            "provider": provider,
            "name": name,
            "temperature": temperature,
        }
        return self

    def with_cost_limits(
        self,
        *,
        per_iteration_usd: float,
        cumulative_usd: float,
    ) -> LoopBuilder:
        self._per_iteration_usd = per_iteration_usd
        self._cumulative_usd = cumulative_usd
        return self

    def build(self) -> dict[str, Any]:
        if self._forked_spec is not None:
            spec = deepcopy(self._forked_spec)
            spec["loop_name"] = self.loop_name
            if self.objective:
                spec["objective"] = self._objective_text()
            return spec
        if self._pattern is None:
            raise ValueError("Call from_pattern() before build()")
        builders = {
            Pattern.SIMPLE: self._build_simple,
            Pattern.REFLECTION: self._build_reflection,
            Pattern.VERIFICATION: self._build_verification,
            Pattern.RESEARCH: self._build_research,
        }
        spec = builders[self._pattern]()
        spec["loop_name"] = self.loop_name
        spec["version"] = self.version
        spec["objective"] = self._objective_text()
        spec["inputs"] = {
            "schema": deepcopy(self._inputs),
            "examples": deepcopy(self._input_examples),
        }
        spec["cost_limits"]["per_iteration_usd"] = self._per_iteration_usd
        spec["cost_limits"]["cumulative_usd"] = self._cumulative_usd
        spec["metrics"][0]["target"] = self._quality_threshold
        spec["evaluators"][0]["rubric"]["pass_threshold"] = self._quality_threshold
        spec["termination_conditions"]["success"][0]["value"] = self._quality_threshold
        spec["termination_conditions"]["failure"][1]["value"] = self._max_iterations
        spec["optimization_strategy"]["max_steps"] = self._max_optimization_steps
        meta = spec.setdefault("metadata", {})
        if isinstance(meta, dict):
            meta.setdefault("schema_version", self._lss_version)
        return spec

    def validate(self, spec: dict[str, Any] | None = None) -> list[str]:
        data = spec if spec is not None else self.build()
        version = "1.1" if data.get("composition") else self._lss_version
        return validate_spec(data, lss_version=version)

    def save(
        self,
        path: str | Path,
        *,
        validate: bool = True,
        suggest_level: bool = False,
    ) -> Path:
        spec = self.build()
        if suggest_level:
            hint = apply_level_hint(spec, getattr(self, "_fork_source", None))
            print(
                f"Level hint: L{hint['taxonomy_level']} "
                f"(pattern={hint['pattern']}, workers={hint['workers']}, confidence={hint['confidence']})"
            )
        if validate:
            errors = self.validate(spec)
            if errors:
                preview = "\n".join(f"  - {e}" for e in errors[:5])
                extra = f"\n  ... and {len(errors) - 5} more" if len(errors) > 5 else ""
                raise ValueError(f"Spec failed LSS validation:\n{preview}{extra}")
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(
                spec,
                fh,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
                width=100,
            )
        return out

    def _objective_text(self) -> str:
        return (
            f"{self.objective.rstrip()}\n"
            f"Achieve primary_quality >= {self._quality_threshold:.2f} within cost_limits "
            "with zero safety violations."
        )

    def _primary_input_ref(self) -> str:
        first_key = next(iter(self._inputs))
        return f"inputs.{first_key}"

    def _worker(
        self,
        worker_id: str,
        role: str,
        *,
        depends_on: list[str] | None = None,
    ) -> dict[str, Any]:
        worker: dict[str, Any] = {
            "id": worker_id,
            "role": role,
            "model": deepcopy(self._model),
            "inputs": [{"from": self._primary_input_ref()}],
            "outputs": {"name": f"{worker_id.title()}Output", "format": "text"},
            "timeout_seconds": 120,
            "retries": 1,
            "cost_budget_usd": round(self._per_iteration_usd * 0.6, 2),
        }
        if depends_on:
            worker["depends_on"] = depends_on
        return worker

    def _quality_rubric(
        self,
        evaluator_id: str,
        runs_after: list[str],
        *,
        criteria: str,
        dimension_name: str = "quality",
    ) -> dict[str, Any]:
        return {
            "id": evaluator_id,
            "type": "llm_rubric",
            "runs_after": runs_after,
            "rubric": {
                "dimensions": [
                    {
                        "name": dimension_name,
                        "weight": 1.0,
                        "scale": [0, 1],
                        "criteria": criteria,
                    }
                ],
                "pass_threshold": self._quality_threshold,
            },
            "model": deepcopy(self._eval_model),
        }

    def _shared_tail(self, worker_ids: list[str], primary_worker: str) -> dict[str, Any]:
        return {
            "memory": {"type": "ephemeral"},
            "feedback_channels": [
                {
                    "id": "quality_to_worker",
                    "source": "evaluators.quality_rubric",
                    "destination": f"workers.{primary_worker}",
                    "format": "structured",
                    "fields": ["failure_codes", "dimension_scores", "remediation_hints"],
                    "max_tokens": 300,
                    "when": "score < pass_threshold",
                },
                {
                    "id": "quality_to_optimizer",
                    "source": "evaluators.quality_rubric",
                    "destination": "optimization_strategy.prompt_refinement",
                    "format": "structured",
                    "fields": ["failure_codes", "remediation_hints"],
                    "max_tokens": 200,
                },
            ],
            "optimization_strategy": {
                "type": "prompt_refinement",
                "max_steps": self._max_optimization_steps,
                "config": {
                    "refinement_target": f"workers.{primary_worker}",
                    "preserve_sections": ["output_format"],
                },
                "rollback": {
                    "on_metric_drop": 0.05,
                    "on_safety_failure": True,
                },
            },
            "termination_conditions": {
                "success": [
                    {
                        "metric": "primary_quality",
                        "operator": "gte",
                        "value": self._quality_threshold,
                        "consecutive": 1,
                    }
                ],
                "failure": [
                    {"type": "safety_violation", "action": "halt"},
                    {
                        "type": "max_iterations",
                        "value": self._max_iterations,
                        "action": "halt",
                    },
                    {"type": "evaluator_error", "consecutive": 2, "action": "halt"},
                ],
                "stall": [
                    {
                        "metric": "primary_quality",
                        "window_iterations": 3,
                        "min_improvement": 0.03,
                        "action": "halt",
                    }
                ],
            },
            "metrics": [
                {
                    "name": "primary_quality",
                    "primary": True,
                    "definition": "Weighted score from quality_rubric evaluator",
                    "source": "evaluators.quality_rubric",
                    "unit": "ratio",
                    "target": self._quality_threshold,
                    "regression_threshold": 0.05,
                },
                {
                    "name": "cost_usd",
                    "definition": "Total API spend per loop run",
                    "source": "telemetry.cost",
                    "unit": "usd",
                    "target": self._cumulative_usd,
                },
            ],
            "safety_constraints": [
                {
                    "id": "injection-guard",
                    "type": "injection_detect",
                    "scope": "pre_worker",
                    "applies_to": worker_ids,
                    "action": "quarantine",
                    "severity": "S0",
                    "on_error": "halt",
                    "config": {"ml_classifier": True, "max_risk_score": 0.7},
                },
                {
                    "id": "secret-scan",
                    "type": "secret_scan",
                    "scope": "post_worker",
                    "applies_to": worker_ids,
                    "action": "halt",
                    "severity": "S0",
                    "on_error": "halt",
                    "config": {"entropy_threshold": 4.5},
                },
            ],
            "cost_limits": {
                "per_iteration_usd": self._per_iteration_usd,
                "cumulative_usd": self._cumulative_usd,
                "token_soft_cap": 8000,
                "on_approach": {"threshold_percent": 80, "action": "warn"},
                "on_exceed": {"action": "halt"},
            },
        }

    def _build_simple(self) -> dict[str, Any]:
        worker_id = "worker"
        spec = self._shared_tail([worker_id], worker_id)
        spec["workers"] = [
            self._worker(worker_id, "Execute the declared objective for the primary input")
        ]
        spec["evaluators"] = [
            self._quality_rubric(
                "quality_rubric",
                [worker_id],
                criteria="Output meets the stated objective with no critical omissions",
            )
        ]
        return spec

    def _build_reflection(self) -> dict[str, Any]:
        generator = "generator"
        reflector = "reflector"
        spec = self._shared_tail([generator, reflector], generator)
        spec["workers"] = [
            self._worker(generator, "Produce a candidate solution for the task"),
            self._worker(
                reflector,
                "Critique the candidate against goals, constraints, and evidence",
                depends_on=[generator],
            ),
        ]
        spec["evaluators"] = [
            self._quality_rubric(
                "quality_rubric",
                [generator],
                criteria="Candidate output aligns with objective before reflection pass",
            )
        ]
        spec["feedback_channels"].append(
            {
                "id": "reflection_to_generator",
                "source": f"workers.{reflector}",
                "destination": f"workers.{generator}",
                "format": "structured",
                "fields": ["failure_codes", "remediation_hints", "summary"],
                "max_tokens": 400,
            }
        )
        return spec

    def _build_verification(self) -> dict[str, Any]:
        implementer = "implementer"
        spec = self._shared_tail([implementer], implementer)
        spec["workers"] = [
            self._worker(
                implementer,
                "Implement a change and iterate until verification gates pass",
            )
        ]
        spec["evaluators"] = [
            self._quality_rubric(
                "quality_rubric",
                [implementer],
                criteria="Functional tests pass and change stays within declared scope",
                dimension_name="verification",
            ),
            {
                "id": "scope_check",
                "type": "deterministic",
                "runs_after": [implementer],
                "implementation": "evaluators.word_count_max",
            },
        ]
        spec["metrics"].append(
            {
                "name": "scope_words",
                "definition": "Word count guard on implementer output",
                "source": "evaluators.scope_check",
                "unit": "count",
                "target": 2000,
            }
        )
        return spec

    def _build_research(self) -> dict[str, Any]:
        planner = "query_planner"
        synthesizer = "synthesizer"
        spec = self._shared_tail([planner, synthesizer], synthesizer)
        spec["workers"] = [
            self._worker(planner, "Decompose the question into retrieval queries"),
            self._worker(
                synthesizer,
                "Draft a sourced brief from planned queries and evidence",
                depends_on=[planner],
            ),
        ]
        spec["evaluators"] = [
            self._quality_rubric(
                "quality_rubric",
                [synthesizer],
                criteria="Brief cites sources, states uncertainty, and answers the task",
                dimension_name="research_quality",
            )
        ]
        return spec
