#!/bin/bash
# Start a local dev rabbit broker (arm architecture; otherwise use x86.sh).
# rm -fv: fresh data dir each run. --pull always: refresh the GHCR :latest.
docker rm -fv gw-dev-rabbit 2>/dev/null || true
cp for_docker/arm.yml arm.yml
docker compose -f arm.yml up -d --pull always
rm arm.yml
