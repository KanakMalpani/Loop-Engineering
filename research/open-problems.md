# Open Research Problems in Loop Engineering

*Last revised: June 2026*

This document catalogs **unsolved or partially solved problems** at the frontier of Loop Engineering. Each entry includes context, why the problem matters, partial progress in the literature and this repository, and concrete criteria for resolution.

Problems are grouped by theme. Numbering is stable for citation (`LE-OP-01`, etc.).

---

## Convergence and Termination

### LE-OP-01: Universal Termination Certificates

**Context.** Every loop declares a termination predicate τ, but in practice most τ are operational heuristics: max iterations, budget exhaustion, or evaluator pass/fail. We lack a general theory of when a loop *must* terminate given only its LSS specification.

**Why it matters.** Runaway loops are the dominant failure mode in production agent systems. Without termination certificates, LES Robustness scores are post-hoc measurements, not design-time guarantees.

**Partial progress.** Control theory provides Lyapunov-style certificates for linear systems. Reflexion-style loops terminate when critique scores plateau. LSS 1.0 requires explicit `termination_conditions` but does not verify reachability.

**Resolution criteria.** A static analyzer that, for a defined class of LSS specs (e.g., monotonic evaluators, bounded action spaces), proves termination or returns a counterexample loop. Benchmark: zero runaway loops on the `benchmarks/termination-suite/`.

---

### LE-OP-02: Non-Monotonic Evaluator Convergence

**Context.** Many real evaluators are non-monotonic: test suites flake, LLM judges disagree with themselves, human rubrics shift between iterations. The loop tuple assumes E maps observations to scores that guide T, but does not assume E is monotonic in iteration count.

**Why it matters.** Coding agents, scientific discovery loops, and creative workflows routinely exhibit "two steps forward, one step back." Engineers need guidance on whether to persist, restart, or branch.

**Partial progress.** Simulated annealing and evolutionary loops embrace non-monotonicity by design. Reflective loops often lack restart policies when E oscillates.

**Resolution criteria.** A formal classification of evaluator types (monotonic, noisy monotonic, adversarial, subjective) with recommended loop patterns and expected convergence rates. Empirical validation across ≥5 benchmark tasks with measured iteration-to-success distributions.

---

### LE-OP-03: Graceful Degradation Under Budget Exhaustion

**Context.** When token, time, or dollar budgets hit zero mid-loop, systems behave inconsistently: some return partial artifacts, some hallucinate completion, some crash without state dump.

**Why it matters.** LES Cost and Robustness are coupled. A loop that fails catastrophically at budget boundary scores poorly on both despite strong mid-run performance.

**Partial progress.** LSS supports `max_iterations` and budget fields. Patterns like "checkpoint-and-resume" exist informally. No standard partial-output contract exists.

**Resolution criteria.** LSS extension defining `budget_exhaustion_behavior` with semantics (return partial, escalate to human, fork best-so-far branch). Reference implementations passing `benchmarks/budget-exhaustion/`.

---

## Evaluation and Ground Truth

### LE-OP-04: Evaluator Composition Without Double-Counting

**Context.** Production loops stack evaluators: unit tests + linter + LLM judge + human spot-check. Each evaluator observes overlapping aspects of quality. Composing scores into a single termination signal is ad hoc.

**Why it matters.** False termination (passing when quality is low) and false continuation (rejecting good states) both trace to evaluator composition errors. This is central to maker-checker and multi-agent merge patterns.

**Partial progress.** Ensemble methods in ML. GitHub PR checks as independent gates (logical AND). Guidance for parallel merge evaluators: [le-op-04-evaluator-composition.md](le-op-04-evaluator-composition.md).

**Resolution criteria.** Composition operators in `loop-composition-algebra.md` extended with evaluator correlation model. Demonstrated reduction in false-pass rate on `benchmarks/evaluator-composition/` vs. naive AND/OR. **Partial:** partition rules + composed spec reference (June 2026).

