from enum import auto
from typing import List

from gw.enums import GwStrEnum


class GNodeClass(GwStrEnum):

    Unknown = auto()
    TerminalAsset = auto()
    AtomicTNode = auto()
    ConnectivityNode = auto()
    LeafTransactiveNode = auto()
    MarketMaker = auto()
    Scada = auto()
    PriceForecastService = auto()
    WeatherForecastService = auto()
    TimeCoordinator = auto()

    @classmethod
    def default(cls) -> "GNodeClass":
        return cls.GNode

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gw.g.node.class"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
