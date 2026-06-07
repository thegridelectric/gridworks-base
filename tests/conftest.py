"""Shared pytest fixtures for gridworks-base tests."""

import json
import uuid
from pathlib import Path
from typing import Callable

import pytest

from gwbase.config import GNodeSettings, ServiceSettings
from gwbase.config.rabbit_settings import RabbitBrokerClient

# GNodeClass values that ARE base.g.node.class members → Physical GNodes
# (BaseClass == GNodeClass, PositionPointId required per Axiom 1a/2).
_PHYSICAL_CLASSES = frozenset({
    "TerminalAsset",
    "LeafTransactiveNode",
    "ConnectivityNode",
    "MarketMaker",
})


@pytest.fixture(autouse=True)
def _xdg_under_tmp(tmp_path_factory, monkeypatch) -> None:
    """Redirect the XDG base dirs under a tmp dir so per-actor loggers and the
    g.node.gt.json default path never touch the real home directory."""
    base = tmp_path_factory.mktemp("xdg")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(base / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(base / "data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(base / "state"))


@pytest.fixture
def make_g_node_json(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that writes a VALID ``g.node.gt/004`` JSON to tmp_path.

    The written file passes Sema validation (axioms 1–5), so it can drive a
    real ``GridworksActor`` boundary. A Physical GNodeClass gets a matching
    BaseClass + a PositionPointId; anything else is treated as Logical.

    Usage::

        path = make_g_node_json(alias="d1.test", g_node_class="LeafTransactiveNode")
    """

    def _write(
        filename: str = "g.node.gt.json",
        *,
        alias: str,
        g_node_id: str | None = None,
        g_node_class: str = "LeafTransactiveNode",
        status: str = "Active",
    ) -> Path:
        path = tmp_path / filename
        data = {
            "GNodeId": g_node_id or str(uuid.uuid4()),
            "Alias": alias,
            "GNodeClass": g_node_class,
            "Status": status,
            "TypeName": "g.node.gt",
            "Version": "004",
        }
        if g_node_class in _PHYSICAL_CLASSES:
            data["BaseClass"] = g_node_class
            data["PositionPointId"] = str(uuid.uuid4())
        else:
            data["BaseClass"] = "Logical"
        path.write_text(json.dumps(data))
        return path

    return _write


@pytest.fixture
def make_gnode_settings() -> Callable[..., GNodeSettings]:
    """Build GNodeSettings for a GNode actor. ``service_alias`` MUST match the
    g.node.gt.json's Alias (GridworksActor enforces the binding at boot)."""

    def _build(
        g_node_path: Path,
        *,
        service_alias: str,
        rabbit: RabbitBrokerClient | None = None,
    ) -> GNodeSettings:
        return GNodeSettings(
            service_alias=service_alias,
            g_node_path=g_node_path,
            rabbit=rabbit or RabbitBrokerClient(),
        )

    return _build


@pytest.fixture
def make_service_settings() -> Callable[..., ServiceSettings]:
    """Build ServiceSettings for a non-GNode actor (tap or Orchestrator) —
    no g.node.gt.json needed."""

    def _build(
        *,
        service_alias: str,
        rabbit: RabbitBrokerClient | None = None,
    ) -> ServiceSettings:
        return ServiceSettings(
            service_alias=service_alias,
            rabbit=rabbit or RabbitBrokerClient(),
        )

    return _build
