import time
from typing import Callable, Any


def retry_operation(
    operation: Callable[[], Any],
    max_attempts: int = 3,
    delay: float = 2,
) -> Any:
    """Retry an operation after temporary failures."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    if delay < 0:
        raise ValueError("delay cannot be negative.")

    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()

        except Exception as e:
            last_error = e

            if attempt < max_attempts:
                time.sleep(delay)

    raise RuntimeError(
        f"Operation failed after {max_attempts} attempts: {last_error}"
    ) from last_error