git checkout -- ODXML SSoT aicapture.json
pushd ../..
# TODO: There are times where we do want to generate docs
git checkout -- docs
poetry run ruff check --fix
poetry run pre-commit run -a
popd
