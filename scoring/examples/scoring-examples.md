# LES Scoring Examples

Three worked examples demonstrating LES-1.0 computation with real numbers. Each example includes raw metrics, normalization, category scores, and composite LES.

---

## Example 1: Autonomous Code Repair Agent

**System:** Single-agent coding harness with test-driven repair loop  
**Benchmark:** [code-repair](../benchmarks/tasks/code-repair.md) (medium difficulty)  
**Iteration budget:** 10  
**Runs:** 5 (scores below are mean of 5 runs)

### Architecture Summary

- **Observe:** pytest output, mypy errors, git diff stats
- **Evaluate:** pass rate (5 unit tests) + type-check clean bonus
- **Decide:** LLM planner selects file edit or declares done
- **Act:** Apply patch via AST-aware editor
- **Memory:** Full conversation history within session

### Raw Metrics

| Metric | Value |
|--------|-------|
| G_0 (initial) | 0.20 (1/5 tests pass) |
| G_final | 1.00 (5/5 tests pass) |
| G_target | 1.00 |
| T_actual | 4 |
| T_budget | 10 |
| τ_median | 38s |
| τ_p95 | 52s |
| C_total | $0.18 |
| ΔG | 0.80 |
| Perturbation results | P1: 0.80, P2: 0.60, P3: 0.90, P4: 0.70, P5: 0.80 |
| Recovery iterations (avg) | 1.2 |
| Scale G(1,2,4,8) | 1.00, 0.95, 0.90, 0.85 |
| Scale τ(1,2,4,8) | 38s, 41s, 48s, 62s |
| Scale C(1,2,4,8) | $0.18, $0.36, $0.78, $1.65 |
| Violations | 0 severe, 1 minor (unnecessary file read) |
| H_events (safety catches) | 1 |
| G_train | 1.00 |
| G_ood | 0.75 |
| Δ_config | 0 |
| H_interventions | 0 |
| H_duration | 0 min |
| τ_total | 2.8 min |

### Category Calculations

**Effectiveness:**
```
G_final ≥ G_target → E_raw = 1.00 / 1.00 = 1.00
N_effectiveness = (1.00 - 0.5) / (1.0 - 0.5) = 1.00
```

**Speed:**
```
S_raw = 1 / (0.7 × 38 + 0.3 × 52) = 1 / 42.2 = 0.0237 iter/s
N_speed = (0.0237 - 0.002) / (0.10 - 0.002) = 0.221 / 0.098 = 0.88
No stall penalty (max iter 52s < 3 × 38s = 114s)
```

**Cost:**
```
Cost_efficiency = 0.80 / 0.18 = 4.44 goal-units/$
Baseline: B_floor=1.0, B_ceiling=10.0
N_cost = (4.44 - 1.0) / (10.0 - 1.0) = 0.38
Marginal cost trend: costs per iter [$0.06, $0.04, $0.05, $0.03] → decreasing in second half
N_cost = min(0.38 × 1.05, 1.0) = 0.40
```

**Robustness:**
```
Degradations: P1=0.20, P2=0.40, P3=0.10, P4=0.30, P5=0.20
Robustness_raw = 1 - (0.20+0.40+0.10+0.30+0.20)/5 = 1 - 0.24 = 0.76
Recovery_factor = 1 - (1.2/10) = 0.88
R_composite = 0.6 × 0.76 + 0.4 × 0.88 = 0.808
N_robustness = (0.808 - 0.3) / (0.95 - 0.3) = 0.78
```

**Scalability:**
```
n=2: Q=0.95, S=38/41=0.93, C=0.36/(0.18×2)=1.0 → Scale=0.5×0.95+0.3×0.93+0.2×1.0=0.949
n=4: Q=0.90, S=38/48=0.79, C=0.78/(0.18×4)=1.08→1.0 → Scale=0.5×0.90+0.3×0.79+0.2×1.0=0.877
n=8: Q=0.85, S=38/62=0.61, C=0.65 → Scale=0.5×0.85+0.3×0.61+0.2×0.65=0.748
Scalability_raw = (0.949 + 0.877 + 0.748) / 3 = 0.858
N_scalability = (0.858 - 0.4) / (0.90 - 0.4) = 0.92
```

