import json

import pytest

from gwbase import gridworks_actor
from gwbase.config import GNodeSettings
from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import GNodeGt
from gwbase.transport_encoding import TransportClass
from tests._stubs import GNodeStubRecorder

OLD = "d1.isone.old"
NEW = "d1.isone.renamed"


def _actor(
    make_g_node_json, make_gnode_settings, gnr_url: str | None
) -> GNodeStubRecorder:
    settings = make_gnode_settings(
        make_g_node_json("gn.json", alias=OLD, g_node_class="LeafTransactiveNode"),
        service_alias=OLD,
    )
    settings = settings.model_copy(update={"gnr_url": gnr_url})
    return GNodeStubRecorder(
        settings=settings,
        transport_class=TransportClass.LeafTransactiveNode,
        my_super_alias="d1.super",
        my_time_coordinator_alias="d1.time",
    )


def _renamed(actor: GNodeStubRecorder) -> GNodeGt:
    """The actor's own provisioned record as gnr would answer it after a
    rename: same GNodeId, the new alias, the old one as PrevAlias."""
    assert isinstance(actor.settings, GNodeSettings)
    data = json.loads(actor.settings.g_node_path.read_text())
    data["Alias"] = NEW
    data["PrevAlias"] = OLD
    return GwBaseSemaCodec().from_dict(data, expect=GNodeGt)


def test_reconnect_adopts_the_registry_alias(
    make_g_node_json, make_gnode_settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    actor = _actor(make_g_node_json, make_gnode_settings, "http://gnr.test")
    asked: list[tuple[str, str]] = []

    def fake_get(gnr_url: str, g_node_id: str, timeout_s: float) -> GNodeGt:
        asked.append((gnr_url, g_node_id))
        return _renamed(actor)

    monkeypatch.setattr(gridworks_actor, "get_g_node_by_id", fake_get)
    adder = actor.queue_name.removeprefix(OLD)

    actor.refresh_identity_before_reconnect()

    assert asked == [("http://gnr.test", actor.g_node_id)]
    assert actor.alias == NEW
    assert actor.queue_name == NEW + adder
    assert actor._connect_claims("d1__1").alias == NEW


def test_reconnect_keeps_the_alias_when_gnr_is_silent(
    make_g_node_json, make_gnode_settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    actor = _actor(make_g_node_json, make_gnode_settings, "http://gnr.test")
    monkeypatch.setattr(gridworks_actor, "get_g_node_by_id", lambda *_: None)

    actor.refresh_identity_before_reconnect()

    assert actor.alias == OLD


def test_no_gnr_url_means_no_lookup(
    make_g_node_json, make_gnode_settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    actor = _actor(make_g_node_json, make_gnode_settings, None)

    def boom(*_: object) -> GNodeGt:
        raise AssertionError("gnr must not be asked")

    monkeypatch.setattr(gridworks_actor, "get_g_node_by_id", boom)
    actor.refresh_identity_before_reconnect()
    assert actor.alias == OLD
