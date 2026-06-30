import time
from collections.abc import Callable


def wait_for(
    predicate: Callable[[], bool],
    timeout_s: float,
    message: str,
    interval_s: float = 0.05,
) -> None:
    """Spin until predicate() is true or timeout expires."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(interval_s)
    raise TimeoutError(f"Timed out after {timeout_s}s waiting for: {message}")
