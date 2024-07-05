"""
Tests for enum strategy.name.001 from the GridWorks Type Registry.
"""

from gwbase.enums import StrategyName


def test_strategy_name() -> None:
    assert set(StrategyName.values()) == {
        "NoActor",
        "WorldA",
        "SupervisorA",
        "AtnHeatPumpWithBoostStore",
        "TcGlobalA",
        "MarketMakerA",
        "AtnBrickStorageHeater",
    }

    assert StrategyName.default() == StrategyName.NoActor
    assert StrategyName.enum_name() == "strategy.name"
    assert StrategyName.enum_version() == "001"

    assert StrategyName.version("NoActor") == "000"
    assert StrategyName.version("WorldA") == "000"
    assert StrategyName.version("SupervisorA") == "000"
    assert StrategyName.version("AtnHeatPumpWithBoostStore") == "000"
    assert StrategyName.version("TcGlobalA") == "000"
    assert StrategyName.version("MarketMakerA") == "000"
    assert StrategyName.version("AtnBrickStorageHeater") == "001"

    for value in StrategyName.values():
        symbol = StrategyName.value_to_symbol(value)
        assert StrategyName.symbol_to_value(symbol) == value
