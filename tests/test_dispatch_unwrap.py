"""``Orchestrator.dispatch_message`` opens a ``gw`` envelope before the
application sees it: a wrapped body reaches ``process_message`` as the
bare inner sema JSON with its ``GridworksHeader``; a bare ``rj`` / ``rjb``
body reaches it unchanged with no header; a wrapped body that does not
unwrap, or whose header disagrees with the routing key, is dropped at the
framework. Broker-free: the actor is constructed and ``dispatch_message``
is called directly."""

import json
import logging

import pytest

from gwbase import Orchestrator, ServiceSettings
from gwbase.sema.types import HeartbeatA
from gwbase.sema.types.gridworks_header import GridworksHeader
from gwbase.transport_encoding import (
    BroadcastRoutingEnvelope,
    RoutingEnvelope,
    TransportClass,
    WrappedRoutingEnvelope,
    parse_routing_key,
)
from gwbase.wrapped import wrap_bytes

SCADA = "d1.isone.me.versant.keene.beech.scada"
SUPER = "d1.super"
INNER = {"TypeName": "report.event", "Src": SCADA, "Version": "004"}


class _Recorder(Orchestrator):
    def __init__(self) -> None:
        super().__init__(
            settings=ServiceSettings(service_alias="d1.alerts"),
            transport_class=TransportClass.Supervisor,
            my_super_alias=SUPER,
            my_time_coordinator_alias="d1.time",
        )
        self.seen: list[tuple[RoutingEnvelope, bytes, GridworksHeader | None]] = []

    def process_message(
        self,
        *,
        envelope: RoutingEnvelope,
        body: bytes,
        header: GridworksHeader | None,
    ) -> None:
        self.seen.append((envelope, body, header))


def wrapped_envelope(type_name: str, src: str = SCADA) -> WrappedRoutingEnvelope:
    envelope = WrappedRoutingEnvelope.from_classes(
        type_name=type_name, from_alias=src, to_class=TransportClass.Supervisor
    )
    parsed = parse_routing_key(envelope.routing_key)
    assert isinstance(parsed, WrappedRoutingEnvelope)
    return parsed


def test_wrapped_body_arrives_bare_with_its_header() -> None:
    actor = _Recorder()
    body = wrap_bytes(
        src=SCADA,
        dst="d1.alerts",
        inner_type_name="report.event",
        inner_payload_dict=INNER,
        ack_required=True,
    )
    actor.dispatch_message(envelope=wrapped_envelope("report.event"), body=body)

    [(envelope, seen_body, header)] = actor.seen
    assert envelope.type_name == "report.event"
    assert json.loads(seen_body) == INNER
    assert isinstance(header, GridworksHeader)
    assert header.src == SCADA
    assert header.dst == "d1.alerts"
    assert header.ack_required is True


def test_bare_broadcast_arrives_unchanged_with_no_header() -> None:
    actor = _Recorder()
    envelope = BroadcastRoutingEnvelope.from_classes(
        type_name="g.node.forest",
        from_alias="d1.gnr",
        from_class=TransportClass.Supervisor,
        radio_channel="d1.isone",
    )
    body = json.dumps({"TypeName": "g.node.forest", "Nodes": []}).encode()
    actor.dispatch_message(envelope=envelope, body=body)

    [(seen_envelope, seen_body, header)] = actor.seen
    assert seen_envelope is envelope
    assert seen_body == body
    assert header is None


@pytest.mark.parametrize(
    "body",
    [
        b"not json",
        json.dumps(INNER).encode(),  # bare body on a gw key
        json.dumps({"TypeName": "gw", "Header": {}}).encode(),  # no Payload
    ],
)
def test_wrapped_body_that_does_not_unwrap_is_dropped(body: bytes, caplog) -> None:
    actor = _Recorder()
    with caplog.at_level(logging.ERROR, logger="gwbase.orchestrator"):
        actor.dispatch_message(envelope=wrapped_envelope("report.event"), body=body)
    assert actor.seen == []
    assert "Dropped wrapped report.event" in caplog.text


def test_header_that_disagrees_with_the_routing_key_is_dropped(caplog) -> None:
    actor = _Recorder()
    body = wrap_bytes(
        src=SCADA,
        dst="d1.alerts",
        inner_type_name="report.event",
        inner_payload_dict=INNER,
    )
    with caplog.at_level(logging.ERROR, logger="gwbase.orchestrator"):
        actor.dispatch_message(envelope=wrapped_envelope("layout.lite"), body=body)
    assert actor.seen == []
    assert "disagrees with the routing key" in caplog.text


def test_wrapped_heartbeat_from_a_subordinate_reaches_the_application() -> None:
    """Control-plane routing runs after the unwrap: a subordinate's wrapped
    heartbeat.a still falls through to process_message, bare, with header."""
    actor = _Recorder()
    ping = HeartbeatA(my_hex="0", your_last_hex="a")
    body = wrap_bytes(
        src=SCADA,
        dst="d1.alerts",
        inner_type_name=ping.type_name,
        inner_payload_dict=ping.to_dict(),
    )
    actor.dispatch_message(envelope=wrapped_envelope(ping.type_name), body=body)

    [(envelope, seen_body, header)] = actor.seen
    assert envelope.type_name == "heartbeat.a"
    assert HeartbeatA.from_dict(json.loads(seen_body)) == ping
    assert header is not None and header.src == SCADA
