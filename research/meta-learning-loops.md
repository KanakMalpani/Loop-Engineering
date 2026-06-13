# Meta-Learning Loops

*Loops that learn how to loop*

Meta-learning—learning to learn—is traditionally framed in machine learning as few-shot adaptation or hyperparameter optimization over training episodes. In Loop Engineering, **meta-learning loops** are Level 4–6 systems where the object of improvement is not task output alone but **loop policy**: prompts, tool selection, evaluator ordering, memory write rules, worker topology, or the LSS specification itself.

This document defines meta-learning loops precisely, catalogs mechanisms, analyzes failure modes, and connects to open problems and patterns.

---

## Definition

A **base loop** L solves task instances drawn from domain D:

```
L = (S, A, O, T, E, M, τ)   →   artifact + LES profile
```

A **meta-learning loop** M(L) operates on a distribution of base loops or episodes:

```
M = (S_meta, A_meta, O_meta, T_meta, E_meta, M_meta, τ_meta)
```

where:

- **S_meta** includes loop specs, telemetry histories, LES vectors, and domain descriptors
- **A_meta** modifies elements of L (not merely actions within L's task environment)
- **E_meta** judges loop performance—typically multi-dimensional LES, not single-task reward
- **τ_meta** fires when meta-metric converges, charter budget exhausts, or stability violation detected

**Key distinction.** Level 2 reflection revises *outputs within an iteration*. Meta-learning revises *the loop that produces outputs* across episodes.

---

## Taxonomy Placement

| Mechanism | Taxonomy level | Modifies |
|-----------|----------------|----------|
| In-context few-shot | 2 (weak meta) | Ephemeral prompt prefix only |
| Session summarization → next session | 2–3 | Procedural memory M |
| Prompt / skill evolution | 4 | Population of prompts or skills |
| DSPy-style compile | 4–5 | Fixed program from examples |
| Hook / policy rewrite | 5 | Transition T or action space A |
| LSS spec synthesis | 5–6 | Full loop tuple |
| Meta-loop over meta-loops | 6 | M itself |

Loop Engineering treats **in-context learning without persistent M update** as weak meta—useful but not durable meta-learning.

---

## Mechanisms in Depth

### 1. Episodic Transfer (Cross-Session Memory)

After base loop terminates, a **consolidation phase** extracts:

- Failed action sequences to avoid (procedural negatives)
- Evaluator-confirmed facts (semantic positives)
- Tool latency and reliability stats (procedural metrics)

Consolidation is itself a small loop with E = "human or strong model confirms extract is valid."

**When it works.** Repeated task families (same repo, same API, same org process).

**When it fails.** Overfitting to session noise; polluting semantic memory with wrong "facts" (LE-OP-07, LE-OP-09).

**LSS pattern.**

```yaml
meta:
  type: episodic_transfer
  trigger: on_termination
  memory_targets: [procedural, semantic]
  evaluator:
    type: consolidation_judge
    threshold: 0.85
```

---

### 2. Compilation from Examples

Given input–output (or input–trace–output) examples, a **compiler loop** searches over prompt/program space to minimize loss on held-out examples while respecting budget and safety constraints.

DSPy, textgrad, and evolutionary prompt optimizers instantiate this pattern.

**Loop structure.**

```
Generate candidate LSS variant → Run on train episodes → Score → Mutate → Repeat
```

**Engineering insight.** Compilation is a **Level 4 outer loop** around a **Level 1–2 inner loop**. The inner loop must be fast enough for thousands of compile iterations.

**Risk.** Compile-time overfit to train evaluators that don't generalize (LE-OP-18). Mitigation: holdout evaluators, adversarial checks, promotion gate.

---

### 3. Online Adaptation (Within Deployment)

Base loop policy updates **during production** based on streaming telemetry:

- Reorder tools by success rate
- Drop workers that correlate with failures
- Tighten τ when error rate spikes

This blurs Level 5 self-modification with standard ML online learning.

**Safety requirement.** Online Δpolicy must lie in **bounded modification set** (LE-OP-14): e.g., reorder only, no new tools, no charter edits.

**Stability requirement.** Track **base metric vs. meta metric** coupling (LE-OP-13); rollback on regression.

---

### 4. Hyper-Loop Search

For a task class, search over **loop topology**:

- Serial vs. parallel workers
- Presence/absence of critic
- Evaluator strictness tiers

Search methods: grid, Bayesian optimization, evolutionary strategies.

**Output.** Recommended level and pattern from taxonomy (addresses LE-OP-11).

**Cost.** Expensive; amortize over many task instances. Cache results in loop registry tagged by task features.

---

## Meta-Evaluator Design

E_meta is the crux. Poor E_meta teaches wrong lessons.

### Recommended: LES vector + constraints

Score each episode with LES dimensions. Meta-selection uses:

- **Pareto dominance** across episodes (avoid scalar gaming)
- **Hard constraints**: Safety ≥ threshold, Robustness ≥ threshold
- **Charter violations**: instant disqualification

### Anti-patterns

| Bad E_meta | Failure mode |
|------------|--------------|
| Single scalar reward | Goodhart; collapse to cheap hacks |
| Self-report success | Meta-loop learns to lie |
| Train evaluator only | Overfit; production surprise |
| Ignoring cost | Unbounded token burn |

### Charter-aligned E_meta

Organizational meta-loops add **charter dimensions**: compliance pass, audit trail completeness, human escalation rate within band.

---

## Stability Analysis

Meta-loops can **oscillate**: prompt v12 beats v11 on Speed, hurts Effectiveness; v13 reverts; endless churn.

**Stabilizers.**

1. **Meta learning rate** — cap Δ per meta-iteration (max edit distance on LSS)
2. **Champion–challenger** — challenger must dominate on Pareto front for N episodes before promotion
3. **Cooldown** — no policy change for M base episodes after promotion
4. **Dual tracking** — plot task metric and meta metric on same dashboard

**Open problem.** LE-OP-13 seeks formal stability conditions analogous to control theory gain margins.

---

## Relationship to Machine Learning Meta-Learning

| ML meta-learning | Loop Engineering meta-learning |
|------------------|--------------------------------|
| Gradient updates on weights | Updates on LSS, prompts, tools, memory |
| Episode = dataset batch | Episode = full loop run to τ |
| Loss on labels | LES vector + charter |
| Generalization across tasks | Generalization across loop specs |
| Black box | Declarative, auditable specs |

They compose: a base loop may use a fine-tuned model **inside** A while meta-loop optimizes everything **outside** weights.

---

## Reference Patterns

| Pattern | Location | Meta mechanism |
|---------|----------|----------------|
| Reflection + skill file | patterns/reflection-gate | Procedural memory append |
| Evolutionary prompt | patterns/population-search | Level 4 outer loop |
| Maker-checker compile | patterns/maker-checker | E_meta = human merge |
| Benchmark-driven tuning | benchmarks/README | E_meta = suite LES |

---

## Research Agenda

1. **LMIF** — standard interchange for cross-session procedural memory (LE-OP-09)
2. **Compile-from-intent** — NL → LSS with bounded search (LE-OP-15)
3. **Stability proofs** for champion–challenger under noisy LES (LE-OP-13)
4. **Task→level classifier** reducing wasted Level 4 search (LE-OP-11)

---

## Practitioner Checklist

Before deploying a meta-learning loop:

- [ ] E_meta uses multi-dimensional LES, not one number
- [ ] Modification set is explicitly bounded and typed
- [ ] Rollback snapshot before every ΔLSS
- [ ] Holdout evaluators distinct from training E
- [ ] Charter constraints are non-writable by meta-loop
- [ ] Telemetry links meta-iterations to base-iteration outcomes
- [ ] Human promotion gate for production deployment

---

## Further Reading

- [recursive-self-improvement.md](./recursive-self-improvement.md) — Level 5–6 limits
- [loop-composition-algebra.md](./loop-composition-algebra.md) — composing meta and base loops
- [future-agent-architectures.md](./future-agent-architectures.md) — Architecture 5 and 6
- [open-problems.md](./open-problems.md) — LE-OP-09, 11, 13, 14, 15

---

<p align="center"><em>Meta-learning is not magic—it is an outer loop with a better evaluator.</em></p>
