# LoopForge scaffold demo

Generates example LSS specs for every built-in pattern using [LoopForge](../../loopforge/).

## Run

```bash
python examples/loopforge-scaffold/run_demo.py
```

Output lands in `generated/` (gitignored). Each file is validated against `standards/schema/lss-1.0.schema.json` before write.

## Create your own loop

```bash
python -m loopforge new \
  --pattern reflection \
  --name my-bug-fixer \
  --objective "Fix failing tests from a bug report" \
  --output loop-library/my-bug-fixer.yaml
```

See [00-planning/LOOP_FORGE.md](../../00-planning/LOOP_FORGE.md) for the full guide.
