# 5-minute offline demo

Cold start for the spec, a deterministic trace, and the fixed-benchmark stub table. No model calls.

## Prerequisites

- Python 3.12 or newer (`python3`)
- bash
- pip on the **first** run only: editable installs for `loopgym`, `loopbench`, `loop-observability`, and `loopnet`, plus `pytest` (hidden tests shell out to `python -m pytest`). `loop-core` is not pip-installable; the demo uses it from the tree.

After install, `$DEMO_VENV` or `./.venv-demo` holds a `.demo-stamp` (sha256 of the five package `pyproject.toml` files, `demo/demo.sh`, and `python3 --version`). When the stamp matches and imports succeed, the script prints `deps: cached (stamp ok)` and skips `venv`/`pip`—warm runs need no network. Delete `.demo-stamp` (or change any stamped file) to force reinstall.

After that, the three steps stay on this machine: SimEnv uses MockLLM, and the benchmark step reads local fixtures and a local results file.

## One command

From a fresh clone, at the repository root:

```bash
./demo/demo.sh
```

The script creates `./.venv-demo` (or `$DEMO_VENV` if you set it), installs the editable packages above on a cold run, then runs `python demo/demo_steps.py all`. A warm run finishes in a few seconds. The script prints total elapsed seconds at the end.

## What each step shows

**1. SPEC.** Loads `packages/loopgym/loopgym/envs/loopbench/code-repair-v1/spec.yaml` and compiles it with `loopgym.runtime.compiler.compile_lss`. Prints workers, evaluators, feedback channels, termination, and cost limits.

**2. TRACE.** Runs one SimEnv episode (`loopbench/code-repair-v1`, task `cr-001`, seed `0`) through `loopotel.integrations.loopgym.run_traced_episode`. MockLLM returns prose, not a patch, so the hidden-test score stays 0 and the loop stops at `max_iterations (6)`. Writes a Loop Trace Format document to `demo/out/trace.json` and prints the OpenTelemetry span tree from that document.

**3. BENCHMARK.** Imports `loopgym.evaluators.sandbox_tests` and scores each fixture: the reference patch in `packages/loopbench/fixtures/_reference` must be 1.0, and empty output must be 0.0. Then prints a three-loop table read from `benchmarks/loopbench-validity/results/stub-fixed-all-10.json`. That file is not modified.

**4. PACKAGES.** After the trace step, loads `packages/loop-core/tools/validate_lss.py` by path with `importlib` (loop-core is not pip-installable) and validates the same LSS YAML against `specs/lss-1.0.schema.json`. Rebuilds a LoopGym episode dict from iteration spans in the trace, exports a LoopNet `ln/record-v1` via `loopgym.export.loopnet.episode_to_record`, validates the record against `packages/loopnet/schema/loopnet-record-v1.json`, and runs `loopnet.les.trajectory_diagnostics`. Feeds one MockLLM run through `loopbench.les_compute.compute_task_les` (scoring math only—not a benchmark run). Prints what loopgym and loopotel contributed (SimEnv path, `gen_ai` span counts, `fail.*` events, LTF validation). Writes `<outdir>/record.json`.

## Known risks

- `loopotel.integrations.loopgym.run_traced_episode` imports the private helper `loopgym.export.loopnet._infer_failure_mode` to choose the `fail.*` event name on failed episodes. A LoopGym refactor of that helper can break the emitted failure event without changing the demo script.
- MockLLM `gen_ai` spans use `gen_ai.system=mock` and `gen_ai.request.model=mock-llm`; `run_traced_episode` does not pass output token counts, so those attributes are absent on worker spans.

## Sample output

```text
=== 1. SPEC ===
spec: packages/loopgym/loopgym/envs/loopbench/code-repair-v1/spec.yaml
compile_lss: ok  loop_name=code-repair-loop  version=1.0.0
workers (1):
  - implementer: Analyze failing tests and produce a minimal code patch
evaluators (2):
  - test_runner: deterministic
  - quality_rubric: llm_rubric
feedback channels (2):
  - tests_to_implementer: evaluators.test_runner -> workers.implementer  fields=['failure_codes', 'remediation_hints']
  - rubric_to_optimizer: evaluators.quality_rubric -> optimization_strategy.prompt_refinement  fields=['failure_codes', 'remediation_hints']
termination:
  compiled quality_threshold: 0.8
  compiled max_iterations: 6
cost limits:
  per_iteration_usd: 0.2
  cumulative_usd: 0.6
  on_exceed: halt

=== 2. TRACE ===
episode: task=cr-001 seed=0 success=False quality_score=0.0 termination=max_iterations (6)
OpenTelemetry span tree (loopotel LTF spans):
loop.run  loop.goal_target=0.8 loop.outcome=failure loop.termination_reason=max_iterations (6)
  loop.iteration  loop.iteration=1 loop.goal_score=0.0 loop.goal_target=0.8 loop.les.cumulative_normalized=0.0 loop.les.effectiveness=0.0 loop.worker.id=implementer loop.evaluator.id=test_runner
    event loop.iteration.start
    event loop.worker.complete
    event loop.evaluator.complete
    event loop.iteration.end
spec_pins: {"les": "les@1.0.0", "lss": "lss@1.0.0", "ltf": "ltf@0.1.0"}

=== 3. BENCHMARK ===
  cr-001: reference_patch=1.0 empty_output=0.0  (evaluator stub check)
loop                    fixed_reply  feedback_stub  label
bad-1-no-feedback            0.0000         0.1667  pending fixed benchmark acceptance
bad-2-no-tests               0.0000         0.0000  pending fixed benchmark acceptance
good-1-fast                  0.0000         1.0000  pending fixed benchmark acceptance
Total elapsed seconds: 9.78
```

The trace excerpt shows the first iteration only. The file on disk has all six.

## SHOWN vs PLANNED

Checked against `packages/loop-observability/specs/otel-semconv-loop.md`, `loopotel/tracer.py`, and `loopotel/integrations/loopgym.py`. The demo prints an attribute as SHOWN only when this episode's trace actually contains it.

**SHOWN**

- Iteration span `loop.iteration` (child of `loop.run`)
- `loop.goal_target` (0.8, from the spec success rule)
- LES attributes `loop.les.cumulative_normalized` and `loop.les.effectiveness`
- `spec_pins`: `lss@1.0.0`, `les@1.0.0`, `ltf@0.1.0`

**PLANNED (not built yet)**

- `loop.cost_usd` on this path. `LoopTracer.emit_iteration` accepts `cost_usd`, and `otel_attributes` will write `loop.cost_usd` when it is not null. `run_traced_episode` never passes it, so the written trace omits the key.
- F-code / `fail.*` events. The semconv draft describes `loop.safety.violation` with `loop.failure.code`. The tracer emits `loop.iteration.start`, `loop.iteration.end`, `loop.worker.complete`, and `loop.evaluator.complete` only. `fail.*` codes exist on the LoopGym evaluator result, not as trace events.
- `gen_ai.*` spans. loopotel has no `gen_ai` span names or attributes. The tree is the `loop.*` convention (`loop.run`, `loop.iteration`).

## Benchmark scores

Every score in the LoopBench table is labelled **pending fixed benchmark acceptance**. No real-model acceptance run has completed. The 1.0 / 0.0 lines are evaluator stub checks (reference patch vs empty output), not acceptance scores.

Why the published acceptance path differs from the frozen criterion: [benchmarks/loopbench-validity/DEVIATION.md](../benchmarks/loopbench-validity/DEVIATION.md).
