import functools
import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, no_type_check

import pika
from pika.channel import Channel as PikaChannel
from pika.spec import Basic, BasicProperties

from gwbase.config import GNodeSettings
from gwbase.transport_encoding import (
    BroadcastRoutingEnvelope,
    DirectRoutingEnvelope,
    MessageCategory,
    RoutingEnvelope,
    TransportClass,
    WrappedRoutingEnvelope,
    parse_routing_key,
    routing_code,
)


class OnSendMessageDiagnostic(Enum):
    CHANNEL_NOT_OPEN = "ChannelNotOpen"
    STOPPED_SO_NOT_SENDING = "StoppedSoNotSending"
    STOPPING_SO_NOT_SENDING = "StoppingSoNotSending"
    MESSAGE_SENT = "MessageSent"
    UNKNOWN_ERROR = "UnknownError"


class OnReceiveMessageDiagnostic(Enum):
    ROUTING_KEY_PARSE_ERROR = "RoutingKeyParseError"
    UNHANDLED_CATEGORY = "UnhandledCategory"
    MESSAGE_DELIVERED = "MessageDelivered"


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class _PublishRequest:
    """Args needed to publish bytes through the open rabbit channel."""

    routing_key: str
    body: bytes
    correlation_id: str
    exchange: str
    category: MessageCategory


