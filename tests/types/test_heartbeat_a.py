"""Tests heartbeat.a type, version 100"""

from gwbase.named_types import HeartbeatA


def test_heartbeat_a_generated() -> None:
    d = {
        "MyHex": "a",
        "YourLastHex": "2",
        "TypeName": "heartbeat.a",
        "Version": "100",
    }

    assert HeartbeatA.from_dict(d).to_dict() == d
