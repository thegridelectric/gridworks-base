"""Type base.g.node.gt, version 002"""

from typing import ConfigDict, Literal, Optional, PositiveInt, field_validator

from gw.named_types import GwBase
from gw.utils import snake_to_pascal

from gwbase.enums import CoreGNodeRole, GNodeStatus
from gwbase.property_format import (
    LeftRightDot,
    UUID4Str,
    check_is_algo_address_string_format,
)


class BaseGNodeGt(GwBase):
    g_node_id: UUID4Str
    alias: LeftRightDot
    status: GNodeStatus
    role: CoreGNodeRole
    g_node_registry_addr: str
    prev_alias: Optional[LeftRightDot] = None
    gps_point_id: Optional[UUID4Str] = None
    ownership_deed_id: Optional[PositiveInt] = None
    ownership_deed_validator_addr: Optional[str] = None
    owner_addr: Optional[str] = None
    daemon_addr: Optional[str] = None
    trading_rights_id: Optional[PositiveInt] = None
    scada_algo_addr: Optional[str] = None
    scada_cert_id: Optional[PositiveInt] = None
    type_name: Literal["base.g.node.gt"] = "base.g.node.gt"
    version: Literal["002"] = "002"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        extra="allow",
        frozen=True,
        populate_by_name=True,
        use_enum_values=True,
    )

    @field_validator("g_node_registry_addr")
    @classmethod
    def _check_g_node_registry_addr(cls, v: str) -> str:
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"GNodeRegistryAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("ownership_deed_validator_addr")
    @classmethod
    def _check_ownership_deed_validator_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnershipDeedValidatorAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("owner_addr")
    @classmethod
    def _check_owner_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"OwnerAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("daemon_addr")
    @classmethod
    def _check_daemon_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"DaemonAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v

    @field_validator("scada_algo_addr")
    @classmethod
    def _check_scada_algo_addr(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_algo_address_string_format(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaAlgoAddr failed AlgoAddressStringFormat format validation: {e}",
            ) from e
        return v
