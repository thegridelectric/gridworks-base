from enum import auto
from typing import List, Optional

from gw.enums import GwStrEnum


class StrategyName(GwStrEnum):
    """
    Used to assign code to run a particular GNodeInstance

    Enum strategy.name version 001 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs). For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#strategyname)

    Values (with symbols in parens):
      - NoActor (00000000): Assigned to GNodes that do not have actors
      - WorldA (642c83d3): Authority on GNodeInstances, and their private keys. Maintains a FastAPI
        used for relational information about backoffice information held locally and/or in
        the GNodeRegistry/GNodeFactory. [More Info](https://gridworks.readthedocs.io/en/latest/world-role.html)
      - SupervisorA (4bb2cf7e): A simple supervisor that monitors its supervised AtomicTNode GNode
        strategies via a heartbeat health check. [More Info](https://gridworks.readthedocs.io/en/latest/supervisor.html)
      - AtnHeatPumpWithBoostStore (f5961401): AtomicTNode for a heat pump thermal storage heating
        system with a boost element and a thermal \n heated by the boost element. [More on AtomicTNodes](https://gridworks.readthedocs.io/en/latest/atomic-t-node.html)
      - TcGlobalA (73fbe6ab): Used to manage the global time of the Gridworks system when run with\n
        in a fully simulated universe. \n [More on TimeCoordinators](https://gridworks.readthedocs.io/en/latest/time-coordinator.html)
      - MarketMakerA (5e18a52e): Runs a two-sided market associated to its GNode as part of the copper
        GNode sub-tree. [More on MarketMakers](https://gridworks.readthedocs.io/en/latest/market-maker.html)
      - AtnBrickStorageHeater (b2a125d6): Publicly available Dijkstra-based AtomicTNode strategy
        for a brick storage heater. These heaters are rooom units that store heat in a brick
        core, are heated with resistive elements, and typically have a fan to blow air over
        the brick core. They are sometimes called Electric Thermal Storage (ETS) heaters, and
        in the UK are often called Economy 7 heaters or Night Storage Heaters. A strategy very
        similar to this was used by VCharge to manage an ETS fleet of several thousand heaters
        in Pennsylvania. This strategy is meant to serve as a template for other private strategies,
        and also allows for an end-to-end simulation of a realistic aggregated transactive load
        capable of generating a highly elastic bid curve [More Info](https://gridworks-atn.readthedocs.io/en/latest/brick-storage-heater.html)
    """

    NoActor = auto()
    WorldA = auto()
    SupervisorA = auto()
    AtnHeatPumpWithBoostStore = auto()
    TcGlobalA = auto()
    MarketMakerA = auto()
    AtnBrickStorageHeater = auto()

    @classmethod
    def default(cls) -> "StrategyName":
        """
        Returns default value (in this case NoActor)
        """
        return cls.NoActor

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
        The name in the GridWorks Type Registry (strategy.name)
        """
        return "strategy.name"

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
            a later version of this enum, returns the default value of "NoActor".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a StrategyName enum to send in seriliazed messages.

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
            "642c83d3",
            "4bb2cf7e",
            "f5961401",
            "73fbe6ab",
            "5e18a52e",
            "b2a125d6",
        ]


symbol_to_value = {
    "00000000": "NoActor",
    "642c83d3": "WorldA",
    "4bb2cf7e": "SupervisorA",
    "f5961401": "AtnHeatPumpWithBoostStore",
    "73fbe6ab": "TcGlobalA",
    "5e18a52e": "MarketMakerA",
    "b2a125d6": "AtnBrickStorageHeater",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "NoActor": "000",
    "WorldA": "000",
    "SupervisorA": "000",
    "AtnHeatPumpWithBoostStore": "000",
    "TcGlobalA": "000",
    "MarketMakerA": "000",
    "AtnBrickStorageHeater": "001",
}
