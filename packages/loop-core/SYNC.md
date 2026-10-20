# Sync policy — Loop Core Engineering

**Canonical source of truth for Loop Engineering specifications.**

| Artifact | Canonical location | Mirror / narrative |
|----------|-------------------|-------------------|
| LSS JSON Schema | **This repo** `specs/lss-1.0.schema.json` | Discipline docs repo → pointer only |
| LES formulas | **This repo** `specs/les-1.0.md` | cite, do not duplicate formulas |
| Loop ID registry | **This repo** `specs/loop-ids.md` | cite, do not duplicate slugs |
| Validators | **This repo** `tools/` | downstream CI checks out this repo |
| Manifesto, patterns, case studies | Discipline docs repo | not duplicated here |

**Repository:** https://github.com/KanakMalpani/Loop-Core-Engineering

## Rules for downstream repos

1. Pin `lss@1.0.0` and `les@1.0.0` in README or `pyproject.toml`.
2. Validate fixtures in CI against `specs/lss-1.0.schema.json` from this repo (checkout or submodule).
3. **Never fork** the schema into another repo.

## Ecosystem

| Repo | URL |
|------|-----|
| Loop Core Engineering | https://github.com/KanakMalpani/Loop-Core-Engineering |
| LoopNet | https://github.com/KanakMalpani/loopnet |
| LoopGym | https://github.com/KanakMalpani/LoopGym |
| LoopBench | https://github.com/KanakMalpani/LoopBench |

## Consume in CI

```yaml
- uses: actions/checkout@v4
  with:
    repository: KanakMalpani/Loop-Core-Engineering
    path: deps/loop-core
```

Or submodule:

```bash
git submodule add https://github.com/KanakMalpani/Loop-Core-Engineering.git deps/loop-core
```
