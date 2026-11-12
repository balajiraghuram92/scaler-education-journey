"""Ported from api/Services/Localization/LocalizationDtos.cs.

Lives in Services in C#; the port keeps DTOs in schemas/ like every other phase.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import model_serializer

from .base import CamelModel, DotNetDateTime, DotNetDecimal


class LocalizationLocaleDto(CamelModel):
    id: int
    locale_code: str
    display_name: str


class LocalizationProjectDto(CamelModel):
    id: int
    slug: str
    name: str
    source_locale: str
    created_at: DotNetDateTime
    locales: list[LocalizationLocaleDto]
    ai_enabled: bool
    tier: str | None


class LocalizationStringRowDto(CamelModel):
    string_id: int
    key: str
    source_text: str
    locale_code: str
    target_text: str | None
    stage: str
    translation_source: str
    updated_at: DotNetDateTime | None


class VendorStringRowDto(CamelModel):
    string_id: int
    key: str
    source_text: str
    locale_code: str
    target_text: str | None
    stage: str
    translation_source: str
    updated_at: DotNetDateTime | None
    score: int | None
    needs_review: bool
    raw_mt_text: str | None
    raw_mt_score: int | None
    in_job: bool
    vendor_reviewed: bool


class UpdateTranslationRequest(CamelModel):
    target_text: str | None = None


class WorkflowStepDto(CamelModel):
    id: int
    project_id: int
    order: int
    trigger: str
    action: str
    condition_expression: str | None
    last_run_at: DotNetDateTime | None
    last_run_outcome: str | None


class AddWorkflowStepRequest(CamelModel):
    trigger: str | None = None
    action: str | None = None
    condition_expression: str | None = None


class UpdateWorkflowStepRequest(CamelModel):
    trigger: str | None = None
    action: str | None = None
    condition_expression: str | None = None


class ReorderWorkflowStepRequest(CamelModel):
    direction: str | None = None


class BuildSnapshotLocaleCountDto(CamelModel):
    locale_code: str
    approved_count: int


class BuildSnapshotDto(CamelModel):
    id: int
    snapshot_identifier: str
    source_revision: str
    localization_revision: str
    config: str
    created_at: DotNetDateTime
    locale_counts: list[BuildSnapshotLocaleCountDto]


class TranslationJobRowDto(CamelModel):
    id: int | None
    project_id: int
    locale_code: str
    status: str
    string_count: int
    word_count: int
    completed_percent: int
    vendor_team_alias: str | None
    member_count: int | None
    created_at: DotNetDateTime | None
    submitted_at: DotNetDateTime | None
    approved_at: DotNetDateTime | None


class VendorJobRowDto(CamelModel):
    id: int
    client_alias: str
    locale_code: str
    status: str
    string_count: int
    word_count: int
    completed_percent: int
    created_at: DotNetDateTime | None
    submitted_at: DotNetDateTime | None
    approved_at: DotNetDateTime | None


class VendorTeamDto(CamelModel):
    id: int
    alias: str
    languages: str


class OpsVendorTeamDto(CamelModel):
    id: int
    alias: str
    real_name: str
    languages: str


class AgreementTeamDto(CamelModel):
    locale_code: str
    vendor_team_alias: str
    member_count: int


class ServiceAgreementDto(CamelModel):
    tier: str
    members_per_team: int
    valid_from: DotNetDateTime
    valid_to: DotNetDateTime | None
    teams: list[AgreementTeamDto]


class OpsAgreementTeamDto(CamelModel):
    locale_code: str
    vendor_team_alias: str
    member_count: int
    vendor_team_id: int
    vendor_team_real_name: str


class OpsServiceAgreementDto(CamelModel):
    tier: str
    members_per_team: int
    valid_from: DotNetDateTime
    valid_to: DotNetDateTime | None
    client_alias: str
    teams: list[OpsAgreementTeamDto]


class AgreementTeamRequest(CamelModel):
    locale_code: str | None = None
    vendor_team_id: int | None = None


class SaveAgreementRequest(CamelModel):
    tier: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    teams: list[AgreementTeamRequest] | None = None


class ProviderHealthSnapshotDto(CamelModel):
    id: int
    provider: str
    p50_latency_ms: int
    p99_latency_ms: int
    error_rate_percent: DotNetDecimal
    circuit_state: str
    updated_at: DotNetDateTime


class UsageMeterTotalDto(CamelModel):
    meter: str
    calls: int
    failed_calls: int
    cache_hits: int
    units: int
    units_out: int | None
    cost_usd: DotNetDecimal


class UsageOperationTotalDto(CamelModel):
    meter: str
    operation: str
    calls: int
    failed_calls: int
    cache_hits: int
    units: int
    units_out: int | None
    cost_usd: DotNetDecimal


class UsageLocaleTotalDto(CamelModel):
    meter: str
    locale_code: str | None
    calls: int
    units: int
    units_out: int | None
    cost_usd: DotNetDecimal


class UsageDayTotalDto(CamelModel):
    date: str
    meter: str
    units: int
    units_out: int | None
    cost_usd: DotNetDecimal


class UsageMissingRateDto(CamelModel):
    meter: str
    unit_kind: str


class UsageSummaryDto(CamelModel):
    month: str
    project_slug: str | None
    meters: list[UsageMeterTotalDto]
    by_operation: list[UsageOperationTotalDto]
    by_locale: list[UsageLocaleTotalDto]
    by_day: list[UsageDayTotalDto]
    rates_missing: list[UsageMissingRateDto]
    caps: list[UsageCapDto] | None = None

    @model_serializer(mode="wrap")
    def _omit_null_caps(self, handler: Any) -> dict[str, Any]:
        # C# marks Caps [JsonIgnore(WhenWritingNull)]: the array is present
        # only when a project slug is given.
        data = handler(self)
        if data.get("caps") is None:
            data.pop("caps", None)
        return data


class UsageCapDto(CamelModel):
    kind: str
    monthly_limit: int | None
    used: int


class ProjectControlsDto(CamelModel):
    project_slug: str
    ai_enabled: bool
    caps: list[UsageCapDto]


class UsageEventDto(CamelModel):
    id: int
    project_slug: str
    workflow_step_id: int | None
    meter: str
    operation: str
    locale_code: str | None
    units: int
    units_out: int | None
    cache_hit: bool
    succeeded: bool
    cost_usd: DotNetDecimal
    occurred_at: DotNetDateTime


class ProviderRateDto(CamelModel):
    id: int
    meter: str
    unit_kind: str
    usd_per_million: DotNetDecimal
    valid_from: DotNetDateTime


class AddProviderRateRequest(CamelModel):
    meter: str | None = None
    unit_kind: str | None = None
    usd_per_million: Decimal | None = None
    valid_from: datetime | None = None