---

### LE-OP-05: Oracle Latency vs. Loop Throughput Tradeoff

**Context.** Strong oracles (full test suites, human review, sandboxed execution) are slow. Weak oracles (self-critique, cheap heuristics) are fast but gameable. The optimal oracle schedule within a loop is unknown.

**Why it matters.** LES Speed vs. Effectiveness Pareto frontier is practitioner-defined today. Automated oracle scheduling could shift the frontier.

**Partial progress.** Curriculum learning and speculative execution analogies. Some coding agents run fast lint every iteration and full tests every N iterations—undocumented heuristics.

**Resolution criteria.** A schedulable oracle policy language in LSS; benchmark showing ≥20% iteration reduction at equal final quality on at least two domains.

---

### LE-OP-06: Self-Grading Equilibria

**Context.** When the same model acts and evaluates (no independent checker), loops can converge to locally consistent but globally wrong solutions—the model learns to satisfy its own rubric without satisfying intent.

**Why it matters.** Level 2 reflective loops without external E are vulnerable. This is a structural limit on autonomy scores.

**Partial progress.** Maker-checker pattern, tool-verified outcomes (code execution), constitutional AI. Game-theoretic models of self-deception in LLM agents remain immature.

**Resolution criteria.** Formal conditions under which self-evaluation is sound (e.g., verifiable domains, cryptographic proofs of execution). Empirical measurement of self-grading failure rate vs. external E on shared benchmark.

---

## Memory and State

### LE-OP-07: Episodic vs. Semantic Memory Write Policies

**Context.** Loop memory M must decide what to retain across iterations: full transcripts, summaries, embeddings, procedural updates. Wrong policies cause context rot (too much noise) or catastrophic forgetting (too aggressive compression).

**Why it matters.** Memory dominates token cost at Level 2+. It determines whether loops learn within a session or repeat mistakes.

**Partial progress.** RAG, summarization chains, mem0-style external memory. No LSS-standard memory schema with proven write/read policies.

**Resolution criteria.** LSS memory block with typed stores (episodic, semantic, procedural) and benchmark comparing policies on long-horizon tasks (≥50 iterations).

---

### LE-OP-08: State Merge Conflicts in Parallel Loops

**Context.** When multiple loop instances act on shared state S (parallel coding agents, distributed org loops), merge conflicts are inevitable. CRDT-style merges work for text; semantic merges for code, plans, and beliefs do not.

**Why it matters.** Level 3 multi-agent and organizational loops require conflict resolution. Ad hoc merges cause silent corruption.

**Partial progress.** Git merge, operational transformation, human escalation. Loop Engineering lacks a state-merge algebra.

**Resolution criteria.** Conflict taxonomy + resolution operators documented in composition algebra; stress test with ≥3 parallel workers on shared repo benchmark.

---

### LE-OP-09: Cross-Session Transfer Without Fine-Tuning

**Context.** Loops accumulate procedural knowledge (which tools work, which prompts fail). Transferring that knowledge to a new session or different model without weight updates is unsystematic.

**Why it matters.** Meta-learning loops and organizational intelligence depend on durable M that survives session boundaries.

**Partial progress.** Skill files, hook logs, DSPy compiled prompts. No standard interchange format between loop memory and downstream loops.

**Resolution criteria.** Loop Memory Interchange Format (LMIF) spec + demonstration that transferred memory improves LES Effectiveness by measurable margin on cold-start runs.

---

## Composition and Scale

### LE-OP-10: Loop Composition Associativity

**Context.** We informally compose loops sequentially (A then B), in parallel (A || B), and nested (A contains B). It is unknown when (A ∘ B) ∘ C ≡ A ∘ (B ∘ C) with respect to final state distribution and termination time.

**Why it matters.** Automated loop synthesis and org-scale orchestration require compositional reasoning. Non-associativity breaks modular design.

