# LES Benchmarking Methodology

This document describes how to conduct a valid Loop Engineering Score evaluation. Follow these procedures to produce reproducible, comparable scores across systems and evaluators.

---

## 1. Prerequisites

Before running a LES benchmark:

1. **Define the loop boundary** — Explicitly state what is inside the loop (agents, tools, memory, human-in-the-loop gates) and what is external (infrastructure, datasets, human operators).
2. **Select a benchmark suite** — Use tasks from [../benchmarks/](../benchmarks/) or document a custom suite with equivalent rigor.
3. **Declare LES version** — Currently 1.0 ([LES-1.0.md](./LES-1.0.md)).
4. **Set iteration budget** — Maximum iterations per task before forced termination.
5. **Establish baselines** — Use suite defaults or justify custom baselines in writing.

---

## 2. Evaluation Protocol

### Phase 1: System Characterization

Document the loop architecture before any runs:

```yaml
system:
  name: "Example Agent Harness v2.1"
  loop_stages:
    observe: "Tool results + test output + git diff"
    evaluate: "LLM critic scores against rubric"
    decide: "Planner selects next tool or declares done"
    act: "Executor runs tool call or submits patch"
  memory:
    short_term: "Conversation context (128K tokens)"
    long_term: "Vector store of prior task summaries"
    persistence: "Session-scoped; cleared between tasks"
  termination:
    success: "All tests pass AND critic score ≥ 0.85"
    failure: "Budget exhausted OR 3 consecutive regressions"
  human_gates:
    - "Approval before git push (optional, disabled for benchmark)"
```

### Phase 2: Warm-Up Runs

Execute 2 warm-up tasks (not scored) to:

- Verify environment connectivity
- Confirm loop stages fire in order
- Calibrate timing instrumentation

Discard warm-up data entirely.

### Phase 3: Primary Benchmark Runs

For each task in the suite:

1. **Initialize** — Reset all memory, caches, and state to documented defaults
2. **Instrument** — Enable logging for all four loop stages with timestamps
3. **Execute** — Run until termination condition met or budget exhausted
4. **Capture** — Record goal trace `G_1, G_2, …, G_T`, costs, interventions, violations
5. **Repeat** — Minimum 5 runs per task for stochastic systems

### Phase 4: Perturbation Runs (Robustness)

Re-run a subset of tasks (minimum 3, recommended 5) under each perturbation:

| ID | Perturbation | Application Point |
|----|--------------|-------------------|
| P1 | Context truncation (-30%) | Before iteration 2 |
| P2 | Corrupted tool result (1 per run) | Random iteration |
| P3 | API latency (+20%) | All external calls |
| P4 | Model downgrade (1 tier) | All LLM calls |
| P5 | Budget reduction (-1 iteration) | At initialization |

Apply perturbations independently—one per run, not combined—unless testing compound failure modes (report separately).

### Phase 5: Scale Runs (Scalability)

Run at scale levels n ∈ {1, 2, 4, 8}:

- **Parallel scale:** n concurrent loop instances on independent tasks
- **Problem scale:** single loop on task with n× normal complexity (e.g., 8× more files to repair)

Document which scale dimension applies.

### Phase 6: OOD Runs (Adaptability)

Execute the holdout task set (defined per benchmark suite) without any configuration changes from primary runs. Record whether manual intervention was required.

---

## 3. Instrumentation Requirements

### Mandatory Logs

Every iteration must produce a structured record:

```json
{
  "iteration": 3,
  "timestamp_start": "2026-06-13T14:22:01.123Z",
  "timestamp_end": "2026-06-13T14:22:45.678Z",
  "observe": {
    "signals": ["test_output: 3/5 pass", "lint: 2 warnings"],
    "signal_fidelity": 1.0
  },
  "evaluate": {
    "goal_score": 0.60,
    "delta_from_previous": 0.20,
    "evaluation_method": "automated_test_harness"
  },
  "decide": {
    "action": "edit_file",
    "target": "src/parser.py",
    "rationale_hash": "a3f8..."
  },
  "act": {
    "outcome": "success",
    "side_effects": ["file_modified"],
    "cost_usd": 0.042
  },
  "human_interventions": [],
  "safety_events": []
}
```

### Cost Tracking

Track per-iteration:

- Token usage (input/output separately)
- Compute time (CPU/GPU seconds)
- External API calls (count and cost)
- Human time (if applicable)

Aggregate to `C_total` using conversion factors from [LES-1.0.md §2.3](./LES-1.0.md).

### Goal Function Measurement

The goal function must be measured by an **independent evaluator**—not the same component that decides loop actions. Acceptable evaluators:

- Automated test harness
- Held-out LLM judge (different model than loop agent)
- Human rater (blinded to system identity)
- Deterministic metric (BLEU, pass@k, etc.)

Document evaluator identity in the report.

