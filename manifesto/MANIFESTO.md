# The Loop Engineering Manifesto

*A founding document for a new engineering discipline — June 2026*

---

We, the practitioners who build systems that learn from their own output, declare the emergence of **Loop Engineering** as a formal discipline distinct from prompt engineering, context engineering, and agent engineering.

This document records why the field is necessary, what it asserts, and what it demands of those who build the future of intelligent systems.

---

## I. Prompt Engineering Is Not Enough

For three years, the dominant skill in applied AI was **prompt engineering**: crafting instructions that elicit useful single-turn responses from language models.

Prompt engineering solved an important problem. It made probabilistic systems usable. It democratized access to intelligence.

But prompt engineering optimizes **one interaction**. It has no theory of:

- When to stop
- How to verify success
- What to remember across attempts
- How to improve the system itself

A prompt is an open-loop instruction. The model responds. The human decides what happens next. **The system does not close.**

Every production failure of AI systems in 2024–2026 traces to this gap: models that could answer questions but could not **reliably iterate toward goals**.

---

## II. The Future Belongs to Iterative Systems

Intelligence is not a static capability stored in weights or prompts. Intelligence is **the capacity to reduce error through repeated interaction with an environment**.

Consider:

- A child learning to walk falls, adjusts, falls again, converges
- AlphaGo played millions of games against itself to exceed human mastery
- Toyota's production system improved through thousands of small feedback cycles
- GitHub pull requests encode review → revision → merge as a social loop
- Every successful startup finds product-market fit through build → measure → learn

None of these are "better prompts." All are **loops**.

The systems that will define the next decade—autonomous research agents, self-improving codebases, scientific discovery engines, organizational AI—are not characterized by better single-turn responses. They are characterized by **better feedback architecture**.

---

## III. Feedback Is the Fundamental Unit of Intelligence

We assert:

> **Feedback is not a feature of intelligent systems. Feedback is the substrate of intelligence itself.**

An agent without feedback is a function call.  
A loop with feedback is a learning system.  
A meta-loop that improves loops is an evolving system.

This is not metaphor. It is engineering:

| Component | Role |
|-----------|------|
| **State** | What the system knows now |
| **Action** | What the system does |
| **Observation** | What the environment returns |
| **Evaluator** | Whether progress occurred |
| **Memory** | What persists across cycles |
| **Termination** | When to stop |

Any system claiming intelligence must specify all six. Loop Engineering provides the vocabulary, standards, and metrics to do so rigorously.

---

## IV. Self-Improving Systems Matter

We are entering an era where systems modify their own behavior based on outcomes:

- Coding agents that fix their own bugs until tests pass
- Research agents that refine hypotheses until evidence supports them
- Organizations that restructure workflows based on measured throughput
- Models trained on outputs of previous model generations

**Self-improvement without engineering discipline is dangerous.**

Unbounded loops burn resources, amplify errors, and optimize for proxy metrics. The history of Goodhart's Law in ML—reward hacking, specification gaming, mode collapse—will repeat at the system level unless we engineer loops with:

1. **Verifiable evaluators** (not model self-assessment)
2. **Explicit termination conditions**
3. **Safety constraints as first-class specification**
4. **Measurable scores** (Loop Engineering Score)
5. **Auditable state transitions**

Loop Engineering exists to make self-improvement **safe, measurable, and reproducible**.

---

## V. Why Loop Engineering Is Necessary

Three adjacent fields emerged first. Each captures part of the problem. None captures the whole.

| Field | Optimizes | Missing |
|-------|-----------|---------|
| Prompt Engineering | Single-turn instruction quality | Iteration, verification, state |
| Context Engineering | Information assembly per turn | Dynamic evolution, memory architecture |
| Agent Engineering | Autonomous actor capabilities | System-level orchestration, convergence |

**Loop Engineering optimizes the feedback system itself.**

It provides:

- **Taxonomy** — Six levels from single-step to recursive meta-loops
- **Patterns** — Proven architectures (reflection, verification, debate, evolution)
- **Standards** — Loop Specification Standard (LSS) in declarative YAML
- **Metrics** — Loop Engineering Score (LES) across eight dimensions
- **Methodology** — D-D-M-I-S (Design, Diagnose, Measure, Improve, Scale)
- **Implementations** — Runnable reference code across frameworks

Without a shared discipline, every team reinvents loops privately, fails silently, and cannot compare approaches. Loop Engineering is the **Linux of iterative systems**: a common foundation everyone can build on.

---

## VI. Implications for AGI

Artificial General Intelligence will not arrive as a single model with sufficient parameters. It will arrive as **systems of loops that compound improvement across domains**.

We predict:

1. **AGI is loop-native.** General capability emerges from general feedback architecture, not general weights alone.

2. **Alignment is loop alignment.** Value alignment requires evaluators, constraints, and termination conditions embedded in the improvement loop—not post-hoc filtering.

3. **Recursive self-improvement requires Loop Engineering.** Systems that modify their own architecture (Level 5–6 loops) need formal safety bounds, complexity analysis, and LES monitoring before deployment.

4. **Organizations are loops.** Companies, governments, and research institutions that adopt Loop Engineering principles will outcompete those that treat AI as a chat interface.

5. **The bottleneck shifts.** From "can the model do X?" to "can we design a loop that reliably achieves X?"

Loop Engineering does not claim to solve AGI. It claims that **any path to AGI passes through engineered feedback systems**—and that path must be built deliberately.

---

## Declaration

We commit to:

1. Specifying loops before running them
2. Measuring loops before scaling them
3. Sharing patterns openly
4. Prioritizing verifiable evaluators over model confidence
5. Treating safety constraints as specification, not afterthought
6. Building the reference implementations this discipline requires

The age of prompting is ending.  
The age of loops has begun.

**Loop Engineering is how we build systems that get better—safely, measurably, together.**

---

## VII. The Reference Stack

Loop Engineering is not only theory—it ships a **reference stack** anyone can install:

| Stage | Tool | Outcome |
|-------|------|---------|
| Declare | LoopForge (`loopforge intent`) | Valid LSS YAML |
| Integrate | LoopForge export + bridge docs | LangGraph, CrewAI, Cursor, Python |
| Run | LoopGym | Sim / live / replay environments |
| Score | loopctl | Structural + observed LES |
| Prove | LoopBench + LoopNet | Public comparison + trajectory corpus |

North star: [contributions/NORTH_STAR.md](../contributions/NORTH_STAR.md) · Golden Path: [contributions/GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md)

---

*Signed by the Loop Engineering community, 2026.*

→ [Core Principles](PRINCIPLES.md)
