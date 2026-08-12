from pydantic_settings import BaseSettings, SettingsConfigDict

from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.transport_format import LeftRightDot, UUID4Str


class ServiceSettings(BaseSettings):
    """Minimum to ride gwbase's rabbit + sema toolkit WITHOUT being a GNode.

    Used by ``ActorBase`` directly (non-GNode consumers). No GNode identity, no ``transport_class`` — a tap
    has no routing identity to name; ``transport_class`` is an
    ``Orchestrator`` ``__init__`` param for the tiers that class-route.

    ``GWBASE_`` is the base-class default prefix only. A deployed service
    subclasses this (or ``GNodeSettings``) with its OWN env prefix, a
    dev-default ``service_alias``, and its own ``service_name`` — one
    ``.env``, one prefix per service (e.g. a journalkeeper reads ``GJK_*``,
    never ``GWBASE_*``)::

        class MySettings(ServiceSettings):
            service_alias: LeftRightDot = "d1.myservice"
            service_name: str = "myservice"
            model_config = SettingsConfigDict(
                env_prefix="MYSERVICE_",
                env_nested_delimiter="__",
                extra="ignore",
            )
    """

    rabbit: RabbitBrokerClient = RabbitBrokerClient()
    service_alias: LeftRightDot  # routable address, e.g. "d1.tap1"
    instance_id: UUID4Str | None = None  # auto-uuid per boot if None
    service_name: str = "gridworks"  # XDG path segment (NOT the alias)
    log_level: str = "INFO"
    log_rotate_bytes: int = 10_000_000  # 10MB per file
    log_rotate_count: int = 5  # 5 backup files

    model_config = SettingsConfigDict(
        env_prefix="GWBASE_",
        env_nested_delimiter="__",
        extra="ignore",
    )
