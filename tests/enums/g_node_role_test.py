"""
Tests for enum g.node.role.001 from the GridWorks Type Registry.
"""

from gwbase.enums import GNodeRole


def test_g_node_role() -> None:
    assert set(GNodeRole.values()) == {
        "GNode",
        "TerminalAsset",
        "AtomicTNode",
        "MarketMaker",
        "AtomicMeteringNode",
        "ConductorTopologyNode",
        "InterconnectionComponent",
        "World",
        "TimeCoordinator",
        "Supervisor",
        "Scada",
        "PriceService",
        "WeatherService",
        "AggregatedTNode",
        "Persister",
    }

    assert GNodeRole.default() == GNodeRole.GNode
    assert GNodeRole.enum_name() == "g.node.role"
    assert GNodeRole.enum_version() == "001"
