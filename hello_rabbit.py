"""Demo: a tiny Supervisor pings a HelloGNode; the gnode pongs back.

Run from the repo root::

    .venv/bin/python hello_rabbit.py

Logging is configured to DEBUG so you can see the pong (``Sent HB pong``)
that ``GridworksActor`` emits when it answers its supervisor.

Requires a rabbit broker reachable via the URL in GNodeSettings.rabbit (the
default points at amqp://smqPublic:smqPublic@localhost:5672/d1__1) with the
standard exchange topology (``<rc>_tx`` consume, ``<rc>mic_tx`` publish,
and bindings from ``supermic_tx`` to ``scada_tx`` for direct messages).
"""

import json
import logging
import random
import tempfile
import time
import uuid
from pathlib import Path

from gwbase.config import GNodeSettings
from gwbase.config.rabbit_settings import RabbitBrokerClient
from gwbase.gridworks_actor import GridworksActor
from gwbase.sema.types import HeartbeatA
from gwbase.sema.wrapped import unwrap_bytes, wrap_bytes
from gwbase.transport_encoding import RoutingEnvelope, TransportClass

LOGGER = logging.getLogger(__name__)


def write_g_node_json(path: Path, *, alias: str, g_node_class: str = "Scada") -> None:
    path.write_text(
        json.dumps(
            {
                "GNodeId": str(uuid.uuid4()),
                "Alias": alias,
                "BaseClass": "Logical",
                "GNodeClass": g_node_class,
                "Status": "Active",
                "TypeName": "g.node.gt",
                "Version": "004",
            }
        )
    )


class HelloGNode(GridworksActor):
    """Application actor with no per-message logic. The control-plane
    pong is sent by ``GridworksActor`` itself; we log when it happens via
    the ``on_supervisor_heartbeat`` hook.

    Holds NO ``SemaCodec``: a ``SemaType`` already serializes itself via
    ``to_bytes()``, and ``wrap_bytes`` / ``unwrap_bytes`` operate on
    dicts. ``GwBaseSemaCodec`` stays out of application scope.
    """

    def __init__(self, *, settings: GNodeSettings, my_super_alias: str):
        super().__init__(
            settings=settings,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias="d1.time",
        )

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        LOGGER.debug(
            "[%s] ignoring app message %s from %s",
            self.alias,
            envelope.type_name,
            envelope.from_alias,
        )

    def on_supervisor_heartbeat(self, *, from_alias: str) -> None:
        LOGGER.info("[%s] got heartbeat from supervisor %s", self.alias, from_alias)


class TinySupervisor(GridworksActor):
    """Supervisor for one subordinate. Sends a direct ``heartbeat.a`` on
    demand; the subordinate's ``GridworksActor`` answers automatically."""

    def __init__(self, *, settings: GNodeSettings, sub_alias: str):
        super().__init__(
            settings=settings,
            # A real supervisor would itself have an upstream supervisor and
            # time coordinator; for the demo they are inert placeholders.
            my_super_alias="d1.super.parent",
            my_time_coordinator_alias="d1.time",
        )
        self._sub_alias = sub_alias

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        # Pongs from the sub show up here (HeartbeatA from sub_alias is not
        # the control-plane case — that's the *incoming-from-supervisor*
        # case — so it falls through to the application).
        LOGGER.info(
            "[%s] received %s from %s",
            self.alias,
            envelope.type_name,
            envelope.from_alias,
        )

    def ping(self) -> None:
        hb = HeartbeatA(
            my_hex=random.choice("0123456789abcdef"),
            your_last_hex="0",
        )
        LOGGER.info("[%s] sending heartbeat to %s", self.alias, self._sub_alias)
        self.send(
            envelope=self.direct_envelope(
                type_name=hb.type_name,
                to_class=TransportClass.Scada,
                to_alias=self._sub_alias,
            ),
            body=hb.to_bytes(),
        )


def _wait_for_consuming(actor: GridworksActor, timeout_s: float = 5.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if actor._consuming:
            return
        time.sleep(0.05)
    raise RuntimeError(f"{actor.alias} did not start consuming within {timeout_s}s")


def demo() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # Tame pika's chatter so the gnode/supervisor logs stand out.
    logging.getLogger("pika").setLevel(logging.WARNING)

    sub_alias = "d1.hello"
    sup_alias = "d1.super1"

    input(
        "Go to http://0.0.0.0:15672/#/queues/d1__1/dummy_ear_q and purge "
        "the messages from the dummy ear queue, then press return."
    )

    with tempfile.TemporaryDirectory() as tmp:
        sub_json = Path(tmp) / "sub.json"
        sup_json = Path(tmp) / "sup.json"
        write_g_node_json(sub_json, alias=sub_alias, g_node_class="Scada")
        write_g_node_json(sup_json, alias=sup_alias, g_node_class="Scada")

        sub_settings = GNodeSettings(
            g_node_path=sub_json,
            transport_class=TransportClass.Scada,
            rabbit=RabbitBrokerClient(),
        )
        sup_settings = GNodeSettings(
            g_node_path=sup_json,
            transport_class=TransportClass.Supervisor,
            rabbit=RabbitBrokerClient(),
        )

        gn = HelloGNode(settings=sub_settings, my_super_alias=sup_alias)
        sv = TinySupervisor(settings=sup_settings, sub_alias=sub_alias)

        gn.start()
        sv.start()
        _wait_for_consuming(gn)
        _wait_for_consuming(sv)

        input(
            f"Both actors are consuming. Look for {sub_alias}-Fxxx and "
            f"{sup_alias}-Fxxx queues at http://0.0.0.0:15672/#/queues, "
            "then press return to ping."
        )

        sv.ping()
        # Give rabbit a moment to deliver the ping and the pong.
        time.sleep(1.0)

        # --------------------------------------------------------------
        # Broadcast + `gw` wrap/unwrap demo (unchanged from before).
        # --------------------------------------------------------------
        hb = HeartbeatA(my_hex="0", your_last_hex="a")
        body = hb.to_bytes()
        LOGGER.info("Broadcasting a heartbeat: %s", body.decode())
        gn.send(
            envelope=gn.broadcast_envelope(type_name=hb.type_name),
            body=body,
        )

        wrapped = wrap_bytes(
            src=gn.alias,
            dst="d1.peer.scada",
            inner_type_name=hb.type_name,
            inner_payload_dict=hb.to_dict(),
            ack_required=True,
        )
        LOGGER.info("Wrapped gw envelope: %s", wrapped.decode())
        header, payload_dict = unwrap_bytes(wrapped)
        hb_back = HeartbeatA.from_dict(payload_dict)
        LOGGER.info(
            "Unwrapped: message_type=%s src=%s dst=%s ack_required=%s inner=%r",
            header.message_type, header.src, header.dst, header.ack_required, hb_back,
        )
        assert hb_back == hb

        input("Hit return to tear down both actors.")
        gn.stop()
        sv.stop()
        input(f"Verify {sub_alias}-Fxxx and {sup_alias}-Fxxx are gone from rabbit.")


if __name__ == "__main__":
    demo()
