"""Drift guard: the committed broker-definitions JSON must equal what the
generator produces from `gwbase.topology`. This is the CI guard — it runs as
part of the normal test suite, so a topology change that isn't re-rendered
fails CI.
"""

from pathlib import Path

import pytest

from gwbase.rabbit_definitions import rendered_artifacts

RABBITCONFIG = Path(__file__).resolve().parents[1] / "rabbit" / "rabbitconfig"


@pytest.mark.parametrize("name, expected", list(rendered_artifacts().items()))
def test_committed_definitions_match_generator(name: str, expected: str) -> None:
    path = RABBITCONFIG / name
    assert path.exists(), (
        f"{path} is missing — run "
        f"`python for_docker/gen_definitions.py --write-all`"
    )
    assert path.read_text() == expected, (
        f"{name} is stale vs gwbase.topology. Regenerate: "
        f"`python for_docker/gen_definitions.py --write-all`"
    )
