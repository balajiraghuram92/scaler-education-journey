"""Ported from api/Services/Localization/UsageMeteringService.cs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal

from sqlalchemy import Date, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_provider_rate import LocalizationProviderRate
from ...models.localization.localization_usage_cap import LocalizationUsageCap
from ...models.localization.localization_usage_event import LocalizationUsageEvent
from ...models.localization.usage_constants import (
    UsageCapKinds,
    UsageMeters,
    UsageUnitKinds,
)
from ...schemas.localization_dtos import (
    UsageCapDto,
    UsageDayTotalDto,
    UsageEventDto,
    UsageLocaleTotalDto,
    UsageMeterTotalDto,
    UsageMissingRateDto,
    UsageOperationTotalDto,
    UsageSummaryDto,
)
from .localization_exceptions import LocalizationProjectNotFoundException


@dataclass
class UsageCallRecord:
    project_id: int
    workflow_step_id: int | None
    meter: str
    operation: str
    locale_code: str | None
    units: int
    units_out: int | None
    cache_hit: bool
    succeeded: bool


class UsageMeteringService:
    """Records one immutable usage event per paid provider call and serves the
    operations-only usage summaries. Costs use the rate in force when the
    call happened; a call with no rate costs 0 and shows up in ratesMissing."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._rates: list[LocalizationProviderRate] | None = None

    async def record_async(
        self, call: UsageCallRecord, occurred_at: datetime
    ) -> None:
        """Computes the cost and adds the event. Does not save; the caller saves."""
        rates = await self._load_rates_async()
        self._session.add(
            LocalizationUsageEvent(
                project_id=call.project_id,
                workflow_step_id=call.workflow_step_id,
                meter=call.meter,
                operation=call.operation,
                locale_code=call.locale_code,
                units=call.units,
                units_out=call.units_out,
                cache_hit=call.cache_hit,
                succeeded=call.succeeded,
                cost_usd=_cost_for(rates, call, occurred_at).quantize(
                    Decimal("0.000001"), rounding=ROUND_HALF_EVEN
                ),
                occurred_at=occurred_at,
            )
        )

    async def get_summary_async(
        self, project_slug: str | None, year: int, month: int
    ) -> UsageSummaryDto:
        project_id = await self._resolve_project_id_async(project_slug)
        start = datetime(year, month, 1, tzinfo=UTC)
        end = (
            datetime(year + 1, 1, 1, tzinfo=UTC)
            if month == 12
            else datetime(year, month + 1, 1, tzinfo=UTC)
        )

        event = LocalizationUsageEvent
        filters = [event.occurred_at >= start, event.occurred_at < end]
        if project_id is not None:
            filters.append(event.project_id == project_id)

        by_meter_rows = (
            await self._session.execute(
                select(
                    event.meter,
                    func.count().label("calls"),
                    func.count(case((~event.succeeded, 1))).label("failed_calls"),
                    func.count(case((event.cache_hit, 1))).label("cache_hits"),
                    func.sum(event.units).label("units"),
                    func.sum(event.units_out).label("units_out"),
                    func.sum(event.cost_usd).label("cost_usd"),
                )
                .where(*filters)
                .group_by(event.meter)
                .order_by(event.meter)
            )
        ).all()

        by_operation_rows = (
            await self._session.execute(
                select(
                    event.meter,
                    event.operation,
                    func.count().label("calls"),
                    func.count(case((~event.succeeded, 1))).label("failed_calls"),
                    func.count(case((event.cache_hit, 1))).label("cache_hits"),
                    func.sum(event.units).label("units"),
                    func.sum(event.units_out).label("units_out"),
                    func.sum(event.cost_usd).label("cost_usd"),
                )
                .where(*filters)
                .group_by(event.meter, event.operation)
                .order_by(event.meter, event.operation)
            )
        ).all()

        by_locale_rows = (
            await self._session.execute(
                select(
                    event.meter,
                    event.locale_code,
                    func.count().label("calls"),
                    func.sum(event.units).label("units"),
                    func.sum(event.units_out).label("units_out"),
                    func.sum(event.cost_usd).label("cost_usd"),
                )
                .where(*filters)
                .group_by(event.meter, event.locale_code)
                .order_by(event.meter, event.locale_code)
            )
        ).all()

        day = cast(event.occurred_at, Date).label("day")
        by_day_rows = (
            await self._session.execute(
                select(
                    day,
                    event.meter,
                    func.sum(event.units).label("units"),
                    func.sum(event.units_out).label("units_out"),
                    func.sum(event.cost_usd).label("cost_usd"),
                )
                .where(*filters)
                .group_by(day, event.meter)
                .order_by(day, event.meter)
            )
        ).all()

        usage_rows = (
            await self._session.execute(
                select(
                    event.meter,
                    func.min(event.occurred_at).label("min_time"),
                    func.count(event.units_out).label("output_count"),
                )
                .where(*filters)
                .group_by(event.meter)
            )
        ).all()

        rates = await self._load_rates_async()
        missing: list[UsageMissingRateDto] = []
        for row in sorted(usage_rows, key=lambda r: r.meter):
            for kind in _kinds_for(row.meter, row.output_count > 0):
                in_force = any(
                    r.meter == row.meter
                    and r.unit_kind == kind
                    and r.valid_from <= row.min_time
                    for r in rates
                )
                if not in_force:
                    missing.append(
                        UsageMissingRateDto(meter=row.meter, unit_kind=kind)
                    )

        caps: list[UsageCapDto] | None = None
        if project_id is not None:
            cap_rows = (
                await self._session.execute(
                    select(LocalizationUsageCap).where(
                        LocalizationUsageCap.project_id == project_id
                    )
                )
            ).scalars().all()
            used = await self._used_totals_async(project_id, start, end)
            caps = [
                UsageCapDto(
                    kind=kind,
                    monthly_limit=next(
                        (c.monthly_limit for c in cap_rows if c.kind == kind), None
                    ),
                    used=used.get(kind, 0),
                )
                for kind in (
                    UsageCapKinds.MACHINE_TRANSLATION,
                    UsageCapKinds.LLM,
                )
            ]

        return UsageSummaryDto(
            month=f"{year:04d}-{month:02d}",
            project_slug=project_slug,
            meters=[
                UsageMeterTotalDto(
                    meter=row.meter,
                    calls=row.calls,
                    failed_calls=row.failed_calls,
                    cache_hits=row.cache_hits,
                    units=row.units,
                    units_out=_output_units(row.meter, row.units_out),
                    cost_usd=row.cost_usd,
                )
                for row in by_meter_rows
            ],
            by_operation=[
                UsageOperationTotalDto(
                    meter=row.meter,
                    operation=row.operation,
                    calls=row.calls,
                    failed_calls=row.failed_calls,
                    cache_hits=row.cache_hits,
                    units=row.units,
                    units_out=_output_units(row.meter, row.units_out),
                    cost_usd=row.cost_usd,
                )
                for row in by_operation_rows
            ],
            by_locale=[
                UsageLocaleTotalDto(
                    meter=row.meter,
                    locale_code=row.locale_code,
                    calls=row.calls,
                    units=row.units,
                    units_out=_output_units(row.meter, row.units_out),
                    cost_usd=row.cost_usd,
                )
                for row in by_locale_rows
            ],
            by_day=[
                UsageDayTotalDto(
                    date=row.day.isoformat(),
                    meter=row.meter,
                    units=row.units,
                    units_out=_output_units(row.meter, row.units_out),
                    cost_usd=row.cost_usd,
                )
                for row in by_day_rows
            ],
            rates_missing=missing,
            caps=caps,
        )

    async def begin_run_async(self, project_id: int, now: datetime) -> UsageBudget:
        """Loads the project's caps and this UTC month's used totals for a run.
        At most two queries; the returned budget tracks in-run spending in memory."""
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
        month_end = (
            datetime(now.year + 1, 1, 1, tzinfo=UTC)
            if now.month == 12
            else datetime(now.year, now.month + 1, 1, tzinfo=UTC)
        )

        caps = (
            await self._session.execute(
                select(LocalizationUsageCap).where(
                    LocalizationUsageCap.project_id == project_id
                )
            )
        ).scalars().all()

        used = await self._used_totals_async(project_id, month_start, month_end)
        return UsageBudget(
            {c.kind: c.monthly_limit for c in caps},
            used,
        )

    async def get_recent_events_async(
        self, project_slug: str | None, limit: int = 100
    ) -> list[UsageEventDto]:
        limit = min(max(limit, 1), 500)
        project_id = await self._resolve_project_id_async(project_slug)

        event = LocalizationUsageEvent
        stmt = (
            select(
                event.id,
                LocalizationProject.slug.label("project_slug"),
                event.workflow_step_id,
                event.meter,
                event.operation,
                event.locale_code,
                event.units,
                event.units_out,
                event.cache_hit,
                event.succeeded,
                event.cost_usd,
                event.occurred_at,
            )
            .join(LocalizationProject, LocalizationProject.id == event.project_id)
            .order_by(event.occurred_at.desc(), event.id.desc())
            .limit(limit)
        )
        if project_id is not None:
            stmt = stmt.where(event.project_id == project_id)

        rows = (await self._session.execute(stmt)).all()
        return [
            UsageEventDto(
                id=row.id,
                project_slug=row.project_slug,
                workflow_step_id=row.workflow_step_id,
                meter=row.meter,
                operation=row.operation,
                locale_code=row.locale_code,
                units=row.units,
                units_out=row.units_out,
                cache_hit=row.cache_hit,
                succeeded=row.succeeded,
                cost_usd=row.cost_usd,
                occurred_at=row.occurred_at,
            )
            for row in rows
        ]

    async def _resolve_project_id_async(self, project_slug: str | None) -> int | None:
        if project_slug is None:
            return None
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)
        return project.id

    async def _load_rates_async(self) -> list[LocalizationProviderRate]:
        if self._rates is None:
            self._rates = list(
                (await self._session.execute(select(LocalizationProviderRate)))
                .scalars()
                .all()
            )
        return self._rates

    async def _used_totals_async(
        self, project_id: int, start: datetime, end: datetime
    ) -> dict[str, int]:
        event = LocalizationUsageEvent
        rows = (
            await self._session.execute(
                select(
                    event.meter,
                    func.sum(event.units).label("units"),
                    func.sum(event.units_out).label("units_out"),
                )
                .where(
                    event.project_id == project_id,
                    ~event.cache_hit,
                    event.occurred_at >= start,
                    event.occurred_at < end,
                )
                .group_by(event.meter)
            )
        ).all()
        by_meter = {row.meter: row for row in rows}

        def meter_units(meter: str) -> int:
            row = by_meter.get(meter)
            return 0 if row is None else row.units

        def meter_units_out(meter: str) -> int:
            row = by_meter.get(meter)
            return 0 if row is None or row.units_out is None else row.units_out

        return {
            UsageCapKinds.MACHINE_TRANSLATION: meter_units(
                UsageMeters.MACHINE_TRANSLATION
            ),
            UsageCapKinds.LLM: (
                meter_units(UsageMeters.LLM_OPTIMIZE)
                + meter_units_out(UsageMeters.LLM_OPTIMIZE)
                + meter_units(UsageMeters.LLM_SCORE)
                + meter_units_out(UsageMeters.LLM_SCORE)
            ),
        }


