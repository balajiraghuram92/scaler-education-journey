from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Logger(ABC):

    @staticmethod
    def get_instance() -> Logger:
        pass

    @staticmethod
    def reset_instance() -> None:
        pass

    @abstractmethod
    def log(self, level: LogLevel, message: str) -> None:
        pass

    @abstractmethod
    def set_log_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def get_log_file(self) -> str:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
