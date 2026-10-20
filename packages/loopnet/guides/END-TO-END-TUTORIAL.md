# End-to-end tutorial — LoopNet v0.2

Load the corpus, replay a captured LoopGym trajectory at zero API cost, then score a fresh SimEnv run with LoopBench.

**Time:** ~5 minutes · **Cost:** $0 (SimEnv + ReplayEnv only)

## Prerequisites

```bash
pip install loopgym loopbench
pip install datasets   # optional — load from Hugging Face instead of a local clone
```

Clone the repos side by side (or set env paths below):

```
All about loops/
  04-loopnet/          ← you are here
  05-loopgym/
  06-loopbench/
```

## Run the script

```bash
cd loopnet
python examples/v02_workflow.py
```

Or load from Hugging Face without a local JSONL file:

```bash
pip install datasets
python examples/v02_workflow.py
```

## What happens (three steps)

### 1. Load LoopNet v0.2

The script loads [KanakMalpani/loopnet-v0.2](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2) from the Hub when `datasets` is installed, otherwise `data/v0.2/records.jsonl` from this repo.

It picks the first **captured** record (`metadata.tags` contains `captured` — produced by `loopgym capture`).

### 2. Replay in LoopGym (zero tokens)

```python
import loopgym as lg

env = lg.make("replay/loopnet-v1", records_path="data/v0.2/records.jsonl")
result = env.run_episode(record_id="ln-37ecfbbf-174b-47d9-8271-2e956f741aac")

print(result["captured"])       # True
print(result["quality_score"])  # final goal_score from corpus
print(result["les_observed"])   # LES stored at capture time
```

ReplayEnv walks the stored trajectory — no LLM calls, no API keys.

### 3. Score with LoopBench (SimEnv)

The captured record maps to `loopbench/code-repair-v1` task `cr-001`. LoopBench runs a **new** mock-LLM episode and computes observed LES:

```bash
loopbench run --task LB-CR-1 \
  --spec ../06-loopbench/submissions/examples/spec-fast-loop.yaml \
  --seeds 0
```

Compare:

| Source | What it measures |
|--------|------------------|
| `record["les_observed"]` | LES at capture time (ground truth in corpus) |
| LoopBench `aggregate.les_observed` | LES from a fresh SimEnv run with your LSS spec |

They will differ — that is expected. Replay reproduces history; LoopBench evaluates your loop design.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `LOOPNET_RECORDS_PATH` | Override path to `records.jsonl` |
| `LOOPBENCH_SPEC` | Override path to LSS YAML for `loopbench run` |

## Next steps

- **Capture more data:** `loopgym capture loopbench/code-repair-v1 ...` — see [V0.2-PLAN.md](../V0.2-PLAN.md)
- **Contribute records:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Observability (Path A):** [07-loop-observability](../07-loop-observability/PLAN.md) — LTF traces from LoopGym runs

## Links

- [LoopNet on Hugging Face](https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2)
- [LoopGym ReplayEnv](https://github.com/KanakMalpani/LoopGym/blob/main/docs/api.md#replayenv-replay)
- [LoopBench CLI](https://github.com/KanakMalpani/LoopBench)
