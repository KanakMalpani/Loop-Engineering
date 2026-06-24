# Good First Issues

Actionable contribution entry points. File these as GitHub issues or pick one and open a PR.

---

## Validation and specs

1. **Validate `interview-coach.yaml` in production context** — Run `scripts/validate_loop_library.py`; document domain-specific `inputs.schema` extensions in companion `.md`.

2. **Extend `coding-agent.yaml` inputs** — Add repository path and branch fields to `inputs.schema` with examples.

3. **LSS spec fix template** — Use `.github/ISSUE_TEMPLATE/lss-spec-fix.md` for any validator failure.

---

## Benchmarks

4. **Reproduce LB-CR-1 baseline** — One command: [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md). Target LES **86.7** ([baseline](../benchmarks/results/lb-cr-1-baseline.json)).

5. **Publish ALS-T1 Research Synthesis baseline** — First external row on LoopBench for task ALS-T1.

6. **Publish ALS-T3 Multi-Agent Debate baseline** — Hardest ALS task; document harness and perturbation runs.

---

## Case studies

7. **Add external case study** — Real org or OSS project **not** already in `case-studies/` (Toyota, GitHub PR, AlphaGo exist). Use case-study issue template; include LES scores.

8. **Map Cursor agent loop to LSS** — **Template landed:** [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md). External PRs welcome to extend with LoopBench LES_obs.

---

## Research

9. **Close LE-OP-11 partial data** — Task→level recommender v0.1 using LoopNet v0.2 features; link benchmark or notebook.

10. **LoopNet explore script enhancement** — Add histogram plots to `examples/loopnet-explore/explore.py` (matplotlib optional dep).

---

## How to claim

Comment on the matching GitHub issue or open a PR referencing the item number above.
