import random
import time
from collections.abc import Callable


class ConflictError(RuntimeError):
    """The row changed between read and write."""


def retry[T](
    fn: Callable[[], T],
    *,
    is_retryable: Callable[[Exception], bool],
    attempts: int = 5,
    base_delay: float = 0.01,
    max_delay: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> T:
    """Call ``fn`` up to ``attempts`` times.

    On a retryable exception with attempts left, sleep ``rng() * min(max_delay, base_delay * 2 ** (attempt - 1))``
    (attempt numbered from 1). Other exceptions, or a retryable one on the last attempt, propagate unchanged.
    ``attempts < 1`` raises ValueError.
    """
    raise NotImplementedError("Implement retry")


class VersionedStore:
    """In-memory ``key -> (value, version)``; new keys start at version 1."""

    def __init__(self, initial: dict[str, int] | None = None) -> None:
        raise NotImplementedError("Implement VersionedStore.__init__")

    def read(self, key: str) -> tuple[int, int]:
        """Return ``(value, version)``; KeyError for an unknown key."""
        raise NotImplementedError("Implement read")

    def compare_and_set(self, key: str, expected_version: int, new_value: int) -> bool:
        """Atomically (internal ``threading.Lock``) store ``new_value`` and bump the version
        only if the current version equals ``expected_version``."""
        raise NotImplementedError("Implement compare_and_set")

    def update(self, key: str, fn: Callable[[int], int], *, attempts: int = 5, **retry_options) -> int:
        """Read, compute ``fn(value)``, ``compare_and_set``; on failure raise ConflictError and retry
        (only on ConflictError, forwarding ``**retry_options`` to ``retry``). Returns the new value.
        Exceptions from ``fn`` are not retried."""
        raise NotImplementedError("Implement update")
