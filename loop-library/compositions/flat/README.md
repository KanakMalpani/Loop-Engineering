# Flat pre-merged compositions (zero-compose path)

Token-optimized **single-file** LSS specs — skip runtime `loop combine` for common pairs.

| File | Replaces composition | Use |
|------|---------------------|-----|
| [research-to-writing-flat.yaml](./research-to-writing-flat.yaml) | `research-to-writing` | Research → writing pipeline |
| [debug-repair-flat.yaml](./debug-repair-flat.yaml) | `code-debug-repair` | Code → debug repair |
| [scenario-swarm-rehearsal-flat.yaml](./scenario-swarm-rehearsal-flat.yaml) | `scenario-swarm-rehearsal` | Parallel swarm rehearsal |

```bash
loopctl validate loop-library/compositions/flat/debug-repair-flat.yaml
loopctl score --spec loop-library/compositions/flat/debug-repair-flat.yaml --json
loopforge export --format minjson --spec loop-library/compositions/flat/debug-repair-flat.yaml --out /tmp/debug.min.json
loopbench run --suite suite-repair --spec loop-library/compositions/flat/debug-repair-flat.yaml --seeds 0,1,2,3,4 -o results.json
```

Regenerate after library template changes:

```bash
python scripts/generate_flat_compositions.py
```
