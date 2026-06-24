# LE-OP-10 — Composition Associativity (Partial Closure)

**Status:** Partial resolution (June 2026)  
**Related:** [loop-composition-algebra.md](loop-composition-algebra.md) · [Lemma 1](../mathematics/composition-cost-bound.md) · [Lemma 2](../mathematics/composition-cost-parallel-nested.md) · LSS 1.1 `composition` blocks

---

## Claim

Composition operators in LSS 1.1 are **associative up to adapter equivalence** when state types align and merge policies are fixed.

---

## Conditions (sufficient)

| Operator | Associativity holds when |
|----------|-------------------------|
| **Sequential** `(L1 → L2) → L3` | Adapters connect `out(L1)→in(L2)` and `out(L2)→in(L3)`; no hidden side channels in S |
| **Parallel** `(L1 ∥ L2) ∥ L3` | Same `merge` strategy and independent branch state; join evaluator is commutative over branch order |
| **Nested** `L_outer[L_inner]` | Inner loop τ is independent of outer iteration index except via declared adapters |

---

## Counterexamples (non-associative)

1. **Sequential adapter mismatch** — `L1 → L2` passes `outputs.draft` but `(L1 → L2) → L3` expects `outputs.code`; reordering parentheses changes which adapter fires.
2. **Parallel merge order** — `merge.strategy: first_wins` with branch priority depends on child order; `(A ∥ B) ∥ C` ≠ `A ∥ (B ∥ C)` when ties differ.
3. **Nested budget bleed** — inner loop reads outer `step` from undeclared global S; nesting depth changes termination.

These are **validator warnings** in [composition_validator.py](../tools/composition_validator.py); **errors** with `--strict`.

---

## Tooling

```bash
python tools/composition_validator.py --library          # warn on adapter gaps
python tools/composition_validator.py --library --strict # fail on parallel merge / adapter gaps
```

Daily CI: [daily_checkin.yml](../.github/workflows/daily-checkin.yml) runs `--strict` on composed specs.

---

## Resolution criteria (full)

- [x] Document conditions + counterexamples (this file)
- [x] Machine-readable warnings in composition validator
- [ ] Formal proof catalog for typed state spaces (stretch, LE-OP-10 open)

Update [open-problems.md](open-problems.md) LE-OP-10 partial progress to link here.
