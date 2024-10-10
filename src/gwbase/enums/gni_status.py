from enum import auto
from typing import List

from gw.enums import GwStrEnum


class GniStatus(GwStrEnum):
    """
    Enum for managing GNodeInstance lifecycle
    Values:
      - Unknown: Default Value
      - Pending: Has been created by the World, but has not yet finished provisioning
      - Active: Active in its GridWorks world. If the GNodeInstance has an actor, that
        actor is communicating
      - Done: No longer represents the GNode.

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#gnistatus)
      - [More Info](https://gridworks.readthedocs.io/en/latest/g-node-instance.html)
    """

    Unknown = auto()
    Pending = auto()
    Active = auto()
    Done = auto()

    @classmethod
    def default(cls) -> "GniStatus":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "gni.status"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
