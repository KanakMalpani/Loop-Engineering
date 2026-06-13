# Recursive Self-Improvement

*Level 5–6 dynamics, safety envelopes, and convergence*

Recursive self-improvement (RSI) is the process by which a system improves its own ability to improve—closing a meta-meta feedback loop. In Loop Engineering terms, RSI occurs when **loops modify loops that modify loops**, with measurable effects on LES dimensions over time.

This document is not a manifesto for unconstrained superintelligence. It is an **engineering analysis** of what RSI means within the loop tuple formalism, what has been demonstrated, what fails in practice, and what safety envelopes are necessary before escalation across taxonomy levels.

---

## Formal Stack

Define improvement operator **I** that maps loop spec L to L' such that expected LES improves on domain D:

```
I: L → L'    where    E[L'] > E[L]   (under E_meta)
```

**First-order improvement:** L' = I(L) — self-modifying loop (Level 5).

**Second-order improvement:** I' = J(I) — meta-loop improves the improvement policy (Level 6).

**Recursive depth k:** I_k = I(I_{k-1}(…I(L)…))

RSI claims exist when **k is unbounded** and **expected LES grows without ceiling** under fixed external resources. Loop Engineering treats unbounded RSI as a **hypothesis requiring containment**, not a deployment default.

---

## What RSI Is Not

| Misconception | Correction |
|---------------|------------|
| Smarter model weights | Weight change is ML training, not loop RSI unless training loop is explicit LSS |
| Longer autonomous run | Duration ≠ improvement depth; runaway loops don't RSI |
| Self-critique once | Level 2 reflection; single step of I |
| Prompt "make yourself better" | Unless change persists in M and passes E_meta, not RSI |
| Tool creation without audit | Capability expansion without bounded modification set |

RSI requires **persistent, evaluator-gated modification** of loop policy with **measurable LES delta** across meta-iterations.

---

## Demonstrated Regimes (2024–2026)

These are **partial, bounded** RSI instances—real but narrow:

### Prompt and program evolution (Level 4–5)

Evolutionary optimizers mutate prompts or small programs; selection uses task evaluators. The **population manager** is a crude I. Demonstrated on algorithm synthesis, prompt tuning, small code puzzles.

**Limit.** Search space and evaluator are fixed; no open-ended tool creation. Fitness plateaus (LE-OP-02).

### Compiler loops (DSPy-like)

Examples → compiled pipeline. I is compile pass; L' is frozen until recompile. Demonstrated on structured NLP tasks.

**Limit.** Recompile is episodic, not continuous; generalization gap on distribution shift.

### Coding agent with skill accumulation

Successful sessions append skills/hooks to M. Later sessions load improved procedural memory. Weak RSI if consolidation is evaluator-gated.

**Limit.** Memory pollution; skills don't rewrite core T; human often curates M.

### AlphaGo-style self-play (Level 4)

Policy improves against self-generated data. I is train-on-self-play; environment and reward fixed.

**Limit.** Closed game; not open-world tool RSI.

**Lesson.** Real systems achieve **shallow RSI depth** (k≤2 effectively) in narrow domains. Open-ended k→∞ remains theoretical.

---

## Failure Modes

### 1. Meta-metric / task-metric decoupling

Meta-loop optimizes compile speed; deployed quality drops. **Symptom:** LES Speed ↑, Effectiveness ↓ after promotion.

**Mitigation.** Pareto E_meta; champion–challenger; rollback.

### 2. Evaluator gaming (Goodhart cascade)

Each I iteration exploits holes in E. **Symptom:** High LES, human inspection fails.

**Mitigation.** Independent verification evaluators; adversarial benchmark (LE-OP-18).

### 3. Instability and oscillation

L' reverts improvements; churn without convergence. **Symptom:** Policy version thrash; no LES trend.

**Mitigation.** Meta learning rate; cooldown; LE-OP-13 research.

### 4. Capability overhang without safety

Autonomy dimension rises; Safety flat or falls. **Symptom:** New tools, broader A, same charter.

**Mitigation.** Modification lattice; Safety hard constraint in τ_meta.

### 5. Containment breach

Self-modification escapes sandbox—filesystem, network, privilege. **Symptom:** Audit log gaps; unapproved ΔA.

**Mitigation.** LE-OP-19 containment profile; fail closed.

---

