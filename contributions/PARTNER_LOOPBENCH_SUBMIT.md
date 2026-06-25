# Partner LoopBench submission (30 minutes)

For maintainers invited via [adoption wave 11](../scripts/adoption_wave11.py) — Agentless, Aider, OpenHands, and similar repair loops.

**Goal:** First **non-maintainer** row on [LoopBench](https://kanakmalpani.github.io/LoopBench/) for task **LB-CR-1** (code repair).

---

## Prerequisites

```bash
pip install "le-loop-stack[bench]>=0.1.0"
```

Partner LSS stubs: [`docs/submission-dry-run/partner/`](../docs/submission-dry-run/partner/)

| Harness | Starter spec |
|---------|--------------|
| Agentless | [agentless-lb-cr-1.yaml](../docs/submission-dry-run/partner/agentless-lb-cr-1.yaml) |
| Aider | [aider-lb-cr-1.yaml](../docs/submission-dry-run/partner/aider-lb-cr-1.yaml) |
| OpenHands | [openhands-lb-cr-1.yaml](../docs/submission-dry-run/partner/openhands-lb-cr-1.yaml) |

---

## Steps

### 1. Fork and customize spec

```bash
git clone https://github.com/KanakMalpani/Loop-Engineering.git
cd Loop-Engineering
cp docs/submission-dry-run/partner/agentless-lb-cr-1.yaml my-lb-cr-1.yaml
# Edit workers/evaluators to match your harness
loopctl validate my-lb-cr-1.yaml
```

Or generate from intent:

```bash
python scripts/run_submission_dryrun.py --partner agentless
```

### 2. Run benchmark (SimEnv — no API keys)

```bash
loopbench run --task LB-CR-1 --spec my-lb-cr-1.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

### 3. Fork LoopBench and add your row

1. Fork [KanakMalpani/LoopBench](https://github.com/KanakMalpani/LoopBench)
2. Copy [`entries-row-template.json`](../docs/submission-dry-run/partner/entries-row-template.json) fields into `leaderboard/entries.json`
3. Set `submitter` to your org/handle, `spec_path` to a **public HTTPS URL** to your YAML, `repro_command` to your exact run
4. Open PR — CI runs validate + render automatically

### 4. Link back

- Comment on [Loop-Engineering #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) with PR link
- Optional: post summary on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)

---

## Maintainer review

Human merge required. Checklist: [ROW_SCHEMA.md](https://github.com/KanakMalpani/LoopBench/blob/main/leaderboard/ROW_SCHEMA.md)

Response SLA and pairing: [EXTERNAL_ROW_PLAYBOOK.md](../docs/maintainer/EXTERNAL_ROW_PLAYBOOK.md)

---

## Recognition

- Named row on [live leaderboard](https://kanakmalpani.github.io/LoopBench/)
- [Contributor badge](../docs/community/CONTRIBUTOR_BADGE.md) + [Community spotlight](../docs/community/spotlight/) when merged
