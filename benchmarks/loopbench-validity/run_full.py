"""Parallel acceptance runner for the FIXED benchmark: 10 loops x 3 runs, concurrently, real model.

  python run_full.py --confirm-acceptance            # the 30-run acceptance test (not run yet)
  python run_full.py --loops good-1-fast --runs 1    # a subset (smoke)
  python run_full.py --probe 10                      # concurrency probe: N parallel single calls

Loops and CRITERION.md are read as-is (frozen at 49809bc). MockLLM is made to raise.
Each run writes results/full/<loop>-r<k>.json with model, llm_class, mock_constructed, wall clock.
"""
import argparse, json, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import loopgym as lg
import loopgym.envs.sim as sim
import loopgym.runtime.loop_runtime as rt

here = Path(__file__).parent
sys.path.insert(0, str(here))
from cursor_llm import CursorAgentLLM  # noqa: E402

MOCK_HITS = []
class _NoMock:
    def __init__(self, *a, **k):
        MOCK_HITS.append(time.time()); raise RuntimeError("MockLLM was constructed - run void")
rt.MockLLM = sim.MockLLM = _NoMock


def one_run(loop: str, k: int, model: str, task: str, outdir: Path) -> dict:
    llm = CursorAgentLLM(model=model)
    env = lg.make("loopbench/code-repair-v1", spec_path=str(here / "loops" / f"{loop}.yaml"),
                  backend="live", llm=llm)
    t0 = time.monotonic(); err = None; res = {}
    try:
        res = env.run_episode(task_id=task, seed=k)
    except Exception as e:  # recorded, never retried silently
        err = f"{type(e).__name__}: {e}"; traceback.print_exc()
    out = {"loop": loop, "run": k, "task": task, "model": model, "llm_class": type(llm).__name__,
           "mock_constructed": bool(MOCK_HITS), "wall_seconds": round(time.monotonic() - t0, 1),
           "error": err, "score": res.get("quality_score"), "success": res.get("success"),
           "result": res, "calls": llm.calls,
           "finished_at": datetime.now(timezone.utc).isoformat()}
    (outdir / f"{loop}-r{k}.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def probe(n: int, model: str) -> dict:
    from loopgym.evaluators.sandbox_tests import get_fixture
    fx = get_fixture("cr-001")
    prompt = (f"Bug description:\n{fx.bug_description}\n\nModule ({fx.module_name}):\n```python\n{fx.source}```"
              f"\n\nReply with the full corrected module in a single ```python code block.")
    def call(i):
        llm = CursorAgentLLM(model=model); t = time.monotonic()
        try:
            txt = llm.complete(prompt, role="implementer"); e = None
        except Exception as ex:
            txt, e = "", f"{type(ex).__name__}: {ex}"
        return {"i": i, "seconds": round(time.monotonic() - t, 1), "error": e, "chars": len(txt),
                "usage": llm.calls[-1]["usage"] if llm.calls else None}
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=n) as ex:
        calls = sorted((f.result() for f in [ex.submit(call, i) for i in range(n)]), key=lambda c: c["i"])
    return {"n": n, "model": model, "wall_seconds": round(time.monotonic() - t0, 1),
            "errors": [c for c in calls if c["error"]], "calls": calls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-5.3-codex-low-fast")
    ap.add_argument("--task", default="LB-CR-1")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--loops", nargs="*")
    ap.add_argument("--probe", type=int)
    ap.add_argument("--confirm-acceptance", action="store_true")
    a = ap.parse_args()
    (here / "results").mkdir(exist_ok=True)
    if a.probe:
        r = probe(a.probe, a.model)
        (here / "results" / f"probe-{a.probe}.json").write_text(json.dumps(r, indent=2))
        print(json.dumps({k: r[k] for k in ("n", "model", "wall_seconds")} | {"errors": len(r["errors"])}))
        return
    loops = a.loops or sorted(p.stem for p in (here / "loops").glob("*.yaml"))
    if not a.loops and a.runs == 3 and not a.confirm_acceptance:
        sys.exit("Full 30-run acceptance needs --confirm-acceptance")
    outdir = here / "results" / "full"; outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(l, k) for k in range(a.runs) for l in loops]
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        rows = [f.result() for f in as_completed([ex.submit(one_run, l, k, a.model, a.task, outdir) for l, k in jobs])]
    wall = round(time.monotonic() - t0, 1)
    summary = {"model": a.model, "task": a.task, "jobs": len(jobs), "wall_seconds": wall,
               "mock_constructed": bool(MOCK_HITS), "errors": [r for r in rows if r["error"]],
               "scores": sorted([(r["loop"], r["run"], r["score"]) for r in rows])}
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({k: summary[k] for k in ("model", "jobs", "wall_seconds", "mock_constructed")}))
    for s in summary["scores"]: print(s)


if __name__ == "__main__":
    main()
