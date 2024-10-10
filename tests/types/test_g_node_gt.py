"""Tests g.node.gt type, version 002"""

from gwbase.enums import GNodeRole, GNodeStatus
from gwbase.named_types import GNodeGt


def test_g_node_gt_generated() -> None:
    d = {
        "GNodeId": "9405686a-14fd-4aef-945b-cd7c97903f14",
        "Alias": "d1.iso.me.orange.ta",
        "Status": "Pending",
        "Role": "TerminalAsset",
        "GNodeRegistryAddr": "MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        "PrevAlias": "d1",
        "GpsPointId": "50f3f6e8-5937-47c2-8d05-06525ef6467d",
        "OwnershipDeedId": 5,
        "OwnershipDeedValidatorAddr": "RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI",
        "OwnerAddr": "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        "DaemonAddr": "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        "TradingRightsId": 1,
        "ScadaAlgoAddr": "MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        "ScadaCertId": 10,
        "ComponentId": "19d3dd42-14de-427f-a489-d96b404ae3c5",
        "DisplayName": "Simulated Freedom House 1",
        "TypeName": "g.node.gt",
        "Version": "002",
    }

    assert GNodeGt.from_dict(d).to_dict() == d

    ######################################
    # Behavior on unknown enum values: sends to default
    ######################################

    d2 = dict(d, Status="unknown_enum_thing")
    assert GNodeGt.from_dict(d2).status == GNodeStatus.default()

    d2 = dict(d, Role="unknown_enum_thing")
    assert GNodeGt.from_dict(d2).role == GNodeRole.default()
