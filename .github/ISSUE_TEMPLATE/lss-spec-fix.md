name: LSS spec fix
description: Fix or extend a loop-library LSS YAML spec
title: "[LSS] "
labels: ["lss", "loop-library"]
body:
  - type: input
    id: spec_path
    attributes:
      label: YAML path
      placeholder: "loop-library/coding-agent.yaml"
    validations:
      required: true

  - type: textarea
    id: issue
    attributes:
      label: What needs fixing?
    validations:
      required: true

  - type: textarea
    id: validator_output
    attributes:
      label: Validator output (if applicable)
      description: Output of python tools/loop_validator.py or scripts/validate_loop_library.py

  - type: checkboxes
    id: checklist
    attributes:
      label: PR checklist
      options:
        - label: Ran scripts/validate_loop_library.py locally
        - label: Updated companion .md if architecture changed
        - label: No breaking change without GOVERNANCE RFC
