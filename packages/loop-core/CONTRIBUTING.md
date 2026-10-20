# Contributing to Loop Core Engineering

Thank you for helping build the canonical spec layer for Loop Engineering.

## What belongs here

- LSS JSON Schema and overview docs
- LES formula definitions
- Loop ID registry (pattern slugs, failure codes, env prefixes)
- Validators and design-time LES tools
- RFCs for spec changes

## What does not belong here

- Narrative docs (manifesto, patterns, case studies) — discipline / docs repo
- Runtime execution — [LoopGym](https://github.com/KanakMalpani/LoopGym)
- Benchmark tasks — [LoopBench](https://github.com/KanakMalpani/LoopBench)
- Dataset records — [LoopNet](https://github.com/KanakMalpani/loopnet)

## Spec changes

1. Open an RFC using [`templates/rfc-template.md`](templates/rfc-template.md)
2. Update schema, examples, and `CHANGELOG.md` in the same PR
3. Ensure CI passes: `python tools/validate_all_examples.py`

## Development setup

```bash
pip install -r requirements.txt
python tools/validate_all_examples.py
```

## License

By contributing, you agree that your contributions are licensed under the MIT License.
