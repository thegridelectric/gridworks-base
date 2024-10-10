"""
Tests for enum universe.type.000 from the GridWorks Type Registry.
"""

from gwbase.enums import UniverseType


def test_universe_type() -> None:
    assert set(UniverseType.values()) == {
        "Dev",
        "Hybrid",
        "Production",
    }

    assert UniverseType.default() == UniverseType.Dev
    assert UniverseType.enum_name() == "universe.type"
    assert UniverseType.enum_version() == "000"
