"""Type heartbeat.a, version 100"""

import json
import logging
from typing import Any
from typing import Dict
from typing import Literal

from gw.errors import GwTypeError
from gw.utils import snake_to_camel
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class HeartbeatA(BaseModel):
    """
    Used to check that an actor can both send and receive messages.

    Payload for direct messages sent back and forth between actors, for example a Supervisor
    and one of its subordinates. Update: MyHex and YourLatestHex must have format HexChar

    [More info](https://gridworks.readthedocs.io/en/latest/g-node-instance.html)
    """

    my_hex: str = Field(
        title="Hex character getting sent",
        default="0",
    )
    your_last_hex: str = Field(
        title="Last hex character received from heartbeat partner",
        default="0",
    )
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["100"] = "100"

    class Config:
        allow_population_by_field_name = True
        alias_generator = snake_to_camel

    @validator("my_hex")
    def _check_my_hex(cls, v: str) -> str:
        try:
            check_is_hex_char(v)
        except ValueError as e:
            raise ValueError(f"MyHex failed HexChar format validation: {e}")
        return v

    @validator("your_last_hex")
    def _check_your_last_hex(cls, v: str) -> str:
        try:
            check_is_hex_char(v)
        except ValueError as e:
            raise ValueError(f"YourLastHex failed HexChar format validation: {e}")
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        heartbeat.a.100 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        heartbeat.a.100 type. Unlike the standard python dict method,
        it makes the following substantive changes:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.
        """
        d = {
            key: value
            for key, value in self.dict(
                by_alias=True, include=self.__fields_set__ | {"type_name", "version"}
            ).items()
            if value is not None
        }
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the heartbeat.a.100 representation.

        Instances in the class are python-native representations of heartbeat.a.100
        objects, while the actual heartbeat.a.100 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is HeartbeatA.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class HeartbeatA_Maker:
    type_name = "heartbeat.a"
    version = "100"

    @classmethod
    def tuple_to_type(cls, tuple: HeartbeatA) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> HeartbeatA:
        """
        Given a serialized JSON type object, returns the Python class object.
        """
        try:
            d = json.loads(t)
        except TypeError:
            raise GwTypeError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing <{t}> must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> HeartbeatA:
        """
        Deserialize a dictionary representation of a heartbeat.a.100 message object
        into a HeartbeatA python object for internal use.

        This is the near-inverse of the HeartbeatA.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a GwTypeError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           GwTypeError: if the dict cannot be turned into a HeartbeatA object.

        Returns:
            HeartbeatA
        """
        d2 = dict(d)
        if "MyHex" not in d2.keys():
            raise GwTypeError(f"dict missing MyHex: <{d2}>")
        if "YourLastHex" not in d2.keys():
            raise GwTypeError(f"dict missing YourLastHex: <{d2}>")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise GwTypeError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "100":
            LOGGER.debug(
                f"Attempting to interpret heartbeat.a version {d2['Version']} as version 100"
            )
            d2["Version"] = "100"
        return HeartbeatA(**d2)


def check_is_hex_char(v: str) -> None:
    """Checks HexChar format

    HexChar format: single-char string in '0123456789abcdefABCDEF'

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not HexChar format
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}> must be a hex char, but not even a string")
    if len(v) > 1:
        raise ValueError(f"<{v}> must be a hex char, but not of len 1")
    if v not in "0123456789abcdefABCDEF":
        raise ValueError(f"<{v}> must be one of '0123456789abcdefABCDEF'")
