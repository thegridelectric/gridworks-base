"""List of all the types used by the actor."""

from typing import Dict, List, no_type_check

from gwbase.types import (
    BaseGNodeGt_Maker,
    GNodeGt_Maker,
    GNodeInstanceGt_Maker,
    HeartbeatA_Maker,
    Ready_Maker,
    SimTimestep_Maker,
    SuperStarter_Maker,
    SupervisorContainerGt_Maker,
)

TypeMakerByName: Dict[str, HeartbeatA_Maker] = {}


@no_type_check
def type_makers() -> List[HeartbeatA_Maker]:
    return [
        BaseGNodeGt_Maker,
        GNodeGt_Maker,
        GNodeInstanceGt_Maker,
        HeartbeatA_Maker,
        Ready_Maker,
        SimTimestep_Maker,
        SuperStarter_Maker,
        SupervisorContainerGt_Maker,
    ]


for maker in type_makers():
    TypeMakerByName[maker.type_name] = maker


def version_by_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are TypeNames, values are versions
    """

    v: Dict[str, str] = {
        "base.g.node.gt": "002",
        "g.node.gt": "002",
        "g.node.instance.gt": "000",
        "heartbeat.a": "100",
        "ready": "001",
        "sim.timestep": "000",
        "super.starter": "000",
        "supervisor.container.gt": "000",
    }

    return v


def status_by_versioned_type_name() -> Dict[str, str]:
    """
    Returns:
        Dict[str, str]: Keys are versioned TypeNames, values are type status
    """

    v: Dict[str, str] = {
        "base.g.node.gt.002": "Active",
        "g.node.gt.002": "Active",
        "g.node.instance.gt.000": "Active",
        "heartbeat.a.100": "Active",
        "ready.001": "Active",
        "sim.timestep.000": "Active",
        "super.starter.000": "Active",
        "supervisor.container.gt.000": "Active",
    }

    return v
