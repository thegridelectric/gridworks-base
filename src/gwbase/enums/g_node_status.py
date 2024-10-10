from enum import auto
from typing import List

from gw.enums import GwStrEnum


class GNodeStatus(GwStrEnum):
    """
    Enum for managing GNode lifecycle
    Values:
      - Unknown: Default value
      - Pending: The GNode exists but cannot be used yet.
      - Active: The GNode can be used.
      - PermanentlyDeactivated: The GNode can no longer be used, now or in the future.
      - Suspended: The GNode cannot be used, but may become active in the future.

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#gnodestatus)
      - [More Info](https://gridworks.readthedocs.io/en/latest/g-node-status.html)
    """

    Unknown = auto()
    Pending = auto()
    Active = auto()
    PermanentlyDeactivated = auto()
    Suspended = auto()

    @classmethod
    def default(cls) -> "GNodeStatus":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "g.node.status"

    @classmethod
    def enum_version(cls) -> str:
        return "100"
