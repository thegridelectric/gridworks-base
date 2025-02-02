import datetime
import enum
import functools
import json
import logging
import random
import threading
import time
import uuid
from abc import ABC
from enum import auto
from typing import Dict, List, Optional, no_type_check

import pika
from gw import utils
from gw.enums import GwStrEnum
from gw.errors import GwTypeError
from gw.named_types import GwBase
from pika.channel import Channel as PikaChannel
from pika.spec import Basic, BasicProperties

from gwbase.codec import GwCodec
from gwbase.config import GNodeSettings
from gwbase.enums import GNodeRole, MessageCategory, MessageCategorySymbol, UniverseType
from gwbase.named_types import HeartbeatA, SimTimestep
from gwbase.named_types.asl_types import TypeByName
from gwbase.property_format import is_left_right_dot


class RabbitRole(GwStrEnum):
    atomictnode = auto()
    gnode = auto()
    marketmaker = auto()
    scada = auto()
    supervisor = auto()
    timecoordinator = auto()
    world = auto()
    ws = auto()

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]


RoleByRabbitRole: Dict[RabbitRole, GNodeRole] = {
    RabbitRole.atomictnode: GNodeRole.AtomicTNode,
    RabbitRole.gnode: GNodeRole.GNode,
    RabbitRole.marketmaker: GNodeRole.MarketMaker,
    RabbitRole.scada: GNodeRole.Scada,
    RabbitRole.supervisor: GNodeRole.Supervisor,
    RabbitRole.timecoordinator: GNodeRole.TimeCoordinator,
    RabbitRole.world: GNodeRole.World,
    RabbitRole.ws: GNodeRole.WeatherService,
}


RabbitRolebyRole: Dict[GNodeRole, RabbitRole] = {
    GNodeRole.AtomicTNode: RabbitRole.atomictnode,
    GNodeRole.GNode: RabbitRole.gnode,
    GNodeRole.MarketMaker: RabbitRole.marketmaker,
    GNodeRole.Scada: RabbitRole.scada,
    GNodeRole.Supervisor: RabbitRole.supervisor,
    GNodeRole.TimeCoordinator: RabbitRole.timecoordinator,
    GNodeRole.World: RabbitRole.world,
    GNodeRole.WeatherService: RabbitRole.ws,
}


class OnSendMessageDiagnostic(enum.Enum):
    CHANNEL_NOT_OPEN = "ChannelNotOpen"
    STOPPED_SO_NOT_SENDING = "StoppedSoNotSending"
    STOPPING_SO_NOT_SENDING = "StoppingSoNotSending"
    MESSAGE_SENT = "MessageSent"
    UNKNOWN_ERROR = "UnknownError"


class OnReceiveMessageDiagnostic(enum.Enum):
    TYPE_NAME_DECODING_PROBLEM = "TypeNameDecodingProblem"
    UNKNOWN_ROUTING_KEY_TYPE = "UnknownRoutingKeyType"
    UNHANDLED_ROUTING_KEY_TYPE = "UnhandledRoutingKeyType"
    UNKNOWN_MESSAGE_CATEGORY_SYMBOL = "UnknownMessageCategorySymbol"
    UNKNOWN_TYPE_NAME = "UnknownTypeName"
    FROM_GNODE_DECODING_PROBLEM = "FromGNodeDecodingProblem"
    UNKONWN_GNODE = "UnknownGNode"
    TO_DIRECT_ROUTING = "ToDirectRouting"


