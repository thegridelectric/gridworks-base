"""Tests g.node.gt type, version 002"""

import json

import pytest
from gw.errors import GwTypeError
from pydantic import ValidationError

from gwbase.enums import GNodeRole
from gwbase.enums import GNodeStatus
from gwbase.types import GNodeGt
from gwbase.types import GNodeGt_Maker as Maker


def test_g_node_gt_generated() -> None:
    t = GNodeGt(
        g_node_id="9405686a-14fd-4aef-945b-cd7c97903f14",
        alias="d1.iso.me.orange.ta",
        status=GNodeStatus.Pending,
        role=GNodeRole.TerminalAsset,
        g_node_registry_addr="MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        prev_alias="d1",
        gps_point_id="50f3f6e8-5937-47c2-8d05-06525ef6467d",
        ownership_deed_id=5,
        ownership_deed_validator_addr="RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI",
        owner_addr="7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        daemon_addr="7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        trading_rights_id=1,
        scada_algo_addr="MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        scada_cert_id=10,
        component_id="19d3dd42-14de-427f-a489-d96b404ae3c5",
        display_name="Simulated Freedom House 1",
    )

    d = {
        "GNodeId": "9405686a-14fd-4aef-945b-cd7c97903f14",
        "Alias": "d1.iso.me.orange.ta",
        "StatusGtEnumSymbol": "153d3475",
        "RoleGtEnumSymbol": "bdeaa0b1",
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
    # Dataclass related tests
    ######################################

    dc = Maker.tuple_to_dc(gtuple)
    assert gtuple == Maker.dc_to_tuple(dc)
    assert Maker.type_to_dc(Maker.dc_to_type(dc)) == dc

    ######################################
    # GwTypeError raised if missing a required attribute
    ######################################

    d2 = dict(d)
    del d2["TypeName"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["GNodeId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["Alias"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["StatusGtEnumSymbol"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["RoleGtEnumSymbol"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["GNodeRegistryAddr"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    ######################################
    # Optional attributes can be removed from type
    ######################################

    d2 = dict(d)
    if "PrevAlias" in d2.keys():
        del d2["PrevAlias"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "GpsPointId" in d2.keys():
        del d2["GpsPointId"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "OwnershipDeedId" in d2.keys():
        del d2["OwnershipDeedId"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "OwnershipDeedValidatorAddr" in d2.keys():
        del d2["OwnershipDeedValidatorAddr"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "OwnerAddr" in d2.keys():
        del d2["OwnerAddr"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "DaemonAddr" in d2.keys():
        del d2["DaemonAddr"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "TradingRightsId" in d2.keys():
        del d2["TradingRightsId"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "ScadaAlgoAddr" in d2.keys():
        del d2["ScadaAlgoAddr"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "ScadaCertId" in d2.keys():
        del d2["ScadaCertId"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "ComponentId" in d2.keys():
        del d2["ComponentId"]
    Maker.dict_to_tuple(d2)

    d2 = dict(d)
    if "DisplayName" in d2.keys():
        del d2["DisplayName"]
    Maker.dict_to_tuple(d2)

    ######################################
    # Behavior on incorrect types
    ######################################

    d2 = dict(d, StatusGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).status == GNodeStatus.default()

    d2 = dict(d, RoleGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).role == GNodeRole.default()

    d2 = dict(d, OwnershipDeedId="5.1")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, TradingRightsId="1.1")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, ScadaCertId="10.1")
    with pytest.raises(ValidationError):
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

    d2 = dict(d, GNodeId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, Alias="a.b-h")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, PrevAlias="a.b-h")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, GpsPointId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, OwnershipDeedId=0)
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, TradingRightsId=0)
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, ScadaCertId=0)
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, ComponentId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)
