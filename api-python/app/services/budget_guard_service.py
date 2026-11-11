"""Ported from api/Services/BudgetGuardService.cs."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.chat_message import ChatMessage
from ..schemas.chat_dtos import UsageSummaryDto
from ..settings import BudgetSettings, get_settings

logger = logging.getLogger(__name__)


class BudgetGuardService:
    def __init__(
        self, session: AsyncSession, options: BudgetSettings | None = None
    ) -> None:
        self._session = session
        self._options = options or get_settings().budget

    async def get_today_usage(self) -> UsageSummaryDto:
        start_of_day_utc = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        total_cost_today = (
            await self._session.execute(
                select(func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0)).where(
                    ChatMessage.role == "assistant",
                    ChatMessage.created_at >= start_of_day_utc,
                )
            )
        ).scalar_one()
        request_count_today = (
            await self._session.execute(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.role == "assistant",
                    ChatMessage.created_at >= start_of_day_utc,
                )
            )
        ).scalar_one()

        total_cost_today = Decimal(total_cost_today)
        daily_cap = (
            self._options.daily_cap_usd
            if self._options.daily_cap_usd > 0
            else Decimal("2.00")
        )
        max_requests = (
            self._options.max_daily_requests
            if self._options.max_daily_requests > 0
            else 500
        )
        exceeded = total_cost_today >= daily_cap or request_count_today >= max_requests
        return UsageSummaryDto(
            total_cost_today_usd=total_cost_today.quantize(
                Decimal("0.000001"), rounding=ROUND_HALF_EVEN
            ),
            daily_cap_usd=daily_cap,
            request_count_today=request_count_today,
            max_daily_requests=max_requests,
            budget_exceeded=exceeded,
        )

    async def try_reserve_request(self) -> tuple[bool, UsageSummaryDto]:
        usage = await self.get_today_usage()
        if usage.budget_exceeded:
            logger.warning(
                "Daily AI Chat budget reached! Cost today: $%.4f/$%.2f, Requests: %d/%d",
                usage.total_cost_today_usd,
                usage.daily_cap_usd,
                usage.request_count_today,
                usage.max_daily_requests,
            )
            return (False, usage)
        return (True, usage)
