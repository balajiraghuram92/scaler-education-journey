using System;
using System.Collections.Generic;

namespace StudyTracker.Api.Services.Localization;

public sealed record LocalizationLocaleDto(
    int Id,
    string LocaleCode,
    string DisplayName
);

public sealed record LocalizationProjectDto(
    int Id,
    string Slug,
    string Name,
    string SourceLocale,
    DateTime CreatedAt,
    IReadOnlyList<LocalizationLocaleDto> Locales
);

public sealed record LocalizationStringRowDto(
    int StringId,
    string Key,
    string SourceText,
    string LocaleCode,
    string? TargetText,
    string Stage,
    string TranslationSource,
    int? QpsScore,
    bool NeedsReview,
    DateTime? UpdatedAt,
    string? RawMtText = null,
    int? RawMtQpsScore = null
);

public sealed record UpdateTranslationRequest(
    string? TargetText
);

public sealed record WorkflowStepDto(
    int Id,
    int ProjectId,
    int Order,
    string Trigger,
    string Action,
    string? ConditionExpression,
    DateTime? LastRunAt,
    string? LastRunOutcome
);

public sealed record AddWorkflowStepRequest(
    string? Trigger,
    string Action,
    string? ConditionExpression
);

public sealed record UpdateWorkflowStepRequest(
    string? Trigger,
    string Action,
    string? ConditionExpression
);

public sealed record ReorderWorkflowStepRequest(
    string Direction
);

public sealed record BuildSnapshotLocaleCountDto(
    string LocaleCode,
    int ApprovedCount
);

public sealed record BuildSnapshotDto(
    int Id,
    string SnapshotIdentifier,
    string SourceRevision,
    string LocalizationRevision,
    string Config,
    DateTime CreatedAt,
    IReadOnlyList<BuildSnapshotLocaleCountDto> LocaleCounts
);

public sealed record MarketplaceBidDto(
    int Id,
    int MarketplaceJobId,
    int VendorId,
    string VendorName,
    string VendorLanguages,
    decimal VendorRating,
    decimal ProposedPrice,
    string Note,
    string Status,
    DateTime SubmittedAt
);

public sealed record MarketplaceJobSummaryDto(
    int? Id,
    int ProjectId,
    string LocaleCode,
    string Status,
    int StringCount,
    int WordCount,
    decimal SuggestedPriceLow,
    decimal SuggestedPriceHigh,
    int? AwardedVendorId,
    string? AwardedVendorName,
    DateTime? PostedAt,
    DateTime? AwardedAt,
    DateTime? SubmittedAt,
    DateTime? ApprovedAt,
    int BidCount
);

public sealed record MarketplaceJobDto(
    int Id,
    int ProjectId,
    string LocaleCode,
    string Status,
    int StringCount,
    int WordCount,
    decimal SuggestedPriceLow,
    decimal SuggestedPriceHigh,
    int? AwardedVendorId,
    string? AwardedVendorName,
    DateTime? PostedAt,
    DateTime? AwardedAt,
    DateTime? SubmittedAt,
    DateTime? ApprovedAt,
    IReadOnlyList<MarketplaceBidDto> Bids
);

public sealed record SubmitBidRequest(
    decimal ProposedPrice,
    string Note
);

public sealed record VendorDto(
    int Id,
    string Name,
    string Languages,
    decimal Rating
);

public sealed record ProviderHealthSnapshotDto(
    int Id,
    string Provider,
    int P50LatencyMs,
    int P99LatencyMs,
    decimal ErrorRatePercent,
    string CircuitState,
    DateTime UpdatedAt
);

public sealed record UsageMeterTotalDto(
    string Meter,
    int Calls,
    int FailedCalls,
    int CacheHits,
    int Units,
    int? UnitsOut,
    decimal CostUsd
);

public sealed record UsageOperationTotalDto(
    string Meter,
    string Operation,
    int Calls,
    int FailedCalls,
    int CacheHits,
    int Units,
    int? UnitsOut,
    decimal CostUsd
);

public sealed record UsageLocaleTotalDto(
    string Meter,
    string? LocaleCode,
    int Calls,
    int Units,
    int? UnitsOut,
    decimal CostUsd
);

public sealed record UsageDayTotalDto(
    string Date,
    string Meter,
    int Units,
    int? UnitsOut,
    decimal CostUsd
);

public sealed record UsageMissingRateDto(
    string Meter,
    string UnitKind
);

public sealed record UsageSummaryDto(
    string Month,
    string? ProjectSlug,
    IReadOnlyList<UsageMeterTotalDto> Meters,
    IReadOnlyList<UsageOperationTotalDto> ByOperation,
    IReadOnlyList<UsageLocaleTotalDto> ByLocale,
    IReadOnlyList<UsageDayTotalDto> ByDay,
    IReadOnlyList<UsageMissingRateDto> RatesMissing
);

public sealed record UsageEventDto(
    int Id,
    string ProjectSlug,
    int? WorkflowStepId,
    string Meter,
    string Operation,
    string? LocaleCode,
    int Units,
    int? UnitsOut,
    bool CacheHit,
    bool Succeeded,
    decimal CostUsd,
    DateTime OccurredAt
);

public sealed record ProviderRateDto(
    int Id,
    string Meter,
    string UnitKind,
    decimal UsdPerMillion,
    DateTime ValidFrom
);

public sealed record AddProviderRateRequest(
    string? Meter,
    string? UnitKind,
    decimal? UsdPerMillion,
    DateTime? ValidFrom
);
