name: Benchmark submission
description: Submit ALS benchmark runs and LES scores
title: "[Benchmark] "
labels: ["benchmark", "contributions"]
body:
  - type: markdown
    attributes:
      value: |
        Submit reproducible benchmark results for the Agent Loop Standard (ALS).
        See [benchmarks/results/README.md](../benchmarks/results/README.md) and [REPRODUCE.md](../contributions/REPRODUCE.md).

  - type: input
    id: task_id
    attributes:
      label: Task ID
      placeholder: "ALS-T2"
    validations:
      required: true

  - type: input
    id: harness
    attributes:
      label: Harness name and version
      placeholder: "loopbench 0.1.x / custom"
    validations:
      required: true

  - type: textarea
    id: les_vector
    attributes:
      label: LES vector (8 dimensions + composite)
      placeholder: "Paste JSON from les_calculator or LoopBench"
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: Reproduction commands
      description: Exact commands another researcher can run
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Submission checklist
      options:
        - label: ≥5 primary runs completed
        - label: LSS spec path included
        - label: Iteration logs attached (JSON)
        - label: Environment documented (Python version, pip freeze snippet)
