# 01 — loop-engineering-core

## One-line purpose

**Canonical home for Loop Engineering specifications** — LSS, LES, taxonomy, patterns, and the constitution every other repo imports.

## Relationship to existing repo

The living docs today live at:

https://github.com/KanakMalpani/Loop-Engineering

This folder plans either:

- **Option A:** Treat `Loop Engineering` as this repo (symlink or note in README), or  
- **Option B:** Split specs into `loop-engineering-core` and keep `Loop Engineering` as the public marketing/docs mirror.

**Decision (2026-06-13):** **Option B** — specs canonical in this repo; `Loop Engineering` is narrative mirror. See [SYNC.md](SYNC.md).

## Scope (in scope)

- LSS JSON Schema + semver policy
- LES formula spec + reference calculator
- Taxonomy + pattern IDs (stable slugs)
- Loop failure taxonomy codes
- Cross-repo API contracts (env IDs, metric names)
- RFC template for spec changes

## Scope (out of scope)

- Runnable benchmarks → `06-loopbench`
- Dataset storage → `04-loopnet`
- Gym runtime → `05-loopgym`
- Institute governance → `12-loop-institute`

## Deliverables v0.1

- [x] `specs/lss-1.0.schema.json` (single canonical copy)
- [x] `specs/les-1.0.md`
- [x] `specs/loop-ids.md` (pattern slugs, failure codes, env prefixes)
- [x] `CHANGELOG.md` semver rules
- [x] CI: schema validation on all example YAMLs

## Dependencies

None — **this repo is the root of the dependency graph**.

## Consumers

All other folders in `All about loops/`.

## Success criteria

Another repo can pin `lss@1.0.0` and validate YAML without copying schema.

## Agent instructions

When implementing: consolidate duplicate LSS/LES from `Loop Engineering` repo; pick 0–100 vs 0–1 LES scale and document; publish semver policy.

## Status

✅ v0.1 shipped (2026-06-13) — see [STATUS.md](./STATUS.md)
