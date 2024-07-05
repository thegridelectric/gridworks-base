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

    assert CoreGNodeRole.version("Other") == "000"
    assert CoreGNodeRole.version("TerminalAsset") == "000"
    assert CoreGNodeRole.version("AtomicTNode") == "000"
    assert CoreGNodeRole.version("MarketMaker") == "000"
    assert CoreGNodeRole.version("AtomicMeteringNode") == "000"
    assert CoreGNodeRole.version("ConductorTopologyNode") == "001"
    assert CoreGNodeRole.version("InterconnectionComponent") == "001"
    assert CoreGNodeRole.version("Scada") == "001"

    for value in CoreGNodeRole.values():
        symbol = CoreGNodeRole.value_to_symbol(value)
        assert CoreGNodeRole.symbol_to_value(symbol) == value
