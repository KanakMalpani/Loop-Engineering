# GitHub Pull Requests

**Domain:** Software development  
**Loop Type:** Human-AI collaborative code review  
**LES:** 0.82 (medium-high confidence)  
**Primary Sources:** GitHub engineering blog, DORA metrics research, GitHub Copilot studies, industry CI/CD data

---

## 1. System Overview

The GitHub pull request (PR) workflow is a distributed code review loop used by millions of developers daily. A contributor submits code changes, automated checks run, human and AI reviewers provide feedback, the contributor revises, and the cycle repeats until approval and merge.

With the addition of GitHub Copilot code review, automated security scanning (Dependabot, CodeQL), and CI/CD integration, the PR loop has evolved into a hybrid human-AI system that represents the most widely deployed software engineering loop in existence.

---

## 2. Architecture

### Loop Mapping

| Stage | Implementation |
|-------|----------------|
| **Observe** | Diff, CI results, review comments, Copilot suggestions, security alerts |
| **Evaluate** | Reviewers assess correctness, style, security; CI pass/fail |
| **Decide** | Approve, request changes, or comment; contributor decides fixes |
| **Act** | Push new commits, resolve conversations, merge |

### PR Loop Architecture

```
[Feature Branch] → [Open PR]
         ↓
[CI Pipeline] → Tests, lint, build, security scan
         ↓
[Automated Review] → Copilot review, CodeQL, Dependabot
         ↓
[Human Review] → Code owners, team members
         ↓
[Feedback] → Comments, requested changes, approvals
         ↓
[Contributor Revision] → New commits pushed
         ↓ (loop until approved)
[Merge] → Main branch updated
         ↓
[Deploy Pipeline] → Production (if CD enabled)
```

Each push to the PR branch triggers a new CI observation cycle.

---

## 3. Feedback Mechanisms

### Signal Sources

| Signal | Fidelity | Latency |
|--------|----------|---------|
| CI test results | 0.95 (deterministic for covered tests) | 2–15 min |
| CodeQL security findings | 0.85 (false positives ~15%) | 3–10 min |
| Human review comments | 0.90 (expert judgment, subjective) | Hours to days |
| Copilot review suggestions | 0.70 (helpful but incomplete) | 1–3 min |
| Dependabot alerts | 0.80 (known CVEs, not zero-days) | Minutes |
| Production metrics (post-merge) | 0.95 (lagging but ground truth) | Hours to days |

### Feedback Quality

CI provides the highest-fidelity automated feedback—pass/fail is unambiguous for covered code paths. Human review adds semantic feedback CI cannot provide (design, maintainability, context).

The loop's weakness is incomplete test coverage: CI passes but production fails because the test suite doesn't exercise the changed behavior.

---

## 4. Optimization

### Within-PR (Review Cycles)

- Typical PR: 1–3 review cycles before merge
- CI feedback arrives in minutes; human review in hours
- Copilot review reduces human review burden by ~20–30% (GitHub data)
- Request-changes → fix → re-review cycle averages 4–8 hours

### Cross-PR (Organizational Learning)

- Code review guidelines evolve from recurring comment patterns
- CI pipeline improvements (new checks) propagate to all future PRs
- CODEOWNERS files route reviews to domain experts
- Post-incident reviews update review checklists

### Convergence Pattern

```
Review cycle:  1     2     3
Issues found:  8     2     0
CI status:     fail  pass  pass
Approval:      no    no    yes
```

Most PRs converge in 2–3 cycles; complex PRs may require 5+.

---

## 5. Memory

| Memory Type | Scope | Content | Decay |
|-------------|-------|---------|-------|
| PR conversation | PR lifetime | Comments, review threads | Archived on merge |
| CI configuration | Repository | Test suites, lint rules, build steps | Updated via PR |
| CODEOWNERS | Repository | Review routing rules | Updated via PR |
| Branch protection | Repository | Required checks, approval count | Admin-managed |
| Git history | Repository | All merged code, blame | Permanent |
| Copilot training | Global | Public code patterns | Model updates |

**Critical memory gap:** Review feedback on PR #123 does not automatically inform review of PR #456 unless reviewers manually apply learned patterns. Organizational memory depends on human transfer.

---

## 6. Success Factors

