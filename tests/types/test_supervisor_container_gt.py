"""Tests supervisor.container.gt type, version 000"""

import json

import pytest
from gw.errors import GwTypeError
from gwbase.enums import SupervisorContainerStatus
from gwbase.types import SupervisorContainerGt
from gwbase.types import SupervisorContainerGt_Maker as Maker
from pydantic import ValidationError


def test_supervisor_container_gt_generated() -> None:
    t = SupervisorContainerGt(
        supervisor_container_id="da2dafe0-b5c8-4c36-984c-ae653a29bfcc",
        status=SupervisorContainerStatus.Authorized,
        world_instance_name="d1__1",
        supervisor_g_node_instance_id="aac80de4-91cf-48e7-9bef-d469eba989ad",
        supervisor_g_node_alias="d1.super1",
    )

    d = {
        "SupervisorContainerId": "da2dafe0-b5c8-4c36-984c-ae653a29bfcc",
        "StatusGtEnumSymbol": "f48cff43",
        "WorldInstanceName": "d1__1",
        "SupervisorGNodeInstanceId": "aac80de4-91cf-48e7-9bef-d469eba989ad",
        "SupervisorGNodeAlias": "d1.super1",
        "TypeName": "supervisor.container.gt",
        "Version": "000",
    }

    assert t.as_dict() == d

    d2 = d.copy()

    del d2["StatusGtEnumSymbol"]
    d2["Status"] = SupervisorContainerStatus.symbol_to_value("f48cff43")

    assert t == Maker.dict_to_tuple(d2)

    with pytest.raises(GwTypeError):
        Maker.type_to_tuple(d)

    with pytest.raises(GwTypeError):
        Maker.type_to_tuple('"not a dict"')

    # Test type_to_tuple
    gtype = json.dumps(d)
    gtuple = Maker.type_to_tuple(gtype)
    assert gtuple == t

    # test type_to_tuple and tuple_to_type maps
    assert Maker.type_to_tuple(Maker.tuple_to_type(gtuple)) == gtuple

    ######################################
    # GwTypeError raised if missing a required attribute
    ######################################

    d2 = d.copy()
    del d2["TypeName"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
    del d2["SupervisorContainerId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["StatusGtEnumSymbol"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
    del d2["WorldInstanceName"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
    del d2["SupervisorGNodeInstanceId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
    del d2["SupervisorGNodeAlias"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    ######################################
    # Behavior on incorrect types
    ######################################

    d2 = dict(d, StatusGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).status == SupervisorContainerStatus.default()

    ######################################
    # ValidationError raised if TypeName is incorrect
    ######################################

    d2 = dict(d, TypeName="not the type name")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    ######################################
    # ValidationError raised if primitive attributes do not have appropriate property_format
    ######################################

    d2 = dict(d, SupervisorContainerId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, SupervisorGNodeInstanceId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, SupervisorGNodeAlias="a.b-h")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)
