name: Case study
description: Propose an external case study with LES scores
title: "[Case study] "
labels: ["case-study", "contributions"]
body:
  - type: input
    id: system_name
    attributes:
      label: System or organization name
    validations:
      required: true

  - type: dropdown
    id: taxonomy_level
    attributes:
      label: Taxonomy level
      options:
        - "1 — Single-step"
        - "2 — Reflective"
        - "3 — Multi-agent"
        - "4 — Evolutionary"
        - "5 — Self-modifying"
        - "6 — Recursive meta"
    validations:
      required: true

  - type: textarea
    id: loop_tuple
    attributes:
      label: Loop tuple mapping (S, A, O, T, E, M, τ)
      description: How does the real system map to L = (S, A, O, T, E, M, τ)?
    validations:
      required: true

  - type: textarea
    id: les_scores
    attributes:
      label: LES scores (numeric, all 8 dimensions if possible)
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Case study checklist
      options:
        - label: Public or anonymized artifact available
        - label: Not duplicate of existing case-studies/ entry
        - label: Follows STYLE_GUIDE.md
