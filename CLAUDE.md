# gridworks-base — notes for Claude

Operative protocol when working in this repo. The umbrella conventions in
`wiki/GridWorks_CLAUDE.md` still apply; this file only adds repo-specific gotchas.

## Dev environment — use `uv run`, never a hand-activated venv

- Run **every** tool via `uv run …`: `uv run pytest`, `uv run ruff check .`,
  `uv run ruff format .`, `uv run mypy src`. uv resolves the project `.venv`
  from `uv.lock`; do **not** create or activate a venv yourself.
- "Executable not found" or a `VIRTUAL_ENV=… does not match the project
  environment path .venv` warning ⇒ a **stale venv is on PATH** (often from a
  previous repo location). `unset VIRTUAL_ENV` / `deactivate`, then use `uv run`.
- **pre-commit** is repo-based: run plain `pre-commit run` (NOT `uv run
  pre-commit`); it also runs on `git commit` and needs no venv on PATH.

## ruff is pinned in three coupled places — keep them equal

`pyproject.toml` (`ruff==<v>`), `uv.lock`, and `.pre-commit-config.yaml`
(`ruff-pre-commit` `rev: v<v>`). Change one ⇒ change all three, or local,
pre-commit, and CI (which runs `uv sync --locked` + `uv run ruff format
--check .`) will disagree on formatting.

## Broker topology is generated — never hand-edit the definitions

`src/gwbase/topology.py` is the single source of truth for exchanges/bindings
(and the `TransportClass`/`RoutingClass` taxonomy in `transport_encoding.py`).
After changing topology, regenerate the committed artifacts:

```
uv run python for_docker/gen_definitions.py --write-all --dir rabbit/rabbitconfig
```

The `rabbit-definitions-drift` pre-commit hook fails if you forget. To apply new
exchanges to a **running** `gw-dev-rabbit`:
`docker exec gw-dev-rabbit rabbitmqctl import_definitions /path/to/dev_definitions.json`.
