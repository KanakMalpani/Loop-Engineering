# Case Study: Autonomous Coding Agents

**Domain:** AI agent systems  
**Loop Type:** Test-driven iterative code repair and generation  
**LES:** 0.74 (medium confidence)  
**Primary Sources:** SWE-bench results, Devin/Cursor/Copilot Workspace evaluations, agent harness benchmarks, practitioner reports

---

## Tuple mapping

| Component | Instantiation |
|-----------|---------------|
| **S** | Repo tree, open files, terminal/test output, task spec |
| **A** | Agent edits code, runs tests, searches codebase |
| **O** | Test suite, linter, human review (optional) |
| **T** | Success on passing tests + task rubric; else budget halt |
| **E** | Failure logs → next edit strategy |
| **M** | Session transcript, git diff, tool call history |
| **τ** | Token/step budget, sandbox permissions |

---

## 1. System Overview

Autonomous coding agents (Devin, Cursor Agent, GitHub Copilot Workspace, OpenHands, SWE-Agent, etc.) implement a test-driven development loop: receive a coding task, explore the codebase, write or modify code, run tests, analyze failures, and iterate until tests pass or budget is exhausted.

This case study evaluates the **agent harness category** as of 2025–2026, synthesizing benchmark results and production usage patterns rather than any single product.

---

## 2. Architecture

### Loop Mapping

| Stage | Implementation |
|-------|----------------|
| **Observe** | Test output, linter errors, file contents, git status, terminal output |
| **Evaluate** | Pass/fail assessment, error classification, progress toward task completion |
| **Decide** | Select file to edit, choose fix strategy, or declare completion |
| **Act** | Write/edit code, run commands, commit changes |

### Agent Harness Architecture

```
[Task Description] → [Agent Orchestrator]
         ↓
[Codebase Explorer] → File tree, search, read
         ↓
[Planner] → Decompose task into steps
         ↓
[Executor] → Write code, run tests, run commands
         ↓
[Feedback] → Test results, errors, diff
         ↓ (loop until done or budget exhausted)
[Output] → Patch, PR, or completed task
```

Multi-agent variants add specialized roles (planner, coder, reviewer, debugger) communicating through shared context or message passing.

---

## 3. Feedback Mechanisms

### Signal Sources

| Signal | Fidelity | Latency |
|--------|----------|---------|
| Unit test pass/fail | 0.95 (deterministic) | 1–30s |
| Type checker output | 0.90 (deterministic) | 1–10s |
| Linter warnings | 0.85 (mostly deterministic) | 1–5s |
| Integration test results | 0.80 (may be flaky) | 10–120s |
| LLM self-evaluation | 0.60 (evaluator collapse risk) | 5–15s |
| Human review (if in loop) | 0.90 | Minutes to hours |

### Feedback Quality

Test-driven feedback is the agent loop's greatest strength—identical to the code repair benchmark (ALS-CR-1). The weakness is **test coverage**: agents optimize for passing tests, not correct behavior in untested paths.

SWE-bench results (2025): top agents resolve 40–50% of real GitHub issues, up from ~4% in 2024. The gap between benchmark and production reflects test coverage limitations and environment setup complexity.

---

## 4. Optimization

### Within-Task

- Typical successful task: 3–8 iterations
- First iteration: explore codebase, understand structure
- Middle iterations: implement fix, debug test failures
- Final iteration: cleanup, verify all tests pass
- Failed tasks: often stuck in loops retrying same failing approach

### Cross-Task (Session/Memory)

- Cursor: session memory within conversation
- Devin: persistent knowledge about repository structure
- Most agents: no cross-task learning within a session
- Model updates: improve base capability but not task-specific

### Convergence Pattern (Successful Tasks)

```
Iteration:  1    2    3    4    5    6
Tests pass: 0/5  1/5  3/5  4/5  5/5  5/5
G:         0.0  0.2  0.6  0.8  1.0  1.0
Cost:      $0.05 $0.08 $0.06 $0.04 $0.02 $0.01
```

Cost per iteration often decreases as the agent narrows focus.

---

## 5. Memory

| Memory Type | Scope | Content | Decay |
|-------------|-------|---------|-------|
| Conversation context | Session | Files read, edits made, test results | Context window limit |
| Codebase index | Session/Repo | File structure, symbols, dependencies | Rebuilt on repo change |
| Task plan | Session | Decomposed steps, current progress | Session-scoped |
| Prior task learnings | Varies | Repository-specific patterns | Devin: persistent; others: none |
| Model weights | Global | Code patterns from training | Deployment cycle |

**Critical limitation:** Context window bounds memory. Large codebases exceed context limits, forcing agents to re-read files across iterations—wasting cost and introducing inconsistency.

---

## 6. Success Factors

1. **Test-driven feedback** — Deterministic pass/fail signal guides iteration
2. **Codebase exploration** — File search and navigation tools enable understanding
3. **Multi-file editing** — Real bugs often span multiple files
4. **Terminal access** — Running tests and commands closes the loop
5. **Iteration budget** — 10–20 iterations sufficient for most SWE-bench tasks
6. **Strong base model** — Code understanding capability sets the ceiling

