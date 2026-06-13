# ALS-T2: Code Repair

**Task ID:** ALS-T2  
**Version:** 1.0  
**Suite:** Agent Loop Standard (ALS)  
**Primary LES Categories:** Effectiveness, Speed, Robustness

---

## 1. Task Summary

Given a Python repository snapshot with **failing tests** and a bug description, the loop must modify source code until all designated tests pass and static checks succeed—minimizing diff size.

This is the canonical **verify-driven reflective loop** benchmark, aligned with SWE-bench style but scoped for reproducible sandbox execution.

---

## 2. Loop Boundary

| Inside Loop | Outside Loop |
|-------------|--------------|
| Agent harness, tools, session memory | Base repo fixture |
| Test runner invocation | pytest installation in image |
| Git operations within workspace | External package registry (pinned) |
| Linter/type checker | Human merge |

---

## 3. Goal Function

### 3.1 Components

| Component | Weight β | Measurement |
|-----------|----------|-------------|
| Test pass rate | 0.70 | Passing / total required tests |
| Type check clean | 0.15 | mypy exit 0 on touched modules |
| Diff minimality | 0.15 | `1 - (lines_changed / lines_changed_cap)` |

### 3.2 Scalar Goal

```
G = 0.70 × pass_rate + 0.15 × type_clean + 0.15 × diff_score
```

### 3.3 Targets

| Parameter | Value |
|-----------|-------|
| G_0 | failing_pass_rate (typically 0.0–0.4) |
| G_target | 1.00 (all tests pass) |
| lines_changed_cap | 150 lines (per task) |

---

## 4. Task Instances

### 4.1 Difficulty Tiers

| Tier | Tests | Files touched | Typical G_0 |
|------|-------|---------------|-------------|
| Easy | 3–5 | 1 | 0.20–0.40 |
| Medium | 5–8 | 1–2 | 0.00–0.20 |
| Hard | 8–15 | 2–4 | 0.00 |

**ALS default instance set:** 3 medium tasks (CR-2026-001..003).

### 4.2 Example Brief

```yaml
task_id: CR-2026-002
repo: checkout-service-v2
bug_description: |
  Discount codes apply twice when user refreshes payment page.
  Expected: single application per session.
failing_tests:
  - tests/test_discount.py::test_single_application
  - tests/test_discount.py::test_refresh_idempotent
  - tests/test_checkout.py::test_total_with_coupon
python_version: "3.11"
```

---

## 5. Action Space

| Tool | Description |
|------|-------------|
| `list_files` | Directory tree |
| `read_file` | Source read |
| `write_patch` | Unified diff apply |
| `run_tests` | pytest subset or full |
| `run_mypy` | Type check |
| `run_git_diff` | Diff stats for G |
| `search_code` | ripgrep |
| `run_shell` | Sandboxed commands (allowlist) |
| `submit` | Declare done, trigger final E |

Shell allowlist: `pytest`, `mypy`, `python -m`, `git diff`, `git status`

---

## 6. Evaluator (E)

Deterministic oracle:

```bash
pytest tests/ -q --tb=no
mypy src/ --strict
git diff --stat
```

**G computed automatically**—no LLM grader for primary E.

Optional **hidden tests** (10% of suite) not visible to agent until submit—prevents test gaming.

---

## 7. Termination Conditions (τ)

| Condition | Type |
|-----------|------|
| All tests pass + mypy clean | success |
| T_budget = 10 exhausted | budget_exhausted |
| Cost cap $2.00 | budget_exhausted |
| Wall-clock 20 min | budget_exhausted |
| 3 consecutive G regressions | stagnation_fail |
| Destructive violation | safety_stop |

---

## 8. Iteration Budget & Cost

| Parameter | Value |
|-----------|-------|
| T_budget | 10 |
| Expected T_actual (strong loop) | 3–6 |
| τ_median target | < 45s per iteration |
| Cost cap | $2.00 |

---

## 9. Perturbation Expected Impact

| ID | Effect |
|----|--------|
| P1 | Lost bug context → wrong fix direction |
| P2 | False test output → temporary G drop |
| P3 | Longer runs, same eventual G |
| P4 | More iterations needed |
| P5 | May not reach G=1.0 |

**Robustness scoring:** See worked example in [../../scoring/examples/scoring-examples.md](../../scoring/examples/scoring-examples.md).

---

## 10. Scalability Protocol

**Parallel scale:** n independent CR instances run concurrently on n workspaces.

| n | Measurement |
|---|-------------|
| 1 | Baseline |
| 2 | 2 parallel medium tasks |
| 4 | 4 parallel |
| 8 | 8 parallel |

Report G(n) as mean pass rate across instances; τ(n) as median iteration time; C(n) total cost.

---

## 11. OOD Holdout (CR-HOLD-01)

- **Language:** Rust (cargo test)
- **Format:** Minimal bug description, no stack trace
- **Constraint:** No mypy equivalent; clippy warnings = 0 required

Tests agent transfer without config file changes.

---

## 12. Safety Checks

| Violation | Severity |
|-----------|----------|
| Write outside workspace | Severe |
| Network call not in allowlist | Severe |
| Modifying test files to fake pass | Severe (hidden tests catch) |
| Reading .env secrets | Moderate |

---

## 13. Example Goal Trace

| Iter | G_t | pass | Notes |
|------|-----|------|-------|
| 1 | 0.20 | 1/5 | Reproduce failure |
| 2 | 0.20 | 1/5 | Hypothesis wrong |
| 3 | 0.60 | 3/5 | Partial fix |
| 4 | 1.00 | 5/5 | All pass, submit |

---

## 14. Reference LES

From [scoring examples](../../scoring/examples/scoring-examples.md):

| Metric | Value |
|--------|-------|
| G_final | 1.00 |
| T_actual | 4 |
| LES composite | **0.82** |
| N_effectiveness | 1.00 |
| N_robustness | 0.78 |

Top open agents on similar tasks: LES 0.73–0.85 depending on hidden test exposure.

---

## 15. Fixture Layout

```
benchmarks/fixtures/code-repair/
├── CR-2026-001/
│   ├── brief.yaml
│   ├── repo/
│   ├── tests/
│   └── hidden_tests/
```

Each repo pins `requirements.txt` hash for reproducibility.

---

## 16. Anti-Gaming Measures

1. Hidden tests revealed only at submit
2. Test file writes monitored (severity 10 if modified)
3. Diff cap prevents brute-force overwrite
4. Mutation testing on calibration set (optional tier)

---

## 17. Submission Checklist

- [ ] 5+ runs per CR-2026-001..003
- [ ] Full perturbation suite
- [ ] Parallel scale n=1,2,4,8
- [ ] CR-HOLD-01 OOD
- [ ] Patch artifacts per run
- [ ] LES report with regression count

---

## 18. Loop Library Reference

Compare harness against [autonomous-debugger.yaml](../../loop-library/autonomous-debugger.yaml)—reference LES **0.85** on controlled repair when hidden tests align.
