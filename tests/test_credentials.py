"""Unit tests for the GridWorks SASL credentials class."""

import json

import pika
import pytest
from pika.spec import Connection

from gwbase.credentials import GridworksClaimsCredentials
from gwbase.sema.types import FisConnectClaims

CLAIMS = FisConnectClaims(
    alias="hw1.isone.weather",
    instance_id="0f6a2f7e-6f2d-4a8b-9c3e-2d1b4a5c6e7f",
    run="hw1__1",
    g_node_class="WeatherForecastService",
)


def _start(mechanisms: str) -> Connection.Start:
    return Connection.Start(mechanisms=mechanisms)


def test_answers_when_the_broker_offers_the_mechanism() -> None:
    mech, response = GridworksClaimsCredentials(CLAIMS).response_for(
        _start("GRIDWORKS PLAIN")
    )

    assert mech == "GRIDWORKS"
    assert response is not None
    # The payload is the sema word on the wire: PascalCase keys, and the
    # TypeName/Version that let the far side decode it as a known word.
    assert json.loads(response.decode()) == {
        "Alias": "hw1.isone.weather",
        "InstanceId": "0f6a2f7e-6f2d-4a8b-9c3e-2d1b4a5c6e7f",
        "Run": "hw1__1",
        "GNodeClass": "WeatherForecastService",
        "TypeName": "fis.connect.claims",
        "Version": "000",
    }


def test_declines_when_the_mechanism_is_not_offered() -> None:
    """A broker that has not been switched over yet must read as an ordinary
    negotiation miss, so pika can fall through to another credentials type."""
    assert GridworksClaimsCredentials(CLAIMS).response_for(
        _start("PLAIN AMQPLAIN")
    ) == (None, None)


def test_does_not_match_a_mechanism_that_merely_contains_the_name() -> None:
    assert GridworksClaimsCredentials(CLAIMS).response_for(
        _start("GRIDWORKS-EXTRA")
    ) == (None, None)


def test_registered_with_pika_so_connection_parameters_accept_it() -> None:
    """Pika rejects a credentials object whose class it does not know, so
    this asserts the module registered itself. (Pika copies the object, so
    equality rather than identity is the check.)"""
    creds = GridworksClaimsCredentials(CLAIMS)
    assert pika.ConnectionParameters(credentials=creds).credentials.claims == CLAIMS


def test_holds_no_secret_to_erase() -> None:
    creds = GridworksClaimsCredentials(CLAIMS)
    assert creds.erase_on_connect is False

    creds.erase_credentials()

    assert creds.claims == CLAIMS


def test_claims_are_validated_on_construction() -> None:
    with pytest.raises(ValueError):
        FisConnectClaims(
            alias="hw1.isone.weather",
            instance_id="not-a-uuid",
            run="hw1__1",
        )
