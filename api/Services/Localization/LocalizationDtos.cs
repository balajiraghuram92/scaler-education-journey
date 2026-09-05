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
    DateTime? UpdatedAt
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
