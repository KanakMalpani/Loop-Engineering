# Loop ID Registry

**Version:** 1.0.0  
**Status:** Stable  
**Owner:** `01-loop-engineering-core`

Stable identifiers for patterns, failure modes, environment IDs, and cross-repo metric names. Downstream repos **must not** fork these slugs silently.

---

## 1. Pattern slugs

Kebab-case slugs matching the Loop Engineering pattern catalog. Use in LSS metadata (`extensions.pattern`), telemetry, and LoopNet records.

| Slug | Taxonomy level | Summary |
|------|----------------|---------|
| `reflection-loop` | L2 | Agent evaluates own output before commit |
| `critique-loop` | L2 | Dedicated critic gates generator output |
| `planning-loop` | L2 | Plan → validate → execute with replan |
| `verification-loop` | L2–L3 | Deterministic checks drive retry until pass |
| `research-loop` | L2 | Iterative gather → synthesize until coverage |
| `simulation-loop` | L2–L4 | Hypothesize → simulate → update belief |
| `debate-loop` | L3 | Adversarial agents; judge merges |
| `exploration-loop` | L4 | Branch search with backtracking / bandits |
| `optimization-loop` | L4 | Score candidates; keep best; mutate |
| `memory-augmented-loop` | L2–L5 | Read/write memory each iteration |
| `human-in-the-loop` | L1–L3 | Explicit human approval or edit gates |
| `safety-constrained-loop` | All | Policy envelope wraps inner loop |
| `multi-agent-coordination` | L3 | Orchestrator + specialists + merge |
| `recursive-improvement-loop` | L5–L6 | Bounded self-edits with convergence |

**Rules:**

- Slug = filename stem in pattern docs (no version suffix).
- Multiple patterns: ordered list, outermost first (e.g. `["safety-constrained-loop", "verification-loop"]`).

---

## 2. Failure taxonomy codes

Universal failure modes (levels 1–6). Use in evaluator feedback, LoopNet labels, and incident dashboards.

| Code | Slug | Name | Typical level |
|------|------|------|---------------|
| F1 | `fail.open_loop` | Open loop | L1 |
| F2 | `fail.self_grade` | Self-grade | L2–L3 |
| F3 | `fail.evaluator_drift` | Evaluator drift | L2–L4 |
| F4 | `fail.tau_omission` | τ omission (no termination/budget) | all |
| F5 | `fail.false_pass` | False pass | L2–L5 |
| F6 | `fail.false_fail` | False fail | L2–L5 |
| F7 | `fail.oscillation` | Oscillation without convergence | L2–L4 |
| F8 | `fail.resource_bleed` | Resource bleed past cost_limits | all |
| F9 | `fail.state_corruption` | Memory inconsistent across iterations | L2–L6 |
| F10 | `fail.orchestration_deadlock` | Multi-agent wait cycle | L3+ |
| F11 | `fail.meta_instability` | Self-modification degrades LES | L5–L6 |
| F12 | `fail.safety_bypass` | Safety constraint ignored | all |

**LSS feedback field:** emit slugs in `failure_codes` arrays on structured feedback channels.

**Detection signals:** see failure taxonomy in discipline repo (`Loop Engineering/standards/failure-taxonomy.md`).

---

## 3. Environment ID prefixes

Cross-repo environment and artifact IDs. Format: `{namespace}/{resource}-{version}`.

### 3.1 LoopGym (`lg`)

```
lg/{family}/{name}-v{major}
```

| Example | Description |
|---------|-------------|
| `lg/loopbench/code-repair-v1` | LoopBench code repair task env |
| `lg/loopbench/research-synthesis-v1` | Research synthesis task env |
| `lg/loopbench/multi-agent-debate-v1` | Multi-agent debate task env |
| `lg/replay/loopnet-v1` | Replay LoopNet trajectories |
| `lg/sim/mock-llm-v1` | SimEnv with mock LLM (no API keys) |

**Owner:** `05-loopgym`

### 3.2 LoopBench tasks (`lb`)

```
lb/{task_code}
```

| ID | Slug | Name |
|----|------|------|
| `LB-CR-1` | `lb/code-repair-1` | Code repair |
| `LB-RS-1` | `lb/research-synthesis-1` | Research synthesis |
| `LB-MA-1` | `lb/multi-agent-debate-1` | Multi-agent debate |

**Owner:** `06-loopbench`

### 3.3 LoopNet records (`ln`)

```
ln/record-v{major}
```

Schema version for LoopNet JSONL/Parquet records. **Owner:** `04-loopnet`

### 3.4 Loop Trace Format (`ltf`)

```
ltf/trace-v{major}
```

OpenTelemetry-compatible iteration spans. **Owner:** `07-loop-observability`

### 3.5 Spec pins

| Pin | Artifact |
|-----|----------|
| `lss@1.0.0` | [`lss-1.0.schema.json`](./lss-1.0.schema.json) |
| `les@1.0.0` | [`les-1.0.md`](./les-1.0.md) |

---

## 4. Standard metric names

LSS `metrics[].name` and telemetry should prefer these names for cross-repo dashboards.

| Name | Unit | Typical source |
|------|------|----------------|
| `primary_quality` | ratio | Primary evaluator rubric |
| `consensus_score` | ratio | Multi-agent merge evaluator |
| `test_pass_rate` | ratio | Deterministic test evaluator |
| `citation_validity` | ratio | Citation integrity check |
| `cost_usd` | usd | `telemetry.cost` |
| `iteration_latency` | seconds | `telemetry.latency` |
| `iteration_count` | count | `telemetry.iteration` |
| `token_count` | tokens | `telemetry.tokens` |
| `safety_trigger_rate` | count | `telemetry.safety` |
| `regression_count` | count | Derived from goal trace |

**Telemetry namespace:** `telemetry.{signal}` where signal matches `[a-z][a-z0-9_.-]*` per LSS schema.

---

## 5. Worker and evaluator ID rules

Defined in LSS schema:

- **Worker ID:** `^[a-z][a-z0-9_-]*$` (max 64 chars)
- **Evaluator ID:** same pattern
- **Feedback source:** `evaluators.{id}` or `workers.{id}`
- **Metric source:** `evaluators.{id}`, `workers.{id}`, or `telemetry.{signal}`

---

## 6. Versioning

Additions to this registry are **MINOR** semver changes. Renaming or removing a slug is **MAJOR**. See [CHANGELOG.md](../CHANGELOG.md).

Propose changes via [RFC template](../templates/rfc-template.md).
