## Adoption wave 8 - LSS 1.1 composition mapping feedback

We stabilized **LSS 1.1** composition blocks (`sequential`, `parallel`, `nested`) and would like framework-specific feedback on how you map them today.

**Reference spec:** [scenario-swarm-rehearsal.yaml](https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/compositions/scenario-swarm-rehearsal.yaml)  
**Standard:** [LSS-1.1.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/standards/LSS-1.1.md)  
**Bridge doc:** [BRIDGE_AGENT_HARNESSES.md](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/BRIDGE_AGENT_HARNESSES.md)

### Quick map exercise

1. Pick a multi-agent workflow in your framework (LangGraph, CrewAI, AutoGen, custom).
2. Label each subgraph as sequential stage, parallel branch, or nested inner loop.
3. Note where **merge** / **adapter** semantics differ from LSS 1.1.
4. Reply here with: framework, 3–5 bullet mapping, one friction point.

### Tooling (optional)

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0"
loopforge intent "Parallel research and coding branches" -o mapped.yaml --suggest-level
loopctl validate mapped.yaml
python tools/composition_validator.py mapped.yaml
```

PyPI naming: https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/PYPI_NAMING.md

**Done when:** first non-maintainer mapping comment on this thread.
