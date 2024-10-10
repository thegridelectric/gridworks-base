"""Type sim.timestep, version 000"""

from typing import Literal

from gw.named_types import GwBase

from gwbase.property_format import (
    LeftRightDot,
    UTCMilliseconds,
    UTCSeconds,
    UUID4Str,
)


class SimTimestep(GwBase):
    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    time_unix_s: UTCSeconds
    timestep_created_ms: UTCMilliseconds
    message_id: UUID4Str
    type_name: Literal["sim.timestep"] = "sim.timestep"
    version: Literal["000"] = "000"
