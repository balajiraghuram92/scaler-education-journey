from typing import Optional, TextIO

from .logger import Logger, LogLevel


class LoggerImpl(Logger):
    """Application-wide file logger: a thread-safe, lazily created singleton.

    Keep the shared instance in a class attribute guarded by a class-level
    ``threading.Lock`` (double-checked locking) and the open file in
    ``self.log_writer`` (a TextIO).
    """

    def __init__(self) -> None:
        self.log_file_path: Optional[str] = None
        self.log_writer: Optional[TextIO] = None

    @staticmethod
    def get_instance() -> Logger:
        """Return the shared logger, creating it on first use (thread-safe)."""
        raise NotImplementedError("Implement get_instance")

    @staticmethod
    def reset_instance() -> None:
        """Forget the shared logger."""
        raise NotImplementedError("Implement reset_instance")

    def log(self, level: LogLevel, message: str) -> None:
        """Write one line with a timestamp, the level and the message.

        Raise RuntimeError if no log file has been set.
        """
        raise NotImplementedError("Implement log")

    def get_log_file(self) -> Optional[str]:
        """Current log file path, or None."""
        raise NotImplementedError("Implement get_log_file")

    def set_log_file(self, file_path: str) -> None:
        """Close any open file, then open ``file_path`` in append mode.

        Wrap IOError in a RuntimeError.
        """
        raise NotImplementedError("Implement set_log_file")

    def flush(self) -> None:
        """Flush the handle if one is open."""
        raise NotImplementedError("Implement flush")

    def close(self) -> None:
        """Close the handle (if any) and clear it."""
        raise NotImplementedError("Implement close")