## Safety Envelopes

Loop Engineering mandates **explicit envelopes** before Level 5–6 deployment:

### Bounded modification set Δ

Allowed changes typed as:

- `prompt_edit` (scope: named fields only)
- `tool_reorder`
- `evaluator_reorder`
- `memory_policy`
- `worker_topology`
- `forbidden`: `new_tool`, `code_exec`, `charter_edit`, `network`

Each type has max delta per meta-iteration (e.g., edit distance ≤ k, fan-out change ≤ 1).

### Charter layer (immutable to loop)

Human/org defined:

- Objective bounds
- Prohibited actions
- Data handling rules
- Kill switch predicate

Charter stored in M_charter; read-only to I for k≥1.

### Audit and rollback

Every I(L) produces:

- Diff of LSS
- LES before/after on shadow benchmark
- Signed promotion record (human or automated gate)

Rollback = restore LSS snapshot + M procedural state.

### Autonomy ceiling

LES Autonomy capped by tier:

| Tier | Max level | Max k | Human gate |
|------|-----------|-------|------------|
| Research sandbox | 6 | 3 | Every I |
| Staging | 5 | 2 | Promotion |
| Production | 4 | 1 | Compile-time only |
| Regulated | 3 | 0 | No RSI |

Escalation requires governance review ([GOVERNANCE.md](../contributions/GOVERNANCE.md)).

---

## Convergence Questions

Does RSI converge? Depends on definitions.

**State space view.** If LSS space is finite and E_meta is deterministic, greedy I eventually plateaus at local optimum—may not be global.

**Noisy E_meta.** Non-monotonic meta-objective; convergence in probability only with annealing-like I.

**Open-ended A.** If Δ can expand action space without bound, convergence is undefined—capability may grow indefinitely (AGI discourse territory).

Loop Engineering **research position:** treat convergence as **empirical per domain** until LE-OP-13 supplies theory. Do not assume global convergence; design for **detectable plateau and safe halt**.

---

## RSI and AGI

AGI is often linked to RSI. Loop Engineering reframes:

> AGI is not a model size threshold. It is **reliable, general-purpose loop closure**—the ability to instantiate appropriate L on novel domains with acceptable LES under charter.

RSI at Level 6 would be **AGI-relevant** only if:

1. I generalizes across D without human-authored LSS per domain
2. E_meta correlates with human intent on open-ended tasks
3. Safety dimensions scale with Autonomy
4. Containment holds under adversarial pressure

None are demonstrated at scale in 2026. See [agi-implications.md](./agi-implications.md).

---

## Experimental Protocol (Research Sandboxes)

Researchers proposing RSI experiments should publish:

1. **Initial LSS** and modification lattice Δ
2. **k max** and tier classification
3. **E_meta** definition (full LES vector)
4. **Shadow benchmarks** + holdout
5. **Containment architecture** (network, FS, privileges)
6. **Time series** of LES dimensions per meta-iteration
7. **Failure logs** including rollbacks

Benchmark target: `benchmarks/containment/` (LE-OP-19).

---

## Ethical and Governance Notes

RSI research carries **dual-use** risk: same mechanisms improve developer productivity and enable autonomous capability growth. Loop Engineering community norms:

- No undisclosed production RSI above tier limits
- Red-team gaming evaluators before claiming improvement
- Share containment profiles when sharing RSI results
- Prefer spec-level (LSS) transparency over weight-level opacity

---

## Summary Table

| Depth | Name | Modifies | Demonstrated? | Production-ready? |
|-------|------|----------|---------------|-------------------|
| k=0 | Base loop | Task state S | Yes | Yes (L1–3) |
| k=1 | Self-modify | L policy | Partial (L5) | Staging only |
| k=2 | Meta-meta | I policy | Rare (L6 lab) | No |
| k→∞ | Open RSI | Unbounded | No | No |

---

## Further Reading

- [meta-learning-loops.md](./meta-learning-loops.md) — mechanisms of I
- [agi-implications.md](./agi-implications.md) — strategic implications
- [open-problems.md](./open-problems.md) — LE-OP-13, 14, 19
- `taxonomy/level-5-self-modifying-loops.md`, `taxonomy/level-6-recursive-meta-loops.md`

---

<p align="center"><em>Recursive self-improvement is an engineering problem with a safety envelope, not a slogan.</em></p>
