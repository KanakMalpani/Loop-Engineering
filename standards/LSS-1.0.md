# Loop Specification Standard (LSS) 1.0

> **Canonical spec:** [Loop Core Engineering — LSS 1.0](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.md) · Schema: [`lss-1.0.schema.json`](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.schema.json)  
> This document is a **narrative mirror**. For validation and semver, use the GitHub repo.

LSS 1.0 is the canonical machine- and human-readable format for specifying autonomous agent loops. A conforming document answers: what the loop optimizes, who does the work, who judges quality, how feedback flows, when execution stops, and what must never happen.

LSS documents are YAML or JSON files validated against the [canonical schema](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.schema.json) (local mirror: [./schema/lss-1.0.schema.json](./schema/lss-1.0.schema.json) — see [schema/README.md](./schema/README.md)).

---

## Design Principles

1. **Completeness** — Thirteen top-level fields; no implicit defaults that hide risk.
2. **Boundedness** — Every loop must terminate via `termination_conditions` or `cost_limits`.
3. **Safety-first** — `safety_constraints` are evaluated before trusting outputs.
4. **Observability** — `metrics` tie to evaluators and logs, not aspirations.
5. **Version discipline** — `version` semver; changes are auditable.

---

## Document Structure

```yaml
loop_name: string          # required
version: string            # required, semver
objective: string          # required
inputs: object             # required
memory: object             # required
workers: array             # required, min 1
evaluators: array          # required, min 1
feedback_channels: array   # required, min 1
optimization_strategy: object  # required
termination_conditions: object # required
metrics: array             # required, min 1
safety_constraints: array  # required for production
cost_limits: object        # required
```

---

## Field Reference

### `loop_name`

**Type:** string (kebab-case recommended)

**Purpose:** Stable identifier across versions. Used in logs, dashboards, and scale manifests.

**Rules:**
- Immutable across versions of the same logical loop
- Unique within an organization
- Pattern: `^[a-z][a-z0-9-]*$`

**Example:** `research-brief-loop`

---

### `version`

**Type:** string (semver)

**Purpose:** Track evolution of worker contracts, evaluators, and safety rules.

**Rules:**
- Follow semver 2.0.0: MAJOR.MINOR.PATCH
- MAJOR: breaking output schema or safety contract
- MINOR: new worker/evaluator, structural change
- PATCH: prompt tweak, threshold adjustment

**Example:** `1.4.2`

---

### `objective`

**Type:** string

**Purpose:** Single declarative statement of outcome, constraints, and consumer.

**Rules:**
- One paragraph maximum
- Must be judgeable by `metrics` and `evaluators`
- Should state failure semantics at high level

**Example:**

> Produce an 800–1200 word research brief answering inputs.query with ≥3 primary sources, weighted rubric score ≥0.85, zero safety constraint violations, terminating within cost_limits.

---

### `inputs`

**Type:** object with `schema` and optional `examples`

**Purpose:** Define variable data per loop invocation.

**Schema entry format:**

```yaml
inputs:
  schema:
    query:
      type: string
      required: true
      max_length: 2000
      description: "Research question"
    depth:
      type: enum
      values: [quick, standard, deep]
      default: standard
    locale:
      type: string
      pattern: "^[a-z]{2}(-[A-Z]{2})?$"
      default: en
  examples:
    - query: "What are solid-state battery commercialization timelines?"
      depth: standard
```

**Supported types:** `string`, `number`, `boolean`, `enum`, `array`, `object`

**Rules:**
- Every field has `type` and `description`
- Secrets never appear in examples
- Validation runs before workers start

---

### `memory`

**Type:** object

**Purpose:** Persist state within or across iterations.

```yaml
memory:
  type: session | ephemeral | persistent
  backend: null | redis | postgres | vector | composite
  retention:
    unit: iteration | hour | day
    value: number
  write_policy:
    allowed_writers: [worker_id, optimizer]
    schema: MemoryEntry
    max_entries: 100
  read_policy:
    researcher: [notes, prior_sources]
    writer: [notes, outline]
```

**Types:**
- `ephemeral` — Cleared each iteration
- `session` — Persists until termination
- `persistent` — Survives across loop invocations (requires backend)

**Rules:**
- `write_policy.allowed_writers` default deny
- PII-sensitive loops require `redaction` block per safety-standard

---

### `workers`

**Type:** array of worker objects (min 1)

**Purpose:** Agents or processes that produce artifacts.

