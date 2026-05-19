from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.transport_encoding import TransportClass


class GNodeSettings(BaseSettings):
    """Minimal runtime settings for a rabbit-actor process.

    The actor's durable identity (alias, GNodeId, free-form GNodeClass) is
    read from a ``g.node.gt`` JSON file at ``g_node_path``. The
    ``g_node_instance_id`` is generated fresh on each boot, per the FIS
    lifecycle. ``transport_class`` is a transport-only concept and is set
    independently here (so a Supervisor, which is not a GNode, can also
    use this settings shape).
    """

    rabbit: RabbitBrokerClient = RabbitBrokerClient()
    g_node_path: Path = Path("/etc/gridworks/g_node.json")
    transport_class: TransportClass = TransportClass.Scada
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="GNODE_", env_nested_delimiter="__", extra="ignore"
    )