class ActorBase(ABC):
    """Rabbit-transport actor.

    Parses the transport envelope, hands raw bytes plus envelope to
    ``dispatch_message``, and offers ``send`` which takes already-encoded
    bytes plus the type_name needed for routing. Does not know about
    payload types or codecs — those are the subclass's concern.

    ``dispatch_message`` is the abstract framework hook that the transport
    invokes for every parsed delivery. Intermediate layers (e.g.
    ``GridworksActor``) implement it to filter control-plane traffic and
    forward application messages to the subclass's ``process_message``.
    Final application classes typically subclass ``GridworksActor`` and
    implement ``process_message`` rather than implementing
    ``dispatch_message`` directly.
    """

    @abstractmethod
    def dispatch_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None: ...

    SHUTDOWN_INTERVAL: float = 0.1

    def __init__(
        self,
        *,
        settings: GNodeSettings,
    ):
        self.settings: GNodeSettings = settings

        # Durable GNode identity is provisioned on disk as a g.node.gt JSON.
        # We read the fields we need verbatim; schema validation is the
        # responsibility of whatever placed the file.
        g_node_data = json.loads(settings.g_node_path.read_text())
        self.alias: str = g_node_data["Alias"]
        self.g_node_id: str = g_node_data["GNodeId"]
        # Free-form per sema g.node.gt/004. Sent to FIS in client_properties.
        self.g_node_class: str = g_node_data["GNodeClass"]

        # Fresh per FIS lifecycle: a new runtime instance every boot.
        self.g_node_instance_id: str = str(uuid.uuid4())

        # Transport class is independent of GNode class — a Supervisor is
        # not a GNode but still routes on rabbit.
        self.transport_class: TransportClass = settings.transport_class
        self.routing_code: str = routing_code(self.transport_class)

        adder = "-F" + str(uuid.uuid4()).split("-")[0][0:3]
        self.queue_name: str = self.alias + adder
        self._consume_exchange: str = self.routing_code + "_tx"
        self._publish_exchange: str = self.routing_code + "mic_tx"
        self._url: str = settings.rabbit.url.get_secret_value()

        self.latest_routing_key: Optional[str] = None
        self.shutting_down: bool = False
        self._main_loop_running: bool = False

        self._consume_connection: Optional[
            pika.adapters.select_connection.SelectConnection
        ] = None
        self._single_channel: Optional[pika.channel.Channel] = None
        self._closing_consumer: bool = False
        self._consumer_tag: Optional[str] = None
        self.should_reconnect_consumer: bool = False
        self.was_consuming: bool = False
        self._consuming: bool = False
        self._prefetch_count: int = 1
        self._reconnect_delay: int = 0

        self.consuming_thread: threading.Thread = threading.Thread(
            target=self.run_reconnecting_consumer,
            daemon=True,
        )
        self._stopping: bool = False
        self._stopped: bool = True
        self._latest_on_message_diagnostic: Optional[OnReceiveMessageDiagnostic] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.local_start()
        self._stopped = False
        self.consuming_thread.start()

    def stop(self) -> None:
        self.shutting_down = True
        self.stop_consumer()
        self.local_stop()
        self.consuming_thread.join()
        self._stopping = False
        self._stopped = True

    def local_start(self) -> None:
        """Subclass hook: spin up additional threads here. Rabbit channels
        are NOT yet open."""
        self._main_loop_running = True

    def local_rabbit_startup(self) -> None:
        """Subclass hook: add extra queue bindings here. Do NOT start
        queues. Called at the end of ``start_consuming``."""

    def local_stop(self) -> None:
        """Subclass hook: join any threads owned by the subclass."""
        self._main_loop_running = False

    @property
    def main_loop_running(self) -> bool:
        return self._main_loop_running

    @property
    def consuming(self) -> bool:
        return self._consuming

    def __repr__(self) -> str:
        return f"{self.alias}"

    @property
    def short_alias(self) -> str:
        return self.alias.split(".")[-1]

    # ------------------------------------------------------------------
    # Consumer infrastructure
    # ------------------------------------------------------------------

    def flush_consumer(self) -> None:
        self.should_reconnect_consumer = False
        self.was_consuming = False
        self._consume_connection = None
        self._single_channel = None
        self._closing_consumer = False
        self._consumer_tag = None
        self._consuming = False

    def run_reconnecting_consumer(self) -> None:
        while self._main_loop_running:
            self.run_consumer()
            self._maybe_reconnect_consumer()

    def _maybe_reconnect_consumer(self) -> None:
        if self.should_reconnect_consumer:
            self.stop_consumer()
            reconnect_delay = self._get_reconnect_delay()
            if self._main_loop_running:
                LOGGER.info("Reconnecting after %d seconds", reconnect_delay)
            time.sleep(reconnect_delay)
            self.flush_consumer()

    def _get_reconnect_delay(self) -> int:
        if self.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        self._reconnect_delay = min(self._reconnect_delay, 30)
        return self._reconnect_delay

    def connect_consumer(self) -> pika.SelectConnection:
        """Connect to RabbitMQ. When the connection is established, pika
        will invoke ``on_consumer_connection_open``.

        :rtype: pika.SelectConnection
        """
        LOGGER.info("Connecting to %s", self._url)
        params = pika.URLParameters(self._url)
        # Per FIS lifecycle: identify runtime instance + GNode at connect
        # time so the broker (via the FIS auth backend) can authorize.
        params.client_properties = {
            "g_node_alias": self.alias,
            "g_node_instance_id": self.g_node_instance_id,
            "g_node_class": self.g_node_class,
        }
        return pika.SelectConnection(
            parameters=params,
            on_open_callback=self.on_consumer_connection_open,  # type: ignore[arg-type]
            on_open_error_callback=self.on_consumer_connection_open_error,  # type: ignore[arg-type]
            on_close_callback=self.on_consumer_connection_closed,  # type: ignore[arg-type]
        )

    def close_consumer_connection(self) -> None:
        self._consuming = False
        if self._consume_connection:
            if (
                not self._consume_connection.is_closing
                and not self._consume_connection.is_closed
            ):
                LOGGER.info("Closing consume connection")
                self._consume_connection.close()

    def on_consumer_connection_open(
        self,
        _unused_connection: pika.SelectConnection,
    ) -> None:
        """Invoked by pika once the connection to RabbitMQ is established.
        Triggers channel creation."""
        LOGGER.info("Connection opened")
        self.open_single_channel()

    def on_consumer_connection_open_error(
        self,
        _unused_connection: pika.SelectConnection,
        err: Exception,
    ) -> None:
        """Invoked by pika if the connection to RabbitMQ can't be
        established. Schedules a reconnect."""
        LOGGER.error(f"Consumer connection open failed: {err}")
        self.reconnect_consumer()

    def on_consumer_connection_closed(
        self,
        _unused_connection: pika.SelectConnection,
        reason: Exception,
    ) -> None:
        """Invoked by pika when the connection to RabbitMQ closes. If we
        weren't already shutting down, treat it as unexpected and try to
        reconnect; otherwise stop the ioloop and let shutdown complete."""
        self._single_channel = None
        if self._closing_consumer:
            self._consume_connection.ioloop.stop()  # type: ignore[union-attr]
        else:
            LOGGER.warning(f"Consumer connection closed, reconnect necessary: {reason}")
            self.reconnect_consumer()

    def reconnect_consumer(self) -> None:
        """Mark that a reconnect is necessary and stop the ioloop. The
        reconnect loop in ``run_reconnecting_consumer`` picks this up."""
        self.should_reconnect_consumer = True
        self.stop_consumer()

    def open_single_channel(self) -> None:
        """Open a channel via Channel.Open. When RabbitMQ confirms the
        channel is open pika will invoke ``on_consumer_channel_open``."""
        LOGGER.info("Creating a new channel")
        self._consume_connection.channel(on_open_callback=self.on_consumer_channel_open)  # type: ignore[union-attr]

    @no_type_check
    def on_consumer_channel_open(self, channel: PikaChannel) -> None:
        """Invoked by pika when the channel opens. Records the channel and
        kicks off exchange declaration."""
        LOGGER.info("Channel opened")
        self._single_channel = channel
        self.add_on_single_channel_close_callback()
        self.setup_exchange()

    @no_type_check
    def add_on_single_channel_close_callback(self) -> None:
        """Tell pika to invoke ``on_consumer_channel_closed`` if RabbitMQ
        unexpectedly closes this channel."""
        LOGGER.info("Adding consumer channel close callback")
        self._single_channel.add_on_close_callback(self.on_consumer_channel_closed)

    @no_type_check
    def on_consumer_channel_closed(
        self,
        channel: PikaChannel,
        reason: Exception,
    ) -> None:
        """Invoked by pika when the channel is unexpectedly closed —
        typically a protocol violation (redeclaring an exchange/queue with
        different parameters). We close the connection so the actor shuts
        down cleanly rather than retrying the channel."""
        LOGGER.warning("Consume channel %i was closed: %s", channel, reason)
        self.close_consumer_connection()

    @no_type_check
    def setup_exchange(self) -> None:
        """Assert the consume exchange exists via a *passive* Exchange.Declare.

        Infra owns the fabric: the exchange set + routing fabric are
        provisioned on the broker out-of-band (generated from
        ``gwbase/topology.py``; see wiki executor spec §3.5–§3.6). The actor
        does NOT define the exchange's params — ``passive=True`` is a pure
        existence check. If the broker was not provisioned the channel is
        closed with a 404, surfacing in ``on_consumer_channel_closed`` as a
        fail-fast rather than the actor silently creating a divergent
        exchange or fighting the definitions over ``internal``/``durable``
        (``PRECONDITION_FAILED``). When the check completes pika invokes
        ``on_exchange_declareok``."""
        LOGGER.info("Asserting consume exchange exists: %s", self._consume_exchange)
        cb = functools.partial(
            self.on_exchange_declareok,
            userdata=self._consume_exchange,
        )
        self._single_channel.exchange_declare(
            exchange=self._consume_exchange,
            exchange_type="topic",
            passive=True,
            callback=cb,
        )

    @no_type_check
    def on_exchange_declareok(self, _unused_frame, userdata) -> None:
        """Invoked by pika once the passive Exchange.Declare confirms the
        exchange exists. Kicks off queue declaration."""
        LOGGER.info("Consume exchange present: %s", userdata)
        self.setup_queue()

    @no_type_check
    def setup_queue(self) -> None:
        """Declare the consumer queue via Queue.Declare. When the
        declaration completes pika will invoke ``on_queue_declareok``."""
        LOGGER.info(f"Declaring queue {self.queue_name}")
        cb = functools.partial(self.on_queue_declareok)
        self._single_channel.queue_declare(
            queue=self.queue_name,
            auto_delete=True,
            callback=cb,
        )

    @no_type_check
    def on_queue_declareok(self, _unused_frame) -> None:
        """Invoked by pika once Queue.Declare completes. Binds the queue to
        the consume exchange with a routing-key pattern that matches direct
        messages addressed to this actor. When the bind completes pika will
        invoke ``on_direct_message_bindok``."""
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

    @no_type_check
    def on_direct_message_bindok(self, _unused_frame, binding) -> None:
        """Invoked by pika once Queue.Bind completes. Sets channel QoS
        (prefetch) next."""
        LOGGER.info(f"Queue {self.queue_name} bound with {binding}")
        self.set_qos()

    @no_type_check
    def set_qos(self) -> None:
        """Set consumer prefetch so RabbitMQ delivers at most
        ``_prefetch_count`` unacknowledged messages at a time. When QoS is
        applied pika will invoke ``on_basic_qos_ok``. Experiment with
        higher prefetch values for throughput in production."""
        self._single_channel.basic_qos(
            prefetch_count=self._prefetch_count,
            callback=self.on_basic_qos_ok,
        )

    @no_type_check
    def on_basic_qos_ok(self, _unused_frame) -> None:
        """Invoked by pika once Basic.QoS completes. Begins consuming."""
        LOGGER.info("QOS set to: %d", self._prefetch_count)
        self.start_consuming()

    @no_type_check
    def start_consuming(self) -> None:
        """Issue Basic.Consume so RabbitMQ begins delivering messages to
        ``on_message``. Registers a cancel callback so we're notified if
        RabbitMQ cancels the consumer. Stores the consumer tag for later
        cancellation, then calls ``local_rabbit_startup`` so subclasses can
        add any extra bindings."""
        LOGGER.info("Start consuming")
        self.add_on_cancel_consumer_callback()
        self._consumer_tag = self._single_channel.basic_consume(
            self.queue_name,
            self.on_message,
        )
        self.was_consuming = True
        self._consuming = True
        self.local_rabbit_startup()

    def add_on_cancel_consumer_callback(self) -> None:
        """Tell pika to invoke ``on_consumer_cancelled`` if RabbitMQ
        cancels our consumer."""
        LOGGER.info("Adding consumer cancellation callback")
        self._single_channel.add_on_cancel_callback(self.on_consumer_cancelled)  # type: ignore[union-attr]

    @no_type_check
    def on_consumer_cancelled(self, method_frame) -> None:
        """Invoked by pika when RabbitMQ sends Basic.Cancel for this
        consumer (e.g. queue deleted). Close the channel."""
        LOGGER.info("Consumer was cancelled remotely, shutting down: %r", method_frame)
        if self._single_channel:
            self._single_channel.close()

    @no_type_check
    def acknowledge_message(self, delivery_tag) -> None:
        """Send Basic.Ack for the given delivery tag."""
        LOGGER.debug(f"Acknowledging message {delivery_tag}")
        self._single_channel.basic_ack(delivery_tag)

    def stop_consuming(self) -> None:
        """Send Basic.Cancel so RabbitMQ stops delivering. When the
        cancellation is acknowledged pika will invoke
        ``on_cancelconsumer_ok``."""
        if self._single_channel:
            LOGGER.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            cb = functools.partial(
                self.on_cancelconsumer_ok,
                userdata=self._consumer_tag,
            )
            self._single_channel.basic_cancel(self._consumer_tag, cb)  # type: ignore[arg-type]

    @no_type_check
    def on_cancelconsumer_ok(self, _unused_frame, userdata) -> None:
        """Invoked by pika once RabbitMQ acknowledges the Basic.Cancel.
        Closes the channel, which in turn triggers
        ``on_consumer_channel_closed`` and ultimately closes the
        connection."""
        self._consuming = False
        LOGGER.info(
            "RabbitMQ acknowledged the cancellation of the consumer: %s",
            userdata,
        )
        self.close_consumer_channel()
        self._closing_consumer = False

    def close_consumer_channel(self) -> None:
        """Issue Channel.Close cleanly."""
        if self._single_channel:
            if (
                not self._single_channel.is_closing
                and not self._single_channel.is_closed
            ):
                self._single_channel.close()

    def run_consumer(self) -> None:
        """Open the consumer connection and run pika's ioloop (blocking).
        Called inside the consuming thread."""
        self._consume_connection = self.connect_consumer()
        self._consume_connection.ioloop.start()

    def stop_consumer(self) -> None:
        """Cleanly shut down the consumer side. If we're actively
        consuming, issues Basic.Cancel and lets the cancel-ok callback
        close the channel and connection; otherwise stops the ioloop
        directly. NB: if you ever want this to work under CTRL-C, figure
        out how to restart the ioloop after stop_consuming() without
        erroring."""
        if not self._closing_consumer:
            self._closing_consumer = True
            LOGGER.info("Consumer connection stopping")
            if self._consuming:
                self.stop_consuming()
            else:
                self._consume_connection.ioloop.stop()  # type: ignore[union-attr]
            LOGGER.info("Consumer connection stopped")

    # ------------------------------------------------------------------
    # Receive
    # ------------------------------------------------------------------

    @no_type_check
    def on_message(
        self,
        _unused_channel: PikaChannel,
        basic_deliver: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """Invoked by pika when a message arrives on the consumer queue.
        Parses the routing key into a RoutingEnvelope, acks the delivery, and
        hands the envelope plus raw body to ``dispatch_message`` for
        subclass-defined dispatch."""
        self.latest_routing_key = basic_deliver.routing_key
        LOGGER.debug(
            f"{self.alias}: Got {basic_deliver.routing_key} with delivery tag {basic_deliver.delivery_tag}",
        )
        self.acknowledge_message(basic_deliver.delivery_tag)

        try:
            envelope = parse_routing_key(basic_deliver.routing_key)
        except ValueError as e:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.ROUTING_KEY_PARSE_ERROR
            )
            LOGGER.warning(f"Could not parse routing key: {e}")
            return

        self._latest_on_message_diagnostic = (
            OnReceiveMessageDiagnostic.MESSAGE_DELIVERED
        )
        self.dispatch_message(envelope=envelope, body=body)

    # ------------------------------------------------------------------
    # RoutingEnvelope helpers — fill in from_alias / from_class from this actor
    # so subclasses only specify destination info.
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

    def wrapped_envelope(
        self,
        *,
        type_name: str,
        to_class: TransportClass,
    ) -> WrappedRoutingEnvelope:
        return WrappedRoutingEnvelope(
            type_name=type_name,
            from_alias=self.alias,
            to_class=to_class,
        )

    # ------------------------------------------------------------------
    # Subscriptions — bind this actor's queue to a publisher's exchange.
    # Call these from ``local_rabbit_startup`` (the queue must exist).
    # ------------------------------------------------------------------

    def subscribe_broadcast(
        self,
        *,
        from_alias: str,
        from_class: TransportClass,
        type_name: str,
        radio_channel: Optional[str] = None,
    ) -> None:
        """Subscribe to a publisher's ``JsonBroadcast`` messages.

        Broadcasts are *not* wired by the static cross-class fabric — a
        subscriber binds its own queue directly to the publisher's
        ``<from-class>mic_tx`` with the broadcast routing key (see wiki
        executor spec §3.5). Call from ``local_rabbit_startup`` once the
        queue exists. ``radio_channel`` selects a specific channel; omit it
        to bind the un-channeled broadcast key.
        """
        binding = BroadcastRoutingEnvelope(
            type_name=type_name,
            from_alias=from_alias,
            from_class=from_class,
            radio_channel=radio_channel,
        ).routing_key
        exchange = routing_code(from_class) + "mic_tx"
        LOGGER.info("Binding %s to %s with %s", self.queue_name, exchange, binding)
        self._single_channel.queue_bind(self.queue_name, exchange, routing_key=binding)

    def subscribe_amq_topic(self, *, binding_key: str) -> None:
        """Subscribe to messages on the built-in ``amq.topic`` exchange —
        the seam where AMQP meets MQTT-native peers (scada). This is how a
        gwbase AMQP actor receives a scada's ``gw`` (wrapped) messages, which
        RabbitMQ bridges from MQTT onto ``amq.topic`` (wiki executor spec
        §3.5). Call from ``local_rabbit_startup``.

        ``binding_key`` is supplied by the caller because the exact scada
        topic ↔ routing-key scheme is owned by gwproactor; the production
        form matches the ``WrappedRoutingEnvelope`` grammar
        (``gw.<from>.to.<to-class>.<inner-type>``), so e.g. a TerminalAsset
        subscribing to wrapped messages addressed to it would bind
        ``gw.*.to.ta.#``.
        """
        LOGGER.info("Binding %s to amq.topic with %s", self.queue_name, binding_key)
        self._single_channel.queue_bind(
            self.queue_name, "amq.topic", routing_key=binding_key
        )

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    def send(
        self,
        *,
        envelope: RoutingEnvelope,
        body: bytes,
        correlation_id: Optional[str] = None,
    ) -> OnSendMessageDiagnostic:
        """Publish pre-encoded ``body`` bytes on rabbit. The envelope
        carries the routing metadata (category, type_name, addressing);
        ActorBase does not open the body."""

        if self._stopping:
            return OnSendMessageDiagnostic.STOPPING_SO_NOT_SENDING
        if self._stopped:
            return OnSendMessageDiagnostic.STOPPED_SO_NOT_SENDING

        if isinstance(envelope, WrappedRoutingEnvelope):
            # Wrapped (gw) messages go to the built-in amq.topic so they reach
            # MQTT-native peers (e.g. scada). Any actor may send wrapped — the
            # wire format matches gwproactor's gw scheme (wiki spec §3.5).
            publish_exchange = "amq.topic"
        else:
            publish_exchange = self._publish_exchange

        routing_key = envelope.routing_key

        if self._single_channel is None or not self._single_channel.is_open:
            LOGGER.error(f"Channel not open so not sending {routing_key}")
            return OnSendMessageDiagnostic.CHANNEL_NOT_OPEN

        properties = pika.BasicProperties(
            reply_to=self.queue_name,
            app_id=self.alias,
            type=envelope.category.value,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )

        try:
            self._single_channel.basic_publish(
                exchange=publish_exchange,
                routing_key=routing_key,
                body=body,
                properties=properties,
            )
            LOGGER.debug(f" [x] Sent {envelope.type_name} w routing key {routing_key}")
            return OnSendMessageDiagnostic.MESSAGE_SENT
        except BaseException:
            LOGGER.exception("Problem publishing")
            return OnSendMessageDiagnostic.UNKNOWN_ERROR
