"""Type super.starter, version 000"""

from typing import List, Literal

from gw.named_types import GwBase
from gw.utils import snake_to_pascal
from pydantic import ConfigDict

from gwbase.named_types.g_node_instance_gt import GNodeInstanceGt
from gwbase.named_types.supervisor_container_gt import SupervisorContainerGt
from gwbase.property_format import (
    LeftRightDot,
)


class SuperStarter(GwBase):
    supervisor_container: SupervisorContainerGt
    gni_list: List[GNodeInstanceGt]
    alias_with_key_list: List[LeftRightDot]
    key_list: List[str]
    type_name: Literal["super.starter"] = "super.starter"
    version: Literal["000"] = "000"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
    )
