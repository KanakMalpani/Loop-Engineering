# Changelog

All notable changes to Loop Engineering core specifications follow [Semantic Versioning 2.0.0](https://semver.org/).

## Semver policy

Applies to **LSS** (`lss-1.0.schema.json`), **LES** (`les-1.0.md`), and **Loop ID registry** (`loop-ids.md`).

| Bump | When |
|------|------|
| **MAJOR** | Breaking schema change; removed/rename required field; changed LES formula or weight; removed failure code or env ID |
| **MINOR** | Additive schema field (optional); new pattern slug; new failure code; new metric name; new env prefix family |
| **PATCH** | Documentation clarifications; example fixes; non-normative typo fixes; stricter validation that accepts all prior valid documents |

### Pin format

Downstream repos declare pins in dependency metadata:

```
lss@1.0.0
les@1.0.0
```

Patch releases do not require consumer updates unless they opt into stricter validation. Major releases require explicit migration.

### RFC process

Normative changes start as RFCs using [`templates/rfc-template.md`](templates/rfc-template.md). Governance moves to `12-loop-institute` in Phase D; until then, RFCs live in this repo's `rfcs/` directory (optional).

### Relationship to loop `version` field

The `version` field **inside** an LSS YAML document is semver for **that loop design**, independent of the LSS **schema** version (`lss@1.0.0`).

---

## [1.0.0] - 2026-06-13

### Added

- Canonical `specs/lss-1.0.schema.json` (consolidated from `Loop Engineering/standards/schema/`)
- `specs/les-1.0.md` — LES composite formulas; **canonical scale `[0, 1]`**, optional display `0–100`
- `specs/loop-ids.md` — pattern slugs, failure codes F1–F12, env ID prefixes, standard metrics
- `specs/lss-1.0.md` — schema home summary
- `examples/` — minimal, research, multi-agent LSS fixtures
- `tools/validate_lss.py`, `tools/validate_all_examples.py`, `tools/les_calculator.py`
- CI workflow validating all example YAMLs against schema
- RFC template for future spec changes

### Decisions

- **Single schema copy** lives in `01-loop-engineering-core`; `Loop Engineering` discipline repo remains narrative mirror until symlink/split decision (PLAN Option A/B).
- **LES scale:** normalized `[0, 1]` is normative for APIs; `× 100` display is optional for humans/leaderboards.

[1.0.0]: https://github.com/loop-engineering/loop-engineering-core/releases/tag/v1.0.0
