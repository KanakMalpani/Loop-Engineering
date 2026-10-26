# Loop stack monorepo migration plan (Deliverable C)

Branch `chore/monorepo-dryrun` of `KanakMalpani/Loop-Engineering`. Written Wed 21 Oct 2026, ~2:15 AM IST. Due Thu 22 Oct, 6 PM IST. Revised Mon 26 Oct 2026.
Updated Mon 26 Oct 2026, ~08:10 IST (status facts re-verified).
Status: **dry run, not merged.** Nothing here has been done to `main`, the old repos, or CI unless stated.

## 0. Current state (verified)

- Base: `main` @ `7212e5e`. Five repos imported under `packages/` with `git subtree add` (no `--squash`). The original SHAs are kept as ancestors.

| Package dir | Source repo | Source HEAD | Commits | Import commit | Method (reason) |
|---|---|---|---|---|---|
| `packages/loop-core` | Loop-Core-Engineering | `77f87a2` | 26 | `8d16c33` | `git subtree add`, no squash (keeps original SHAs, no history rewrite; see §1) |
| `packages/loop-observability` | loop-observability | `1db686b` | 8 | `d4f180f` | `git subtree add`, no squash (keeps original SHAs, no history rewrite; see §1) |
| `packages/loopbench` | LoopBench | `109d31f` | 303 | `6da5988` | `git subtree add`, no squash (keeps original SHAs, no history rewrite; see §1) |
| `packages/loopgym` | LoopGym | `5d67a9d` | 27 | `36c3283` | `git subtree add`, no squash (keeps original SHAs, no history rewrite; see §1) |
| `packages/loopnet` | loopnet | `a4ea88b` | 21 | `7a1e270` | `git subtree add`, no squash (keeps original SHAs, no history rewrite; see §1) |

- All five are **KEEP** per `/workspace/loop-verdict-v2.md`. No component reached ALIGN (≥70%) or DROP. LTF scored 61%, LSS 44%, LES 33%, LoopBench 55% and LoopGym 61%.
- loopnet stays **frozen** (no feature work). PR #17 ([feat(loop-library): document interview-coach domain inputs and validation (#1)](https://github.com/KanakMalpani/Loop-Engineering/pull/17), head `feat/1-validate-interview-coach` @ `283b604`, base `main`): **OPEN**, draft, not merged, mergeable; its "Validate loop-library" check **SUCCESS** (20 Oct). QA bot passed it at `283b604` merged onto `7212e5e` (relayed by Engineering Lead). The merge is **waiting on Kanak's direct approval** (a relayed approval does not count); it is still an open draft at `283b604` (gh, 26 Oct 2026 08:12 IST).
- Remote `main` @ `7212e5e`. Remote `dryrun/loop-monorepo` still exists, empty at `7212e5e`. Deleting it **needs Kanak's approval**.
- Remote `chore/monorepo-dryrun` @ `fe4c21a`; the local branch has further unpushed commits (Row 4 demo work). Pushing it **needs Kanak's approval**.
- Old clones for comparison are in `/workspace/mono-survey/` (the 5 repos plus Argus and Trellis).

## 1. Subtree vs filter-repo

| | `git subtree add` (used) | `git filter-repo` + merge |
|---|---|---|
| History | Preserved verbatim; original SHAs reachable as ancestors | Rewritten: every commit gets a new SHA |
| Existing references (issues, PRs, docs citing SHAs) | Still resolve | Break |
| Path in old commits | Old commits show root-relative paths; `git log -- packages/x` needs `--follow` or `git log <import>^2` | Paths rewritten to `packages/x/...`, so per-path log is clean |
| Ongoing sync from old repo | `git subtree pull --prefix packages/x <repo> main` | Re-run filter, error-prone |
| Policy | Allowed | **Disallowed** (history rewrite) |

**Recommendation: keep `git subtree add`.** It doesn't rewrite history, keeps every original SHA (`77f87a2`, `1db686b`, `109d31f`, `5d67a9d`, `a4ea88b`) reachable, and allows `subtree pull` until cutover. The downside is noisier per-path history. That's a cosmetic cost, and the policy rules out the alternative.

