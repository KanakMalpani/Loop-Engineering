## Case study + practitioner exam pilot

Map your agent harness with LoopForge intent, then submit a case study:

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0"
loopforge intent "YOUR AGENT LOOP DESCRIPTION" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
```

- Template: https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/TEMPLATE.md
- Starter example: https://github.com/KanakMalpani/Loop-Engineering/blob/main/case-studies/cursor-agent-loop.md
- Exam pilot volunteers: https://github.com/KanakMalpani/Loop-Engineering/blob/main/education/practitioner/exam-v0.1.md
