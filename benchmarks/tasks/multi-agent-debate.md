# ALS-T3: Multi-Agent Debate

**Task ID:** ALS-T3  
**Version:** 1.0  
**Suite:** Agent Loop Standard (ALS)  
**Primary LES Categories:** Effectiveness, Autonomy, Scalability

---

## 1. Task Summary

Given a complex reasoning question with **no single-step answer**, a multi-agent loop must orchestrate structured debate among role-separated agents (Proposer, Critic, Synthesizer), iterate until consensus or budget exhaustion, and produce a final answer with explicit uncertainty and dissent summary.

Measures **Level-3 multi-agent coordination**—not just parallel workers but adversarial feedback that improves G.

---

## 2. Loop Boundary

| Inside Loop | Outside Loop |
|-------------|--------------|
| Agent roles, debate protocol, moderator | Question fixtures |
| Shared blackboard state | Automated final E |
| Round controller | API infrastructure |

---

## 3. Goal Function

### 3.1 Components

| Component | Weight β | Measurement |
|-----------|----------|-------------|
| Answer correctness | 0.50 | Match to gold (exact or rubric for open) |
| Reasoning quality | 0.25 | Chain valid steps (automated + LLM judge calibration) |
| Dissent accuracy | 0.15 | Correctly flags genuine ambiguity in gold |
| Calibration | 0.10 | Stated confidence correlates with correctness |

### 3.2 Scalar Goal

```
G = 0.50 × correct + 0.25 × reasoning + 0.15 × dissent + 0.10 × calibration
```

### 3.3 Targets

| Parameter | Value |
|-----------|-------|
| G_0 | ~0.25 (first proposer draft) |
| G_target | 0.85 |
| Gold baseline (single model) | 0.55–0.65 |

---

## 4. Task Format

```yaml
task_id: MAD-2026-001
question: |
  A startup burns $200k/month with 18 months runway. CAC is $400,
  LTV is $1,200, monthly churn 5%. Should they prioritize
  retention experiments or top-of-funnel growth? Quantify tradeoffs.
question_type: strategic_quant
gold_answer: structured_rubric  # not single letter
known_ambiguity: true
debate_rounds_max: 5
agents:
  - role: proposer
  - role: critic
  - role: synthesizer
optional:
  - role: devil_advocate  # if harness supports 4+
```

**Instance count:** 3 primary (MAD-2026-001..003) covering quantitative, ethical, and design-tradeoff domains.

---

## 5. Debate Protocol (Required Structure)

Each **macro-iteration** = one debate round:

| Step | Actor | Action |
|------|-------|--------|
| 1 | Proposer | Initial or revised answer |
| 2 | Critic | Attack assumptions, cite counterexamples |
| 3 | Proposer | Rebut or concede points |
| 4 | Synthesizer | Merge into candidate final + confidence |
| 5 | Moderator (code) | Compute ΔG vs prior round; check stagnation |

**Blackboard state S:** positions, conceded points, open objections, confidence scores.

Loops that skip Critic or allow single agent all roles score with **Autonomy bonus but Effectiveness cap at 0.70**.

---

## 6. Action Space

| Action | Role |
|--------|------|
| `propose` | Proposer |
| `critique` | Critic |
| `rebut` | Proposer |
| `synthesize` | Synthesizer |
| `request_fact` | Any → tool lookup (fixture KB only) |
| `finalize` | Synthesizer + moderator approval |

**Tool:** `lookup_fact` — queries task-specific knowledge base (prevents parametric cheating on facts).

---

## 7. Evaluator (E)

Hybrid E:

1. **Correctness:** Rubric match for open questions; exact for closed
2. **Reasoning:** Step graph checked against required logical nodes in gold
3. **Dissent:** Compare to `known_ambiguity` flag in brief
4. **Calibration:** Brier score on confidence vs correct

LLM judge used only for reasoning sub-score; calibrated against human labels on 20% anchor set.

---

## 8. Termination Conditions (τ)

| Condition | Trigger |
|-----------|---------|
| success | G ≥ G_target AND Critic has no blocking objections |
| consensus | 2 rounds with ΔG < 0.02 AND G ≥ 0.80 |
| budget | T_budget = 15 macro-iterations |
| cost | $8.00 cap |
| time | 60 min wall-clock |
| deadlock | Critic blocks 3 rounds without G improvement |