## 2. CI and install changes per package

Today each package's workflows live under `packages/<pkg>/.github/workflows/`. GitHub ignores these: only the root `.github/workflows/` runs. The root currently runs `daily-checkin`, `ecosystem-digest`, `external-submission-hint`, `publish-loop-stack`, `publish-loopctl`, `publish-loopforge` and `validate-loop-library`. **So no package CI runs in the monorepo yet.**

| Package | Dist name / version | Python | Existing workflows (in `packages/<pkg>/.github/workflows/`) | Test command today | Monorepo change needed |
|---|---|---|---|---|---|
| loop-core | `loop-engineering-core` 1.0.0 | ≥3.12 | `validate.yml` | `pip install -r requirements.txt`; `python tools/validate_all_examples.py`; `les_calculator.py --spec examples/minimal-loop.yaml` | `working-directory: packages/loop-core` |
| loop-observability | `loopotel` 0.1.0 | ≥3.12 | `test.yml`, `publish.yml` | `pytest tests/ -q`; `loopotel-validate examples/sample-trace.jsonl` | working dir; publish tag prefix `loopotel-v*` |
| loopbench | `loopbench` 0.2.0 | ≥3.12 | `test.yml`, `publish.yml`, `pages.yml`, `leaderboard-{validate,render,pr-hint}.yml`, `suite-baselines.yml`, `sync-platform-pack.yml` | checks out LoopGym into `deps/LoopGym`, then `pip install -e deps/LoopGym`, `pip install -e ".[dev]"`, `pytest tests/ -q`, `loopbench validate leaderboard/entries.json` | **Replace the `deps/LoopGym` checkout with `pip install -e packages/loopgym`** (same-commit dependency); trigger on `packages/loopgym/**` too; `pages.yml` needs one Pages site per repo, so choose a sub-path |
| loopgym | `loopgym` 0.1.4 | ≥3.12 | `test.yml`, `publish.yml` (has `uv.lock`) | `pip install -e ".[dev]"`; `pytest tests/ -q`; `examples/quickstart.py` | working dir; keep `uv.lock` per package |
| loopnet (frozen) | `loopnet` 0.1.0 | ≥3.12 | `validate.yml`, `validate-community.yml`, `upload-hf.yml`, `hf-dataset-upload.yml` | `generate_seed.py --count 500 --seed 42`; `validate_record.py --require-count 500` | validate only; **do not port the HF upload jobs** while frozen |

