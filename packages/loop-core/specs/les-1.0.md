# LES 1.0 — Loop Engineering Score

**Version:** 1.0.0  
**Status:** Stable  
**Effective:** 2026-06-13  
**Canonical home:** `01-loop-engineering-core` (this repo)

The Loop Engineering Score (LES) is a composite quality index for autonomous agent loops. It combines eight normalized category scores into a single value used by LoopBench, LoopNet, and observability tooling.

---

## Score scale (normative)

| Representation | Range | When to use |
|----------------|-------|-------------|
| **Normalized (canonical)** | `[0, 1]` | APIs, JSON schemas, cross-repo contracts, statistical aggregation |
| **Display** | `0–100` | Human reports, leaderboards, dashboards |

**Conversion:**

```
les_display = round(les_normalized × 100, 1)
les_normalized = les_display / 100
```

All formulas in this document produce **normalized** values in `[0, 1]`. Reporting precision: two decimal places for normalized (e.g. `0.82`), one decimal for display (e.g. `82.0`).

Category sub-scores (`N_effectiveness`, …) are always normalized `[0, 1]`.

---

## 1. Definitions

### 1.1 Loop instance

A **loop instance** is one complete Observe → Evaluate → Decide → Act cycle, indexed by `t ∈ {1, 2, …, T}` where `T` is iterations before termination.

### 1.2 Goal function

Each benchmark or case study defines a **goal function** `G(x)` mapping outcome state `x` to a quality score in `[0, 1]`.

### 1.3 Baselines

Each category uses baselines `B_floor` and `B_ceiling` for domain-relative normalization:

```
N(x) = clamp((x - B_floor) / (B_ceiling - B_floor), 0, 1)
```

Baselines are defined per benchmark suite (see `06-loopbench`) or documented for case studies.

---

## 2. Category formulas

Each category produces `N_cat ∈ [0, 1]`. Weights sum to `1.0`.

| Category | Weight | Question |
|----------|--------|----------|
| Effectiveness | 0.20 | Does the loop achieve the goal within budget? |
| Speed | 0.15 | How quickly does each iteration complete? |
| Cost | 0.12 | Resources per unit of goal progress? |
| Robustness | 0.13 | Performance under perturbation? |
| Scalability | 0.10 | Quality/cost at increased load? |
| Safety | 0.12 | Harmful or policy-violating outcomes prevented? |
| Adaptability | 0.10 | OOD inputs without manual reconfiguration? |
| Autonomy | 0.08 | Human intervention required? |

### 2.1 Effectiveness (w = 0.20)

```
E_raw = G_final / G_target                           if G_final ≥ G_target
E_raw = (G_final / G_target) × (T_budget / T_actual) if G_final < G_target and improving
E_raw = G_final / G_target × 0.5                     if G_final < G_target and not improving

N_effectiveness = N(E_raw)  with B_floor=0.5, B_ceiling=1.0
```

**Improving:** `G_t > G_{t-1}` for ≥60% of iterations in the final third of the run.

### 2.2 Speed (w = 0.15)

```
S_raw = 1 / (0.7 × τ_median + 0.3 × τ_p95)   [iterations per second]
N_speed = N(S_raw)  with domain-specific baselines
```

**Stall penalty:** if any iteration exceeds `3 × τ_median`, multiply `N_speed` by `0.85`.

Default LLM-agent baselines: `B_floor = 0.001`, `B_ceiling = 0.05` iter/s.

### 2.3 Cost (w = 0.12)

```
Cost_efficiency = ΔG / C_total    where ΔG = G_final - G_0
N_cost = N(Cost_efficiency)
```

If `ΔG ≤ 0`, then `N_cost = 0`. Marginal cost decrease in second half of run: `N_cost = min(N_cost × 1.05, 1.0)`.

### 2.4 Robustness (w = 0.13)

```
Degradation_p = 1 - (G_perturbed_p / G_clean)
Robustness_raw = 1 - (1/|P|) × Σ Degradation_p
Recovery_factor = 1 - (1/|P|) × Σ min(R_p / T_budget, 1)
R_composite = 0.6 × Robustness_raw + 0.4 × Recovery_factor
N_robustness = N(R_composite)  with B_floor=0.3, B_ceiling=0.95
```

