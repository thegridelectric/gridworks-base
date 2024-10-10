"""Tests g.node.instance.gt type, version 000"""

from gwbase.enums import GniStatus, StrategyName
from gwbase.named_types import GNodeInstanceGt


def test_g_node_instance_gt_generated() -> None:
    d = {
        "GNodeInstanceId": "76d2a9b9-7804-4bdb-b712-8710a1e37252",
        "GNodeId": "7b1df82e-10c5-49d9-8d02-1e837e31b87e",
        "Strategy": "WorldA",
        "Status": "Active",
        "SupervisorContainerId": "299ed6df-183d-4230-b60d-fd2eae34b1cd",
        "StartTimeUnixS": 1670025409,
        "EndTimeUnixS": 0,
        "AlgoAddress": "4JHRDNY4F6RCVGPALZULZWZNVP3OKT3DATEOLINCGILVPGHUOFY7KCHVIQ",
        "TypeName": "g.node.instance.gt",
        "Version": "000",
    }

    assert GNodeInstanceGt.from_dict(d).to_dict() == d

    ######################################
    # Behavior on unknown enum values: sends to default
    ######################################

    d2 = dict(d, Strategy="unknown_enum_thing")
    assert GNodeInstanceGt.from_dict(d2).strategy == StrategyName.default()

    d2 = dict(d, Status="unknown_enum_thing")
    assert GNodeInstanceGt.from_dict(d2).status == GniStatus.default()
