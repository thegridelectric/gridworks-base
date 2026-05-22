from typing import Literal

from gwbase.sema.base import GwBaseSemaType
from gwbase.sema.property_format import LeftRightDot, UTCSeconds, UUID4Str


class Ready(GwBaseSemaType):
    """Sema: https://schemas.electricity.works/types/sim.ready/000"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    time_unix_s: UTCSeconds
    type_name: Literal["sim.ready"] = "sim.ready"
    version: Literal["000"] = "000"
