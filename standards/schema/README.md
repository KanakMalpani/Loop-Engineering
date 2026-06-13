# LSS JSON Schema — mirror notice

**This file is a local mirror for offline use only.**

The canonical schema is maintained in **[Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering)**:

- Raw JSON: https://raw.githubusercontent.com/KanakMalpani/Loop-Core-Engineering/main/specs/lss-1.0.schema.json
- Spec overview: https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.0.md

Validate against canonical:

```bash
git clone https://github.com/KanakMalpani/Loop-Core-Engineering.git
pip install -r Loop-Core-Engineering/requirements.txt
python Loop-Core-Engineering/tools/validate_lss.py your-loop.yaml
```

Do not edit `lss-1.0.schema.json` in this folder without syncing from upstream.
