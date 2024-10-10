"""Tests ready type, version 001"""

from gwbase.named_types import Ready


def test_ready_generated() -> None:
    d = {
        "FromGNodeAlias": "d1.time",
        "FromGNodeInstanceId": "eac00c51-d944-4829-aaca-847bca1b8438",
        "TimeUnixS": 1669757715,
        "TypeName": "ready",
        "Version": "001",
    }

    assert Ready.from_dict(d).to_dict() == d
