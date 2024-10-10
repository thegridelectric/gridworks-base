from enum import auto
from typing import List

from gw.enums import GwStrEnum


class GNodeRole(GwStrEnum):
    """
    Categorizes GNodes by their function within GridWorks
    Values:
      - GNode: Default value
      - TerminalAsset: An avatar for a real-word Transactive Device [More Info](https://gridworks.readthedocs.io/en/latest/transactive-device.html).
      - AtomicTNode: Transacts in markets on behalf of, and controlling the power use
        of, a TerminalAsset [More Info](https://gridworks.readthedocs.io/en/latest/atomic-t-node.html).
      - MarketMaker: Runs energy markets at its Node in the GNodeTree [More Info](https://gridworks.readthedocs.io/en/latest/market-maker.html).
      - AtomicMeteringNode: Role of a GNode that will become an AtomicTNode, prior to
        it owning TaTradingRights
      - ConductorTopologyNode: An avatar for a real-world electric grid node - e.g. a
        substation or transformer
      - InterconnectionComponent: An avatar for a cable or wire on the electric grid
      - World: Adminstrative GNode responsible for managing and authorizing instances [More Info](https://gridworks.readthedocs.io/en/latest/world-role.html).
      - TimeCoordinator: Responsible for managing time in simulations
      - Supervisor: Responsible for GNode actors running in a container [More Info](https://gridworks.readthedocs.io/en/latest/supervisor.html).
      - Scada: GNode associated to the device and code that directly monitors and actuates
        a Transactive Device
      - PriceService: Provides price forecasts for markets run by MarketMakers
      - WeatherService: Provides weather forecasts
      - AggregatedTNode: An aggregation of AtomicTNodes
      - Persister: Responsible for acking events with delivery guarantees

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#gnoderole)
      - [More Info](https://gridworks.readthedocs.io/en/latest/g-node-role.html)
    """

    GNode = auto()
    TerminalAsset = auto()
    AtomicTNode = auto()
    MarketMaker = auto()
    AtomicMeteringNode = auto()
    ConductorTopologyNode = auto()
    InterconnectionComponent = auto()
    World = auto()
    TimeCoordinator = auto()
    Supervisor = auto()
    Scada = auto()
    PriceService = auto()
    WeatherService = auto()
    AggregatedTNode = auto()
    Persister = auto()

    @classmethod
    def default(cls) -> "GNodeRole":
        return cls.GNode

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.role"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
