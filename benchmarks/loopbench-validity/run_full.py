"""Parallel acceptance runner for the FIXED benchmark: 10 loops x 3 runs, concurrently, real model.

  python run_full.py --confirm-acceptance            # the 30-run acceptance test (not run yet)
  python run_full.py --loops LOOP --runs 1           # a subset (smoke)
  python run_full.py --probe 10                      # concurrency probe: N parallel single calls

Each run calls run_episode once per --seeds value (default 0,1,2,3,4), sequentially.
Loops and CRITERION.md are read as-is (frozen at 49809bc). MockLLM is made to raise.
The scored result is provisional; see DEVIATION.md.
Each run writes <outdir>/<loop>-r<k>.json as soon as it finishes, plus <outdir>/progress.json.
"""
import argparse
import json
import re
import subprocess
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import loopgym as lg
import loopgym.runtime.loop_runtime as rt
import yaml
from loopgym.envs import sim

here = Path(__file__).parent
sys.path.insert(0, str(here))
import cursor_llm
from cursor_llm import CursorAgentLLM, InfraError

PINNED_MODEL = cursor_llm.DEFAULT_MODEL
MIN_AVAILABLE_MB = 4096

MOCK_HITS = []
class _NoMock:
    def __init__(self, *a, **k):
        MOCK_HITS.append(time.time()); raise RuntimeError("MockLLM was constructed - run void")
rt.MockLLM = sim.MockLLM = _NoMock

_progress_lock = threading.Lock()
_progress = {"completed": 0, "total": 0}