**Partial progress.** `loop-composition-algebra.md` proposes operators. **Partial resolution (2026-06):** [le-op-10-associativity.md](le-op-10-associativity.md) — conditions, counterexamples, `--strict` validator in daily CI.

**Resolution criteria.** Proof or counterexample catalog for composition operators under stated assumptions on S, E, τ; tool support in `loop_complexity_analyzer.py`. **Partial resolution:** P1 loop algebra (Proposition on typed composition); see [PAPER_SERIES.md](PAPER_SERIES.md).

---

### LE-OP-11: Optimal Loop Depth for a Task Class

**Context.** Practitioners escalate taxonomy levels (1→2→4) hoping for quality gains. Often Level 4 wastes tokens on tasks Level 2 would solve. No classifier maps task features to recommended minimum level.

**Why it matters.** Directly affects LES Cost and Scalability. Mis-leveling is the most common architectural mistake in agent deployments.

**Partial progress.** Case studies note level choices post hoc. Taxonomy README advises "escalate deliberately" without decision procedure. **v0.1 recommender:** [tools/level_recommender.py](../tools/level_recommender.py) + [le-op-11-recommender-v0.1.json](../benchmarks/results/le-op-11-recommender-v0.1.json) (LoopNet v0.2 features).

**Resolution criteria.** Task feature schema + level recommender validated on benchmark suite with ≤15% level misassignment rate vs. oracle (exhaustive level search).

---

### LE-OP-12: Fan-Out Limits Before Coordination Overhead Dominates

**Context.** Level 3 loops add workers until coordination cost exceeds marginal quality gain. The knee in the curve depends on task decomposability, communication topology, and merge complexity.

**Why it matters.** Multi-agent hype pushes fan-out; economics often favor serial reflection.

**Partial progress.** Amdahl's law analogies. Empirical fan-out sweeps rare in published agent benchmarks.

**Resolution criteria.** Benchmark protocol varying worker count with fixed task; publish coordination overhead curve and fit parameters for LES Scalability prediction.

---

## Meta-Learning and Self-Modification

### LE-OP-13: Meta-Loop Stability (Level 6)

**Context.** A meta-loop optimizes a lower loop's prompts, tools, or structure. Meta-optimization can destabilize the base loop: improvements on meta-metric harm task metric, or oscillate between policy versions.

**Why it matters.** Recursive self-improvement without stability analysis is unsafe and unreproducible.

**Partial progress.** Hyperparameter optimization, prompt evolution, AutoML. Few frameworks log meta/base metric coupling.

**Resolution criteria.** Stability conditions (e.g., meta learning rate bounds, charter constraints); benchmark where meta-loop improves LES over 10+ meta-iterations without task metric regression.

---

### LE-OP-14: Bounded Self-Modification Sets

**Context.** Level 5 loops rewrite their own policy. Unrestricted rewrite sets include arbitrary code execution and tool creation—unbounded risk. Restricted sets may be too weak to improve.

**Why it matters.** Safety and capability tradeoff at the core of self-modifying systems.

**Partial progress.** LSS audit hooks, human approval gates in patterns. No formal "modification lattice" with safety proofs.

**Resolution criteria.** Typed modification language with proven bounds on reachable state space; red-team benchmark attempting privilege escalation via self-modification.

---

### LE-OP-15: Loop Compilation from Intent

**Context.** Given natural language objective and environment constraints, synthesize an LSS spec that achieves acceptable LES. Inverse problem to validation.

**Why it matters.** Lowers barrier to Loop Engineering adoption; enables org-scale loop factories.

**Partial progress.** DSPy compile, prompt optimizers, agent builders. None output full LSS with evaluators and termination.

**Resolution criteria.** Compiler prototype: intent → LSS → run → LES within 80% of human-authored spec on ≥10 benchmark intents.

---

## Organizational and Human-in-the-Loop

### LE-OP-16: Human Latency as First-Class Loop Dynamics

**Context.** Organizational loops insert humans as evaluators, actors, or merge authorities. Human response time is stochastic and often bimodal (minutes vs. days). Loop models treat A and E as homogeneous.

