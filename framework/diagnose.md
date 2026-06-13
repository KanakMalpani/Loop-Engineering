# Diagnose Phase

The Diagnose phase activates when a loop exhibits unexpected behavior: metric regression, safety violations, cost overruns, evaluator drift, or operator-reported "something feels wrong." Diagnosis is structured forensic work—not tweaking the last bad output. The goal is a **classified failure**, a **bounded root cause**, and a **scoped remediation plan** that feeds Improve without contaminating unrelated subsystems.

---

## When to Enter Diagnose

| Trigger | Urgency | Typical entry signal |
|---------|---------|---------------------|
| Safety constraint violation | Immediate | `safety_violation` halt; alert fired |
| Primary metric regression > ε | High | Dashboard threshold breach |
| Cost anomaly | High | 2× expected spend per iteration |
| Evaluator disagreement spike | Medium | Inter-evaluator variance exceeds baseline |
| Stall detected | Medium | termination_conditions.metric_stall would fire |
| Human escalation | Variable | Qualitative failure reports |
| Post-incident review | Scheduled | Weekly/monthly loop health review |

**Do not diagnose during active safety incidents without first halting the loop.** Preserve artifacts (logs, memory snapshots, last worker outputs) before remediation.

---

## Diagnosis Decision Tree

```
START: Is the loop still running?
│
├─ NO (halted)
│   └─ What halted it?
│       ├─ safety_constraints → Go to SAFETY PATH
│       ├─ cost_limits → Go to COST PATH
│       ├─ termination_conditions.failure → Go to QUALITY PATH
│       └─ infrastructure error → Go to INFRA PATH
│
└─ YES (degraded but running)
    └─ What degraded?
        ├─ metrics only → Go to QUALITY PATH
        ├─ cost only → Go to COST PATH
        ├─ latency only → Go to PERFORMANCE PATH
        └─ intermittent → Go to FLAKINESS PATH
```

### SAFETY PATH

```
1. Identify which safety_constraint triggered (id, type, evidence)
2. Determine exposure: did violating output leave the loop boundary?
3. Classify per failure-taxonomy.md (Safety class)
4. Trace: which worker produced violating content? Pre-checks skipped?
5. Check for prompt injection via inputs or retrieved memory
6. Remediation: patch constraint, worker, or input sanitization—NOT "add please be safe"
```

### QUALITY PATH

```
1. Pull last N iterations where primary metric dropped
2. Diff worker outputs iteration N vs N-1 (same input fixture if possible)
3. Evaluator calibration check: run evaluators on known golden set
4. Classify failure mode:
   ├─ Worker regression (model, prompt, tool change)
   ├─ Evaluator drift (judge model update, rubric ambiguity)
   ├─ Input distribution shift (new input types)
   ├─ Memory corruption (stale/poisoned context)
   └─ Optimization overshoot (prompt_refinement broke constraint)
5. Localize to subsystem using worker_id tags in logs
```

### COST PATH

```
1. Aggregate spend by worker_id and tool invocation
2. Compare to cost_limits and historical baseline
3. Classify:
   ├─ Retry storm (worker timeouts)
   ├─ Context bloat (memory/feedback growth)
   ├─ Tool loop (worker repeatedly calls expensive tool)
   ├─ Model routing error (premium model on trivial subtask)
   └─ Optimization runaway (too many iterations)
4. Check whether cost_limits fired correctly or were misconfigured
```

### PERFORMANCE PATH

```
1. Break down latency: queue, worker, evaluator, tool, memory I/O
2. Identify p95 vs p50 divergence (tail latency)
3. Classify: timeout too low, tool latency, evaluator parallelism missing, cold start
```

### FLAKINESS PATH

```
1. Re-run same input fixture 5× with fixed seed where possible
2. If variance high on deterministic evaluators → infrastructure bug
3. If variance only on LLM workers → temperature, model version, or ambiguous prompt
4. If variance only on LLM evaluators → rubric ambiguity; tighten criteria
```

### INFRA PATH

```
1. Correlate with deploys, model API outages, rate limits
2. Distinguish transient (retry succeeds) from structural (config error)
3. Do not optimize prompts for API 503 errors
```

---

## Diagnosis Checklist

### Evidence Preservation

- [ ] Loop halted or iteration frozen if safety-related
- [ ] Correlation IDs collected for failing iterations
- [ ] Worker outputs, evaluator scores, and memory state snapshotted
- [ ] Input payload preserved (redacted if sensitive)
- [ ] LSS `version` and git commit hash recorded
- [ ] Model versions and API endpoints logged

### Classification

- [ ] Failure assigned taxonomy code (see failure-taxonomy.md)
- [ ] Severity assigned: S0 (safety), S1 (production), S2 (degraded), S3 (cosmetic)
- [ ] Blast radius estimated: single iteration, single input class, all inputs
- [ ] Regression vs. novel failure mode determined (check git history, metric history)

