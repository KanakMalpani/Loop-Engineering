# Loop Engineering — Status Q1 2027 (Phase 11)

**Date:** 2026-06-25  
**Phase:** 11 Platform Gravity — **maintainer complete**; community unlocks pending

---

## Shipped (Phase 11)

| Item | Artifact |
|------|----------|
| Portable scoring | `loopctl/scoring/` · `le-loopctl` **0.2.0** |
| Meta-package | `le-loop-stack` **0.1.0** · [stack/](../stack/) |
| Golden Path v3 | [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) |
| Integration hub | [integrate/README.md](../contributions/integrate/README.md) |
| Claude Code pack | [CLAUDE_CODE.md](../contributions/integrate/CLAUDE_CODE.md) · [claude-code-agent-loop.md](../case-studies/claude-code-agent-loop.md) |
| Codex pack | [CODEX.md](../contributions/integrate/CODEX.md) |
| OpenAI Agents export | `openai_agents` target · [OPENAI_AGENTS.md](../contributions/integrate/OPENAI_AGENTS.md) |
| Aider + Gemini CLI | [AIDER.md](../contributions/integrate/AIDER.md) · [GEMINI_CLI.md](../contributions/integrate/GEMINI_CLI.md) |
| Copilot / Devin bridges | [COPILOT.md](../contributions/integrate/COPILOT.md) · [DEVIN.md](../contributions/integrate/DEVIN.md) |
| Adoption wave 10 | [adoption_wave10.py](../scripts/adoption_wave10.py) |
| LoopNet HF preview path | [HF-v0.3-preview.md](../docs/loopnet/HF-v0.3-preview.md) |

---

## Community (still yellow)

[docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md)

| Signal | Action |
|--------|--------|
| External LoopBench #4 | [outreach README](../docs/outreach/README.md) · wave 11/12 partner outreach |
| Discussion #10 repro | Trace-native template + Golden Path v3 |
| Issue #7 case study | Claude Code / Codex mappers |
| Discussion #11 RFC | Framework tuple replies |
| Exam pilots #12 | Integration-themed pilot |

---

## PyPI targets

| Package | Version |
|---------|---------|
| le-loop-stack | 0.1.0 |
| le-loopctl | 0.2.0 |
| le-loopforge | 0.2.1 |
| loopgym | 0.1.2 |

Registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)

---

## CI

Daily check-in: ~30 checks including pip-only stack/score smokes and integrate harness demos.

```bash
python scripts/daily_checkin.py
```
