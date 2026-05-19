import re
from dataclasses import dataclass
from enum import StrEnum


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


class MessageCategory(StrEnum):
    """Defines routing + envelope structure."""

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
    from_class: TransportClass
    to_class: TransportClass
    to_alias: str

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.JsonDirect

    @property
    def routing_key(self) -> str:
        return json_direct_routing_key(
            from_alias=self.from_alias,
            from_class=self.from_class,
            type_name=self.type_name,
            to_class=self.to_class,
            to_alias=self.to_alias,
        )


@dataclass(frozen=True)
class BroadcastRoutingEnvelope(RoutingEnvelope):
    from_class: TransportClass
    radio_channel: str | None = None

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.JsonBroadcast

    @property
    def routing_key(self) -> str:
        return json_broadcast_routing_key(
            from_alias=self.from_alias,
            from_class=self.from_class,
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

    to_class: TransportClass

    def __post_init__(self) -> None:
        if self.type_name == "gw":
            raise ValueError(
                "WrappedRoutingEnvelope.type_name must be the inner type, "
                "not the outer 'gw' wrapper type"
            )

    @property
    def category(self) -> MessageCategory:
        return MessageCategory.GridworksWrapped

    @property
    def routing_key(self) -> str:
        return gridworks_wrapped_routing_key(
            from_alias=self.from_alias,
            to_class=self.to_class,
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


def _parse_routing_class_token(token: str, routing_key: str) -> RoutingClass:
    try:
        return RoutingClass(token)
    except ValueError as e:
        raise ValueError(
            f"Unknown routing class {token} in {routing_key}. "
            f"Must belong to {[x.value for x in RoutingClass]}"
        ) from e


def _parse_transport_class_token(token: str, routing_key: str) -> TransportClass:
    routing_class = _parse_routing_class_token(token, routing_key)
    return TRANSPORT_CLASS_BY_ROUTING_CLASS[routing_class]


def _parse_json_direct_envelope(
    tokens: list[str], routing_key: str
) -> DirectRoutingEnvelope:
    if len(tokens) != 6:
        raise ValueError(f"Expect JsonDirect messages to have 6 words! {routing_key}")
    return DirectRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        from_class=_parse_transport_class_token(tokens[2], routing_key),
        type_name=_parse_alias_token(tokens[3], routing_key, "TypeName"),
        to_class=_parse_transport_class_token(tokens[4], routing_key),
        to_alias=_parse_alias_token(tokens[5], routing_key, "ToAlias"),
    )


def _parse_json_broadcast_envelope(
    tokens: list[str], routing_key: str
) -> BroadcastRoutingEnvelope:
    if len(tokens) < 4:
        raise ValueError(
            f"Expect JsonBroadcast messages to have at least 4 words! {routing_key}"
        )
    radio_channel: str | None = None
    if len(tokens) > 4:
        radio_channel = ".".join(tokens[4:])
    return BroadcastRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        from_class=_parse_transport_class_token(tokens[2], routing_key),
        type_name=_parse_alias_token(tokens[3], routing_key, "TypeName"),
        radio_channel=radio_channel,
    )


def _parse_scada_wrapped_envelope(
    tokens: list[str], routing_key: str
) -> WrappedRoutingEnvelope:
    if len(tokens) != 5:
        raise ValueError(f"Wrapped messages must have 5 words! {routing_key}")
    if tokens[2] != "to":
        raise ValueError(f"Wrapped messages with 5 words must use 'to'! {routing_key}")
    return WrappedRoutingEnvelope(
        from_alias=_parse_alias_token(tokens[1], routing_key, "FromAlias"),
        type_name=_parse_alias_token(tokens[4], routing_key, "TypeName"),
        to_class=_parse_transport_class_token(tokens[3], routing_key),
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
    from_class: TransportClass,
    type_name: str,
    to_class: TransportClass,
    to_alias: str,
) -> str:
    return ".".join(
        [
            MessageCategory.JsonDirect.value,
            from_alias.replace(".", "-"),
            routing_code(from_class),
            type_name.replace(".", "-"),
            routing_code(to_class),
            to_alias.replace(".", "-"),
        ]
    )


def json_broadcast_routing_key(
    *,
    from_alias: str,
    from_class: TransportClass,
    type_name: str,
    radio_channel: str | None = None,
) -> str:
    parts = [
        MessageCategory.JsonBroadcast.value,
        from_alias.replace(".", "-"),
        routing_code(from_class),
        type_name.replace(".", "-"),
    ]
    if radio_channel:
        parts.append(radio_channel)
    return ".".join(parts)


def gridworks_wrapped_routing_key(
    *,
    from_alias: str,
    to_class: TransportClass,
    type_name: str,
) -> str:
    return ".".join(
        [
            MessageCategory.GridworksWrapped.value,
            from_alias.replace(".", "-"),
            "to",
            routing_code(to_class),
            type_name.replace(".", "-"),
        ]
    )