---

## 4. Scoring Procedure

### Step 1: Compute Raw Metrics

From logged data, calculate per-category raw values per [LES-1.0.md](./LES-1.0.md).

### Step 2: Normalize

Apply baseline normalization for each category. Use suite defaults from [../benchmarks/suite-overview.md](../benchmarks/suite-overview.md) unless custom baselines are justified.

### Step 3: Apply Penalties and Bonuses

- Speed stall penalty
- Cost zero-progress penalty
- Safety automatic zero
- Adaptability learning bonus
- Cost marginal trend bonus

### Step 4: Compute Composite

Weighted sum per LES-1.0 formula.

### Step 5: Aggregate Across Tasks

For multi-task benchmarks:

```
LES_suite = (1/|Tasks|) × Σ LES_task
```

Report per-task scores alongside suite aggregate.

### Step 6: Confidence Interval

For stochastic systems, report mean ± CI across runs:

```
CI_95 = 1.96 × σ / √n
```

---

## 5. Reporting Template

```markdown
# LES Evaluation Report

## Metadata
- System: [name and version]
- LES Version: 1.0
- Benchmark Suite: [name and version]
- Evaluator: [person/org]
- Date: [YYYY-MM-DD]
- Runs per task: [n]

## Architecture Summary
[Loop boundary, stages, memory, termination]

## Results

### Composite Score
LES = 0.XX ± 0.YY

### Category Breakdown
| Category | Raw | Normalized | Weight | Contribution |
|----------|-----|------------|--------|--------------|
| Effectiveness | ... | 0.XX | 0.20 | 0.XX |
| ... | | | | |

### Per-Task Scores
| Task | LES | Iterations | Cost | Notes |
|------|-----|------------|------|-------|
| ... | | | | |

### Diagnostics
- Convergence rate: X.XX
- Regression count: N
- Termination reasons: [breakdown]

## Perturbation Results
[Table of G_clean vs G_perturbed per perturbation]

## Scale Results
[Table of metrics at n=1,2,4,8]

## OOD Results
[Transfer ratio, config changes required]

## Raw Data
[Link to iteration logs, reproducibility instructions]
```

---

## 6. Validity Criteria

A LES evaluation is **valid** if and only if:

| Criterion | Requirement |
|-----------|-------------|
| Independence | Goal evaluator ≠ loop decision component |
| Completeness | All 8 categories measured OR partial score declared with renormalized weights |
| Reproducibility | Environment spec and random seeds documented |
| Minimum runs | ≥ 5 per task (benchmarks) or ≥ 3 (case studies) |
| Budget declared | Iteration budget stated before runs |
| No post-hoc tuning | Loop configuration frozen before primary runs |

Invalid evaluations may be published with an `INVALID` tag but must not be compared against valid scores.

---

## 7. Common Failure Modes in Benchmarking

### 7.1 Evaluator Collapse

The loop agent and the goal evaluator share weights, context, or training data. This inflates Effectiveness and deflates Adaptability. **Fix:** Use a distinct model or automated harness.

### 7.2 Budget Gaming

Systems that exhaust the iteration budget on trivial improvements to inflate `ΔG` for Cost scoring. **Fix:** Apply the zero-progress penalty and report convergence rate.

### 7.3 Cherry-Picked Perturbations

Running only easy perturbations or stopping after the first success. **Fix:** Run all standard perturbations independently.

### 7.4 Memory Leakage

State from prior tasks bleeding into subsequent tasks, inflating Adaptability. **Fix:** Hard reset between tasks; verify with a control task.

### 7.5 Human-in-the-Loop Masking

Human operators making unstated corrections that should count as interventions. **Fix:** Log all human actions with timestamps; apply intervention weights.

---

## 8. Comparison Guidelines

When comparing two systems:

1. **Same benchmark suite and version** — Required for direct comparison
2. **Same iteration budget** — Required
3. **Same perturbation set** — Required for Robustness comparison
4. **Statistical test** — If CI intervals overlap, report "no significant difference" unless paired test shows p < 0.05
5. **Category-level comparison** — A system with higher LES may be worse in Safety; always compare categories individually

Do not rank systems across different benchmark suites without a calibration bridge task.

---

## 9. Ethics and Safety

Benchmark operators must:

- Run Safety perturbations in sandboxed environments
- Not publish outputs containing real PII, credentials, or harmful content
- Disclose any human labor involved (for Autonomy scoring and ethical transparency)
- Report severe safety violations to the benchmark maintainers regardless of score impact

---

## 10. Submission Process

To submit scores to the Loop Engineering repository:

1. Fork the repository
2. Add evaluation report to `evaluations/[system-name]/`
3. Include raw iteration logs (compressed)
4. Include reproducibility script or Dockerfile
5. Open a pull request with the reporting template filled

Maintainers verify validity criteria before merging.
