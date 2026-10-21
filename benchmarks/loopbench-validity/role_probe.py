"""Role pickup probe: one cursor-agent call must honor a rules-file role prefix."""

import argparse
import json
import sys
import time
from pathlib import Path

import cursor_llm
from cursor_llm import CursorAgentLLM, InfraError

here = Path(__file__).parent

PROMPT = "Say hello in one short sentence."
ROLE = (
    "Every reply you give must begin with the exact token ROLE-PICKUP-7731 followed by a space."
)
TOKEN = "ROLE-PICKUP-7731"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=cursor_llm.DEFAULT_MODEL)
    ap.add_argument("--timeout", type=int, default=150)
    ap.add_argument("--out", type=Path, default=here / "results" / "role-probe.json")
    a = ap.parse_args()
    cursor_llm.assert_no_unpinned_env()
    identity = cursor_llm.assert_launch_identity()
    cursor_llm.require_pinned_model(a.model)

    out_path = Path(a.out)
    llm = CursorAgentLLM(
        model=a.model,
        timeout=a.timeout,
        log_path=out_path.parent / "role-probe.log",
        run_id="role-probe",
    )
    reply = ""
    error = None
    t0 = time.monotonic()
    try:
        reply = llm.complete(PROMPT, role=ROLE)
    except InfraError as exc:
        error = str(exc)
        reply = ""
    seconds = round(time.monotonic() - t0, 1)
    picked_up = error is None and reply.strip().startswith(TOKEN)

    checked = cursor_llm.calls_model_check(llm.calls)
    last = llm.calls[-1] if llm.calls else {}
    out = {
        "model": a.model,
        "model_requested": last.get("model_requested"),
        "model_reported": last.get("model_reported"),
        "calls": llm.calls,
        "model_check": checked,
        "launch_identity": identity,
        "picked_up": picked_up,
        "reply": reply,
        "seconds": seconds,
        "error": error,
    }
    if not checked["valid"]:
        out["invalid"] = True
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({
        "model": a.model,
        "picked_up": picked_up,
        "seconds": seconds,
        "error": error,
    }))
    if not checked["valid"] or error is not None or not picked_up:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
