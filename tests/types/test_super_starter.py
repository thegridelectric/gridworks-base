"""Tests super.starter type, version 000"""

import json

import pytest
from gw.errors import GwTypeError
from gwbase.enums import SupervisorContainerStatus
from gwbase.types import SuperStarter, SupervisorContainerGt
from gwbase.types import SuperStarter_Maker as Maker
from pydantic import ValidationError


def test_super_starter_generated() -> None:
    supervisor_container = SupervisorContainerGt(
        supervisor_container_id="995b0334-9940-424f-8fb1-4745e52ba295",
        status=SupervisorContainerStatus.Authorized,
        world_instance_name="d1__1",
        supervisor_g_node_instance_id="20e7edec-05e5-4152-bfec-ec21ddd2e3dd",
        supervisor_g_node_alias="d1.isone.ver.keene.super1",
    )

    t = SuperStarter(
        supervisor_container=supervisor_container,
        gni_list=[],
        alias_with_key_list=[],
        key_list=[],
    )

    d = {
        "SupervisorContainer": {
            "SupervisorContainerId": "995b0334-9940-424f-8fb1-4745e52ba295",
            "WorldInstanceName": "d1__1",
            "SupervisorGNodeInstanceId": "20e7edec-05e5-4152-bfec-ec21ddd2e3dd",
            "SupervisorGNodeAlias": "d1.isone.ver.keene.super1",
            "TypeName": "supervisor.container.gt",
            "Version": "000",
            "StatusGtEnumSymbol": "f48cff43",
        },
        "GniList": [],
        "AliasWithKeyList": [],
        "KeyList": [],
        "TypeName": "super.starter",
        "Version": "000",
    }

    assert t.as_dict() == d

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

    d2 = dict(d)
    del d2["TypeName"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["SupervisorContainer"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["GniList"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["AliasWithKeyList"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["KeyList"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    ######################################
    # Behavior on incorrect types
    ######################################

    d2 = dict(d, GniList="Not a list.")
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, GniList=["Not a list of dicts"])
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, GniList=[{"Failed": "Not a GtSimpleSingleStatus"}])
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    ######################################
    # ValidationError raised if TypeName is incorrect
    ######################################

    d2 = dict(d, TypeName="not the type name")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    ######################################
    # ValidationError raised if primitive attributes do not have appropriate property_format
    ######################################

    d2 = dict(d, AliasWithKeyList=["a.b-h"])
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)
