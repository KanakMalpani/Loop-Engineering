# Measure Phase

The Measure phase establishes **evidence** for loop behavior. Without measurement, Improve becomes guesswork and Scale becomes replication of luck. Measurement answers: What is the baseline? Is a change real or noise? Are we optimizing the right metric? Are safety and cost envelopes holding?

Measurement is not a one-time activity—it runs continuously in production with periodic baseline refresh.

---

## Measurement Objectives

1. **Baseline** — Quantify primary and secondary metrics before optimization or scale.
2. **Instrumentation** — Ensure every iteration emits structured, correlatable data.
3. **Calibration** — Verify evaluators discriminate good from bad on fixtures.
4. **Guardrails** — Confirm cost_limits and safety_constraints fire at expected thresholds.
5. **Comparability** — Changes across LSS versions are A/B comparable on fixed fixtures.

---

## What to Measure

### Primary Quality Metrics

Derived from LSS `metrics` and evaluator rubrics. Examples by loop type:

| Loop type | Primary metric | Unit |
|-----------|----------------|------|
| Research | `weighted_rubric_score` | 0–1 |
| Code patch | `test_pass_rate` | 0–1 |
| Classification | `f1_score` | 0–1 |
| Summarization | `coverage + faithfulness composite` | 0–1 |
| Multi-agent task | `end_to_end_success` | boolean |

Always document **how** the metric is computed—not just its name.

### Secondary Metrics (Operational)

| Metric | Purpose |
|--------|---------|
| `iteration_latency_p50`, `p95` | Performance regressions |
| `tokens_in`, `tokens_out` per worker | Cost attribution |
| `cost_usd_per_iteration` | Budget tracking |
| `evaluator_agreement` | Multi-evaluator health |
| `safety_trigger_rate` | Constraint tuning |
| `retry_count` | Worker reliability |
| `optimization_steps` | Convergence behavior |
| `memory_write_bytes` | Context bloat detection |

### Leading vs. Lagging Indicators

| Lagging (outcome) | Leading (predictive) |
|-------------------|----------------------|
| Primary quality score | Deterministic pre-check pass rate |
| Task success rate | Evaluator confidence variance |
| User acceptance | Token growth per iteration |
| Incident count | Safety near-miss rate (soft triggers) |

Optimize on lagging metrics; use leading metrics for early warning.

---

## Measurement Decision Tree

```
START: What is the measurement goal?
│
├─ Pre-production baseline
│   ├─ Fixtures available?
│   │   ├─ YES → Run workers + evaluators on fixture set (bounded cost_limits)
│   │   └─ NO  → Create minimum 5 fixtures (golden, edge, adversarial) first
│   └─ Output: baseline report + dashboard skeleton
│
├─ Post-change verification (Improve)
│   ├─ Change isolated to one subsystem?
│   │   ├─ YES → Paired comparison on same fixtures (before/after)
│   │   └─ NO  → Full regression suite; treat as version bump
│   └─ Statistical significance required?
│       ├─ YES → n ≥ 30 per arm or bootstrap CI
│       └─ NO  → Directional check only (exploratory loops)
│
├─ Production monitoring
│   └─ Streaming metrics + weekly baseline refresh on fixture subset
│
└─ Evaluator health check
    └─ Golden/trap fixtures on schedule; independent of worker runs
```

---

## Baseline Protocol

### Step 1: Freeze Configuration

- Pin LSS `version`, model IDs, and dependency versions.
- Record git commit hash and timestamp.
- Disable optimization_strategy auto-changes during baseline collection.

### Step 2: Select Inputs

| Set | Size | Purpose |
|-----|------|---------|
| Core fixtures | 10–50 | Representative happy path |
| Edge fixtures | 5–15 | Boundaries, empty inputs, max size |
| Adversarial | 5–10 | Safety stress (never in production uncontrolled) |
| Production sample | 100+ (sampled) | Distribution realism |

### Step 3: Run Protocol

For each fixture:

1. Execute full loop until termination (or cap for baseline mode).
2. Record all metrics per iteration.
3. Store artifacts with `baseline_run_id`.
4. Respect `cost_limits`; abort baseline if exceeded (indicates design flaw).

### Step 4: Aggregate

Report at minimum:

```
primary_metric: mean, std, p5, p50, p95
cost_usd: mean, total
iteration_count: mean, max
safety_triggers: count by constraint_id
evaluator_scores: per-dimension breakdown
failure_codes: frequency table
```

### Step 5: Sign-off

Baseline is **accepted** when:

