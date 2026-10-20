#!/usr/bin/env bash
# Offline cold-start demo. No model calls.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORIG="$(pwd)"
cd "$ROOT"

if [[ -n "${DEMO_VENV:-}" ]]; then
  if [[ "$DEMO_VENV" = /* ]]; then
    VENV="$DEMO_VENV"
  else
    VENV="$ORIG/$DEMO_VENV"
  fi
else
  VENV="$ROOT/.venv-demo"
fi

START="$(date +%s.%N)"

python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# Declared deps: loopgym (PyYAML), loopbench (PyYAML, jsonschema),
# loopotel (jsonschema). pytest is not a library dependency; the sandbox
# evaluator shells out to `python -m pytest` for hidden tests.
python -m pip install --disable-pip-version-check -e "$ROOT/packages/loopgym" \
  -e "$ROOT/packages/loopbench" \
  -e "$ROOT/packages/loop-observability" \
  "pytest>=8.0"

python demo/demo_steps.py all

END="$(date +%s.%N)"
awk -v s="$START" -v e="$END" 'BEGIN { printf "Total elapsed seconds: %.2f\n", e - s }'
