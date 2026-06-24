# Lemma 1: Sequential composition cost bound

**Status:** Draft (informal). First entry in the mathematics proof roadmap.

---

## Statement

Let \(L_1\) and \(L_2\) be loops with cumulative cost caps \(C_1\) and \(C_2\) declared in LSS `cost_limits.cumulative_usd`. For a **sequential** composition \(L = L_1 \to L_2\) with adapter glue and no shared retry budget:

\[
C(L) \;\leq\; C_1 + C_2
\]

Observed spend satisfies the same bound when child loops halt on their own `on_exceed` policies.

---

## Assumptions

1. Children run at most once per parent macro-iteration (sequential, not nested retry).
2. Parent orchestrator cost \(C_o\) is declared separately; total \(C(L) \leq C_o + C_1 + C_2\).
3. No cross-child token reuse that bypasses telemetry (shared cache excluded).

---

## Proof sketch

Each child loop terminates only when its local cost envelope is respected or success/failure \(\tau\) fires. Sequential execution does not increase either child's per-run cap. Summing independent caps upper-bounds total spend. Parent orchestrator adds \(C_o\) additively.

---

## LSS implication

Parent composed specs should set:

```yaml
cost_limits:
  cumulative_usd: <sum of child caps + orchestrator budget>
```

Example: [research-to-writing.yaml](../loop-library/compositions/research-to-writing.yaml) declares cumulative_usd ≥ research + writing child budgets.

---

## Open extension (LE-OP-10)

Nested and parallel compositions need separate lemmas (inner retry may multiply cost; parallel runs sum branch spend concurrently).

See [loop-composition-algebra.md](../research/loop-composition-algebra.md).
