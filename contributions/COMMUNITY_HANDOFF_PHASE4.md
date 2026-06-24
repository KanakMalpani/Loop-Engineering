# Community handoff — Phase 4 (composed env + PyPI)

Phase 4 closes the LB-COMP-1 fidelity gap. Community signals still require **non-maintainer** accounts.

**Tracker:** [docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md)  
**One-pager:** [ADOPTION.md](ADOPTION.md)

---

## What changed in Phase 4

| Item | Status |
|------|--------|
| LoopBench LB-COMP-1 | Uses `loopbench/composed-swarm-v1` (not MA-1 proxy) |
| Maintainer COMP LES | **80.3** ([lb-comp-1-baseline.json](../benchmarks/results/lb-comp-1-baseline.json)) |
| loopgym PyPI | Target **0.1.1** with composed env |
| BEAT guides | All four tasks; COMP target updated |

---

## Fastest wins (unchanged owner: community)

### LoopBench row (#4)

```bash
pip install "loopbench>=0.1.1" "loopgym>=0.1.1"
# Pick any BEAT guide → loopbench run → validate → LoopBench PR
```

Guides: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [RS](BEAT_LB-RS-1.md) · [MA](BEAT_LB-MA-1.md) · [COMP](BEAT_LB-COMP-1.md)

### Reproduction (#10)

[REPRODUCE.md](REPRODUCE.md) — include composed smoke:

```bash
python -c "import loopgym as lg; print(lg.make('loopbench/composed-swarm-v1').run_episode(task_id='comp-001', seed=0))"
```

### Case study (#7)

[TEMPLATE.md](../case-studies/TEMPLATE.md) — LangGraph / CrewAI bridge case studies are maintainer examples; submit an **org not in catalog**.

---

## Maintainer outreach

```bash
python scripts/adoption_wave4.py
```

See also [COMMUNITY_HANDOFF_PHASE3.md](COMMUNITY_HANDOFF_PHASE3.md) for signal checklist.
