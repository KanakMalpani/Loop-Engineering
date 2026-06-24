# Good First Issues

Actionable contribution entry points. File these as GitHub issues or pick one and open a PR.

---

## Validation and specs

1. **Validate `interview-coach.yaml` in production context** — Run `scripts/validate_loop_library.py`; document domain-specific `inputs.schema` extensions in companion `.md`.

2. **Extend `coding-agent.yaml` inputs** — Add repository path and branch fields to `inputs.schema` with examples.

3. **LSS spec fix template** — Use `.github/ISSUE_TEMPLATE/lss-spec-fix.md` for any validator failure.

---

## Benchmarks

4. **Reproduce LB-CR-1 baseline** — [BEAT_LB-CR-1.md](BEAT_LB-CR-1.md). Target LES **86.7**.

5. **Publish LB-RS-1 baseline** — [BEAT_LB-RS-1.md](BEAT_LB-RS-1.md). Target LES **81.9**.

6. **Publish LB-MA-1 baseline** — [BEAT_LB-MA-1.md](BEAT_LB-MA-1.md). Target LES **86.5**.

---

## Case studies

7. **Add external case study** — Real org or OSS project **not** already in `case-studies/` (Toyota, GitHub PR, AlphaGo exist). Use case-study issue template; include LES scores.

8. **Map Cursor agent loop to LSS** — **Done (template):** [cursor-agent-loop.md](../case-studies/cursor-agent-loop.md). External PRs welcome for LES_obs.

9. **Close LE-OP-11 partial data** — **Done:** [tools/level_recommender.py](../tools/level_recommender.py) · [results](../benchmarks/results/le-op-11-recommender-v0.1.json).

10. **LoopNet explore histograms** — **Done:** `python examples/loopnet-explore/explore.py --plot-dir docs/loopnet/histograms`

---

## How to claim

Comment on the matching GitHub issue or open a PR referencing the item number above.

**External adoption pack:** [EXTERNAL_SUBMISSIONS.md](EXTERNAL_SUBMISSIONS.md)
