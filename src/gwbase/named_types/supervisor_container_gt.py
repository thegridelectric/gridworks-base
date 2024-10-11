"""Type supervisor.container.gt, version 000"""

from typing import Literal

from gw.named_types import GwBase
from gw.utils import snake_to_pascal
from pydantic import ConfigDict, field_validator

from gwbase.enums import SupervisorContainerStatus
from gwbase.property_format import (
    LeftRightDot,
    UUID4Str,
    check_is_world_instance_name_format,
)


class SupervisorContainerGt(GwBase):
    supervisor_container_id: UUID4Str
    status: SupervisorContainerStatus
    world_instance_name: str
    supervisor_g_node_instance_id: UUID4Str
    supervisor_g_node_alias: LeftRightDot
    type_name: Literal["supervisor.container.gt"] = "supervisor.container.gt"
    version: Literal["000"] = "000"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
    )

    @field_validator("world_instance_name")
    @classmethod
    def _check_world_instance_name(cls, v: str) -> str:
        try:
            check_is_world_instance_name_format(v)
        except ValueError as e:
            raise ValueError(
                f"WorldInstanceName failed WorldInstanceNameFormat format validation: {e}",
            ) from e
        return v
