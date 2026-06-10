"""Tolerant parsing of current-production routing keys whose class slot is a
proactor **short_name** (e.g. ``s``=scada, ``ws``=weather) rather than a
gwbase long-form ``RoutingClass``.

Regression guard for the silent-data-loss bug fixed by the design
'must-accept-current-ltn-messages': gwbase MUST parse (not drop) these keys,
resolving the unknown class token to ``None`` best-effort while preserving the
exact wire key on round-trip.
"""

import pytest

from gwbase.transport_encoding import (
    BroadcastRoutingEnvelope,
    DirectRoutingEnvelope,
    TransportClass,
    WrappedRoutingEnvelope,
    parse_routing_key,
    transport_class_or_none,
)

# Verbatim from the 2026-05-27 production survey (design doc).
PROD_WRAPPED_TO_SCADA = "gw.hw1-isone-me-versant-keene-beech.to.s.gridworks-ping"
PROD_WEATHER_BROADCAST = "rjb.hw1-isone-ws.ws.weather"


def test_transport_class_or_none_resolves_long_form() -> None:
    assert transport_class_or_none("scada") is TransportClass.Scada
    assert transport_class_or_none("weather") is TransportClass.WeatherForecastService


def test_transport_class_or_none_is_none_for_short_form() -> None:
    # Proactor short_names are not RoutingClass values — resolve to None, never raise.
    assert transport_class_or_none("s") is None
    assert transport_class_or_none("a") is None
    assert transport_class_or_none("ws") is None
    assert transport_class_or_none("") is None


def test_wrapped_short_form_to_class_parses_and_round_trips() -> None:
    env = parse_routing_key(PROD_WRAPPED_TO_SCADA)
    assert isinstance(env, WrappedRoutingEnvelope)
    # The class slot is retained raw; resolution is best-effort (None here).
    assert env.to_class_token == "s"
    assert env.to_class is None
    # Delivery-relevant fields are intact.
    assert env.from_alias == "hw1.isone.me.versant.keene.beech"
    assert env.type_name == "gridworks.ping"
    # The exact wire key is preserved — no drift, no drop.
    assert env.routing_key == PROD_WRAPPED_TO_SCADA


def test_broadcast_short_form_from_class_parses_and_round_trips() -> None:
    env = parse_routing_key(PROD_WEATHER_BROADCAST)
    assert isinstance(env, BroadcastRoutingEnvelope)
    assert env.from_class_token == "ws"
    assert env.from_class is None
    assert env.from_alias == "hw1.isone.ws"
    assert env.type_name == "weather"
    assert env.routing_key == PROD_WEATHER_BROADCAST


def test_long_form_class_still_resolves() -> None:
    # Regression: a long-form to-class still resolves to its TransportClass.
    env = parse_routing_key("gw.hw1-isone-keene-scada.to.ltn.layout-lite")
    assert isinstance(env, WrappedRoutingEnvelope)
    assert env.to_class_token == "ltn"
    assert env.to_class is TransportClass.LeafTransactiveNode


def test_direct_short_form_class_tokens_parse_and_round_trip() -> None:
    # The from- and to-class slots of a JsonDirect key are equally tolerant.
    key = "rj.hw1-isone-keene-scada.s.report-event.a.hw1-isone-keene-atn"
    env = parse_routing_key(key)
    assert isinstance(env, DirectRoutingEnvelope)
    assert env.from_class_token == "s"
    assert env.to_class_token == "a"
    assert env.from_class is None
    assert env.to_class is None
    assert env.from_alias == "hw1.isone.keene.scada"
    assert env.to_alias == "hw1.isone.keene.atn"
    assert env.type_name == "report.event"
    assert env.routing_key == key


def test_unknown_category_still_raises() -> None:
    # gwbase's main parser deliberately does NOT learn the LTN's legacy
    # `broadcast.*` hack as a category — that is the JournalKeeper `legacy_hack`'s
    # job (design 'ltn-sends-gw-wrapped'). token[0] is not a MessageCategory.
    with pytest.raises(ValueError, match="not a known MessageCategory"):
        parse_routing_key("broadcast.glitch")


def test_from_classes_emits_long_form_tokens() -> None:
    # Build-side constructors keep emitting long-form class tokens from typed
    # TransportClass values, and round-trip through parse to a resolved class.
    wrapped = WrappedRoutingEnvelope.from_classes(
        type_name="layout.lite",
        from_alias="d1.scada",
        to_class=TransportClass.LeafTransactiveNode,
    )
    assert wrapped.to_class_token == "ltn"
    assert (
        parse_routing_key(wrapped.routing_key).to_class
        is TransportClass.LeafTransactiveNode
    )

    direct = DirectRoutingEnvelope.from_classes(
        type_name="bid",
        from_alias="d1.ltn",
        from_class=TransportClass.LeafTransactiveNode,
        to_class=TransportClass.MarketMaker,
        to_alias="d1.mm",
    )
    assert (direct.from_class_token, direct.to_class_token) == ("ltn", "mm")

    bcast = BroadcastRoutingEnvelope.from_classes(
        type_name="latest.price",
        from_alias="d1.mm",
        from_class=TransportClass.MarketMaker,
    )
    assert bcast.from_class_token == "mm"


def test_structural_arity_still_raises() -> None:
    # The tolerance is for class *values*, not key *shape* — arity/structure
    # checks the parse-helper rewrite must preserve.
    with pytest.raises(ValueError, match="5 words"):
        parse_routing_key("gw.d1-source.to.scada")  # wrapped: 4 tokens
    with pytest.raises(ValueError, match="must use 'to'"):
        parse_routing_key("gw.d1-source.XX.scada.report-event")  # wrapped: no 'to'
    with pytest.raises(ValueError, match="at least 4 words"):
        parse_routing_key("rjb.d1-source.scada")  # broadcast: 3 tokens
    with pytest.raises(ValueError, match="6 words"):
        parse_routing_key("rj.d1-source.scada.report-event.scada")  # direct: 5 tokens
