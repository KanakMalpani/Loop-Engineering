# Lemma 2: Parallel and nested composition cost bounds

**Status:** Draft (informal). Extends [Lemma 1](./composition-cost-bound.md).

---

## Lemma 2a — Parallel composition

Let branches \(L_1, \ldots, L_k\) run concurrently with declared caps \(C_1, \ldots, C_k\). For **parallel** composition \(L = L_1 \parallel \cdots \parallel L_k\) with orchestrator cost \(C_o\):

\[
C(L) \;\leq\; C_o + \sum_{i=1}^{k} C_i
\]

Wall-clock time is \(\max_i T(L_i)\) (not summed); **spend** sums because branches execute concurrently on independent budgets.

### Assumptions

1. Branches do not share a single undeclared token pool (each child has `cost_limits`).
2. Merge/orchestrator runs after branch completion (cost \(C_o\) additive).
3. Failed branches still incur spend up to their local cap or early \(\tau\).

### LSS implication

```yaml
cost_limits:
  cumulative_usd: <C_o + sum(child cumulative_usd)>
```

Example: [scenario-swarm-rehearsal.yaml](../loop-library/compositions/scenario-swarm-rehearsal.yaml) — three branches + orchestrator.

---

## Lemma 2b — Nested composition

Let outer loop \(L_{\text{outer}}\) invoke inner loop \(L_{\text{inner}}\) up to \(R\) times per outer iteration (retry / repair nest). With outer cap \(C_{\text{out}}\), inner cap \(C_{\text{in}}\) **per invocation**:

\[
C(L) \;\leq\; C_{\text{out}} + R \cdot C_{\text{in}}
\]

If outer runs at most \(I\) macro-iterations:

\[
C(L) \;\leq\; I \cdot (C_{\text{out,iter}} + R \cdot C_{\text{in}})
\]

where \(C_{\text{out,iter}}\) is outer spend excluding inner invocations.

### Assumptions

1. Inner loop resets or sub-accounts spend per invocation (telemetry tags `child_id`).
2. \(R\) is declared in `termination_conditions.max_iterations` or adapter `trigger` policy.
3. No unbounded inner recursion without Level 5 governance.

### LSS implication

Parent nested specs should declare:

```yaml
cost_limits:
  cumulative_usd: <outer cap + max_inner_invocations * inner cap>
```

Example: [code-debug-repair.yaml](../loop-library/compositions/code-debug-repair.yaml).

---

## Proof sketch

**Parallel:** Branch spends are independent random variables capped by \(C_i\); total spend is sum of branch totals plus orchestrator. **Nested:** Each outer step invokes inner at most \(R\) times; multiply inner cap by invocation count; sum over outer iterations.

---

## Validator link

[composition_validator.py](../tools/composition_validator.py) warns on adapter gaps; parent `cost_limits` should be checked against these sums in CI (future: `tools/composition_cost_check.py`).

See [loop-composition-algebra.md](../research/loop-composition-algebra.md) · LE-OP-10.
