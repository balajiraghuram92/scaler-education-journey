using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

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
    IReadOnlyList<LocalizationLocaleDto> Locales,
    bool AiEnabled,
    string? Tier
);

public sealed record LocalizationStringRowDto(
    int StringId,
    string Key,
    string SourceText,
    string LocaleCode,
    string? TargetText,
    string Stage,
    string TranslationSource,
    DateTime? UpdatedAt
);

public sealed record VendorStringRowDto(
    int StringId,
    string Key,
    string SourceText,
    string LocaleCode,
    string? TargetText,
    string Stage,
    string TranslationSource,
    DateTime? UpdatedAt,
    int? Score,
    bool NeedsReview,
    string? RawMtText,
    int? RawMtScore,
    bool InJob,
    bool VendorReviewed
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

public sealed record TranslationJobRowDto(
    int? Id,
    int ProjectId,
    string LocaleCode,
    string Status,
    int StringCount,
    int WordCount,
    int CompletedPercent,
    string? VendorTeamAlias,
    int? MemberCount,
    DateTime? CreatedAt,
    DateTime? SubmittedAt,
    DateTime? ApprovedAt
);

public sealed record VendorJobRowDto(
    int Id,
    string ClientAlias,
    string LocaleCode,
    string Status,
    int StringCount,
    int WordCount,
    int CompletedPercent,
    DateTime? CreatedAt,
    DateTime? SubmittedAt,
    DateTime? ApprovedAt
);

public sealed record VendorTeamDto(
    int Id,
    string Alias,
    string Languages
);

public sealed record OpsVendorTeamDto(
    int Id,
    string Alias,
    string RealName,
    string Languages
);

public sealed record AgreementTeamDto(
    string LocaleCode,
    string VendorTeamAlias,
    int MemberCount
);

public sealed record ServiceAgreementDto(
    string Tier,
    int MembersPerTeam,
    DateTime ValidFrom,
    DateTime? ValidTo,
    IReadOnlyList<AgreementTeamDto> Teams
);

public sealed record OpsAgreementTeamDto(
    string LocaleCode,
    string VendorTeamAlias,
    int MemberCount,
    int VendorTeamId,
    string VendorTeamRealName
);

public sealed record OpsServiceAgreementDto(
    string Tier,
    int MembersPerTeam,
    DateTime ValidFrom,
    DateTime? ValidTo,
    string ClientAlias,
    IReadOnlyList<OpsAgreementTeamDto> Teams
);

public sealed record AgreementTeamRequest(
    string? LocaleCode,
    int? VendorTeamId
);

public sealed record SaveAgreementRequest(
    string? Tier,
    DateTime? ValidFrom,
    DateTime? ValidTo,
    IReadOnlyList<AgreementTeamRequest>? Teams
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
    IReadOnlyList<UsageMissingRateDto> RatesMissing,
    [property: JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)] IReadOnlyList<UsageCapDto>? Caps
);

public sealed record UsageCapDto(
    string Kind,
    long? MonthlyLimit,
    long Used
);

public sealed record ProjectControlsDto(
    string ProjectSlug,
    bool AiEnabled,
    IReadOnlyList<UsageCapDto> Caps
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
