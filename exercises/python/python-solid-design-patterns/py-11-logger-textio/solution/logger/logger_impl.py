from datetime import datetime
from threading import Lock
from typing import Optional, TextIO

from .logger import Logger, LogLevel


class LoggerImpl(Logger):
    _instance: Optional[Logger] = None
    _lock = Lock()

    def __init__(self) -> None:
        self.log_file_path: Optional[str] = None
        self.log_writer: Optional[TextIO] = None

    @staticmethod
    def get_instance() -> Logger:
        if LoggerImpl._instance is None:
            with LoggerImpl._lock:
                if LoggerImpl._instance is None:
                    LoggerImpl._instance = LoggerImpl()
        return LoggerImpl._instance

    @staticmethod
    def reset_instance() -> None:
        with LoggerImpl._lock:
            LoggerImpl._instance = None

    def log(self, level: LogLevel, message: str) -> None:

        if self.log_writer is None:
            raise RuntimeError("Log file not set. Call set_log_file() before logging.")

        timestamp = datetime.now().isoformat()
        formatted_message = f"[{timestamp}] [{level.value}] {message}\n"
        self.log_writer.write(formatted_message)

    def get_log_file(self) -> Optional[str]:
        return self.log_file_path

    def set_log_file(self, file_path: str) -> None:
        try:
            self.close()
            self.log_file_path = file_path
            self.log_writer = open(file_path, "a")
        except IOError as e:
            raise RuntimeError(f"Error setting log file: {e}")

    def flush(self) -> None:
        if self.log_writer is not None:
            self.log_writer.flush()

    def close(self) -> None:
        if self.log_writer is not None:
            self.log_writer.close()
            self.log_writer = None
