"""Budget guard per run, per day and per product.

A call that would exceed a budget fails with BudgetExceeded and is logged by
the caller. Scopes without a row are unlimited.
"""
from __future__ import annotations

import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g4 import Budget

PRODUCT = "tessera-editor"


class BudgetExceeded(Exception):
    pass


def _day_key() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")


async def seed_budgets(
    session: AsyncSession,
    run_limit: float = 5.0,
    day_limit: float = 50.0,
    product_limit: float = 1000.0,
) -> None:
    for scope, key, limit in (
        ("run", "*", run_limit),
        ("day", _day_key(), day_limit),
        ("product", PRODUCT, product_limit),
    ):
        existing = (
            await session.execute(
                select(Budget).where(Budget.scope == scope, Budget.key == key)
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(Budget(scope=scope, key=key, limit_usd=limit))
    await session.commit()


async def _rows_for(
    session: AsyncSession, run_id: str | None
) -> dict[tuple[str, str], Budget]:
    keys = [("day", _day_key()), ("product", PRODUCT)]
    if run_id:
        keys.append(("run", run_id))
    rows: dict[tuple[str, str], Budget] = {}
    for scope, key in keys:
        row = (
            await session.execute(
                select(Budget).where(Budget.scope == scope, Budget.key == key)
            )
        ).scalar_one_or_none()
        if row is not None:
            rows[(scope, key)] = row
    return rows


async def check_budget(
    session: AsyncSession, run_id: str | None, estimate_usd: float
) -> None:
    """Fail before the provider call when the estimate would exceed a budget."""
    for (scope, key), row in (await _rows_for(session, run_id)).items():
        if row.spent_usd + estimate_usd > row.limit_usd:
            raise BudgetExceeded(
                f"budget exceeded: {scope}/{key} "
                f"spent={row.spent_usd:.4f} + est={estimate_usd:.4f} "
                f"> limit={row.limit_usd:.4f}"
            )


async def record_spend(
    session: AsyncSession, run_id: str | None, cost_usd: float
) -> None:
    rows = await _rows_for(session, run_id)
    for row in rows.values():
        row.spent_usd += cost_usd
        row.updated_at = datetime.datetime.now(datetime.UTC)
    if rows:
        await session.commit()
