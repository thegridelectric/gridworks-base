"""Unit tests for the `gw` application envelope wrap/unwrap helpers."""

import json
import uuid

import pytest

from gwbase.sema.types import HeartbeatA
from gwbase.sema.types.gridworks_header import GridworksHeader
from gwbase.sema.wrapped import unwrap_bytes, wrap_bytes
from gwbase.transport_encoding import (
    TransportClass,
    WrappedRoutingEnvelope,
    parse_routing_key,
)


def test_wrap_unwrap_round_trip() -> None:
    inner = HeartbeatA(my_hex="0", your_last_hex="a")
    mid = str(uuid.uuid4())

    body = wrap_bytes(
        src="d1.source",
        dst="d1.scada1",
        inner_type_name=inner.type_name,
        inner_payload_dict=inner.to_dict(),
        message_id=mid,
        ack_required=True,
    )

    # Wire shape
    parsed = json.loads(body)
    assert parsed["TypeName"] == "gw"
    assert parsed["Header"]["TypeName"] == "gridworks.header"
    assert parsed["Header"]["MessageType"] == "heartbeat.a"
    assert parsed["Header"]["MessageId"] == mid
    assert parsed["Header"]["AckRequired"] is True
    assert parsed["Payload"]["TypeName"] == "heartbeat.a"

    # Round trip
    header, payload_dict = unwrap_bytes(body)
    assert isinstance(header, GridworksHeader)
    assert header.message_type == "heartbeat.a"
    assert header.src == "d1.source"
    assert header.dst == "d1.scada1"
    assert payload_dict["TypeName"] == "heartbeat.a"

    # Inner can be re-decoded by a SemaType directly — no codec required
    inner_back = HeartbeatA.from_dict(payload_dict)
    assert inner_back == inner


def test_wrap_generates_message_id_when_omitted() -> None:
    body = wrap_bytes(
        src="d1.source",
        dst="d1.scada1",
        inner_type_name="heartbeat.a",
        inner_payload_dict={"TypeName": "heartbeat.a", "MyHex": "0", "YourLastHex": "a", "Version": "101"},
    )
    header, _ = unwrap_bytes(body)
    uuid.UUID(header.message_id, version=4)  # raises if not a UUID4


def test_wrap_rejects_payload_typename_mismatch() -> None:
    with pytest.raises(ValueError, match="does not match inner_type_name"):
        wrap_bytes(
            src="d1.a",
            dst="d1.b",
            inner_type_name="heartbeat.a",
            inner_payload_dict={"TypeName": "wrong.type", "MyHex": "0", "YourLastHex": "a", "Version": "101"},
        )


def test_wrap_rejects_missing_payload_typename() -> None:
    with pytest.raises(ValueError, match="missing TypeName"):
        wrap_bytes(
            src="d1.a",
            dst="d1.b",
            inner_type_name="heartbeat.a",
            inner_payload_dict={"MyHex": "0"},
        )


def test_unwrap_rejects_non_gw_outer() -> None:
    body = json.dumps(
        {"TypeName": "heartbeat.a", "MyHex": "0", "YourLastHex": "a", "Version": "101"}
    ).encode()
    with pytest.raises(ValueError, match="Expected TypeName 'gw'"):
        unwrap_bytes(body)


def test_unwrap_rejects_header_payload_type_mismatch() -> None:
    # Hand-craft a body whose Header.MessageType disagrees with Payload.TypeName.
    body = json.dumps(
        {
            "TypeName": "gw",
            "Header": {
                "TypeName": "gridworks.header",
                "Version": "001",
                "Src": "d1.a",
                "Dst": "d1.b",
                "MessageType": "heartbeat.a",
                "MessageId": str(uuid.uuid4()),
                "AckRequired": False,
            },
            "Payload": {"TypeName": "other.type", "Foo": 1},
        }
    ).encode()
    with pytest.raises(ValueError, match="does not match payload TypeName"):
        unwrap_bytes(body)


def test_wrapped_routing_envelope_rejects_gw_as_type_name() -> None:
    with pytest.raises(ValueError, match="must be the inner type"):
        WrappedRoutingEnvelope(
            type_name="gw",
            from_alias="d1.source",
            to_class=TransportClass.Scada,
        )


def test_wrapped_routing_envelope_carries_inner_type_name() -> None:
    env = WrappedRoutingEnvelope(
        type_name="heartbeat.a",
        from_alias="d1.source",
        to_class=TransportClass.Scada,
    )
    assert env.routing_key == "gw.d1-source.to.scada.heartbeat-a"

    parsed = parse_routing_key(env.routing_key)
    assert isinstance(parsed, WrappedRoutingEnvelope)
    assert parsed.type_name == "heartbeat.a"
    assert parsed.to_class == TransportClass.Scada
