# LoopNet v0.3 preview corpus

**Status:** Preview (Phase 9) · **Schema:** [schema/record-v0.3.json](../../schema/record-v0.3.json)

Rows in this directory are **flat trace exports** (not full `ln/record-v1` documents). Produce rows with Loop-Engineering:

```bash
pip install le-loopctl
python scripts/loopnet_export_trace.py trace.json -o row.json
python scripts/validate_trace_export.py row.json
```

Sample maintainer dry-run: [dry-run-row.json](./dry-run-row.json)

Discipline-side guide: [Loop-Engineering CONTRIBUTING-v0.3](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/loopnet/CONTRIBUTING-v0.3.md)
