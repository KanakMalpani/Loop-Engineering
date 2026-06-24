# LE-OP-04 — Evaluator Composition Without Double-Counting (Partial Closure)

**Status:** Partial guidance (June 2026)  
**Related:** [loop-composition-algebra.md](loop-composition-algebra.md) · [Lemma 2](../mathematics/composition-cost-parallel-nested.md) · [LE-OP-10](le-op-10-associativity.md) · RFC [#11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11)

---

## Problem

Production loops stack evaluators: unit tests + linter + LLM rubric + human spot-check. Overlapping evaluators can **double-count** the same quality dimension in termination signals, causing false pass or false continue.

---

## Composition rules (v0.1 guidance)

### 1. Partition dimensions

Each evaluator should own **disjoint rubric dimensions** when composed in parallel merge:

| Evaluator role | Owns dimension | Do not also score |
|----------------|----------------|-------------------|
| `syntax_gate` | parse/build success | logical correctness |
| `test_gate` | behavioral correctness | style |
| `llm_rubric` | synthesis quality | raw pass/fail of tests |
| `human_spot` | policy / safety edge cases | token cost |

Reference: [scenario-swarm-rehearsal.yaml](../loop-library/compositions/scenario-swarm-rehearsal.yaml) uses a **single** parent `composite_gate` after merge — branch loops should not each re-run full composite rubrics.

### 2. Merge strategies vs. evaluator stacking

| Pattern | Safe composition | Risk |
|---------|------------------|------|
| **Parallel branches** | Branch-local evaluators + one parent synthesizer evaluator | Re-scoring branch outputs in parent *and* branches |
| **Sequential stages** | Stage evaluators gate handoff only | Propagating raw scores into next stage threshold |
| **Logical AND gates** | Independent dimensions (tests AND lint) | Correlated signals (lint + formatter on same AST) |
| **Weighted average** | Normalized weights sum to 1.0 on disjoint dims | Same dim in two weights |

### 3. No double-counting LES dimensions

When computing structural LES for composed loops:

- Count branch evaluators **once per branch** (Lemma 2 parallel bound).
- Count parent merge evaluator **additively**, not multiplied by branch count.
- Use [loop_complexity_analyzer.py](../tools/loop_complexity_analyzer.py) `--json` on composed specs for token bounds.

```bash
python tools/loop_complexity_analyzer.py loop-library/compositions/scenario-swarm-rehearsal.yaml --json
```

### 4. Termination signal algebra (informal)

Let \(E_1, \ldots, E_n\) be evaluators with dimension sets \(D_i\).

**Valid parallel merge termination:**

\[
\tau_{\text{pass}} \Leftrightarrow E_{\text{merge}}(\text{merge}(b_1,\ldots,b_k)) \geq \theta
\]

where branch evaluators \(E_j\) only gate **local** branch success, not global composite.

**Invalid (double-count):**

\[
\tau_{\text{pass}} \Leftrightarrow \Big(\prod_i score(E_i)\Big) \geq \theta \;\;\text{when}\;\; D_i \cap D_j \neq \emptyset
\]

---

## Worked example: scenario-swarm-rehearsal

1. **Branches** (`falsifier`, `evidence`, `operator`) each run local worker + optional branch rubric inside child specs.
2. **Parent** `orchestrator` synthesizes; **only** `composite_gate` sets `composite_quality` for τ.
3. `merge.preserve_dissent: true` ensures minority branch evaluators are not overwritten by majority vote.

Validator: `python tools/composition_validator.py loop-library/compositions/scenario-swarm-rehearsal.yaml --strict`

---

## Resolution criteria (full LE-OP-04)

- [x] Document partition + merge rules (this file)
- [x] Reference composed spec + validator strict mode
- [ ] Correlation model + benchmark on `benchmarks/evaluator-composition/` (future)

Update [open-problems.md](open-problems.md) LE-OP-04 partial progress to link here.

---

## See also

- [human-in-the-loop.md](../patterns/human-in-the-loop.md) — oracle stacking
- [multi-agent-coordination.md](../patterns/multi-agent-coordination.md) — merge policies
- [BEAT_LB-COMP-1.md](../contributions/BEAT_LB-COMP-1.md) — composed LoopBench path
