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

    assert GNodeRole.version("GNode") == "000"
    assert GNodeRole.version("TerminalAsset") == "000"
    assert GNodeRole.version("AtomicTNode") == "000"
    assert GNodeRole.version("MarketMaker") == "000"
    assert GNodeRole.version("AtomicMeteringNode") == "000"
    assert GNodeRole.version("ConductorTopologyNode") == "000"
    assert GNodeRole.version("InterconnectionComponent") == "000"
    assert GNodeRole.version("World") == "000"
    assert GNodeRole.version("TimeCoordinator") == "000"
    assert GNodeRole.version("Supervisor") == "000"
    assert GNodeRole.version("Scada") == "000"
    assert GNodeRole.version("PriceService") == "000"
    assert GNodeRole.version("WeatherService") == "000"
    assert GNodeRole.version("AggregatedTNode") == "000"
    assert GNodeRole.version("Persister") == "001"

    for value in GNodeRole.values():
        symbol = GNodeRole.value_to_symbol(value)
        assert GNodeRole.symbol_to_value(symbol) == value