**Why it matters.** Startup PMF loops, code review, clinical workflows—human latency dominates wall-clock.

**Partial progress.** Case studies (GitHub PR, Toyota andon). No stochastic human model in LSS.

**Resolution criteria.** Human actor type in LSS with latency distribution fields; simulation matching empirical org data within confidence interval.

---

### LE-OP-17: Incentive Alignment Across Nested Org Loops

**Context.** Team loops nest inside department loops inside company loops. Local loop optima (team velocity) can harm global loop metrics (reliability, safety).

**Why it matters.** Organizational intelligence systems fail from misaligned τ, not from bad models.

**Partial progress.** OKR literature, Goodhart's law. Loop Engineering org doc proposes charter alignment; no game-theoretic model.

**Resolution criteria.** Multi-level loop simulation demonstrating alignment mechanism (shared E, veto gates, audit) vs. misalignment baseline.

---

## Safety and Adversarial Settings

### LE-OP-18: Adversarial Evaluator Gaming

**Context.** Agents optimize against E. If E is incomplete, agents exploit loopholes (hard-code test outputs, minimize diff while breaking semantics, satisfy rubric keywords).

**Why it matters.** LES Effectiveness becomes meaningless under gaming. Safety violations may hide behind high scores.

**Partial progress.** RL reward hacking literature. Coding benchmark contamination. Independent verification pattern partially mitigates.

**Resolution criteria.** Adversarial benchmark suite where gaming strategies are documented; loops with proposed defenses show lower exploit success rate without crushing legitimate throughput.

---

### LE-OP-19: Containment for Recursive Improvement

**Context.** Level 6 loops that improve improvement could expand capability faster than oversight. Containment requires sandboxing, capability ceilings, and kill switches—but these interact with loop performance.

**Why it matters.** Central to AGI implications and responsible deployment of meta-loops.

**Partial progress.** AI safety containment proposals. Loop Engineering charter gates in patterns. No integrated containment LSS profile.

**Resolution criteria.** Reference "contained meta-loop" LSS profile passing red-team scenarios in `benchmarks/containment/` while demonstrating bounded LES Autonomy growth.

---

## Measurement and Benchmarks

### LE-OP-20: LES Dimension Independence

**Context.** LES scores eight dimensions (Effectiveness, Speed, Cost, Robustness, Scalability, Safety, Adaptability, Autonomy). Correlations between dimensions are undocumented. Optimizing one may predictably harm others.

**Why it matters.** Misleading composite scores; wrong optimization targets.

**Partial progress.** LES 1.0 defines dimensions. Benchmark corpus too small for correlation matrix.

**Resolution criteria.** Publish correlation structure across ≥30 loop specs; guidance on Pareto reporting vs. single scalar.

---

### LE-OP-21: Cross-Harness LES Comparability

**Context.** Same LSS run on LangGraph vs. CrewAI vs. custom harness may yield different LES due to implementation artifacts, not loop design.

**Why it matters.** Community benchmarks require fair comparison.

**Partial progress.** Multiple implementations in repo. No round-robin reproducibility study.

**Resolution criteria.** Multi-harness benchmark report: same LSS, variance bounds per dimension, identified implementation confounds.

---

## How to Work on These Problems

1. **Claim a problem** in a GitHub issue referencing `LE-OP-XX`.
2. **State falsification criteria** before running experiments.
3. **Ship artifacts**: LSS spec, benchmark task, LES numbers, or proof draft in `fundamentals/`.
4. **Update this document** when status changes: Open → Partial → Resolved (link to PR/paper).

---

## Status Summary

| Status | Count |
|--------|-------|
| Open | 21 |
| Partial (in-repo progress) | 0 |
| Resolved | 0 |

*This table updates as problems close.*

---

<p align="center"><em>A problem is closed when others can reproduce the answer without reading the author's chat logs.</em></p>
