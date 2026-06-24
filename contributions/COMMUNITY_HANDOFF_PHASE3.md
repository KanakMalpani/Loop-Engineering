# Community handoff — Phase 3 adoption signals

Maintainer infrastructure for the **five yellow** adoption tracker signals. These require **non-maintainer** accounts to flip green.

**Tracker:** [docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md)  
**One-pager:** [ADOPTION.md](ADOPTION.md)

---

## Signal 1: External LoopBench row (#4)

| Step | Action |
|------|--------|
| 1 | Pick a BEAT guide: [CR](BEAT_LB-CR-1.md) · [RS](BEAT_LB-RS-1.md) · [MA](BEAT_LB-MA-1.md) · [COMP](BEAT_LB-COMP-1.md) |
| 2 | `loopbench run` + `loopbench validate` |
| 3 | PR to [LoopBench leaderboard](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) |
| 4 | Comment on [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) |

Maintainer cannot satisfy this signal — use a personal or org account that is not `KanakMalpani`.

---

## Signal 2: Discussion #10 external reproduction

Follow [REPRODUCE.md](REPRODUCE.md) (~60 min). Post template from [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md) §2.

**Composed path (new in Phase 3):**

```bash
pip install loopgym
python -c "import loopgym as lg; print(lg.make('loopbench/composed-swarm-v1').run_episode(task_id='comp-001', seed=0))"
```

---

## Signal 3: Discussion #11 framework feedback

Post a mapping note for LangGraph or CrewAI:

- [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md)
- [crewai-composition-bridge.md](../case-studies/crewai-composition-bridge.md)

Reply on [#11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) or linked framework issues.

---

## Signal 4: External case study (#7)

Use [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md). Map tuple **L = (S, A, O, T, E, M, τ)** + LES.

Open PR referencing [#7](https://github.com/KanakMalpani/Loop-Engineering/issues/7).

---

## Maintainer support (already shipped)

- `python scripts/adoption_wave3.py` — BEAT quad announcement + stale ping
- Four BEAT guides + [ADOPTION.md](ADOPTION.md)
- LoopGym `loopbench/composed-swarm-v1` env
- [COMMUNITY-SUBMISSION](https://github.com/KanakMalpani/loopnet/blob/main/guides/COMMUNITY-SUBMISSION.md) linked from [LOOPNET.md](../research/LOOPNET.md)

Questions: open a thread on Discussion #10.