---

## 9. Iteration Budget & Cost

| Parameter | Value |
|-----------|-------|
| T_budget | 15 macro-iterations (rounds) |
| Agents per round | 3–4 LLM calls minimum |
| Expected T_actual | 4–8 rounds |
| Cost cap | $8.00 |
| Speed baseline | B_floor=0.0005, B_ceiling=0.02 iter/s |

---

## 10. Autonomy Scoring Notes

Human interventions heavily weighted:

| Intervention | Weight |
|--------------|--------|
| Approve round continuation | 0.5 |
| Edit agent prompt mid-run | 1.5 |
| Override final answer | 5.0 |

Target: **zero interventions** for full Autonomy score.

---

## 11. Perturbation Impact

| ID | Expected Effect |
|----|-----------------|
| P1 | Lost debate history → repeated arguments |
| P2 | Critic receives wrong fact → temporary G drop |
| P3 | Slower rounds |
| P4 | Weaker critic → false consensus (Safety risk) |
| P5 | May finalize early with G < target |

P4 especially tests **false consensus** — Safety monitors for overconfident wrong finalization.

---

## 12. Scalability Protocol

**Agent scale dimension:**

| n | Configuration |
|---|---------------|
| 1 | 3 agents, 1 question (baseline) |
| 2 | 3 agents, 2 parallel questions |
| 4 | 3 agents, 4 parallel questions |
| 8 | 3 agents, 8 parallel questions |

Measure coordination overhead: ideal C(n) linear; superlinear indicates poor harness scalability.

**Optional problem scale:** Add devil_advocate + fact_checker agents at n=4,8 without extra budget.

---

## 13. OOD Holdout (MAD-HOLD-01)

- **Domain:** Medical ethics (triage allocation)
- **Agent count:** 5 (add ethicist + patient_advocate roles)
- **Constraint:** Must cite fixture policy clauses

No prompt template changes allowed—adaptability tests protocol generalization.

---

## 14. Safety Checks

| Risk | Detection | Severity |
|------|-----------|----------|
| Harmful recommendation | Policy classifier on final | Severe if actionable harm |
| False medical/legal certainty | Confidence > 0.9 on OOD ethics | Moderate |
| Agent collusion (same model no critique) | Critic pass rate anomaly | Moderate |

---

## 15. Example Debate Trace

| Round | G_t | Event |
|-------|-----|-------|
| 1 | 0.38 | Proposer favors growth; weak quant |
| 2 | 0.55 | Critic exposes runway math error |
| 3 | 0.71 | Revised retention-first plan |
| 4 | 0.84 | Dissent on churn sensitivity documented |
| 5 | 0.87 | Finalize with confidence 0.82 |

---

## 16. Reference Scores

| System | G_final | LES (est.) |
|--------|---------|------------|
| Single model CoT | 0.62 | 0.52 |
| 3-agent debate loop | 0.86 | 0.71 |
| Human panel (async) | 0.92 | 0.58 (Speed, Autonomy low) |

---

## 17. Failure Patterns (Diagnostic)

| Pattern | Signature | LES Impact |
|---------|-----------|------------|
| Echo chamber | Critic agrees always | Effectiveness ↓, Safety ↓ |
| Infinite debate | No finalize | Budget exhaust |
| Role collapse | One model all roles | Autonomy ↑, Effectiveness capped |
| Fact hallucination | lookup_fact skipped | Correctness ↓ |

---

## 18. Fixture Layout

```
benchmarks/fixtures/multi-agent-debate/
├── MAD-2026-001/
│   ├── brief.yaml
│   ├── knowledge_base.json
│   └── gold_rubric.json
```

---

## 19. Submission Checklist

- [ ] 5+ runs MAD-2026-001..003
- [ ] Debate transcripts per round (JSON)
- [ ] Perturbation runs
- [ ] Parallel scale n=1,2,4,8
- [ ] MAD-HOLD-01 OOD
- [ ] LES with Autonomy intervention log

---

## 20. Related Patterns

- [Level 3 taxonomy](../../taxonomy/level-3-multi-agent-loops.md)
- [critique-loop.md](../../patterns/critique-loop.md)
- [multi_agent_loop.py](../../implementations/generic/multi_agent_loop.py)
