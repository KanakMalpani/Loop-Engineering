# Loop Engineering Score (LES)

The Loop Engineering Score is a quantitative framework for evaluating closed-loop systems—any architecture that observes outcomes, updates internal state, and iterates toward a goal. LES applies equally to AI agent harnesses, manufacturing feedback loops, scientific peer review, and autonomous software development pipelines.

## Why LES Exists

Most system evaluations measure **outputs** (accuracy, latency, cost) in isolation. Loop Engineering treats the **iteration mechanism itself** as the primary object of study. A system that achieves 90% task success in one shot differs fundamentally from one that reaches 90% after five adaptive iterations with declining cost per iteration. LES captures that difference.

Traditional benchmarks answer: *Did it work?*  
LES answers: *How well does the loop work, and where does it break?*

## Core Concepts

### Loop

A loop is a recurring cycle with four mandatory stages:

1. **Observe** — gather signals about current state and outcomes
2. **Evaluate** — compare observations against goals, constraints, and prior predictions
3. **Decide** — select the next action, parameter change, or termination condition
4. **Act** — execute the decision and produce new observable state

Systems that lack any stage are not loops under LES—they are pipelines, scripts, or open-loop controllers.

### Loop Engineering

The discipline of designing, measuring, and optimizing iterative feedback systems. Loop Engineering concerns itself with:

- **Cycle time** — wall-clock duration per iteration
- **Convergence rate** — how quickly quality metrics approach asymptotes
- **Signal fidelity** — whether observations accurately reflect ground truth
- **Memory architecture** — what persists across iterations and what decays
- **Termination policy** — when the loop stops, retries, or escalates
- **Failure recovery** — behavior when an iteration produces regressions

## The Eight Categories

LES-1.0 scores loops across eight weighted categories:

| Category | Weight | Question Answered |
|----------|--------|-------------------|
| **Effectiveness** | 0.20 | Does the loop reach its stated goal? |
| **Speed** | 0.15 | How fast does each iteration complete? |
| **Cost** | 0.12 | What resources does each iteration consume? |
| **Robustness** | 0.13 | Does performance hold under perturbation? |
| **Scalability** | 0.10 | Does throughput degrade gracefully as load increases? |
| **Safety** | 0.12 | Are harmful outcomes prevented or bounded? |
| **Adaptability** | 0.10 | Can the loop handle novel inputs without redesign? |
| **Autonomy** | 0.08 | How much human intervention does the loop require? |

Composite score:

```
LES = Σ(wᵢ × Nᵢ)   where wᵢ = category weight, Nᵢ = normalized score ∈ [0, 1]
```

Full formulas, normalization procedures, and edge-case handling are specified in [LES-1.0.md](./LES-1.0.md).

## How to Use This Directory

| File | Purpose |
|------|---------|
| [LES-1.0.md](./LES-1.0.md) | Complete specification with formulas |
| [methodology.md](./methodology.md) | How to run a LES benchmark |
| [examples/scoring-examples.md](./examples/scoring-examples.md) | Worked examples with real numbers |

## Interpreting Scores

| Range | Interpretation |
|-------|----------------|
| 0.90 – 1.00 | Production-grade loop; minor tuning only |
| 0.75 – 0.89 | Strong loop; targeted improvements in 1–2 categories |
| 0.60 – 0.74 | Functional loop; structural changes likely needed |
| 0.40 – 0.59 | Fragile loop; high regression risk in deployment |
| 0.00 – 0.39 | Non-viable loop; redesign required |

Scores are **comparative within a domain**. A LES of 0.82 for an autonomous coding agent and 0.82 for a manufacturing kanban system are both "strong" but not directly interchangeable—the benchmarks and baselines differ.

## Relationship to Benchmarks and Case Studies

- **[../benchmarks/](../benchmarks/)** — Standardized task suites for measuring LES categories under controlled conditions
- **[../case-studies/](../case-studies/)** — Retrospective LES evaluations of real-world loop systems (AlphaGo, Toyota TPS, GitHub PRs, etc.)

Benchmarks produce **prospective** scores on synthetic tasks. Case studies produce **retrospective** scores on historical systems. Both feed the same LES-1.0 formula.

## Versioning

This repository implements **LES-1.0**. Future versions may adjust category weights, add sub-metrics, or introduce domain-specific normalization tables. All scores must cite the LES version used.

## Contributing Scores

When publishing a LES evaluation:

1. State the LES version (1.0)
2. List the benchmark suite or case study source
3. Report raw metrics before normalization
4. Document the baseline used for each category
5. Include iteration traces (minimum: observe/evaluate/decide/act per cycle)

See [methodology.md](./methodology.md) for the full reporting template.
