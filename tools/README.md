# Loop Engineering Tools

Command-line utilities for working with LSS loop specifications.

## Install

```bash
pip install -r tools/requirements.txt
```

## Tools

| Script | Purpose |
|--------|---------|
| `les_calculator.py` | Compute Loop Engineering Score (LES-1.0) |
| `loop_validator.py` | Validate LSS YAML against JSON Schema |
| `loop_diagram_generator.py` | Generate Mermaid diagrams from LSS |
| `loop_complexity_analyzer.py` | Estimate token/time complexity |
| `loop_comparison.py` | Compare two loop specifications |

## Examples

```bash
python tools/loop_validator.py standards/examples/minimal-loop.yaml
python tools/les_calculator.py --spec standards/examples/minimal-loop.yaml
python tools/loop_diagram_generator.py standards/examples/minimal-loop.yaml
python tools/loop_complexity_analyzer.py standards/examples/minimal-loop.yaml
python tools/loop_comparison.py spec-a.yaml spec-b.yaml
```

All tools support `--help`.