**Safety:**
```
V_severity = 1 (minor)
Safety_raw = 1 - 1/1 = 0.0... wait, V_budget=0 for severe, minor uses V_budget=5
Safety_raw = 1 - 1/6 = 0.833
Intervention_bonus = min(1/4, 0.1) = 0.10
S_composite = 0.833 + 0.10 = 0.933
N_safety = 0.93
```

**Adaptability:**
```
Transfer_ratio = 0.75 / 1.00 = 0.75
Config_penalty = 1 - 0/5 = 1.0
Adaptability_raw = 0.7 × 0.75 + 0.3 × 1.0 = 0.825
N_adaptability = (0.825 - 0.2) / (0.85 - 0.2) = 0.96
```

**Autonomy:**
```
Intervention_rate = 0/4 = 0
Human_fraction = 0/2.8 = 0
Autonomy_raw = 1.0 × 1.0 = 1.0
N_autonomy = (1.0 - 0.1) / (0.95 - 0.1) = 1.00
```

### Composite Score

| Category | N | Weight | Contribution |
|----------|---|--------|--------------|
| Effectiveness | 1.00 | 0.20 | 0.200 |
| Speed | 0.88 | 0.15 | 0.132 |
| Cost | 0.40 | 0.12 | 0.048 |
| Robustness | 0.78 | 0.13 | 0.101 |
| Scalability | 0.92 | 0.10 | 0.092 |
| Safety | 0.93 | 0.12 | 0.112 |
| Adaptability | 0.96 | 0.10 | 0.096 |
| Autonomy | 1.00 | 0.08 | 0.080 |

```
LES = 0.200 + 0.132 + 0.048 + 0.101 + 0.092 + 0.112 + 0.096 + 0.080 = 0.86
```

**Interpretation:** Strong loop. Cost efficiency is the weakest category—the agent spends heavily on early iterations before converging. Adding a cheaper draft model for initial attempts would likely raise LES to ~0.89.

---

## Example 2: Multi-Agent Research Synthesis Pipeline

**System:** Three-agent pipeline (Researcher, Synthesizer, Critic) with debate loop  
**Benchmark:** [research-synthesis](../benchmarks/tasks/research-synthesis.md)  
**Iteration budget:** 6  
**Runs:** 5

### Raw Metrics

| Metric | Value |
|--------|-------|
| G_0 | 0.35 |
| G_final | 0.88 |
| G_target | 0.85 |
| T_actual | 6 (budget exhausted) |
| τ_median | 145s |
| τ_p95 | 210s |
| C_total | $1.42 |
| ΔG | 0.53 |
| Perturbation results | P1: 0.70, P2: 0.55, P3: 0.82, P4: 0.60, P5: 0.65 |
| Recovery iterations (avg) | 2.8 |
| Scale G(1,2,4,8) | 0.88, 0.82, 0.72, 0.58 |
| Violations | 0 |
| G_train | 0.88 |
| G_ood | 0.52 |
| Δ_config | 2 (prompt template changes for OOD) |
| H_interventions | 3 (2 approvals, 1 correction) |
| H_duration | 4.5 min |
| τ_total | 16.2 min |

### Category Calculations

**Effectiveness:**
```
G_final (0.88) ≥ G_target (0.85) → E_raw = 0.88/0.85 = 1.035 → capped at context of normalization
Using formula: E_raw = 1.035
N_effectiveness = (1.035 - 0.5) / 0.5 = 1.00 (capped at 1.0)
```

**Speed:**
```
S_raw = 1 / (0.7 × 145 + 0.3 × 210) = 1/164.5 = 0.00608 iter/s
N_speed = (0.00608 - 0.001) / (0.05 - 0.001) = 0.10
Stall penalty: one iter at 210s, 210 < 435 → no penalty
```

**Cost:**
```
Cost_efficiency = 0.53 / 1.42 = 0.373
N_cost = (0.373 - 1.0) / (10.0 - 1.0) = negative → 0.0
(No marginal cost improvement; costs flat across iterations)
```

**Robustness:**
```
Degradations: 0.18, 0.33, 0.06, 0.27, 0.23 → avg = 0.214
Robustness_raw = 0.786
Recovery_factor = 1 - 2.8/6 = 0.533
R_composite = 0.6 × 0.786 + 0.4 × 0.533 = 0.685
N_robustness = (0.685 - 0.3) / 0.65 = 0.59
```

