# External submission pack

Ready-to-use paths for the three highest-value **community-owned** adoption signals. Maintainer dry-runs do not count toward the [adoption tracker](../docs/adoption-tracker/latest.md).

---

## 1. LoopBench leaderboard row (issue #4)

**Target:** Non-maintainer submitter on [leaderboard/entries.json](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/entries.json).

**Step 1 — scaffold with LoopForge:**

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopbench>=0.1.1" "loopgym>=0.1.2" pyyaml jsonschema
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering

loopforge fork --from autonomous-debugger --name my-submission -o my-submission.yaml --suggest-level
python -m loopctl validate my-submission.yaml
```

```bash
loopbench run \
  --task LB-CR-1 \
  --spec my-submission.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

1. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench)
2. Add your row to `leaderboard/entries.json` (see existing entries)
3. Open PR — reference [good-first #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

Full guides: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md)

**Other tasks:** LB-RS-1 → [#5](https://github.com/KanakMalpani/Loop-Engineering/issues/5) · LB-MA-1 → [#6](https://github.com/KanakMalpani/Loop-Engineering/issues/6) · LB-COMP-1 → composed spec + [LoopGym composed-swarm-v1](https://github.com/KanakMalpani/LoopGym)

---

## 2. Reproduction report (Discussion #10)

**Target:** Comment on [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) from a **non-maintainer** GitHub account.

Follow [GOLDEN_PATH.md](GOLDEN_PATH.md) (~60 min). Include in your post:

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

Use [case-studies/TEMPLATE.md](../case-studies/TEMPLATE.md):

- Tuple **L = (S, A, O, T, E, M, τ)** filled in
- At least one **LES** score (structural or observed)
- Link to your LSS YAML or harness mapping via [BRIDGE_AGENT_HARNESSES.md](BRIDGE_AGENT_HARNESSES.md)

Open PR referencing [good-first #7](https://github.com/KanakMalpani/Loop-Engineering/issues/7).

**Example maintainer bridge (extend or copy):** [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md)

---

## Campaign

Re-run maintainer outreach: `python scripts/adoption_wave2.py` · `python scripts/adoption_wave3.py`

Community handoff: [COMMUNITY_HANDOFF_PHASE4.md](COMMUNITY_HANDOFF_PHASE4.md) · [ADOPTION.md](ADOPTION.md)
