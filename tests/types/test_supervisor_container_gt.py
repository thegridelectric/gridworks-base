"""Tests supervisor.container.gt type, version 000"""

from gwbase.enums import SupervisorContainerStatus
from gwbase.named_types import SupervisorContainerGt


def test_supervisor_container_gt_generated() -> None:
    d = {
        "SupervisorContainerId": "da2dafe0-b5c8-4c36-984c-ae653a29bfcc",
        "Status": "Authorized",
        "WorldInstanceName": "d1__1",
        "SupervisorGNodeInstanceId": "aac80de4-91cf-48e7-9bef-d469eba989ad",
        "SupervisorGNodeAlias": "d1.super1",
        "TypeName": "supervisor.container.gt",
        "Version": "000",
    }

    assert SupervisorContainerGt.from_dict(d).to_dict() == d

    ######################################
    # Behavior on unknown enum values: sends to default
    ######################################

    d2 = dict(d, Status="unknown_enum_thing")
    assert (
        SupervisorContainerGt.from_dict(d2).status
        == SupervisorContainerStatus.default()
    )
