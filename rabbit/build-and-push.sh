#!/bin/bash
set -euo pipefail
#
# Build + push the multi-arch dev-broker image to GHCR, tagged with the git
# commit for traceability — same convention CI uses
# (.github/workflows/broker-image.yml). Replaces the old per-arch
# build-dev-broker-{arm,x86}.sh: official rabbitmq is multi-arch, so one
# buildx run produces one image for arm64 + amd64.
#
# Prereq: docker login ghcr.io (PAT with write:packages). Run from anywhere
# in the repo. For a quick local-only test (no push), use instead:
#   docker build -f rabbit/Dockerfile -t dev-rabbit-local .

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

IMAGE="ghcr.io/thegridelectric/dev-rabbit"
GIT_COMMIT=$(git rev-parse --short HEAD)
DATE=$(date +'%Y%m%d')

if [[ -n "$(git status --untracked-files=no --porcelain)" ]]; then
  # uncommitted changes in tracked files — don't pin a misleading commit tag
  TAG="chaos__dev"
  DOCKER_ID="${IMAGE}__${GIT_COMMIT}-DIRTY__${DATE}"
else
  TAG="chaos__${GIT_COMMIT}__${DATE}"
  DOCKER_ID="${IMAGE}__${GIT_COMMIT}__${DATE}"
fi

echo "Building ${IMAGE}:${TAG} (+ :latest), gridworks_docker_id=${DOCKER_ID}"

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f rabbit/Dockerfile \
  -t "${IMAGE}:${TAG}" \
  -t "${IMAGE}:latest" \
  --label "gridworks_docker_id=${DOCKER_ID}" \
  --push \
  .
