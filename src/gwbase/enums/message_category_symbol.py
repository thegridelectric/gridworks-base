from enum import auto
from typing import List

from gw.enums import GwStrEnum


class MessageCategorySymbol(GwStrEnum):
    """
    Shorthand symbols for MessageCategory000 Enum, used in meta-data like routing keys
    Values:
      - unknown: Default value
      - rj: Serialized Json message sent on the world rabbit broker from one GNode actor
        to another
      - rjb: Serailized Json message broadcast on the world rabbit broker by a GNode actor
      - s: GwSerial protocol message sent on the world rabbit broker
      - gw: Serialized Json message following MQTT topic format, sent on the world rabbit
        broker
      - post: REST API post
      - postack: REST API post response
      - get: REST API GET

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#messagecategorysymbol)
    """

    unknown = auto()
    rj = auto()
    rjb = auto()
    s = auto()
    gw = auto()
    post = auto()
    postack = auto()
    get = auto()

    @classmethod
    def default(cls) -> "MessageCategorySymbol":
        return cls.unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "message.category.symbol"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
