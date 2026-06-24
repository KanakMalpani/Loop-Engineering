# Adoption — flip the tracker green

One-page guide for **community-owned** adoption signals. Maintainer dry-runs do not count.

**Live dashboard:** [docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md) (updated daily)

---

## Fastest wins

| Goal | Path | Target |
|------|------|--------|
| LoopBench row | [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [RS-1](BEAT_LB-RS-1.md) · [MA-1](BEAT_LB-MA-1.md) · [COMP-1](BEAT_LB-COMP-1.md) | Non-maintainer PR on [LoopBench leaderboard](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json) |
| Reproduction report | [REPRODUCE.md](REPRODUCE.md) (~60 min) | Comment on [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) from **non-maintainer** account |
| Case study | [TEMPLATE.md](../case-studies/TEMPLATE.md) | PR → [#7](https://github.com/KanakMalpani/Loop-Engineering/issues/7) |
| RFC feedback | [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) | LangGraph / CrewAI mapping note |

Full pack: [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md)

---

## Maintainer outreach

```bash
python scripts/adoption_wave2.py   # checklist + framework pings
python scripts/adoption_wave3.py # Phase 3 BEAT quad + stale-issue ping
python scripts/adoption_wave4.py # Phase 4 HF + LoopBench + framework comments
```

---

## Bounty wording (issues #4, #7)

**#4:** First **non-maintainer** LoopBench row beating maintainer LES on any of CR/RS/MA/COMP gets leaderboard credit + Discussion #10 shout-out.

**#7:** First **external org** case study (not in catalog) with tuple + LES merged closes the 2027 adoption gap.

Labels: `good-first`, `adoption`
