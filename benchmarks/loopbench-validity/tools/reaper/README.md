# Tag-based cursor-agent reaper (prototype, under test)

These tools are not wired into `run_full.py` or `cursor_llm.py`, which are unchanged. To use them, point `CURSOR_AGENT_BIN` at the reaper (`~/.local/bin/cursor-agent-reap` on the box; this directory holds the same files).

- `cursor-agent-reap` tags one call with a unique `CURSOR_REAP_TAG`. A detached watcher that carries no tag kills only processes whose environ holds that exact tag, once the call ends. That includes calls ended by SIGKILL of the call's process group.
  - It logs `START`, every `KILL` (pid, tag, call id, cmd) and `DONE` to `$CURSOR_REAP_LOG`.
  - It changes no sandbox argument.
- `cursor-agent-errlog` saves each call's stderr and exit code to `$CURSOR_LLM_SANDBOX/stderr/`.
- `snap.sh` and `verify.py` do the per-trial check that every killed PID carried one of our tags and that the untagged decoy survived.
- Evidence: `/workspace/concurrency-investigation/03-reaper.md` on the box.
