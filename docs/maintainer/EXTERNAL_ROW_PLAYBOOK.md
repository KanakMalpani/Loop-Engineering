# External LoopBench row — maintainer playbook

When a partner or community member responds to [adoption wave 11](../../scripts/adoption_wave11.py) outreach or opens a LoopBench PR.

---

## Response SLA

| Event | Action | Target time |
|-------|--------|-------------|
| New comment on outreach issue | Reply with [PARTNER_LOOPBENCH_SUBMIT.md](../../contributions/PARTNER_LOOPBENCH_SUBMIT.md) link + offer 15-min pairing | 24h |
| LoopBench PR opened (`entries.json`) | Acknowledge on PR + link [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) | 24h |
| Valid PR (CI green) | Human review + merge | 48h |
| Merge complete | Update spotlight draft; comment on #4 and Discussion #10 | 24h |

---

## Review checklist

1. `submitter` is **not** a maintainer marker (see `leaderboard_common.py` INTERNAL_SUBMITTER_MARKERS)
2. `loopbench validate results.json` passes in CI
3. `repro_command` matches actual run
4. `spec_path` is public HTTPS; `spec_hash` matches YAML bytes
5. Seeds documented (default `0,1,2,3,4`)
6. Set `verified_external: true` on merge if schema supports it

Full schema: [ROW_SCHEMA.md](../../docs/ecosystem-sync/LoopBench/leaderboard/ROW_SCHEMA.md)

---

## Pairing session (15 min)

1. Share partner stub: `docs/submission-dry-run/partner/<harness>-lb-cr-1.yaml`
2. Run together: `python scripts/run_submission_dryrun.py --partner agentless`
3. Walk through LoopBench fork → PR → CI
4. Post PR link on [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

---

## Outreach issue tracker

| Repo | Issue | Partner stub |
|------|-------|--------------|
| OpenAutoCoder/Agentless | [#86](https://github.com/OpenAutoCoder/Agentless/issues/86) | `agentless-lb-cr-1.yaml` |
| Aider-AI/aider | [#5328](https://github.com/Aider-AI/aider/issues/5328) | `aider-lb-cr-1.yaml` |
| OpenHands/OpenHands | [#14984](https://github.com/OpenHands/OpenHands/issues/14984) | `openhands-lb-cr-1.yaml` |

Monitor via [ecosystem digest](../../scripts/ecosystem_digest.py) on ops issue [#13](https://github.com/KanakMalpani/Loop-Engineering/issues/13).

---

## Explicit non-goals

- Do not merge maintainer rows as external
- Do not auto-merge without human review
- Do not create fake external accounts or bot submissions
