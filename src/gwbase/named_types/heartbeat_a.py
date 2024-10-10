"""Type heartbeat.a, version 100"""

from typing import Literal

from gw.named_types import GwBase

from gwbase.property_format import (
    HexChar,
)


class HeartbeatA(GwBase):
    my_hex: HexChar
    your_last_hex: HexChar
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["100"] = "100"
