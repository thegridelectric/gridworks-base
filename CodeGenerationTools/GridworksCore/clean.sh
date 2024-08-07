pushd ../..
pre-commit run -a trailing-whitespace
ruff check --fix --select I
# ruff check --fix
# ruff format
