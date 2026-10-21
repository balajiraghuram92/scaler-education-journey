from __future__ import annotations

from dataclasses import dataclass

from .builder import Builder


@dataclass
class DatabaseConfiguration:
    database_url: str
    username: str
    password: str
    max_connections: int
    enable_cache: bool
    is_read_only: bool

    @staticmethod
    def builder() -> DatabaseBuilder:
        """Return a NEW DatabaseBuilder on every call."""
        raise NotImplementedError("Implement DatabaseConfiguration.builder")

    class DatabaseBuilder(Builder["DatabaseConfiguration"]):
        """Fluent builder: every ``with_*`` setter stores its value and returns the builder.

        Keep the working state in ``self._instance`` (a DatabaseConfiguration with
        every field ``None``). ``build()`` returns a configured DatabaseConfiguration
        that is independent of the builder: later setter calls must not change an
        object that was already built.
        """

        def __init__(self):
            raise NotImplementedError("Implement the constructor")

        def with_database_url(self, database_url: str) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_database_url")

        def with_username(self, username: str) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_username")

        def with_password(self, password: str) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_password")

        def with_max_connections(self, max_connections: int) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_max_connections")

        def with_enable_cache(self, enable_cache: bool) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_enable_cache")

        def with_is_read_only(self, is_read_only: bool) -> DatabaseConfiguration.DatabaseBuilder:
            raise NotImplementedError("Implement with_is_read_only")

        def build(self) -> DatabaseConfiguration:
            raise NotImplementedError("Implement build")
