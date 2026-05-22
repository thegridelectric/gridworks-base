"""Drift guard: the committed broker-definitions JSON must equal what the
generator produces from `gwbase.topology`. This is the CI guard — it runs as
part of the normal test suite, so a topology change that isn't re-rendered
fails CI.
"""

from pathlib import Path

import pytest

from gwbase.rabbit_definitions import DEFINITION_ARTIFACTS, rendered_artifacts

RABBITCONFIG = Path(__file__).resolve().parents[1] / "rabbit" / "rabbitconfig"


# Parametrize over the filename only, so the test ID is e.g.
# "[dev_definitions.json]" rather than the entire rendered JSON.
@pytest.mark.parametrize("name", [name for name, _ in DEFINITION_ARTIFACTS])
def test_committed_definitions_match_generator(name: str) -> None:
    path = RABBITCONFIG / name
    assert path.exists(), (
        f"{path} is missing — run `python for_docker/gen_definitions.py --write-all`"
    )
    assert path.read_text() == rendered_artifacts()[name], (
        f"{name} is stale vs gwbase.topology. Regenerate: "
        f"`python for_docker/gen_definitions.py --write-all`"
    )
