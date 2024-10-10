"""Type heartbeat.a, version 001 - sample of type evolution with versions."""

import json
from typing import Any, Dict, Literal

from gw.errors import GwTypeError
from pydantic import BaseModel
from pydantic.alias_generators import to_pascal, to_snake


class HeartbeatA001(BaseModel):
    """
    This earlier version of type heartbeat.a does not enforce that MyHex and
    YourLastHex are single character hexes - just that they are strings
    """

    my_hex: str
    your_last_hex: str
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: str = "001"

    class Config:
        populate_by_name = True
        alias_generator = to_pascal

    def as_dict(self) -> Dict[str, Any]:
        d = {
            to_pascal(key): value
            for key, value in self.model_dump().items()
            if value is not None
        }
        return d

    def as_type(self) -> str:
        return json.dumps(self.as_dict())


class HeartbeatA001_Maker:
    type_name = "heartbeat.a"
    version = "001"

    @classmethod
    def tuple_to_type(cls, tuple: HeartbeatA001) -> str:
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> HeartbeatA001:
        try:
            d = json.loads(t)
        except TypeError:
            raise GwTypeError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise GwTypeError(f"Deserializing {t} must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> HeartbeatA001:
        d2 = dict(d)
        if "MyHex" not in d2.keys():
            raise GwTypeError(f"dict {d2} missing MyHex")
        if "YourLastHex" not in d2.keys():
            raise GwTypeError(f"dict {d2} missing YourLastHex")
        if "TypeName" not in d2.keys():
            raise GwTypeError(f"dict {d2} missing TypeName")
        d3 = {to_snake(key): value for key, value in d2.items()}
        return HeartbeatA001(**d3)
