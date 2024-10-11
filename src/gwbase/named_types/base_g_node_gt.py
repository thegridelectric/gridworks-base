"""Type base.g.node.gt, version 002"""

from typing import Literal, Optional

from gw.named_types import GwBase
from gw.utils import snake_to_pascal
from pydantic import ConfigDict, PositiveInt

from gwbase.enums import CoreGNodeRole, GNodeStatus
from gwbase.property_format import (
    AlgoAddress,
    LeftRightDot,
    UUID4Str,
)


class BaseGNodeGt(GwBase):
    g_node_id: UUID4Str
    alias: LeftRightDot
    status: GNodeStatus
    role: CoreGNodeRole
    g_node_registry_addr: AlgoAddress
    prev_alias: Optional[LeftRightDot] = None
    gps_point_id: Optional[UUID4Str] = None
    ownership_deed_id: Optional[PositiveInt] = None
    ownership_deed_validator_addr: Optional[AlgoAddress] = None
    owner_addr: Optional[AlgoAddress] = None
    daemon_addr: Optional[AlgoAddress] = None
    trading_rights_id: Optional[PositiveInt] = None
    scada_algo_addr: Optional[AlgoAddress] = None
    scada_cert_id: Optional[PositiveInt] = None
    type_name: Literal["base.g.node.gt"] = "base.g.node.gt"
    version: Literal["002"] = "002"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
    )
