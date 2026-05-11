import datetime
import logging
import random
import time
import uuid

import pika
from gw.named_types import GwBase
from gwbase.actor_base import ActorBase
from gwbase.enums import UniverseType
from gwbase.named_types import HeartbeatA, SimTimestep
from gwbase.transport_encoding import MessageCategory

LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class SupervisableActor(ActorBase):
    def __init__(self, settings, type_by_name=None):
        if type_by_name is None:
            super().__init__(settings=settings)
        else:
            super().__init__(settings=settings, type_by_name=type_by_name)
        self.universe_type: UniverseType = UniverseType(settings.universe_type_value)
        self._time: float = time.time()
        if self.universe_type == UniverseType.Dev:
            self._time = settings.initial_time_unix_s

    def route_message(
        self,
        from_alias: str,
        from_class,
        payload: GwBase,
    ) -> None:
        if payload.type_name == HeartbeatA.type_name_value:
            self._handle_heartbeat(from_alias=from_alias, payload=payload)
            return
        if payload.type_name == SimTimestep.type_name_value:
            try:
                self.timestep_from_timecoordinator(payload)
            except Exception:
                LOGGER.exception("Error in timestep_from_timecoordinator")
            return
        super().route_message(
            from_alias=from_alias,
            from_class=from_class,
            payload=payload,
        )

    def _handle_heartbeat(self, from_alias: str, payload: HeartbeatA) -> None:
        if from_alias != self.settings.my_super_alias:
            LOGGER.info("Ignoring HeartbeatA from non-supervisor")
            return
        self.heartbeat_from_super(from_alias=from_alias, ping=payload)

    def heartbeat_from_super(self, from_alias: str, ping: HeartbeatA) -> None:
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
        self._send_legacy_supervisor_message(pong)

        LOGGER.debug(
            f"[{self.alias}] Sent HB: SuHex {pong.your_last_hex}, AtnHex {pong.my_hex}",
        )

    def _send_legacy_supervisor_message(self, payload: GwBase) -> None:
        if "MessageId" in payload.to_dict():
            correlation_id = payload["MessageId"]
        else:
            correlation_id = str(uuid.uuid4())

        if self._single_channel is None or not self._single_channel.is_open:
            raise RuntimeError("Channel not open so not sending supervisor heartbeat")

        routing_key = ".".join(
            [
                MessageCategory.JsonDirect.value,
                self.alias.replace(".", "-"),
                self.routing_code,
                payload.type_name.replace(".", "-"),
                "supervisor",
                self.settings.my_super_alias.replace(".", "-"),
            ]
        )
        properties = pika.BasicProperties(
            reply_to=self.queue_name,
            app_id=self.alias,
            type=MessageCategory.JsonDirect,
            correlation_id=correlation_id,
        )
        self._single_channel.basic_publish(
            exchange=self._publish_exchange,
            routing_key=routing_key,
            body=payload.to_type(),
            properties=properties,
        )

    def timestep_from_timecoordinator(self, payload: SimTimestep) -> None:
        if self._time < payload.time_unix_s:
            self._time = payload.time_unix_s
            self.new_timestep(payload)
            LOGGER.debug(f"Time is now {self.time_str()}")
        elif self._time == payload.time_unix_s:
            self.repeat_timestep(payload)

    def new_timestep(self, payload: SimTimestep) -> None:
        ...

    def repeat_timestep(self, payload: SimTimestep) -> None:
        ...

    def time(self) -> float:
        if self.universe_type == UniverseType.Dev:
            return self._time
        return time.time()

    def time_str(self) -> str:
        timestamp = self.time()
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        return dt.strftime("%m/%d/%Y, %H:%M")
