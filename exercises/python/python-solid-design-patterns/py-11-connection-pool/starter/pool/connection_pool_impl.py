from typing import Optional

from .connection_pool import ConnectionPool
from .database_connection import DatabaseConnection


class ConnectionPoolImpl(ConnectionPool):
    """Singleton pool of ``max_connections`` DatabaseConnection objects.

    Hints: keep the shared instance in a class attribute guarded by a class-level
    ``threading.Lock`` (double-checked locking), and keep the free connections in
    a thread-safe ``queue.Queue`` so borrowing blocks when the pool is exhausted.
    """

    def __init__(self, max_connections: int):
        self.max_connections = max_connections
        raise NotImplementedError("Implement the constructor: build the queue and call initialize_pool()")

    @staticmethod
    def get_instance(max_connections: int) -> ConnectionPool:
        """Return the shared pool, creating it on first use with ``max_connections`` connections."""
        raise NotImplementedError("Implement get_instance")

    @staticmethod
    def reset_instance() -> None:
        """Forget the singleton so a new pool can be created."""
        raise NotImplementedError("Implement reset_instance")

    def initialize_pool(self) -> None:
        """Create ``max_connections`` DatabaseConnection objects and make them all available."""
        raise NotImplementedError("Implement initialize_pool")

    def get_connection(self) -> Optional[DatabaseConnection]:
        """Hand out a free connection; block until one is returned if none is free."""
        raise NotImplementedError("Implement get_connection")

    def release_connection(self, connection: DatabaseConnection) -> None:
        """Make ``connection`` available again; ``None`` is ignored."""
        raise NotImplementedError("Implement release_connection")

    def get_available_connections_count(self) -> int:
        """Number of connections currently free."""
        raise NotImplementedError("Implement get_available_connections_count")

    def get_total_connections_count(self) -> int:
        """Total pool size."""
        raise NotImplementedError("Implement get_total_connections_count")
