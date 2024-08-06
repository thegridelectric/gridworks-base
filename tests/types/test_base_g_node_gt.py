"""Tests base.g.node.gt type, version 002"""

import json

import pytest
from gw.errors import GwTypeError
from pydantic import ValidationError

from gwbase.enums import CoreGNodeRole
from gwbase.enums import GNodeStatus
from gwbase.types import BaseGNodeGt
from gwbase.types import BaseGNodeGt_Maker as Maker


def test_base_g_node_gt_generated() -> None:
    t = BaseGNodeGt(
        g_node_id="9405686a-14fd-4aef-945b-cd7c97903f14",
        alias="d1.iso.me.orange.ta",
        status=GNodeStatus.Pending,
        role=CoreGNodeRole.TerminalAsset,
        g_node_registry_addr="MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        prev_alias="d1",
        gps_point_id="50f3f6e8-5937-47c2-8d05-06525ef6467d",
        ownership_deed_id=5,
        ownership_deed_validator_addr="RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI",
        owner_addr="7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        daemon_addr="7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        trading_rights_id=1,
        scada_algo_addr="7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        scada_cert_id=10,
    )

    d = {
        "GNodeId": "9405686a-14fd-4aef-945b-cd7c97903f14",
        "Alias": "d1.iso.me.orange.ta",
        "StatusGtEnumSymbol": "153d3475",
        "RoleGtEnumSymbol": "0f8872f7",
        "GNodeRegistryAddr": "MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        "PrevAlias": "d1",
        "GpsPointId": "50f3f6e8-5937-47c2-8d05-06525ef6467d",
        "OwnershipDeedId": 5,
        "OwnershipDeedValidatorAddr": "RNMHG32VTIHTC7W3LZOEPTDGREL5IQGK46HKD3KBLZHYQUCAKLMT4G5ALI",
        "OwnerAddr": "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        "DaemonAddr": "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        "TradingRightsId": 1,
        "ScadaAlgoAddr": "7QQT4GN3ZPAQEFCNWF5BMF7NULVK3CWICZVT4GM3BQRISD52YEDLWJ4MII",
        "ScadaCertId": 10,
        "TypeName": "base.g.node.gt",
        "Version": "002",
    }

    assert t.as_dict() == d

    d2 = d.copy()

    del d2["StatusGtEnumSymbol"]
    d2["Status"] = GNodeStatus.symbol_to_value("153d3475")

    del d2["RoleGtEnumSymbol"]
    d2["Role"] = CoreGNodeRole.symbol_to_value("0f8872f7")

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
    # Dataclass related tests
    ######################################

    dc = Maker.tuple_to_dc(gtuple)
    assert gtuple == Maker.dc_to_tuple(dc)
    assert Maker.type_to_dc(Maker.dc_to_type(dc)) == dc

    ######################################
    # GwTypeError raised if missing a required attribute
    ######################################

    d2 = d.copy()
    del d2["TypeName"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
    del d2["GNodeId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = d.copy()
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

    d2 = d.copy()
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

    ######################################
    # Behavior on incorrect types
    ######################################

    d2 = dict(d, StatusGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).status == GNodeStatus.default()

    d2 = dict(d, RoleGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).role == CoreGNodeRole.default()

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
