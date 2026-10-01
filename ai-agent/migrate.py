"""Apply ai-agent SQL migrations: ``python migrate.py``.

* Uses one plain synchronous connection (no pgvector registration), so it works
  on a brand-new database where the ``vector`` extension does not exist yet.
* Holds a session-level advisory lock, so two runners cannot interleave.
* Each file runs in its own real transaction together with its
  ``schema_migrations`` row: a failure rolls back only that file, earlier
  files stay committed and later files are not attempted.
* Idempotent: files already recorded in ``schema_migrations`` are skipped.
* The migrations directory is resolved relative to this file, not the cwd.

Migration files must not contain transaction control (BEGIN/COMMIT) or
statements that cannot run inside a transaction (e.g. CREATE INDEX CONCURRENTLY).
002 references ``lessons(id)``, so the API's EF Core migrations must run first.
"""

import os
import sys
from collections.abc import Callable
from pathlib import Path

import psycopg

import config

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
# Arbitrary fixed key; only needs to be unique among advisory locks in this DB.
ADVISORY_LOCK_KEY = 7_274_100_001

_CREATE_LEDGER = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename    TEXT PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


class MigrationError(RuntimeError):
    def __init__(self, filename: str, cause: Exception):
        super().__init__(f"{filename}: {cause}")
        self.filename = filename


def run_migrations(
    conninfo: str,
    migrations_dir: Path = MIGRATIONS_DIR,
    log: Callable[[str], None] = print,
) -> list[str]:
    """Apply pending migrations in filename order; return the names applied."""
    applied: list[str] = []
    files = sorted(migrations_dir.glob("*.sql"))
    with psycopg.connect(conninfo, autocommit=True) as conn:
        conn.execute("SELECT pg_advisory_lock(%s)", (ADVISORY_LOCK_KEY,))
        try:
            conn.execute(_CREATE_LEDGER)
            for path in files:
                sql = path.read_text(encoding="utf-8")
                try:
                    with conn.transaction():  # autocommit conn: a real BEGIN/COMMIT
                        done = conn.execute(
                            "SELECT 1 FROM schema_migrations WHERE filename = %s",
                            (path.name,),
                        ).fetchone()
                        if done:
                            log(f"{path.name}: already applied, skipping")
                            continue
                        conn.execute(sql)
                        conn.execute(
                            "INSERT INTO schema_migrations (filename) VALUES (%s)",
                            (path.name,),
                        )
                except psycopg.Error as exc:
                    raise MigrationError(path.name, exc) from exc
                applied.append(path.name)
                log(f"{path.name}: applied")
        finally:
            if not conn.closed:
                conn.execute("SELECT pg_advisory_unlock(%s)", (ADVISORY_LOCK_KEY,))
    return applied


def main() -> int:
    try:
        conninfo = config.build_database_conninfo(os.environ)
    except config.ConfigError as exc:
        print(f"migrate: configuration error: {exc}", file=sys.stderr)
        return 2
    try:
        applied = run_migrations(conninfo)
    except MigrationError as exc:
        print(f"migrate: FAILED, rolled back {exc}", file=sys.stderr)
        return 1
    except psycopg.OperationalError as exc:
        print(f"migrate: cannot connect to the database: {exc}", file=sys.stderr)
        return 1
    print(f"migrate: done ({len(applied)} applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
