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

    assert GniStatus.version("Unknown") == "000"
    assert GniStatus.version("Pending") == "000"
    assert GniStatus.version("Active") == "000"
    assert GniStatus.version("Done") == "000"

    for value in GniStatus.values():
        symbol = GniStatus.value_to_symbol(value)
        assert GniStatus.symbol_to_value(symbol) == value
