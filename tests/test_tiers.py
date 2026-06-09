"""Showcase: the three actor tiers and what each one is for.

These are broker-free, construction-only tests — they document the
``ActorBase`` -> ``Orchestrator`` -> ``GridworksActor`` hierarchy introduced
to let non-GNode services ride gwbase without faking a GNode identity. Read
top-to-bottom as a tour of the new capability.

  - ActorBase    : a passive ear-tap. ServiceSettings, NO g.node.gt.json,
                   consumes ear_tx, cannot class-route.
  - Orchestrator : adds class-routing (a transport_class) + the heartbeat /
                   sim-timestep rhythm. Used by Supervisor / TimeCoordinator,
                   which are NOT GNodes.
  - GridworksActor : adds Sema-validated GNode identity (g.node.gt.json).
"""

import json
import uuid
from pathlib import Path

import pytest

from gwbase import (
    ActorBase,
    GNodeSettings,
    GridworksActor,
    OnSendMessageDiagnostic,
    Orchestrator,
    ServiceSettings,
)
from gwbase.transport_encoding import (
    DirectRoutingEnvelope,
    TransportClass,
    WrappedRoutingEnvelope,
)

# --- minimal concrete subclasses for each tier ---------------------------


class _Tap(ActorBase):
    """A bare ear-tap: implements dispatch_message directly (no control plane)."""

    def dispatch_message(self, *, envelope, body) -> None:  # noqa: ARG002
        return


class _Orch(Orchestrator):
    def process_message(self, *, envelope, body) -> None:  # noqa: ARG002
        return


class _GNode(GridworksActor):
    def process_message(self, *, envelope, body) -> None:  # noqa: ARG002
        return


# --- the hierarchy -------------------------------------------------------


def test_inheritance_chain_is_linear() -> None:
    """GridworksActor *is an* Orchestrator *is an* ActorBase — not siblings."""
    assert GridworksActor.__mro__[:3] == (GridworksActor, Orchestrator, ActorBase)
    assert issubclass(Orchestrator, ActorBase)
    assert issubclass(GridworksActor, Orchestrator)


# --- Tier 1: ActorBase as a passive ear-tap ------------------------------


def test_tap_rides_service_settings_with_no_gnode_file() -> None:
    """The core win: a non-GNode service constructs with ServiceSettings and
    NO g.node.gt.json on disk. (Journalkeeper no longer fakes one.)"""
    tap = _Tap(
        settings=ServiceSettings(
            service_alias="d1.journal", service_name="journalkeeper"
        )
    )
    assert tap.alias == "d1.journal"
    # identity comes from settings; there is no GNode identity at all
    assert not hasattr(tap, "g_node_id")
    assert not hasattr(tap, "transport_class")


def test_tap_consumes_ear_tx_and_has_no_publish_exchange() -> None:
    tap = _Tap(settings=ServiceSettings(service_alias="d1.journal"))
    assert tap._consume_exchange == "ear_tx"
    assert tap._publish_exchange is None


def test_tap_can_send_wrapped_but_not_direct() -> None:
    """A tap may emit wrapped (gw -> amq.topic) but cannot class-route: a
    Direct send returns NO_PUBLISH_EXCHANGE rather than silently dropping."""
    tap = _Tap(settings=ServiceSettings(service_alias="d1.journal"))
    tap._stopped = False  # past the lifecycle guard; channel is still closed

    direct = DirectRoutingEnvelope(
        type_name="hb.a",
        from_alias="d1.journal",
        from_class=TransportClass.Supervisor,
        to_class=TransportClass.Supervisor,
        to_alias="d1.super",
    )
    assert tap.send(envelope=direct, body=b"{}") == (
        OnSendMessageDiagnostic.NO_PUBLISH_EXCHANGE
    )

    # Wrapped is allowed: it targets amq.topic, not a class mic_tx. With no
    # open channel it reports CHANNEL_NOT_OPEN — crucially NOT
    # NO_PUBLISH_EXCHANGE, proving the wrapped path is available to a tap.
    wrapped = WrappedRoutingEnvelope(
        type_name="hb.a", from_alias="d1.journal", to_class=TransportClass.Scada
    )
    assert tap.send(envelope=wrapped, body=b"{}") == (
        OnSendMessageDiagnostic.CHANNEL_NOT_OPEN
    )


