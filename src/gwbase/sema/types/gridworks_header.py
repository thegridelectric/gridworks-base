from typing import Any, Literal

from gwbase.sema.base import GwBaseSemaType
from gwbase.sema.property_format import LeftRightDot


class GridworksHeader(GwBaseSemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.header/001"""

    src: str
    dst: Any
    message_type: LeftRightDot
    message_id: str
    ack_required: bool
    type_name: Literal["gridworks.header"] = "gridworks.header"
    version: Literal["001"] = "001"
