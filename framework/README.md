# Loop Engineering Framework: D-D-M-I-S

Loop Engineering is a disciplined methodology for building, operating, and evolving autonomous agent loops—recurring systems where workers produce outputs, evaluators judge quality, and feedback channels drive optimization until termination conditions are met. The framework is organized around five phases that form a continuous cycle: **Design → Diagnose → Measure → Improve → Scale** (D-D-M-I-S).

Unlike one-shot prompt engineering, loop engineering treats the loop itself as the primary artifact. The loop specification (LSS) is versioned, testable, and observable. Each phase produces durable artifacts that constrain the next phase, preventing the common failure mode where teams scale broken loops because they never diagnosed root causes or defined measurable success.

---

## Why Loops, Not Prompts

A prompt answers a single question. A loop answers a class of questions under uncertainty, with memory, cost bounds, and safety constraints. Production agent systems—research pipelines, code review harnesses, multi-agent orchestration—are loops whether or not they are documented as such. D-D-M-I-S makes implicit loop structure explicit so teams can reason about failure, cost, and improvement systematically.

| One-shot prompt | Engineered loop |
|-----------------|-----------------|
| Success = readable output | Success = metric thresholds + safety invariants |
| Failure = retry manually | Failure = classified, routed, bounded |
| Cost = unknown until bill arrives | Cost = budgeted per iteration and cumulative |
| Improvement = tweak wording | Improvement = optimization strategy with evaluators |
| Scale = copy-paste to more tasks | Scale = parameterized inputs + shared evaluators |

---

## The Five Phases

```
                    ┌─────────────┐
                    │   DESIGN    │
                    │  (specify)  │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │       DIAGNOSE          │
              │  (when things break)    │
              └────────────┬────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │              MEASURE               │
         │     (instrument & baseline)        │
         └─────────────────┬─────────────────┘
                           │
              ┌────────────▼────────────┐
              │       IMPROVE         │
              │  (close the gap)      │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │        SCALE          │
              │  (replicate safely)   │
              └────────────┬────────────┘
                           │
                           └──────► back to DESIGN (next version)
```

### Design

Define what the loop must accomplish before writing worker prompts. Outputs include an LSS document, evaluator rubrics, safety constraints, cost limits, and termination conditions. Design is where most downstream failures are prevented.

**Primary question:** *What does "done" mean, and what must never happen?*

→ See [design.md](./design.md)

### Diagnose

When a loop misbehaves—silent degradation, runaway cost, safety violations, or evaluator drift—diagnosis classifies the failure using the [failure taxonomy](../standards/failure-taxonomy.md), traces causality across workers/evaluators/memory, and produces a bounded remediation plan. Diagnosis is reactive but structured; it is not debugging by intuition.

**Primary question:** *Which subsystem failed, and is this a new failure mode or a regression?*

→ See [diagnose.md](./diagnose.md)

### Measure

Instrument the loop so improvement decisions are evidence-based. Establish baselines for quality metrics, latency, token spend, evaluator agreement, and safety trigger rates. Measurement distinguishes signal from noise before optimization changes are applied.

**Primary question:** *Are we improving the right variable, and is the delta real?*

→ See [measure.md](./measure.md)

### Improve

Apply targeted changes to workers, evaluators, memory schema, feedback routing, or optimization strategy. Improvements are hypothesis-driven: each change maps to a metric, has a rollback condition, and respects safety constraints as hard invariants.

**Primary question:** *What is the smallest change that moves the primary metric without violating safety?*

→ See [improve.md](./improve.md)

### Scale

Replicate a proven loop to new objectives, inputs, or deployment contexts without re-learning failure modes. Scaling introduces parameterization, shared evaluator libraries, cost envelopes per tenant, and operational runbooks—not simply running more iterations.

**Primary question:** *What transfers unchanged, and what must be re-designed per context?*

→ See [scale.md](./scale.md)

---

## Relationship to LSS (Loop Specification Standard)

