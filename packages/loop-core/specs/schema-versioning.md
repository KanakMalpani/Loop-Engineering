# JSON Schema Versioning Policy (LSS / LES)

**Status:** Stable (June 2026)  
**Applies to:** Loop-Core-Engineering `specs/*.schema.json`, discipline mirror under `standards/schema/`

---

## Semver rules

| Bump | When |
|------|------|
| **MAJOR** | Breaking change to required fields or enum semantics |
| **MINOR** | Backward-compatible extension (e.g. LSS 1.1 optional `composition`) |
| **PATCH** | Documentation, `$id` URL, non-semantic constraint tightening with RFC |

LSS **1.0** specs remain valid without migration when **1.1** adds optional blocks only.

---

## Draft vs stable

| Stage | Filename | Validator behavior |
|-------|----------|-------------------|
| Draft | `lss-1.1-draft.md` | Warn-only in discipline repo |
| Stable | `lss-1.1.md` | Canonical; Loop-Core `$schema` URLs point here |
| Deprecated | `*-deprecated.md` | 90-day sunset in CHANGELOG |

Promotion requires: RFC discussion + 30-day comment window OR explicit errata merge.

---

## `$schema` URL pattern

```
https://raw.githubusercontent.com/KanakMalpani/Loop-Core-Engineering/main/specs/lss-1.0.schema.json
https://raw.githubusercontent.com/KanakMalpani/Loop-Core-Engineering/main/specs/lss-1.1-composition.schema.json
```

Discipline copies are **mirrors** — open RFCs against Loop-Core-Engineering first.

---

## Cross-repo sync

On release:

1. Update Loop-Core `specs/` + `ECOSYSTEM.md`
2. Mirror to Loop-Engineering [ECOSYSTEM_VERSIONS.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/ECOSYSTEM_VERSIONS.md)
3. Bump PyPI packages if bundled schemas change (`loopbench`, `loopgym`)

---

## Changelog

- **2026-06-24** — Initial policy; LSS 1.1 stable promotion
