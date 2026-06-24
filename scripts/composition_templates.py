#!/usr/bin/env python3
"""Shared orchestrator shell for composed loop-library specs."""

from __future__ import annotations

from typing import Any


def orchestrator_shell(
    loop_name: str,
    objective: str,
    level: int,
    les: float,
    composition: dict[str, Any],
    *,
    pass_threshold: float = 0.85,
    max_iterations: int = 20,
    cumulative_usd: float = 8.0,
) -> str:
    """Return LSS 1.0 YAML with composition block and minimal orchestrator."""
    comp_type = composition["type"]
    child_ids = [c["id"] for c in composition["children"]]
    first_eval = f"pipeline_{child_ids[0]}"

    adapter_yaml = ""
    for a in composition.get("adapters", []):
        adapter_yaml += f"""
    - from: {a['from']}
      to: {a['to']}"""

    children_yaml = ""
    for c in composition["children"]:
        trigger = ""
        if c.get("trigger"):
            trigger = f"\n      trigger: \"{c['trigger']}\""
        children_yaml += f"""
    - id: {c['id']}
      ref: {c['ref']}
      role: {c.get('role', 'stage')}{trigger}"""

    return f"""loop_name: {loop_name}
version: 1.0.0

objective: >
  {objective}
  Achieve composite_quality >= {pass_threshold:.2f} within cost_limits.

inputs:
  schema:
    task:
      type: string
      description: "Top-level task for the composed pipeline"
      required: true
  examples:
    - task: "Run the composed loop pipeline on this objective."

memory:
  type: ephemeral

workers:
  - id: orchestrator
    role: "Route work across composed child loops and merge stage outputs"
    model:
      provider: openai
      name: gpt-4.1-mini
      temperature: 0.2
    inputs:
      - from: inputs.task
    outputs:
      name: OrchestratorOutput
      format: text
    timeout_seconds: 180
    retries: 1
    cost_budget_usd: 0.50

evaluators:
  - id: composite_gate
    type: llm_rubric
    runs_after: [orchestrator]
    rubric:
      dimensions:
        - name: pipeline_quality
          weight: 1.0
          scale: [0, 1]
          criteria: "All child loop stages met their pass thresholds"
      pass_threshold: {pass_threshold:.2f}
    model:
      provider: openai
      name: gpt-4.1-mini
      temperature: 0

feedback_channels:
  - id: composite_to_orchestrator
    source: evaluators.composite_gate
    destination: workers.orchestrator
    format: structured
    fields: [failure_codes, dimension_scores, remediation_hints]
    max_tokens: 600
    when: "score < pass_threshold"

optimization_strategy:
  type: prompt_refinement
  max_steps: {max_iterations}
  config:
    refinement_target: workers.orchestrator
  rollback:
    on_metric_drop: 0.05
    on_safety_failure: true

termination_conditions:
  success:
    - metric: composite_quality
      operator: gte
      value: {pass_threshold:.2f}
      consecutive: 1
  failure:
    - type: safety_violation
      action: halt
    - type: max_iterations
      value: {max_iterations}
      action: halt

metrics:
  - name: composite_quality
    primary: true
    definition: "Product of child stage quality scores"
    source: evaluators.composite_gate
    unit: ratio
    target: {pass_threshold:.2f}
  - name: cost_usd
    definition: "Cumulative spend across all child loops"
    source: telemetry.cost
    unit: usd
    target: {cumulative_usd * 0.6:.2f}

safety_constraints:
  - id: composition-guard
    type: injection_detect
    scope: pre_worker
    applies_to: [orchestrator]
    action: quarantine
    severity: S1
    on_error: halt

cost_limits:
  per_iteration_usd: {cumulative_usd / max_iterations:.2f}
  cumulative_usd: {cumulative_usd:.2f}
  token_soft_cap: 20000
  on_exceed:
    action: halt

composition:
  type: {comp_type}
  children:{children_yaml}
  adapters:{adapter_yaml}

metadata:
  taxonomy_level: {level}
  les_estimate: {les}
  composition_type: {comp_type}
  child_loops: {child_ids}
  lss_extension: "1.1-composition-draft"
"""
