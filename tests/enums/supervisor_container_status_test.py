"""
Tests for enum supervisor.container.status.000 from the GridWorks Type Registry.
"""

from gwbase.enums import SupervisorContainerStatus


def test_supervisor_container_status() -> None:
    assert set(SupervisorContainerStatus.values()) == {
        "Unknown",
        "Authorized",
        "Launching",
        "Provisioning",
        "Running",
        "Stopped",
        "Deleted",
    }

    assert SupervisorContainerStatus.default() == SupervisorContainerStatus.Unknown
    assert SupervisorContainerStatus.enum_name() == "supervisor.container.status"
    assert SupervisorContainerStatus.enum_version() == "000"
