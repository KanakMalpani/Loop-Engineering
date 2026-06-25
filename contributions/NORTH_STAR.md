# Loop Engineering — North Star

**Canonical goal statement** — propagate to [README.md](../README.md), [manifesto/MANIFESTO.md](../manifesto/MANIFESTO.md), and [MASTER_CHECKLIST.md](../All%20about%20loops/MASTER_CHECKLIST.md).

---

## North star

> **Loop Engineering is the default stack for building, running, scoring, and integrating feedback loops** — from natural-language intent to LSS spec, from spec to any harness (Claude Code, Codex, LangGraph, CrewAI, Cursor, Aider, Gemini CLI), from run to Loop Trace to observed LES, from score to public LoopBench comparison — **without forcing a rewrite of what you already run**.

---

## Five integration promises (2026)

| Promise | Command surface | Phase 11 target |
|---------|-----------------|-----------------|
| **Declare** | `loopforge intent` · `loopforge compose` | One-line `pip install le-loop-stack` |
| **Run** | `loopforge export` → `run.py` · LoopGym | Export works from **pip install only** |
| **Score** | `loopctl score` · `loopctl observed` · `loopctl pipeline` | **PyPI-native** structural + observed LES (`le-loopctl>=0.2.0`) |
| **Integrate** | [integrate/](integrate/) hub — 10+ harness packs | Claude Code, Codex, OpenAI Agents, Aider, Gemini CLI |
| **Prove** | LoopBench · LoopNet · adoption tracker | External submissions + framework RFC feedback |

---

## Success looks like

1. A practitioner runs `pip install le-loop-stack` and reaches **validated spec + LES score + export in 15 minutes** (no repo clone).
2. Claude Code / Codex / LangGraph teams map existing loops to LSS **without abandoning their runtime**.
3. The adoption tracker shows **≥10 green** signals (PyPI stack + community proof).
4. Integration hub lists **≥8 harness rows** with runnable smoke demos.

---

## Related

- [GOLDEN_PATH.md](GOLDEN_PATH.md) — Golden Path v3
- [integrate/README.md](integrate/README.md) — harness hub
- [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md) — mapping table
- [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md) — community unlock paths
