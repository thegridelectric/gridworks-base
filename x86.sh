#!/bin/bash
# Start a local dev rabbit broker (x86 architecture; otherwise use arm.sh).
# rm -fv: fresh data dir each run. --pull always: refresh the GHCR :latest.
docker rm -fv gw-dev-rabbit 2>/dev/null || true
cp for_docker/x86.yml x86.yml
docker compose -f x86.yml up -d --pull always
rm x86.yml
