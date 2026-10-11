"""A deliberate stop ends the consumer thread and is not mistaken for an
outage, whatever a subclass does in ``local_stop``. Needs the dev broker."""

import logging
import uuid

import pytest

from gwbase import ActorBase, ServiceSettings
from gwbase.transport_encoding import RoutingEnvelope
from tests._wait import wait_for

STOP_TIMEOUT_S = 5.0


class TapWithOwnStop(ActorBase):
    """A tap whose ``local_stop`` does not call the base hook."""

    def dispatch_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        pass

    def local_stop(self) -> None:
        pass


def test_stop_ends_consumer_thread_without_reconnect(
    caplog: pytest.LogCaptureFixture,
) -> None:
    tap = TapWithOwnStop(
        settings=ServiceSettings(service_alias=f"d1.tap{uuid.uuid4().hex[:4]}")
    )
    tap.start()
    wait_for(lambda: tap.consuming, 10.0, "tap consuming")
    with caplog.at_level(logging.WARNING, logger="gwbase.actor_base"):
        tap.stop()
    tap.consuming_thread.join(timeout=STOP_TIMEOUT_S)
    assert not tap.consuming_thread.is_alive()
    assert "reconnect necessary" not in caplog.text
