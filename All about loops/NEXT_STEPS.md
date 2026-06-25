# Next Steps — 2027 execution (June 2026)

**Adoption path:** [REPRODUCE.md](../contributions/REPRODUCE.md) → [Discussion #10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10)

---

## Completed (this sprint)

| Item | Artifact |
|------|----------|
| Adoption tracker (daily CI) | [docs/adoption-tracker/](../docs/adoption-tracker/) |
| PyPI loopbench 0.1.1 | [pypi.org/project/loopbench](https://pypi.org/project/loopbench/) |
| LSS 1.1 stable | [Loop-Core lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md) |
| LE-OP-11 recommender v0.1 | [tools/level_recommender.py](../tools/level_recommender.py) |
| LoopNet histograms | [docs/loopnet/histograms](../docs/loopnet/histograms/) |
| BEAT_LB-CR-1 amplification | [BEAT_LB-CR-1.md](../contributions/BEAT_LB-CR-1.md) · LoopBench README · HF card |
| RFC #11 outreach | [LangGraph #8186](https://github.com/langchain-ai/langgraph/issues/8186) · [CrewAI #6316](https://github.com/crewAIInc/crewAI/issues/6316) |
| External submission pack | [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) |

---

## Still open (community)

Tracked daily: [docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md)

| Item | Entry |
|------|-------|
| Non-maintainer LoopBench row | [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [BEAT_LB-CR-1.md](../contributions/BEAT_LB-CR-1.md) · [#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) |
| External reproduction | [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [#10](https://github.com/KanakMalpani/Loop-Engineering/discussions/10) |
| External case study | [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [#7](https://github.com/KanakMalpani/Loop-Engineering/issues/7) |
| RFC #11 framework comments | LangGraph [#8186](https://github.com/langchain-ai/langgraph/issues/8186) · CrewAI [#6316](https://github.com/crewAIInc/crewAI/issues/6316) · [#11](https://github.com/KanakMalpani/Loop-Engineering/discussions/11) |

---

## Next maintainer targets

1. ~~LSS 1.1 **stable** promotion~~ → [Loop-Core lss-1.1.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/lss-1.1.md)
2. ~~LoopBench **PyPI** 0.1.1~~ → live on PyPI
3. ~~LoopNet explore histograms~~ → [docs/loopnet/histograms](../docs/loopnet/histograms/)
4. ~~LE-OP-11 recommender v0.1~~ → [tools/level_recommender.py](../tools/level_recommender.py)

## Phase 2 completed (maintainer)

| Item | Artifact |
|------|----------|
| BEAT LB-RS-1 / LB-MA-1 | [BEAT_LB-RS-1.md](../contributions/BEAT_LB-RS-1.md) · [BEAT_LB-MA-1.md](../contributions/BEAT_LB-MA-1.md) |
| LE-OP-10 partial | [le-op-10-associativity.md](../research/le-op-10-associativity.md) |
| Schema versioning | [Loop-Core schema-versioning.md](https://github.com/KanakMalpani/Loop-Core-Engineering/blob/main/specs/schema-versioning.md) |
| LoopGym compose env spec | [LOOPGYM.md](../research/LOOPGYM.md) `loopbench/composed-swarm-v1` |
| LangGraph bridge case study | [langgraph-composition-bridge.md](../case-studies/langgraph-composition-bridge.md) |
| LES baseline audit CI | [validate_baselines.py](../scripts/validate_baselines.py) |

## Phase 3 completed (maintainer)

| Item | Artifact |
|------|----------|
| BEAT LB-COMP-1 | [BEAT_LB-COMP-1.md](../contributions/BEAT_LB-COMP-1.md) |
| LoopGym composed env | [LoopGym](https://github.com/KanakMalpani/LoopGym) `loopbench/composed-swarm-v1` |
| CrewAI bridge | [crewai-composition-bridge.md](../case-studies/crewai-composition-bridge.md) |
| LE-OP-04 partial | [le-op-04-evaluator-composition.md](../research/le-op-04-evaluator-composition.md) |
| Composition complexity tool | [loop_complexity_analyzer.py](../tools/loop_complexity_analyzer.py) |
| LE-OP-21 pilot | [le-op-21-harness-compare-v0.1.json](../benchmarks/results/le-op-21-harness-compare-v0.1.json) |
| LoopNet changelog | [LOOPNET-SCHEMA-CHANGELOG.md](../research/LOOPNET-SCHEMA-CHANGELOG.md) |
| Adoption wave 3 | [adoption_wave3.py](../scripts/adoption_wave3.py) · [ADOPTION.md](../contributions/ADOPTION.md) |
| Community handoff | [COMMUNITY_HANDOFF_PHASE3.md](../contributions/COMMUNITY_HANDOFF_PHASE3.md) |

## Community (tracked daily)

[docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md) · [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [COMMUNITY_HANDOFF_PHASE4.md](../contributions/COMMUNITY_HANDOFF_PHASE4.md)

## Phase 4 completed (maintainer)

| Item | Artifact |
|------|----------|
| LoopBench COMP wire | `loopbench/composed-swarm-v1` on LB-COMP-1 |
| loopgym PyPI 0.1.1 | [LoopGym](https://github.com/KanakMalpani/LoopGym) release |
| Adoption wave 4 | [adoption_wave4.py](../scripts/adoption_wave4.py) |
| LE-OP-04 benchmark | [benchmarks/evaluator-composition/](../benchmarks/evaluator-composition/) |
| Composition diagrams | [loop_diagram_generator.py](../tools/loop_diagram_generator.py) |
| LE-OP-21 v0.2 | [le-op-21-harness-compare-v0.2.json](../benchmarks/results/le-op-21-harness-compare-v0.2.json) |
| Pareto LES tool | [loop_comparison.py --pareto](../tools/loop_comparison.py) |
| Level warn CI | `validate_loop_library --warn-level` in daily checkin |

## Phase 5 completed (maintainer)

| Item | Artifact |
|------|----------|
| Golden Path onboarding | [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) |
| LoopForge v0.2 | [loopforge/](../loopforge/) — fork, compose, export, level hints |
| LoopForge PyPI layout | [loopforge/pyproject.toml](../loopforge/pyproject.toml) · publish workflow |
| loopctl CLI | [tools/loopctl.py](../tools/loopctl.py) |
| LSS 1.1 metadata | `metadata.schema_version: "1.1"` on all loop-library specs |
| Loop Trace 1.0 | [LOOP-TRACE-1.0.md](../standards/LOOP-TRACE-1.0.md) |
| Practitioner curriculum | [education/practitioner/](../education/practitioner/README.md) |
| Adoption wave 5 | [adoption_wave5.py](../scripts/adoption_wave5.py) · [BEAT_TEMPLATE.md](../contributions/BEAT_TEMPLATE.md) |

## Phase 6 completed (maintainer)

| Item | Artifact |
|------|----------|
| loopctl package | [loopctl/](../loopctl/) · PyPI publish workflow |
| Loop Trace emitter | [trace_emitter.py](../implementations/generic/trace_emitter.py) |
| Observed LES | [observed_les.py](../tools/observed_les.py) · `loopctl observed` |
| LoopForge intent (LE-OP-15) | [intent.py](../loopforge/intent.py) · [intent-to-lss benchmark](../benchmarks/intent-to-lss/) |
| LE-OP-10 composition warnings | [composition_validator.py](../tools/composition_validator.py) |
| Adoption wave 6 | [adoption_wave6.py](../scripts/adoption_wave6.py) |
| Submission dry-run | [docs/submission-dry-run/](../docs/submission-dry-run/) |
| LoopNet v0.3 prep | [loopnet_export_trace.py](../scripts/loopnet_export_trace.py) |
| Practitioner exam | [exam-v0.1.md](../education/practitioner/exam-v0.1.md) |
| Q3 status report | [STATUS-2026-Q3.md](../contributions/STATUS-2026-Q3.md) |

## Phase 7 completed (maintainer)

| Item | Artifact |
|------|----------|
| PyPI name sync | `le-loopforge` / `le-loopctl` across Golden Path, README, BEAT |
| Golden Path traces | Step 4b Loop Trace + LoopGym 0.1.2 |
| le-loopctl adoption signal | [track_adoption_signals.py](../scripts/track_adoption_signals.py) |
| LoopNet v0.3 contributor path | [docs/loopnet/CONTRIBUTING-v0.3.md](../docs/loopnet/CONTRIBUTING-v0.3.md) |
| Intent benchmark v0.4 | 30 intents · [manifest.json](../benchmarks/intent-to-lss/manifest.json) |
| Trace-native dry-run | [run_submission_dryrun.py](../scripts/run_submission_dryrun.py) |
| Adoption wave 7 | [adoption_wave7.py](../scripts/adoption_wave7.py) |

## Phase 8 completed (maintainer + community)

| Item | Artifact |
|------|----------|
| Stale doc sweep | [PYPI_NAMING.md](../contributions/PYPI_NAMING.md) · [check_pypi_naming.py](../scripts/check_pypi_naming.py) |
| GitHub outreach | Wave 7 posted on #4, #7, Discussion #10 |
| Exam pilot issue | [#12](https://github.com/KanakMalpani/Loop-Engineering/issues/12) |

## Phase 9 completed (maintainer); community unlocks pending

| Item | Artifact |
|------|----------|
| STATUS Q4 | [STATUS-2026-Q4.md](../contributions/STATUS-2026-Q4.md) |
| External LoopBench template | [external-template-row.json](../docs/submission-dry-run/external-template-row.json) |
| Trace reproduction template | [TEMPLATE-trace-native.md](../docs/reproduction-reports/TEMPLATE-trace-native.md) |
| LoopNet v0.3 schema | Merged [loopnet PR #1](https://github.com/KanakMalpani/loopnet/pull/1) |
| Intent v0.5 composition | [intent.py](../loopforge/intent.py) · [results-v0.5.json](../benchmarks/intent-to-lss/results-v0.5.json) (40 intents) |
| LE-OP-10 counterexamples | [composition-counterexamples/](../standards/examples/composition-counterexamples/) |
| LE-OP-04 v0.2 | [results-v0.2.json](../benchmarks/evaluator-composition/results-v0.2.json) |
| Adoption wave 8 | [adoption_wave8.py](../scripts/adoption_wave8.py) |
| Exam v0.2 | [exam-v0.2.md](../education/practitioner/exam-v0.2.md) |

## Community (tracked daily)

[docs/adoption-tracker/latest.md](../docs/adoption-tracker/latest.md) · [EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [adoption_wave9.py](../scripts/adoption_wave9.py)

## Phase 10 completed (maintainer)

| Item | Artifact |
|------|----------|
| North star | [NORTH_STAR.md](../contributions/NORTH_STAR.md) |
| Golden Path v2 | [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) |
| PyPI-native export | [loopforge/export.py](../loopforge/export.py) |
| loopctl pipeline | [loopctl/pipeline.py](../loopctl/pipeline.py) |
| LangGraph / CrewAI / Cursor packs | [integrate-langgraph](../examples/integrate-langgraph/) · [integrate-crewai](../examples/integrate-crewai/) · [CURSOR.md](../contributions/integrate/CURSOR.md) |
| Adoption wave 9 | [adoption_wave9.py](../scripts/adoption_wave9.py) |
| LE-OP-11 v0.2 gate | [run_level_recommender_benchmark.py](../scripts/run_level_recommender_benchmark.py) |

## Phase 11 completed (maintainer); community unlocks pending

| Item | Artifact |
|------|----------|
| Portable scoring | [loopctl/scoring/](../loopctl/scoring/) · `le-loopctl` **0.2.0** |
| Meta-package | [stack/](../stack/) · `le-loop-stack` **0.1.0** |
| Golden Path v3 | [GOLDEN_PATH.md](../contributions/GOLDEN_PATH.md) |
| Integration hub | [integrate/README.md](../contributions/integrate/README.md) |
| Claude Code / Codex / Agents / Aider / Gemini | [integrate/](../contributions/integrate/) · [examples/integrate-*](../examples/) |
| Copilot / Devin bridges | [COPILOT.md](../contributions/integrate/COPILOT.md) · [DEVIN.md](../contributions/integrate/DEVIN.md) |
| Adoption wave 10 | [adoption_wave10.py](../scripts/adoption_wave10.py) |
| STATUS Q1 2027 | [STATUS-2027-Q1.md](../contributions/STATUS-2027-Q1.md) |
| LoopNet HF v0.3 preview path | [HF-v0.3-preview.md](../docs/loopnet/HF-v0.3-preview.md) |
