import threading
from datetime import datetime
from typing import Any, TextIO


class SingletonMeta(type):
    """Reusable, thread-safe singleton metaclass: one instance per class.

    - ``__call__`` uses double-checked locking and runs ``__init__`` exactly once.
    - Different classes using this metaclass get different instances.
    - ``reset_instance()`` (called on the class, e.g. ``Logger.reset_instance()``)
      forgets the instance and calls its ``close()`` if it has one.
    """

    _instances: dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("Implement SingletonMeta.__call__")

    def reset_instance(cls) -> None:
        """Test hook: forget the instance (and close it if it can be closed)."""
        raise NotImplementedError("Implement SingletonMeta.reset_instance")


class Logger(metaclass=SingletonMeta):
    """File logger that is a singleton through ``SingletonMeta``.

    - ``log`` raises RuntimeError if no file is set or after ``close()``.
    - Each line looks like ``[<iso timestamp>] [<LEVEL>] <message>``.
    - A write lock must keep lines from concurrent writers whole.
    """

    def __init__(self) -> None:
        self._sink: TextIO | None = None
        self._path: str | None = None
        self._write_lock = threading.Lock()

    def set_log_file(self, path: str) -> None:
        """Close any open file, then open ``path`` in append mode."""
        raise NotImplementedError("Implement set_log_file")

    def get_log_file(self) -> str | None:
        """The current path, or None."""
        raise NotImplementedError("Implement get_log_file")

    def log(self, level: str, message: str) -> None:
        """Append one line; RuntimeError when there is no open file."""
        raise NotImplementedError("Implement log")

    def flush(self) -> None:
        """Flush the open file, if any."""
        raise NotImplementedError("Implement flush")

    def close(self) -> None:
        """Close the open file, if any; later ``log`` calls raise RuntimeError."""
        raise NotImplementedError("Implement close")
