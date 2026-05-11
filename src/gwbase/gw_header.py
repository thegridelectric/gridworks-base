from typing import TypedDict

import re
from dataclasses import dataclass

LEFT_RIGHT_DOT_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)*$")
UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@dataclass
class GwHeader(TypedDict):
    Src: str
    Dst: str
    MessageType: str
    MessageId: str
    AckRequired: bool

    def validate(self) -> None:
        if not LEFT_RIGHT_DOT_RE.match(self.Src):
            raise ValueError("Invalid Src format")

        if not LEFT_RIGHT_DOT_RE.match(self.Dst):
            raise ValueError("Invalid Dst format")

        if not LEFT_RIGHT_DOT_RE.match(self.MessageType):
            raise ValueError("Invalid MessageType format")

        if not UUID4_RE.match(self.MessageId):
            raise ValueError("Invalid MessageId format")