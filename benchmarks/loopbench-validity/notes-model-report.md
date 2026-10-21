# Does cursor-agent 2026.10.19-6bbf2c4 report the model? (21 Oct 2026, ~22:50 IST)

Evidence in `evidence/model-report-2026.10.19-6bbf2c4/` (raw stdout/stderr kept). Runs were outside bwrap in an empty temp dir, prompt "Say hi.", `--model grok-4.7-high`.

| Source | Model field? | Value |
|---|---|---|
| `--output-format json` (what cursor_llm.py uses) | **No.** Keys: type, subtype, is_error, duration_ms, duration_api_ms, result, session_id, request_id, usage | - |
| `--output-format stream-json`, `system/init` event | Yes, `model` | `"Grok 4.7 256K High"` (display name, not the slug) |
| `--output-format stream-json`, `result` event | No (same keys as json) | - |
| `cursor-agent about` | Yes, "Model" line | `Grok 4.7 256K High` (account default/selected model) |
| `--list-models` | slug -> display name | `grok-4.7-high - Grok 4.7  High` |
| bogus `--model not-a-real-model` | exits 1 before any request: "Cannot use this model: ..." | - |
| `--help` | no flag that adds model info to json output | - |

Findings:
1. With `--output-format json` the CLI never reports the model, so `model_reported` is always None in our records. `_model_reported()` looks for `model`/`modelInfo` keys that this version does not emit.
2. stream-json's `system/init.model` is a client-side echo of the selected model as a display name ("Grok 4.7 256K High"); it does not exactly match the `--list-models` display name ("Grok 4.7  High") and is emitted before any server response, so it is not server-side proof of which model answered.
3. The CLI rejects unknown model slugs before any call (exit 1), so the requested slug is at least validated client-side.

Options for QA bot: (a) accept known limit: model_requested pinned + launch identity + slug validation, model_reported unavailable; (b) switch cursor_llm to stream-json and record `system/init.model` as `model_announced` (client echo, not verification) - a larger frozen-code change needing its own tests and re-freeze.
(about.txt: email line redacted in this copy; raw in /workspace/f5-model-evidence/)
