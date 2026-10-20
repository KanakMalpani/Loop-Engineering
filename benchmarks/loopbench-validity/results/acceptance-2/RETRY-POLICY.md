# Retry policy

Infra-only retries inside `CursorAgentLLM.complete`. This policy applies to acceptance attempt 2 from its start. Attempt 1 is unchanged.

## Rule

An attempt is an infra failure only when it:

- raises `subprocess.TimeoutExpired`, or
- returns empty stdout (`no_output`), or
- returns stdout whose last line is not valid JSON (`bad_json`).

On an infra failure the call is retried up to `INFRA_RETRIES` more times. `INFRA_RETRIES = int(os.environ.get("CURSOR_LLM_INFRA_RETRIES", "2"))`, so the default is 2 retries and 3 attempts. Each attempt uses a fresh per-call temp home. Each attempt's timeout is `self.timeout`. Attempt 2 passes that as `run_full.py --timeout 150`, so 150 s per attempt.

Model replies of any content are not retried. JSON with `is_error` true is not an infra failure and is not retried; it still raises `RuntimeError` as before. That exception is the seed error. Infra attempts already made on that call stay in the `calls` entry; `is_error` is not an `attempts` outcome.

After the last infra failure, the last error is re-raised.

## Logging

Every attempt is logged in the run files. Each `calls` entry includes `attempts`: `{"n": 1, "seconds": ..., "outcome": "ok" | "timeout" | "no_output" | "bad_json"}`, one object per attempt. The shim also keeps `self.infra_failures`, incremented once per infra failure.

If every attempt fails, that `calls` entry is still written, the error is re-raised, and the seed is recorded as an error scoring 0. Nothing is dropped.

## Why

Acceptance attempt 1 was aborted: `cursor-agent` calls hit the 180 s timeout, and Cursor logged "Connection lost".
