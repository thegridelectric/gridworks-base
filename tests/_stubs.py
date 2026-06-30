"""Stub actors used to exercise ActorBase / Orchestrator / GridworksActor
against a live rabbit broker.

Note the tier split: the GNode under test (``GNodeStubRecorder``) is a
``GridworksActor`` (real GNode identity, g.node.gt.json), while Supervisor and
TimeCoordinator — which are NOT GNodes — are ``Orchestrator`` stubs that ride
``ServiceSettings`` with no g.node.gt.json. That mirrors the production tiers.
"""

from typing import Optional

import pika

from gwbase import topology
from gwbase.config import GNodeSettings, ServiceSettings
from gwbase.gridworks_actor import GridworksActor
from gwbase.orchestrator import Orchestrator
from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import HeartbeatA, Ready
from gwbase.transport_encoding import RoutingEnvelope, TransportClass


def declare_topology(ch: pika.channel.Channel) -> None:
    """Declare every exchange + binding from the shared topology source
    (``gwbase.topology``) — so test / dev / prod provision the same fabric.
    """
    for ex in topology.exchanges():
        ch.exchange_declare(
            exchange=ex.name,
            exchange_type=ex.exchange_type,
            durable=ex.durable,
            internal=ex.internal,
        )
    for b in topology.exchange_bindings():
        ch.exchange_bind(
            destination=b.destination,
            source=b.source,
            routing_key=b.routing_key,
        )


def provision_topology(url: str) -> None:
    """Provision the broker fabric BEFORE any actor starts.

    Actors only *passively* assert their consume exchange exists, so the
    exchange set + bindings must pre-exist (mirrors how dev/prod load the
    generated definitions). Opens a short-lived admin connection, declares
    the topology from ``gwbase.topology``, and closes.
    """
    conn = pika.BlockingConnection(pika.URLParameters(url))
    try:
        declare_topology(conn.channel())
    finally:
        conn.close()


class _RecorderMixin:
    """Recording behavior shared by the GNode and Orchestrator stubs.

    Sits ahead of the actor tier in the MRO so its ``on_message`` /
    ``process_message`` / ``on_supervisor_heartbeat`` overrides win while
    still chaining to the framework via ``super()``.
    """

    def _init_recorder(self) -> None:
        self._codec = GwBaseSemaCodec()
        self.messages_received: int = 0
        self.messages_routed_internally: int = 0
        self.got_heartbeat_from_super: bool = False
        self.latest_envelope: RoutingEnvelope | None = None
        self.latest_body: bytes | None = None

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        self.messages_received += 1
        super().on_message(_unused_channel, basic_deliver, properties, body)

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        self.messages_routed_internally += 1
        self.latest_envelope = envelope
        self.latest_body = body

    def on_supervisor_heartbeat(self, *, from_alias: str) -> None:
        self.got_heartbeat_from_super = True

    def summary_str(self) -> str:
        return (
            f"{self.transport_class.value} [{self.alias}] "
            f"messages_received={self.messages_received}"
        )


class GNodeStubRecorder(_RecorderMixin, GridworksActor):
    """A real GNode (GridworksActor) that records inbound transport metadata."""

    def __init__(
        self,
        *,
        settings: GNodeSettings,
        transport_class: TransportClass,
        my_super_alias: str,
        my_time_coordinator_alias: str,
    ):
        super().__init__(
            settings=settings,
            transport_class=transport_class,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )
        self._init_recorder()


class OrchestratorStubRecorder(_RecorderMixin, Orchestrator):
    """A non-GNode orchestration participant (Orchestrator) — ServiceSettings,
    no g.node.gt.json. Base for the Supervisor / TimeCoordinator stubs."""

    def __init__(
        self,
        *,
        settings: ServiceSettings,
        transport_class: TransportClass,
        my_super_alias: str,
        my_time_coordinator_alias: str,
    ):
        super().__init__(
            settings=settings,
            transport_class=transport_class,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )
        self._init_recorder()


class SupervisorStubRecorder(OrchestratorStubRecorder):
    """Heartbeats from a known sub fall through to process_message
    (Orchestrator filters incoming HBs by my_super_alias). We record them."""

    def __init__(
        self,
        *,
        settings: ServiceSettings,
        transport_class: TransportClass = TransportClass.Supervisor,
        my_super_alias: str,
        my_time_coordinator_alias: str,
        subordinate_alias: str,
    ):
        super().__init__(
            settings=settings,
            transport_class=transport_class,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )
        self.my_single_sub: str = subordinate_alias
        self.got_heartbeat_from_sub: bool = False

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        super().process_message(envelope=envelope, body=body)
        if (
            envelope.type_name == HeartbeatA.type_name_value()
            and envelope.from_alias == self.my_single_sub
        ):
            self.got_heartbeat_from_sub = True


class TimeCoordinatorStubRecorder(OrchestratorStubRecorder):
    """Records Ready announcements that match its current simulated time."""

    def __init__(
        self,
        *,
        settings: ServiceSettings,
        transport_class: TransportClass = TransportClass.TimeCoordinator,
        my_super_alias: str,
        my_time_coordinator_alias: str,
        current_time_unix_s: int,
        my_actor_aliases: list[str],
    ):
        super().__init__(
            settings=settings,
            transport_class=transport_class,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )
        self.my_actors: list[str] = my_actor_aliases
        self.ready: list[str] = []
        self._time: int = current_time_unix_s

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        super().process_message(envelope=envelope, body=body)
        if envelope.type_name != Ready.type_name_value():
            return
        try:
            msg = self._codec.from_bytes(body)
        except Exception:
            return
        if (
            isinstance(msg, Ready)
            and envelope.from_alias in self.my_actors
            and msg.time_unix_s == self._time
        ):
            self.ready.append(envelope.from_alias)

    def is_ready(self) -> bool:
        return set(self.ready) == set(self.my_actors)
