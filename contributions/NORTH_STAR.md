# Loop Engineering — North Star

**Canonical goal statement** — propagate to [README.md](../README.md), [manifesto/MANIFESTO.md](../manifesto/MANIFESTO.md), and [MASTER_CHECKLIST.md](../All%20about%20loops/MASTER_CHECKLIST.md).

---

## North star

> **Loop Engineering is the default stack for building, running, scoring, and integrating feedback loops** — from natural-language intent to LSS spec, from spec to any harness (LangGraph, CrewAI, Cursor, generic Python), from run to Loop Trace to observed LES, from score to public LoopBench comparison — **without forcing a rewrite of what you already run**.

---

## Five integration promises (2026)

| Promise | Command surface | Phase 10 target |
|---------|-----------------|-----------------|
| **Declare** | `loopforge intent` · `loopforge compose` | Default Golden Path entry; PyPI `le-loopforge>=0.2.1` |
| **Run** | `loopforge export` → `run.py` · LoopGym | Export works from **pip install only** (no repo clone) |
| **Score** | `loopctl score` · `loopctl observed` · `loopctl pipeline` | One command: intent → validate → trace → LES report |
| **Integrate** | LangGraph / CrewAI / Cursor bridges | First-class packs under [integrate/](integrate/) |
| **Prove** | LoopBench · LoopNet · adoption tracker | External submissions + framework RFC feedback |

---

## Success looks like

1. A practitioner installs three PyPI packages and reaches a **validated spec + runnable export in 15 minutes**.
2. A LangGraph or CrewAI team maps existing graphs to LSS **without abandoning their runtime**.
3. A Cursor user validates agent loops with `loopctl` inside their IDE workflow.
4. The adoption tracker shows **≥10 green** signals with external LoopBench, reproduction, and case-study proof.

---

## Related

- [GOLDEN_PATH.md](GOLDEN_PATH.md) — intent-first onboarding
- [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md) — harness mapping table
- [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md) — community unlock paths
