#!/bin/bash
# Run locally everything CI runs, so a push won't go red. Mirrors
# .github/workflows/tests.yml (lint + tests) plus the broker-image drift gate
# (.github/workflows/broker-image.yml). Usage: ./ci.sh
set -euo pipefail

step() { printf '\n=== %s ===\n' "$1"; shift; "$@"; }

# Resolve the env exactly as CI does.
step "uv sync (locked)" uv sync --all-groups --locked

# lint job
step "ruff check" uv run ruff check --no-fix .   # fail on lint errors; don't auto-fix in CI (config has fix=true)
step "ruff format --check" uv run ruff format --check .

# broker-image gate: committed definitions JSON must match gwbase.topology.
step "rabbit definitions drift" uv run python for_docker/gen_definitions.py --check

# tests job needs a running 4.x dev broker. CI uses a service container; locally
# that's ./arm.sh (or ./x86.sh) — the same baked image.
if ! nc -z localhost 5672 2>/dev/null; then
  echo "ERROR: no broker on localhost:5672 — start one with ./arm.sh (or ./x86.sh)." >&2
  exit 1
fi
step "tests (coverage)" uv run coverage run --parallel -m pytest
uv run coverage combine
uv run coverage report

printf '\nAll CI checks passed.\n'
