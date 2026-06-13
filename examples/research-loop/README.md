# Research Loop Example

Gather → synthesize → verify: iterative research with source-quality evaluation.

## Run

```bash
python EXAMPLES/research-loop/run.py
python EXAMPLES/research-loop/run.py --topic "multi-agent feedback loops"
python EXAMPLES/research-loop/run.py --iterations 3 --json
```

## Spec

Defaults to `standards/examples/research-loop.yaml`. Create that file or pass `--spec`.

## Evaluator Logic

Passes when the mock output cites enough sources (keyword markers) or max iterations is reached.
