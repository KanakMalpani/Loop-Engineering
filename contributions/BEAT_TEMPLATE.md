# BEAT Template — external benchmark submission

Copy-paste pack for non-maintainer LoopBench rows. **Step 1 is always LoopForge.**

---

## 1. Create or fork your spec

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" loopbench loopgym pyyaml jsonschema

# New loop
loopforge new --pattern verification --name my-beat-loop --objective "YOUR TASK" -o my-beat-loop.yaml --suggest-level

# Or fork library template
loopforge fork --from autonomous-debugger --name my-beat-loop -o my-beat-loop.yaml --suggest-level
```

Validate:

```bash
python -m loopctl validate my-beat-loop.yaml
python -m loopctl score --spec my-beat-loop.yaml --json > les.json
```

---

## 2. Run LoopBench

```bash
loopbench list
loopbench run --task LB-CR-1 --spec my-beat-loop.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

Task guides: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md) · [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md) · [BEAT_LB-COMP-1.md](BEAT_LB-COMP-1.md)

---

## 3. Trace + observed LES (recommended)

```bash
python scripts/generate_loopgym_trace_demo.py
loopctl trace validate docs/submission-dry-run/trace-loopgym.json
loopctl observed docs/submission-dry-run/trace-loopgym.json --spec my-beat-loop.yaml --json > observed-les.json
python scripts/loopnet_export_trace.py docs/submission-dry-run/trace-loopgym.json -o loopnet-row.json
```

Full path: [docs/loopnet/CONTRIBUTING-v0.3.md](../docs/loopnet/CONTRIBUTING-v0.3.md) · maintainer reference [submission-dry-run](../docs/submission-dry-run/)

---

## 4. Submit PR to LoopBench

1. Fork [LoopBench](https://github.com/KanakMalpani/LoopBench)
2. Add row to `leaderboard/entries.json`:

```json
{
  "submitter": "Your Name / Org",
  "task": "LB-CR-1",
  "spec": "my-beat-loop.yaml",
  "les_composite": 0.0,
  "notes": "Scaffolded with loopforge fork autonomous-debugger"
}
```

3. Attach `results.json` and `les.json` in PR description
4. Reference [issue #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4)

---

## 5. Report reproduction

Comment on [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) with:

- LoopForge command used
- `loopctl validate` output
- LES composite from `les.json`
- LoopBench validate summary

See [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md) for full adoption paths.
