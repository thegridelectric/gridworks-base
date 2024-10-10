from enum import auto
from typing import List

from gw.enums import GwStrEnum


class UniverseType(GwStrEnum):
    """
    Allows for multiple GridWorks, in particular for development and shared simulations
    Values:
      - Dev: Simulation running on a single computer.
      - Hybrid: Anything goes.
      - Production: Money at stake.

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#universetype)
      - [More Info](https://gridworks.readthedocs.io/en/latest/universe.html)
    """

    Dev = auto()
    Hybrid = auto()
    Production = auto()

    @classmethod
    def default(cls) -> "UniverseType":
        return cls.Dev

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "universe.type"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
