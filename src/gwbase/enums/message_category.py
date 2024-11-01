from enum import auto
from typing import List

from gw.enums import GwStrEnum


class MessageCategory(GwStrEnum):
    """
    Categorizes how GridWorks messages are sent and decoded/encoded
    Values:
      - Unknown: Default value
      - RabbitJsonDirect: Serialized Json message sent on the world rabbit broker from
        one GNode actor to another
      - RabbitJsonBroadcast: Serailized Json message broadcast on the world rabbit broker
        by a GNode actor
      - RabbitGwSerial: GwSerial protocol message sent on the world rabbit broker
      - MqttJsonBroadcast: Serialized Json message following MQTT topic format, sent on
        the world rabbit broker. Format: gw/from-node/type-name (or gw.from-node.type-name in
        rabbit broker)
      - RestApiPost: REST API post
      - RestApiPostResponse: REST API post response
      - RestApiGet: REST API GET
      - MqttDirect: e.g gw/hw1-isone-me-versant-keene-beech-scada/to/a/report-event

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#messagecategory)
    """

    Unknown = auto()
    RabbitJsonDirect = auto()
    RabbitJsonBroadcast = auto()
    RabbitGwSerial = auto()
    MqttJsonBroadcast = auto()
    RestApiPost = auto()
    RestApiPostResponse = auto()
    RestApiGet = auto()
    MqttDirect = auto()

    @classmethod
    def default(cls) -> "MessageCategory":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "message.category"

    @classmethod
    def enum_version(cls) -> str:
        return "001"
