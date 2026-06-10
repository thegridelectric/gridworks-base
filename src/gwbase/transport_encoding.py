import re
from dataclasses import dataclass
from enum import StrEnum

# Routing-key token counts per envelope grammar (see executor/transport.md).
_DIRECT_TOKEN_COUNT = 6
_BROADCAST_MIN_TOKEN_COUNT = 4
_WRAPPED_TOKEN_COUNT = 5


class TransportClass(StrEnum):
    """Closed taxonomy of routable classes on the rabbit transport. This
    is NOT Sema vocabulary; in particular ``Supervisor`` is not a member of
    ``gw.g.node.class`` because a Supervisor is not a GNode."""

    TerminalAsset = "TerminalAsset"
    LeafTransactiveNode = "LeafTransactiveNode"
    ConnectivityNode = "ConnectivityNode"
    MarketMaker = "MarketMaker"
    Scada = "Scada"
    PriceForecastService = "PriceForecastService"
    WeatherForecastService = "WeatherForecastService"
    TimeCoordinator = "TimeCoordinator"
    Supervisor = "Supervisor"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]


class RoutingClass(StrEnum):
    # domain-backed
    TerminalAsset = "ta"
    ConnectivityNode = "cn"
    LeafTransactiveNode = "ltn"
    MarketMaker = "mm"
    Scada = "scada"
    PriceForecastService = "price"
    WeatherForecastService = "weather"
    TimeCoordinator = "time"
    # control plane
    Supervisor = "super"


ROUTING_CLASS_BY_TRANSPORT_CLASS: dict[TransportClass, RoutingClass] = {
    TransportClass.TerminalAsset: RoutingClass.TerminalAsset,
    TransportClass.ConnectivityNode: RoutingClass.ConnectivityNode,
    TransportClass.LeafTransactiveNode: RoutingClass.LeafTransactiveNode,
    TransportClass.MarketMaker: RoutingClass.MarketMaker,
    TransportClass.Scada: RoutingClass.Scada,
    TransportClass.PriceForecastService: RoutingClass.PriceForecastService,
    TransportClass.WeatherForecastService: RoutingClass.WeatherForecastService,
    TransportClass.TimeCoordinator: RoutingClass.TimeCoordinator,
    TransportClass.Supervisor: RoutingClass.Supervisor,
}


TRANSPORT_CLASS_BY_ROUTING_CLASS: dict[RoutingClass, TransportClass] = {
    v: k for k, v in ROUTING_CLASS_BY_TRANSPORT_CLASS.items()
}


def transport_class_or_none(token: str) -> TransportClass | None:
    """Best-effort resolve a routing-key class token to its ``TransportClass``.

    Returns ``None`` when the token is not a known long-form ``RoutingClass`` —
    e.g. a proactor **short_name** (``s``=scada, ``a``=atn, ``ws``=weather) that
    rides in the class slot of a current production routing key. Resolution is
    metadata only; delivery and dispatch never depend on it (the message already
    reached this consumer's queue, so its own class is redundant). gwbase MUST
    NOT raise or drop on an unresolved token — see the design
    'must-accept-current-ltn-messages'.
    """
    try:
        return TRANSPORT_CLASS_BY_ROUTING_CLASS[RoutingClass(token)]
    except ValueError:
        return None


class MessageCategory(StrEnum):
    """Defines routing + envelope structure — and how much each kind leans on
    the *class* tokens in its routing key.

    A consumer only ever receives a message because it **subscribed** (bound its
    queue to a matching key); by the time it is dispatched the message is already
    "for me." So a parsed envelope's own class/alias slots are addressing
    **metadata**, not a delivery decision — gwbase resolves them best-effort and
    never drops on an unknown one (design 'must-accept-current-ltn-messages').

    - ``GridworksWrapped`` (``gw``): pub/sub wrapped messages bridged from the
      proactor's MQTT grammar (``gw/<src>/to/<dst>/<type>``). The ``to``-class is
      the **least important** token: it is needed neither for *routing* (the
      topic binding already selected this subscriber) nor for *disambiguating
      between potential partners* (the consumer knows who it is talking to). It
      is just the publisher's peer short_name — a soft hint, not a closed class.
    - ``JsonBroadcast`` (``rjb``): one-to-many; the ``from``-class is likewise a
      short_name hint. Subscribers bind by from-class + type, so the body still
      arrives even when the class token is an unrecognized short form.
    - ``JsonDirect`` (``rj``): point-to-point; class tokens are hints the
      cross-class fabric binds on, but dispatch keys on type + from-alias.
    - ``Serial`` (``s``): reserved.
    """

    JsonDirect = "rj"
    JsonBroadcast = "rjb"
    GridworksWrapped = "gw"
    Serial = "s"  # reserved


class PayloadEncoding(StrEnum):
    """Defines how payload bytes are encoded."""

    Json = "json"
    Binary = "binary"


