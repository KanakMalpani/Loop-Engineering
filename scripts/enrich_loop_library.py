#!/usr/bin/env python3
"""Generate LSS 1.0-compliant loop-library YAML from architecture metadata."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "loop-library"

# worker_id, role, depends_on (empty = root)
SPECS: dict[str, dict] = {
    "coding-agent": {
        "objective": "Implement a software change so tests pass, static analysis is clean, and diff stays in scope.",
        "level": 3,
        "les": 82,
        "workers": [
            ("architect", "Produce file-touch plan and test strategy before code changes", []),
            ("implementer", "Implement change and run edit-test inner loop", ["architect"]),
            ("reviewer", "Review diff for security, scope, and diff budget", ["implementer"]),
        ],
        "evaluators": [
            ("test_suite", "Functional test oracle"),
            ("linter", "Static analysis gate"),
            ("diff_budget", "Complexity cap on changed lines"),
            ("scope_guard", "Path allowlist enforcement"),
        ],
        "pass_threshold": 0.88,
        "max_iterations": 12,
        "cumulative_usd": 5.0,
    },
    "autonomous-debugger": {
        "objective": "Repair failing tests with minimal, reviewable diffs via reproduce-diagnose-patch-verify.",
        "level": 3,
        "les": 85,
        "workers": [
            ("reproducer", "Confirm failure reproduces deterministically", []),
            ("diagnostician", "Rank root-cause hypotheses from traces", ["reproducer"]),
            ("patcher", "Apply minimal diff addressing root cause", ["diagnostician"]),
            ("verifier", "Reject symptom fixes; require full suite pass", ["patcher"]),
        ],
        "evaluators": [
            ("repro_oracle", "Failure reproduces before diagnose"),
            ("test_suite", "Full test suite pass"),
            ("patch_budget", "Diff size within budget"),
            ("regression_guard", "No unrelated file changes"),
        ],
        "pass_threshold": 0.85,
        "max_iterations": 15,
        "cumulative_usd": 3.5,
    },
    "research-agent": {
        "objective": "Produce a sourced research brief with traceable citations and explicit uncertainty.",
        "level": 2,
        "les": 78,
        "workers": [
            ("query_planner", "Decompose question into retrieval queries", []),
            ("retriever", "Fetch evidence from search and corpora", ["query_planner"]),
            ("synthesizer", "Draft brief from retrieved evidence", ["retriever"]),
            ("critic", "Adversarial review triggering re-retrieval", ["synthesizer"]),
        ],
        "evaluators": [
            ("citation_verifier", "Citation integrity oracle"),
            ("hallucination_scan", "Entailment alignment check"),
            ("coherence_rubric", "Rhetorical coherence rubric"),
        ],
        "pass_threshold": 0.80,
        "max_iterations": 10,
        "cumulative_usd": 2.5,
    },
    "scientific-discovery-agent": {
        "objective": "Generate and evaluate hypotheses until supported model emerges or search exhausts.",
        "level": 4,
        "les": 71,
        "workers": [
            ("hypothesis_generator", "Propose competing hypotheses", []),
            ("experiment_designer", "Pre-register experiment protocol", ["hypothesis_generator"]),
            ("executor", "Run deterministic experiment code", ["experiment_designer"]),
            ("analyst", "Statistical analysis and model selection", ["executor"]),
        ],
        "evaluators": [
            ("significance_test", "Statistical significance gate"),
            ("replication_check", "Replication consistency"),
            ("hypothesis_diversity", "Maintain competing hypotheses"),
        ],
        "pass_threshold": 0.75,
        "max_iterations": 20,
        "cumulative_usd": 8.0,
    },
    "business-strategy-agent": {
        "objective": "Produce decision-ready strategy memo with ranked options and red-team challenges.",
        "level": 3,
        "les": 76,
        "workers": [
            ("strategist", "Generate ranked strategic options", []),
            ("financial_modeler", "Quantify scenario outcomes", ["strategist"]),
            ("red_team", "Adversarial challenge of assumptions", ["strategist"]),
            ("synthesizer", "Merge into decision memo", ["financial_modeler", "red_team"]),
        ],
        "evaluators": [
            ("scenario_stress", "Scenario stress tests"),
            ("kpi_alignment", "KPI alignment rubric"),
            ("assumption_audit", "Explicit assumption tracking"),
        ],
        "pass_threshold": 0.82,
        "max_iterations": 10,
        "cumulative_usd": 4.0,
    },
    "startup-validator": {
        "objective": "Validate startup hypotheses via experiments and produce PMF evidence ledger.",
        "level": 2,
        "les": 74,
        "workers": [
            ("experiment_designer", "Design falsifiable PMF experiments", []),
            ("operator", "Execute experiment automation", ["experiment_designer"]),
            ("interviewer", "Synthesize qualitative signals", ["operator"]),
            ("judge", "Neutral kill-continue-pivot verdict", ["interviewer"]),
        ],
        "evaluators": [
            ("falsification_log", "Hypothesis falsification record"),
            ("signal_strength", "Evidence strength rubric"),
            ("experiment_integrity", "Protocol adherence check"),
        ],
        "pass_threshold": 0.78,
        "max_iterations": 8,
        "cumulative_usd": 2.0,
    },
    "learning-coach": {
        "objective": "Guide learner to demonstrable mastery via adaptive instruction and verified assessments.",
        "level": 2,
        "les": 80,
        "workers": [
            ("diagnostician", "Estimate learner knowledge state", []),
            ("instructor", "Deliver adaptive instruction", ["diagnostician"]),
            ("exercise_generator", "Generate spaced practice items", ["instructor"]),
            ("reflector", "Summarize session progress", ["exercise_generator"]),
        ],
        "evaluators": [
            ("mastery_probe", "Mastery assessment oracle"),
            ("retention_check", "Retention verification"),
            ("pedagogy_rubric", "Instruction quality rubric"),
        ],
        "pass_threshold": 0.80,
        "max_iterations": 12,
        "cumulative_usd": 1.5,
    },
    "interview-coach": {
        "objective": "Prepare candidate via mock sessions and rubric-based iterative feedback.",
        "level": 2,
        "les": 77,
        "workers": [
            ("interviewer", "Conduct realistic mock interviews", []),
            ("proctor", "Score responses against rubric", ["interviewer"]),
            ("coach", "Deliver actionable feedback", ["proctor"]),
            ("drill_master", "Run rapid micro-drills on weak areas", ["coach"]),
        ],
        "evaluators": [
            ("rubric_score", "Technical rubric scoring"),
            ("behavioral_calibration", "Behavioral dimension check"),
            ("improvement_delta", "Iteration-over-iteration improvement"),
        ],
        "pass_threshold": 0.78,
        "max_iterations": 10,
        "cumulative_usd": 1.8,
    },
    "writing-assistant": {
        "objective": "Produce publication-ready content through iterative drafting and multi-channel review.",
        "level": 2,
        "les": 79,
        "workers": [
            ("outliner", "Produce document structure and section plan", []),
            ("drafter", "Draft long-form content", ["outliner"]),
            ("editor", "Line editing and style refinement", ["drafter"]),
            ("fact_checker", "Verify factual claims", ["editor"]),
        ],
        "evaluators": [
            ("style_rubric", "Style and structure rubric"),
            ("fact_check", "Fact verification oracle"),
            ("readability", "Readability and clarity score"),
        ],
        "pass_threshold": 0.82,
        "max_iterations": 10,
        "cumulative_usd": 2.2,
    },
}


def worker_block(wid: str, role: str, deps: list[str]) -> str:
    dep_line = f"\n    depends_on: [{', '.join(deps)}]" if deps else ""
    return f"""  - id: {wid}
    role: "{role}"
    model:
      provider: openai
      name: gpt-4.1-mini
      temperature: 0.2{dep_line}
    inputs:
      - from: inputs.task
    outputs:
      name: {wid.title().replace('_', '')}Output
      format: text
    timeout_seconds: 120
    retries: 1
    cost_budget_usd: 0.30"""


def evaluator_block(eid: str, criteria: str, runs_after: list[str]) -> str:
    after = runs_after[-1] if runs_after else "workers"
    workers_list = runs_after if runs_after else []
    runs = workers_list if workers_list else [after.split(".")[-1] if "." in after else after]
    return f"""  - id: {eid}
    type: llm_rubric
    runs_after: [{', '.join(runs)}]
    rubric:
      dimensions:
        - name: quality
          weight: 1.0
          scale: [0, 1]
          criteria: "{criteria}"
      pass_threshold: 0.75
    model:
      provider: openai
      name: gpt-4.1-mini
      temperature: 0"""


def build(loop_name: str, cfg: dict) -> str:
    workers = cfg["workers"]
    worker_ids = [w[0] for w in workers]
    worker_yaml = "\n".join(worker_block(w[0], w[1], w[2]) for w in workers)
    evaluators = cfg["evaluators"]
    eval_yaml = "\n".join(
        evaluator_block(e[0], e[1], worker_ids[: min(2, len(worker_ids))]) for e in evaluators
    )
    last_worker = worker_ids[-1]
    feedback = f"""  - id: quality_to_{last_worker}
    source: evaluators.{evaluators[0][0]}
    destination: workers.{last_worker}
    format: structured
    fields: [failure_codes, dimension_scores, remediation_hints]
    max_tokens: 500
    when: "score < pass_threshold"
  - id: quality_to_optimizer
    source: evaluators.{evaluators[0][0]}
    destination: optimization_strategy.prompt_refinement
    format: structured
    fields: [failure_codes, remediation_hints]
    max_tokens: 200"""

    return f"""loop_name: {loop_name}
