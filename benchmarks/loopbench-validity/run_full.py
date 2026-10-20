"""Parallel acceptance runner for the FIXED benchmark: 10 loops x 3 runs, concurrently, real model.

  python run_full.py --confirm-acceptance            # the 30-run acceptance test (not run yet)
  python run_full.py --loops good-1-fast --runs 1    # a subset (smoke)
  python run_full.py --probe 10                      # concurrency probe: N parallel single calls

Each run calls run_episode once per --seeds value (default 0,1,2,3,4), sequentially.
Loops and CRITERION.md are read as-is (frozen at 49809bc). MockLLM is made to raise.
The scored result is provisional; see DEVIATION.md.
Each run writes <outdir>/<loop>-r<k>.json as soon as it finishes, plus <outdir>/progress.json.
"""
import argparse
import json
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import loopgym as lg
import loopgym.runtime.loop_runtime as rt
from loopgym.envs import sim

here = Path(__file__).parent
sys.path.insert(0, str(here))
import cursor_llm
from cursor_llm import CursorAgentLLM

MOCK_HITS = []
class _NoMock:
    def __init__(self, *a, **k):
        MOCK_HITS.append(time.time()); raise RuntimeError("MockLLM was constructed - run void")
rt.MockLLM = sim.MockLLM = _NoMock

_progress_lock = threading.Lock()
_progress = {"completed": 0, "total": 0}
BAD3 = "bad-3-wrong-role"


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


