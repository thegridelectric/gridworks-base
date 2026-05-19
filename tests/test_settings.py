from pathlib import Path

from gwbase.config import GNodeSettings
from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.transport_encoding import TransportClass


def test_g_node_settings_defaults() -> None:
    settings = GNodeSettings()
    assert settings.rabbit.model_dump() == RabbitBrokerClient().model_dump()
    assert settings.g_node_path == Path("/etc/gridworks/g_node.json")
    assert settings.transport_class == TransportClass.Scada
    assert settings.log_level == "INFO"
    assert (
        settings.rabbit.url.get_secret_value()
        == "amqp://smqPublic:smqPublic@localhost:5672/d1__1"
    )


def test_g_node_settings_env_overrides(monkeypatch, tmp_path) -> None:
    path = tmp_path / "g_node.json"
    monkeypatch.setenv("GNODE_G_NODE_PATH", str(path))
    monkeypatch.setenv("GNODE_TRANSPORT_CLASS", "Supervisor")
    monkeypatch.setenv("GNODE_LOG_LEVEL", "DEBUG")

    settings = GNodeSettings()
    assert settings.g_node_path == path
    assert settings.transport_class == TransportClass.Supervisor
    assert settings.log_level == "DEBUG"
