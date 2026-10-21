from dataclasses import dataclass, field
from typing import Self


@dataclass(frozen=True, slots=True)
class DatabaseConfiguration:
    database_url: str
    username: str
    password: str = field(repr=False)  # the password must never appear in repr()
    max_connections: int
    enable_cache: bool
    read_only: bool
    allowed_hosts: tuple[str, ...]

    @staticmethod
    def builder() -> "DatabaseConfigurationBuilder":
        """Return a new DatabaseConfigurationBuilder."""
        raise NotImplementedError("Implement DatabaseConfiguration.builder")


class DatabaseConfigurationBuilder:
    """Fluent, validating builder for DatabaseConfiguration.

    Defaults: ``max_connections=10``, ``enable_cache=False``, ``read_only=False``,
    no allowed hosts. ``with_allowed_host`` APPENDS (it never overwrites).

    ``build()`` collects every problem and raises ONE ValueError whose message
    joins them with ``"; "``:
      - URL missing, or not starting with ``postgresql://`` or ``mysql://``
        (the message must mention ``database_url``; for an unsupported scheme it
        must mention ``postgresql://``)
      - username or password missing (mention ``credentials``)
      - max_connections outside 1..500 (mention ``max_connections``)

    Every ``build()`` returns a NEW object; later builder changes must not affect
    earlier products; ``allowed_hosts`` is stored as a tuple (defensive copy).
    """

    def __init__(self) -> None:
        raise NotImplementedError("Implement the constructor")

    def with_database_url(self, database_url: str) -> Self:
        raise NotImplementedError("Implement with_database_url")

    def with_credentials(self, username: str, password: str) -> Self:
        raise NotImplementedError("Implement with_credentials")

    def with_max_connections(self, max_connections: int) -> Self:
        raise NotImplementedError("Implement with_max_connections")

    def with_enable_cache(self, enable_cache: bool) -> Self:
        raise NotImplementedError("Implement with_enable_cache")

    def with_read_only(self, read_only: bool) -> Self:
        raise NotImplementedError("Implement with_read_only")

    def with_allowed_host(self, host: str) -> Self:
        raise NotImplementedError("Implement with_allowed_host")

    def build(self) -> DatabaseConfiguration:
        raise NotImplementedError("Implement build")
