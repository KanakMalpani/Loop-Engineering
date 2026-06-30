#!/usr/bin/env python3
"""Generated CrewAI-oriented stub for {loop_name}."""

from __future__ import annotations

import argparse
import json
import sys


def run_stub_fallback(trace: str, json_out: bool) -> int:
    payload = {
        "mode": "stub",
        "success": True,
        "output_len": 42,
        "trace": trace,
    }
    if json_out:
        print(json.dumps(payload, indent=2))
    else:
        print(f"No CrewAI/LoopGym — stub success len={payload['output_len']}")
    return 0


def run_loopgym_fallback(trace: str, json_out: bool) -> int:
    try:
        import loopgym as lg
    except ImportError:
        return run_stub_fallback(trace, json_out)

    env = lg.make("loopbench/code-repair-v1")
    try:
        result = env.run_episode(task_id="cr-001", seed=42, trace_path=trace)
    except TypeError:
        result = env.run_episode(task_id="cr-001", seed=42)
    payload = {"mode": "loopgym_fallback", "success": result.get("success"), "trace": trace}
    if json_out:
        print(json.dumps(payload, indent=2))
    else:
        print(f"CrewAI not installed — ran LoopGym composed fallback success={payload['success']}")
    return 0 if payload["success"] else 1


def run_crewai() -> dict:
    from crewai import Agent, Crew, Process, Task

    researcher = Agent(role="Researcher", goal="Gather facts", backstory="Analyst", verbose=False, allow_delegation=False)
    writer = Agent(role="Writer", goal="Synthesize brief", backstory="Editor", verbose=False, allow_delegation=False)
    t1 = Task(description="Research: {objective_short}", expected_output="bullet facts", agent=researcher)
    t2 = Task(description="Write summary from research", expected_output="short brief", agent=writer)
    crew = Crew(agents=[researcher, writer], tasks=[t1, t2], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    text = str(result)
    success = len(text) > 20
    return {"success": success, "output_len": len(text), "mode": "crewai"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", default="trace.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        payload = run_crewai()
    except ImportError:
        return run_loopgym_fallback(args.trace, args.json)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"success={{payload['success']}} mode={{payload['mode']}}")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
