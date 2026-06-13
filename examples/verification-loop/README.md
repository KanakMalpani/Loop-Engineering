# Verification Loop Example

Propose fix → run tests → iterate until evaluators pass (maker-checker pattern).

## Run

```bash
python EXAMPLES/verification-loop/run.py
python EXAMPLES/verification-loop/run.py --json
python EXAMPLES/verification-loop/run.py --spec standards/examples/minimal-loop.yaml
```

## Behavior

Uses the default `LoopRuntime._default_evaluator` pattern: tests fail on iterations 1–2, pass on iteration 3.

Ideal for demonstrating Level-3 verification loops without real test runners.
