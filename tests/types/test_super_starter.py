"""Tests super.starter type, version 000"""

from gwbase.named_types import SuperStarter


def test_super_starter_generated() -> None:
    d = {
        "SupervisorContainer": {
            "SupervisorContainerId": "995b0334-9940-424f-8fb1-4745e52ba295",
            "WorldInstanceName": "d1__1",
            "SupervisorGNodeInstanceId": "20e7edec-05e5-4152-bfec-ec21ddd2e3dd",
            "SupervisorGNodeAlias": "d1.isone.ver.keene.super1",
            "TypeName": "supervisor.container.gt",
            "Version": "000",
            "Status": "Authorized",
        },
        "GniList": [],
        "AliasWithKeyList": [],
        "KeyList": [],
        "TypeName": "super.starter",
        "Version": "000",
    }

    assert SuperStarter.from_dict(d).to_dict() == d
