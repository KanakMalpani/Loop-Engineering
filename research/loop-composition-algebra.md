# Loop Composition Algebra

*Formal operators for combining loops*

Individual loops are specified in LSS. Production systems require **composition**: sequential pipelines, parallel exploration, nested meta-loops, and conditional branching. This document proposes a minimal algebra for composing loops with predictable τ and E behavior.

---

## Primitives

Let Lᵢ be loops with specs spec(Lᵢ). Define:

| Operator | Notation | Semantics |
|----------|----------|-----------|
| Sequential | L₁ → L₂ | Output of L₁ feeds input of L₂; τ = τ₁ ∧ τ₂ |
| Parallel | L₁ ∥ L₂ | Independent runs; merge at join evaluator |
| Choice | L₁ + L₂ | Router selects branch by predicate on S |
| Nest | L₁[L₂] | L₂ runs inside worker policy of L₁ (meta) |
| Repeat | L* | Repeat L until τ or budget (Kleene-style) |

---

## Typing Rules (Informal)

**Input compatibility:** out(L₁) must satisfy inputs(L₂) for L₁ → L₂.

**Evaluator lift:** parallel merge requires evaluator E_merge with access to all branch artifacts.

**Safety compose:** safety(L₁ → L₂) = safety(L₁) ∪ safety(L₂) ∪ transfer constraints.

**Cost compose:** cost(L₁ → L₂) ≤ cost(L₁) + cost(L₂) (cumulative caps in parent spec).

---

## Example: Research → Verification

```
L_research → L_verification
```

- L_research produces patch candidate
- L_verification runs tests; τ_v failure may trigger L_research with diagnostic feedback

LSS: parent spec references child loop_name in `patterns` and `metadata.composes`.

---

## Example: Parallel Workers

```
(L_a ∥ L_b ∥ L_c) → L_merge
```

- Orchestrator dispatches three actor workers
- L_merge integrator + consensus evaluator

See [standards/examples/multi-agent-loop.yaml](../standards/examples/multi-agent-loop.yaml).

---

## Open Problems

1. **Semantic equivalence** — when are two compositions observationally equivalent?
2. **Optimal τ** — minimize expected cost subject to Effectiveness ≥ θ
3. **Safety monotonicity** — does composition preserve safety constraint satisfaction?
4. **LES of compositions** — is LES(L₁ → L₂) a function of LES(L₁), LES(L₂)?

---

## Tooling

- `tools/loop_comparison.py` — diff composed vs atomic specs
- `tools/loop_complexity_analyzer.py` — complexity grows with composition depth
- Future: composition validator in LSS schema 1.1

Status: **research draft** — partial closure in [le-op-10-associativity.md](le-op-10-associativity.md).
