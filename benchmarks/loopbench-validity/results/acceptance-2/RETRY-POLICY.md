# Retry policy

Infra-only retries inside `CursorAgentLLM.complete`. This policy applies to acceptance attempt 2 from its start. Committed before the first call of attempt 2. Attempt 1 is unchanged.

## Rule

Retry only when the call produced no result:

- timeout (`subprocess.TimeoutExpired`, outcome `timeout`)
- no output (outcome `no_output`)
- unparsable output (outcome `bad_json`)
- connection lost / process error, including JSON with `is_error` true and a non-zero exit with no JSON (outcome `process_error`)

Never retry on score or patch content. Model replies with content are never retried.

Fixed max 2 retries (3 attempts) per call. `INFRA_RETRIES` defaults to 2 (`CURSOR_LLM_INFRA_RETRIES`). 150 s timeout per attempt (`run_full.py --timeout 150`). Each attempt uses a fresh per-call temp home.

After the last failed attempt, `complete` raises `InfraError` chained from the last error.

## Logging

Every attempt is logged. Each `calls` entry includes `attempts`: `{"n": 1, "seconds": ..., "outcome": "ok" | "timeout" | "no_output" | "bad_json" | "process_error"}`, one object per attempt. The shim also keeps `self.infra_failures`, incremented once per infra failure.

An episode seed with no result after the last retry is recorded `INFRA-FAIL` (not 0, not dropped) and reported separately in `summary.json` (`infra_fail`, distinct from `errors`).

## Why

Acceptance attempt 1 was aborted: `cursor-agent` calls hit the 180 s timeout, and Cursor logged "Connection lost".