### Root Cause Analysis

- [ ] Five-whys or equivalent completed without stopping at "model hallucinated"
- [ ] Subsystem localized: worker / evaluator / memory / optimizer / input / infra
- [ ] Contributing factors listed (not just proximate cause)
- [ ] Hypothesis stated in falsifiable form

### Remediation Scoping

- [ ] Fix scoped to smallest subsystem change
- [ ] Rollback plan documented if fix fails
- [ ] Safety constraints re-run on adversarial fixtures before resuming
- [ ] No simultaneous unrelated improvements (one hypothesis per change)

### Communication

- [ ] Incident report filed with timeline
- [ ] Stakeholders notified if S0/S1
- [ ] Known-good inputs added to regression fixture set

---

## Diagnostic Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| **Classified** | Taxonomy code assigned | "Bad output" without category |
| **Localized** | Named worker/evaluator/memory component | Whole loop blamed |
| **Reproducible** | Fails on ≥1 fixture, or statistical repro documented | Anecdote only |
| **Bounded** | Remediation plan < 1 page | "Redesign everything" |
| **Safe to resume** | Safety checks pass on patched path | Resume without verification |

---

## Instrumentation Requirements

Effective diagnosis depends on Design-phase observability. Minimum viable diagnostics:

```yaml
# Required log fields per iteration
iteration_id: uuid
loop_version: semver
worker_id: string
evaluator_id: string
tokens_in: integer
tokens_out: integer
latency_ms: integer
evaluator_scores: object
safety_checks: [{ constraint_id, passed, evidence }]
failure_codes: [string]  # from taxonomy
```

### Evaluator Self-Diagnostics

Run evaluators on **golden** (should pass) and **trap** (should fail) fixtures weekly. If golden fails, the evaluator is broken—not the workers.

| Fixture type | Purpose |
|--------------|---------|
| Golden | Known-good worker output; evaluator must pass |
| Trap | Known-bad output; evaluator must fail with correct failure_code |
| Edge | Boundary inputs; documents expected behavior |
| Adversarial | Injection, PII, policy stress; safety_constraints must halt |

---

## Common Failure Patterns and Signatures

| Signature | Likely cause | First check |
|-----------|--------------|-------------|
| Metric cliff after version bump | Worker or evaluator contract change | `git diff` on LSS version |
| Slow metric erosion | Memory bloat or rubric creep | Memory size over iterations; evaluator prompt |
| Cost linear with iterations but flat quality | Optimization not converging | feedback_channels routing; optimizer logs |
| Evaluator always ~0.7 | Rubric ceiling effect or judge laziness | Score distribution histogram |
| Worker succeeds, evaluator fails, loop retries forever | Threshold mismatch | pass_threshold vs. typical scores |
| Safety fires on benign inputs | Over-constrained regex or keyword list | Constraint test suite |
| Good on demo inputs, bad in production | Input distribution shift | Compare input schema stats |

---

## Anti-Patterns in Diagnosis

| Anti-pattern | Why it fails | Alternative |
|--------------|--------------|-------------|
| **Last-output fixation** | Fixes symptom, not system | Classify and localize |
| **Prompt thrash** | Multiple changes; can't attribute | One change per hypothesis |
| **Blame the model** | Hides contract/evaluator bugs | Check evaluators on fixtures first |
| **Skip safety on resume** | Reintroduces exposure | Re-run adversarial suite |
| **Undocumented incident** | Same failure recurs | Incident report + regression fixture |
| **Diagnose in production** | Amplifies blast radius | Reproduce in staging with frozen LSS |

---

## Incident Report Template

```markdown
## Incident: [loop_name] — [taxonomy code]

**Severity:** S0 | S1 | S2 | S3
**Detected:** [timestamp]
**LSS version:** [semver]
**Iterations affected:** [range or count]

### Summary
[One paragraph: what happened, user impact]

### Timeline
- [T0] ...
- [T1] ...

### Classification
- Taxonomy: [code]
- Subsystem: [worker/evaluator/memory/optimizer/input/infra]
- Regression: yes | no

### Root Cause
[Bounded statement]

### Remediation
- Immediate: [halt, rollback, hotfix]
- Follow-up: [LSS change, version bump, Improve phase ticket]

### Regression Fixtures Added
- [fixture_id]: [description]
```

---

## Handoff

| Diagnosis outcome | Next phase |
|-------------------|------------|
| Root cause requires LSS change | **Improve** (with Measure verification) |
| Misconfiguration only | **Improve** (patch + re-baseline) |
| Cannot reproduce | **Measure** (increase instrumentation) |
| Design flaw (missing evaluator, no bounds) | **Design** (version bump) |
| Scale-related (tenant-specific) | **Scale** (parameterization review) |

Diagnosis without a written incident report does not complete the Diagnose phase.
