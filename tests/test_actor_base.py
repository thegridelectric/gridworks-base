import datetime
import time
import uuid

from gwbase.sema import GwBaseSemaCodec
from gwbase.sema.types import HeartbeatA, SimTimestep
from gwbase.transport_encoding import (
    BroadcastRoutingEnvelope,
    DirectRoutingEnvelope,
    TransportClass,
    WrappedRoutingEnvelope,
    parse_routing_key,
)
from tests._stubs import (
    GNodeStubRecorder,
    SupervisorStubRecorder,
    TimeCoordinatorStubRecorder,
    provision_topology,
)
from tests._wait import wait_for


def test_parse_routing_key_json_direct() -> None:
    env = parse_routing_key("rj.d1-source.scada.report-event.scada.d1-super")
    assert isinstance(env, DirectRoutingEnvelope)
    assert env.from_alias == "d1.source"
    assert env.from_class == TransportClass.Scada
    assert env.type_name == "report.event"
    assert env.to_class == TransportClass.Scada
    assert env.to_alias == "d1.super"


def test_parse_routing_key_json_broadcast() -> None:
    env = parse_routing_key("rjb.d1-source.scada.report-event.ops.alerts")
    assert isinstance(env, BroadcastRoutingEnvelope)
    assert env.from_alias == "d1.source"
    assert env.from_class == TransportClass.Scada
    assert env.type_name == "report.event"
    assert env.radio_channel == "ops.alerts"


def test_parse_routing_key_wrapped() -> None:
    env = parse_routing_key("gw.d1-source.to.scada.report-event")
    assert isinstance(env, WrappedRoutingEnvelope)
    assert env.from_alias == "d1.source"
    assert env.type_name == "report.event"
    assert env.to_class == TransportClass.Scada


def test_parse_routing_key_supervisor() -> None:
    env = parse_routing_key("rj.d1-leaf.scada.heartbeat-a.super.d1-super1")
    assert isinstance(env, DirectRoutingEnvelope)
    assert env.from_class == TransportClass.Scada
    assert env.to_class == TransportClass.Supervisor


def test_actor_base(make_g_node_json, make_settings) -> None:
    codec = GwBaseSemaCodec()

    gn_settings = make_settings(
        make_g_node_json(
            "gn.json",
            alias="d1.isone.unknown.gnode",
            g_node_class="LeafTransactiveNode",
        ),
        transport_class=TransportClass.LeafTransactiveNode,
    )
    su_settings = make_settings(
        make_g_node_json("su.json", alias="d1.super", g_node_class="Scada"),
        transport_class=TransportClass.Supervisor,
    )
    tc_settings = make_settings(
        make_g_node_json("tc.json", alias="d1.time", g_node_class="TimeCoordinator"),
        transport_class=TransportClass.TimeCoordinator,
    )

    # Infra owns the fabric: provision exchanges + bindings BEFORE any actor
    # starts (actors only passively assert their consume exchange exists).
    provision_topology(gn_settings.rabbit.url.get_secret_value())

    gn = GNodeStubRecorder(
        settings=gn_settings,
        my_super_alias="d1.super",
        my_time_coordinator_alias="d1.time",
    )
    gn.start()
    su = SupervisorStubRecorder(
        settings=su_settings,
        my_super_alias="d1.super.parent",
        my_time_coordinator_alias="d1.time",
        subordinate_alias=gn.alias,
    )
    su.start()
    tc = TimeCoordinatorStubRecorder(
        settings=tc_settings,
        my_super_alias="d1.super",
        my_time_coordinator_alias="d1.time",
        current_time_unix_s=int(
            datetime.datetime(2020, 1, 1, 5, tzinfo=datetime.timezone.utc).timestamp(),
        ),
        my_actor_aliases=[gn.alias],
    )
    tc.start()
    try:
        wait_for(lambda: su._consuming, 4, "supervisor is consuming")
        wait_for(lambda: gn._consuming, 4, "gnode is consuming")
        wait_for(lambda: tc._consuming, 4, "timecoordinator is consuming")

        hb = HeartbeatA(my_hex="0", your_last_hex="0")
        gn.send(
            envelope=gn.direct_envelope(
                type_name=hb.type_name,
                to_class=TransportClass.Supervisor,
                to_alias=su.alias,
            ),
            body=codec.to_bytes(hb),
        )

        wait_for(lambda: su.messages_received > 0, 2, "supervisor received message")
        assert su.messages_received == 1
        assert su.messages_routed_internally == 1
        assert su.got_heartbeat_from_sub

        d = datetime.datetime(year=2020, month=1, day=1, hour=5)
        ts = SimTimestep(
            from_g_node_alias="d1.time",
            from_g_node_instance_id=str(uuid.uuid4()),
            time_unix_s=int(d.timestamp()),
            timestep_created_ms=1000 * int(time.time()),
            message_id=str(uuid.uuid4()),
        )
        _ = codec.to_bytes(ts)
    finally:
        gn.stop()
        su.stop()
        tc.stop()
