"""BudgetGuardService tests on the scratch database."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage
from app.services.budget_guard_service import BudgetGuardService
from app.settings import BudgetSettings


async def _seed_assistant_message(
    db: AsyncSession, cost: Decimal, created_at: datetime | None = None
) -> None:
    now = datetime.now(timezone.utc)
    user = AppUser(
        email=f"{uuid4().hex}@example.com",
        password_hash="h",
        password_salt="s",
        role="User",
        status="Approved",
        created_at=now,
        totp_enabled=False,
    )
    db.add(user)
    await db.flush()
    conversation = ChatConversation(user_id=user.id, created_at=now, updated_at=now)
    db.add(conversation)
    await db.flush()
    db.add(
        ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content="reply",
            prompt_tokens=10,
            completion_tokens=5,
            usage_estimated=False,
            estimated_cost_usd=cost,
            created_at=created_at or now,
        )
    )
    await db.flush()


@pytest.mark.asyncio
async def test_empty_day_is_within_budget(scratch_session: AsyncSession) -> None:
    service = BudgetGuardService(
        scratch_session, BudgetSettings(Budget__DailyCapUsd=Decimal("2.00"))
    )

    usage = await service.get_today_usage()

    assert usage.total_cost_today_usd == Decimal("0.000000")
    assert usage.daily_cap_usd == Decimal("2.00")
    assert usage.request_count_today == 0
    assert usage.max_daily_requests == 500
    assert usage.budget_exceeded is False

    allowed, _ = await service.try_reserve_request()
    assert allowed is True


@pytest.mark.asyncio
async def test_budget_exceeded_by_cost(scratch_session: AsyncSession) -> None:
    await _seed_assistant_message(scratch_session, Decimal("2.50"))
    service = BudgetGuardService(
        scratch_session, BudgetSettings(Budget__DailyCapUsd=Decimal("2.00"))
    )

    usage = await service.get_today_usage()

    assert usage.total_cost_today_usd == Decimal("2.500000")
    assert usage.request_count_today == 1
    assert usage.budget_exceeded is True

    allowed, _ = await service.try_reserve_request()
    assert allowed is False


@pytest.mark.asyncio
async def test_budget_exceeded_by_request_count(scratch_session: AsyncSession) -> None:
    await _seed_assistant_message(scratch_session, Decimal("0.01"))
    service = BudgetGuardService(
        scratch_session, BudgetSettings(Budget__MaxDailyRequests=1)
    )

    usage = await service.get_today_usage()

    assert usage.request_count_today == 1
    assert usage.budget_exceeded is True
