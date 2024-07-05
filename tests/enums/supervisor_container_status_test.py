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

    assert SupervisorContainerStatus.version("Unknown") == "000"
    assert SupervisorContainerStatus.version("Authorized") == "000"
    assert SupervisorContainerStatus.version("Launching") == "000"
    assert SupervisorContainerStatus.version("Provisioning") == "000"
    assert SupervisorContainerStatus.version("Running") == "000"
    assert SupervisorContainerStatus.version("Stopped") == "000"
    assert SupervisorContainerStatus.version("Deleted") == "000"

    for value in SupervisorContainerStatus.values():
        symbol = SupervisorContainerStatus.value_to_symbol(value)
        assert SupervisorContainerStatus.symbol_to_value(symbol) == value
