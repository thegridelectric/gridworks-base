pushd ../..
poetry run ruff check
poetry run pre-commit run -a
popd