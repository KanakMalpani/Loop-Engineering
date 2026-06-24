# LoopGym — discipline reference

LoopGym is the runtime layer: compile LSS YAML into SimEnv, LiveEnv, or ReplayEnv. Install: `pip install loopgym` ([PyPI](https://pypi.org/project/loopgym/)).

**Canonical repo:** [KanakMalpani/LoopGym](https://github.com/KanakMalpani/LoopGym)

---

## Environment IDs (v0.1)

| Env ID | Backend | Use |
|--------|---------|-----|
| `loopbench/code-repair-v1` | Sim | LB-CR-1 code repair |
| `loopbench/research-synthesis-v1` | Sim | LB-RS-1 research synthesis |
| `loopbench/multi-agent-debate-v1` | Sim | LB-MA-1 / LB-COMP-1 (composed proxy) |
| `replay/loopnet-v1` | Replay | LoopNet v0.2 trajectories — zero API cost |
| `sim/mock-llm-v1` | Sim | Custom LSS specs |

---

## Quick replay (REPRODUCE Step 6)

```bash
pip install loopgym
python -c "
import loopgym as lg
env = lg.make('loopbench/code-repair-v1')
obs = env.reset(task_id='cr-001')
print('task:', obs.task_id, '| step:', obs.step)
"
```

From [REPRODUCE.md](../contributions/REPRODUCE.md):

```bash
pip install loopgym loopbench
loopbench run --task LB-CR-1 --spec loop-library/autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json
```

---

## Composed loops (local smoke)

LoopGym v0.1 has no dedicated composed env yet. Use the generic composed runtime:

```bash
python examples/compose-loop/run.py loop-library/compositions/scenario-swarm-rehearsal.yaml
python examples/compose-loop/run.py loop-library/compositions/code-debug-repair.yaml
```

LB-COMP-1 on LoopBench uses `multi-agent-debate-v1` as a SimEnv proxy until a composed env ships.

---

## Replay → LoopNet contribution path

Existing LoopGym users can grow the corpus without new labeling infrastructure:

1. Run an episode (Sim or Live) and export an LTF trace via [loop-observability](https://github.com/KanakMalpani/loop-observability).
2. Format as `ln/record-v1` per [loopnet schema](https://github.com/KanakMalpani/loopnet/blob/main/schema/loopnet-record-v1.json).
3. Submit via [loopnet COMMUNITY-SUBMISSION](https://github.com/KanakMalpani/loopnet/blob/main/guides/COMMUNITY-SUBMISSION.md).

ReplayEnv users can validate against existing records first:

```python
import loopgym as lg
env = lg.make("replay/loopnet-v1")
obs = env.reset(record_id="ln-00042")
```

---

## Adoption

Validated your harness? Post on the [reproduction challenge](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) after [REPRODUCE.md](../contributions/REPRODUCE.md).
