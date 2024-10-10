"""
Tests for enum gni.status.000 from the GridWorks Type Registry.
"""

from gwbase.enums import GniStatus


def test_gni_status() -> None:
    assert set(GniStatus.values()) == {
        "Unknown",
        "Pending",
        "Active",
        "Done",
    }

    assert GniStatus.default() == GniStatus.Unknown
    assert GniStatus.enum_name() == "gni.status"
    assert GniStatus.enum_version() == "000"
