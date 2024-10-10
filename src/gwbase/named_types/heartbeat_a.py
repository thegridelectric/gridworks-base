"""Type heartbeat.a, version 100"""

from typing import Literal

from gw.named_types import GwBase


class HeartbeatA(GwBase):
    my_hex: str
    your_last_hex: str
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["100"] = "100"