# ---------------------------------------------------------------------------
# Routing envelopes
#
# ``category`` and ``routing_key`` are properties — derived from each
# envelope subclass's structural fields rather than stored — so a parsed
# envelope and a constructed envelope can use the same dataclass and the
# routing key cannot drift out of sync with its structural fields.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoutingEnvelope:
    type_name: str
    from_alias: str

    @property
    def category(self) -> MessageCategory:
        raise NotImplementedError

    @property
    def routing_key(self) -> str:
        raise NotImplementedError


@dataclass(frozen=True)
class DirectRoutingEnvelope(RoutingEnvelope):
    # Stored structural wire fields are the raw class *tokens* (exactly as they
    # appear on the key — short_name or long form); ``from_class`` / ``to_class``
    # are derived best-effort views (None for an unknown short form).
    from_class_token: str
    to_class_token: str
    to_alias: str

    @classmethod
    def from_classes(
        cls,
        *,
        type_name: str,
        from_alias: str,
        from_class: TransportClass,
        to_class: TransportClass,
        to_alias: str,
    ) -> "DirectRoutingEnvelope":
        """Build-side constructor: emit long-form class tokens from typed classes."""
        return cls(
            type_name=type_name,
            from_alias=from_alias,
            from_class_token=routing_code(from_class),
            to_class_token=routing_code(to_class),
            to_alias=to_alias,
        )

    @property
    def from_class(self) -> TransportClass | None:
        return transport_class_or_none(self.from_class_token)

    @property
    def to_class(self) -> TransportClass | None:
        return transport_class_or_none(self.to_class_token)

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.JsonDirect

    @property
    def routing_key(self) -> str:
        return json_direct_routing_key(
            from_alias=self.from_alias,
            from_class_token=self.from_class_token,
            type_name=self.type_name,
            to_class_token=self.to_class_token,
            to_alias=self.to_alias,
        )


@dataclass(frozen=True)
class BroadcastRoutingEnvelope(RoutingEnvelope):
    # ``from_class_token`` is the raw wire token; ``from_class`` is the derived
    # best-effort view (None for an unknown short form such as ``ws``).
    from_class_token: str
    radio_channel: str | None = None

    @classmethod
    def from_classes(
        cls,
        *,
        type_name: str,
        from_alias: str,
        from_class: TransportClass,
        radio_channel: str | None = None,
    ) -> "BroadcastRoutingEnvelope":
        """Build-side constructor: emit a long-form class token from a typed class."""
        return cls(
            type_name=type_name,
            from_alias=from_alias,
            from_class_token=routing_code(from_class),
            radio_channel=radio_channel,
        )

    @property
    def from_class(self) -> TransportClass | None:
        return transport_class_or_none(self.from_class_token)

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.JsonBroadcast

    @property
    def routing_key(self) -> str:
        return json_broadcast_routing_key(
            from_alias=self.from_alias,
            from_class_token=self.from_class_token,
            type_name=self.type_name,
            radio_channel=self.radio_channel,
        )


@dataclass(frozen=True)
class WrappedRoutingEnvelope(RoutingEnvelope):
    """Routing for a ``gw`` (GridworksWrapped) message.

    ``type_name`` MUST be the **inner** application type name carried in
    ``Gw.Payload.TypeName`` — not the literal string ``"gw"``. The transport
    routes on the inner type so consumers can bind without opening bodies;
    the outer wire object is always a ``gw``. ``wrap_bytes`` /
    ``unwrap_bytes`` enforce that ``Gw.Header.MessageType`` matches the
    payload's ``TypeName``; this envelope's ``type_name`` must match both.
    """

    # ``to_class_token`` is the raw wire token; ``to_class`` is the derived
    # best-effort view. In ``gw`` pub/sub the to-class is the least-important
    # token (see MessageCategory) — an unknown short_name (e.g. ``s``) resolves
    # to None and is never a delivery decision.
    to_class_token: str

    def __post_init__(self) -> None:
        if self.type_name == "gw":
            raise ValueError(
                "WrappedRoutingEnvelope.type_name must be the inner type, "
                "not the outer 'gw' wrapper type"
            )

    @classmethod
    def from_classes(
        cls,
        *,
        type_name: str,
        from_alias: str,
        to_class: TransportClass,
    ) -> "WrappedRoutingEnvelope":
        """Build-side constructor: emit a long-form to-class token from a typed class."""
        return cls(
            type_name=type_name,
            from_alias=from_alias,
            to_class_token=routing_code(to_class),
        )

    @property
    def to_class(self) -> TransportClass | None:
        return transport_class_or_none(self.to_class_token)

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.GridworksWrapped

    @property
    def routing_key(self) -> str:
        return gridworks_wrapped_routing_key(
            from_alias=self.from_alias,
            to_class_token=self.to_class_token,
            type_name=self.type_name,
        )


# ---------------------------------------------------------------------------
# Routing key parsing
# ---------------------------------------------------------------------------


