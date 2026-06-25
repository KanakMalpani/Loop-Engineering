# Loop Practitioner Exam v0.1

**Time:** ~30 minutes after completing [README.md](./README.md)  
**Pass threshold:** 16/20 correct + practical checklist complete

---

## Part A — Concepts (10 questions)

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

---

## Part B — Tooling (10 questions)

11. Command to fork `research-agent` as `my-agent`?
12. Command to validate a spec with loopctl?
13. Command to score structural LES as JSON?
14. Command to validate a trace file?
15. Command to compute observed LES from a trace?
16. Which LoopBench task maps to code repair?
17. What flag prints LE-OP-11 level hint on save?
18. Where are bundled LSS schemas in the loopforge package?
19. What daily CI check runs `loopforge demo`?
20. What file is the Golden Path onboarding doc?

---

## Part C — Practical (required)

- [ ] Run `loopforge intent "Summarize feedback into themes" -o exam-loop.yaml --suggest-level`
- [ ] Run `loopctl validate exam-loop.yaml`
- [ ] Run `loopctl score --spec exam-loop.yaml --json > exam-les.json`
- [ ] Run `python examples/reflection-loop/run.py` successfully

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
| 11 | `loopforge fork --from research-agent --name my-agent -o my-agent.yaml` |
| 12 | `loopctl validate my-agent.yaml` |
| 13 | `loopctl score --spec my-agent.yaml --json` |
| 14 | `loopctl trace validate trace.json` |
| 15 | `loopctl observed trace.json --json` |
| 16 | LB-CR-1 |
| 17 | `--suggest-level` |
| 18 | `loopforge/schemas/` |
| 19 | `loopforge_scaffold` in `scripts/daily_checkin.py` |
| 20 | `contributions/GOLDEN_PATH.md` |

Pass: ≥16/20 Part A+B + all Part C checkboxes.
