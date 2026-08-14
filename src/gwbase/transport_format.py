"""Wire-grammar string formats for the transport / config layer.

These are the sema-*shaped* string types the transport and settings layers
need (``LeftRightDot`` aliases, ``UUID4Str`` instance ids) WITHOUT importing
the sema codec. The architectural commitment is a
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
UNIVERSE_RUN_PATTERN = re.compile(r"^[a-z][a-z0-9]*__[1-9][0-9]*$")
UNIVERSE_PATTERN = re.compile(r"^[a-z][a-z0-9]*$")


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


def is_universe_run(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: universe.run must be a string.")
    if not UNIVERSE_RUN_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails universe.run format.")
    return v


def is_universe(v: str) -> str:
    """A universe token, constrained to the kinds on the universe ladder
    (gnr executor "Universes"): d-kind (dev — localhost comms only), h-kind
    (hybrid), or exactly ``w`` — the single production universe. No sema
    word carries the kind constraint yet; a ``universe`` format would
    retire this validator.
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: universe must be a string.")
    if not UNIVERSE_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails universe token format.")
    if not (v.startswith(("d", "h")) or v == "w"):
        raise ValueError(
            f"<{v}>: unknown universe kind — a universe starts with 'd' (dev) "
            f"or 'h' (hybrid), or is exactly 'w' (production)."
        )
    return v


def universe_of(run: str) -> str:
    """The universe token of a ``universe.run`` value (``hw1__1`` -> ``hw1``)."""
    return is_universe(is_universe_run(run).split("__", 1)[0])


LeftRightDot = Annotated[str, BeforeValidator(is_left_right_dot)]
UUID4Str = Annotated[str, BeforeValidator(is_uuid4_str)]
UniverseRun = Annotated[str, BeforeValidator(is_universe_run)]
Universe = Annotated[str, BeforeValidator(is_universe)]
