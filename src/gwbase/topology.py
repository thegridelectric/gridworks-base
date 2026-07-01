"""Single source of truth for the rabbit broker topology.

Both the broker-definitions generator (``for_docker/gen_definitions.py``)
and the test harness (``tests/_stubs.py``) derive their exchanges and
bindings from here, so test / dev / prod topologies cannot diverge.

Spec: ``wiki/gridworks-base/executor/transport.md`` §3.5 and
``provisioning.md`` §3.6.
"""

from dataclasses import dataclass

from gwbase.transport_encoding import MessageCategory, RoutingClass

# Classes that run as rabbit AMQP actors and therefore get a <rc>_tx
# (internal, consume) + <rc>mic_tx (non-internal, publish) pair. Opt-in:
#   - scada is MQTT-only (reached via amq.topic), so it is NOT here.
#   - cn (ConnectivityNode) is passive / non-runtime, so it is NOT here.
# A newly-added RoutingClass gets NO exchanges until it is added to this set.
AMQP_ACTOR_CLASSES: frozenset[RoutingClass] = frozenset({
    RoutingClass.TerminalAsset,
    RoutingClass.LeafTransactiveNode,
    RoutingClass.MarketMaker,
    RoutingClass.PriceForecastService,
    RoutingClass.WeatherForecastService,
    RoutingClass.TimeCoordinator,
    RoutingClass.Supervisor,
    RoutingClass.GridNodeRegistry,
    RoutingClass.FleetIndexService,
})

# Direct-message routing edges: a sender of class ``src`` may reach a
# receiver of class ``dst`` via the cross-class mic_tx -> _tx forwarding
# fabric. Direct-only — broadcasts are subscriber-bound, not here (§3.5).
ROUTING_EDGES: list[tuple[RoutingClass, RoutingClass]] = [
    (RoutingClass.LeafTransactiveNode, RoutingClass.MarketMaker),
    (RoutingClass.LeafTransactiveNode, RoutingClass.Supervisor),
    (RoutingClass.LeafTransactiveNode, RoutingClass.TimeCoordinator),
    (RoutingClass.MarketMaker, RoutingClass.Supervisor),
    (RoutingClass.MarketMaker, RoutingClass.TimeCoordinator),
    (RoutingClass.Supervisor, RoutingClass.LeafTransactiveNode),
    (RoutingClass.Supervisor, RoutingClass.MarketMaker),
    (RoutingClass.Supervisor, RoutingClass.TimeCoordinator),
    (RoutingClass.TimeCoordinator, RoutingClass.Supervisor),
    # A MarketMaker sends the re-parent command to the registry and gets the reply.
    (RoutingClass.MarketMaker, RoutingClass.GridNodeRegistry),
    (RoutingClass.GridNodeRegistry, RoutingClass.MarketMaker),
    # FIS reads the registry over request-reply (a gwbase citizen): its read
    # request reaches the registry, and the registry's reply reaches FIS.
    (RoutingClass.FleetIndexService, RoutingClass.GridNodeRegistry),
    (RoutingClass.GridNodeRegistry, RoutingClass.FleetIndexService),
]

# The universal audit tap (ear) and the built-in MQTT/wrapped exchange.
EAR_EXCHANGE = "ear_tx"
AMQP_TOPIC = "amq.topic"  # built-in; MQTT-bridged + wrapped (gw) traffic
EAR_BINDING_KEY = "#"


def consume_exchange(rc: RoutingClass) -> str:
    """Internal exchange an actor of class ``rc`` consumes from."""
    return f"{rc.value}_tx"


def publish_exchange(rc: RoutingClass) -> str:
    """Non-internal exchange anyone publishes to in order to reach ``rc``."""
    return f"{rc.value}mic_tx"


def direct_binding_key(src: RoutingClass, dst: RoutingClass) -> str:
    """Topic pattern matching JsonDirect keys from class ``src`` to ``dst``.

    JsonDirect grammar is ``rj.<from>.<from-class>.<type>.<to-class>.<to-alias>``
    (6 tokens); this filters on the from-class and to-class positions and
    wildcards the rest.
    """
    return f"*.*.{src.value}.*.{dst.value}.*"


@dataclass(frozen=True)
class ExchangeSpec:
    """A topic exchange the broker must pre-provision."""

    name: str
    internal: bool
    exchange_type: str = "topic"
    durable: bool = True


@dataclass(frozen=True)
class BindingSpec:
    """An exchange-to-exchange binding the broker must pre-provision."""

    source: str
    destination: str
    routing_key: str


def _amqp_classes_sorted() -> list[RoutingClass]:
    return sorted(AMQP_ACTOR_CLASSES, key=lambda rc: rc.value)


def exchanges() -> list[ExchangeSpec]:
    """Every exchange the broker must pre-provision, in a stable order:
    the ear tap, then a consume/publish pair per AMQP-actor class."""
    specs: list[ExchangeSpec] = [ExchangeSpec(EAR_EXCHANGE, internal=True)]
    for rc in _amqp_classes_sorted():
        specs.append(ExchangeSpec(consume_exchange(rc), internal=True))
        specs.append(ExchangeSpec(publish_exchange(rc), internal=False))
    return specs


def exchange_bindings() -> list[BindingSpec]:
    """Every exchange-to-exchange binding: the cross-class direct fabric
    plus the ear taps (every publish exchange + amq.topic fan into ear)."""
    bindings: list[BindingSpec] = [
        BindingSpec(
            publish_exchange(src), consume_exchange(dst), direct_binding_key(src, dst)
        )
        for src, dst in ROUTING_EDGES
    ]
    for rc in _amqp_classes_sorted():
        bindings.append(
            BindingSpec(publish_exchange(rc), EAR_EXCHANGE, EAR_BINDING_KEY)
        )
    bindings.append(BindingSpec(AMQP_TOPIC, EAR_EXCHANGE, EAR_BINDING_KEY))
    # MQTT bridge tap: the time coordinator's BROADCASTS cross to the MQTT
    # plugin's exchange, so MQTT-native actors (scadas — reached via
    # amq.topic, see AMQP_ACTOR_CLASSES note) can subscribe to sim
    # timesteps. Broadcasts only; direct traffic stays on the AMQP fabric.
    bindings.append(
        BindingSpec(
            publish_exchange(RoutingClass.TimeCoordinator),
            AMQP_TOPIC,
            f"{MessageCategory.JsonBroadcast.value}.#",
        )
    )
    return bindings


def _validate() -> None:
    """Every routing edge must connect two AMQP-actor classes, else the
    binding would target an exchange that is never provisioned."""
    for src, dst in ROUTING_EDGES:
        if src not in AMQP_ACTOR_CLASSES:
            raise ValueError(f"ROUTING_EDGES src {src} not in AMQP_ACTOR_CLASSES")
        if dst not in AMQP_ACTOR_CLASSES:
            raise ValueError(f"ROUTING_EDGES dst {dst} not in AMQP_ACTOR_CLASSES")


_validate()