def test_tap_handshake_is_service_only() -> None:
    """FIS handshake for a non-GNode: ServiceAlias + ServiceInstanceId, and
    crucially NO GNodeClass (the discriminator that says 'I am a GNode')."""
    tap = _Tap(settings=ServiceSettings(service_alias="d1.journal"))
    props = tap._client_properties()
    assert set(props) == {"ServiceAlias", "ServiceInstanceId"}
    assert props["ServiceAlias"] == "d1.journal"


# --- Tier 2: Orchestrator class-routes without GNode identity -------------


def test_orchestrator_class_routes_without_a_gnode_file() -> None:
    """Supervisor / TimeCoordinator shape: ServiceSettings (no g.node.gt.json),
    but a transport_class so it consumes/publishes on its class exchanges."""
    orch = _Orch(
        settings=ServiceSettings(service_alias="d1.super"),
        transport_class=TransportClass.Supervisor,
        my_super_alias="d1.super.parent",
        my_time_coordinator_alias="d1.time",
    )
    assert orch.transport_class == TransportClass.Supervisor
    assert orch._consume_exchange == "super_tx"
    assert orch._publish_exchange == "supermic_tx"
    assert not hasattr(orch, "g_node_id")  # still not a GNode


# --- Tier 3: GridworksActor validates GNode identity at the boundary ------


def _write_scada(tmp: Path, alias: str = "d1.iso.me.scada") -> Path:
    p = tmp / "g.node.gt.json"
    p.write_text(
        json.dumps({
            "GNodeId": str(uuid.uuid4()),
            "Alias": alias,
            "BaseClass": "Scada",
            "GNodeClass": "Scada",
            "Status": "Active",
            "PositionPointId": str(uuid.uuid4()),
            "TypeName": "g.node.gt",
            "Version": "004",
        })
    )
    return p


def _scada(path: Path, service_alias: str) -> _GNode:
    return _GNode(
        settings=GNodeSettings(
            service_alias=service_alias, service_name="scada", g_node_path=path
        ),
        transport_class=TransportClass.Scada,
        my_super_alias="d1.super",
        my_time_coordinator_alias="d1.time",
    )


def test_gridworks_actor_loads_validated_identity(tmp_path) -> None:
    path = _write_scada(tmp_path)
    actor = _scada(path, service_alias="d1.iso.me.scada")
    assert actor.g_node_class == "Scada"
    # handshake now carries the GNodeClass discriminator
    assert actor._client_properties()["GNodeClass"] == "Scada"
    # back-compat aliases still resolve for existing callers
    assert actor.g_node_alias == actor.alias
    assert actor.g_node_instance_id == actor.instance_id


def test_provisioning_drift_fails_at_boot(tmp_path) -> None:
    """If the file's Alias disagrees with settings.service_alias, boot fails
    loudly instead of surfacing a mismatch mid-run."""
    path = _write_scada(tmp_path, alias="d1.iso.me.scada")
    with pytest.raises(ValueError, match="drift"):
        _scada(path, service_alias="d1.other.scada")


def test_malformed_gnode_file_fails_sema_validation(tmp_path) -> None:
    """A typo'd / incomplete g.node.gt.json (here: GNodeClass=Scada but no
    .scada suffix — Axiom 5) is rejected at the boundary, not accepted as
    three untyped strings the way the old ActorBase did."""
    p = tmp_path / "g.node.gt.json"
    p.write_text(
        json.dumps({
            "GNodeId": str(uuid.uuid4()),
            "Alias": "d1.iso.me",  # missing the required .scada suffix
            "BaseClass": "Scada",
            "GNodeClass": "Scada",
            "Status": "Active",
            "PositionPointId": str(uuid.uuid4()),
            "TypeName": "g.node.gt",
            "Version": "004",
        })
    )
    with pytest.raises(ValueError, match="Sema validation"):
        _scada(p, service_alias="d1.iso.me")


def test_missing_gnode_file_fails_with_clear_message(tmp_path) -> None:
    with pytest.raises(ValueError, match="provision"):
        _scada(tmp_path / "does-not-exist.json", service_alias="d1.iso.me.scada")