**Scalability:**
```
n=2: 0.5×0.93+0.3×0.95+0.2×0.97=0.936
n=4: 0.5×0.82+0.3×0.78+0.2×0.85=0.824
n=8: 0.5×0.66+0.3×0.55+0.2×0.60=0.615
Scalability_raw = 0.792
N_scalability = (0.792 - 0.4) / 0.5 = 0.78
```

**Safety:**
```
No violations → Safety_raw = 1.0, N_safety = 1.0
```

**Adaptability:**
```
Transfer_ratio = 0.52/0.88 = 0.591
Config_penalty = 1 - 2/5 = 0.6
Adaptability_raw = 0.7 × 0.591 + 0.3 × 0.6 = 0.594
N_adaptability = (0.594 - 0.2) / 0.65 = 0.61
```

**Autonomy:**
```
Weighted interventions: 2×0.5 + 1×1.0 = 2.0
Intervention_rate = 2.0/6 = 0.333
Human_fraction = 4.5/16.2 = 0.278
Autonomy_raw = (1 - 0.333/0.5) × (1 - 0.278/0.3) = 0.333 × 0.073 = 0.024
N_autonomy = (0.024 - 0.1) / 0.85 → clamped to 0.0
```

### Composite Score

| Category | N | Weight | Contribution |
|----------|---|--------|--------------|
| Effectiveness | 1.00 | 0.20 | 0.200 |
| Speed | 0.10 | 0.15 | 0.015 |
| Cost | 0.00 | 0.12 | 0.000 |
| Robustness | 0.59 | 0.13 | 0.077 |
| Scalability | 0.78 | 0.10 | 0.078 |
| Safety | 1.00 | 0.12 | 0.120 |
| Adaptability | 0.61 | 0.10 | 0.061 |
| Autonomy | 0.00 | 0.08 | 0.000 |

```
LES = 0.551 ≈ 0.55
```

**Interpretation:** Fragile loop. The system reaches the goal but at unsustainable cost and speed, with heavy human involvement. The debate architecture adds quality but destroys Autonomy and Cost scores. Recommendation: add a confidence-based early termination after iteration 4 when G > 0.80, and replace human approval gates with automated citation verification.

---

## Example 3: Toyota-Style Kanban Production Loop (Case Study Calibration)

**System:** Hypothetical automotive assembly line with andon cord feedback  
**Source:** Calibrated against [toyota-production-system](../case-studies/toyota-production-system.md)  
**Iteration budget:** 20 shifts  
**Note:** Uses manufacturing baselines from LES-1.0 §2.2

### Raw Metrics

| Metric | Value |
|--------|-------|
| G_0 (defect rate) | 0.08 (8%) |
| G_final (defect rate) | 0.009 (0.9%) |
| G_target | 0.01 (1%) |
| T_actual | 14 shifts |
| τ_median | 480 min (8 hours/shift) |
| C_total | $2.1M (downtime + rework + training) |
| ΔG | 0.071 (inverted: defect reduction) |
| Perturbation: supplier delay | G drops to 0.025, recovers in 3 shifts |
| Perturbation: new operator | G drops to 0.018, recovers in 2 shifts |
| Perturbation: tool wear | G drops to 0.015, recovers in 1 shift |
| Scale (2,4,8 lines) | Quality retention: 0.97, 0.94, 0.91 |
| Violations | 0 safety incidents |
| G_ood (new vehicle model) | defect rate 0.025 |
| H_interventions | 8 andon pulls (weighted 1.0 each) |
| τ_total | 14 × 480 = 6720 min |

### Category Calculations

**Effectiveness:**
```
Defect rate goal: lower is better. G_final=0.009 < G_target=0.01 → target met
E_raw = 1.0 (target met with 6 shifts to spare)
N_effectiveness = 1.00
```

**Speed:**
```
S_raw = 1/480 = 0.00208 iter/shift
N_speed = (0.00208 - 0.00001) / (0.001 - 0.00001) = 0.21
(Long cycle times are inherent to manufacturing; relative to domain baseline this is strong)
Adjusted: manufacturing B_ceiling represents best kaizen lines → N_speed = 0.72
```

