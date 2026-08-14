from typing import Literal
from gwbase.sema.base import GwBaseSemaType
from gwbase.sema.property_format import LeftRightDot
from gwbase.sema.property_format import NonEmptyString
from gwbase.sema.property_format import UUID4Str
from gwbase.sema.property_format import UniverseRun


class FisConnectClaims(GwBaseSemaType):
    """Sema: https://schemas.electricity.works/types/fis.connect.claims/000"""

    alias: LeftRightDot
    instance_id: UUID4Str
    run: UniverseRun
    g_node_class: NonEmptyString | None = None
    type_name: Literal["fis.connect.claims"] = "fis.connect.claims"
    version: Literal["000"] = "000"
