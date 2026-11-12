"""Ported from api/Services/Localization/ProviderHealthService.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.localization.provider_health_snapshot import ProviderHealthSnapshot
from ...schemas.localization_dtos import ProviderHealthSnapshotDto
from .localization_exceptions import ProviderNotFoundException


class ProviderHealthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_health_async(self) -> list[ProviderHealthSnapshotDto]:
        rows = (
            await self._session.execute(
                select(ProviderHealthSnapshot).order_by(ProviderHealthSnapshot.id)
            )
        ).scalars().all()
        return [_dto(row) for row in rows]

    async def simulate_outage_async(self, provider: str) -> ProviderHealthSnapshotDto:
        record = (
            await self._session.execute(
                select(ProviderHealthSnapshot).where(
                    func.lower(ProviderHealthSnapshot.provider) == provider.lower()
                )
            )
        ).scalar_one_or_none()
        if record is None:
            raise ProviderNotFoundException(provider)
        record.circuit_state = "Open"
        record.error_rate_percent = Decimal("87.5")
        record.updated_at = datetime.now(UTC)
        await self._session.flush()
        return _dto(record)

    async def resolve_outage_async(self, provider: str) -> ProviderHealthSnapshotDto:
        record = (
            await self._session.execute(
                select(ProviderHealthSnapshot).where(
                    func.lower(ProviderHealthSnapshot.provider) == provider.lower()
                )
            )
        ).scalar_one_or_none()
        if record is None:
            raise ProviderNotFoundException(provider)
        record.circuit_state = "Closed"
        record.error_rate_percent = (
            Decimal("0.4") if record.provider.lower() == "azuretranslator" else Decimal("1.1")
        )
        record.updated_at = datetime.now(UTC)
        await self._session.flush()
        return _dto(record)


def _dto(row: ProviderHealthSnapshot) -> ProviderHealthSnapshotDto:
    return ProviderHealthSnapshotDto(
        id=row.id,
        provider=row.provider,
        p50_latency_ms=row.p50_latency_ms,
        p99_latency_ms=row.p99_latency_ms,
        error_rate_percent=row.error_rate_percent,
        circuit_state=row.circuit_state,
        updated_at=row.updated_at,
    )