def _seed_result(res: dict, err: str | None) -> tuple[dict, float]:
    """Per-seed record. An errored seed contributes 0.0 to the run mean."""
    if err:
        return {
            "score": 0.0,
            "success": None,
            "termination_reason": None,
            "instance_scores": {},
            "error": err,
        }, 0.0
    raw = res.get("quality_score")
    score = 0.0 if raw is None else float(raw)
    return {
        "score": score,
        "success": res.get("success"),
        "termination_reason": res.get("termination_reason"),
        "instance_scores": _instance_scores(res),
        "error": None,
    }, score


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
    """One independent run: every seed, sequentially, no retries. File written on finish."""
    t0 = time.monotonic()
    llm = None
    by_seed: dict[str, dict] = {}
    errors: list[dict] = []
    contributions: list[float] = []
    try:
        llm = CursorAgentLLM(model=model, timeout=timeout)
        env = lg.make("loopbench/code-repair-v1", spec_path=str(here / "loops" / f"{loop}.yaml"),
                      backend="live", llm=llm)
        for s in seeds:
            err = None
            res: dict = {}
            try:
                res = env.run_episode(task_id=task, seed=s)
            except Exception as e:  # noqa: BLE001  # record and continue; never retried
                err = f"{type(e).__name__}: {e}"
                traceback.print_exc()
            record, contribution = _seed_result(res, err)
            by_seed[str(s)] = record
            contributions.append(contribution)
            if err:
                errors.append({"seed": s, "error": err})
    except Exception as e:  # noqa: BLE001  # setup failure: record every seed not yet run
        err = f"{type(e).__name__}: {e}"
        traceback.print_exc()
        for s in seeds:
            if str(s) in by_seed:
                continue
            record, contribution = _seed_result({}, err)
            by_seed[str(s)] = record
            contributions.append(contribution)
            errors.append({"seed": s, "error": err})
    out = {
        "loop": loop,
        "run": k,
        "task": task,
        "seeds": list(seeds),
        "model": model,
        "llm_class": type(llm).__name__ if llm is not None else None,
        "mock_constructed": bool(MOCK_HITS),
        "wall_seconds": round(time.monotonic() - t0, 1),
        "score": (sum(contributions) / len(seeds)) if seeds else 0.0,
        "errors": errors,
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


def _grouped(rows: list[dict], k: int, prefix: str) -> dict[str, float]:
    grouped = {
        r["loop"]: r["score"]
        for r in rows
        if r["run"] == k and r["loop"].startswith(prefix)
    }
    return dict(sorted(grouped.items()))


def criterion_block(rows: list[dict], n_runs: int) -> dict:
    """CRITERION.md: each run passes only when min(GOOD) > max(BAD). A tie is a FAIL."""
    runs = []
    for k in range(n_runs):
        good = _grouped(rows, k, "good-")
        bad = _grouped(rows, k, "bad-")
        min_good = min(good.values()) if good else None
        max_bad = max(bad.values()) if bad else None
        if min_good is None or max_bad is None:
            tie, passed = None, False
        else:
            tie = min_good == max_bad
            passed = min_good > max_bad
        runs.append({
            "run": k,
            "good": good,
            "bad": bad,
            "min_good": min_good,
            "max_bad": max_bad,
            "tie": tie,
            "pass": passed,
        })
    return {"pass": bool(runs) and all(item["pass"] for item in runs), "runs": runs}


def bad3_vs_good(rows: list[dict], n_runs: int) -> list[dict]:
    """Per run, bad-3-wrong-role against each good loop: tie, or bad-3 strictly beats it."""
    report = []
    for k in range(n_runs):
        bad_rows = [r for r in rows if r["run"] == k and r["loop"] == BAD3]
        bad_score = bad_rows[0]["score"] if bad_rows else None
        versus = []
        goods = sorted(
            (r for r in rows if r["run"] == k and str(r["loop"]).startswith("good-")),
            key=lambda r: r["loop"],
        )
        for good in goods:
            good_score = good["score"]
            if bad_score is None or good_score is None:
                ties, beats = None, None
            else:
                ties = bad_score == good_score
                beats = bad_score > good_score
            versus.append({
                "loop": good["loop"],
                "score": good_score,
                "ties": ties,
                "beats": beats,
            })
        report.append({"run": k, BAD3: bad_score, "versus": versus})
    return report


def per_loop_scores(rows: list[dict], n_runs: int) -> dict[str, list]:
    by_key = {(r["loop"], r["run"]): r["score"] for r in rows}
    loops = sorted({r["loop"] for r in rows})
    return {loop: [by_key.get((loop, k)) for k in range(n_runs)] for loop in loops}


def probe(n: int, model: str, timeout: int, cap: int) -> dict:
    from loopgym.evaluators.sandbox_tests import get_fixture
    fx = get_fixture("cr-001")
    prompt = (f"Bug description:\n{fx.bug_description}\n\nModule ({fx.module_name}):\n```python\n{fx.source}```"
              f"\n\nReply with the full corrected module in a single ```python code block.")
    def call(i):
        llm = CursorAgentLLM(model=model, timeout=timeout); t = time.monotonic()
        try:
            txt = llm.complete(prompt, role="implementer"); e = None
        except Exception as ex:  # noqa: BLE001  # probe records call errors deliberately
            txt, e = "", f"{type(ex).__name__}: {ex}"
        return {"i": i, "seconds": round(time.monotonic() - t, 1), "error": e, "chars": len(txt),
                "usage": llm.calls[-1]["usage"] if llm.calls else None}
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
    (here / "results").mkdir(exist_ok=True)
    if a.probe:
        r = probe(a.probe, a.model, a.timeout, a.max_concurrency)
        (here / "results" / f"probe-{a.probe}.json").write_text(json.dumps(r, indent=2))
        print(json.dumps({k: r[k] for k in ("n", "max_concurrency", "model", "wall_seconds")} | {"errors": len(r["errors"])}))
        return
    seeds = a.seeds
    loops = a.loops or sorted(p.stem for p in (here / "loops").glob("*.yaml"))
    if not a.loops and a.runs == 3 and not a.confirm_acceptance:
        sys.exit("Full 30-run acceptance needs --confirm-acceptance")
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
    any_error = any(r["errors"] for r in rows)
    summary = {
        "model": a.model,
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
        "deviation": "see DEVIATION.md",
        "criterion_complete": not any_error,
        "errors": [
            {"loop": r["loop"], "run": r["run"], "errors": r["errors"]}
            for r in rows if r["errors"]
        ],
        "scores": sorted((r["loop"], r["run"], r["score"]) for r in rows),
        "per_loop": per_loop_scores(rows, a.runs),
        "criterion": criterion_block(rows, a.runs),
        "bad3_vs_good": bad3_vs_good(rows, a.runs),
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    brief = ("model", "jobs", "wall_seconds", "mock_constructed", "provisional", "criterion_complete")
    shown = {key: summary[key] for key in brief}
    shown["criterion_pass"] = summary["criterion"]["pass"]
    print(json.dumps(shown))
    for score in summary["scores"]:
        print(score)


if __name__ == "__main__":
    main()
