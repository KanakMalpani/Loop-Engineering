# Canonical specifications

**Schema authority lives on GitHub — not in this repo.**

| Spec | Canonical source |
|------|------------------|
| LSS 1.0 JSON Schema | [Loop-Core-Engineering/specs/lss-1.0.schema.json](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.schema.json) |
| LSS 1.1 composition | [Loop-Core-Engineering/specs/lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md) |
| Schema versioning | [Loop-Core-Engineering/specs/schema-versioning.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/schema-versioning.md) |
| LES 1.0 | [Loop-Core-Engineering/specs/les-1.0.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/les-1.0.md) |
| Loop ID registry | [Loop-Core-Engineering/specs/loop-ids.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/loop-ids.md) |
| Failure taxonomy | [Loop-Core-Engineering/specs/failure-taxonomy.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/failure-taxonomy.md) |
| Validators | [Loop-Core-Engineering/tools/](https://github.com/KanakMalpani/Loop-Core-Engineering/tree/main/tools) |

This discipline repo remains the **narrative mirror**: manifesto, fundamentals, patterns, case studies, loop library.

## Published ecosystem

Version registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md) (discipline repo).

| Repo | URL | Current version |
|------|-----|-----------------|
| Loop Core Engineering | https://github.com/KanakMalpani/Loop-Core-Engineering | LSS 1.0 + **1.1**, LES 1.0 |
| LoopNet | https://github.com/KanakMalpani/loopnet | **v0.2** (545 Tier-1 trajectories) |
| LoopGym | https://github.com/KanakMalpani/LoopGym | PyPI `loopgym` **0.1.1** |
| LoopBench | https://github.com/KanakMalpani/LoopBench | PyPI `loopbench` **0.1.1** |

LoopNet dataset (Tier 1): https://huggingface.co/datasets/KanakMalpani/loopnet-v0.2

Full install map: [ECOSYSTEM.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/ECOSYSTEM.md)

## LES scale

Normalized **`[0, 1]`** is canonical for APIs and storage. Multiply by 100 for human display only.

## Rules

- Do **not** edit `standards/schema/lss-1.0.schema.json` here — open an RFC in [Loop-Core-Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering).
- Prefer `python tools/validate_lss.py` from Loop Core Engineering over local copies.
