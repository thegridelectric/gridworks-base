"""Type g.node.instance.gt, version 000"""

from typing import Literal, Optional

from gw.named_types import GwBase
from gw.utils import snake_to_pascal
from pydantic import ConfigDict, StrictInt

from gwbase.enums import GniStatus, StrategyName
from gwbase.property_format import (
    AlgoAddress,
    UTCSeconds,
    UUID4Str,
)


class GNodeInstanceGt(GwBase):
    g_node_instance_id: UUID4Str
    g_node_id: UUID4Str
    strategy: StrategyName
    status: GniStatus
    supervisor_container_id: UUID4Str
    start_time_unix_s: UTCSeconds
    end_time_unix_s: StrictInt
    algo_address: Optional[AlgoAddress] = None
    type_name: Literal["g.node.instance.gt"] = "g.node.instance.gt"
    version: Literal["000"] = "000"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
    )
