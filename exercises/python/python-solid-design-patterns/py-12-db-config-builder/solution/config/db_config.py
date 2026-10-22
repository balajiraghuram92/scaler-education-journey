from __future__ import annotations

import dataclasses
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
        return DatabaseConfiguration.DatabaseBuilder()

    class DatabaseBuilder(Builder["DatabaseConfiguration"]):
        def __init__(self):
            self._instance = DatabaseConfiguration(None, None, None, None, None, None)

        def with_database_url(
            self, database_url: str
        ) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.database_url = database_url
            return self

        def with_username(self, username: str) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.username = username
            return self

        def with_password(self, password: str) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.password = password
            return self

        def with_max_connections(
            self, max_connections: int
        ) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.max_connections = max_connections
            return self

        def with_enable_cache(
            self, enable_cache: bool
        ) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.enable_cache = enable_cache
            return self

        def with_is_read_only(
            self, is_read_only: bool
        ) -> DatabaseConfiguration.DatabaseBuilder:
            self._instance.is_read_only = is_read_only
            return self

        def build(self) -> DatabaseConfiguration:
            return dataclasses.replace(self._instance)
