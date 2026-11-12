"""Ported from api/Services/Localization/LocalizationDtos.cs.

Lives in Services in C#; the port keeps DTOs in schemas/ like every other phase.
"""

from __future__ import annotations

from decimal import Decimal

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


class LocalizationStringRowDto(CamelModel):
    string_id: int
    key: str
    source_text: str
    locale_code: str
    target_text: str | None
    stage: str
    translation_source: str
    qps_score: int | None
    needs_review: bool
    updated_at: DotNetDateTime | None
    raw_mt_text: str | None = None
    raw_mt_qps_score: int | None = None


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


class MarketplaceBidDto(CamelModel):
    id: int
    marketplace_job_id: int
    vendor_id: int
    vendor_name: str
    vendor_languages: str
    vendor_rating: DotNetDecimal
    proposed_price: DotNetDecimal
    note: str
    status: str
    submitted_at: DotNetDateTime


class MarketplaceJobSummaryDto(CamelModel):
    id: int | None
    project_id: int
    locale_code: str
    status: str
    string_count: int
    word_count: int
    suggested_price_low: DotNetDecimal
    suggested_price_high: DotNetDecimal
    awarded_vendor_id: int | None
    awarded_vendor_name: str | None
    posted_at: DotNetDateTime | None
    awarded_at: DotNetDateTime | None
    submitted_at: DotNetDateTime | None
    approved_at: DotNetDateTime | None
    bid_count: int


class MarketplaceJobDto(CamelModel):
    id: int
    project_id: int
    locale_code: str
    status: str
    string_count: int
    word_count: int
    suggested_price_low: DotNetDecimal
    suggested_price_high: DotNetDecimal
    awarded_vendor_id: int | None
    awarded_vendor_name: str | None
    posted_at: DotNetDateTime | None
    awarded_at: DotNetDateTime | None
    submitted_at: DotNetDateTime | None
    approved_at: DotNetDateTime | None
    bids: list[MarketplaceBidDto]


class SubmitBidRequest(CamelModel):
    # C# binds a missing decimal to 0, which the service rejects; default 0
    # here so the same 400 (not a 422) is produced for a missing price.
    proposed_price: Decimal = Decimal("0")
    note: str | None = None


class VendorDto(CamelModel):
    id: int
    name: str
    languages: str
    rating: DotNetDecimal


class ProviderHealthSnapshotDto(CamelModel):
    id: int
    provider: str
    p50_latency_ms: int
    p99_latency_ms: int
    error_rate_percent: DotNetDecimal
    circuit_state: str
    updated_at: DotNetDateTime
