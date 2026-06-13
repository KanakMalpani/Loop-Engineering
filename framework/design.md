# Design Phase

The Design phase converts an intent ("build a research agent") into a versioned, validatable Loop Specification (LSS). Design is front-loaded: decisions made here determine 80% of operational pain. A well-designed loop fails loudly and cheaply; a poorly designed loop fails silently and expensively.

---

## Design Objectives

By the end of Design, you must be able to answer:

1. What is the loop's **objective**, stated in measurable terms?
2. What **inputs** vary per run, and what is fixed?
3. Which **workers** produce artifacts, and what are their contracts?
4. Which **evaluators** judge quality, with what rubrics and thresholds?
5. How does **feedback** route from evaluators to workers or optimization?
6. What **optimization strategy** adjusts behavior across iterations?
7. When does the loop **terminate**—success, failure, or budget exhaustion?
8. Which **metrics** prove the loop works?
9. What **safety constraints** are hard invariants?
10. What **cost limits** bound spend per iteration and cumulatively?

If any answer is "TBD," the loop is not ready to run in production.

---

## Decision Tree: Loop Topology

Start here when choosing worker and evaluator architecture.

```
START: What is the primary output type?
│
├─ Single artifact (report, patch, answer)
│   ├─ Quality verifiable automatically?
│   │   ├─ YES → 1 worker + 1+ automated evaluators
│   │   └─ NO  → 1 worker + human-in-loop evaluator + automated pre-checks
│   └─ Output decomposable into subtasks?
│       ├─ YES → Consider multi-worker pipeline (sequential)
│       └─ NO  → Single worker with rich context in memory
│
├─ Multiple artifacts with dependencies
│   ├─ Dependencies strict (DAG)?
│   │   └─ YES → Multi-worker DAG; evaluators per stage + final integrator evaluator
│   └─ Dependencies loose (parallel exploration)?
│       └─ Parallel workers + merge worker + consensus evaluator
│
└─ Ongoing monitoring / recurring task
    ├─ State accumulates across runs?
    │   └─ YES → External memory (vector store, DB) + idempotent workers
    └─ Each run independent?
        └─ Ephemeral memory; focus on cost_limits and termination_conditions
```

### Decision Tree: Evaluator Selection

```
START: What evidence do you have of correctness?
│
├─ Ground truth available (tests, labels, golden files)
│   └─ Use deterministic evaluators (pass/fail, diff, schema validation)
│
├─ Ground truth partial (rubrics, reference docs)
│   └─ Hybrid: deterministic pre-checks + LLM-as-judge with structured rubric
│
├─ No ground truth (subjective quality)
│   ├─ Low stakes → LLM-as-judge + spot human audit (sampling rate in metrics)
│   └─ High stakes → Human evaluator required; automate only formatting/safety checks
│
└─ Safety-critical domain
    └─ Mandatory: safety_constraints enforced BEFORE quality evaluators run
```

### Decision Tree: Memory Architecture

```
START: What must persist across iterations?
│
├─ Nothing (stateless)
│   └─ memory: { type: ephemeral, scope: iteration }
│
├─ Within single loop run only
│   └─ memory: { type: session, retention: until termination }
│
├─ Across runs (learning, cache, user context)
│   ├─ Structured facts → key-value or document store
│   ├─ Unstructured retrieval → vector store with explicit write policy
│   └─ Audit trail → append-only log (never overwrite)
│
└─ Multi-agent shared state
    └─ Partitioned memory per worker + shared "blackboard" with conflict resolution rules
```

### Decision Tree: Optimization Strategy

```
START: What changes between iterations?
│
├─ Worker prompt / instructions only
│   └─ optimization_strategy: prompt_refinement (evaluator feedback → prompt patch)
│
├─ Tool selection or parameters
│   └─ optimization_strategy: parameter_search (bounded grid or bandit)
│
├─ Worker topology (add/remove/reorder)
│   └─ optimization_strategy: structural (requires human approval gate in safety_constraints)
│
├─ External knowledge (RAG corpus, examples)
│   └─ optimization_strategy: memory_update (write to memory per policy)
│
└─ No automatic optimization (human operates loop)
    └─ optimization_strategy: manual (feedback_channels → human only)
```

---

