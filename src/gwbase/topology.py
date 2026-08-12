"""Single source of truth for the rabbit broker topology.

Both the broker-definitions generator (``for_docker/gen_definitions.py``)
and the test harness (``tests/_stubs.py``) derive their exchanges and
bindings from here, so test / dev / prod topologies cannot diverge.
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
})

# Direct-message routing edges: a sender of class ``src`` may reach a
# receiver of class ``dst`` via the cross-class mic_tx -> _tx forwarding
# fabric. Direct-only — broadcasts are subscriber-bound, not here.
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
    # Weather-class actors direct-message each other: the weather minter
    # (an operator identity of the weather class) sends the create
    # command and gets the verdict over the one self-edge.
    (RoutingClass.WeatherForecastService, RoutingClass.WeatherForecastService),
]

# The universal audit tap (ear) and the built-in MQTT/wrapped exchange.
EAR_EXCHANGE = "ear_tx"
AMQP_TOPIC = "amq.topic"  # built-in; MQTT-bridged + wrapped (gw) traffic
EAR_BINDING_KEY = "#"

# The registry's SCOPED audit tap: a second, tiny ear fed only the
# meaning-bearing registry slice — everything addressed to the registry (its
# consume exchange) and everything the registry says (its publish exchange:
# forest broadcasts AND the write verdicts, since every actor publishes via
# its own mic — so refusals are witnessed too). The seed-store capture
# consumes this with a plain `#`; the slice is defined HERE, in the fabric,
# in git — never in a tap's runtime binding.
GNR_EAR_EXCHANGE = "gnr_ear_tx"


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


@dataclass(frozen=True)
class QueueSpec:
    """A durable queue the broker must pre-provision."""

    name: str
    durable: bool = True


@dataclass(frozen=True)
class PolicySpec:
    """A policy the broker must pre-provision."""

    name: str
    pattern: str
    definition: dict
    apply_to: str = "queues"
    priority: int = 0


def _amqp_classes_sorted() -> list[RoutingClass]:
    return sorted(AMQP_ACTOR_CLASSES, key=lambda rc: rc.value)


def exchanges() -> list[ExchangeSpec]:
    """Every exchange the broker must pre-provision, in a stable order:
    the ear tap, then a consume/publish pair per AMQP-actor class."""
    specs: list[ExchangeSpec] = [
        ExchangeSpec(EAR_EXCHANGE, internal=True),
        ExchangeSpec(GNR_EAR_EXCHANGE, internal=True),
    ]
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
    # The registry's scoped audit slice (see GNR_EAR_EXCHANGE): to-gnr and
    # from-gnr both fan in.
    bindings.append(
        BindingSpec(
            consume_exchange(RoutingClass.GridNodeRegistry),
            GNR_EAR_EXCHANGE,
            EAR_BINDING_KEY,
        )
    )
    bindings.append(
        BindingSpec(
            publish_exchange(RoutingClass.GridNodeRegistry),
            GNR_EAR_EXCHANGE,
            EAR_BINDING_KEY,
        )
    )
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
    # Same bridge for the grid-node-registry's BROADCASTS (`g.node.forest`
    # topology changes, radio_channel = the audience-known alias), so
    # MQTT-native actors can passively hear ancestor renames too. The forest
    # carries aliases + immutable ids only — never coordinates — so it is
    # safe to cross to the MQTT side.
    bindings.append(
        BindingSpec(
            publish_exchange(RoutingClass.GridNodeRegistry),
            AMQP_TOPIC,
            f"{MessageCategory.JsonBroadcast.value}.#",
        )
    )
    return bindings


def queues() -> list[QueueSpec]:
    """Every durable queue the broker pre-provisions.

    Just the standing `debug` tap today: a consumer-less queue for
    inspecting raw traffic in the management UI without standing up a
    consumer. Its BINDING is deliberately NOT here — which slice it taps is
    investigation state, hand-(re)bound per debugging session; the queue and
    its cap policy are topology. Contents are always duplicates of what crosses
    the audit tap (``ear_tx``), so it is always safe to purge."""
    return [QueueSpec("debug")]


def policies() -> list[PolicySpec]:
    """Every policy the broker pre-provisions. `debug-cap` keeps a forgotten
    debug tap from growing unboundedly: last 1000 messages, drop-oldest."""
    return [
        PolicySpec(
            name="debug-cap",
            pattern="^debug$",
            definition={"max-length": 1000, "overflow": "drop-head"},
        )
    ]


def _validate() -> None:
    """Every routing edge must connect two AMQP-actor classes, else the
    binding would target an exchange that is never provisioned."""
    for src, dst in ROUTING_EDGES:
        if src not in AMQP_ACTOR_CLASSES:
            raise ValueError(f"ROUTING_EDGES src {src} not in AMQP_ACTOR_CLASSES")
        if dst not in AMQP_ACTOR_CLASSES:
            raise ValueError(f"ROUTING_EDGES dst {dst} not in AMQP_ACTOR_CLASSES")


_validate()
