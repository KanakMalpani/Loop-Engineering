# Loop Playground — test your own loop

**Single entry point:** declare a loop, score it, run a benchmark, submit for recognition.

**North star:** [NORTH_STAR.md](./NORTH_STAR.md) · **Live rankings:** [LoopBench leaderboard](https://github.com/KanakMalpani/LoopBench) · **Status:** [COMMUNITY_PLATFORM_STATUS.md](../docs/maintainer/COMMUNITY_PLATFORM_STATUS.md)

---

## 60-second path (no benchmark)

```bash
pip install "le-loop-stack>=0.1.0"

loopforge intent "Fix failing tests with minimal diff" -o my-loop.yaml --suggest-level
loopctl validate my-loop.yaml
loopctl score --spec my-loop.yaml --json
```

You now have a validated LSS spec and structural LES. Optional: [Golden Path v3](./GOLDEN_PATH.md) for export + LoopGym trace.

---

## Benchmark path (observed LES)

Run on fixed tasks and seeds — results are auditable.

| Task | Guide | Good-first issue |
|------|-------|------------------|
| LB-CR-1 Code repair | [BEAT_LB-CR-1.md](./BEAT_LB-CR-1.md) | [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) |
| LB-RS-1 Research synthesis | [BEAT_LB-RS-1.md](./BEAT_LB-RS-1.md) | [#5](https://github.com/KanakMalpani/Loop-Engineering/issues/5) |
| LB-MA-1 Multi-agent debate | [BEAT_LB-MA-1.md](./BEAT_LB-MA-1.md) | [#6](https://github.com/KanakMalpani/Loop-Engineering/issues/6) |
| LB-COMP-1 Composed swarm | [BEAT_LB-COMP-1.md](./BEAT_LB-COMP-1.md) | composed spec + LoopGym |

**Typical run:**

```bash
pip install "le-loop-stack>=0.1.0" loopbench loopgym pyyaml jsonschema

loopbench run \
  --task LB-CR-1 \
  --spec my-loop.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json

loopbench validate results.json
```

Fork a [loop-library](../loop-library/) spec or start from [external-template-row.json](../docs/submission-dry-run/external-template-row.json).

---

## Submit for recognition

1. Post a short summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) (optional but helps docs).
2. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench).
3. Add your row to `leaderboard/entries.json` (see [ROW_SCHEMA.md](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/ROW_SCHEMA.md) after sync).
4. Open PR — reference the matching good-first issue ([#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) for LB-CR-1).

After merge, you appear on the [live board](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/LIVE.md) and may be featured in the [monthly spotlight](../docs/community/spotlight/).

**Contributor badge:** [CONTRIBUTOR_BADGE.md](../docs/community/CONTRIBUTOR_BADGE.md)

---

## Two contribution paths

| Goal | Where | Reward |
|------|-------|--------|
| Beat a benchmark | LoopBench PR (`entries.json`) | Leaderboard row + optional spotlight |
| Contribute curated spec | `loop-library/` PR on Loop-Engineering | Library catalog + docs |

Maintainer dry-runs do **not** count toward [adoption tracker](../docs/adoption-tracker/latest.md) external signals.

---

## Minimum bar for public listing

| Requirement | Why |
|-------------|-----|
| Non-maintainer GitHub identity | Credibility for community adoption |
| `loopbench validate results.json` pass | Schema + anti-gaming |
| `spec_path` or `spec_uri` pointing to your YAML | Others can inspect the loop |
| Documented seeds (default `0,1,2,3,4`) | Reproducibility |
| `repro_command` in row (single-line) | One-click re-run for reviewers |

Optional row fields: `harness` (`native`, `cursor`, `langgraph`, `crewai`), `trace_uri`, `verified_external: true` (set by maintainer on merge).

Full template: [external-template-row.json](../docs/submission-dry-run/external-template-row.json)

---

## Map your harness

Already running agents in Cursor, LangGraph, or CrewAI? Map first — no runtime swap required.

→ [integrate/README.md](./integrate/README.md) · [BRIDGE_AGENT_HARNESSES.md](./BRIDGE_AGENT_HARNESSES.md)

---

## See also

- [EXTERNAL_SUBMISSIONS.md](./EXTERNAL_SUBMISSIONS.md) — reproduction + case study paths
- [GOLDEN_PATH.md](./GOLDEN_PATH.md) — 15-minute integrate path
- [REPRODUCE.md](./REPRODUCE.md) — full reproduction challenge