# LRH ("left-right-hyphen") is LeftRightDot with dots replaced by hyphens.
# This pattern mirrors sema's LEFT_RIGHT_DOT_PATTERN
# (gwbase/sema/property_format.py) with `\.` swapped for `-`. Keep the two
# in sync: sema is the authority on the underlying format.
LRH_ALIAS_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def is_lrh_alias_format(candidate: str) -> bool:
    if not isinstance(candidate, str):
        return False
    return LRH_ALIAS_PATTERN.fullmatch(candidate) is not None


def _parse_alias_token(token: str, routing_key: str, field_name: str) -> str:
    if not is_lrh_alias_format(token):
        raise ValueError(
            f"{field_name} {token} in {routing_key} message not lrh_alias_format!",
        )
    return token.replace("-", ".")


def _parse_json_direct_envelope(
    tokens: list[str], routing_key: str
) -> DirectRoutingEnvelope:
    if len(tokens) != _DIRECT_TOKEN_COUNT:
        raise ValueError(f"Expect JsonDirect messages to have 6 words! {routing_key}")
    # Class tokens are stored raw (best-effort resolved later); only the
    # structural arity and the alias/type tokens are validated.
    return DirectRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        from_class_token=tokens[2],
        type_name=_parse_alias_token(tokens[3], routing_key, "TypeName"),
        to_class_token=tokens[4],
        to_alias=_parse_alias_token(tokens[5], routing_key, "ToAlias"),
    )


def _parse_json_broadcast_envelope(
    tokens: list[str], routing_key: str
) -> BroadcastRoutingEnvelope:
    if len(tokens) < _BROADCAST_MIN_TOKEN_COUNT:
        raise ValueError(
            f"Expect JsonBroadcast messages to have at least 4 words! {routing_key}"
        )
    radio_channel: str | None = None
    if len(tokens) > _BROADCAST_MIN_TOKEN_COUNT:
        radio_channel = ".".join(tokens[_BROADCAST_MIN_TOKEN_COUNT:])
    return BroadcastRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        from_class_token=tokens[2],
        type_name=_parse_alias_token(tokens[3], routing_key, "TypeName"),
        radio_channel=radio_channel,
    )


def _parse_scada_wrapped_envelope(
    tokens: list[str], routing_key: str
) -> WrappedRoutingEnvelope:
    if len(tokens) != _WRAPPED_TOKEN_COUNT:
        raise ValueError(f"Wrapped messages must have 5 words! {routing_key}")
    if tokens[2] != "to":
        raise ValueError(f"Wrapped messages with 5 words must use 'to'! {routing_key}")
    return WrappedRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        type_name=_parse_alias_token(tokens[4], routing_key, "TypeName"),
        to_class_token=tokens[3],
    )


def parse_routing_key(routing_key: str) -> RoutingEnvelope:
    tokens = routing_key.split(".")
    if not tokens or not tokens[0]:
        raise ValueError(f"Empty routing key category in {routing_key}!")

    try:
        category = MessageCategory(tokens[0])
    except ValueError as e:
        raise ValueError(
            f"First word of {routing_key} not a known MessageCategory!",
        ) from e

    if category == MessageCategory.JsonDirect:
        return _parse_json_direct_envelope(tokens, routing_key)
    if category == MessageCategory.JsonBroadcast:
        return _parse_json_broadcast_envelope(tokens, routing_key)
    if category == MessageCategory.GridworksWrapped:
        return _parse_scada_wrapped_envelope(tokens, routing_key)
    raise ValueError(f"Rabbit messages do not handle {category.value}")


# ---------------------------------------------------------------------------
# Routing-key construction helpers
# ---------------------------------------------------------------------------


def routing_code(transport_class: TransportClass) -> str:
    return ROUTING_CLASS_BY_TRANSPORT_CLASS[transport_class].value


def json_direct_routing_key(
    *,
    from_alias: str,
    from_class_token: str,
    type_name: str,
    to_class_token: str,
    to_alias: str,
) -> str:
    return ".".join([
        MessageCategory.JsonDirect.value,
        from_alias.replace(".", "-"),
        from_class_token,
        type_name.replace(".", "-"),
        to_class_token,
        to_alias.replace(".", "-"),
    ])


def json_broadcast_routing_key(
    *,
    from_alias: str,
    from_class_token: str,
    type_name: str,
    radio_channel: str | None = None,
) -> str:
    parts = [
        MessageCategory.JsonBroadcast.value,
        from_alias.replace(".", "-"),
        from_class_token,
        type_name.replace(".", "-"),
    ]
    if radio_channel:
        parts.append(radio_channel)
    return ".".join(parts)


def gridworks_wrapped_routing_key(
    *,
    from_alias: str,
    to_class_token: str,
    type_name: str,
) -> str:
    return ".".join([
        MessageCategory.GridworksWrapped.value,
        from_alias.replace(".", "-"),
        "to",
        to_class_token,
        type_name.replace(".", "-"),
    ])