```yaml
workers:
  - id: researcher
    role: "Gather and summarize primary sources"
    model:
      provider: openai
      name: gpt-4.1
      temperature: 0.3
    depends_on: []           # worker ids
    inputs:
      - from: inputs.query
      - from: memory.notes
    outputs:
      name: ResearchNotes
      format: json
      schema_ref: schemas/research-notes.json
    tools:
      - web_search
      - fetch_url
    timeout_seconds: 120
    retries: 1
    cost_budget_usd: 0.50
```

**Required fields per worker:** `id`, `role`, `model`, `inputs`, `outputs`

**Optional:** `depends_on`, `tools`, `timeout_seconds`, `retries`, `cost_budget_usd`

**Rules:**
- `id` unique within loop
- `depends_on` must form DAG (no cycles)
- Tools not listed are forbidden

---

### `evaluators`

**Type:** array of evaluator objects (min 1)

**Purpose:** Judge worker outputs against rubrics or ground truth.

```yaml
evaluators:
  - id: quality_rubric
    type: llm_rubric | deterministic | human
    runs_after: [writer]
    rubric:
      dimensions:
        - name: accuracy
          weight: 0.4
          scale: [0, 1]
          criteria: "Claims supported by sources"
        - name: coverage
          weight: 0.3
          scale: [0, 1]
          criteria: "All aspects of query addressed"
        - name: clarity
          weight: 0.3
          scale: [0, 1]
          criteria: "Readable by technical PM"
      pass_threshold: 0.75
    model:
      provider: openai
      name: gpt-4.1
      temperature: 0
  - id: link_check
    type: deterministic
    runs_after: [writer]
    implementation: evaluators.link_check
```

**Required fields:** `id`, `type`, `runs_after`

**Types:**
- `deterministic` — Code, schema, tests (preferred when ground truth exists)
- `llm_rubric` — Structured judge with weighted dimensions
- `human` — Async human review; requires SLA in `timeout_seconds`

**Rules:**
- `runs_after` references worker ids or `*` for all
- Multiple evaluators: document aggregation (min, weighted avg, veto)

---

### `feedback_channels`

**Type:** array of channel objects (min 1)

**Purpose:** Route evaluator output to workers or optimizer.

```yaml
feedback_channels:
  - id: quality_to_writer
    source: evaluators.quality_rubric
    destination: workers.writer
    format: structured
    fields: [failure_codes, dimension_scores, remediation_hints]
    max_tokens: 500
  - id: quality_to_optimizer
    source: evaluators.quality_rubric
    destination: optimization_strategy
    format: structured
    when: score < pass_threshold
```

**Required fields:** `id`, `source`, `destination`, `format`

**Formats:** `structured` (JSON), `template` (mustache), `human_queue`

**Rules:**
- `max_tokens` prevents feedback bloat
- `when` optional condition expression

---

### `optimization_strategy`

**Type:** object

**Purpose:** How the loop improves across iterations.

```yaml
optimization_strategy:
  type: prompt_refinement | parameter_search | memory_update | structural | manual
  max_steps: 10
  config:
    refinement_target: workers.writer
    preserve_sections: [safety_rules, output_schema]
  rollback:
    on_metric_drop: 0.03
    on_safety_failure: true
```

**Types:**
- `prompt_refinement` — Patch prompts from feedback
- `parameter_search` — Search declared parameters
- `memory_update` — Add examples/summaries to memory
- `structural` — Change worker topology (requires human approval gate)
- `manual` — Human applies changes; loop pauses

**Required:** `type`, `max_steps`

---

### `termination_conditions`

**Type:** object

**Purpose:** Define success, failure, and stall stopping rules.

```yaml
termination_conditions:
  success:
    - metric: primary_quality
      operator: gte
      value: 0.85
      consecutive: 2
  failure:
    - type: safety_violation
      action: halt
    - type: max_iterations
      value: 20
    - type: evaluator_error
      consecutive: 3
      action: halt
  stall:
    - metric: primary_quality
      window_iterations: 5
      min_improvement: 0.02
      action: halt
```

**Operators:** `gte`, `lte`, `eq`, `gt`, `lt`

**Actions:** `halt`, `escalate_human`, `retry_iteration`

**Rules:**
- At least one of success, failure, or budget termination must exist
- `max_iterations` strongly recommended

---

### `metrics`

**Type:** array (min 1)

**Purpose:** Quantitative loop health and success measures.

