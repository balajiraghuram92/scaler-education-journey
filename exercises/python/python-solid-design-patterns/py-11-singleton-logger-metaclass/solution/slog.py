import threading
from datetime import datetime
from typing import Any, TextIO


class SingletonMeta(type):
    """Thread-safe singleton per class using double-checked locking."""

    _instances: dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in SingletonMeta._instances:
            with SingletonMeta._lock:
                if cls not in SingletonMeta._instances:
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

    def reset_instance(cls) -> None:
        """Test hook: forget the instance (and close it if it can be closed)."""
        with SingletonMeta._lock:
            instance = SingletonMeta._instances.pop(cls, None)
        if instance is not None and hasattr(instance, "close"):
            instance.close()


class Logger(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._sink: TextIO | None = None
        self._path: str | None = None
        self._write_lock = threading.Lock()

    def set_log_file(self, path: str) -> None:
        with self._write_lock:
            if self._sink is not None:
                self._sink.close()
            self._sink = open(path, "a", encoding="utf-8")
            self._path = path

    def get_log_file(self) -> str | None:
        return self._path

    def log(self, level: str, message: str) -> None:
        with self._write_lock:
            if self._sink is None:
                raise RuntimeError("Log file not set. Call set_log_file() before logging.")
            stamp = datetime.now().isoformat()
            self._sink.write(f"[{stamp}] [{level}] {message}\n")

    def flush(self) -> None:
        with self._write_lock:
            if self._sink is not None:
                self._sink.flush()

    def close(self) -> None:
        with self._write_lock:
            if self._sink is not None:
                self._sink.close()
                self._sink = None
