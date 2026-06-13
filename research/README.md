# Loop Engineering Research

This directory collects **open questions, theoretical extensions, and long-horizon implications** for Loop Engineering—the discipline of designing systems that continuously improve through feedback.

Research here is not a separate academic silo. It is the forward edge of the same engineering practice documented in `fundamentals/`, `taxonomy/`, and `standards/`. Every document assumes familiarity with the loop tuple **L = (S, A, O, T, E, M, τ)**, the six-level taxonomy, and the D-D-M-I-S methodology (Design, Diagnose, Measure, Improve, Scale).

---

## Purpose

Loop Engineering research addresses three classes of question:

1. **Foundational**: What can be proved about loops as dynamical systems? What are the limits of composition, convergence, and safety?
2. **Applied**: How do we build loops that work in production—under cost constraints, adversarial inputs, and organizational friction?
3. **Speculative**: What happens when loops improve loops at scale? What are the implications for AGI, institutions, and the design of intelligence itself?

We publish research as **living documents**. They are revised as benchmarks, case studies, and community implementations produce evidence. A problem listed as "open" may become "partially resolved" when a pattern, standard extension, or benchmark result gives us a reproducible answer.

---

## Document Index

| Document | Focus | Audience |
|----------|-------|----------|
| [open-problems.md](./open-problems.md) | Catalog of unsolved research problems with context and partial progress | Researchers, benchmark authors |
| [future-agent-architectures.md](./future-agent-architectures.md) | Architectural trajectories for agentic systems through 2030 | Engineers, system architects |
| [meta-learning-loops.md](./meta-learning-loops.md) | Loops that learn how to loop—compilation, adaptation, transfer | ML engineers, harness builders |
| [recursive-self-improvement.md](./recursive-self-improvement.md) | Level 5–6 dynamics, safety envelopes, convergence | Safety researchers, long-horizon builders |
| [agi-implications.md](./agi-implications.md) | How loop engineering reframes AGI as an engineering problem | Strategists, policy, general audience |
| [organizational-intelligence-systems.md](./organizational-intelligence-systems.md) | Loops at team, company, and ecosystem scale | Org leaders, ops, platform teams |
| [loop-composition-algebra.md](./loop-composition-algebra.md) | Formal operators for combining loops (sequential, parallel, nested) | Theorists, compiler/tool builders |

---

## Relationship to Other Repository Areas

```
fundamentals/     ←  axioms, definitions, proofs-in-progress
taxonomy/         ←  classification of loop cognitive depth (Levels 1–6)
patterns/         ←  engineering solutions to recurring loop design problems
standards/        ←  LSS: declarative loop specifications
scoring/          ←  LES: eight-dimensional loop performance measurement
benchmarks/       ←  reproducible tasks that stress-test research claims
case-studies/     ←  empirical grounding from real systems
research/         ←  you are here: questions not yet closed
contributions/    ←  how to propose, review, and merge research updates
```

Research documents **propose**; patterns and standards **encode**; benchmarks **test**; case studies **ground**.

---

## Research Norms

### Evidence hierarchy

We rank claims by reproducibility:

1. **Demonstrated**: Benchmark result with public artifact, LSS spec, and LES score
2. **Replicated**: Independent reproduction on different harness or domain
3. **Theorized**: Formal argument or simulation without production validation
4. **Conjectured**: Plausible hypothesis with identified falsification criteria

Documents in this directory mix all four levels. Each section should make its evidence tier explicit.

### Falsification over rhetoric

An open problem is valuable when it specifies:

- What observation would **resolve** it (positive or negative)
- What **metric** moves (LES dimension, convergence rate, safety violation rate)
- What **minimal experiment** a practitioner could run in a week

### Safety-first escalation

Research on Level 5 (self-modifying) and Level 6 (recursive meta) loops assumes **explicit safety envelopes**: bounded modification sets, human charter gates, rollback paths, and audit logs. Speculative documents discuss upside; they also discuss failure modes and containment.

---

## How to Contribute Research

1. Read [open-problems.md](./open-problems.md) and identify whether your work closes, narrows, or reframes an existing problem.
2. Follow [contributions/CONTRIBUTING.md](../contributions/CONTRIBUTING.md) for pull request structure.
3. If your contribution includes empirical results, add or extend a benchmark in `benchmarks/` and reference LES scores.
4. Propose standard changes via [contributions/GOVERNANCE.md](../contributions/GOVERNANCE.md) when research stabilizes into specification language.

Major research updates are tracked on the [RESEARCH_ROADMAP.md](../contributions/RESEARCH_ROADMAP.md) (2026–2030).

---

## Reading Paths

**Engineer entering research (1 week)**  
`fundamentals/03-feedback-and-convergence.md` → `open-problems.md` (Problems 1–5) → `meta-learning-loops.md` → one benchmark reproduction

**Theorist (2 weeks)**  
`fundamentals/` full path → `loop-composition-algebra.md` → `recursive-self-improvement.md` → `open-problems.md` (Problems 10–18)

**Org / strategy (3 days)**  
`organizational-intelligence-systems.md` → `agi-implications.md` → case studies in `case-studies/`

**Safety reviewer (1 week)**  
`recursive-self-improvement.md` → `open-problems.md` (Safety cluster) → `standards/LSS-1.0.md` termination and audit sections

---

## Citation

When citing research documents from this directory, use the repository citation format in [contributions/CITATION.md](../contributions/CITATION.md), adding the specific document path and revision date.

---

<p align="center"><em>Research closes when a loop can be specified, scored, and reproduced.</em></p>
