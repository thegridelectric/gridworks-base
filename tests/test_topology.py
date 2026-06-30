"""Invariants for the shared broker topology source."""

from gwbase import topology as topo
from gwbase.transport_encoding import RoutingClass


def test_mqtt_only_and_passive_classes_excluded() -> None:
    # scada is MQTT-only; cn is passive — neither gets AMQP exchanges.
    assert RoutingClass.Scada not in topo.AMQP_ACTOR_CLASSES
    assert RoutingClass.ConnectivityNode not in topo.AMQP_ACTOR_CLASSES
    assert topo.AMQP_ACTOR_CLASSES == frozenset({
        RoutingClass.TerminalAsset,
        RoutingClass.LeafTransactiveNode,
        RoutingClass.MarketMaker,
        RoutingClass.PriceForecastService,
        RoutingClass.WeatherForecastService,
        RoutingClass.TimeCoordinator,
        RoutingClass.Supervisor,
        RoutingClass.GridNodeRegistry,
    })


def test_every_edge_endpoint_is_an_amqp_actor_class() -> None:
    for src, dst in topo.ROUTING_EDGES:
        assert src in topo.AMQP_ACTOR_CLASSES
        assert dst in topo.AMQP_ACTOR_CLASSES


def test_direct_binding_key_filters_on_class_positions() -> None:
    key = topo.direct_binding_key(RoutingClass.Supervisor, RoutingClass.Scada)
    assert key == "*.*.super.*.scada.*"


def test_exchange_naming() -> None:
    assert topo.consume_exchange(RoutingClass.LeafTransactiveNode) == "ltn_tx"
    assert topo.publish_exchange(RoutingClass.LeafTransactiveNode) == "ltnmic_tx"
    # mm + "mic_tx" -> "mmmic_tx" (matches actor_base's routing_code + "mic_tx")
    assert topo.publish_exchange(RoutingClass.MarketMaker) == "mmmic_tx"


def test_exchanges_cover_ear_plus_a_pair_per_class() -> None:
    specs = topo.exchanges()
    names = {s.name for s in specs}
    assert topo.EAR_EXCHANGE in names
    # ear + 2 per AMQP class
    assert len(specs) == 1 + 2 * len(topo.AMQP_ACTOR_CLASSES)
    by_name = {s.name: s for s in specs}
    # ear_tx and every <rc>_tx are internal; every <rc>mic_tx is not
    assert by_name["ear_tx"].internal is True
    assert by_name["ltn_tx"].internal is True
    assert by_name["ltnmic_tx"].internal is False
    assert all(s.exchange_type == "topic" and s.durable for s in specs)


def test_bindings_cover_edges_and_ear_taps() -> None:
    bindings = topo.exchange_bindings()
    # one per routing edge, plus one ear tap per AMQP class, plus the
    # amq.topic ear tap, plus the timemic -> amq.topic MQTT bridge tap
    assert len(bindings) == len(topo.ROUTING_EDGES) + len(topo.AMQP_ACTOR_CLASSES) + 2

    # a known direct edge: ltnmic_tx -> super_tx on *.*.ltn.*.super.*
    assert any(
        b.source == "ltnmic_tx"
        and b.destination == "super_tx"
        and b.routing_key == "*.*.ltn.*.super.*"
        for b in bindings
    )
    # amq.topic fans into ear with '#'
    assert any(
        b.source == "amq.topic" and b.destination == "ear_tx" and b.routing_key == "#"
        for b in bindings
    )
    # time coordinator broadcasts cross to the MQTT plugin's exchange
    # (rjb.# only — direct traffic stays on the AMQP fabric)
    assert any(
        b.source == "timemic_tx"
        and b.destination == "amq.topic"
        and b.routing_key == "rjb.#"
        for b in bindings
    )
