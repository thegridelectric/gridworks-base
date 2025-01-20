"""List of all the types used by the actor."""

from typing import Dict, List

from gw.named_types import GwBase

from gwbase.named_types.base_g_node_gt import BaseGNodeGt
from gwbase.named_types.g_node_gt import GNodeGt
from gwbase.named_types.g_node_instance_gt import GNodeInstanceGt
from gwbase.named_types.heartbeat_a import HeartbeatA
from gwbase.named_types.ready import Ready
from gwbase.named_types.sim_timestep import SimTimestep
from gwbase.named_types.super_starter import SuperStarter
from gwbase.named_types.supervisor_container_gt import SupervisorContainerGt

TypeByName: Dict[str, GwBase] = {}
VersionedTypeByName: Dict[str, GwBase] = {}


def types() -> List[GwBase]:
    return [
        BaseGNodeGt,
        GNodeGt,
        GNodeInstanceGt,
        HeartbeatA,
        Ready,
        SimTimestep,
        SuperStarter,
        SupervisorContainerGt,
    ]


for t in types():
    versioned_type_name = f"{t.type_name_value()}.{t.version_value()}"
    type_name = t.type_name_value()
    try:
        TypeByName[type_name] = t
        VersionedTypeByName[versioned_type_name] = t
    except Exception:
        print(f"Problem w {t}")
