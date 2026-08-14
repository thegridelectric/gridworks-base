"""What an actor claims at the broker gate.

Identity is not claimed here — it is proven by the client certificate. These
are the runtime assertions the gate checks against the registry and its lease
state, so what matters is that they come from the actor's live state.
"""

from gwbase.actor_base import ActorBase, RoutingEnvelope
from gwbase.sema.types import FisConnectClaims
from gwbase.transport_encoding import TransportClass
from tests._stubs import GNodeStubRecorder


class _ServiceStub(ActorBase):
    """A non-GNode service actor — the plain-principal case."""

    def dispatch_message(
        self, *, envelope: RoutingEnvelope, body: bytes
    ) -> None:  # pragma: no cover - claims need no message flow
        raise NotImplementedError


def test_service_claims_carry_no_gnode_class(make_service_settings) -> None:
    actor = _ServiceStub(settings=make_service_settings(service_alias="d1.super"))

    claims = actor._connect_claims(run="hw1__1")

    assert isinstance(claims, FisConnectClaims)
    assert claims.alias == "d1.super"
    assert claims.instance_id == actor.instance_id
    assert claims.run == "hw1__1"
    # Absence is the gate's discriminator that this is a service, not a GNode.
    assert claims.g_node_class is None


def test_gnode_claims_carry_the_class(make_g_node_json, make_gnode_settings) -> None:
    alias = "d1.isone.unknown.gnode"
    settings = make_gnode_settings(
        make_g_node_json("gn.json", alias=alias, g_node_class="LeafTransactiveNode"),
        service_alias=alias,
    )
    actor = GNodeStubRecorder(
        settings=settings,
        transport_class=TransportClass.LeafTransactiveNode,
        my_super_alias="d1.super",
        my_time_coordinator_alias="d1.time",
    )

    claims = actor._connect_claims(run="hw1__1")

    assert claims.alias == alias
    assert claims.g_node_class == "LeafTransactiveNode"
    assert claims.instance_id == actor.instance_id


def test_claims_reject_a_run_that_is_not_a_universe_run(
    make_service_settings,
) -> None:
    """The dev broker's '/' vhost is not a run: claims are only meaningful on
    a fabric whose vhost names the universe and run."""
    actor = _ServiceStub(settings=make_service_settings(service_alias="d1.super"))

    try:
        actor._connect_claims(run="/")
    except ValueError:
        return
    raise AssertionError("expected a validation error for run='/'")
