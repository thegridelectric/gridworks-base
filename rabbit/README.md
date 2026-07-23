# rabbit/ — the dev-broker image and the canonical definitions

This directory is where the GridWorks dev-broker image and the broker
definitions artifacts live:

- **`Dockerfile`** — bakes `enabled_plugins`, `dev_rabbitmq.conf`, and the
  generated `rabbitconfig/dev_definitions.json` onto the official
  multi-arch `rabbitmq:4.1-management` image.
- **`build-and-push.sh`** — builds and pushes
  `ghcr.io/thegridelectric/dev-rabbit` for arm64 + amd64 in one buildx
  run. Clean tree → tag `chaos__<short-sha>__<date>`; dirty tree → tag
  `chaos__dev` with `-DIRTY` in the `gridworks_docker_id` image label.
  CI does the same via `.github/workflows/broker-image.yml`, gated on the
  definitions drift check.
- **`rabbitconfig/`** — the generated definitions artifacts
  (`dev_definitions.json`, `hybrid_definitions.json`). Never hand-edit;
  they are produced from `gwbase.topology` by
  `for_docker/gen_definitions.py`, and a drift test + pre-commit hook
  keep them in sync.

Running the dev broker (pulls the GHCR image): see the repo README's
*Dev Rabbit Broker* section. Production broker operations live in the
private `gridworks-infra` repo (`rmqbot/`), which runs the official
`rabbitmq:4.x-management` image with the `hybrid_definitions.json`
artifact fetched from this repo's pushed `main`.
