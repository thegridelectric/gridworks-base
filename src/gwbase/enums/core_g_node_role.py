from enum import auto
from typing import List

from gw.enums import GwStrEnum


class CoreGNodeRole(GwStrEnum):
    """
    CoreGNodeRole assigned by GNodeFactory
    Values:
      - Other
      - TerminalAsset
      - AtomicTNode
      - MarketMaker
      - AtomicMeteringNode
      - ConductorTopologyNode
      - InterconnectionComponent
      - Scada

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#coregnoderole)
      - [More Info](https://gridworks.readthedocs.io/en/latest/core-g-node-role.html)
    """

    Other = auto()
    TerminalAsset = auto()
    AtomicTNode = auto()
    MarketMaker = auto()
    AtomicMeteringNode = auto()
    ConductorTopologyNode = auto()
    InterconnectionComponent = auto()
    Scada = auto()

    @classmethod
    def default(cls) -> "CoreGNodeRole":
        return cls.Other

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "core.g.node.role"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
