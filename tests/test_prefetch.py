"""Consumer prefetch comes from the service's settings, no broker."""

from gwbase import ActorBase, ServiceSettings
from gwbase.transport_encoding import RoutingEnvelope


class RecordingChannel:
    """Stands in for the consumer channel; records Basic.Qos arguments."""

    def __init__(self) -> None:
        self.qos: dict[str, object] = {}

    def basic_qos(self, **kwargs: object) -> None:
        self.qos = kwargs


class Tap(ActorBase):
    def dispatch_message(self, *, envelope: RoutingEnvelope, body: bytes) -> None:
        pass


def test_prefetch_defaults_to_100() -> None:
    assert ServiceSettings(service_alias="d1.tap1").prefetch_count == 100


def test_set_qos_uses_settings_prefetch() -> None:
    actor = Tap(settings=ServiceSettings(service_alias="d1.tap1", prefetch_count=7))
    channel = RecordingChannel()
    actor._single_channel = channel  # noqa: SLF001  # pyright: ignore[reportAttributeAccessIssue]
    actor.set_qos()
    assert channel.qos["prefetch_count"] == 7
