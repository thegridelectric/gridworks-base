from gwbase.gridworks_actor import GridworksActor
from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import HeartbeatA
from gwbase.transport_encoding import RoutingEnvelope, TransportClass
from tests._stubs import provision_topology
from tests._wait import wait_for


class HelloGNode(GridworksActor):
    def __init__(self, *, settings, my_super_alias, my_time_coordinator_alias):
        super().__init__(
            settings=settings,
            my_super_alias=my_super_alias,
            my_time_coordinator_alias=my_time_coordinator_alias,
        )
        self._codec = GwBaseSemaCodec()

    def process_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        return


def test_hello(make_g_node_json, make_settings) -> None:
    # scada is MQTT-only (no AMQP exchanges); the demo actor is a
    # LeafTransactiveNode, which has a ltn_tx / ltnmic_tx pair.
    json_path = make_g_node_json(alias="d1.hello", g_node_class="LeafTransactiveNode")
    settings = make_settings(
        json_path, transport_class=TransportClass.LeafTransactiveNode
    )

    # Provision the fabric before the actor starts (passive consume-exchange
    # assert needs ltn_tx to already exist).
    provision_topology(settings.rabbit.url.get_secret_value())

    gn = HelloGNode(
        settings=settings,
        my_super_alias="d1.super1",
        my_time_coordinator_alias="d1.time",
    )
    gn.start()
    try:
        wait_for(lambda: gn._consuming, 4, "gnode is consuming")
        hb = HeartbeatA(my_hex="a", your_last_hex="0")
        gn.send(
            envelope=gn.broadcast_envelope(type_name=hb.type_name),
            body=gn._codec.to_bytes(hb),
        )
    finally:
        gn.stop()
