from enum import auto
from typing import List

from gw.enums import GwStrEnum


class SupervisorContainerStatus(GwStrEnum):
    """
    Manages lifecycle of the docker containers where GridWorks actors run
    Values:
      - Unknown: Default value
      - Authorized: World has created the information for starting the container
      - Launching: World has launched the container
      - Provisioning: Container has started, but is going through its provisioning process
      - Running: GNode actors in the container are active
      - Stopped: Stopped
      - Deleted: Deleted

    For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#supervisorcontainerstatus)
    """

    Unknown = auto()
    Authorized = auto()
    Launching = auto()
    Provisioning = auto()
    Running = auto()
    Stopped = auto()
    Deleted = auto()

    @classmethod
    def default(cls) -> "SupervisorContainerStatus":
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        return [elt.value for elt in cls]

    @classmethod
    def enum_name(cls) -> str:
        return "supervisor.container.status"

    @classmethod
    def enum_version(cls) -> str:
        return "000"
