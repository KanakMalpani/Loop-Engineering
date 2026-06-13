# Contributing to Loop Engineering

Thank you for helping establish this discipline. Contributions shape a field—not just a repo.

---

## What We Need

| Contribution | Directory |
|--------------|-----------|
| New patterns with LSS specs | `patterns/`, `loop-library/` |
| Case studies with LES scores | `case-studies/` |
| Reference implementations | `implementations/` |
| Benchmark tasks and results | `benchmarks/` |
| Theoretical extensions | `fundamentals/`, `research/` |
| Tool improvements | `tools/` |

## Pull Request Requirements

1. **Loops must have LSS specs** — validate with `python tools/loop_validator.py --strict`
2. **Patterns must include** — problem, architecture, pseudocode, failure modes
3. **Case studies must include** — LES evaluation with numeric scores
4. **Code must run** — include instructions; mock LLM acceptable for demos
5. **No placeholders** — substantive content only

## Process

1. Fork → branch (`add-pattern-foo`, `fix-les-calculator`)
2. One logical change per PR
3. Run validator on any new YAML
4. Open PR with description, LES impact if applicable

## Style

See [STYLE_GUIDE.md](STYLE_GUIDE.md). Plain language, mermaid diagrams, cite sources.

## Governance

Spec changes (LSS, LES) require review per [GOVERNANCE.md](GOVERNANCE.md).

→ [Code of Conduct](CODE_OF_CONDUCT.md)
