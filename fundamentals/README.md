# Loop Engineering Fundamentals

A structured curriculum for designing, building, and governing iterative intelligent systems.

---

## What This Series Covers

Loop Engineering is the discipline of treating **feedback-driven iteration** as a first-class engineering artifact. These fundamentals provide the vocabulary, formal abstractions, and practical patterns needed to move beyond one-shot prompting toward systems that observe, evaluate, and improve.

Each module includes:

- **Definitions** — precise terms with unambiguous meaning
- **Formal abstractions** — mathematical or structural models
- **Examples** — concrete instances from software, agents, and organizations
- **Mermaid diagrams** — visual models of structure and flow
- **Practical implications** — what to do differently on Monday morning

---

## Learning Path

### Tier 1: Core Concepts (Start Here)

Build mental models for what a loop is and how feedback drives intelligence.

| Order | Module | Time | Prerequisite |
|-------|--------|------|--------------|
| 1 | [What Is a Loop?](01-what-is-a-loop.md) | 45 min | None |
| 2 | [Feedback Theory](02-feedback-theory.md) | 60 min | Module 1 |
| 3 | [State Transitions](03-state-transitions.md) | 45 min | Module 1 |

**Outcome**: You can diagram any iterative system as an explicit loop with state, actions, observations, and transitions.

---

### Tier 2: System Components

Understand the machinery inside well-engineered loops.

| Order | Module | Time | Prerequisite |
|-------|--------|------|--------------|
| 4 | [Memory Systems](04-memory-systems.md) | 60 min | Modules 1–3 |
| 5 | [Optimization Systems](05-optimization-systems.md) | 60 min | Modules 1–3 |
| 6 | [Evaluation Systems](06-evaluation-systems.md) | 75 min | Modules 1–3 |

**Outcome**: You can specify memory architecture, search strategy, and evaluation oracles for a loop before writing code.

---

### Tier 3: Loop Lifecycle

Engineer loops that finish — correctly, efficiently, and safely.

| Order | Module | Time | Prerequisite |
|-------|--------|------|--------------|
| 7 | [Convergence](07-convergence.md) | 45 min | Modules 5–6 |
| 8 | [Termination Conditions](08-termination-conditions.md) | 45 min | Module 7 |

**Outcome**: You can define when a loop should stop trying and when it should stop entirely.

---

### Tier 4: Disciplinary Connections

Connect Loop Engineering to established fields. Use these as lenses, not replacements.

| Order | Module | Time | Prerequisite |
|-------|--------|------|--------------|
| 9 | [Control Theory Connections](09-control-theory-connections.md) | 60 min | Modules 2, 7 |
| 10 | [Reinforcement Learning Connections](10-reinforcement-learning-connections.md) | 75 min | Modules 1, 5–6 |
| 11 | [Cybernetics Connections](11-cybernetics-connections.md) | 45 min | Modules 2, 4 |
| 12 | [Organizational Learning Connections](12-organizational-learning-connections.md) | 45 min | Modules 2, 6 |

**Outcome**: You can translate between loop engineering vocabulary and the vocabulary of adjacent disciplines.

---

### Tier 5: Advanced Topics

| Order | Module | Time | Prerequisite |
|-------|--------|------|--------------|
| 13 | [Self-Improving Systems](13-self-improving-systems.md) | 90 min | All prior modules |

**Outcome**: You can design bounded recursive improvement with safety envelopes and audit trails.

---

## Recommended Study Tracks

### Track A: Agent Builder
Modules 1 → 2 → 3 → 4 → 6 → 7 → 8 → 13

Focus on building coding and research agents that terminate reliably with explicit memory and evaluation.

### Track B: ML Engineer
Modules 1 → 2 → 5 → 6 → 7 → 10 → 13

Focus on optimization, reward design, and the RL mapping for training iterative systems.

### Track C: Systems / Platform Engineer
Modules 1 → 3 → 4 → 7 → 8 → 9 → 11

Focus on stability, state management, and control-theoretic governance of production loops.

### Track D: Engineering Manager
Modules 1 → 2 → 6 → 12 → 13

Focus on evaluation culture, organizational learning patterns, and governance of self-improving tooling.

---

## How to Read

1. **Read sequentially** on first pass, even if you are experienced. The formal abstractions in early modules are referenced throughout.
2. **Draw the diagrams** yourself after reading each mermaid figure. Translation to your own notation reveals gaps in understanding.
3. **Apply immediately**: after each module, diagram one loop from your current project using that module's vocabulary.
4. **Cross-reference the Manifesto**: [MANIFESTO.md](../manifesto/MANIFESTO.md) states *why*; these fundamentals state *how*.
5. **Cross-reference the Principles**: [PRINCIPLES.md](../manifesto/PRINCIPLES.md) provides review checklists mapped to module content.

---

## Formal Notation Used Throughout

| Symbol | Meaning |
|--------|---------|
| \( S \) | State space |
| \( A \) | Action space |
| \( O \) | Observation space |
| \( T \) | Transition function |
| \( R \) | Reward / evaluation function |
| \( \gamma \) | Discount factor (horizon weighting) |
| \( \tau \) | Termination function |
| \( \pi \) | Policy (action selection strategy) |
| \( e \) | Evaluation / error signal |

---

## Module Index

1. [What Is a Loop?](01-what-is-a-loop.md)
2. [Feedback Theory](02-feedback-theory.md)
3. [State Transitions](03-state-transitions.md)
4. [Memory Systems](04-memory-systems.md)
5. [Optimization Systems](05-optimization-systems.md)
6. [Evaluation Systems](06-evaluation-systems.md)
7. [Convergence](07-convergence.md)
8. [Termination Conditions](08-termination-conditions.md)
9. [Control Theory Connections](09-control-theory-connections.md)
10. [Reinforcement Learning Connections](10-reinforcement-learning-connections.md)
11. [Cybernetics Connections](11-cybernetics-connections.md)
12. [Organizational Learning Connections](12-organizational-learning-connections.md)
13. [Self-Improving Systems](13-self-improving-systems.md)

---

*Begin with [What Is a Loop?](01-what-is-a-loop.md).*
