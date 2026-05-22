"""Shared pytest fixtures for gridworks-base tests."""

import json
import uuid
from pathlib import Path
from typing import Callable

import pytest

from gwbase.config import GNodeSettings
from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.transport_encoding import TransportClass


@pytest.fixture
def make_g_node_json(tmp_path: Path) -> Callable[..., Path]:
    """Return a factory that writes a g.node.gt/004 JSON to tmp_path.

    Usage::

        def test_foo(make_g_node_json):
            path = make_g_node_json("g_node.json", alias="d1.test")
    """

    def _write(
        filename: str = "g_node.json",
        *,
        alias: str,
        g_node_id: str | None = None,
        g_node_class: str = "Scada",
        base_class: str = "Logical",
        status: str = "Active",
    ) -> Path:
        path = tmp_path / filename
        data = {
            "GNodeId": g_node_id or str(uuid.uuid4()),
            "Alias": alias,
            "BaseClass": base_class,
            "GNodeClass": g_node_class,
            "Status": status,
            "TypeName": "g.node.gt",
            "Version": "004",
        }
        path.write_text(json.dumps(data))
        return path

    return _write


@pytest.fixture
def make_settings() -> Callable[..., GNodeSettings]:
    """Return a factory that builds GNodeSettings for a given g_node JSON."""

    def _build(
        g_node_path: Path,
        *,
        transport_class: TransportClass = TransportClass.Scada,
        rabbit: RabbitBrokerClient | None = None,
    ) -> GNodeSettings:
        return GNodeSettings(
            g_node_path=g_node_path,
            transport_class=transport_class,
            rabbit=rabbit or RabbitBrokerClient(),
        )

    return _build