## Design Checklist

### Objective Definition

- [ ] Objective is a single declarative sentence, not a task list
- [ ] Objective maps to at least one primary metric with target threshold
- [ ] Objective explicitly states what is out of scope
- [ ] Objective names the consumer of the loop output (human, system, downstream loop)
- [ ] Success and failure are distinguishable without human judgment (or human path is specified)

### Inputs

- [ ] Every input has a name, type, and validation rule
- [ ] Required vs. optional inputs are documented
- [ ] Input bounds defined (max size, allowed values, sanitization)
- [ ] Secrets referenced by name, never embedded in LSS
- [ ] Example input fixtures exist for CI validation

### Workers

- [ ] Each worker has unique `id`, `role`, and `model` (or execution backend)
- [ ] Input contract: what each worker reads from inputs/memory/previous workers
- [ ] Output contract: schema or format specification
- [ ] Timeout and retry policy per worker
- [ ] Workers are idempotent where retries are possible
- [ ] Tool access explicitly listed; default-deny for undeclared tools

### Evaluators

- [ ] At least one evaluator for primary quality metric
- [ ] Evaluators run after relevant worker(s), order documented
- [ ] Rubric is structured (scores, dimensions, pass threshold)
- [ ] Evaluator failures (timeout, parse error) have defined behavior
- [ ] LLM-as-judge evaluators use temperature 0 or equivalent for reproducibility
- [ ] Evaluator disagreement strategy defined when multiple evaluators exist

### Feedback Channels

- [ ] Each channel maps evaluator output to a destination (worker, optimizer, human)
- [ ] Feedback format is structured (not freeform prose-only)
- [ ] Rate limits on feedback volume to prevent prompt bloat
- [ ] Negative feedback triggers specific worker revision, not global reset

### Optimization Strategy

- [ ] Strategy type declared and matches loop topology
- [ ] Maximum optimization steps bounded (pairs with termination_conditions)
- [ ] Rollback behavior defined when optimization degrades metrics
- [ ] Human approval gates for structural or high-risk changes

### Termination Conditions

- [ ] Success termination: metric thresholds met
- [ ] Failure termination: max iterations, repeated evaluator failure, safety violation
- [ ] Budget termination: cost_limits exhausted
- [ ] Stall detection: no metric improvement for K iterations
- [ ] Partial success handling documented

### Metrics

- [ ] Primary metric named with unit and target
- [ ] Secondary metrics for latency, cost, safety triggers
- [ ] Collection method specified (log scrape, evaluator score, external probe)
- [ ] Baseline measurement plan referenced (→ measure.md)

### Safety Constraints

- [ ] All constraints use enforceable types (see safety-standard.md)
- [ ] Pre-execution checks vs. post-execution checks distinguished
- [ ] Violation action: halt, quarantine, alert—specified per constraint
- [ ] Constraints tested with adversarial inputs

### Cost Limits

- [ ] Per-iteration token/currency cap
- [ ] Cumulative cap for loop run
- [ ] Per-worker budget allocation (optional but recommended for multi-agent)
- [ ] Behavior when limit approached (warn vs. hard stop)

---

## Design Criteria (Quality Bar)

| Criterion | Pass | Fail |
|-----------|------|------|
| **Completeness** | All 13 LSS fields populated with non-placeholder values | Any field missing or "TBD" |
| **Testability** | Evaluators runnable on fixtures without live workers | Evaluators require production-only context |
| **Boundedness** | termination_conditions + cost_limits guarantee finite runs | Loop can run indefinitely |
| **Observability** | Every worker/evaluator emits structured logs with correlation ID | Outputs only in unstructured chat |
| **Safety-first ordering** | safety_constraints evaluated before expensive workers | Safety checks after full generation |
| **Version discipline** | `version` semver; changes bump version | Undocumented live edits |

---

## Best Practices

### Objective Writing

Write objectives as **outcome + constraint + consumer**:

> "Produce a cited research brief of 800–1200 words answering `input.query`, with ≥3 primary sources, readable by a technical PM in <10 minutes, failing if any safety_constraint triggers."

Avoid:

> "Do good research on the topic."

### Worker Decomposition

