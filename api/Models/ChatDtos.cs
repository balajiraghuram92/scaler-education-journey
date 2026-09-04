using System;
using System.Collections.Generic;

namespace StudyTracker.Api.Models;

public sealed record CreateChatConversationRequest(
    int? LessonId,
    string? Title
);

public sealed record ChatConversationDto(
    Guid Id,
    int UserId,
    int? LessonId,
    string? Title,
    DateTime CreatedAt,
    DateTime UpdatedAt
);

public sealed record SendChatMessageRequest(
    string Content,
    string? ClientRequestId = null
);

public sealed record ChatMessageDto(
    Guid Id,
    Guid ConversationId,
    string Role,
    string Content,
    string? ClientRequestId,
    int? PromptTokens,
    int? CompletionTokens,
    bool UsageEstimated,
    decimal? EstimatedCostUsd,
    int? LatencyMs,
    DateTime CreatedAt
);

public sealed record UsageSummaryDto(
    decimal TotalCostTodayUsd,
    decimal DailyCapUsd,
    int RequestCountToday,
    int MaxDailyRequests,
    bool BudgetExceeded
);

public sealed record UserUsageDto(
    int UserId,
    string Email,
    string? DisplayName,
    int TotalRequests,
    decimal TotalCostUsd,
    int TotalPromptTokens,
    int TotalCompletionTokens,
    DateTime? LastRequestAt
);
