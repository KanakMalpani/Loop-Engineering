# CrewAI ↔ LSS 1.1 Composition Bridge

**System:** CrewAI sequential + parallel crew patterns  
**Pattern:** research-loop (Level 2) · composable to LSS 1.1 `composition` blocks  
**Harness:** [implementations/crewai/](../implementations/crewai/)

---

## Tuple L = (S, A, O, T, E, M, τ)

| Component | CrewAI | LSS 1.0 / 1.1 |
|-----------|--------|----------------|
| **S** State | Crew shared memory / task context | `memory` + `workers[].inputs` |
| **A** Actors | `Agent` roles with goals | `workers` |
| **O** Observation | Task `expected_output` review | `evaluators[].inputs` |
| **T** Transition | `Process.sequential` / parallel task groups | `composition.type` + `adapters` |
| **E** Evaluator | Verifier agent or rubric hook | `evaluators` + `termination_conditions` |
| **M** Memory | Crew memory backend | `memory` block |
| **τ** Termination | Task completion / quality gate | `termination_conditions` |

---

## LSS 1.1 composition mapping (RFC #11)

Sequential crew (research → analyze → verify):

```yaml
composition:
  type: sequential
  children:
    - id: research
      ref: loop-library/research-agent.yaml
      role: stage
    - id: verify
      ref: loop-library/research-agent.yaml
      role: stage
```

Parallel worldview rehearsal ([scenario-swarm-rehearsal](../loop-library/compositions/scenario-swarm-rehearsal.yaml)):

```yaml
composition:
  type: parallel
  merge:
    strategy: consensus_rubric
    preserve_dissent: true
    synthesizer: workers.orchestrator
  children:
    - id: falsifier
      ref: loop-library/startup-validator.yaml
      role: branch
    - id: evidence
      ref: loop-library/research-agent.yaml
      role: branch
    - id: operator
      ref: loop-library/business-strategy-agent.yaml
      role: branch
```

| CrewAI concept | LSS 1.1 field |
|----------------|---------------|
| `Agent` + `Task` | `composition.children` + `workers` |
| `Process.sequential` | `type: sequential` |
| Parallel task groups | `type: parallel` + `merge` |
| Role backstory | `workers[].role` + branch `lens` |

See [RFC-LSS-1.1-composition.md](../contributions/RFC-LSS-1.1-composition.md) · [Discussion #11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11).

---

## LES (structural)

| Dimension | Score (0–1) | Notes |
|-----------|-------------|-------|
| Effectiveness | 0.82 | Mock crew; LiveEnv for LES_obs |
| Speed | 0.85 | 3-branch parallel + merge |
| Cost | 0.92 | No API keys in smoke path |
| Autonomy | 0.78 | Role-specialized agents |
| **Composite (structural)** | **~80** | `les_calculator --spec loop-library/research-agent.yaml` baseline |

---

## Reproduce (no API keys)

```bash
pip install -r implementations/crewai/requirements.txt  # optional crewai
python implementations/crewai/run.py
python implementations/crewai/research_crew.py
```

---

## LoopBench path

After mapping your CrewAI harness to LSS YAML:

```bash
pip install "loopbench>=0.1.1"
loopbench run --task LB-COMP-1 \
  --spec loop-library/compositions/scenario-swarm-rehearsal.yaml \
  --seeds 0,1,2,3,4 -o results.json
```

Guide: [BEAT_LB-COMP-1.md](../contributions/BEAT_LB-COMP-1.md)

---

## Cross-links

- LangGraph bridge: [langgraph-composition-bridge.md](langgraph-composition-bridge.md)
- Harness index: [BRIDGE_AGENT_HARNESSES.md](../contributions/BRIDGE_AGENT_HARNESSES.md)
- CrewAI outreach: [crewAI #6316](https://github.com/crewAIInc/crewAI/issues/6316)