version: 1.0.0

objective: >
  {cfg['objective']}
  Achieve primary_quality >= {cfg['pass_threshold']:.2f} within cost_limits with zero safety violations.

inputs:
  schema:
    task:
      type: string
      description: "Primary task description or domain context"
      required: true
  examples:
    - task: "Complete the declared objective for this loop profile."

memory:
  type: ephemeral

workers:
{worker_yaml}

evaluators:
{eval_yaml}

feedback_channels:
{feedback}

optimization_strategy:
  type: prompt_refinement
  max_steps: {cfg['max_iterations']}
  config:
    refinement_target: workers.{last_worker}
  rollback:
    on_metric_drop: 0.05
    on_safety_failure: true

termination_conditions:
  success:
    - metric: primary_quality
      operator: gte
      value: {cfg['pass_threshold']:.2f}
      consecutive: 1
  failure:
    - type: safety_violation
      action: halt
    - type: max_iterations
      value: {cfg['max_iterations']}
      action: halt
  stall:
    - metric: primary_quality
      window_iterations: 3
      min_improvement: 0.03
      action: halt

metrics:
  - name: primary_quality
    primary: true
    definition: "Weighted score from primary evaluator rubric"
    source: evaluators.{evaluators[0][0]}
    unit: ratio
    target: {cfg['pass_threshold']:.2f}
    regression_threshold: 0.05
  - name: cost_usd
    definition: "Total API spend per loop run"
    source: telemetry.cost
    unit: usd
    target: {cfg['cumulative_usd'] * 0.5:.2f}

safety_constraints:
  - id: injection-guard
    type: injection_detect
    scope: pre_worker
    applies_to: [{', '.join(worker_ids)}]
    action: quarantine
    severity: S1
    on_error: halt
    config:
      max_risk_score: 0.7

cost_limits:
  per_iteration_usd: {cfg['cumulative_usd'] / cfg['max_iterations']:.2f}
  cumulative_usd: {cfg['cumulative_usd']:.2f}
  token_soft_cap: 12000
  on_approach:
    threshold_percent: 80
    action: warn
  on_exceed:
    action: halt

metadata:
  taxonomy_level: {cfg['level']}
  les_estimate: {cfg['les']}
  worker_count: {len(workers)}
  evaluator_count: {len(evaluators)}
  enriched: "2026-06-17 architecture-aligned LSS 1.0"
"""


def main() -> None:
    for name, cfg in SPECS.items():
        path = LIB / f"{name}.yaml"
        path.write_text(build(name, cfg), encoding="utf-8")
        print(f"Wrote {path.name} ({len(cfg['workers'])} workers, {len(cfg['evaluators'])} evaluators)")


if __name__ == "__main__":
    main()
