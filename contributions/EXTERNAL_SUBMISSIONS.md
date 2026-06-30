# External submission pack

**Start here:** [LOOP_PLAYGROUND.md](./LOOP_PLAYGROUND.md) — test your loop, run benchmarks, submit for recognition.

Ready-to-use paths for the three highest-value **community-owned** adoption signals. Maintainer dry-runs do not count toward the [adoption tracker](../docs/adoption-tracker/latest.md).

---

## 1. LoopBench leaderboard row (issue #4)

**Target:** Non-maintainer submitter on [leaderboard/entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json).

### Dual-track policy (Wave 15/16)

| Track | Path | When to use |
|-------|------|-------------|
| **Easy** | Path 1a — single `--task LB-CR-1` | First submission, repair harnesses, wave 11–12 partners |
| **Preferred** | Path 1b — `--suite` + `suite_scores` | Generalist + suite-tab ranking, loop mix recipes |

Both count as external adoption. Suite submissions rank on **generalist** (`grand_composite`) and **per-suite tabs**; single-task rows rank on that task only.

### Path 1a — single task (LB-CR-1 easy on-ramp)

```bash
pip install "le-loop-stack>=0.3.0"
```

See [external-template-row.json](../docs/submission-dry-run/external-template-row.json) for the full command block.

1. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench)
2. Add your row to `leaderboard/entries.json`
3. Open PR — reference [good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

Guide: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · Partner pack: [PARTNER_LOOPBENCH_SUBMIT.md](PARTNER_LOOPBENCH_SUBMIT.md)

### Path 1b — comparison suite (preferred)

```bash
pip install "le-loop-stack>=0.3.0"

loop mix dev-agent --intent "Fix CI tests" -o mixed.yaml --json
loopbench run --suite suite-repair --spec mixed.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

Submit with `suite_scores`, `grand_composite`, optional `primary_suite`, and `partial: false` when all 4 suites are present. Micro-task map: [SUITE-OVERVIEW.md](../docs/ecosystem-sync/LoopBench/docs/SUITE-OVERVIEW.md).

Suite guides: [BEAT_suite-repair.md](BEAT_suite-repair.md) · [BEAT_suite-agent.md](BEAT_suite-agent.md) · [BEAT_suite-knowledge.md](BEAT_suite-knowledge.md) · [BEAT_suite-rigor.md](BEAT_suite-rigor.md)

**Legacy single-task guides:** [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md) · LB-RS-1 → [#5](https://github.com/KanakMalpani/Loop-Engineering/issues/5) · LB-MA-1 → [#6](https://github.com/KanakMalpani/Loop-Engineering/issues/6)

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

Partner outreach: `python scripts/adoption_wave11.py` · follow-up `python scripts/adoption_wave12.py` · **Wave 15 suites:** `python scripts/adoption_wave15.py`

Partner pack: [PARTNER_LOOPBENCH_SUBMIT.md](PARTNER_LOOPBENCH_SUBMIT.md) · Playbook: [EXTERNAL_ROW_PLAYBOOK.md](../docs/maintainer/EXTERNAL_ROW_PLAYBOOK.md)

One-pager: [ADOPTION.md](ADOPTION.md)
