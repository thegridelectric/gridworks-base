from abc import ABC, abstractmethod
from typing import Any
from gw_base.transport_encoding import MessageCategory


class ActorApplication(ABC):

    @abstractmethod
    def process_message(
        self,
        *,
        category: MessageCategory,
        type_name: str,
        payload: bytes,
        codec: Any, 
        routing_key: str,
    ) -> None:
        """Handle an incoming message."""
        ...
