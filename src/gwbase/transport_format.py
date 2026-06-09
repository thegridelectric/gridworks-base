"""Wire-grammar string formats for the transport / config layer.

These are the sema-*shaped* string types the transport and settings layers
need (``LeftRightDot`` aliases, ``UUID4Str`` instance ids) WITHOUT importing
the sema codec. The architectural commitment (see
``wiki/gridworks-base/executor/primary.md`` "The central commitment") is a
strict separation between transport and codec: the transport layer is
sema-shape-aware but does not depend on ``gwbase.sema``.

``gwbase.sema.property_format`` is the authority on these formats; the
patterns here mirror it verbatim. Keep the two in sync — the same convention
already governs ``LRH_ALIAS_PATTERN`` in ``transport_encoding.py``.
"""

import re
import uuid
from typing import Annotated

from pydantic import BeforeValidator

# Mirrors gwbase.sema.property_format (the authority). Keep in sync.
LEFT_RIGHT_DOT_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z0-9]+)*$")
UUID4_STR_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def is_left_right_dot(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: LeftRightDot must be a string.")
    if not LEFT_RIGHT_DOT_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails LeftRightDot format.")
    return v


def is_uuid4_str(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: uuid4.str must be a string.")
    if not UUID4_STR_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails uuid4.str format.")
    try:
        u = uuid.UUID(v)
    except Exception as e:
        raise ValueError(f"Invalid UUID4: {v}  <{e}>") from e
    if u.version != 4:  # noqa: PLR2004 — UUID version 4
        raise ValueError(
            f"{v} is valid uid, but of version {u.version}. Fails UuidCanonicalTextual"
        )
    return str(u)


LeftRightDot = Annotated[str, BeforeValidator(is_left_right_dot)]
UUID4Str = Annotated[str, BeforeValidator(is_uuid4_str)]
