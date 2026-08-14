"""What an actor claims at the broker gate, and how the connection carries it.

Identity is not claimed here — it is proven by the client certificate. These
are the runtime assertions the gate checks against the registry and its lease
state, so what matters is that they come from the actor's live state.
"""

import subprocess

import pika
import pytest
from pydantic import SecretStr

from gwbase.actor_base import ActorBase, RoutingEnvelope
from gwbase.config.rabbit_settings import RabbitBrokerClient, RabbitTls
from gwbase.credentials import GridworksClaimsCredentials
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


@pytest.fixture
def throwaway_certs(tmp_path):
    """A self-signed CA + client cert, minted with openssl — just enough for
    ``ssl.SSLContext`` to load real files."""
    ca_key, ca = tmp_path / "ca.key", tmp_path / "ca.pem"
    key, csr, cert = (
        tmp_path / "client.key",
        tmp_path / "c.csr",
        tmp_path / "client.pem",
    )
    run = lambda *a: subprocess.run(a, check=True, capture_output=True)  # noqa: E731
    run(
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(ca_key),
        "-out",
        str(ca),
        "-days",
        "1",
        "-subj",
        "/CN=test-ca",
    )
    run(
        "openssl",
        "req",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(key),
        "-out",
        str(csr),
        "-subj",
        "/CN=00000000-0000-4000-8000-000000000000",
    )
    run(
        "openssl",
        "x509",
        "-req",
        "-in",
        str(csr),
        "-CA",
        str(ca),
        "-CAkey",
        str(ca_key),
        "-CAcreateserial",
        "-out",
        str(cert),
        "-days",
        "1",
    )
    return RabbitTls(ca_cert_path=ca, cert_path=cert, private_key_path=key)


def test_connection_parameters_without_tls_stay_on_password(
    make_service_settings,
) -> None:
    actor = _ServiceStub(settings=make_service_settings(service_alias="d1.super"))

    params = actor._connection_parameters()

    assert isinstance(params.credentials, pika.PlainCredentials)
    assert params.ssl_options is None


def test_connection_parameters_with_tls_carry_cert_and_claims(
    make_service_settings, throwaway_certs
) -> None:
    rabbit = RabbitBrokerClient(
        url=SecretStr("amqps://localhost:5671/d1__1"),
        tls=throwaway_certs,
    )
    actor = _ServiceStub(
        settings=make_service_settings(service_alias="d1.super", rabbit=rabbit)
    )

    params = actor._connection_parameters()

    assert params.ssl_options is not None
    assert params.ssl_options.server_hostname == "localhost"
    creds = params.credentials
    assert isinstance(creds, GridworksClaimsCredentials)
    # The claims come from the actor's live state; the run from the vhost.
    assert creds.claims.alias == "d1.super"
    assert creds.claims.instance_id == actor.instance_id
    assert creds.claims.run == "d1__1"