```yaml
metrics:
  - name: primary_quality
    primary: true
    definition: "Weighted mean of quality_rubric dimensions"
    source: evaluators.quality_rubric
    unit: ratio
    target: 0.85
    regression_threshold: 0.03
  - name: cost_usd
    definition: "Sum of worker and evaluator API cost"
    source: telemetry.cost
    unit: usd
    target: 2.00
```

**Required per metric:** `name`, `definition`, `source`, `unit`

**Optional:** `primary`, `target`, `regression_threshold`

**Rules:**
- Exactly one metric should have `primary: true`
- `regression_threshold` enables alerts

---

### `safety_constraints`

**Type:** array

**Purpose:** Hard invariants enforced before outputs propagate.

See [safety-standard.md](./safety-standard.md) for constraint types.

```yaml
safety_constraints:
  - id: no-pii-output
    type: pii_detect
    scope: post_worker
    applies_to: [writer]
    action: halt
    config:
      categories: [email, phone, ssn]
  - id: prompt-injection-guard
    type: injection_detect
    scope: pre_worker
    applies_to: [researcher, writer]
    action: quarantine
```

**Required per constraint:** `id`, `type`, `scope`, `action`

**Production rule:** Must be non-empty for production deployment.

---

### `cost_limits`

**Type:** object

**Purpose:** Financial and token budgets.

```yaml
cost_limits:
  per_iteration_usd: 1.00
  cumulative_usd: 5.00
  token_soft_cap: 50000
  on_approach:
    threshold_percent: 80
    action: warn
  on_exceed:
    action: halt
  price_table_ref: standards/price-tables/openai-2026-06.json
```

**Required:** `per_iteration_usd`, `cumulative_usd`, `on_exceed`

**Rules:**
- `on_exceed.action` should be `halt` in production
- Per-worker `cost_budget_usd` sums must not exceed cumulative without justification

---

## Validation

### Schema Validation

```bash
# Using ajv or equivalent
ajv validate -s standards/schema/lss-1.0.schema.json -d my-loop.yaml
```

### Semantic Validation (recommended)

Beyond JSON Schema:

| Check | Rule |
|-------|------|
| DAG | `workers.depends_on` acyclic |
| References | `feedback_channels.source` exists |
| Metric linkage | `primary` metric source exists |
| Safety coverage | `applies_to` workers exist |
| Termination | `max_iterations` or equivalent present |

---

## Examples

| Example | Path | Description |
|---------|------|-------------|
| Minimal | [minimal-loop.yaml](./examples/minimal-loop.yaml) | Smallest valid loop |
| Research | [research-loop.yaml](./examples/research-loop.yaml) | Full research pipeline |
| Multi-agent | [multi-agent-loop.yaml](./examples/multi-agent-loop.yaml) | DAG workers + consensus |

---

## Versioning and Migration

### 1.0.0 Scope

LSS 1.0 defines the thirteen fields above. Extensions use `x_` prefixed keys ignored by strict validators or nested under `extensions` object if schema allows.

### Breaking Changes (future 2.0)

Reserved: evaluator aggregation enum, first-class `human_gates`, standardized `failure_codes` enum in schema.

### Migration Checklist

1. Bump `version` semver
2. Re-validate schema
3. Run fixture regression
4. Update scale manifest overrides
5. Document in CHANGELOG

---

## Conformance Levels

| Level | Requirements |
|-------|--------------|
| **LSS-Parseable** | Schema valid |
| **LSS-Operational** | + metrics collection + cost_limits enforced |
| **LSS-Production** | + non-empty safety_constraints + evaluator calibration + runbook |

Loops must declare conformance target in deployment metadata.

---

## Relationship to D-D-M-I-S

| Field | Primary phase |
|-------|---------------|
| loop_name, version, objective | Design |
| inputs, workers, memory | Design |
| evaluators, feedback_channels | Design, Improve |
| optimization_strategy | Design, Improve |
| termination_conditions | Design |
| metrics | Measure |
| safety_constraints | Design, Diagnose |
| cost_limits | Design, Measure, Scale |

---

## Glossary

| Term | Definition |
|------|------------|
| **Iteration** | One worker→evaluator→feedback cycle |
| **Fixture** | Frozen input for testing |
| **Trap fixture** | Input/output designed to fail evaluators |
| **Override** | Scale-time patch to base LSS |
| **Halt** | Immediate loop stop; no further worker calls |
