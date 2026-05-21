# Self-contained dev broker image for distribution via GHCR, so other repos
# (gridworks-marketmaker, gridworks-scada, ...) can run a dev broker with NO
# gridworks-base checkout. Built + pushed by .github/workflows/broker-image.yml
# from the guard-checked definitions, so the image can't lag the repo.
#
# Build context is the REPO ROOT:
#   docker build -f rabbit/Dockerfile -t ghcr.io/thegridelectric/dev-rabbit .
#
# Official multi-arch RabbitMQ (arm64 + amd64). Dev runs 4.x; the generated
# definitions are version-agnostic.
FROM rabbitmq:4.1-management

COPY for_docker/enabled_plugins /etc/rabbitmq/enabled_plugins
COPY for_docker/dev_rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY rabbit/rabbitconfig/dev_definitions.json /etc/rabbitmq/definitions.json
