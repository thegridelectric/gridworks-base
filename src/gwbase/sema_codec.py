from abc import ABC, abstractmethod
from typing import Any


class SemaCodec(ABC):
    """Application-provided semantic codec."""

    @abstractmethod
    def from_bytes(self, payload: bytes) -> Any:
        """Deserialize payload bytes into a domain object."""

    @abstractmethod
    def to_bytes(self, msg: Any) -> bytes:
        """Serialize domain object into payload bytes."""