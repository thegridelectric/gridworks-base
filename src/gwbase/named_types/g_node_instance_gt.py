"""Type g.node.instance.gt, version 000"""

from typing import ConfigDict, Literal, Optional, StrictInt, field_validator

from gw.named_types import GwBase
from gw.utils import snake_to_pascal

from gwbase.enums import GniStatus, StrategyName
from gwbase.property_format import (
    UTCSeconds,
    UUID4Str,
    check_is_algo_address_string_format,
)


class GNodeInstanceGt(GwBase):
    g_node_instance_id: UUID4Str
    g_node_id: UUID4Str
    strategy: StrategyName
    status: GniStatus
    supervisor_container_id: UUID4Str
    start_time_unix_s: UTCSeconds
    end_time_unix_s: StrictInt
    algo_address: Optional[str] = None
    type_name: Literal["g.node.instance.gt"] = "g.node.instance.gt"
    version: Literal["000"] = "000"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    @field_validator("algo_address")
    @classmethod
    def _check_algo_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"AlgoAddress failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v
