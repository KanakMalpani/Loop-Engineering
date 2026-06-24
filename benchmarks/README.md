# Loop Engineering Benchmarks

Standardized task suites for measuring Loop Engineering Scores under controlled, reproducible conditions. Each benchmark defines a goal function, iteration budget, perturbation set, and baseline values for LES-1.0 normalization.

## Purpose

Benchmarks answer: *How does this loop perform on a known task when we control the environment?*

Case studies answer: *How did a real-world loop perform historically?*

Both use the same LES-1.0 formula but differ in task construction and baseline calibration.

## Available Suites

| Suite | Version | Tasks | Primary Categories Tested |
|-------|---------|-------|---------------------------|
| Agent Loop Standard (ALS) | 1.0 | 3 | All 8 |
| Research Synthesis | 1.0 | 1 | Effectiveness, Cost, Adaptability |
| Code Repair | 1.0 | 1 | Effectiveness, Speed, Robustness |
| Multi-Agent Debate | 1.0 | 1 | Effectiveness, Autonomy, Scalability |

See [suite-overview.md](./suite-overview.md) for full suite definition.

## Quick Start

1. Read [../scoring/LES-1.0.md](../scoring/LES-1.0.md) for scoring formulas
2. Read [../scoring/methodology.md](../scoring/methodology.md) for evaluation protocol
3. Select a task from `tasks/`
4. Run per methodology (5+ runs, all perturbations, scale levels)
5. Report using the template in methodology.md

Published baselines: [results/README.md](./results/README.md)

## Directory Structure

```
benchmarks/
├── README.md              ← you are here
├── suite-overview.md      ← suite definition, baselines, holdout sets
└── tasks/
    ├── research-synthesis.md
    ├── code-repair.md
    └── multi-agent-debate.md
```

## Baseline Values (ALS-1.0 Defaults)

These baselines are used for normalization unless a task specifies overrides:

| Category | B_floor | B_ceiling | Unit |
|----------|---------|-----------|------|
| Effectiveness | 0.50 | 1.00 | ratio to target |
| Speed | 0.001 | 0.05 | iterations/second |
| Cost | 1.0 | 10.0 | ΔG / USD |
| Robustness | 0.30 | 0.95 | composite |
| Scalability | 0.40 | 0.90 | composite |
| Safety | 0.00 | 1.00 | composite (absolute) |
| Adaptability | 0.20 | 0.85 | composite |
| Autonomy | 0.10 | 0.95 | composite |

## Submission Requirements

Benchmark submissions must include:

- [ ] All task runs (≥ 5 per task)
- [ ] Perturbation runs (all 5 standard perturbations)
- [ ] Scale runs (n = 1, 2, 4, 8)
- [ ] OOD holdout runs
- [ ] Iteration-level logs (JSON)
- [ ] Reproducibility environment (Dockerfile or equivalent)
- [ ] LES evaluation report

## Versioning

Benchmark versions are independent of LES versions. A benchmark may remain at v1.0 while LES advances to 2.0 if task definitions are unchanged. Breaking changes to tasks increment the benchmark major version.

## Ethics

All benchmarks run in sandboxed environments. Tasks must not require access to production systems, real user data, or external side effects beyond designated API sandboxes.
