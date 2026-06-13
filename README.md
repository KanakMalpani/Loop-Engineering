# Loop Engineering

**The discipline of designing systems that continuously improve through feedback.**

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT"></a>
  <a href="https://github.com/KanakMalpani/Loop-Core-Engineering"><img src="https://img.shields.io/badge/Spec-LSS--1.0-green.svg" alt="LSS 1.0"></a>
  <a href="https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/les-1.0.md"><img src="https://img.shields.io/badge/Score-LES--1.0-purple.svg" alt="LES 1.0"></a>
</p>

> *Prompt Engineering optimizes a single interaction.*  
> *Context Engineering optimizes information.*  
> *Agent Engineering optimizes autonomous actors.*  
> **Loop Engineering optimizes self-improving systems.**

---

## Published stack (v0.1)

The runnable ecosystem lives on GitHub — this repo is the **narrative and pattern library**; specs are canonical elsewhere.

| Repository | Role | Link |
|------------|------|------|
| **Loop Core Engineering** | LSS / LES specs + validators | [→](https://github.com/KanakMalpani/Loop-Core-Engineering) |
| **LoopNet** | Dataset (ImageNet of loops) | [→](https://github.com/KanakMalpani/loopnet) |
| **LoopGym** | Runtime (Gym for loops) | [→](https://github.com/KanakMalpani/LoopGym) |
| **LoopBench** | Benchmarks (MLPerf for loops) | [→](https://github.com/KanakMalpani/LoopBench) |

→ [**Full install map**](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/ECOSYSTEM.md) · [**Canonical source policy**](standards/CANONICAL-SOURCE.md)

---

> *Prompt Engineering optimizes a single interaction.*  
> *Context Engineering optimizes information.*  
> *Agent Engineering optimizes autonomous actors.*  
> **Loop Engineering optimizes self-improving systems.**

---

## What is Loop Engineering?

Loop Engineering is the formal discipline of **designing, analyzing, measuring, and improving iterative feedback systems**. It answers one question:

**How do we systematically design systems that continuously improve through feedback?**

A **loop** is a closed dynamical system:

```
observe → decide → act → evaluate → update state → repeat
```

until a verifiable termination condition holds or resources are exhausted.

Loop Engineering unifies AI agents, autonomous systems, scientific discovery, organizational learning, startup iteration, and multi-agent orchestration under one engineering framework.

---

## Why It Matters

| Era | Primary Skill | Limitation |
|-----|---------------|------------|
| 2020–2023 | Prompt Engineering | Single-turn; no closure |
| 2023–2024 | Context Engineering | Static information; no iteration |
| 2024–2025 | Agent Engineering | Autonomous actors; no system-level improvement |
| **2025+** | **Loop Engineering** | **Self-improving systems at scale** |

Intelligence—biological, organizational, or artificial—is not a static capability. It is **the capacity to iterate toward better outcomes using structured feedback**. Loop Engineering makes that capacity engineerable.

---

## Core Concepts

### The Loop Tuple

Every loop can be formalized as:

```
L = (S, A, O, T, E, M, τ)
```

| Symbol | Meaning |
|--------|---------|
| **S** | State space (persistent + ephemeral) |
| **A** | Action space (agents, tools, humans) |
| **O** | Observation function (structured feedback) |
| **T** | Transition function (state update) |
| **E** | Evaluator (oracle, rubric, test suite) |
| **M** | Memory system (episodic, semantic, procedural) |
| **τ** | Termination predicate |

→ [Full formal treatment](fundamentals/01-what-is-a-loop.md)

### Six-Level Taxonomy

| Level | Name | Description |
|-------|------|-------------|
| 1 | Single-Step | One action, one observation |
| 2 | Reflective | Act → observe → reflect → revise |
| 3 | Multi-Agent | Coordinated actors with role separation |
| 4 | Evolutionary | Population-based search and selection |
| 5 | Self-Modifying | Loop modifies its own structure |
| 6 | Recursive Meta | Loops that improve loops |

→ [Complete taxonomy](taxonomy/README.md)

### D-D-M-I-S Methodology

| Phase | Question |
|-------|----------|
| **Design** | What should improve, and how do we know? |
| **Diagnose** | Where is the loop failing or stalling? |
| **Measure** | What does LES say about current performance? |
| **Improve** | Which lever (architecture, eval, memory) moves the score? |
| **Scale** | How do we run 10× loops without 10× failure? |

→ [Framework guide](framework/README.md)

### Loop Specification Standard (LSS)

Every loop is declarative YAML:

```yaml
loop_name: code-repair-loop
version: "1.0"
objective: "Fix failing tests with minimal diff"
workers:
  - role: implementer
    model: gpt-4.1
evaluators:
  - type: test_suite
    command: pytest
termination_conditions:
  - type: all_tests_pass
  - type: max_iterations
    value: 10
```

→ [LSS 1.0 Specification](standards/LSS-1.0.md)

### Loop Engineering Score (LES)

Universal scoring across eight dimensions:

**Effectiveness · Speed · Cost · Robustness · Scalability · Safety · Adaptability · Autonomy**

```bash
python tools/les_calculator.py --spec loop-library/autonomous-debugger.yaml
```

→ [LES 1.0 Specification](scoring/LES-1.0.md)

---

## Repository Map

```
Loop-Engineering/
├── manifesto/          Founding documents and principles
├── fundamentals/       Theoretical foundation (13 topics)
├── taxonomy/           Six-level loop classification
├── patterns/           14 design patterns with implementations
├── framework/          D-D-M-I-S methodology
├── standards/          LSS spec, schemas, validators
├── benchmarks/         Reproducible benchmark suite
├── scoring/            LES framework and examples
├── case-studies/       Deep analyses of real systems
├── loop-library/       Production-ready loop specifications
├── diagrams/           Centralized architecture diagrams
├── examples/           Runnable minimal examples
├── implementations/    Python, LangGraph, CrewAI, OpenAI Agents
├── tools/              LES calculator, validator, analyzers
├── research/           Open problems and AGI implications
├── assets/             Visual assets
└── contributions/      Governance and contribution guides
```

---

## Quick Start

### 1. Read the manifesto (15 min)

[manifesto/MANIFESTO.md](manifesto/MANIFESTO.md)

### 2. Understand loop fundamentals (2 hours)

[fundamentals/README.md](fundamentals/README.md) → follow the learning path

### 3. Specify your first loop (30 min)

```bash
cp standards/examples/minimal-loop.yaml my-loop.yaml
python tools/loop_validator.py my-loop.yaml
```

### 4. Run a reference implementation (15 min)

```bash
cd implementations/generic
pip install -r requirements.txt
python examples/reflection_loop.py
```

### 5. Score your loop

```bash
python tools/les_calculator.py --spec my-loop.yaml --interactive
```

---

## Learning Path

| Audience | Path | Duration |
|----------|------|----------|
| **Student** | manifesto → fundamentals → taxonomy → patterns | 1 week |
| **Engineer** | patterns → standards → loop-library → implementations | 3 days |
| **Researcher** | fundamentals → research → case-studies → benchmarks | 2 weeks |
| **Founder** | case-studies/startup-pmf-loops → framework/design → scoring | 2 days |
| **Org leader** | case-studies/toyota-production-system → framework/scale | 1 day |

---

## Loop Library Preview

| Loop | Level | Use Case | LES |
|------|-------|----------|-----|
| [Research Agent](loop-library/research-agent.yaml) | 2 | Literature synthesis | 78 |
| [Coding Agent](loop-library/coding-agent.yaml) | 3 | Feature implementation | 82 |
| [Autonomous Debugger](loop-library/autonomous-debugger.yaml) | 3 | Test-driven repair | 85 |
| [Scientific Discovery](loop-library/scientific-discovery-agent.yaml) | 4 | Hypothesis testing | 71 |
| [Startup Validator](loop-library/startup-validator.yaml) | 2 | PMF experiments | 74 |

→ [Full library](loop-library/README.md)

---

## Case Studies

| System | Loop Type | Key Insight |
|--------|-----------|-------------|
| [AlphaGo Self-Play](case-studies/alphago-self-play.md) | Evolutionary | Self-play generates its own training signal |
| [GitHub Pull Requests](case-studies/github-pull-requests.md) | Multi-Agent | Human + CI as distributed evaluators |
| [Toyota Production System](case-studies/toyota-production-system.md) | Reflective | Andon cord = hard termination on quality |
| [Autonomous Coding Agents](case-studies/autonomous-coding-agents.md) | Reflective + Verify | Maker-checker prevents self-grading |

→ [All case studies](case-studies/README.md)

---

## Tools

| Tool | Purpose |
|------|---------|
| [`les_calculator.py`](tools/les_calculator.py) | Compute Loop Engineering Score (local mirror) |
| [`loop_validator.py`](tools/loop_validator.py) | Validate LSS YAML (local mirror — prefer [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering/tree/main/tools)) |
| [`loop_diagram_generator.py`](tools/loop_diagram_generator.py) | Generate Mermaid from LSS |
| [`loop_complexity_analyzer.py`](tools/loop_complexity_analyzer.py) | Token/time complexity estimates |
| [`loop_comparison.py`](tools/loop_comparison.py) | Compare two loop specifications |

**Canonical validators:** `pip install -r requirements.txt` from [Loop-Core-Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) → `python tools/validate_lss.py …`

---

## Research Roadmap

| Horizon | Focus |
|---------|-------|
| **2026** | LSS adoption, LES benchmarking, pattern library |
| **2027** | Loop composition algebra, automated loop synthesis |
| **2028** | Organizational loop operating systems |
| **2030+** | Recursive self-improvement with safety proofs |

→ [Open research problems](research/open-problems.md)

---

## Contributing

Loop Engineering is a community-defined discipline. We welcome:

- New patterns with LSS specifications
- Case studies with LES evaluations
- Implementations in new frameworks
- Benchmark tasks and results
- Theoretical extensions to fundamentals

See [contributions/CONTRIBUTING.md](contributions/CONTRIBUTING.md) and [contributions/GOVERNANCE.md](contributions/GOVERNANCE.md).

---

## Citation

```bibtex
@misc{loop-engineering-2026,
  title={Loop Engineering: The Discipline of Self-Improving Systems},
  author={Loop Engineering Community},
  year={2026},
  url={https://github.com/KanakMalpani/Loop-Engineering}
}
```

---

## License

[MIT](LICENSE) — use freely, attribute kindly, improve collectively.

---

<p align="center">
  <strong>Feedback is the fundamental unit of intelligence.</strong><br>
  Loop Engineering makes it engineerable.
</p>