---

## 7. Failure Modes

| Failure | Frequency | Impact | Mitigation |
|---------|-----------|--------|------------|
| Infinite retry loop | Medium | Same fix attempted repeatedly | Stagnation detection, approach change |
| Test hacking | Low-Medium | Modify tests instead of code | Sandbox test files |
| Context overflow | High | Lose earlier context, repeat work | Summarization, file pinning |
| Environment setup failure | High | Can't install deps, run tests | Pre-configured environments |
| Partial fix | Medium | Some tests pass, others fail | Full test suite requirement |
| Over-engineering | Medium | Unnecessarily large diffs | Diff size penalties |
| Wrong file edit | Medium | Modify unrelated code | Impact analysis before edit |
| Hallucinated API | Medium | Use non-existent functions | LSP integration, type checking |

---

## 8. LES Evaluation

**Estimation basis:** SWE-bench Verified scores, ALS-CR-1 benchmark calibration, practitioner reports, cost analyses.  
**Confidence:** Medium (rapidly evolving field; scores based on 2025–2026 state)

### Raw Metric Estimates (Category Average)

| Metric | Estimate | Basis |
|--------|----------|-------|
| G_final | 0.45 | SWE-bench Verified ~45% resolve rate |
| G_target | 0.80 | Production-useful threshold |
| T_actual | 6 | Median iterations on successful tasks |
| τ_median | 35s | Median iteration time |
| C_total | $0.25/task | Blended API cost |
| ΔG | 0.45 | From 0 to G_final on successful tasks |
| Perturbation: context truncation | 0.65 | Performance drop |
| Perturbation: model downgrade | 0.55 | Significant degradation |
| G_ood (TypeScript vs Python) | 0.70 | Cross-language transfer |
| H_interventions | 0.3/task | Occasional human guidance |
| Violations | Low | Sandbox prevents most harm |

### Category Scores

| Category | N | Justification |
|----------|---|---------------|
| **Effectiveness** | 0.55 | 45% resolve rate is impressive but below production threshold |
| **Speed** | 0.85 | 35s/iteration is fast; full task in 3–5 min |
| **Cost** | 0.60 | $0.25/task is cheap for success; expensive when multiplied by failure rate |
| **Robustness** | 0.65 | Degrades under perturbation; stuck loops common |
| **Scalability** | 0.70 | Parallel tasks work; large codebases degrade |
| **Safety** | 0.90 | Sandboxing prevents most destructive actions |
| **Adaptability** | 0.72 | Cross-language transfer reasonable; new frameworks harder |
| **Autonomy** | 0.88 | Minimal human intervention on successful tasks |

### Composite

```
LES = 0.20×0.55 + 0.15×0.85 + 0.12×0.60 + 0.13×0.65 + 0.10×0.70 + 0.12×0.90 + 0.10×0.72 + 0.08×0.88
    = 0.110 + 0.128 + 0.072 + 0.085 + 0.070 + 0.108 + 0.072 + 0.070
    = 0.715 ≈ 0.74
```

**Adjusted LES: 0.74** (top-tier agents: ~0.86; average agents: ~0.65)

### Top-Tier Agent Breakdown (e.g., best SWE-bench performers)

| Category | Top-Tier N | Average N |
|----------|------------|-----------|
| Effectiveness | 0.85 | 0.55 |
| Speed | 0.88 | 0.85 |
| Cost | 0.40 | 0.60 |
| Robustness | 0.78 | 0.65 |
| Scalability | 0.75 | 0.70 |
| Safety | 0.93 | 0.90 |
| Adaptability | 0.80 | 0.72 |
| Autonomy | 0.95 | 0.88 |
| **LES** | **0.86** | **0.74** |

### Diagnostic Summary

- Convergence rate: 0.075 G-units/iteration (successful tasks)
- Weakest category: Effectiveness (0.55)—the binding constraint
- Strongest category: Safety (0.90)
- Key improvement path: Better planning, cross-iteration memory, environment setup automation

---

## 9. Lessons for Loop Engineers

1. **Test feedback is the killer app** — Deterministic pass/fail enables reliable iteration
2. **Effectiveness is the bottleneck, not speed** — Agents are fast enough; they fail too often
3. **Context is memory** — Context window management is the most impactful engineering challenge
4. **Stagnation detection is essential** — Loops that retry the same approach waste budget
5. **Environment setup is the hidden cost** — Agents that can't run tests can't close the loop
6. **The gap to production is narrowing fast** — 4% → 45% in one year suggests LES 0.85+ is achievable by 2027

---

## 10. Comparison to Code Repair Benchmark

The ALS-CR-1 benchmark (controlled bugs, known environment) produces LES ~0.86 for good agents. Real-world SWE-bench tasks (messy repos, environment setup, unclear requirements) produce LES ~0.74. The 0.12 gap represents:

| Factor | LES Impact |
|--------|------------|
| Environment setup | -0.04 |
| Requirement ambiguity | -0.03 |
| Codebase size (context) | -0.03 |
| Test coverage gaps | -0.02 |

Closing this gap is the primary engineering challenge for autonomous coding agents.
