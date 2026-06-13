# Citing Loop Engineering

How to reference the Loop Engineering discipline, repository, standards, and individual documents in academic papers, blog posts, technical reports, and software documentation.

---

## Recommended Citation (Repository)

For general citation of the discipline and this repository:

```bibtex
@misc{loop-engineering-2026,
  title        = {Loop Engineering: The Discipline of Self-Improving Systems},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/KanakMalpani/Loop-Engineering}},
  note         = {Accessed: YYYY-MM-DD}
}
```

**APA 7th:**

> Loop Engineering Community. (2026). *Loop Engineering: The discipline of self-improving systems*. GitHub. https://github.com/KanakMalpani/Loop-Engineering

Replace access date on retrieval.

**Chicago (website):**

> Loop Engineering Community. "Loop Engineering: The Discipline of Self-Improving Systems." GitHub repository. 2026. https://github.com/KanakMalpani/Loop-Engineering.

---

## Citing Standards

### Loop Specification Standard (LSS)

```bibtex
@techreport{lss-1-0-2026,
  title        = {Loop Specification Standard (LSS) Version 1.0},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  institution  = {Loop Engineering},
  url          = {https://github.com/KanakMalpani/Loop-Engineering/blob/main/standards/LSS-1.0.md},
  type         = {Standard}
}
```

In prose: "We specify our agent using LSS 1.0 (Loop Engineering Community, 2026)."

### Loop Engineering Score (LES)

```bibtex
@techreport{les-1-0-2026,
  title        = {Loop Engineering Score (LES) Version 1.0},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  institution  = {Loop Engineering},
  url          = {https://github.com/KanakMalpani/Loop-Engineering/blob/main/scoring/LES-1.0.md},
  type         = {Standard}
}
```

Always cite **version** when reporting scores: "LES 1.0 Effectiveness = 0.82."

---

## Citing Specific Documents

Use `@misc` with `howpublished = {GitHub repository document}` and stable path URL.

**Example — open problems:**

```bibtex
@misc{le-open-problems-2026,
  title        = {Open Research Problems in Loop Engineering},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  howpublished = {\url{https://github.com/KanakMalpani/Loop-Engineering/blob/main/research/open-problems.md}},
  note         = {Problem IDs LE-OP-01 through LE-OP-21}
}
```

**Example — manifesto:**

```bibtex
@misc{le-manifesto-2026,
  title        = {The Loop Engineering Manifesto},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  howpublished = {\url{https://github.com/KanakMalpani/Loop-Engineering/blob/main/manifesto/MANIFESTO.md}}
}
```

### Version pinning

For reproducibility, cite **commit SHA** or **release tag**:

```bibtex
note = {Version v2026.06, commit \texttt abc1234}
```

Or use Zenodo DOI if repository obtains one (future).

---

## Citing Open Problems

Reference by stable ID in prose:

> The termination certificate problem (LE-OP-01) remains open as of June 2026 (Loop Engineering Community, 2026).

BibTeX may include `note = {LE-OP-01}` for specific problems discussed.

---

## Citing Loop Specifications (LSS Files)

When publishing benchmark results tied to a spec:

```bibtex
@misc{le-spec-coding-agent-2026,
  title        = {Loop Specification: coding-agent},
  author       = {{Loop Engineering Community}},
  year         = {2026},
  howpublished = {\url{https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/coding-agent.yaml}},
  note         = {LSS 1.0}
}
```

Report `loop_name` and `version` field from YAML in body text.

---

## In-Text Terminology

First use in a paper:

> **Loop Engineering** is the discipline of designing systems that improve through feedback, formalized as loops $L = (S, A, O, T, E, M, \tau)$ (Loop Engineering Community, 2026).

Do not abbreviate to "LE" on first mention. "LSS" and "LES" may follow defined spelled-out forms.

---

## Software That Implements LSS/LES

If your software implements standards:

> This harness accepts Loop Specification Standard (LSS) 1.0 files (Loop Engineering Community, 2026) and reports Loop Engineering Score (LES) 1.0 dimensions.

Link to validator or calculator if forked; note modifications in README.

---

## Attribution for Contributors

Individual authors may additionally cite their papers **about** Loop Engineering. The community repository citation does not replace personal authorship on novel research.

For substantial merged contributions, contributors may list themselves in paper acknowledgments:

> We thank [Name] for contributions to the Loop Engineering pattern library.

---

## Trademark and Naming

"Loop Engineering" is used descriptively for this open discipline. Third parties may say "LSS-compatible" or "inspired by Loop Engineering." Do not imply official endorsement without maintainer written approval.

---

## Markdown / README Badge

```markdown
[![Loop Engineering](https://img.shields.io/badge/Loop-Engineering-LSS--1.0-green.svg)](https://github.com/KanakMalpani/Loop-Engineering)
```

Optional link to specific spec version used.

---

## Questions

Citation format requests: GitHub issue label `documentation`. DOI/Zenodo setup: governance RFC.

---

<p align="center"><em>Cite the version you measured, not the version you wish you used.</em></p>
