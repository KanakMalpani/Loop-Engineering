# Loop Practitioner Exam v0.2

**Time:** ~35 minutes after [README.md](./README.md) and [exam-v0.1.md](./exam-v0.1.md)  
**Pass threshold:** 18/22 correct + practical checklist complete  
**Pilot feedback:** Issue [#12](https://github.com/KanakMalpani/Loop-Engineering/issues/12) — v0.2 adds PyPI naming, trace/observed LES, composition intents

---

## Part A — Concepts (11 questions)

1. What are the seven components of the formal loop tuple L = (S, A, O, T, E, M, τ)?
2. Name the four phases of a single loop iteration in order.
3. What is the difference between a **pattern** and a **taxonomy level**?
4. Which pattern fits: "run tests until pass"?
5. What does LSS stand for and what is its primary artifact format?
6. What eight dimensions does LES 1.0 score?
7. When should `composition.type: parallel` be used vs `sequential`?
8. What is the purpose of `termination_conditions.stall`?
9. What does Loop Trace 1.0 capture that structural LES does not?
10. What command scaffolds a valid spec from natural language intent?
11. Why install **`le-loopforge`** on PyPI instead of `loopforge`?

---

## Part B — Tooling (11 questions)

12. Command to fork `research-agent` as `my-agent`?
13. Command to validate a spec with loopctl?
14. Command to score structural LES as JSON?
15. Command to validate a trace file?
16. Command to compute observed LES from a trace?
17. Which LoopBench task maps to code repair?
18. What flag prints LE-OP-11 level hint on save?
19. Where are bundled LSS schemas in the loopforge package?
20. What daily CI check runs `loopforge demo`?
21. What file is the Golden Path onboarding doc?
22. What intent phrase routes to a **parallel** composition scaffold?

---

## Part C — Practical (required)

Install with canonical PyPI names ([PYPI_NAMING.md](../../contributions/PYPI_NAMING.md)):

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0"
```

- [ ] Run `loopforge intent "Summarize feedback into themes" -o exam-loop.yaml --suggest-level`
- [ ] Run `loopctl validate exam-loop.yaml`
- [ ] Run `loopctl score --spec exam-loop.yaml --json > exam-les.json`
- [ ] Run `loopforge intent "Parallel research and coding branches" -o exam-compose.yaml --suggest-level`
- [ ] Confirm `exam-compose.yaml` contains a `composition:` block
- [ ] Run `python examples/reflection-loop/run.py` successfully

---

## Rubric (maintainer / self-assess)

| Section | Weight | Pass bar |
|---------|--------|----------|
| Part A | 40% | ≥9/11 |
| Part B | 40% | ≥9/11 |
| Part C | 20% | All checkboxes |

Combined written pass: **≥18/22**. Part C is mandatory regardless of written score.

---

## Answer key (self-serve)

| # | Answer |
|---|--------|
| 1 | State, Actions, Observations/Orchestration, Transitions, Evaluators, Memory, termination/budget τ |
| 2 | Observe → act → evaluate → update (then repeat) |
| 3 | Pattern = control structure; level = cognitive depth (L1–L6) |
| 4 | verification-loop |
| 5 | Loop Specification Standard; YAML |
| 6 | effectiveness, speed, cost, robustness, scalability, safety, adaptability, autonomy |
| 7 | Parallel = independent branches merged; sequential = pipeline stages |
| 8 | Detect stagnation; halt when improvement below threshold over window |
| 9 | Per-iteration worker outputs, evaluator scores, cost, termination from live run |
| 10 | `loopforge intent "..." -o file.yaml` |
| 11 | `loopforge` PyPI name is a different project; canonical package is `le-loopforge` |
| 12 | `loopforge fork --from research-agent --name my-agent -o my-agent.yaml` |
| 13 | `loopctl validate my-agent.yaml` |
| 14 | `loopctl score --spec my-agent.yaml --json` |
| 15 | `loopctl trace validate trace.json` |
| 16 | `loopctl observed trace.json --json` (optional `--spec`) |
| 17 | LB-CR-1 |
| 18 | `--suggest-level` |
| 19 | `loopforge/schemas/` |
| 20 | `loopforge_scaffold` in `scripts/daily_checkin.py` |
| 21 | `contributions/GOLDEN_PATH.md` |
| 22 | Phrases with parallel/concurrent/branches/swarm (LE-OP-15 v0.5) |

---

## Pilot friction log (template for #12 reporters)

| Step | Minutes | Confusion |
|------|---------|-----------|
| pip install | | |
| intent | | |
| validate | | |
| reflection-loop | | |

Post filled table on [#12](https://github.com/KanakMalpani/Loop-Engineering/issues/12).
