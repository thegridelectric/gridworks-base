from typing import Literal

from gwbase.sema.base import GwBaseSemaType
from gwbase.sema.property_format import HexChar


class HeartbeatA(GwBaseSemaType):
    """Sema: https://schemas.electricity.works/types/heartbeat.a/000"""

    my_hex: HexChar
    your_last_hex: HexChar | None = None
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["000"] = "000"
