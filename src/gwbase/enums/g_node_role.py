from enum import auto
from typing import List, Optional

from gw.enums import GwStrEnum


class GNodeRole(GwStrEnum):
    """
    Categorizes GNodes by their function within GridWorks

    Enum g.node.role version 001 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs). For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#gnoderole)
      - [More Info](https://gridworks.readthedocs.io/en/latest/g-node-role.html)

    Values (with symbols in parens):
      - GNode (00000000): Default value
      - TerminalAsset (bdeaa0b1): An avatar for a real-word Transactive Device [More Info](https://gridworks.readthedocs.io/en/latest/transactive-device.html).
      - AtomicTNode (8021dcad): Transacts in markets on behalf of, and controlling the power use
        of, a TerminalAsset [More Info](https://gridworks.readthedocs.io/en/latest/atomic-t-node.html).
      - MarketMaker (304890c5): Runs energy markets at its Node in the GNodeTree [More Info](https://gridworks.readthedocs.io/en/latest/market-maker.html).
      - AtomicMeteringNode (8eb5b9e1): Role of a GNode that will become an AtomicTNode, prior to
        it owning TaTradingRights
      - ConductorTopologyNode (234cfaa2): An avatar for a real-world electric grid node - e.g. a
        substation or transformer
      - InterconnectionComponent (fec0c127): An avatar for a cable or wire on the electric grid
      - World (3901c7d2): Adminstrative GNode responsible for managing and authorizing instances [More Info](https://gridworks.readthedocs.io/en/latest/world-role.html).
      - TimeCoordinator (c499943c): Responsible for managing time in simulations
      - Supervisor (88112a93): Responsible for GNode actors running in a container [More Info](https://gridworks.readthedocs.io/en/latest/supervisor.html).
      - Scada (674ad859): GNode associated to the device and code that directly monitors and actuates
        a Transactive Device
      - PriceService (2161739f): Provides price forecasts for markets run by MarketMakers
      - WeatherService (1dce1efd): Provides weather forecasts
      - AggregatedTNode (db57d184): An aggregation of AtomicTNodes
      - Persister (07f28817): Responsible for acking events with delivery guarantees
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
        """
        Returns default value (in this case GNode)
        """
        return cls.GNode

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]

    @classmethod
    def version(cls, value: Optional[str] = None) -> str:
        """
        Returns the version of the class (default) used by this package or the
        version of a candidate enum value (always less than or equal to the version
        of the class)

        Args:
            value (Optional[str]): None (for version of the Enum itself) or
            the candidate enum value.

        Raises:
            ValueError: If the value is not one of the enum values.

        Returns:
            str: The version of the enum used by this code (if given no
            value) OR the earliest version of the enum containing the value.
        """
        if value is None:
            return "001"
        if not isinstance(value, str):
            raise ValueError("This method applies to strings, not enums")
        if value not in value_to_version.keys():
            raise ValueError(f"Unknown enum value: {value}")
        return value_to_version[value]

    @classmethod
    def enum_name(cls) -> str:
        """
        The name in the GridWorks Type Registry (g.node.role)
        """
        return "g.node.role"

    @classmethod
    def enum_version(cls) -> str:
        """
        The version in the GridWorks Type Registry (001)
        """
        return "001"

    @classmethod
    def symbol_to_value(cls, symbol: str) -> str:
        """
        Given the symbol sent in a serialized message, returns the encoded enum.

        Args:
            symbol (str): The candidate symbol.

        Returns:
            str: The encoded value associated to that symbol. If the symbol is not
            recognized - which could happen if the actor making the symbol is using
            a later version of this enum, returns the default value of "GNode".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a GNodeRole enum to send in seriliazed messages.

        Args:
            symbol (str): The candidate value.

        Returns:
            str: The symbol encoding that value. If the value is not recognized -
            which could happen if the actor making the message used a later version
            of this enum than the actor decoding the message, returns the default
            symbol of "00000000".
        """
        if value not in value_to_symbol.keys():
            return value_to_symbol[cls.default().value]
        return value_to_symbol[value]

    @classmethod
    def symbols(cls) -> List[str]:
        """
        Returns a list of the enum symbols
        """
        return [
            "00000000",
            "bdeaa0b1",
            "8021dcad",
            "304890c5",
            "8eb5b9e1",
            "234cfaa2",
            "fec0c127",
            "3901c7d2",
            "c499943c",
            "88112a93",
            "674ad859",
            "2161739f",
            "1dce1efd",
            "db57d184",
            "07f28817",
        ]


symbol_to_value = {
    "00000000": "GNode",
    "bdeaa0b1": "TerminalAsset",
    "8021dcad": "AtomicTNode",
    "304890c5": "MarketMaker",
    "8eb5b9e1": "AtomicMeteringNode",
    "234cfaa2": "ConductorTopologyNode",
    "fec0c127": "InterconnectionComponent",
    "3901c7d2": "World",
    "c499943c": "TimeCoordinator",
    "88112a93": "Supervisor",
    "674ad859": "Scada",
    "2161739f": "PriceService",
    "1dce1efd": "WeatherService",
    "db57d184": "AggregatedTNode",
    "07f28817": "Persister",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "GNode": "000",
    "TerminalAsset": "000",
    "AtomicTNode": "000",
    "MarketMaker": "000",
    "AtomicMeteringNode": "000",
    "ConductorTopologyNode": "000",
    "InterconnectionComponent": "000",
    "World": "000",
    "TimeCoordinator": "000",
    "Supervisor": "000",
    "Scada": "000",
    "PriceService": "000",
    "WeatherService": "000",
    "AggregatedTNode": "000",
    "Persister": "001",
}