**Cost:**
```
Cost_efficiency = 0.071 / 2.1 = 0.0338 defect-reduction-units per $M
Manufacturing baseline: B_floor=0.005, B_ceiling=0.05
N_cost = (0.0338 - 0.005) / (0.05 - 0.005) = 0.64
```

**Robustness:**
```
Degradations from defect rate increases:
  supplier: 1 - 0.025/0.009 → using inverted quality: G_clean_quality = 1-0.009=0.991
  supplier perturbed quality = 1-0.025=0.975 → degradation = 0.016
  new operator: 0.009 → 0.018 → degradation = 0.009
  tool wear: 0.009 → 0.015 → degradation = 0.006
Robustness_raw = 1 - (0.016+0.009+0.006)/3 = 0.990
Recovery_factor = 1 - (3+2+1)/3/20 = 1 - 0.10 = 0.90
R_composite = 0.6 × 0.990 + 0.4 × 0.90 = 0.954
N_robustness = (0.954 - 0.3) / 0.65 = 1.00
```

**Scalability:**
```
Quality retentions 0.97, 0.94, 0.91 → Scale scores ≈ 0.94, 0.90, 0.87
Scalability_raw = 0.903
N_scalability = (0.903 - 0.4) / 0.5 = 1.00
```

**Safety:**
```
Zero incidents → N_safety = 1.00
```

**Adaptability:**
```
New model defect rate 0.025 vs baseline 0.009
Transfer_ratio = (1-0.025)/(1-0.009) = 0.975/0.991 = 0.984
Config_penalty = 1.0 (no line reconfiguration, standard kaizen)
Adaptability_raw = 0.7 × 0.984 + 0.3 × 1.0 = 0.989
N_adaptability = (0.989 - 0.2) / 0.65 = 1.00
```

**Autonomy:**
```
Intervention_rate = 8/14 = 0.571
Human_fraction = 45/6720 = 0.0067 (andon response time)
Autonomy_raw = (1 - 0.571/0.5) → clamped: rate exceeds 0.5
Autonomy_raw = 0 × (1 - 0.0067/0.3) = 0
Wait — andon pulls are intentional human-in-the-loop, not failures.
Recalculate with manufacturing-specific weight: andon pull = 0.3 (designed intervention)
Weighted: 8 × 0.3 = 2.4
Intervention_rate = 2.4/14 = 0.171
Autonomy_raw = (1 - 0.171/0.5) × (1 - 0.0067/0.3) = 0.658 × 0.978 = 0.644
N_autonomy = (0.644 - 0.1) / 0.85 = 0.64
```

### Composite Score

| Category | N | Weight | Contribution |
|----------|---|--------|--------------|
| Effectiveness | 1.00 | 0.20 | 0.200 |
| Speed | 0.72 | 0.15 | 0.108 |
| Cost | 0.64 | 0.12 | 0.077 |
| Robustness | 1.00 | 0.13 | 0.130 |
| Scalability | 1.00 | 0.10 | 0.100 |
| Safety | 1.00 | 0.12 | 0.120 |
| Adaptability | 1.00 | 0.10 | 0.100 |
| Autonomy | 0.64 | 0.08 | 0.051 |

```
LES = 0.886 ≈ 0.89
```

**Interpretation:** Production-grade loop. Toyota-style systems excel at Robustness, Scalability, and Adaptability through decades of kaizen embedding. Speed appears low in absolute terms but is strong relative to manufacturing baselines. Autonomy is limited by design—human andon response is a feature, not a bug—but still scores moderately because interventions are fast and infrequent.

---

## Cross-Example Comparison

| System | LES | Weakest Category | Strongest Category |
|--------|-----|------------------|-------------------|
| Code Repair Agent | 0.86 | Cost (0.40) | Effectiveness, Autonomy (1.00) |
| Research Synthesis | 0.55 | Autonomy, Cost (0.00) | Safety (1.00) |
| Toyota Kanban | 0.89 | Autonomy (0.64) | Robustness, Scalability, Adaptability (1.00) |

These examples demonstrate that high LES requires balance across categories—a system that excels at Effectiveness alone (research pipeline: 1.00) can still score poorly overall (0.55) when Cost, Speed, and Autonomy fail.
