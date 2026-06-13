# Loop Engineering Governance

How the discipline evolves—standards, scoring, taxonomy, and community process.

Loop Engineering is not a standards body with paid membership. It is an **open repository with explicit governance rules** so practitioners can trust that LSS 1.0 today means the same thing tomorrow, and that breaking changes happen predictably.

---

## Principles

1. **Evidence over authority** — claims converge through benchmarks and reproduction, not credentials alone
2. **Declarative core** — loops are specs (LSS), not locked vendor graphs
3. **Safety proportional to autonomy** — higher taxonomy levels require stronger review
4. **Backward compatibility when possible** — semver for standards; migration guides for breaks
5. **Transparent process** — proposals, discussion, and decision records are public in git

---

## Scope of Governance

| Artifact | Maintainer role | Change class |
|----------|-----------------|--------------|
| LSS (Loop Specification Standard) | Standards stewards | Major / minor / patch |
| LES (Loop Engineering Score) | Scoring stewards | Major / minor / patch |
| Taxonomy levels | Architecture council | Major (rare) |
| Patterns, case studies, library | Community PR | Continuous |
| Research docs | Community PR + council review for AGI/safety claims | Continuous |
| Tools | Community PR | Continuous |
| This GOVERNANCE.md | Maintainers + community RFC | Major |

---

## Roles

### Maintainers

- Triage issues and PRs
- Enforce CODE_OF_CONDUCT
- Merge when review criteria met
- Appoint stewards for LSS/LES

*Initial maintainers: repository owners; list in GitHub team `loop-engineering/maintainers`.*

### Standards stewards (LSS)

- Review schema changes
- Run validator against full `loop-library/`
- Publish migration notes

### Scoring stewards (LES)

- Review dimension definitions and weighting guidance
- Ensure calculator matches spec
- Coordinate benchmark corpus updates when LES majors change

### Architecture council

- Adjudicate taxonomy changes (e.g., Level 7 proposal)
- Review recursive self-improvement and containment profiles
- Resolve cross-cutting design conflicts

Council meets asynchronously via GitHub RFC issues; quorum = 2 stewards + 1 maintainer.

---

## Change Process

### Class A — Documentation and patterns

**Path:** PR → maintainer review → merge

Examples: new pattern, case study, research essay, typo fix.

### Class B — Minor standard extension

**Path:** Issue/RFC (1 week comment) → PR → steward approval → merge

Examples: new optional LSS field, new evaluator type enum, new LES sub-metric documentation.

Requirements:

- Backward compatible with existing valid specs
- Validator updated with tests
- CHANGELOG entry

### Class C — Major standard revision

**Path:** RFC issue (minimum 2 weeks comment) → draft PR → steward + council approval → merge with version bump

Examples: LSS 2.0, LES dimension redefinition, taxonomy level addition.

Requirements:

- Written **rationale** and **migration guide**
- Deprecation period announced (minimum 90 days for LSS majors)
- Reference implementations updated
- Benchmark re-baselining plan

### Class D — Safety and containment profiles

**Path:** Class C plus mandatory red-team review checklist

Examples: default tier caps, contained meta-loop reference profile, adversarial benchmark promotion to required.

External safety reviewers invited when available; no blocking veto by vendors.

---

## RFC Template

Post as GitHub issue with label `rfc`:

```markdown
# RFC-NNN: Title

## Problem
What fails today?

## Proposal
Concrete spec/language change.

## Alternatives considered

## Compatibility
Breaking? Migration?

## Evidence
Benchmarks, case studies, or formal argument.

## Safety impact
Autonomy tier, containment, evaluator gaming.

## Timeline
Target version and deprecation.
```

Number RFCs sequentially in issue title.

---

## Versioning

### LSS and LES semver

- **MAJOR** — incompatible schema or dimension meaning change
- **MINOR** — additive fields, backward compatible
- **PATCH** — clarifications, non-normative fixes

Files: `standards/LSS-1.0.md` → `LSS-1.1.md` on minor; `LSS-2.0.md` on major.

### Repository releases

Git tags `vYYYY.MM` for periodic snapshots; `standards-v1.1.0` for standard milestones.

---

## Decision Records

Significant Class C/D decisions append a **Decision Record (DR)** to `contributions/decisions/`:

```
DR-001-lss-evaluator-composition.md
```

Format: context, decision, consequences, links to RFC/PR.

---

## Conflict Resolution

1. Discuss in RFC issue with good-faith technical arguments
2. Steward proposes decision summary after comment period
3. If unresolved: architecture council vote (simple majority)
4. Appeal: fork with documented divergence (open source exit)

Personal disputes → CODE_OF_CONDUCT process, not technical vote.

---

## Forks and Extensions

Vendors and labs may extend LSS privately. For **community recognition**:

- Extensions use `x-` prefix fields in YAML (ignored by core validator) OR
- Submit MINORE RFC to merge extension into core

"Loop Engineering Compatible" label (future) requires passing core validator + reference benchmark tier.

---

## Election of Stewards (Future)

When maintainer group >5 contributors active for 6+ months:

- Stewards nominated from contributors with merged LSS/LES/benchmark work
- Confirmed by maintainer supermajority
- 12-month term, renewable

Until then, repository owners appoint stewards.

---

## Research Roadmap Alignment

[RESEARCH_ROADMAP.md](./RESEARCH_ROADMAP.md) sets horizons; governance does not dictate research outcomes but **prioritizes standardization** when problems close (LE-OP-XX → pattern → LSS field).

Quarterly maintainer review:

- Which open problems moved to Partial/Resolved
- Whether roadmap dates shift (evidence-based)

---

## Amendments to Governance

Changes to this document require:

- RFC labeled `governance`
- 2 week comment period
- Approval by all maintainers OR council supermajority if maintainers disagree

---

## Contact

Governance questions: GitHub issue with label `governance`. Security: private advisory channel per CONTRIBUTING.md.

---

<p align="center"><em>Standards slow down bad surprises. They should not slow down good evidence.</em></p>
