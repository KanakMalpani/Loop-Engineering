## Reproduction v3 — PyPI install names

Use **`le-loopforge`** and **`le-loopctl`** on PyPI (CLI commands remain `loopforge` / `loopctl`).

Do **not** `pip install loopforge` or `pip install loopctl` — those are unrelated packages. See https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PYPI_NAMING.md

Required artifacts:
1. LoopForge command output (`loopforge new`, `fork`, or `intent`)
2. `loopctl validate` pass
3. Loop Trace 1.0 JSON
4. Observed LES composite (`loopctl observed trace.json --json`)
5. Optional LoopBench `results.json`

Reference dry-run: https://github.com/KanakMalpani/Loop-Engineering/tree/main/docs/submission-dry-run

Recommended install:

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench
```