- [ ] ≥95% of core fixtures reach termination without infra errors
- [ ] Primary metric variance documented (std > 0 unless deterministic)
- [ ] Evaluator golden pass rate = 100%
- [ ] Evaluator trap fail rate = 100%
- [ ] Cost within cost_limits envelope
- [ ] Dashboard displays live data from baseline run

---

## Statistical Rigor for Improve Verification

When comparing version A vs. B:

### Minimum Sample Sizes

| Context | Recommendation |
|---------|----------------|
| Deterministic evaluators | 1 fixture sufficient per condition |
| LLM stochastic workers | ≥30 runs per fixture for means; report CI |
| Rare events (safety) | Aggregate over time; use exact counts |

### Comparison Methods

- **Paired fixtures:** Same input, A then B (or parallel if non-interfering).
- **Bootstrap CI:** For small samples, bootstrap primary metric difference.
- **Sequential testing:** Avoid peeking without correction; pre-register iteration budget.

### Regression Detection

Define ε (epsilon) per metric in LSS or team policy:

```yaml
metrics:
  - name: primary_quality
    target: 0.85
    regression_threshold: 0.03  # alert if drops >3 points from baseline
```

Alert when `baseline_mean - rolling_7d_mean > regression_threshold`.

---

## Dashboard Structure

### Panel 1: Loop Health

- Primary metric (rolling avg + baseline line)
- Success termination rate
- Active iterations / stalls

### Panel 2: Cost

- USD per iteration (stacked by worker)
- Cumulative vs. cost_limits
- Token volume trends

### Panel 3: Safety

- Triggers by constraint_id
- Near-misses (soft warnings)
- Halt events timeline

### Panel 4: Evaluators

- Score distributions per dimension
- Inter-evaluator disagreement
- Golden/trap calibration status (last run)

### Panel 5: Workers

- Latency p50/p95 by worker_id
- Retry rate
- Tool invocation counts

---

## Measurement Checklist

### Instrumentation

- [ ] Correlation ID spans workers, evaluators, tools
- [ ] All LSS `metrics` have collection implementation
- [ ] Logs exportable to analysis backend (not trapped in chat UI)
- [ ] cost_usd computed with documented price table per model

### Baseline

- [ ] Fixture set committed to repo
- [ ] Baseline report archived with run_id
- [ ] regression_threshold configured per metric

### Evaluator Calibration

- [ ] Golden suite passes 100%
- [ ] Trap suite fails 100% with expected failure_codes
- [ ] Calibration schedule defined (weekly minimum for LLM judges)

### Guardrails

- [ ] cost_limits tested (simulate approach to cap)
- [ ] safety_constraints tested on adversarial fixtures
- [ ] termination_conditions verified (max_iterations, stall)

### Production

- [ ] Dashboards live
- [ ] Alerts wired to regression_threshold and safety
- [ ] Weekly review ritual scheduled

---

## Best Practices

### Measure Before Optimizing

No Improve-phase prompt changes without a baseline reference. The baseline report is the contract that proves improvement.

### Fixture Hygiene

Fixtures are code. Review them when objectives change. Stale fixtures that no longer represent the objective create false confidence.

### Separate Evaluator Health from Worker Quality

If golden evaluators fail, **stop measuring worker quality** until evaluators are fixed. Otherwise you optimize against a broken ruler.

### Cost Attribution Granularity

Attribute spend to `worker_id` and `tool_name`. Aggregate loop cost alone cannot diagnose COST PATH failures.

### Document Metric Definitions

```yaml
metrics:
  - name: citation_validity
    definition: "Fraction of citations where URL resolves HTTP 200 and quoted text appears in fetched body"
    source: evaluator.citation_check
    unit: ratio
    target: 0.95
    regression_threshold: 0.05
```

---

## Anti-Patterns

| Anti-pattern | Consequence | Fix |
|--------------|-------------|-----|
| **Vanity metrics** | High scores, no user value | Tie to objective consumer |
| **Single-number worship** | Optimizer games one dimension | Multi-dimensional rubrics |
| **No baseline file** | "Improved" without proof | Archive baseline reports |
| **Production-only measurement** | No reproducibility | Fixture suite in CI |
| **Ignoring variance** | Chase noise | Report std, use CIs |
| **Stale calibration** | Drift undetected | Scheduled golden/trap runs |

---

## Handoff

| Measurement outcome | Next phase |
|-------------------|------------|
| Baseline accepted; gap to target | **Improve** |
| Baseline accepted; target met | **Scale** (or operate) |
| Instrumentation gaps | Remain in **Measure** |
| Evaluator calibration failed | **Design** or **Diagnose** |
| Safety/cost guardrails failed in baseline | **Design** |

Measurement artifacts: baseline report, dashboard links, fixture manifest, calibration log.
