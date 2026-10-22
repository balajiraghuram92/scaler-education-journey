from queue import Queue
from threading import Lock
from typing import Optional

from .connection_pool import ConnectionPool
from .database_connection import DatabaseConnection


class ConnectionPoolImpl(ConnectionPool):
    _instance = None
    _lock = Lock()

    def __init__(self, max_connections: int):
        self.max_connections = max_connections
        self.connection_queue: Queue[DatabaseConnection] = Queue(max_connections)
        self.initialize_pool()

    @staticmethod
    def get_instance(max_connections: int) -> ConnectionPool:
        if ConnectionPoolImpl._instance is None:
            with ConnectionPoolImpl._lock:
                if ConnectionPoolImpl._instance is None:
                    ConnectionPoolImpl._instance = ConnectionPoolImpl(max_connections)
        return ConnectionPoolImpl._instance

    @staticmethod
    def reset_instance() -> None:
        with ConnectionPoolImpl._lock:
            ConnectionPoolImpl._instance = None

    def initialize_pool(self) -> None:
        for _ in range(self.max_connections):
            connection = self.create_connection()
            self.connection_queue.put(connection)

    def create_connection(self) -> DatabaseConnection:
        return DatabaseConnection()

    def get_connection(self) -> Optional[DatabaseConnection]:
        try:
            return self.connection_queue.get(block=True)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise RuntimeError("Error getting connection") from e

    def release_connection(self, connection: DatabaseConnection) -> None:
        try:
            if connection is not None:
                self.connection_queue.put(connection)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise RuntimeError("Error releasing connection") from e

    def get_available_connections_count(self) -> int:
        return self.connection_queue.qsize()

    def get_total_connections_count(self) -> int:
        return self.max_connections
