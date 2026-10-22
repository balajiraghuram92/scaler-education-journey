from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .database_connection import DatabaseConnection


class ConnectionPool(ABC):
    @staticmethod
    def get_instance(max_connections: int) -> ConnectionPool:
        pass

    @staticmethod
    def reset_instance() -> None:
        pass

    @abstractmethod
    def initialize_pool(self) -> None:
        pass

    @abstractmethod
    def get_connection(self) -> Optional[DatabaseConnection]:
        pass

    @abstractmethod
    def release_connection(self, connection: DatabaseConnection) -> None:
        pass

    @abstractmethod
    def get_available_connections_count(self) -> int:
        pass

    @abstractmethod
    def get_total_connections_count(self) -> int:
        pass
