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
