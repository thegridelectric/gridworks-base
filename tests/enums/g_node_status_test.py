"""
Tests for enum g.node.status.100 from the GridWorks Type Registry.
"""

from gwbase.enums import GNodeStatus


def test_g_node_status() -> None:
    assert set(GNodeStatus.values()) == {
        "Unknown",
        "Pending",
        "Active",
        "PermanentlyDeactivated",
        "Suspended",
    }

    assert GNodeStatus.default() == GNodeStatus.Unknown
    assert GNodeStatus.enum_name() == "g.node.status"
    assert GNodeStatus.enum_version() == "100"

    assert GNodeStatus.version("Unknown") == "100"
    assert GNodeStatus.version("Pending") == "100"
    assert GNodeStatus.version("Active") == "100"
    assert GNodeStatus.version("PermanentlyDeactivated") == "100"
    assert GNodeStatus.version("Suspended") == "100"

    for value in GNodeStatus.values():
        symbol = GNodeStatus.value_to_symbol(value)
        assert GNodeStatus.symbol_to_value(symbol) == value
