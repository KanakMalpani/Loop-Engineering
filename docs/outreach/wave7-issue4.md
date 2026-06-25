## Adoption wave 7 — trace-native LoopBench row

PyPI packages (note names — `loopforge` on PyPI is a different project):

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench

loopforge intent "Fix failing tests from CI" -o my-loop.yaml --suggest-level
loopctl validate my-loop.yaml

python -c "
import loopgym as lg
env = lg.make('loopbench/code-repair-v1')
env.run_episode(task_id='cr-001', seed=42, trace_path='trace.json')
"

loopctl trace validate trace.json
loopctl observed trace.json --spec my-loop.yaml --json
loopbench run --task LB-CR-1 --spec my-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

- Golden Path: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/GOLDEN_PATH.md
- BEAT template: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BEAT_TEMPLATE.md
- LoopNet v0.3: https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/loopnet/CONTRIBUTING-v0.3.md
- Maintainer dry-run: https://github.com/KanakMalpani/Loop-Engineering/tree/main/docs/submission-dry-run
- PyPI naming: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PYPI_NAMING.md
