import random
import threading
import time
from collections.abc import Callable


class ConflictError(RuntimeError):
    pass


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
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == attempts or not is_retryable(exc):
                raise
            sleep(rng() * min(max_delay, base_delay * 2 ** (attempt - 1)))
    raise AssertionError("unreachable")


class VersionedStore:
    def __init__(self, initial: dict[str, int] | None = None) -> None:
        self._rows: dict[str, tuple[int, int]] = {
            key: (value, 1) for key, value in (initial or {}).items()
        }
        self._lock = threading.Lock()

    def read(self, key: str) -> tuple[int, int]:
        with self._lock:
            return self._rows[key]

    def compare_and_set(self, key: str, expected_version: int, new_value: int) -> bool:
        with self._lock:
            _, version = self._rows[key]
            if version != expected_version:
                return False
            self._rows[key] = (new_value, version + 1)
            return True

    def update(
        self,
        key: str,
        fn: Callable[[int], int],
        *,
        attempts: int = 5,
        **retry_options,
    ) -> int:
        def attempt() -> int:
            value, version = self.read(key)
            new_value = fn(value)
            if not self.compare_and_set(key, version, new_value):
                raise ConflictError(f"{key!r} changed while updating")
            return new_value

        return retry(
            attempt,
            is_retryable=lambda exc: isinstance(exc, ConflictError),
            attempts=attempts,
            **retry_options,
        )