Every engineered loop should be expressible as an LSS 1.0 document. The standard defines thirteen top-level fields:

| Field | Phase emphasis |
|-------|----------------|
| `loop_name`, `version` | Design |
| `objective` | Design |
| `inputs` | Design, Scale |
| `memory` | Design, Improve |
| `workers` | Design, Improve |
| `evaluators` | Design, Measure, Improve |
| `feedback_channels` | Design, Diagnose |
| `optimization_strategy` | Design, Improve |
| `termination_conditions` | Design, Measure |
| `metrics` | Measure |
| `safety_constraints` | Design (see [safety-standard](../standards/safety-standard.md)) |
| `cost_limits` | Design, Measure, Scale |

Full specification: [LSS-1.0.md](../standards/LSS-1.0.md)

JSON Schema: [lss-1.0.schema.json](../standards/schema/lss-1.0.schema.json)

---

## Entry Criteria and Exit Criteria by Phase

| Phase | Enter when | Exit when |
|-------|------------|-----------|
| **Design** | New loop or major version bump | LSS validates; evaluators have rubrics; safety + cost limits defined |
| **Diagnose** | Metric regression, incident, or anomaly | Failure classified; root cause bounded; remediation scoped |
| **Measure** | Post-design baseline needed, or post-change verification | Dashboards live; baselines recorded; evaluator calibration done |
| **Improve** | Measured gap vs. objective | Primary metric moved; no safety regression; change documented in version bump |
| **Scale** | Loop stable over N iterations (team-defined) | Parameterization documented; per-context overrides tested |

---

## Artifacts Produced

| Artifact | Owner phase | Persistence |
|----------|-------------|-------------|
| LSS YAML/JSON | Design | Version control |
| Evaluator rubrics | Design | Version control |
| Failure incident reports | Diagnose | Incident log |
| Metric baselines & dashboards | Measure | Observability backend |
| Change logs / version diffs | Improve | Git + LSS `version` |
| Scale playbooks | Scale | Runbooks directory |

---

## Anti-Patterns at the Framework Level

1. **Prompt-first design** — Writing worker prompts before defining objective, metrics, and termination conditions.
2. **Evaluator as afterthought** — Shipping workers without evaluators; "we'll know good output when we see it."
3. **Unbounded optimization** — Running improve cycles without cost_limits or max_iterations guardrails.
4. **Scaling before measuring** — Deploying the same loop to ten use cases without baseline on one.
5. **Safety as documentation** — Listing safety concerns in prose but omitting `safety_constraints` enforceable fields.
6. **Diagnosis by anecdote** — Fixing the last bad output instead of classifying failure mode and checking for regressions.

---

## Quick Start

1. Copy [minimal-loop.yaml](../standards/examples/minimal-loop.yaml) and adapt `objective`, `workers`, and `evaluators`.
2. Walk through [design.md](./design.md) decision trees for your use case.
3. Validate against [lss-1.0.schema.json](../standards/schema/lss-1.0.schema.json).
4. Run baseline measurement per [measure.md](./measure.md).
5. Use [dd-mis-checklists.md](./dd-mis-checklists.md) at each phase gate.

---

## Document Index

| Document | Purpose |
|----------|---------|
| [design.md](./design.md) | Decision trees, checklists, criteria for the Design phase |
| [diagnose.md](./diagnose.md) | Structured diagnosis when loops fail |
| [measure.md](./measure.md) | Instrumentation, baselines, statistical rigor |
| [improve.md](./improve.md) | Hypothesis-driven optimization |
| [scale.md](./scale.md) | Safe replication and parameterization |
| [dd-mis-checklists.md](./dd-mis-checklists.md) | Consolidated phase checklists |

| Standard | Purpose |
|----------|---------|
| [LSS-1.0.md](../standards/LSS-1.0.md) | Loop Specification Standard |
| [failure-taxonomy.md](../standards/failure-taxonomy.md) | Classified failure modes |
| [safety-standard.md](../standards/safety-standard.md) | Safety constraints as first-class citizens |