### Proposed root CI (`.github/workflows/packages-ci.yml` — **TODO, not included** on this branch)
- **Job 1, `changes`:** `dorny/paths-filter` with outputs `core: packages/loop-core/**`, `otel: packages/loop-observability/**`, `bench: [packages/loopbench/**, packages/loopgym/**]`, `gym: packages/loopgym/**`, `net: packages/loopnet/**`.
- **Job 2, `test`:** a matrix over the changed packages. It uses Python 3.12, `working-directory: packages/${{ matrix.pkg }}`, and the per-package commands above.
- **Publish:** one workflow keyed on tag prefix (`loopotel-v*`, `loopbench-v*`, `loopgym-v*`, `loop-core-v*`). Each package builds from its own directory. Move PyPI trusted-publisher settings to the new repo before the first release (done by Kanak on PyPI; external step, **needs Kanak's approval**).
- **Old per-package workflow files:** delete them only after the root workflow is green (a separate commit, **needs Kanak's approval**).

### Local install / venv
- One venv at the repo root, Python 3.12. Editable installs in dependency order: `pip install -e packages/loopgym[dev] -e packages/loopbench[dev] -e packages/loop-observability -e packages/loop-core`. loopnet is installed only when needed.
- On this branch: `9dd5523` made loopbench `pip install -e` in the venv, so tests run without `PYTHONPATH`. The demo uses `.venv-demo` (Python 3.12), installs all five packages (including loopnet), and skips reinstall when the stamp file `.demo-stamp` matches (warm demo run is offline). As of `58d7530`, QA bot passed a cold run at 10 to 11 s per run (fresh venv per cold run).
- Optional follow-up (estimate 0.5 day): a uv workspace (`[tool.uv.workspace] members = ["packages/*"]`) to replace the per-package `uv.lock`.

## 3. Step order (now → cutover)

Each step lists rollback consistent with §4 (Rollback plan) below.

1. **Finish dry-run branch + QA** on `chore/monorepo-dryrun` (local work including Row 4 demo). Rollback: abandon or reset the branch; `main` unchanged.
2. **Push branch** to `origin/chore/monorepo-dryrun` — **needs Kanak's approval**. Rollback: leave it (no change to `main`); deleting the remote branch also **needs Kanak's approval**.
3. **Add `.github/workflows/packages-ci.yml`** (**TODO, not included** today) and get it green; still no root package CI until this lands. Rollback: revert the CI commit on the dry-run branch.
4. **Merge** into `main` (PR; no force-push) — **needs Kanak's approval**; not before a counted acceptance run is graded (none yet as of 26 Oct). Rollback: §4 item 2 (`git revert -m 1` on `main`).
5. **Move PyPI trusted publishers / HF settings** to the monorepo — **needs Kanak's approval** (external). Rollback: §4 item 5 (keep old publisher entries until first monorepo publish succeeds).
6. **Delete per-package workflow files** under `packages/*/.github/workflows/` — **needs Kanak's approval**. Rollback: restore files from git history on `main`.
7. **README banners** on old repos + **archive** the five superseded repos — **needs Kanak's approval**. Rollback: §4 item 3 (unarchive; subtree split if needed).
8. **Delete** remote `dryrun/loop-monorepo`, and later `chore/monorepo-dryrun` after merge — **needs Kanak's approval**. Rollback: recreate empty `dryrun/loop-monorepo` at `7212e5e` if needed; the merged history remains on `main`.

## 4. Rollback plan

Every step before cutover can be undone, because the old repos are untouched and history isn't rewritten.

1. **Before merge to main:** abandon the `chore/monorepo-dryrun` branch. `main` stays at `7212e5e`. Nothing else changes.
2. **After merge, before archiving:** `git revert -m 1 <merge-commit>` on `main` (no force-push). The old repos are still live and authoritative, and nothing was archived.
3. **After archiving:** unarchive in GitHub settings (reversible, by Kanak). Any monorepo-only commits go back with `git subtree split --prefix packages/<pkg>` and a normal push or PR to the old repo. SHAs before the import are identical, so it fast-forwards.
4. **Freeze rule for the window:** between merge and archive, commits go only to the monorepo. If an old repo gets a commit, pull it in with `git subtree pull --prefix packages/<pkg>`, without `--squash`.
5. **PyPI:** keep the old repos' trusted-publisher entries until the first successful publish from the monorepo.

## 5. Archive list (after cutover; NOT done, needs Kanak's approval)

Classification is from `gh repo list KanakMalpani --limit 200` (read-only, 21 Oct 2026). None of them are archived today.

**A. Superseded by the monorepo (archive after cutover):**

| Repo | Last push | Note |
|---|---|---|
| Loop-Core-Engineering | 2026-06-30 | → `packages/loop-core` |
| loop-observability | 2026-06-30 | → `packages/loop-observability` |
| LoopBench | 2026-08-13 | → `packages/loopbench`; pushed after the others, so check for open PRs/issues first |
| LoopGym | 2026-06-30 | → `packages/loopgym` |
| loopnet | 2026-06-30 | → `packages/loopnet` (frozen; the HF dataset link must still resolve) |

Before archiving each one: no open PRs, a README banner pointing to `Loop-Engineering/packages/<pkg>`, and its PyPI/HF publishing moved.

**B. Possibly dead (not part of this migration; Kanak to decide):** no pushes in 4+ months as of 21 Oct 2026. This is a guess from push date only, not a judgement on value: `Autonomous-Startup-in-a-Box` (2026-05-12), `General-Private-Skills` (2026-03-21), `campaignx_mvp` (2026-03-07), `SPAM` (2026-02-19). Pushed June 2026: `PEFT`, `ecell-commerce`, `jarvis-v1-private`.

**C. Forks (listed separately; archive or delete is Kanak's call):** `x-algorithm` (2026-08-14), `everything-claude-code` (2026-04-21), `claw-code` (2026-04-01).

**Not to archive:** Loop-Engineering (target), Argus, Trellis (active, unrelated, see §7), and the other recently pushed repos.

## 6. Planned work items (all efforts are **estimates**, engineer-days)

| # | Item | Scope | Estimate |
|---|---|---|---|
| W1 | LTF → OTel redesign in `packages/loop-observability/loopotel` | On this branch (local, not yet pushed): loopotel already emits worker `gen_ai.*` spans (`gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`) via `LoopTracer.emit_llm_call`, and `fail.*` events (`loop.failure.code` / `loop.failure.f_code`) via `emit_failure`, wired into `run_traced_episode`; the demo exercises all five packages. Still open: fuller redesign (`invoke_workflow`/`invoke_agent`, `gen_ai.evaluation.*`, output tokens, real providers). Keep a thin `loop.*` profile only for the unique parts: iteration span kind + `loop.iteration`, `loop.goal_target`, `loop.cost_usd`, `loop.les.*` attrs, `spec_pins`, F-code `loop.safety.violation` events. Update `specs/`, the exporter, the validator and tests. | 5–8 d |
| W2 | LoopGym OpenEnv adapter | Wrap LoopGym envs (SimEnv, PerturbedSim) in the OpenEnv interface, with tests | 2–3 d |
| W3 | LoopGym Inspect adapter | Expose LoopGym tasks as Inspect tasks/solvers + scorer bridge | 2–3 d |
| W4 | Full `suite-repair` acceptance | Run the whole suite named in `CRITERION.md`, not only LB-CR-1 (see `benchmarks/loopbench-validity/DEVIATION.md`) | 1–2 d build + 4.5–9 h run |
| W5 | LB-SAFE fixtures | Real fixture projects for the safety tasks (none exist) | 1–2 d |
| W6 | `tool_pass_rate` evaluator for LB-REACT | Missing metric needed for the composite score | 1 d |
| W7 | cursor-agent sandbox/concurrency caveat | Sandboxed calls time out at 5 concurrent, so attempt 2 is capped at 4. The wrapper uses the shared Cursor login. Document it, find the root cause (load avg 70–108 observed), and make concurrency a config setting | 1–2 d |
| W8 | Root CI matrix (§2) + publish workflow | Write `.github/workflows/packages-ci.yml` (**TODO, not included** on this branch), verify green, then remove the per-package workflow files | 1–1.5 d |

Total estimate is about 14–23 engineer-days. W1 to W3 are the KEEP follow-ups from the verdict, W4 to W7 are the benchmark follow-ups, and W8 is the migration itself.

## 7. Collisions with Argus and Trellis

- Ran `grep -rlE 'loopotel|loopbench|loopgym|loopnet|loop_core'` over `*.rs`, `*.py`, `*.toml` in `/workspace/mono-survey/Argus` and `/workspace/mono-survey/Trellis`: **no matches.** Neither imports or depends on the loop packages.
- Trellis's Python package is `heddura` (`Trellis/pyproject.toml`), so there's no name clash with `loopotel`, `loopbench`, `loopgym`, `loopnet` or `loop-engineering-core`. Argus is Rust, so there's no Python namespace overlap.
- Result: neither repo is affected by the migration, and both stay separate.
- Caveat: only the local clones were checked (not other branches, and only those file types).

## 8. Approvals needed from Kanak

1. **Merge** `chore/monorepo-dryrun` → `main` (via PR; not before a counted acceptance run is graded — none yet as of 26 Oct).
2. **CI changes:** add the root `packages-ci.yml` (**TODO, not included** on this branch; no root package CI runs yet) and publish workflow, delete the per-package workflow files, and move PyPI trusted publishers and HF upload settings.
3. **Archiving** the 5 superseded repos (§5A) after cutover, plus any decision on §5B and the forks in §5C.
4. **Branch deletion:** `dryrun/loop-monorepo` (empty at `7212e5e`), and later `chore/monorepo-dryrun` after merge.
5. Confirm loopnet stays frozen. PR #17: merge **waiting on Kanak's direct approval**; still an open draft at `283b604` (gh, 26 Oct 2026).
