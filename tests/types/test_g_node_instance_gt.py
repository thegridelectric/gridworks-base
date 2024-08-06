"""Tests g.node.instance.gt type, version 000"""

import json

import pytest
from gw.errors import DcError
from gw.errors import GwTypeError
from pydantic import ValidationError

from gwbase.data_classes.g_node import GNode
from gwbase.enums import GniStatus
from gwbase.enums import GNodeRole
from gwbase.enums import GNodeStatus
from gwbase.enums import StrategyName
from gwbase.types import GNodeInstanceGt
from gwbase.types import GNodeInstanceGt_Maker as Maker


def test_g_node_instance_gt_generated() -> None:
    t = GNodeInstanceGt(
        g_node_instance_id="76d2a9b9-7804-4bdb-b712-8710a1e37252",
        g_node_id="7b1df82e-10c5-49d9-8d02-1e837e31b87e",
        strategy=StrategyName.WorldA,
        status=GniStatus.Active,
        supervisor_container_id="299ed6df-183d-4230-b60d-fd2eae34b1cd",
        start_time_unix_s=1670025409,
        end_time_unix_s=0,
        algo_address="4JHRDNY4F6RCVGPALZULZWZNVP3OKT3DATEOLINCGILVPGHUOFY7KCHVIQ",
    )

    d = {
        "GNodeInstanceId": "76d2a9b9-7804-4bdb-b712-8710a1e37252",
        "GNodeId": "7b1df82e-10c5-49d9-8d02-1e837e31b87e",
        "StrategyGtEnumSymbol": "642c83d3",
        "StatusGtEnumSymbol": "69241259",
        "SupervisorContainerId": "299ed6df-183d-4230-b60d-fd2eae34b1cd",
        "StartTimeUnixS": 1670025409,
        "EndTimeUnixS": 0,
        "AlgoAddress": "4JHRDNY4F6RCVGPALZULZWZNVP3OKT3DATEOLINCGILVPGHUOFY7KCHVIQ",
        "TypeName": "g.node.instance.gt",
        "Version": "000",
    }

    assert t.as_dict() == d

    d2 = d.copy()

    del d2["StrategyGtEnumSymbol"]
    d2["Strategy"] = StrategyName.symbol_to_value("642c83d3")

    del d2["StatusGtEnumSymbol"]
    d2["Status"] = GniStatus.symbol_to_value("69241259")

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

    # the data class requires an actual GNode dc object with matching g_node_id
    with pytest.raises(DcError):
        dc = Maker.tuple_to_dc(gtuple)

    gn = GNode(
        g_node_id="7b1df82e-10c5-49d9-8d02-1e837e31b87e",
        alias="d1",
        g_node_registry_addr="MONSDN5MXG4VMIOHJNCJJBVASG7HEZQSCEIKJAPEPVI5ZJUMQGXQKSOAYU",
        status=GNodeStatus.Active,
        role=GNodeRole.World,
    )

    dc = Maker.tuple_to_dc(gtuple)
    assert dc.g_node == gn

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
    del d2["GNodeInstanceId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["GNodeId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["StrategyGtEnumSymbol"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["StatusGtEnumSymbol"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["SupervisorContainerId"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["StartTimeUnixS"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d)
    del d2["EndTimeUnixS"]
    with pytest.raises(GwTypeError):
        Maker.dict_to_tuple(d2)

    ######################################
    # Optional attributes can be removed from type
    ######################################

    d2 = dict(d)
    if "AlgoAddress" in d2.keys():
        del d2["AlgoAddress"]
    Maker.dict_to_tuple(d2)

    ######################################
    # Behavior on incorrect types
    ######################################

    d2 = dict(d, StrategyGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).strategy == StrategyName.default()

    d2 = dict(d, StatusGtEnumSymbol="unknown_symbol")
    Maker.dict_to_tuple(d2).status == GniStatus.default()

    d2 = dict(d, StartTimeUnixS="1670025409.1")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, EndTimeUnixS="0.1")
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

    d2 = dict(d, GNodeInstanceId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, SupervisorContainerId="d4be12d5-33ba-4f1f-b9e5")
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)

    d2 = dict(d, StartTimeUnixS=32503683600)
    with pytest.raises(ValidationError):
        Maker.dict_to_tuple(d2)
