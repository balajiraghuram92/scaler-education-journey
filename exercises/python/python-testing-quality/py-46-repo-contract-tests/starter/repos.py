from __future__ import annotations

from pathlib import Path


class SqlUsageRepo:
    """SQLite-backed ``UsageRepo`` (use the stdlib ``sqlite3``).

    - ``__init__(path)`` opens the database and creates the table if missing.
    - ``get(tenant)`` returns 0 for unknown tenants.
    - ``add(tenant, tokens)`` upserts, COMMITS, and returns the new running total,
      so a second connection to the same file sees the data.
    - ``close()`` closes the connection.
    """

    def __init__(self, path: str | Path) -> None:
        raise NotImplementedError("Implement SqlUsageRepo.__init__")

    def get(self, tenant: str) -> int:
        raise NotImplementedError("Implement SqlUsageRepo.get")

    def add(self, tenant: str, tokens: int) -> int:
        raise NotImplementedError("Implement SqlUsageRepo.add")

    def close(self) -> None:
        raise NotImplementedError("Implement SqlUsageRepo.close")


class FileUsageRepo:
    """JSON-file ``UsageRepo``.

    - A missing file means no usage (``get`` returns 0 and must not create the file).
    - ``add`` writes atomically: write a temporary sibling file, then ``os.replace``.
      No temporary file may be left behind.
    """

    def __init__(self, path: str | Path) -> None:
        raise NotImplementedError("Implement FileUsageRepo.__init__")

    def get(self, tenant: str) -> int:
        raise NotImplementedError("Implement FileUsageRepo.get")

    def add(self, tenant: str, tokens: int) -> int:
        raise NotImplementedError("Implement FileUsageRepo.add")
