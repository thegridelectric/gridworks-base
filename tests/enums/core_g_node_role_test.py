"""
Tests for enum core.g.node.role.001 from the GridWorks Type Registry.
"""

from gwbase.enums import CoreGNodeRole


def test_core_g_node_role() -> None:
    assert set(CoreGNodeRole.values()) == {
        "Other",
        "TerminalAsset",
        "AtomicTNode",
        "MarketMaker",
        "AtomicMeteringNode",
        "ConductorTopologyNode",
        "InterconnectionComponent",
        "Scada",
    }

    assert CoreGNodeRole.default() == CoreGNodeRole.Other
    assert CoreGNodeRole.enum_name() == "core.g.node.role"
    assert CoreGNodeRole.enum_version() == "001"
