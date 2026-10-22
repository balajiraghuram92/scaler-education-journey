from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path


class SqlUsageRepo:
    """SQLite-backed repo; every add is committed so a second connection sees it."""

    def __init__(self, path: str | Path) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS usage("
            "tenant TEXT PRIMARY KEY, tokens INTEGER NOT NULL)"
        )
        self._conn.commit()

    def get(self, tenant: str) -> int:
        row = self._conn.execute(
            "SELECT tokens FROM usage WHERE tenant = ?", (tenant,)
        ).fetchone()
        return int(row[0]) if row else 0

    def add(self, tenant: str, tokens: int) -> int:
        with self._conn:  # commits on success, rolls back on error
            self._conn.execute(
                "INSERT INTO usage(tenant, tokens) VALUES (?, ?) "
                "ON CONFLICT(tenant) DO UPDATE SET tokens = tokens + excluded.tokens",
                (tenant, tokens),
            )
        return self.get(tenant)

    def close(self) -> None:
        self._conn.close()


class FileUsageRepo:
    """JSON file repo with atomic replace so a crash never leaves a torn file."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def _load(self) -> dict[str, int]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def get(self, tenant: str) -> int:
        return self._load().get(tenant, 0)

    def add(self, tenant: str, tokens: int) -> int:
        data = self._load()
        data[tenant] = data.get(tenant, 0) + tokens
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data), encoding="utf-8")
        os.replace(tmp, self._path)
        return data[tenant]
