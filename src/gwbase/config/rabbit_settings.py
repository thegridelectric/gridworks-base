from pathlib import Path
from urllib.parse import unquote, urlparse

from pydantic import BaseModel, SecretStr, model_validator

from gwbase.transport_format import Universe, UniverseRun, universe_of

_LOCAL_HOSTS = {"localhost", "127.0.0.1"}


class RabbitTls(BaseModel):
    """Client-certificate material for mTLS. The presence of this block
    switches the actor to cert-plus-claims connect (the GRIDWORKS SASL
    mechanism); all three paths are required — turning on mTLS means
    declaring where the certs live. Field names match the proactor's, so
    the fleet's two client stacks read the same.
    """

    ca_cert_path: Path
    cert_path: Path  # client certificate (CN = principal id)
    private_key_path: Path


class RabbitBrokerClient(BaseModel):
    """Settings for connecting to a Rabbit Broker.

    The URL's vhost is the ``universe.run`` being joined — the single
    source for the ``Run`` connect claim, never declared a second time.
    Validation enforces the universe ladder (gnr executor "Universes") at
    boot: the universe kind must be d/h/w, and a d-kind (dev) universe is
    reachable on localhost ONLY and localhost hosts dev ONLY — the dev
    rung's isolation guarantee ("all comms go through localhost brokers"),
    enforced rather than trusted.
    """

    url: SecretStr = SecretStr("amqp://smqPublic:smqPublic@localhost:5672/d1__1")
    tls: RabbitTls | None = None

    @model_validator(mode="after")
    def _check_url(self) -> "RabbitBrokerClient":
        parts = urlparse(self.url.get_secret_value())
        run = unquote(parts.path.lstrip("/"))
        universe = universe_of(run)  # loud on a non-universe.run vhost

        host = (parts.hostname or "").lower()
        if (host in _LOCAL_HOSTS) != universe.startswith("d"):
            raise ValueError(
                f"broker URL host {host!r} does not fit universe "
                f"{universe!r}: a dev (d-kind) universe lives on "
                f"localhost/127.0.0.1, and localhost/127.0.0.1 hosts only "
                f"dev universes."
            )

        if self.tls is not None and parts.scheme != "amqps":
            raise ValueError(
                f"rabbit.tls is set but the broker URL scheme is "
                f"{parts.scheme!r} — cert-plus-claims connect requires amqps."
            )
        return self

    @property
    def run(self) -> UniverseRun:
        """The universe run this client joins (= the URL's vhost)."""
        return unquote(urlparse(self.url.get_secret_value()).path.lstrip("/"))

    @property
    def universe(self) -> Universe:
        return universe_of(self.run)
