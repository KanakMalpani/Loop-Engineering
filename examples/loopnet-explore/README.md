# LoopNet v0.2 Explorer

Load the public Tier-1 corpus from Hugging Face and print summary statistics. No API keys required.

## Prerequisites

```bash
pip install datasets
```

## Run

From repository root:

```bash
python examples/loopnet-explore/explore.py
```

## Output

- Record count
- Column names
- Top patterns, taxonomy levels, termination reasons (when present)
- Iteration count min/max/mean
- CTA to [reproduction challenge](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)

See [research/LOOPNET.md](../../research/LOOPNET.md) for schema details and P4 empirical findings.
