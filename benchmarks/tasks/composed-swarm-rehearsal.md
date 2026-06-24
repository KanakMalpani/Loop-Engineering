# LB-COMP-1: Composed Swarm Rehearsal

**Task ID:** LB-COMP-1  
**Version:** 1.0.0 (preview)  
**Suite:** LoopBench 0.1.0  
**Primary LES Categories:** Effectiveness, Autonomy, Scalability

---

## 1. Task Summary

Score a **parallel composed loop** — [scenario-swarm-rehearsal](../../loop-library/compositions/scenario-swarm-rehearsal.yaml) — that fans out falsifier, evidence, and operator branches, then merges with dissent preserved.

Inspired by MiroFish-style worldview rehearsal; expressed as portable LSS 1.1 composition.

---

## 2. Loop Boundary

| Inside Loop | Outside Loop |
|-------------|--------------|
| Composed orchestrator + child loops | LoopBench task instances |
| Parallel branch workers | SimEnv fixture (v0.1 proxy: multi-agent-debate-v1) |
| Merge evaluator | Human decision commit |

---

## 3. Spec

```bash
loopbench run \
  --task LB-COMP-1 \
  --spec loop-library/compositions/scenario-swarm-rehearsal.yaml \
  --seeds 0,1,2,3,4 \
  -o results.json
```

Local smoke (no LoopBench):

```bash
python examples/compose-loop/run.py loop-library/compositions/scenario-swarm-rehearsal.yaml
```

---

## 4. Maintainer baseline

| Field | Value |
|-------|-------|
| LES (observed) | 77.4 |
| Success@k | 1.0 |
| Spec | scenario-swarm-rehearsal.yaml |
| JSON | [lb-comp-1-baseline.json](../results/lb-comp-1-baseline.json) |

Beat this score → [good-first issue #4](https://github.com/KanakMalpani/Loop-Engineering/issues/4).

---

## 5. Notes (v0.1)

LoopGym ships no dedicated composed SimEnv yet. LB-COMP-1 registers as its own task ID but uses `loopbench/multi-agent-debate-v1` as the execution proxy until LoopGym adds `loopbench/composed-swarm-v1`.
