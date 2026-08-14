from typing import Literal
from gwbase.sema.base import GwBaseSemaType
from gwbase.sema.property_format import LeftRightDot
from gwbase.sema.property_format import UTCMilliseconds
from gwbase.sema.property_format import UTCSeconds
from gwbase.sema.property_format import UUID4Str


class SimTimestep(GwBaseSemaType):
    """Sema: https://schemas.electricity.works/types/sim.timestep/000"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    time_unix_s: UTCSeconds
    timestep_created_ms: UTCMilliseconds
    message_id: UUID4Str
    type_name: Literal["sim.timestep"] = "sim.timestep"
    version: Literal["000"] = "000"
