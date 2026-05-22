# Gridworks Base

[![PyPI](https://img.shields.io/pypi/v/gridworks-base.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/gridworks-base.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/gridworks-base)][python version]
[![License](https://img.shields.io/pypi/l/gridworks-base)][license]

[![Read the documentation at https://gridworks-base.readthedocs.io/](https://img.shields.io/readthedocs/gridworks-base/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/thegridelectric/gridworks-base/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/thegridelectric/gridworks-base/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/gridworks-base/
[status]: https://pypi.org/project/gridworks-base/
[python version]: https://pypi.org/project/gridworks-base
[read the docs]: https://gridworks-base.readthedocs.io/
[tests]: https://github.com/thegridelectric/gridworks-base/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/thegridelectric/gridworks-base
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

This repository serves two purposes:

1. it provides the base class for the default GridWorks actor using pika, the main python package for interacting with RabbitMQ

   - install the `gwbase` package via

   ```
   $ pip install gridworks-base
   ```

2. It provides scripts for runnig a local dev rabbit broker, which is the recommended way to develop.

## Dev Rabbit Broker

All GridWorks repos require a running rabbitMQ dev broker running to pass tests or run dev simulations. Instructions for setting it up:

- Make sure you have [docker](https://www.docker.com/products/docker-desktop/) installed
- Start the dev broker in a docker container — `./arm.sh` or `./x86.sh`
  (**identical now**: both pull the same multi-arch image
  `ghcr.io/thegridelectric/dev-rabbit`, arm64 + amd64; Docker selects your
  architecture automatically). The image bakes the generated broker
  definitions, so no extra setup is needed to get the right exchanges.

Note those scripts are just aliases so one doesn't need to remember the docker incantation. Also, if you have an older version of docker, you may need to use `docker-compose` instead of `docker compose`. That should also work.

Tests for success:

1. go to http://0.0.0.0:15672/ - it should look like this:

![alt_text](docs/images/dev-broker-login.png) - Username/password for the dev rabbit broker: `smqPublic/smqPublic` - [More info]](https://gridworks.readthedocs.io/en/latest/gridworks-broker.html) on the GridWorks use of rabbit brokers

2. Test mqtt access via mqtt_sub:

```
mosquitto_sub -h localhost -p 1885 -u smqPublic -P smqPublic -t "#" -v
```

and go to `http://0.0.0.0:15672/queues` to confirm a new queue has showed up

```
docker exec -it gw-dev-rabbit rabbitmq-plugins list
```

And confirm `rabbitmq_mqtt` and `rabbitmq_management` appear as enabled
(`[E*]`).



3. Confirm the **baked broker definitions** loaded — the exchanges and the
   `smqPublic` user come from inside the image (generated from
   `gwbase.topology`):

```
# exchanges live in the d1__1 vhost (not the default "/"):
docker exec gw-dev-rabbit rabbitmqctl list_exchanges -p d1__1 | grep -E 'ltn_tx|super_tx|ear_tx'
docker exec gw-dev-rabbit rabbitmqctl list_users   # expect smqPublic
```

4. tests pass

```
uv sync --all-groups
uv run pytest -v
```

This repository uses [uv](https://docs.astral.sh/uv/) for package and
environment management (`pyproject.toml` + `uv.lock`). Common tasks:

```
uv run pytest          # tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run mypy src        # type-check
```

`nox` sessions (`nox -s tests|lint|mypy|xdoctest|docs-build`) are an
optional convenience wrapper over the same `uv run` commands; install nox
globally (e.g. `uv tool install nox`) to use them. CI runs the `uv run`
commands directly.

## Building & publishing the dev-broker image (GHCR)

`arm.sh` / `x86.sh` pull a prebuilt multi-arch image,
`ghcr.io/thegridelectric/dev-rabbit`, that bakes the generated broker
definitions onto official RabbitMQ (`rabbit/Dockerfile`). The definitions
are generated from `gwbase.topology` (single source of truth; a drift guard
keeps the committed `rabbit/rabbitconfig/*_definitions.json` in sync). You
only rebuild/push the image when the definitions, conf, or plugins change.

**Automatic (CI):** `.github/workflows/broker-image.yml` builds and pushes
the image on a push to `main`/`dev` that touches the baked inputs, gated by
the definitions drift check (`gen_definitions.py --check`). Usually you do
not push by hand.

**Manual (seed / local):**

```bash
# one-time: a buildx builder that can do multi-arch. The default "docker"
# driver CANNOT — it errors "Multi-platform build is not supported for the
# docker driver". Create a docker-container builder instead:
docker buildx create --name gw --driver docker-container --use
docker buildx inspect --bootstrap

# one-time: log in to GHCR with a GitHub PAT (classic) that has
# write:packages (your account needs write access to the thegridelectric org):
echo "$GHCR_PAT" | docker login ghcr.io -u <github-username> --password-stdin

# build + push (run on a clean tree so the tag is chaos__<short-sha>__<date>,
# not chaos__dev):
./rabbit/build-and-push.sh
```

After the **first** push the package is **private** — set it **Public**
(GitHub → `thegridelectric` → Packages → `dev-rabbit` → Package settings →
Change visibility) so any machine can `docker pull` without auth. Then
verify both arches are published:

```bash
docker buildx imagetools inspect ghcr.io/thegridelectric/dev-rabbit:latest
# expect: linux/amd64 and linux/arm64/v8
```

For a quick local-only test without pushing, build just your host arch:
`docker build -f rabbit/Dockerfile -t dev-rabbit-local .`

## Hello Rabbit

Quick start for seeing how the actor base can send a message on the rabbit broker. Run hello_rabbit.py (after starting up the dev rabbit broker, see [dev broker](dev-rabbit-broker) above) and look at the `src/gwbase/actor_base.py` code.

TODO: explain more about what this code does. Links to the type registroy, code generation.
TODO: create a second hello script with two actors sending heartbeats back and forth.

Distributed under the terms of the [MIT license][license],
_Gridworks Base_ is free and open source software.

<!-- github-only -->

[license]: https://github.com/thegridelectric/gridworks-base/blob/main/LICENSE
[contributor guide]: https://github.com/thegridelectric/gridworks-base/blob/main/CONTRIBUTING.md
[command-line reference]: https://gridworks-base.readthedocs.io/en/latest/usage.html
