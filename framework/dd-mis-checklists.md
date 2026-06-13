# DD-MIS Checklists

Design → Diagnose → Measure → Improve → Scale checklists for loop operators.

---

## Design Checklist

- [ ] Objective is measurable (one sentence)
- [ ] Taxonomy level chosen and justified
- [ ] Workers defined with roles and policies
- [ ] Evaluators independent from actors (maker-checker where needed)
- [ ] Termination conditions include max_iterations or cost_limit
- [ ] safety_constraints cover forbidden actions
- [ ] cost_limits set (tokens, USD, iterations)
- [ ] LSS validates: `python tools/loop_validator.py spec.yaml --strict`

---

## Diagnose Checklist

- [ ] Failure classified via [failure-taxonomy.md](../standards/failure-taxonomy.md)
- [ ] Last N run histories inspected
- [ ] termination_reason distribution analyzed
- [ ] Evaluator false pass / false fail identified
- [ ] Complexity tier noted (`loop_complexity_analyzer.py`)
- [ ] Root cause is spec vs implementation vs environment

---

## Measure Checklist

- [ ] LES computed for representative sample
- [ ] Per-dimension scores recorded
- [ ] Latency and token metrics per iteration
- [ ] Success rate vs max_iterations plotted
- [ ] Baseline tagged in git for comparison

---

## Improve Checklist

- [ ] Hypothesis links to LES dimension
- [ ] Minimal LSS diff
- [ ] Shadow run before promote
- [ ] `loop_comparison.py` old vs new
- [ ] No safety regression
- [ ] PR includes test plan

---

## Scale Checklist

- [ ] Readiness gates in [scale.md](scale.md) satisfied
- [ ] Kill switch tested
- [ ] Cost alerts configured
- [ ] Multi-tenant isolation verified (if applicable)
- [ ] Runbook for on-call
- [ ] Post-deploy LES sample scheduled

---

## Quick Reference

| Phase | Primary tool | Primary artifact |
|-------|--------------|------------------|
| Design | loop_validator | LSS YAML |
| Diagnose | failure taxonomy | RCA memo |
| Measure | les_calculator | LES report |
| Improve | loop_comparison | Versioned LSS |
| Scale | complexity_analyzer | Runbook + alerts |
