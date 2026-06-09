import pytest
from pydantic import ValidationError

from gwbase.config import GNodeSettings, ServiceSettings
from gwbase.config.rabbit_settings import RabbitBrokerClient


def test_service_settings_defaults() -> None:
    s = ServiceSettings(service_alias="d1.journal")
    assert s.service_alias == "d1.journal"
    assert s.instance_id is None  # auto-uuid happens in the actor, per boot
    assert s.service_name == "gridworks"
    assert s.log_level == "INFO"
    assert s.log_rotate_bytes == 10_000_000
    assert s.log_rotate_count == 5
    assert s.rabbit.model_dump() == RabbitBrokerClient().model_dump()


def test_service_alias_required_and_typed() -> None:
    # service_alias is required (no default)
    with pytest.raises(ValidationError):
        ServiceSettings()
    # and must be LeftRightDot (lowercase dotted)
    with pytest.raises(ValidationError):
        ServiceSettings(service_alias="Bad.Alias")


def test_service_settings_env_overrides(monkeypatch) -> None:
    monkeypatch.setenv("GWBASE_SERVICE_ALIAS", "d1.env.svc")
    monkeypatch.setenv("GWBASE_SERVICE_NAME", "journalkeeper")
    monkeypatch.setenv("GWBASE_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("GWBASE_LOG_ROTATE_COUNT", "3")
    s = ServiceSettings()
    assert s.service_alias == "d1.env.svc"
    assert s.service_name == "journalkeeper"
    assert s.log_level == "DEBUG"
    assert s.log_rotate_count == 3


def test_gnode_settings_inherits_and_adds_g_node_path() -> None:
    g = GNodeSettings(service_alias="d1.iso.me.scada", service_name="scada")
    # inherits the ServiceSettings shape (GWBASE_ prefix, generic fields)
    assert g.log_rotate_bytes == 10_000_000
    # g_node_path defaults via XDG to ~/.config/gridworks/<service_name>/...
    assert str(g.g_node_path).endswith("gridworks/scada/g.node.gt.json")


def test_gnode_settings_env_override(monkeypatch, tmp_path) -> None:
    path = tmp_path / "g.node.gt.json"
    monkeypatch.setenv("GWBASE_SERVICE_ALIAS", "d1.iso.me.scada")
    monkeypatch.setenv("GWBASE_G_NODE_PATH", str(path))
    g = GNodeSettings()
    assert g.service_alias == "d1.iso.me.scada"
    assert g.g_node_path == path
