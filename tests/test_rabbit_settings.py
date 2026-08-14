"""Boot-time invariants on the broker URL.

The vhost is the ``universe.run`` being joined; the universe ladder (gnr
executor "Universes") pins which kinds exist and where dev may live. These
checks fire at settings construction, so a bad URL fails the boot, not the
first connect.
"""

import pytest
from pydantic import SecretStr, ValidationError

from gwbase.config.rabbit_settings import RabbitBrokerClient, RabbitTls


def _client(url: str, **kwargs) -> RabbitBrokerClient:
    return RabbitBrokerClient(url=SecretStr(url), **kwargs)


def test_default_is_a_dev_universe_on_localhost() -> None:
    client = RabbitBrokerClient()
    assert client.run == "d1__1"
    assert client.universe == "d1"


def test_hybrid_universe_on_a_real_host() -> None:
    client = _client("amqps://hw1-1.electricity.works:5671/hw1__1")
    assert client.run == "hw1__1"
    assert client.universe == "hw1"


def test_production_universe_is_exactly_w() -> None:
    assert _client("amqps://w-1.electricity.works:5671/w__1").universe == "w"


@pytest.mark.parametrize(
    "url",
    [
        # dev must be on localhost — a remote d-universe breaks the dev
        # rung's isolation guarantee
        "amqp://smqPublic:x@somebox.example.com:5672/d1__1",
        # ...and localhost must be dev — a local hw1 is a masquerade
        "amqp://smqPublic:x@localhost:5672/hw1__1",
        "amqp://smqPublic:x@127.0.0.1:5672/hw1__1",
    ],
)
def test_localhost_iff_dev(url: str) -> None:
    with pytest.raises(ValidationError, match="does not fit universe"):
        _client(url)


@pytest.mark.parametrize(
    "url,complaint",
    [
        # w is THE production universe; w1 is not a universe
        ("amqps://w1.electricity.works:5671/w1__1", "unknown universe kind"),
        ("amqps://x.electricity.works:5671/x1__1", "unknown universe kind"),
        # Rabbit's bare default vhost is not a run
        ("amqp://smqPublic:x@localhost:5672/", "universe.run"),
        ("amqp://smqPublic:x@localhost:5672/%2F", "universe.run"),
        ("amqp://smqPublic:x@localhost:5672/hw1__01", "universe.run"),
    ],
)
def test_vhost_must_be_a_ladder_universe_run(url: str, complaint: str) -> None:
    with pytest.raises(ValidationError, match=complaint):
        _client(url)


def test_tls_block_requires_amqps() -> None:
    with pytest.raises(ValidationError, match="requires amqps"):
        _client(
            "amqp://smqPublic:x@localhost:5672/d1__1",
            tls=RabbitTls(
                ca_cert_path="/certs/ca.pem",
                cert_path="/certs/client.pem",
                private_key_path="/certs/client.key",
            ),
        )


def test_tls_block_demands_all_three_paths() -> None:
    with pytest.raises(ValidationError):
        RabbitTls(ca_cert_path="/certs/ca.pem")
