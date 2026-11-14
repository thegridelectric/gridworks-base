#!/bin/bash
# Start a local dev rabbit broker (x86 architecture; otherwise use arm.sh).
# Refreshes the GHCR :latest when the registry answers and starts from the
# cached image when it does not. The running broker is replaced only once
# an image is known to be on disk. rm -fv: fresh data dir each run.
set -euo pipefail

cp for_docker/x86.yml x86.yml
trap 'rm -f x86.yml' EXIT

if ! docker compose -f x86.yml pull; then
  image=$(docker compose -f x86.yml config --images)
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "ERROR: pull failed and $image is not cached; the running broker is untouched." >&2
    exit 1
  fi
  echo "Pull failed; starting from the cached $image." >&2
fi

docker rm -fv gw-dev-rabbit 2>/dev/null || true
docker compose -f x86.yml up -d --pull never