1. **Automated gatekeeping** — CI blocks merge on test failure
2. **Distributed review** — Multiple reviewers catch different issue classes
3. **Async collaboration** — Contributors and reviewers need not be co-located
4. **Audit trail** — Every comment, commit, and approval is logged
5. **Incremental integration** — Small PRs converge faster than large ones
6. **Tool ecosystem** — Linters, security scanners, and AI review integrate via CI

---

## 7. Failure Modes

| Failure | Frequency | Impact | Mitigation |
|---------|-----------|--------|------------|
| Rubber-stamp approval | Medium | Defects merge without review | Required reviewers, CODEOWNERS |
| Review latency | High | PRs stall for days | Review SLAs, rotation schedules |
| CI false confidence | Medium | Tests pass, production fails | Coverage requirements, staging deploys |
| Large PR paralysis | Medium | Too many changes to review effectively | PR size limits, splitting guidance |
| Reviewer burnout | Medium | Quality degrades with volume | Review load balancing |
| Flaky CI | Medium | Non-deterministic pass/fail | Flaky test quarantine |
| Security scan false positives | High | Alert fatigue, ignored warnings | Triage workflows |
| Knowledge silos | Medium | Only one reviewer understands code | CODEOWNERS, pair review |

---

## 8. LES Evaluation

**Estimation basis:** DORA metrics, GitHub Copilot studies, industry CI/CD benchmarks, architectural analysis.  
**Confidence:** Medium-high (extensive industry data, variable across organizations)

### Raw Metric Estimates

| Metric | Estimate | Basis |
|--------|----------|-------|
| G_final | 0.92 | ~92% of merged PRs don't cause incidents (DORA elite) |
| G_target | 0.90 | Industry standard for change failure rate |
| T_actual | 2.5 cycles | Median review cycles per PR |
| τ_median | 4 hours | Median cycle time (CI + review) |
| C_total | ~$50/PR | Engineer time (2.5 × 2h × $50/h) + CI compute |
| ΔG | 0.15 | From initial submission to merge-ready |
| Perturbation: CI outage | 0.70 | Manual review only |
| Perturbation: key reviewer unavailable | 0.80 | Delay, not quality loss |
| Scale (team size 2,4,8,16) | 0.95, 0.90, 0.85, 0.78 | Brooks's law effect |
| H_interventions | 2.5/PR | Human review cycles (by design) |
| Violations | Low | Security incidents from merged PRs ~2% |

### Category Scores

| Category | N | Justification |
|----------|---|---------------|
| **Effectiveness** | 0.92 | High merge quality at elite organizations; varies widely |
| **Speed** | 0.75 | Hours per cycle is fast for engineering but slow for hotfixes |
| **Cost** | 0.70 | $50/PR in engineer time is significant at scale |
| **Robustness** | 0.85 | CI outage degrades but human review compensates |
| **Scalability** | 0.78 | Review bottlenecks emerge at 16+ person teams |
| **Safety** | 0.88 | Security scanning + review catches most issues; not all |
| **Adaptability** | 0.80 | New languages/frameworks work via CI config changes |
| **Autonomy** | 0.75 | CI is autonomous; merge requires human approval |

### Composite

```
LES = 0.20×0.92 + 0.15×0.75 + 0.12×0.70 + 0.13×0.85 + 0.10×0.78 + 0.12×0.88 + 0.10×0.80 + 0.08×0.75
    = 0.184 + 0.113 + 0.084 + 0.111 + 0.078 + 0.106 + 0.080 + 0.060
    = 0.816 ≈ 0.82
```

**LES: 0.82**

### Diagnostic Summary

- Convergence rate: 0.06 G-units/cycle (issues found decreases ~60% per cycle)
- Weakest category: Scalability (0.78)—review bottlenecks at scale
- Strongest category: Effectiveness (0.92)
- Key improvement path: AI review quality, cross-PR memory, automated PR splitting

---

## 9. Lessons for Loop Engineers

1. **Automated gates are non-negotiable** — CI pass/fail provides the loop's highest-fidelity signal
2. **Human review adds irreplaceable value** — Semantic and design feedback cannot be fully automated
3. **Small iterations converge faster** — PR size is the strongest predictor of cycle time
4. **Memory is the scaling bottleneck** — Organizational learning doesn't transfer automatically between PRs
5. **The loop is only as good as its tests** — CI confidence is bounded by test coverage
6. **Async is a feature** — The loop works across time zones because it's event-driven, not synchronous