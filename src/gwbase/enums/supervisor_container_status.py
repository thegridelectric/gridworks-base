from enum import auto
from typing import List, Optional

from gw.enums import GwStrEnum


class SupervisorContainerStatus(GwStrEnum):
    """
    Manages lifecycle of the docker containers where GridWorks actors run

    Enum supervisor.container.status version 000 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs). For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#supervisorcontainerstatus)

    Values (with symbols in parens):
      - Unknown (00000000): Default value
      - Authorized (f48cff43): World has created the information for starting the container
      - Launching (17c5cc54): World has launched the container
      - Provisioning (ec342324): Container has started, but is going through its provisioning process
      - Running (cfde1b40): GNode actors in the container are active
      - Stopped (4e28b6ae): Stopped
      - Deleted (da2dafe0): Deleted
    """

    Unknown = auto()
    Authorized = auto()
    Launching = auto()
    Provisioning = auto()
    Running = auto()
    Stopped = auto()
    Deleted = auto()

    @classmethod
    def default(cls) -> "SupervisorContainerStatus":
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
            return "000"
        if not isinstance(value, str):
            raise ValueError("This method applies to strings, not enums")
        if value not in value_to_version.keys():
            raise ValueError(f"Unknown enum value: {value}")
        return value_to_version[value]

    @classmethod
    def enum_name(cls) -> str:
        """
        The name in the GridWorks Type Registry (supervisor.container.status)
        """
        return "supervisor.container.status"

    @classmethod
    def enum_version(cls) -> str:
        """
        The version in the GridWorks Type Registry (000)
        """
        return "000"

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
        Provides the encoding symbol for a SupervisorContainerStatus enum to send in seriliazed messages.

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
            "f48cff43",
            "17c5cc54",
            "ec342324",
            "cfde1b40",
            "4e28b6ae",
            "da2dafe0",
        ]


symbol_to_value = {
    "00000000": "Unknown",
    "f48cff43": "Authorized",
    "17c5cc54": "Launching",
    "ec342324": "Provisioning",
    "cfde1b40": "Running",
    "4e28b6ae": "Stopped",
    "da2dafe0": "Deleted",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "Unknown": "000",
    "Authorized": "000",
    "Launching": "000",
    "Provisioning": "000",
    "Running": "000",
    "Stopped": "000",
    "Deleted": "000",
}
