from dataclasses import dataclass, field
from typing import Self


@dataclass(frozen=True, slots=True)
class DatabaseConfiguration:
    database_url: str
    username: str
    password: str = field(repr=False)
    max_connections: int
    enable_cache: bool
    read_only: bool
    allowed_hosts: tuple[str, ...]

    @staticmethod
    def builder() -> "DatabaseConfigurationBuilder":
        return DatabaseConfigurationBuilder()


class DatabaseConfigurationBuilder:
    def __init__(self) -> None:
        self._database_url: str | None = None
        self._username: str | None = None
        self._password: str | None = None
        self._max_connections = 10
        self._enable_cache = False
        self._read_only = False
        self._allowed_hosts: list[str] = []

    def with_database_url(self, database_url: str) -> Self:
        self._database_url = database_url
        return self

    def with_credentials(self, username: str, password: str) -> Self:
        self._username = username
        self._password = password
        return self

    def with_max_connections(self, max_connections: int) -> Self:
        self._max_connections = max_connections
        return self

    def with_enable_cache(self, enable_cache: bool) -> Self:
        self._enable_cache = enable_cache
        return self

    def with_read_only(self, read_only: bool) -> Self:
        self._read_only = read_only
        return self

    def with_allowed_host(self, host: str) -> Self:
        self._allowed_hosts.append(host)  # accumulates, never overwrites
        return self

    def build(self) -> DatabaseConfiguration:
        problems: list[str] = []
        if not self._database_url:
            problems.append("database_url is required")
        elif not self._database_url.startswith(("postgresql://", "mysql://")):
            problems.append("database_url must start with postgresql:// or mysql://")
        if not self._username or not self._password:
            problems.append("credentials are required (username and password)")
        if not 1 <= self._max_connections <= 500:
            problems.append("max_connections must be between 1 and 500")
        if problems:
            raise ValueError("; ".join(problems))
        assert self._database_url and self._username and self._password
        return DatabaseConfiguration(
            database_url=self._database_url,
            username=self._username,
            password=self._password,
            max_connections=self._max_connections,
            enable_cache=self._enable_cache,
            read_only=self._read_only,
            allowed_hosts=tuple(self._allowed_hosts),  # defensive copy
        )
