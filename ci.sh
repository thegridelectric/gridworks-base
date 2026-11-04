#!/usr/bin/env bash
#
# The gate for this repo: the GitHub workflow runs this script and nothing
# else, so a local pass is a CI pass. Run it before committing.
#
# The tests need the dev broker on localhost:5672 (./arm.sh or ./x86.sh;
# CI runs the same baked image as a service container).
#
# Usage: ./ci.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

step() { printf '\n=== %s ===\n' "$1"; shift; "$@"; }

step "uv sync (locked)" uv sync --all-groups --locked

# --no-fix: fail on lint errors, don't auto-fix (config has fix=true).
# --no-cache: a stale .ruff_cache verdict can replay "clean" for bytes a
# cache-less run rejects; this script predicts CI, so it must not answer
# from cache.
step "ruff check" uv run ruff check --no-fix --no-cache .
step "ruff format --check" uv run ruff format --check --no-cache .
step "pyright" uv run pyright

# The committed broker definitions must match gwbase.topology.
step "rabbit definitions drift" uv run python for_docker/gen_definitions.py --check

if ! nc -z localhost 5672 2>/dev/null; then
  echo "ERROR: no broker on localhost:5672 — start one with ./arm.sh (or ./x86.sh)." >&2
  exit 1
fi
step "tests (coverage)" uv run coverage run --parallel -m pytest
uv run coverage combine
uv run coverage report
uv run coverage xml

printf '\nAll checks passed.\n'
