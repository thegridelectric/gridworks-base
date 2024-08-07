from enum import auto
from typing import List, Optional

from gw.enums import GwStrEnum


class GNodeStatus(GwStrEnum):
    """
    Enum for managing GNode lifecycle

    Enum g.node.status version 100 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs). For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#gnodestatus)
      - [More Info](https://gridworks.readthedocs.io/en/latest/g-node-status.html)

    Values (with symbols in parens):
      - Unknown (00000000): Default value
      - Pending (153d3475): The GNode exists but cannot be used yet.
      - Active (a2cfc2f7): The GNode can be used.
      - PermanentlyDeactivated (839b38db): The GNode can no longer be used, now or in the future.
      - Suspended (f5831e1d): The GNode cannot be used, but may become active in the future.
    """

    Unknown = auto()
    Pending = auto()
    Active = auto()
    PermanentlyDeactivated = auto()
    Suspended = auto()

    @classmethod
    def default(cls) -> "GNodeStatus":
        """
        Returns default value (in this case Unknown)
        """
        return cls.Unknown

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
            return "100"
        if not isinstance(value, str):
            raise ValueError("This method applies to strings, not enums")
        if value not in value_to_version.keys():
            raise ValueError(f"Unknown enum value: {value}")
        return value_to_version[value]

    @classmethod
    def enum_name(cls) -> str:
        """
        The name in the GridWorks Type Registry (g.node.status)
        """
        return "g.node.status"

    @classmethod
    def enum_version(cls) -> str:
        """
        The version in the GridWorks Type Registry (100)
        """
        return "100"

    @classmethod
    def symbol_to_value(cls, symbol: str) -> str:
        """
        Given the symbol sent in a serialized message, returns the encoded enum.

        Args:
            symbol (str): The candidate symbol.

        Returns:
            str: The encoded value associated to that symbol. If the symbol is not
            recognized - which could happen if the actor making the symbol is using
            a later version of this enum, returns the default value of "Unknown".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a GNodeStatus enum to send in seriliazed messages.

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
            "153d3475",
            "a2cfc2f7",
            "839b38db",
            "f5831e1d",
        ]


symbol_to_value = {
    "00000000": "Unknown",
    "153d3475": "Pending",
    "a2cfc2f7": "Active",
    "839b38db": "PermanentlyDeactivated",
    "f5831e1d": "Suspended",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "Unknown": "100",
    "Pending": "100",
    "Active": "100",
    "PermanentlyDeactivated": "100",
    "Suspended": "100",
}
