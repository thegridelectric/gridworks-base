from pydantic_settings import BaseSettings, SettingsConfigDict

from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.transport_format import LeftRightDot, UUID4Str


class ServiceSettings(BaseSettings):
    """Minimum to ride gwbase's rabbit + sema toolkit WITHOUT being a GNode.

    Used by ``ActorBase`` directly (journalkeeper, ear actor-side, future
    audit-tap consumers). No GNode identity, no ``transport_class`` — a tap
    has no routing identity to name; ``transport_class`` is an
    ``Orchestrator`` ``__init__`` param for the tiers that class-route.

    One ``GWBASE_`` env prefix for every gwbase service (tap or GNode):
    ``GNodeSettings`` inherits it.
    """

    rabbit: RabbitBrokerClient = RabbitBrokerClient()
    service_alias: LeftRightDot  # routable address, e.g. "d1.journal"
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
