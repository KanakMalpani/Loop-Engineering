<div align="center">

# Loop Core Engineering

**The specification layer for systems that improve through feedback.**

Machine-readable contracts for declaring loops, scoring them, and naming failures — so every tool in the ecosystem speaks the same language.

<br>

[![CI](https://github.com/KanakMalpani/Loop-Core-Engineering/actions/workflows/validate.yml/badge.svg)](https://github.com/KanakMalpani/Loop-Core-Engineering/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LSS 1.0](https://img.shields.io/badge/LSS-1.0.0-green.svg)](specs/lss-1.0.schema.json)
[![LES 1.0](https://img.shields.io/badge/LES-1.0.0-purple.svg)](specs/les-1.0.md)

<br>

[**Validate a loop in 30 seconds**](#try-it-now) · [**Read LSS 1.0**](specs/lss-1.0.md) · [**Full stack map**](ECOSYSTEM.md) · [**Discipline docs**](https://github.com/KanakMalpani/Loop-Engineering)

</div>

---

## What you get here

| Deliverable | What it does for you |
|-------------|----------------------|
| **[LSS 1.0](specs/lss-1.0.md)** — Loop Specification Standard | Declare objectives, workers, evaluators, memory, safety, and termination in validated YAML |
| **[LES 1.0](specs/les-1.0.md)** — Loop Engineering Score | Compare loops on 8 dimensions: effectiveness, speed, cost, robustness, scalability, safety, adaptability, autonomy |
| **[Failure taxonomy](specs/failure-taxonomy.md)** | Shared `fail.*` codes — not tribal knowledge in Slack threads |
| **[ID registry](specs/loop-ids.md)** | Stable slugs for patterns, env prefixes, and cross-repo references |
| **Validators & LES calculator** | CI-ready tooling every other repo pins — no copied schemas |

This repo is the **root of the dependency graph**. [LoopNet](https://github.com/KanakMalpani/loopnet), [LoopGym](https://github.com/KanakMalpani/LoopGym), and [LoopBench](https://github.com/KanakMalpani/LoopBench) import specs from here. One source. Semver. RFCs.

---

## The problem this solves

Teams building agentic AI hit the same wall: every project invents its own config format, its own metrics, its own vocabulary for "why did the loop fail?"

| Without a shared spec | With Loop Core Engineering |
|-----------------------|----------------------------|
| Incomparable demos | LES-scored, reproducible runs |
| Schema copied into 5 repos | One canonical `lss@1.0.0` pin |
| "It worked in the demo" | Bounded termination + evaluator contracts |
| Failure post-mortems don't transfer | Shared taxonomy across data, runtime, and bench |

Think of it as **HTTP for loops** — a thin, versioned layer that everything else builds on.

---

## The ecosystem

```mermaid
flowchart TB
  CORE["<b>Loop Core Engineering</b><br/>LSS · LES · taxonomy · validators"]
  NET["LoopNet v0.2<br/>545 trajectories + failures"]
  GYM["LoopGym<br/>Sim · Live · Replay"]
  BENCH["LoopBench<br/>3 tasks · leaderboard"]

  CORE --> NET
  CORE --> GYM
  CORE --> BENCH
  NET --> GYM
  GYM --> BENCH
```

| Repo | Role | Install |
|------|------|---------|
| **Loop Core Engineering** | Specs & governance | Clone + `pip install -r requirements.txt` |
| [LoopNet](https://github.com/KanakMalpani/loopnet) | Dataset | [Hugging Face v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) (recommended) or JSONL |
| [LoopGym](https://github.com/KanakMalpani/LoopGym) | Runtime | `pip install loopgym` |
| [LoopBench](https://github.com/KanakMalpani/LoopBench) | Benchmarks | `pip install loopbench` |

Narrative depth — manifesto, patterns, case studies: [**Loop Engineering**](https://github.com/KanakMalpani/Loop-Engineering)

---

## Try it now

```bash
git clone https://github.com/KanakMalpani/Loop-Core-Engineering.git
cd Loop-Core-Engineering
pip install -r requirements.txt

# Validate against LSS 1.0 (same check CI runs)
python tools/validate_lss.py examples/minimal-loop.yaml

# Structural LES estimate before you run anything expensive
python tools/les_calculator.py --spec examples/minimal-loop.yaml --display
```

**A minimal loop spec looks like this:**

```yaml
loop_name: minimal-echo-loop
version: "1.0"
objective: "Demonstrate smallest valid LSS document"
workers:
  - role: echo
    model: mock
evaluators:
  - type: rubric
termination_conditions:
  - type: max_iterations
    value: 3
```

Three [CI-validated examples](examples/) ship with the repo — from smoke test to multi-agent debate.

---

## Specifications `@1.0.0`

| Artifact | Pin | Document |
|----------|-----|----------|
| LSS JSON Schema | `lss@1.0.0` | [`specs/lss-1.0.schema.json`](specs/lss-1.0.schema.json) |
| LSS overview | — | [`specs/lss-1.0.md`](specs/lss-1.0.md) |
| LES formulas | `les@1.0.0` | [`specs/les-1.0.md`](specs/les-1.0.md) |
| Pattern & env IDs | — | [`specs/loop-ids.md`](specs/loop-ids.md) |
| Semver policy | — | [`CHANGELOG.md`](CHANGELOG.md) |

**LES scale:** store and exchange in **`[0, 1]`**. Multiply by 100 only for display.

---

## Who this is for

| You are… | Start here |
|----------|------------|
| **Building an agent framework** | Pin LSS — let users export portable loop specs |
| **Running benchmarks** | Validate submissions against [`lss-1.0.schema.json`](specs/lss-1.0.schema.json) |
| **Publishing research** | Cite `lss@1.0.0` + `les@1.0.0` for reproducibility |
| **Designing org workflows** | Use failure taxonomy + LES dimensions as a shared scorecard |

---

## Governance

Spec changes flow through **[RFCs](templates/rfc-template.md)** → review → semver bump in [`CHANGELOG.md`](CHANGELOG.md). See [CONTRIBUTING.md](CONTRIBUTING.md) · [SYNC.md](SYNC.md) · [SECURITY.md](SECURITY.md)

---

## Adoption

Reproduce the stack in 60 minutes: [REPRODUCE.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/REPRODUCE.md) · [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)

---

## Citation

```bibtex
@misc{loop-core-engineering-2026,
  title={Loop Core Engineering: Canonical LSS and LES Specifications},
  author={Malpani, Kanak},
  year={2026},
  url={https://github.com/KanakMalpani/Loop-Core-Engineering}
}
```

<div align="center">

<sub>MIT License · v0.1 · <a href="STATUS.md">Status</a> · <a href="LAUNCH-CHECKLIST.md">Launch checklist</a></sub>

</div>