Apply **single responsibility** per worker. A worker that researches, writes, and self-edits in one pass is harder to evaluate and optimize than three workers with clear contracts. The integration cost of multi-worker designs is paid back in diagnosability.

### Evaluator Rubrics

Rubrics should be **dimensional** (accuracy, completeness, citation validity) with weights summing to 1.0. Single scalar "quality 1–10" scores are not actionable for optimization.

Example rubric structure:

```yaml
dimensions:
  - name: factual_accuracy
    weight: 0.4
    scale: [0, 1]
    criteria: "Claims supported by cited sources; no contradictions."
  - name: coverage
    weight: 0.3
    scale: [0, 1]
    criteria: "Addresses all sub-questions in input.query."
  - name: citation_validity
    weight: 0.3
    scale: [0, 1]
    criteria: "URLs resolve; quotes match source text."
pass_threshold: 0.75
```

### Memory Write Policy

Declare **who can write, what, and when**. Unrestricted worker memory writes cause evaluators to grade stale or poisoned context. Prefer append-only logs with explicit summarization workers.

### Feedback Minimization

Route only **actionable** feedback to workers. Evaluator output should include `failure_codes` (from failure taxonomy) and `remediation_hints`, not full rewrites of the artifact.

### Design for Diagnosis

Include `correlation_id` in every log line. Tag worker outputs with `worker_id` and `iteration`. When something fails at iteration 47, you need to diff against iteration 46, not re-read 47 pages of logs.

---

## Anti-Patterns

| Anti-pattern | Symptom | Remediation |
|--------------|---------|-------------|
| **God worker** | One prompt does everything; evaluators can't localize faults | Split into pipeline workers |
| **Rubber-stamp evaluator** | Evaluator always passes; metric never moves | Add deterministic checks; calibrate on failures |
| **Prompt warehouse** | 400-line system prompt; no modular memory | Externalize reference docs to memory; slim prompts |
| **Implicit termination** | Loop runs until operator Ctrl+C | Add max_iterations and cost_limits |
| **Feedback firehose** | Full artifact pasted into next worker prompt | Structured delta feedback only |
| **Version zero forever** | `version: 0.1.0` after 50 production changes | Bump version on every evaluator/worker contract change |
| **Safety prose** | "Be careful with PII" in prompt, no constraint | Add `safety_constraints` with enforceable rules |
| **Metric mirage** | Optimizing proxy metric that doesn't correlate with objective | Validate proxy against human sample periodically |

---

## Design Phase Workflow

```
1. Draft objective + consumer story
2. Walk topology decision trees
3. Sketch worker DAG (boxes and arrows, even on paper)
4. Define evaluators and rubrics BEFORE worker prompts
5. Specify safety_constraints and cost_limits (non-negotiable bounds)
6. Write LSS YAML
7. Validate against lss-1.0.schema.json
8. Run dry evaluation: evaluators on golden + adversarial fixtures (workers mocked)
9. Design phase gate: dd-mis-checklists.md § Design
10. Hand off to Measure for baseline (or limited pilot if exploratory)
```

---

## Templates

### Minimal Worker Contract

```yaml
workers:
  - id: researcher
    role: "Gather sources and extract claims relevant to input.query"
    model: "gpt-4.1"
    inputs:
      - from: inputs.query
      - from: memory.prior_research  # optional
    outputs:
      schema: ResearchNotes
      fields: [claims, sources, gaps]
    timeout_seconds: 120
    retries: 1
    tools: [web_search, fetch_url]
```

### Termination Block Template

```yaml
termination_conditions:
  success:
    - metric: primary_quality
      operator: gte
      value: 0.85
      consecutive: 2
  failure:
    - condition: safety_violation
      action: halt
    - condition: max_iterations
      value: 20
    - condition: metric_stall
      metric: primary_quality
      window: 5
      min_delta: 0.02
  budget:
    - cost_limits.cumulative_usd
```

---

## Handoff to Next Phase

| Outcome | Next phase |
|---------|------------|
| LSS valid; fixtures pass dry eval | **Measure** (baseline) |
| Exploratory / high uncertainty | **Measure** with limited pilot (bounded cost_limits) |
| Design gate failed | Remain in **Design**; do not run production iterations |

Design artifacts must be committed to version control before baseline measurement begins. Undocumented loops are not engineered loops.
