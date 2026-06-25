# LoopForge — loop scaffolding library

**Status:** v0.2 (in-repo) · **Spec target:** LSS 1.0 / 1.1 composition

LoopForge helps people **create valid loop specifications** without hand-writing every LSS field. It sits between the pattern docs (`patterns/`) and the runtime layer (`implementations/`, LoopGym):

```
patterns/*.md  →  LoopForge  →  loop-library/*.yaml  →  validator / runtime / LoopBench
```

## Why it exists

Hand-authoring LSS YAML is error-prone: workers, evaluators, feedback channels, termination guards, metrics, safety, and cost envelopes must all align with the JSON Schema. LoopForge generates a **schema-valid skeleton** from a named pattern so you can focus on roles, rubrics, and domain inputs.

## Quick start

From the repo root (requires `pyyaml` and `jsonschema` — see `loopforge/requirements.txt`):

```bash
pip install -r loopforge/requirements.txt

# List patterns
python -m loopforge list-patterns

# Scaffold a reflection loop
python -m loopforge new \
  --pattern reflection \
  --name bug-fixer \
  --objective "Fix failing tests from a bug report" \
  --output loop-library/bug-fixer.yaml

# Validate any spec
python -m loopforge validate loop-library/bug-fixer.yaml
```

## Python API

```python
from loopforge import LoopBuilder, Pattern

spec = (
    LoopBuilder("my-agent", "Summarize user feedback into actionable themes")
    .from_pattern(Pattern.SIMPLE)
    .with_input("feedback", description="Raw user feedback text")
    .with_quality_threshold(0.85)
    .with_max_iterations(10)
    .build()
)

errors = LoopBuilder("my-agent", "...").from_pattern(Pattern.SIMPLE).validate(spec)
assert not errors

LoopBuilder("my-agent", "...").from_pattern(Pattern.SIMPLE).save("loop-library/my-agent.yaml")
```

## Built-in patterns

| Pattern | Workers | Use when |
|---------|---------|----------|
| `simple` | 1 executor | Fastest start; single worker + quality rubric |
| `reflection` | generator + reflector | Output must be critiqued before commit |
| `verification` | implementer | Code/change must pass test + scope gates |
| `research` | query_planner + synthesizer | Sourced briefs with citations |

Each pattern ships with: ephemeral memory, prompt-refinement optimization, safety constraints (injection + secret scan), cost limits, stall detection, and a primary quality metric wired to the rubric evaluator.

## Relationship to other tools

| Tool | Role |
|------|------|
| [loop_validator.py](../tools/loop_validator.py) | Standalone CLI validation (LoopForge embeds the same schema check) |
| [level_recommender.py](../tools/level_recommender.py) | Suggests D–M–I–S maturity level from a spec — run **after** scaffolding |
| [loop_diagram_generator.py](../tools/loop_diagram_generator.py) | Mermaid diagrams from finished YAML |
| [LoopGym](https://pypi.org/project/loopgym/) | Runtime + sim/live/replay envs for scored runs |
| [LoopBench](https://pypi.org/project/loopbench/) | Benchmark tasks and LES scoring |

## Roadmap (v0.2+)

- [x] PyPI package layout (`pip install le-loopforge`) with bundled schema
- [x] `from_library("research-agent")` / `loopforge fork`
- [x] Composition scaffolds (`loopforge compose`)
- [x] LE-OP-11 level hint on save (`--suggest-level`)
- [x] Export to LangGraph / CrewAI / generic stubs
- [ ] NL intent→LSS compiler (LE-OP-15, Phase 6) — **v0.3 prototype:** `loopforge intent`

## Files

| Path | Purpose |
|------|---------|
| [loopforge/](../loopforge/) | Python package (`builder`, `patterns`, `validate`, CLI) |
| [examples/loopforge-scaffold/](../examples/loopforge-scaffold/) | Demo runner |
| [standards/examples/minimal-loop.yaml](../standards/examples/minimal-loop.yaml) | Hand-crafted reference spec (compare against scaffolds) |

## Daily CI

`scripts/daily_checkin.py` runs `python -m loopforge demo` to scaffold and validate all patterns on every check-in.
