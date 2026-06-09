import functools
import logging
import random
from abc import ABC, abstractmethod
from typing import Optional, no_type_check

from gwbase.actor_base import ActorBase
from gwbase.config import ServiceSettings
from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import HeartbeatA, Ready, SimTimestep
from gwbase.transport_encoding import (
    BroadcastRoutingEnvelope,
    DirectRoutingEnvelope,
    MessageCategory,
    RoutingEnvelope,
    TransportClass,
    routing_code,
)

LOGGER = logging.getLogger(__name__)


class Orchestrator(ActorBase, ABC):
    """An ``ActorBase`` that class-routes and rides the GridWorks
    orchestration rhythm — answering heartbeats from its supervisor and
    tracking simulated time from its time coordinator.

    This is the first tier with a ``transport_class``: it arrives as an
    explicit ``__init__`` param (intrinsic to the actor's role, not
    deployment config — like ``my_super_alias``). From it, ``Orchestrator``
    names its class exchanges (``<rc>_tx`` consume / ``<rc>mic_tx`` publish)
    and binds its queue direct-to-me, and it gains ``direct_envelope`` /
    ``broadcast_envelope`` (which stamp ``from_class``).

    Used by Supervisor and TimeCoordinator (non-GNode orchestration
    participants, ``ServiceSettings``) and, with GNode identity added, by
    ``GridworksActor``.

    The Sema codec used for control-plane types is private to this class.
    Subclasses see only semantic events (``on_supervisor_heartbeat``,
    ``on_simulated_time``); they implement ``process_message`` for
    application traffic and never touch ``dispatch_message``.
    """

    _CONTROL_PLANE_TYPES: frozenset[str] = frozenset({"heartbeat.a", "sim.timestep"})

    def __init__(
        self,
        *,
        settings: ServiceSettings,
        transport_class: TransportClass,
        my_super_alias: str,
        my_time_coordinator_alias: str,
    ):
        super().__init__(settings=settings)

        # Class routing: override the ear-tap defaults with this actor's
        # class consume/publish exchanges (infra owns the fabric, §3.5–§3.6).
        self.transport_class: TransportClass = transport_class
        self.routing_code: str = routing_code(transport_class)
        self._consume_exchange = self.routing_code + "_tx"
        self._publish_exchange = self.routing_code + "mic_tx"

        self._control_plane_codec = GwBaseSemaCodec()
        self._my_super_alias: str = my_super_alias
        self._my_time_coordinator_alias: str = my_time_coordinator_alias
        self._sim_time_unix_s: int = 0

    @property
    def my_super_alias(self) -> str:
        return self._my_super_alias

    @property
    def my_time_coordinator_alias(self) -> str:
        return self._my_time_coordinator_alias

    # ------------------------------------------------------------------
    # Queue binding — class-routed: bind direct-to-me on <rc>_tx
    # ------------------------------------------------------------------

    @no_type_check
    def bind_queue(self) -> None:
        """Bind the queue to this actor's consume exchange with a routing-key
        pattern matching direct messages addressed to it. When the bind
        completes pika invokes ``on_direct_message_bindok`` (which sets QoS)."""
        lrh_alias = self.alias.replace(".", "-")
        rj = MessageCategory.JsonDirect.value
        direct_message_to_me_binding = f"{rj}.*.*.*.*.{lrh_alias}"
        LOGGER.info(
            "Binding %s to %s with %s",
            self._consume_exchange,
            self.queue_name,
            direct_message_to_me_binding,
        )
        cb = functools.partial(
            self.on_direct_message_bindok,
            binding=direct_message_to_me_binding,
        )
        self._single_channel.queue_bind(
            self.queue_name,
            self._consume_exchange,
            routing_key=direct_message_to_me_binding,
            callback=cb,
        )

    # ------------------------------------------------------------------
    # RoutingEnvelope helpers that stamp from_class (= transport_class)
    # ------------------------------------------------------------------

    def direct_envelope(
        self,
        *,
        type_name: str,
        to_class: TransportClass,
        to_alias: str,
    ) -> DirectRoutingEnvelope:
        return DirectRoutingEnvelope(
            type_name=type_name,
            from_alias=self.alias,
            from_class=self.transport_class,
            to_class=to_class,
            to_alias=to_alias,
        )

    def broadcast_envelope(
        self,
        *,
        type_name: str,
        radio_channel: Optional[str] = None,
    ) -> BroadcastRoutingEnvelope:
        return BroadcastRoutingEnvelope(
            type_name=type_name,
            from_alias=self.alias,
            from_class=self.transport_class,
            radio_channel=radio_channel,
        )

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        if envelope.type_name in self._CONTROL_PLANE_TYPES:
            self._dispatch_control_plane(envelope=envelope, body=body)
            return
        self.process_message(envelope=envelope, body=body)

    @abstractmethod
    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        """Subclass hook for application-level messages."""

    def _dispatch_control_plane(
        self, *, envelope: RoutingEnvelope, body: bytes
    ) -> None:
        try:
            obj = self._control_plane_codec.from_bytes(body)
        except Exception as e:
            LOGGER.warning(f"Failed to decode control-plane {envelope.type_name}: {e}")
            return
        if isinstance(obj, HeartbeatA):
            self._handle_heartbeat(obj, envelope=envelope, body=body)
        elif isinstance(obj, SimTimestep):
            self._handle_timestep(obj, from_alias=envelope.from_alias)

    # ------------------------------------------------------------------
    # Internal handlers — Sema objects do not escape these methods
    # ------------------------------------------------------------------

    def _handle_heartbeat(
        self, ping: HeartbeatA, *, envelope: RoutingEnvelope, body: bytes
    ) -> None:
        # Only a ping from THIS actor's supervisor is handled internally
        # (pong + on_supervisor_heartbeat hook). Any other heartbeat.a — e.g.
        # a subordinate's heartbeat arriving at its supervisor — is surfaced
        # to the application via process_message so it can be observed.
        if envelope.from_alias != self._my_super_alias:
            self.process_message(envelope=envelope, body=body)
            return
        self.on_supervisor_heartbeat(from_alias=envelope.from_alias)
        self._send_heartbeat_response(ping=ping)

    def _handle_timestep(self, ts: SimTimestep, *, from_alias: str) -> None:
        if ts.time_unix_s < self._sim_time_unix_s:
            return
        is_new = ts.time_unix_s > self._sim_time_unix_s
        self._sim_time_unix_s = ts.time_unix_s
        self.on_simulated_time(
            time_unix_s=ts.time_unix_s,
            from_alias=from_alias,
            is_new=is_new,
        )

    # ------------------------------------------------------------------
    # Semantic hooks — subclasses override these
    # ------------------------------------------------------------------

    def on_supervisor_heartbeat(self, *, from_alias: str) -> None:
        """Called after this actor receives a heartbeat from its supervisor
        (and after the pong is sent). Default is no-op."""

    def on_simulated_time(
        self, *, time_unix_s: int, from_alias: str, is_new: bool
    ) -> None:
        """Called after the simulated clock advances or repeats.

        ``is_new`` is True if the timestep advanced; False if it repeated
        the current value. Default is no-op.
        """

    # ------------------------------------------------------------------
    # Control-plane sends — Sema objects are constructed and encoded here,
    # then handed to ActorBase as bytes + type_name
    # ------------------------------------------------------------------

    def _send_heartbeat_response(self, ping: HeartbeatA) -> None:
        pong = HeartbeatA(
            my_hex=random.choice("0123456789abcdef"),
            your_last_hex=ping.my_hex,
        )
        self.send(
            envelope=self.direct_envelope(
                type_name=pong.type_name,
                to_class=TransportClass.Supervisor,
                to_alias=self._my_super_alias,
            ),
            body=self._control_plane_codec.to_bytes(pong),
        )
        LOGGER.debug(
            f"[{self.alias}] Sent HB pong: SuHex {pong.your_last_hex}, MyHex {pong.my_hex}"
        )

    def send_ready(self, *, time_unix_s: int | None = None) -> None:
        """Announce readiness for a simulated timestep to the time
        coordinator. Defaults to the latest received simulated time."""
        msg = Ready(
            from_g_node_alias=self.alias,
            from_g_node_instance_id=self.instance_id,
            time_unix_s=time_unix_s
            if time_unix_s is not None
            else self._sim_time_unix_s,
        )
        self.send(
            envelope=self.direct_envelope(
                type_name=msg.type_name,
                to_class=TransportClass.TimeCoordinator,
                to_alias=self._my_time_coordinator_alias,
            ),
            body=self._control_plane_codec.to_bytes(msg),
        )

    # ------------------------------------------------------------------
    # Simulated time accessors
    # ------------------------------------------------------------------

    @property
    def time_unix_s(self) -> int:
        """Latest simulated time announced by the time coordinator."""
        return self._sim_time_unix_s
