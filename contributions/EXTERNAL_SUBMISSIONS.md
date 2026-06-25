# External submission pack

**Start here:** [LOOP_PLAYGROUND.md](./LOOP_PLAYGROUND.md) — test your loop, run benchmarks, submit for recognition.

Ready-to-use paths for the three highest-value **community-owned** adoption signals. Maintainer dry-runs do not count toward the [adoption tracker](../docs/adoption-tracker/latest.md).

---

## 1. LoopBench leaderboard row (issue #4)

**Target:** Non-maintainer submitter on [leaderboard/entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json).

**Step 1 — scaffold with LoopForge:**

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench
```

See [external-template-row.json](../docs/submission-dry-run/external-template-row.json) for the full command block and LoopBench row shape.

1. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench)
2. Add your row to `leaderboard/entries.json` (see existing entries)
3. Open PR — reference [good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

Full guides: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md)

**Other tasks:** LB-RS-1 → [#5](https://github.com/KanakMalpani/Loop-Engineering/issues/5) · LB-MA-1 → [#6](https://github.com/KanakMalpani/Loop-Engineering/issues/6) · LB-COMP-1 → composed spec + [LoopGym composed-swarm-v1](https://github.com/KanakMalpani/LoopGym)

---

## 2. Reproduction report (Discussion #10)

**Target:** Comment on [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) from a **non-maintainer** GitHub account.

Follow [GOLDEN_PATH.md](GOLDEN_PATH.md) (~60 min) or [TEMPLATE-trace-native.md](../docs/reproduction-reports/TEMPLATE-trace-native.md). Include in your post:

- Fork URL
- `python scripts/validate_loop_library.py` result
- One `loopbench run` or `loopgym` replay command + LES_obs snippet
- What was unclear (helps us fix docs)

Template:

```markdown
## Reproduction report — [your org/handle]

- Fork: https://github.com/YOU/Loop-Engineering
- Validator: pass (9 atomic + 5 composed)
- Benchmark: loopbench run --task LB-CR-1 ... → LES_obs X.X
- Time: ~NN min
- Friction: (one sentence)
```

---

## 3. External case study (issue #7)

**Target:** New `case-studies/<org>-*.md` from an org **not** already in the catalog.

### PR checklist

1. **New file** under `case-studies/<org>-<topic>.md` (kebab-case, org prefix required)
2. **Template sections** from [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md):
   - Tuple **L = (S, A, O, T, E, M, τ)** filled in
   - At least one **LES** score (structural from `loopctl score` and/or observed from trace)
   - Pattern + taxonomy level (L1–L6)
3. **LoopForge mapping** — attach or link LSS YAML:
   ```bash
   pip install le-loopforge le-loopctl
   loopforge intent "YOUR AGENT LOOP DESCRIPTION" -o mapped.yaml --suggest-level
   loopctl validate mapped.yaml
   loopctl score --spec mapped.yaml --json
   ```
4. **Harness bridge** — map to LangGraph / CrewAI / custom via [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md)
5. **Optional trace** — Loop Trace 1.0 + `loopctl observed` for observed LES
6. Open PR referencing [good-first #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7)

**Starter examples:** [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md) · [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md)

**Exam cross-link:** Practitioner exam pilot [#12](https://github.com/KanakMalpani/Loop-Engineering/issues/12) · [exam-v0.2.md](../education/practitioner/exam-v0.2.md)

---

## Campaign

Re-run maintainer outreach: `python scripts/adoption_wave8.py` · `python scripts/adoption_wave7.py`

Community handoff: [COMMUNITY_HANDOFF_PHASE4.md](COMMUNITY_HANDOFF_PHASE4.md) · [ADOPTION.md](ADOPTION.md)
