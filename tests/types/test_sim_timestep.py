"""Tests sim.timestep type, version 000"""

from gwbase.named_types import SimTimestep


def test_sim_timestep_generated() -> None:
    d = {
        "FromGNodeAlias": "d1.tc",
        "FromGNodeInstanceId": "bdb20ce2-332f-4d3e-b848-0c350be2ea67",
        "TimeUnixS": 1667852537,
        "TimestepCreatedMs": 1667852537000,
        "MessageId": "7bc73995-c71b-45b4-a608-761fdc1c28eb",
        "TypeName": "sim.timestep",
        "Version": "000",
    }

    assert SimTimestep.from_dict(d).to_dict() == d
