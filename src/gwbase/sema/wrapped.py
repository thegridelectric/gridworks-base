"""Pure helpers for the ``gw`` application envelope.

A ``gw`` body is a JSON object with a ``Header`` (validated against
``GridworksHeader``) and a ``Payload`` (an opaque PascalCase dict whose
``TypeName`` must match ``Header.MessageType``). These helpers do NOT
depend on a SemaCodec registry — the inner payload is treated as bytes-
adjacent data and decoded later by whichever codec the application owns.

Wire form::

    {
        "TypeName": "gw",
        "Header":   { GridworksHeader fields },
        "Payload":  { "TypeName": "<inner>", ... }
    }
"""

import json
import uuid
from gwbase.sema.types.gridworks_header import GridworksHeader
from gwbase.sema.property_format import LeftRightDot, UUID4Str


def wrap_bytes(
    *,
    src: LeftRightDot,
    dst: LeftRightDot,
    inner_type_name: str,
    inner_payload_dict: dict,
    message_id: UUID4Str | None = None,
    ack_required: bool = False,
) -> bytes:
    """Build a ``gw`` envelope around ``inner_payload_dict`` and return its
    JSON-encoded bytes. ``inner_payload_dict`` must be PascalCase and carry
    a ``TypeName`` matching ``inner_type_name``."""
    if "TypeName" not in inner_payload_dict:
        raise ValueError("inner_payload_dict missing TypeName")
    if inner_payload_dict["TypeName"] != inner_type_name:
        raise ValueError(
            f"inner_payload_dict TypeName {inner_payload_dict['TypeName']!r} "
            f"does not match inner_type_name {inner_type_name!r}"
        )
    if not message_id:
        message_id = str(uuid.uuid4())

    header = GridworksHeader(
        src=src,
        dst=dst,
        message_type=inner_type_name,
        message_id=message_id,
        ack_required=ack_required,
    )
    envelope = {
        "TypeName": "gw",
        "Header": header.to_dict(),
        "Payload": dict(inner_payload_dict),
    }
    return json.dumps(envelope).encode()


def unwrap_bytes(body: bytes) -> tuple[GridworksHeader, dict]:
    """Parse a ``gw`` envelope. Returns ``(header, inner_payload_dict)`` and
    asserts ``header.message_type == payload['TypeName']``."""
    try:
        d = json.loads(body)
    except Exception as e:
        raise ValueError(f"Invalid JSON: {e}") from e
    if not isinstance(d, dict):
        raise ValueError("gw body must be a JSON object")
    if d.get("TypeName") != "gw":
        raise ValueError(f"Expected TypeName 'gw', got {d.get('TypeName')!r}")
    if "Header" not in d or "Payload" not in d:
        raise ValueError("gw body missing Header or Payload")
    header = GridworksHeader.from_dict(d["Header"])
    payload = d["Payload"]
    if not isinstance(payload, dict):
        raise ValueError("gw Payload must be a JSON object")
    inner_type = payload.get("TypeName")
    if header.message_type != inner_type:
        raise ValueError(
            f"gw header.message_type {header.message_type!r} does not match "
            f"payload TypeName {inner_type!r}"
        )
    return header, payload
