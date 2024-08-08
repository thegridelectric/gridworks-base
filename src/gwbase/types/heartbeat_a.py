"""Type heartbeat.a, version 100"""

import json
import logging
from typing import Any, Dict, Literal

import dotenv
from gw.errors import GwTypeError
from gw.utils import is_pascal_case, pascal_to_snake, snake_to_pascal
from pydantic import BaseModel, Field, field_validator

from gwbase.config import EnumSettings

ENCODE_ENUMS = EnumSettings(_env_file=dotenv.find_dotenv()).encode

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
        populate_by_name = True
        alias_generator = snake_to_pascal

    @field_validator("my_hex")
    @classmethod
    def _check_my_hex(cls, v: str) -> str:
        try:
            check_is_hex_char(v)
        except ValueError as e:
            raise ValueError(f"MyHex failed HexChar format validation: {e}") from e
        return v

    @field_validator("your_last_hex")
    @classmethod
    def _check_your_last_hex(cls, v: str) -> str:
        try:
            check_is_hex_char(v)
        except ValueError as e:
            raise ValueError(
                f"YourLastHex failed HexChar format validation: {e}"
            ) from e
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Main step in serializing the object. Encodes enums as their 8-digit random hex symbol if
        settings.encode_enums = 1.
        """
        if ENCODE_ENUMS:
            return self.enum_encoded_dict()
        else:
            return self.plain_enum_dict()

    def plain_enum_dict(self) -> Dict[str, Any]:
        """
        Returns enums as their values.
        """
        d = {
            snake_to_pascal(key): value
            for key, value in self.model_dump().items()
            if value is not None
        }
        return d

    def enum_encoded_dict(self) -> Dict[str, Any]:
        """
        Encodes enums as their 8-digit random hex symbol
        """
        d = {
            snake_to_pascal(key): value
            for key, value in self.model_dump().items()
            if value is not None
        }
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the heartbeat.a.100 representation designed to send in a message.

        Recursively encodes enums as hard-to-remember 8-digit random hex symbols
        unless settings.encode_enums is set to 0.
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
    def type_to_tuple(cls, b: bytes) -> HeartbeatA:
        """
        Given the bytes in a message, returns the corresponding class object.

        Args:
            b (bytes): candidate type instance

        Raises:
           GwTypeError: if the bytes are not a heartbeat.a.100 type

        Returns:
            HeartbeatA instance
        """
        try:
            d = json.loads(b)
        except TypeError as e:
            raise GwTypeError("Type must be string or bytes!") from e
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing  must result in dict!\n <{b}>")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> HeartbeatA:
        """
        Translates a dict representation of a heartbeat.a.100 message object
        into the Python class object.
        """
        for key in d.keys():
            if not is_pascal_case(key):
                raise GwTypeError(f"Key '{key}' is not PascalCase")
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
        d3 = {pascal_to_snake(key): value for key, value in d2.items()}
        return HeartbeatA(**d3)


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
