"""Type ready, version 001"""

from typing import Literal

from gw.named_types import GwBase
from pydantic import StrictInt

from gwbase.property_format import (
    LeftRightDot,
    UUID4Str,
)


class Ready(GwBase):
    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    time_unix_s: StrictInt
    type_name: Literal["ready"] = "ready"
    version: Literal["001"] = "001"
