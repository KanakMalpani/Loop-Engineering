# Reproduction report — [your org/handle]

**Date:** YYYY-MM-DD  
**Source:** [GOLDEN_PATH.md](../../contributions/GOLDEN_PATH.md) trace-native path  
**Discussion:** [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)

---

## 1. Environment

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench pyyaml jsonschema
pip show le-loopforge le-loopctl loopgym loopbench
python --version
```

Paste `pip show` output here.

---

## 2. LoopForge scaffold

```bash
loopforge intent "YOUR OBJECTIVE" -o repro-loop.yaml --suggest-level
loopctl validate repro-loop.yaml
```

Paste validate output (must pass).

---

## 3. Loop Trace 1.0

```bash
python -c "
import loopgym as lg
env = lg.make('loopbench/code-repair-v1')
result = env.run_episode(task_id='cr-001', seed=42, trace_path='trace.json')
print('success:', result.get('success'), 'iterations:', result.get('iterations'))
"

loopctl trace validate trace.json
```

Attach or link `trace.json` (redact secrets).

---

## 4. Observed LES composite

```bash
loopctl observed trace.json --spec repro-loop.yaml --json
```

Paste JSON snippet with `observed_les` and `structural_les`.

---

## 5. Optional — LoopBench

```bash
loopbench run --task LB-CR-1 --spec repro-loop.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

---

## 6. Friction log

| Step | Time (min) | Unclear? |
|------|------------|----------|
| Install | | |
| LoopForge | | |
| Trace | | |
| Observed LES | | |

One sentence on what we should fix in docs.

---

## Checklist (maintainer verification)

- [ ] Non-maintainer GitHub account
- [ ] `pip show` lists `le-loopforge` / `le-loopctl` (not legacy names)
- [ ] `loopctl validate` pass
- [ ] Valid Loop Trace 1.0
- [ ] Observed LES JSON included

Reference maintainer dry-run: [docs/submission-dry-run/](../submission-dry-run/)
