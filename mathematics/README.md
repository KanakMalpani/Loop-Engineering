# Mathematics of Loop Engineering

Formal foundations for Loop Engineering — definitions, notation, and proof targets that complement [fundamentals/](../fundamentals/) (intuition) and [research/](../research/) (open problems).

**Status:** Seed directory (2026-06). Not yet peer-reviewed.

---

## Why this exists

Disciplines gain credibility when claims are **falsifiable**. Loop Engineering already has:

- Informal algebra — [research/loop-composition-algebra.md](../research/loop-composition-algebra.md)
- Convergence prose — [fundamentals/07-convergence.md](../fundamentals/07-convergence.md)
- Heuristic complexity — [tools/loop_complexity_analyzer.py](../tools/loop_complexity_analyzer.py)

This directory will consolidate **normative mathematical definitions** as they stabilize.

---

## Core tuple (reference)

A loop instance is treated as:

\[
L = (S, A, O, T, E, M, \tau)
\]

| Symbol | LSS field | Meaning |
|--------|-----------|---------|
| \(S\) | state / memory | Information carried across iterations |
| \(A\) | workers | Actors that transform state |
| \(O\) | evaluators | Oracles producing feedback |
| \(T\) | termination_conditions | Stop rules (success, failure, stall) |
| \(E\) | feedback_channels | Routing from \(O\) to \(A\) |
| \(M\) | metrics | Scalar summaries for \(O\) and telemetry |
| \(\tau\) | cost_limits + safety | Budget and constraint envelope |

Case studies should map explicitly to this tuple (see [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md)).

---

## Roadmap (proof targets)

| Topic | Doc / tool | Target artifact |
|-------|------------|-----------------|
| **Composition algebra** | [loop-composition-algebra.md](../research/loop-composition-algebra.md) | Associativity conditions (LE-OP-10) |
| **Stability** | fundamentals/07 + P3 | Lyapunov non-increasing criterion |
| **Complexity** | loop_complexity_analyzer | \(O(\cdot)\) bounds vs worker/evaluator count |
| **Convergence** | open-problems LE-OP-03 | Expected iterations to \(\tau\) success |
| **LES composition** | LES-1.0 | Is LES(\(L_1 \to L_2\)) a function of LES(\(L_1\)), LES(\(L_2\))? |

---

## Composition operators (working notation)

From the algebra draft:

| Operator | Notation | LSS 1.1 `composition.type` |
|----------|----------|----------------------------|
| Sequential | \(L_1 \to L_2\) | `sequential` |
| Parallel | \(L_1 \parallel L_2 \parallel \cdots\) | `parallel` |
| Nest | \(L_{\text{outer}}[L_{\text{inner}}]\) | `nested` |
| Repeat | \(L^*\) | (future: `repeat` block) |

Implemented examples: [loop-library/compositions/](../loop-library/compositions/).

---

## How to contribute

1. Propose a definition or lemma in a PR under `mathematics/`
2. Link to an LE-OP entry in [open-problems.md](../research/open-problems.md)
3. Add a validator warning or test when the math implies a checkable invariant

See [contributions/CONTRIBUTING.md](../contributions/CONTRIBUTING.md) and [All about loops/MASTER_CHECKLIST.md](../All%20about%20loops/MASTER_CHECKLIST.md) Part C.1.

---

## Non-goals (for now)

- Full category-theoretic formalization
- Machine-checked proofs (Coq/Lean) — stretch 2028+
- Replacing LSS YAML with a theorem prover input format