def _parse_seeds(text: str) -> list[int]:
    parts = [part.strip() for part in text.split(",")]
    if not parts or any(part == "" for part in parts):
        raise argparse.ArgumentTypeError("seeds must be a comma-separated list of integers")
    try:
        return [int(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be integers") from exc


def _resolve_outdir(text: str) -> Path:
    path = Path(text)
    return path if path.is_absolute() else here / path


def _dump_progress(outdir: Path) -> None:
    """Write progress.json. Caller must hold _progress_lock."""
    path = outdir / "progress.json"
    tmp = outdir / "progress.json.tmp"
    payload = {"completed": _progress["completed"], "total": _progress["total"]}
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(path)


def _reset_progress(outdir: Path, total: int) -> None:
    with _progress_lock:
        _progress["completed"] = 0
        _progress["total"] = total
        _dump_progress(outdir)


def _bump_progress(outdir: Path) -> None:
    with _progress_lock:
        _progress["completed"] += 1
        _dump_progress(outdir)


def _instance_scores(res: dict) -> dict:
    instances = res.get("instances")
    if isinstance(instances, list) and instances:
        return {str(item.get("fixture")): item.get("quality_score") for item in instances}
    fixture = res.get("fixture")
    if fixture is not None:
        return {str(fixture): res.get("quality_score")}
    return {}


def _seed_result(res: dict, status: str, err: str | None) -> dict:
    """Per-seed record. INFRA-FAIL and ERROR score None and stay out of the run mean."""
    if status != "OK":
        return {
            "status": status,
            "score": None,
            "success": None,
            "termination_reason": None,
            "instance_scores": {},
            "error": err,
        }
    raw = res.get("quality_score")
    score = 0.0 if raw is None else float(raw)
    return {
        "status": "OK",
        "score": score,
        "success": res.get("success"),
        "termination_reason": res.get("termination_reason"),
        "instance_scores": _instance_scores(res),
        "error": None,
    }


def _failure_status(exc: BaseException) -> str:
    if isinstance(exc, (InfraError, subprocess.TimeoutExpired)):
        return "INFRA-FAIL"
    return "ERROR"


def _record_failure(by_seed: dict[str, dict], seed: int, exc: BaseException) -> None:
    _seed = _seed_result({}, _failure_status(exc), f"{type(exc).__name__}: {exc}")
    by_seed[str(seed)] = _seed


def _tally(by_seed: dict[str, dict]) -> tuple[int, int, int, float | None]:
    n_ok = sum(rec["status"] == "OK" for rec in by_seed.values())
    n_infra_fail = sum(rec["status"] == "INFRA-FAIL" for rec in by_seed.values())
    n_error = sum(rec["status"] == "ERROR" for rec in by_seed.values())
    ok_scores = [
        rec["score"] for rec in by_seed.values()
        if rec["status"] == "OK" and rec["score"] is not None
    ]
    score = (sum(ok_scores) / len(ok_scores)) if ok_scores else None
    return n_ok, n_infra_fail, n_error, score


def _call_log(llm) -> list[dict]:
    if llm is None:
        return []
    logged = []
    for call in llm.calls:
        entry = dict(call)
        entry["isolated"] = call.get("isolated", cursor_llm.ISOLATE)
        logged.append(entry)
    return logged


def one_run(loop: str, k: int, model: str, task: str, outdir: Path, timeout: int,
            seeds: list[int]) -> dict:
    """One independent run: every seed, sequentially. File written on finish.

    Call retries stay inside CursorAgentLLM. A seed that still has no result is
    INFRA-FAIL with score None. Any other exception is ERROR with score None.
    """
    t0 = time.monotonic()
    llm = None
    by_seed: dict[str, dict] = {}
    try:
        llm = CursorAgentLLM(
            model=model,
            timeout=timeout,
            log_path=outdir / "run.log",
            run_id=f"{loop}/r{k}",
        )
        env = lg.make("loopbench/code-repair-v1", spec_path=str(here / "loops" / f"{loop}.yaml"),
                      backend="live", llm=llm)
        for s in seeds:
            try:
                res = env.run_episode(task_id=task, seed=s)
            except Exception as exc:  # noqa: BLE001  # record and continue; seed is not retried
                traceback.print_exc()
                _record_failure(by_seed, s, exc)
            else:
                by_seed[str(s)] = _seed_result(res, "OK", None)
    except Exception as exc:  # noqa: BLE001  # setup failure: record every seed not yet run
        traceback.print_exc()
        for s in seeds:
            if str(s) in by_seed:
                continue
            _record_failure(by_seed, s, exc)
    n_ok, n_infra_fail, n_error, score = _tally(by_seed)
    out = {
        "loop": loop,
        "run": k,
        "task": task,
        "seeds": list(seeds),
        "model": model,
        "llm_class": type(llm).__name__ if llm is not None else None,
        "mock_constructed": bool(MOCK_HITS),
        "wall_seconds": round(time.monotonic() - t0, 1),
        "score": score,
        "n_ok": n_ok,
        "n_infra_fail": n_infra_fail,
        "n_error": n_error,
        "by_seed": by_seed,
        "calls": _call_log(llm),
        "finished_at": datetime.now(UTC).isoformat(),
    }
    try:
        (outdir / f"{loop}-r{k}.json").write_text(json.dumps(out, indent=2, default=str))
    except Exception:  # noqa: BLE001  # progress still updates; the returned dict is the record
        traceback.print_exc()
    _bump_progress(outdir)
    return out


def _cohort_of(stem: str) -> str:
    """Cohort label is the first comment word of that loop's own spec file."""
    path = here / "loops" / f"{stem}.yaml"
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip().split(":", 1)[0].strip()
    return ""


def _criterion_cohorts() -> tuple[str, str]:
    """Higher-scoring cohort, then lower-scoring cohort, as stated in CRITERION.md."""
    text = (here / "CRITERION.md").read_text(encoding="utf-8")
    match = re.search(r"min\(score of (\w+) loops\) > max\(score of (\w+) loops\)", text)
    if match is None:
        raise RuntimeError("CRITERION.md does not state the cohort comparison")
    return match.group(1), match.group(2)


def _grouped_cohort(rows: list[dict], k: int, cohort: str) -> dict[str, float | None]:
    grouped = {
        r["loop"]: r["score"]
        for r in rows
        if r["run"] == k and _cohort_of(str(r["loop"])) == cohort
    }
    return dict(sorted(grouped.items()))


def criterion_block(rows: list[dict], n_runs: int) -> dict:
    """Each run passes only when the higher cohort's minimum beats the lower cohort's maximum."""
    high_name, low_name = _criterion_cohorts()
    runs = []
    for k in range(n_runs):
        high = _grouped_cohort(rows, k, high_name)
        low = _grouped_cohort(rows, k, low_name)
        high_scores = [score for score in high.values() if score is not None]
        low_scores = [score for score in low.values() if score is not None]
        min_high = min(high_scores) if high_scores else None
        max_low = max(low_scores) if low_scores else None
        if min_high is None or max_low is None:
            tie, passed = None, False
        else:
            tie = min_high == max_low
            passed = min_high > max_low
        runs.append({
            "run": k,
            "good": high,
            "bad": low,
            "min_good": min_high,
            "max_bad": max_low,
            "tie": tie,
            "pass": passed,
        })
    return {"pass": bool(runs) and all(item["pass"] for item in runs), "runs": runs}


def _worker_role_text(stem: str) -> str:
    spec = yaml.safe_load((here / "loops" / f"{stem}.yaml").read_text(encoding="utf-8")) or {}
    workers = spec.get("workers") or []
    worker = workers[0] if workers else {}
    for key in ("system_prompt", "role"):
        value = worker.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return str(worker.get("id") or "")


def _unique_role_stems(stems: list[str]) -> list[str]:
    groups: dict[str, list[str]] = {}
    for stem in stems:
        groups.setdefault(_worker_role_text(stem), []).append(stem)
    return [group[0] for group in groups.values() if len(group) == 1]


def bad3_vs_good(rows: list[dict], n_runs: int) -> list[dict]:
    """Per run, each uniquely-roled loop against each loop in the higher cohort."""
    stems = sorted({str(r["loop"]) for r in rows})
    subjects = _unique_role_stems(stems)
    high_name, _low_name = _criterion_cohorts()
    report = []
    for k in range(n_runs):
        reference = _grouped_cohort(rows, k, high_name)
        for subject in subjects:
            matched = [r for r in rows if r["run"] == k and r["loop"] == subject]
            subject_score = matched[0]["score"] if matched else None
            versus = []
            for loop_name, reference_score in reference.items():
                if subject_score is None or reference_score is None:
                    ties, beats = None, None
                else:
                    ties = subject_score == reference_score
                    beats = subject_score > reference_score
                versus.append({
                    "loop": loop_name,
                    "score": reference_score,
                    "ties": ties,
                    "beats": beats,
                })
            report.append({"run": k, subject: subject_score, "versus": versus})
    return report


def _issue_list(rows: list[dict], status: str) -> list[dict]:
    """Flat summary rows for one seed status: loop, run, seed, error."""
    items = []
    for row in rows:
        for seed, rec in row.get("by_seed", {}).items():
            if rec.get("status") != status:
                continue
            items.append({
                "loop": row["loop"],
                "run": row["run"],
                "seed": int(seed),
                "error": rec.get("error"),
            })
    return items


def _criterion_complete(rows: list[dict]) -> bool:
    """False when any seed is missing or not OK."""
    for row in rows:
        by_seed = row.get("by_seed") or {}
        if len(by_seed) != len(row.get("seeds") or []):
            return False
        if any(rec.get("status") != "OK" for rec in by_seed.values()):
            return False
    return True


def model_check(rows: list[dict]) -> dict:
    """Calls whose requested model is not the pinned acceptance model."""
    violations = []
    for row in rows:
        checked = cursor_llm.calls_model_check(row.get("calls") or [])
        for item in checked["violations"]:
            violations.append({
                "loop": row.get("loop"),
                "run": row.get("run"),
                "call": item["call"],
            })
    return {"pinned": PINNED_MODEL, "valid": not violations, "violations": violations}


def mem_available_mb(meminfo_path: str = "/proc/meminfo") -> int:
    """MemAvailable from a meminfo file, as integer megabytes (kB // 1024)."""
    text = Path(meminfo_path).read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    raise ValueError(f"MemAvailable missing from {meminfo_path}")


def check_launch_memory(outdir_or_logdir) -> dict:
    """Read MemAvailable once and append results/launch-memcheck.log.

    main() passes `here`, so the file is `<here>/results/launch-memcheck.log`.
    """
    available_mb = mem_available_mb()
    time_ist = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(timespec="seconds")
    ok = available_mb >= MIN_AVAILABLE_MB
    record = {
        "available_mb": available_mb,
        "required_mb": MIN_AVAILABLE_MB,
        "ok": ok,
        "time_ist": time_ist,
    }
    log_path = Path(outdir_or_logdir) / "results" / "launch-memcheck.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    status = "PASS" if ok else "ABORT"
    line = (
        f"{time_ist} LAUNCH-MEMCHECK available_mb={available_mb} "
        f"required_mb={MIN_AVAILABLE_MB} result={status}"
    )
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, file=sys.stderr)
    return record


def per_loop_scores(rows: list[dict], n_runs: int) -> dict[str, list]:
    by_key = {(r["loop"], r["run"]): r["score"] for r in rows}
    loops = sorted({r["loop"] for r in rows})
    return {loop: [by_key.get((loop, k)) for k in range(n_runs)] for loop in loops}


def probe(n: int, model: str, timeout: int, cap: int) -> dict:
    from loopgym.evaluators.sandbox_tests import get_fixture
    fx = get_fixture("cr-001")
    prompt = (
        f"Bug description:\n{fx.bug_description}\n\nModule ({fx.module_name}):\n```\n{fx.source}```"
        "\n\nReturn the full corrected module in one fenced code block."
    )
    def call(i):
        llm = CursorAgentLLM(model=model, timeout=timeout); t = time.monotonic()
        try:
            txt = llm.complete(prompt, role="implementer"); e = None
        except Exception as ex:  # noqa: BLE001  # probe records call errors deliberately
            txt, e = "", f"{type(ex).__name__}: {ex}"
        last = llm.calls[-1] if llm.calls else {}
        return {
            "i": i,
            "seconds": round(time.monotonic() - t, 1),
            "error": e,
            "chars": len(txt),
            "usage": last.get("usage"),
            "model_requested": last.get("model_requested"),
            "model_reported": last.get("model_reported"),
        }
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=min(n, cap)) as ex:
        calls = sorted((f.result() for f in [ex.submit(call, i) for i in range(n)]), key=lambda c: c["i"])
    return {"n": n, "max_concurrency": cap, "model": model, "wall_seconds": round(time.monotonic() - t0, 1),
            "errors": [c for c in calls if c["error"]], "calls": calls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=cursor_llm.DEFAULT_MODEL)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--task", default="LB-CR-1")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--seeds", type=_parse_seeds, default=_parse_seeds("0,1,2,3,4"),
                    help="comma-separated seeds (default: 0,1,2,3,4)")
    ap.add_argument("--outdir", default="results/full",
                    help="output directory, relative to this script (default: results/full)")
    ap.add_argument("--loops", nargs="*")
    ap.add_argument("--probe", type=int)
    ap.add_argument("--max-concurrency", type=int, default=5)
    ap.add_argument("--confirm-acceptance", action="store_true")
    a = ap.parse_args()
    cursor_llm.assert_no_unpinned_env()
    identity = cursor_llm.assert_launch_identity()
    if a.confirm_acceptance and a.model != PINNED_MODEL:
        sys.exit(f"acceptance run requires pinned model {PINNED_MODEL}")
    if a.probe:
        cursor_llm.require_pinned_model(a.model)
    elif not a.loops and a.runs == 3 and not a.confirm_acceptance:
        sys.exit("Full 30-run acceptance needs --confirm-acceptance")
    launch_memcheck = check_launch_memory(here)
    if not launch_memcheck["ok"]:
        sys.exit(
            "launch memory check failed: "
            f"available_mb={launch_memcheck['available_mb']} "
            f"required_mb={launch_memcheck['required_mb']}"
        )
    (here / "results").mkdir(exist_ok=True)
    if a.probe:
        r = probe(a.probe, a.model, a.timeout, a.max_concurrency)
        r["launch_identity"] = identity
        r["launch_memcheck"] = launch_memcheck
        r["model_check"] = cursor_llm.calls_model_check(r["calls"])
        if not r["model_check"]["valid"]:
            r["invalid"] = True
        (here / "results" / f"probe-{a.probe}.json").write_text(json.dumps(r, indent=2))
        brief = {k: r[k] for k in ("n", "max_concurrency", "model", "wall_seconds")}
        brief["errors"] = len(r["errors"])
        print(json.dumps(brief))
        if r.get("invalid"):
            sys.exit(1)
        return
    seeds = a.seeds
    loops = a.loops or sorted(p.stem for p in (here / "loops").glob("*.yaml"))
    outdir = _resolve_outdir(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(loop, k) for k in range(a.runs) for loop in loops]
    _reset_progress(outdir, len(jobs))
    started_at = datetime.now(UTC).isoformat()
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=a.max_concurrency) as ex:
        futures = [
            ex.submit(one_run, loop, k, a.model, a.task, outdir, a.timeout, seeds)
            for loop, k in jobs
        ]
        rows = [fut.result() for fut in as_completed(futures)]
    wall = round(time.monotonic() - t0, 1)
    finished_at = datetime.now(UTC).isoformat()
    rows.sort(key=lambda r: (r["run"], r["loop"]))
    criterion_complete = _criterion_complete(rows)
    criterion = criterion_block(rows, a.runs)
    criterion["incomplete"] = not criterion_complete
    checked = model_check(rows)
    if not checked["valid"]:
        criterion["pass"] = False
    summary = {
        "model": a.model,
        "launch_identity": identity,
        "launch_memcheck": launch_memcheck,
        "task": a.task,
        "seeds": seeds,
        "start": started_at,
        "end": finished_at,
        "started_at": started_at,
        "finished_at": finished_at,
        "jobs": len(jobs),
        "max_concurrency": a.max_concurrency,
        "wall_seconds": wall,
        "mock_constructed": bool(MOCK_HITS),
        "provisional": True,
        "deviation": "see DEVIATION.md, DEVIATION-2.md, DEVIATION-3.md",
        "criterion_complete": criterion_complete,
        "model_check": checked,
        "infra_fail": _issue_list(rows, "INFRA-FAIL"),
        "errors": _issue_list(rows, "ERROR"),
        "scores": sorted((r["loop"], r["run"], r["score"]) for r in rows),
        "per_loop": per_loop_scores(rows, a.runs),
        "criterion": criterion,
        "bad3_vs_good": bad3_vs_good(rows, a.runs),
    }
    if not checked["valid"]:
        summary["invalid"] = True
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    brief = ("model", "jobs", "wall_seconds", "mock_constructed", "provisional", "criterion_complete")
    shown = {key: summary[key] for key in brief}
    shown["n_infra_fail"] = len(summary["infra_fail"])
    shown["criterion_pass"] = summary["criterion"]["pass"]
    print(json.dumps(shown))
    for score in summary["scores"]:
        print(score)


if __name__ == "__main__":
    main()