BACKOFF_NUMBER = 16

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class ActorBase(ABC):
    "This is the base class for GNodes, used to communicate via RabbitMQ"

    _url: str
    codec: GwCodec  # meant to be set by the derived object
    SHUTDOWN_INTERVAL: float = 0.1

    def __init__(
        self,
        settings: GNodeSettings,
        type_by_name: Dict[str, GwBase] = TypeByName,
    ):
        self.codec = GwCodec(type_by_name)
        # add gwbase types
        for name in TypeByName:
            if name not in self.codec.type_by_name:
                self.codec.type_by_name[name] = TypeByName[name]
        self.settings: GNodeSettings = settings
        self.latest_routing_key: Optional[str] = None
        self.shutting_down: bool = False
        self.alias: str = settings.g_node_alias
        self.g_node_instance_id: str = settings.g_node_instance_id
        self.g_node_role: GNodeRole = GNodeRole(settings.g_node_role_value)
        self.rabbit_role: RabbitRole = RabbitRolebyRole[self.g_node_role]
        self.universe_type: UniverseType = UniverseType(settings.universe_type_value)
        # Used for tracking time in simulated worlds
        self._time: float = time.time()
        if self.universe_type == UniverseType.Dev:
            self._time = settings.initial_time_unix_s
        self._main_loop_running: bool = False

        adder = "-F" + str(uuid.uuid4()).split("-")[0][0:3]
        self.queue_name: str = self.alias + adder
        self._consume_exchange: str = self.rabbit_role.value + "_tx"
        self._publish_exchange: str = self.rabbit_role.value + "mic_tx"

        self._consume_connection: Optional[
            pika.adapters.select_connection.SelectConnection
        ] = None
        self._single_channel: Optional[pika.channel.Channel] = None
        self._closing_consumer: bool = False
        self._consumer_tag: Optional[str] = None
        self.should_reconnect_consumer: bool = False
        self.was_consuming: bool = False
        self._consuming: bool = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count: int = 1
        self._reconnect_delay: int = 0
        self._url: str = settings.rabbit.url.get_secret_value()

        self.is_debug_mode: bool = False
        self.consuming_thread: threading.Thread = threading.Thread(
            target=self.run_reconnecting_consumer,
            daemon=True,
        )
        self.publishing_thread: threading.Thread = threading.Thread(
            target=self.run_publisher,
            daemon=True,
        )
        self._publish_connection: Optional[
            pika.adapters.select_connection.SelectConnection
        ] = None
        self._publish_channel: Optional[PikaChannel] = None
        self._stopping: bool = False
        self._stopped: bool = True
        self._latest_on_message_diagnostic: Optional[OnReceiveMessageDiagnostic] = None

    def start(self) -> None:
        self.local_start()
        self._stopped = False
        self.consuming_thread.start()
        # self.publishing_thread.start()

    def stop(self) -> None:
        self.shutting_down = True
        # self.stop_publisher()
        self.stop_consumer()
        self.local_stop()
        self.consuming_thread.join()
        # self.publishing_thread.join()
        self._stopping = False
        self._stopped = True

    def local_start(self) -> None:
        """This should be overwritten in derived class for additional threads.
        It cannot assume the rabbit channels are established and that
        messages can be received or sent."""
        self._main_loop_running = True

    def local_rabbit_startup(self) -> None:
        """This should be overwritten in derived class for any additional rabbit
        bindings. DO NOT start queues here.  It is called at the end of
        self.start_consuming()"""
        pass

    def local_stop(self) -> None:
        """Join any threads in the derived class."""
        self._main_loop_running = False

    @property
    def main_loop_running(self) -> bool:
        return self._main_loop_running

    @property
    def consuming(self) -> bool:
        return self._consuming

    def __repr__(self) -> str:
        return f"{self.alias}"

    ########################
    # Core Rabbit infrastructure
    ########################

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
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_consumer_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        LOGGER.info("Connecting to %s", self._url)
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
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
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        LOGGER.info("Connection opened")
        self.open_single_channel()

    def on_consumer_connection_open_error(
        self,
        _unused_connection: pika.SelectConnection,
        err: Exception,
    ) -> None:
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        LOGGER.error(f"Consumer connection open failed: {err}")
        self.reconnect_consumer()

    def on_consumer_connection_closed(
        self,
        _unused_connection: pika.SelectConnection,
        reason: Exception,
    ) -> None:
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
        connection.
        """
        self._single_channel = None
        if self._closing_consumer:
            self._consume_connection.ioloop.stop()  # type: ignore[union-attr]
        else:
            LOGGER.warning(f"Consumer connection closed, reconnect necessary: {reason}")
            self.reconnect_consumer()

    def reconnect_consumer(self) -> None:
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect_consumer = True
        self.stop_consumer()

    def open_single_channel(self) -> None:
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        LOGGER.info("Creating a new channel")
        self._consume_connection.channel(on_open_callback=self.on_consumer_channel_open)  # type: ignore

    @no_type_check
    def on_consumer_channel_open(self, channel: PikaChannel) -> None:
        """Invoked by pika when the channel has been successfully opened.

        This callback is triggered when the channel is opened, and it provides
        the channel object that can be used for further operations. In this case,
        we'll proceed to declare the exchange to be used.

        :param channel: The opened channel object.
        :type channel: PikaChannel
        """
        LOGGER.info("Channel opened")
        self._single_channel = channel
        self.add_on_single_channel_close_callback()
        self.setup_exchange()

    @no_type_check
    def add_on_single_channel_close_callback(self) -> None:
        """This method tells pika to call the on_consumer_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        LOGGER.info("Adding consumer channel close callback")
        self._single_channel.add_on_close_callback(self.on_consumer_channel_closed)

    @no_type_check
    def on_consumer_channel_closed(
        self,
        channel: PikaChannel,
        reason: Exception,
    ) -> None:
        """Invoked by pika when the RabbitMQ channel is unexpectedly closed.

        This callback is triggered when a channel is closed, usually due to
        violating the protocol by attempting to re-declare an exchange or queue
        with different parameters. In this case, the connection is closed to
        gracefully shutdown the object.

        :param channel: The closed channel object.
        :type channel: PikaChannel
        :param reason: why the channel was closed
        :type reason: Exception
        """
        LOGGER.warning("Consume channel %i was closed: %s", channel, reason)
        self.close_consumer_connection()

    @no_type_check
    def setup_exchange(self) -> None:
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        LOGGER.info("Declaring exchange: %s", self._consume_exchange)
        # Note: using functools.partial is not required, it is demonstrating
        # how arbitrary data can be passed to the callback when it is called
        cb = functools.partial(
            self.on_exchange_declareok,
            userdata=self._consume_exchange,
        )
        self._single_channel.exchange_declare(
            exchange=self._consume_exchange,
            exchange_type="topic",
            durable=True,
            internal=True,
            callback=cb,
        )

    @no_type_check
    def on_exchange_declareok(self, _unused_frame, userdata) -> None:
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        LOGGER.info("Exchange declared: %s", userdata)
        self.setup_queue()

    @no_type_check
    def setup_queue(self) -> None:
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        LOGGER.info(f"Declaring queue {self.queue_name}")
        cb = functools.partial(self.on_queue_declareok)
        self._single_channel.queue_declare(
            queue=self.queue_name,
            auto_delete=True,
            callback=cb,
        )

    @no_type_check
    def on_queue_declareok(self, _unused_frame) -> None:
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        lrh_alias = self.alias.replace(".", "-")
        rj = MessageCategorySymbol.rj.value
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
        """Invoked by pika when the Queue.Bind method has completed for direct messages. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        LOGGER.info(f"Queue {self.queue_name} bound with {binding}")
        self.set_qos()

    @no_type_check
    def set_qos(self) -> None:
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._single_channel.basic_qos(
            prefetch_count=self._prefetch_count,
            callback=self.on_basic_qos_ok,
        )

    @no_type_check
    def on_basic_qos_ok(self, _unused_frame) -> None:
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        LOGGER.info("QOS set to: %d", self._prefetch_count)
        self.start_consuming()

    @no_type_check
    def start_consuming(self) -> None:
        """This method sets up the consumer by first calling
        add_on_cancel_consumer_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
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
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        LOGGER.info("Adding consumer cancellation callback")
        self._single_channel.add_on_cancel_callback(self.on_consumer_cancelled)  # type: ignore

    @no_type_check
    def on_consumer_cancelled(self, method_frame) -> None:
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        LOGGER.info("Consumer was cancelled remotely, shutting down: %r", method_frame)
        if self._single_channel:
            self._single_channel.close()

    @no_type_check
    def acknowledge_message(self, delivery_tag) -> None:
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        LOGGER.debug(
            f"Acknowledging message {delivery_tag}",
        )
        self._single_channel.basic_ack(delivery_tag)

    def stop_consuming(self) -> None:
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._single_channel:
            LOGGER.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            cb = functools.partial(
                self.on_cancelconsumer_ok,
                userdata=self._consumer_tag,
            )
            self._single_channel.basic_cancel(self._consumer_tag, cb)  # type: ignore[arg-type]

    @no_type_check
    def on_cancelconsumer_ok(self, _unused_frame, userdata) -> None:
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_consumer_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)
        """
        self._consuming = False
        LOGGER.info(
            "RabbitMQ acknowledged the cancellation of the consumer: %s",
            userdata,
        )
        self.close_consumer_channel()
        self._closing_consumer = False

    def close_consumer_channel(self) -> None:
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        if self._single_channel:
            if (
                not self._single_channel.is_closing
                and not self._single_channel.is_closed
            ):
                self._single_channel.close()

    def run_consumer(self) -> None:
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """

        self._consume_connection = self.connect_consumer()
        self._consume_connection.ioloop.start()

    def stop_consumer(self) -> None:
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelconsumer_ok
        will be invoked by pika, which will then closing the channel and
        connection. If you want to use this with CTRL-C, figure out
        how to add back the commented out ioloop.start() below without error.
        """
        if not self._closing_consumer:
            self._closing_consumer = True
            LOGGER.info("Consumer connection stopping")
            if self._consuming:
                self.stop_consuming()
                # self._consume_connection.ioloop.start()
            else:
                self._consume_connection.ioloop.stop()  # type: ignore

            LOGGER.info("Consumer connection stopped")

    def connect_publisher(self) -> pika.SelectConnection:
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        LOGGER.info("Setting up publisher connection to %s", self._url)
        return pika.SelectConnection(
            pika.URLParameters(self._url),
            on_open_callback=self.on_publish_connection_open,
            on_open_error_callback=self.on_publish_connection_open_error,
            on_close_callback=self.on_publish_connection_closed,
        )

    @no_type_check
    def on_publish_connection_open(self, _unused_connection) -> None:
        """This method is called by pika once the publisher connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        LOGGER.info("Producer connection opened")
        self.open_publish_channel()

    @no_type_check
    def on_publish_connection_open_error(self, _unused_connection, err) -> None:
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        LOGGER.error("Producer connection open failed, reopening in 1 second: %s", err)
        self._publish_connection.ioloop.call_later(
            1,
            self._publish_connection.ioloop.stop,
        )

    @no_type_check
    def on_publish_connection_closed(self, _unused_connection, reason) -> None:
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
        connection.
        """
        self._publish_channel = None
        if self._stopping:
            self._publish_connection.ioloop.stop()
        else:
            LOGGER.warning("Connection closed, reopening in 1 second: %s", reason)
            self._publish_connection.ioloop.call_later(
                1,
                self._publish_connection.ioloop.stop,
            )

    def open_publish_channel(self) -> None:
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.
        """
        LOGGER.info("Creating a new publish channel")
        self._publish_connection.channel(on_open_callback=self.on_publish_channel_open)  # type: ignore

    @no_type_check
    def on_publish_channel_open(self, channel: PikaChannel) -> None:
        """Invoked by pika when the channel has been successfully opened.

        This callback is triggered when the channel is opened, and it provides
        the channel object that can be used for further operations. In this case,
        we'll proceed to declare the exchange to be used.

        :param channel: The opened channel object.
        :type channel: PikaChannel
        """
        LOGGER.info("Publish channel opened")
        self._publish_channel = channel
        self.add_on_publish_channel_close_callback()

    def add_on_publish_channel_close_callback(self) -> None:
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        LOGGER.info("Adding channel close callback")
        self._publish_channel.add_on_close_callback(self.on_publish_channel_closed)  # type: ignore

    @no_type_check
    def on_publish_channel_closed(
        self,
        channel: PikaChannel,
        reason: Exception,
    ) -> None:
        """Invoked by pika when the RabbitMQ channel is unexpectedly closed.

        This callback is triggered when a channel is closed, usually due to
        violating the protocol by attempting to re-declare an exchange or queue
        with different parameters. In this case, the connection is closed to
        gracefully shutdown the object.

        :param channel: The closed channel object.
        :type channel: PikaChannel
        :param reason: The reason why the channel was closed.
        :type reason: Exception
        """
        LOGGER.warning(f"Publish channel {channel} was closed: {reason}")
        self._publish_channel = None
        if not self._stopping:
            self._publish_connection.close()

    def run_publisher(self) -> None:
        """Run the example code by connecting and then starting the IOLoop."""
        while not self._stopping:
            self._publish_connection = None
            try:
                self._publish_connection = self.connect_publisher()
                self._publish_connection.ioloop.start()
            except KeyboardInterrupt:
                self.stop_publisher()
                if (
                    self._publish_connection is not None
                    and not self._publish_connection.is_closed
                ):
                    # Finish closing
                    self._publish_connection.ioloop.start()

        LOGGER.info("Stopped")

    def stop_publisher(self) -> None:
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. The IOLoop is started because this method is
        invoked by the Try/Catch below when KeyboardInterrupt is caught.
        Starting the IOLoop again will allow the publisher to cleanly
        disconnect from RabbitMQ.
        """
        LOGGER.info(
            "Stopping RabbitMq message production - closing channel and connection",
        )
        self._stopping = True
        self.close_publish_channel()
        self.close_publish_connection()

    def close_publish_channel(self) -> None:
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.
        """
        if self._publish_channel:
            if (
                not self._publish_channel.is_closing
                and not self._publish_channel.is_closed
            ):
                self._publish_channel.close()

    def close_publish_connection(self) -> None:
        """This method closes the production connection to RabbitMQ."""
        if self._publish_connection:
            if (
                not self._publish_connection.is_closing
                and not self._publish_connection.is_closed
            ):
                self._publish_connection.close()
                LOGGER.info("Closing publish connection")

    ########################
    # Message passing semantics
    ########################

    def get_version_from_dict(self, d: Dict) -> str:
        # Scada messages have TypeName gw
        if d["TypeName"] == "gw":
            payload_dict = d["Payload"]
        else:
            payload_dict = d
        if "Version" not in payload_dict.keys():
            raise GwTypeError(f"Missing Version! keys: {payload_dict.keys()}")
        return payload_dict["Version"]

    @no_type_check
    def get_type_name(self, basic_deliver, body: bytes) -> str:
        """The TypeName is a string that provides the strongly typed specification
            (API/ABI) for the incoming message. This is similar to knowing
            the protobuf name/method or the ABI name/method.

            The TypeName will articulate, in particular, how
            to decode the payload.

        Args:
            basic_deliver: the rabbit basic_deliver object
            body: the rabbit body object (i.e. the payload as incoming type)

        Returns:
            str: raises GwTypeError if the TypeName is not accessible.
            Otherwise returns the TypeName

        """
        # TODO: right now we encode this in the routing key. However, we
        # could also add it to a different basic_deliver property, which
        # might be easier for developers to grock.

        try:
            type_name = self.type_name_from_routing_key(
                routing_key=basic_deliver.routing_key,
            )
        except GwTypeError as e:
            LOGGER.info(f"Could not figure out TypeName: {e}")
            raise GwTypeError(f"{e}") from e
        # d = json.loads(body.decode("utf-8"))
        # # Scada messages have TypeName gw
        # if d["TypeName"] == "gw":
        #     payload_dict = d["Payload"]
        #     print(f"payload_dict keys are {payload_dict.keys()}")
        # else:
        #     payload_dict = d
        # if "Version" not in payload_dict.keys():
        #     raise GwTypeError(f"Missing Version! keys: {payload_dict.keys()}")
        # versioned_type_name = f"{type_name}.{payload_dict['Version']}"
        return type_name

    def broadcast_routing_key(
        self,
        payload: GwBase,
        radio_channel: Optional[str],
    ) -> str:
        msg_type = MessageCategorySymbol.rjb.value
        from_alias_lrh = self.alias.replace(".", "-")
        type_name_lrh = payload.type_name.replace(".", "-")
        from_role = self.rabbit_role.value
        if radio_channel is None:
            return f"{msg_type}.{from_alias_lrh}.{from_role}.{type_name_lrh}"
        else:
            try:
                is_left_right_dot(radio_channel)
            except ValueError as e:
                raise Exception(e) from e
            return f"{msg_type}.{from_alias_lrh}.{from_role}.{type_name_lrh}.{radio_channel}"

    def scada_routing_key(self, payload: GwBase) -> str:
        if self.g_node_role != GNodeRole.AtomicTNode:
            raise Exception("Only send messages to SCADA if role is AtomicTNode!")
        msg_type = MessageCategorySymbol.gw.value
        from_alias_lrh = self.alias.replace(".", "-")
        type_name_lrh = payload.type_name.replace(".", "-")

        # this follows the mqtt dirct pattern. Note "s" stands for "Scada.""
        scada_routing_key = f"{msg_type}.{from_alias_lrh}.to.s.{type_name_lrh}"
        return scada_routing_key

    def direct_routing_key(
        self,
        to_role: GNodeRole,
        payload: GwBase,
        to_g_node_alias: str,
    ) -> str:
        msg_type = MessageCategorySymbol.rj.value
        from_lrh_alias = self.alias.replace(".", "-")
        from_role = self.rabbit_role.value
        to_role_val = RabbitRolebyRole[to_role].value
        to_lrh_alias = to_g_node_alias.replace(".", "-")
        type_name_lrh = payload.type_name.replace(".", "-")

        direct_routing_key = f"{msg_type}.{from_lrh_alias}.{from_role}.{type_name_lrh}.{to_role_val}.{to_lrh_alias}"
        return direct_routing_key

    def message_category_from_routing_key(self, routing_key: str) -> MessageCategory:
        """Returns the MessageCategory of the message given the routing key.

        Raises a GwTypeError exception if there is a problem decoding the MessageCategory

        Args:
           routing_key (str): This is the basic_deliver.routing_key string
           in a rabbit message

        Returns:
           MessageCategory: the MessageCategory, as enum
        """
        routing_key_words = routing_key.split(".")
        msg_category_symbol_value = routing_key_words[0]

        try:
            msg_category_symbol = MessageCategorySymbol(msg_category_symbol_value)
        except ValueError as e:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.UNKNOWN_MESSAGE_CATEGORY_SYMBOL
            )
            raise GwTypeError(
                f"First  word of {routing_key} not a known MessageCategorySymbol!",
            ) from e
        msg_category = utils.message_category_from_symbol(msg_category_symbol)
        # both MqttDirect and MqttJsonBroadcast use the symbol 'gw'
        if msg_category == MessageCategory.MqttJsonBroadcast:
            if len(routing_key_words) <= 2:
                raise GwTypeError(
                    f"gw messages should not have just 2 words: {routing_key}"
                )
            if routing_key_words[2] == "to":
                if len(routing_key_words) != 5:
                    raise GwTypeError(
                        f"Expect MqttDirect messages to have 5 words! {routing_key}"
                    )
                msg_category = MessageCategory.MqttDirect

        allowable_categories = [
            MessageCategory.RabbitJsonDirect,
            MessageCategory.RabbitJsonBroadcast,
            MessageCategory.MqttJsonBroadcast,
            MessageCategory.MqttDirect,
        ]
        if msg_category not in allowable_categories:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.UNHANDLED_ROUTING_KEY_TYPE
            )
            raise GwTypeError(
                f"Rabbit messages do not handle {msg_category_symbol.value}",
            )
        return msg_category

    def type_name_from_routing_key(
        self,
        routing_key: str,
    ) -> str:
        """Returns the TypeName of the message given the routing key. Raises a GwTypeError
        exception if there is a problem decoding the TypeName, or if it does not have
        the appropriate left-right-dot format.

        Args:
            routing_key (str): This is the basic_deliver.routing_key string
            in a rabbit message

        Returns:
            str: the TypeName of the payload, in Lrd format
        """
        routing_key_words = routing_key.split(".")
        msg_category = self.message_category_from_routing_key(routing_key)
        if msg_category == MessageCategory.MqttJsonBroadcast:
            type_name_lrh = routing_key_words[2]
        elif msg_category == MessageCategory.MqttDirect:
            type_name_lrh = routing_key_words[4]
        else:
            type_name_lrh = routing_key_words[3]

        if not is_lrh_alias_format(type_name_lrh):
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.TYPE_NAME_DECODING_PROBLEM
            )
            raise GwTypeError(
                f"TypeName {type_name_lrh} in {routing_key} message not lrh_alias_format!",
            )
        type_name = type_name_lrh.replace("-", ".")
        return type_name

    def from_alias_from_routing_key(self, routing_key: str) -> str:
        """Returns the GNodeAlias in left-right-dot format. Raises a GwTypeError
        if there is trouble getting this.
        Args:
            routing_key (str): This is the basic_deliver.routing_key string
            in a rabbit message
        """
        routing_key_words = routing_key.split(".")
        try:
            from_g_node_alias_lrh = routing_key_words[1]
        except Exception as e:
            raise GwTypeError(f"{routing_key} must have at least two words!") from e

        if not is_lrh_alias_format(from_g_node_alias_lrh):
            raise GwTypeError(
                f"GNodeAlias not is_lrh_alias_format for routing key {routing_key}!",
            )
        from_g_node_alias = from_g_node_alias_lrh.replace("-", ".")
        return from_g_node_alias

    def from_role_from_routing_key(self, routing_key: str) -> GNodeRole:
        """Returns the GNodeRole that the message came from. Raises a GwTypeError
        if there is trouble getting this.
        Args:
            routing_key (str): basic_deliver.routing_key string
            in a rabbit message

        Raises:
            GwTypeError: Error in message construction

        Returns:
            GNodeRole: GNodeRole of the actor that sent the message
        """
        msg_category = self.message_category_from_routing_key(routing_key)
        if msg_category in {
            MessageCategory.MqttJsonBroadcast,
            MessageCategory.MqttDirect,
        }:
            raise Exception(
                "MqttJsonBroadcast & MqttDirect do not contain FromRole in routing key",
            )
        routing_key_words = routing_key.split(".")
        try:
            from_g_node_rabbit_role = routing_key_words[2]
        except Exception as e:
            raise GwTypeError(f"{routing_key} must have at least three words!") from e
        try:
            rabbit_role = RabbitRole(from_g_node_rabbit_role)
        except ValueError as e:
            raise GwTypeError(
                f"Unknown short alias {from_g_node_rabbit_role} in {routing_key}"
                f" Must belong to {RabbitRole}",
            ) from e

        return RoleByRabbitRole[rabbit_role]

    @no_type_check
    def send_message(
        self,
        payload: GwBase,
        message_category: MessageCategory = MessageCategory.RabbitJsonDirect,
        to_role: Optional[GNodeRole] = None,
        to_g_node_alias: Optional[str] = None,
        radio_channel: Optional[str] = None,
    ) -> OnSendMessageDiagnostic:
        """Publish a direct message to another GNode in the registry world. The only type
        of direct messages in the registry use json (i.e. no more streamlined serial encoding),
        unlike in non-registry worlds.

        Args:
            payload: Any GridWorks types with a json content-type
            that includes TypeName as a json key, and has to_type()
            as an encoding method.
            routing_key_type: for creating routing key
            to_role (Optional[GNodeRole]): used if a direct message
            to_g_node_alias (str): used if a direct message

        Returns:
            OnSendMessageDiagnostic: MESSAGE_SENT with success, otherwise some
            description of why the message was not sent.
        """
        if self._stopping:
            return OnSendMessageDiagnostic.STOPPING_SO_NOT_SENDING
        if self._stopped:
            return OnSendMessageDiagnostic.STOPPED_SO_NOT_SENDING

        if "MessageId" in payload.to_dict():
            correlation_id = payload["MessageId"]
        else:
            correlation_id = str(uuid.uuid4())

        properties = pika.BasicProperties(
            reply_to=self.queue_name,
            app_id=self.alias,
            type=message_category,
            correlation_id=correlation_id,
        )
        print(f"type is {message_category}")
        publish_exchange = self._publish_exchange
        if message_category == MessageCategory.RabbitJsonDirect:
            if not isinstance(to_role, GNodeRole):
                raise Exception("Must include to_role for a direct message")
            try:
                is_left_right_dot(to_g_node_alias)
            except Exception as e:
                raise Exception(
                    f"to_g_node_alias must have LrdAliasFormat. Got {to_g_node_alias}",
                ) from e
            routing_key = self.direct_routing_key(
                to_role=to_role,
                payload=payload,
                to_g_node_alias=to_g_node_alias,
            )
        elif message_category == MessageCategory.RabbitJsonBroadcast:
            routing_key = self.broadcast_routing_key(
                payload=payload,
                radio_channel=radio_channel,
            )
        elif message_category == MessageCategory.MqttDirect:
            routing_key = self.scada_routing_key(
                payload=payload,
            )
            publish_exchange = "amq.topic"
        else:
            raise Exception(f"Does not handle MessageCategory {message_category}")

        # if self._publish_channel is None:
        #     LOGGER.error(f"No publish channel so not sending {routing_key}")
        #     return OnSendMessageDiagnostic.CHANNEL_NOT_OPEN
        # if not self._publish_channel.is_open:
        #     LOGGER.error(f"Publish channel not open so not sending {routing_key}")
        #     return OnSendMessageDiagnostic.CHANNEL_NOT_OPEN

        if self._single_channel is None:
            LOGGER.error(f"No channel so not sending {routing_key}")
            return OnSendMessageDiagnostic.CHANNEL_NOT_OPEN
        if not self._single_channel.is_open:
            LOGGER.error(f"Channel not open so not sending {routing_key}")
            return OnSendMessageDiagnostic.CHANNEL_NOT_OPEN

        try:
            self._single_channel.basic_publish(
                exchange=publish_exchange,
                routing_key=routing_key,
                body=payload.to_type(),
                properties=properties,
            )
            # self._publish_channel.basic_publish(
            #     exchange=self._publish_exchange,
            #     routing_key=routing_key,
            #     body=payload.to_type(),
            #     properties=properties,
            # )
            LOGGER.debug(
                f" [x] Sent {payload.type_name_value} w routing key {routing_key}"
            )
            return OnSendMessageDiagnostic.MESSAGE_SENT

        except BaseException:
            LOGGER.exception("Problem publishing w consume channel")
            # LOGGER.exception("Problem w publish channel")
            return OnSendMessageDiagnostic.UNKNOWN_ERROR

    #################################################
    # Receiving messages
    #################################################

    @no_type_check
    def on_message(
        self,
        _unused_channel: PikaChannel,
        basic_deliver: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        """
        Invoked by pika when a message is delivered from RabbitMQ. If a message
        does not get here that you expect should get here, check the routing key
        of the outbound message and the rabbitmq bindings.

        Parses the TypeName of the message payload and the GNodeAlias of the sender.
        If it recognizes the GNode and the TypeName, then it sends the message on to
        the check_routing function, which will be defined in a child class (e.g., the
        GNodeFactoryActorBase if the actor is a GNodeFactory).

        From RabbitMQ: The channel is passed for your convenience. The basic_deliver
        object that is passed in carries the exchange, delivery tag, and a redelivered
        flag for the message. The properties passed in is an instance of BasicProperties
        with the message properties including the routing key. The body is the message
        that was sent.

        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.spec.Basic.Deliver basic_deliver: The basic.deliver method
        :param pika.spec.BasicProperties properties: The message properties including the routing key
        :param bytes body: The message body
        """
        self.latest_routing_key = basic_deliver.routing_key
        LOGGER.debug(
            f"{self.alias}: Got {basic_deliver.routing_key} with delivery tag {basic_deliver.delivery_tag}",
        )
        self.acknowledge_message(basic_deliver.delivery_tag)
        try:
            type_name = self.get_type_name(basic_deliver, body)
        except GwTypeError as e:
            print(
                f"Did not get type name from routing key {basic_deliver.routing_key}: {e}"
            )
            return
        if type_name not in self.codec.type_list:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.UNKNOWN_TYPE_NAME
            )
            LOGGER.warning(
                f"IGNORING MESSAGE. {self._latest_on_message_diagnostic}: {type_name}",
            )
            return
        this_type = self.codec.type_by_name[type_name]
        try:
            data = json.loads(body)
        except Exception as e:
            LOGGER.warning(f"json.loads failed! {e}")
            return
        try:
            version = self.get_version_from_dict(data)
        except GwTypeError as e:
            LOGGER.warning(e)
            return
        routing_key: str = basic_deliver.routing_key
        msg_category = self.message_category_from_routing_key(routing_key)
        try:
            from_alias = self.from_alias_from_routing_key(routing_key)
        except GwTypeError as e:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.FROM_GNODE_DECODING_PROBLEM
            )
            LOGGER.warning(
                f"IGNORING MESSAGE. {self._latest_on_message_diagnostic}: {e}",
            )
            return
        try:
            payload = self.codec.from_type(body)
        except Exception:
            # self.bad_body = json.loads(body.decode("utf-8"))
            LOGGER.warning(
                f"Decode failed for Inbound {type_name}, Version {version} from {from_alias} - ",
                f"expected version {this_type.version_value()}.",
            )
            return
        if msg_category in {
            MessageCategory.MqttJsonBroadcast,
            MessageCategory.MqttDirect,
        }:
            self.route_mqtt_message(from_alias=from_alias, payload=payload)
            return
        try:
            from_role = self.from_role_from_routing_key(routing_key)
        except GwTypeError as e:
            self._latest_on_message_diagnostic = (
                OnReceiveMessageDiagnostic.FROM_GNODE_DECODING_PROBLEM
            )
            LOGGER.warning(
                f"IGNORING MESSAGE. {self._latest_on_message_diagnostic}: {e}",
            )
            return

        self._latest_on_message_diagnostic = (
            OnReceiveMessageDiagnostic.TO_DIRECT_ROUTING
        )
        self.route_message(
            from_alias=from_alias,
            from_role=from_role,
            payload=payload,
        )

    ########################
    ## Receives
    ########################

    def route_message(
        self,
        from_alias: str,
        from_role: GNodeRole,
        payload: GwBase,
    ) -> None:
        """
        Base class for message routing in GNode Actors, handling interactions
        with the Supervisor and TimeCoordinator.

        Derived classes are expected to implement their own `route_message` method.
        It is recommended to call `super().route_message(from_alias, from_role, payload)`
        at the end of the method if the message has not been routed yet.
        """

        if payload.type_name == HeartbeatA.type_name_value:
            if from_role != GNodeRole.Supervisor:
                LOGGER.info(
                    f"Ignoring HeartbeatA from GNode {from_alias} with GNodeRole {from_role}; expects"
                    f"Supervisor as the GNodeRole",
                )
                return
            elif from_alias != self.settings.my_super_alias:
                LOGGER.info(
                    f"Ignoring HeartbeatA from supervisor {from_alias}; "
                    f"my supervisor is {self.settings.my_super_alias}",
                )
                return

            try:
                self.heartbeat_from_super(from_alias, payload)
            except Exception:
                LOGGER.exception("Error in heartbeat_received")
        elif payload.type_name == SimTimestep.type_name_value:
            try:
                self.timestep_from_timecoordinator(payload)
            except Exception:
                LOGGER.exception("Error in timestep_from_timecoordinator")

    def route_mqtt_message(self, from_alias: str, payload: GwBase) -> None:
        """
        Base class for message routing from SCADA actors, which use
        MessageCategory.MqttJsonBroadcast

        This is only intended to be used for AtomicTNodes and Ears.
        """
        ...

    def heartbeat_from_super(self, from_alias: str, ping: HeartbeatA) -> None:
        """
        Subordinate GNode responds to its supervisor's heartbeat with a "pong" message.

        Both the received heartbeat (ping) and the response (pong) have the type HeartbeatA
        (see: https://gridworks.readthedocs.io/en/latest/apis/types.html#heartbeata).

        The subordinate GNode generates its own unique identifier (hex) and includes it
        in the pong message along with the heartbeat it received from the supervisor.

        Note that the subordinate GNode does not have the responsibility of verifying
        the authenticity of the last heartbeat received from the supervisor - although typically,
        the supervisor does send the last heartbeat from this GNode (except during the initial
        heartbeat exchange).

        Args:
            from_alias (str): the alias of the GNode that sent the ping.
            ping (HeartbeatA): the heartbeat sent.

        Raises:
        ValueError: If `from_alias` is not this GNode's Supervisor alias.

        """
        if from_alias != self.settings.my_super_alias:
            raise ValueError(
                f"from_alias {from_alias} does not match my supervisor"
                f" {self.settings.my_super_alias}. This message should"
                f"have been filtered out in the route_message method.",
            )

        pong = HeartbeatA(
            my_hex=str(random.choice("0123456789abcdef")),
            your_last_hex=ping.my_hex,
        )
        self.send_message(
            payload=pong,
            to_role=GNodeRole.Supervisor,
            to_g_node_alias=self.settings.my_super_alias,
        )

        LOGGER.debug(
            f"[{self.alias}] Sent HB: SuHex {pong.your_last_hex}, AtnHex {pong.my_hex}",
        )

    ########################
    ## Time related (simulated time)
    ########################

    def timestep_from_timecoordinator(self, payload: SimTimestep) -> None:
        if self._time < payload.time_unix_s:
            self._time = payload.time_unix_s
            self.new_timestep(payload)
            LOGGER.debug(f"Time is now {self.time_str()}")
        elif self._time == payload.time_unix_s:
            self.repeat_timestep(payload)

    def new_timestep(self, payload: SimTimestep) -> None:
        ...
        # LOGGER.info("New timestep")

    def repeat_timestep(self, payload: SimTimestep) -> None:
        ...
        # LOGGER.info("Timestep received again in atn_actor_base")

    def time(self) -> float:
        if self.universe_type == UniverseType.Dev:
            return self._time
        else:
            return time.time()

    def time_str(self) -> str:
        timestamp = self.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        return dt.strftime("%m/%d/%Y, %H:%M")

    ###############################
    # Other GNode-related methods
    ###############################

    @property
    def short_alias(self) -> str:
        return self.alias.split(".")[-1]


def is_lrh_alias_format(candidate: str) -> bool:
    """AlphanumericStrings separated by hyphens, with most
    significant word to the left.  I.e. `d1.ne` is the child of `d1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter"""
    try:
        x = candidate.split("-")
    except:  # noqa
        return False
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        return False
    for word in x:
        if not word.isalnum():
            return False
    if not candidate.islower():
        return False
    return True
