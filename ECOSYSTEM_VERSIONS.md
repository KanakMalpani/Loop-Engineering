# Loop Engineering Ecosystem — Version Registry

Single source of truth for public version strings across the five-repo stack.  
Update this file when any component releases; mirror changes in sibling repo READMEs.

**Last updated:** 2026-06-25

---

## Standards

| Component | Version | Canonical location |
|-----------|---------|------------------|
| LSS (Loop Specification Standard) | **1.0** + **1.1** composition | [lss-1.0.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.md) · [lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md) |
| Schema versioning policy | **1.0** | [schema-versioning.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/schema-versioning.md) |
| LES (Loop Engineering Score) | **1.0** | [Loop-Core-Engineering/specs/les-1.0.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/les-1.0.md) |
| Loop Trace | **1.0** | [standards/LOOP-TRACE-1.0.md](standards/LOOP-TRACE-1.0.md) |
| Loop ID registry | **1.0** | [Loop-Core-Engineering/specs/loop-ids.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/loop-ids.md) |

---

## Dataset

| Component | Version | Records | Location |
|-----------|---------|---------|----------|
| LoopNet Tier 1 | **v0.2** | 545 trajectories | [Hugging Face](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) · [GitHub](https://github.com/KanakMalpani/loopnet) |

**Deprecated:** `loopnet-seed-v0.1` — do not cite in new work; use v0.2.

---

## Runtime and benchmarks (PyPI)

| Package | Version | Install | Repository |
|---------|---------|---------|------------|
| le-loopforge | **0.2.0** | `pip install "le-loopforge>=0.2.0"` (CLI: `loopforge`) | [Loop-Engineering/loopforge](loopforge/) |
| le-loopctl | **0.1.0** | `pip install "le-loopctl>=0.1.0"` (CLI: `loopctl`) | [Loop-Engineering/loopctl](loopctl/) |
| loopgym | **0.1.2** | `pip install "loopgym>=0.1.2"` | [LoopGym](https://github.com/KanakMalpani/LoopGym) |
| loopbench | **0.1.1** | `pip install "loopbench>=0.1.1"` | [LoopBench](https://github.com/KanakMalpani/LoopBench) |

Pin exact versions in reproduction docs; run `pip show le-loopforge le-loopctl loopgym loopbench` after install.

**PyPI naming:** [PYPI_NAMING.md](contributions/PYPI_NAMING.md) — use `le-loopforge` / `le-loopctl`, not bare `loopforge` / `loopctl`.

---

## Discipline repos

| Repository | Role | URL |
|------------|------|-----|
| Loop Engineering | Narrative home — manifesto, patterns, case studies | https://github.com/KanakMalpani/Loop-Engineering |
| Loop Core Engineering | Specs, validators, governance | https://github.com/KanakMalpani/Loop-Core-Engineering |

---

## Paper series (local / forthcoming)

| ID | Title (short) | Maps to |
|----|---------------|---------|
| S1 | Loop Engineering Survey | fundamentals/, patterns/, research/ |
| P1 | Loop Algebra + LSS | standards/, loop-library/ |
| P2 | Loop Complexity | benchmarks/, tools/ |
| P3 | Convergence & Stability | fundamentals/07-convergence.md |
| P4 | LoopNet Empirical | LoopNet v0.2, research/LOOPNET.md |

See [research/PAPER_SERIES.md](research/PAPER_SERIES.md).

---

## Sync checklist (maintainers)

When releasing a new component version:

- [ ] Update this file
- [ ] Update [README.md](README.md) published-stack table
- [ ] Update [standards/CANONICAL-SOURCE.md](standards/CANONICAL-SOURCE.md)
- [ ] Update Loop Core Engineering `ECOSYSTEM.md`
- [ ] Update LoopNet HF dataset card
- [ ] Update LoopBench leaderboard metadata if benchmark version changes
