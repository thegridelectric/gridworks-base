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
