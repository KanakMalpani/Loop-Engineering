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

STAMP="$VENV/.demo-stamp"

_demo_stamp_compute() {
  {
    sha256sum \
      "$ROOT/packages/loop-core/pyproject.toml" \
      "$ROOT/packages/loop-observability/pyproject.toml" \
      "$ROOT/packages/loopbench/pyproject.toml" \
      "$ROOT/packages/loopgym/pyproject.toml" \
      "$ROOT/packages/loopnet/pyproject.toml" \
      "$ROOT/demo/demo.sh"
    python3 --version
  } | sha256sum | awk '{print $1}'
}

_demo_imports_ok() {
  "$VENV/bin/python" -c "import loopgym, loopbench, loopotel, loopnet, pytest, jsonschema, yaml"
}

START="$(date +%s.%N)"

if [[ -x "$VENV/bin/python" ]] \
  && [[ -f "$STAMP" ]] \
  && [[ "$(cat "$STAMP")" == "$(_demo_stamp_compute)" ]] \
  && _demo_imports_ok \
  && [[ -f "$ROOT/packages/loop-core/tools/validate_lss.py" ]]; then
  echo "deps: cached (stamp ok)"
else
  echo "deps: installing"
  python3 -m venv "$VENV"
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"

  # Declared deps: loopgym (PyYAML), loopbench (PyYAML, jsonschema),
  # loopotel (jsonschema), loopnet (jsonschema). pytest is not a library
  # dependency; the sandbox evaluator shells out to `python -m pytest` for
  # hidden tests.
  python -m pip install --disable-pip-version-check -e "$ROOT/packages/loopgym" \
    -e "$ROOT/packages/loopbench" \
    -e "$ROOT/packages/loop-observability" \
    -e "$ROOT/packages/loopnet" \
    "pytest>=8.0"

  _demo_stamp_compute >"$STAMP"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

python demo/demo_steps.py all

END="$(date +%s.%N)"
awk -v s="$START" -v e="$END" 'BEGIN { printf "Total elapsed seconds: %.2f\n", e - s }'
