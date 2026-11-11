"""Postgres-backed test helpers. Skips when no test database is reachable."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
TEST_DATABASE_URL = os.environ.get(
    "ISSUEINTEL_TEST_DATABASE_URL",
    "postgresql+asyncpg://issueintel:issueintel@localhost:5433/issueintel_test",
)
_migrated = False


def ensure_test_db() -> str | None:
    """Create the test database if missing and migrate it. None -> skip."""
    global _migrated
    if _migrated:
        return TEST_DATABASE_URL
    try:
        import asyncio

        import sqlalchemy as sa

        async def _create() -> None:
            parsed = urlparse(TEST_DATABASE_URL)
            dbname = parsed.path.lstrip("/")
            maint_url = TEST_DATABASE_URL.replace(f"/{dbname}", "/postgres", 1)
            engine = sa.ext.asyncio.create_async_engine(maint_url, isolation_level="AUTOCOMMIT")
            async with engine.connect() as conn:
                exists = (
                    await conn.execute(
                        sa.text("SELECT 1 FROM pg_database WHERE datname = :d"),
                        {"d": dbname},
                    )
                ).first()
                if not exists:
                    await conn.execute(sa.text(f'CREATE DATABASE "{dbname}"'))
            await engine.dispose()

        asyncio.run(_create())
        os.environ["ISSUEINTEL_DATABASE_URL"] = TEST_DATABASE_URL
        from alembic import command
        from alembic.config import Config

        cfg = Config(str(ROOT / "alembic.ini"))
        cfg.set_main_option("script_location", str(ROOT / "alembic"))
        command.upgrade(cfg, "head")
    except Exception:
        return None
    _migrated = True
    return TEST_DATABASE_URL