# SUM over a column that is always null comes back as 0 from SQL (EF adds COALESCE);
# the character meter has no output units, so report null rather than 0 (CONTRACT 4.1).
def _output_units(meter: str, summed: int | None) -> int | None:
    if meter == UsageMeters.MACHINE_TRANSLATION:
        return None
    return summed if summed is not None else 0


def _cost_for(
    rates: list[LocalizationProviderRate],
    call: UsageCallRecord,
    occurred_at: datetime,
) -> Decimal:
    if call.cache_hit:
        return Decimal(0)
    if call.meter == UsageMeters.MACHINE_TRANSLATION:
        return _cost_part(
            rates, call.meter, UsageUnitKinds.CHAR, call.units, occurred_at
        )
    return _cost_part(
        rates, call.meter, UsageUnitKinds.INPUT_TOKEN, call.units, occurred_at
    ) + _cost_part(
        rates,
        call.meter,
        UsageUnitKinds.OUTPUT_TOKEN,
        call.units_out if call.units_out is not None else 0,
        occurred_at,
    )


def _cost_part(
    rates: list[LocalizationProviderRate],
    meter: str,
    unit_kind: str,
    units: int,
    occurred_at: datetime,
) -> Decimal:
    candidates = [
        r
        for r in rates
        if r.meter == meter and r.unit_kind == unit_kind and r.valid_from <= occurred_at
    ]
    if not candidates:
        return Decimal(0)
    rate = max(candidates, key=lambda r: r.valid_from)
    return Decimal(units) * rate.usd_per_million / Decimal(1000000)


def _kinds_for(meter: str, has_output: bool) -> list[str]:
    if meter == UsageMeters.MACHINE_TRANSLATION:
        return [UsageUnitKinds.CHAR]
    kinds = [UsageUnitKinds.INPUT_TOKEN]
    if has_output:
        kinds.append(UsageUnitKinds.OUTPUT_TOKEN)
    return kinds


class UsageBudget:
    """In-memory cap budget for one workflow run. A kind without a cap row is uncapped."""

    def __init__(self, limits: dict[str, int], used: dict[str, int]) -> None:
        self._limits = dict(limits)
        self._used = dict(used)

    def can_spend(self, cap_kind: str, known_units: int) -> bool:
        if cap_kind not in self._limits:
            return True
        used = self.used(cap_kind)
        if cap_kind == UsageCapKinds.MACHINE_TRANSLATION:
            return used + known_units <= self._limits[cap_kind]
        return used < self._limits[cap_kind]

    def spent(self, cap_kind: str, units: int) -> None:
        self._used[cap_kind] = self.used(cap_kind) + units

    def used(self, cap_kind: str) -> int:
        return self._used.get(cap_kind, 0)

    def limit(self, cap_kind: str) -> int | None:
        return self._limits.get(cap_kind)