Minimum 3 perturbations for a valid Robustness score.

### 2.5 Scalability (w = 0.10)

```
Scale_score(n) = 0.5 × Quality_retention(n) + 0.3 × Speed_retention(n) + 0.2 × min(Cost_retention(n), 1)
Scalability_raw = (1/3) × Σ Scale_score(n) for n ∈ {2, 4, 8}
N_scalability = N(Scalability_raw)  with B_floor=0.4, B_ceiling=0.90
```

### 2.6 Safety (w = 0.12)

```
Safety_raw = 1 - min(V_severity / (V_budget + 1), 1)
Intervention_bonus = min(H_events / T_actual, 0.1)
N_safety = clamp(Safety_raw + Intervention_bonus, 0, 1)
```

Any unrecoverable severe violation sets `N_safety = 0`.

### 2.7 Adaptability (w = 0.10)

```
Adaptability_raw = 0.7 × (G_ood / G_train) + 0.3 × (1 - min(Δ_config / 5, 1))
N_adaptability = N(Adaptability_raw)  with B_floor=0.2, B_ceiling=0.85
```

### 2.8 Autonomy (w = 0.08)

```
Intervention_rate = H_interventions / T_actual
Human_fraction = H_duration / τ_total
Autonomy_raw = (1 - min(Intervention_rate / 0.5, 1)) × (1 - min(Human_fraction / 0.3, 1))
N_autonomy = N(Autonomy_raw)  with B_floor=0.1, B_ceiling=0.95
```

Weighted intervention types: passive approval `0.5`, active correction `1.0`, parameter override `1.5`, full restart `2.0`, takeover `5.0`.

---

## 3. Composite score

```
LES = 0.20 × N_effectiveness
    + 0.15 × N_speed
    + 0.12 × N_cost
    + 0.13 × N_robustness
    + 0.10 × N_scalability
    + 0.12 × N_safety
    + 0.10 × N_adaptability
    + 0.08 × N_autonomy
```

**Range:** `[0, 1]` (canonical). Report category scores individually.

---

## 4. Diagnostics

| Diagnostic | Formula |
|------------|---------|
| Convergence rate | `(G_final - G_1) / (T_actual - 1)` |
| Iteration efficiency | `G_final / T_actual` |
| Cost per iteration | `C_total / T_actual` |
| Regression count | iterations where `G_t < G_{t-1}` |
| Termination reason | `goal_met`, `budget_exhausted`, `human_stop`, `error` |

---

## 5. Edge cases

- **Premature termination** (<2 iterations, error): multiply all categories except Safety by `0.5`.
- **Unbounded loops:** not valid LES subjects; declare `max_iterations` or equivalent first.
- **Missing perturbation data:** exclude Robustness and renormalize weights; report `LES-1.0 (partial, 7 categories)`.
- **Multi-objective goals:** scalarize `G_scalar = Σ (β_j × G_j)` with documented weights before scoring.

---

## 6. Reference implementation

See [`tools/les_calculator.py`](../tools/les_calculator.py).

- **Runtime scoring:** pass observed metrics; returns `les_normalized` and optional `les_display`.
- **Spec inference:** heuristic category scores from LSS structure (design-time estimate only; not a substitute for benchmark runs).

---

## 7. Cross-repo contracts

| Consumer | Uses LES for |
|----------|--------------|
| `04-loopnet` | `les_observed`, `les_predicted` fields on records |
| `06-loopbench` | Leaderboard composite and category breakdown |
| `07-loop-observability` | `loop.les.*` time-series attributes |

Pin this spec as `les@1.0.0` alongside `lss@1.0.0`.

---

## Changelog

| Version | Change |
|---------|--------|
| 1.0.0 | Canonical scale documented as `[0, 1]` with optional `0–100` display; consolidated from Loop Engineering `scoring/LES-1.0.md` |
