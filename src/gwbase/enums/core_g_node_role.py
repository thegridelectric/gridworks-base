from enum import auto
from typing import List, Optional

from gw.enums import GwStrEnum


class CoreGNodeRole(GwStrEnum):
    """
    CoreGNodeRole assigned by GNodeFactory

    Enum core.g.node.role version 001 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs). For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#coregnoderole)
      - [More Info](https://gridworks.readthedocs.io/en/latest/core-g-node-role.html)

    Values (with symbols in parens):
      - Other (00000000)
      - TerminalAsset (0f8872f7)
      - AtomicTNode (d9823442)
      - MarketMaker (86f21dd2)
      - AtomicMeteringNode (9521af06)
      - ConductorTopologyNode (4502e355)
      - InterconnectionComponent (d67e564e)
      - Scada (7a8e4046)
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
        """
        Returns default value (in this case Other)
        """
        return cls.Other

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
        The name in the GridWorks Type Registry (core.g.node.role)
        """
        return "core.g.node.role"

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
            a later version of this enum, returns the default value of "Other".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a CoreGNodeRole enum to send in seriliazed messages.

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
            "0f8872f7",
            "d9823442",
            "86f21dd2",
            "9521af06",
            "4502e355",
            "d67e564e",
            "7a8e4046",
        ]


symbol_to_value = {
    "00000000": "Other",
    "0f8872f7": "TerminalAsset",
    "d9823442": "AtomicTNode",
    "86f21dd2": "MarketMaker",
    "9521af06": "AtomicMeteringNode",
    "4502e355": "ConductorTopologyNode",
    "d67e564e": "InterconnectionComponent",
    "7a8e4046": "Scada",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "Other": "000",
    "TerminalAsset": "000",
    "AtomicTNode": "000",
    "MarketMaker": "000",
    "AtomicMeteringNode": "000",
    "ConductorTopologyNode": "001",
    "InterconnectionComponent": "001",
    "Scada": "001",
}
