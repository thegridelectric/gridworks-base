import json
from typing import Dict, Optional

from gw.errors import GwTypeError
from gw.named_types import GwBase

from gwbase.named_types.asl_types import TypeByName


class GwCodec:
    type_by_name: Dict[str, GwBase]

    def __init__(self, type_by_name: Dict[str, GwBase] = TypeByName) -> None:
        self.type_by_name = type_by_name

    @property
    def type_list(self) -> list[str]:
        return list(self.type_by_name.keys())

    def from_type(self, msg_bytes: bytes) -> Optional[GwBase]:
        try:
            data = json.loads(msg_bytes.decode("utf-8"))
        except Exception:
            print("failed json loads")
            return None
        return self.from_dict(data)

    def from_dict(self, data: dict) -> Optional[GwBase]:
        if "TypeName" not in data.keys():
            raise GwTypeError(f"No TypeName - so not a type. Keys: <{data.keys()}>")
        outer_type_name = data["TypeName"]
        # Scada messages all come in a 'gw' incomplete type with actual message in "Payload"
        if outer_type_name == "gw":
            if "Payload" not in data.keys():
                raise GwTypeError(
                    f"Type Gw must include Payload! Keys: <{data.keys()}>"
                )
            data = data["Payload"]
            if "TypeName" not in data.keys():
                raise GwTypeError(f"gw Payload must have TypeName. Keys: {data.keys()}")

        return self.type_by_name[data["TypeName"]].from_dict(data)
