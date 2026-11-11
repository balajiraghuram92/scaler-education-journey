"""P1 proof: the SQLAlchemy metadata matches the migrated database schema.

Reflects the scratch database (EF migrations applied, see README) and fails
on any table, column, type, nullability, key or index difference in either
direction. The comparison core lives in app/seed/schema_check.py (shared with
the --migrate CLI mode); the documented exceptions are named there.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from app.seed.schema_check import check_schema


def _scratch_url() -> str:
    return os.environ.get(
        "PY_SCRATCH_DATABASE_URL",
        "postgresql+asyncpg://studyuser:studyuserpass@localhost:5432/studytracker_py",
    )


@pytest.mark.asyncio
async def test_schema_parity() -> None:
    engine = create_async_engine(_scratch_url())
    try:
        errors = await check_schema(engine)
    finally:
        await engine.dispose()

    assert not errors, "schema parity failures:\n- " + "\n- ".join(errors)
