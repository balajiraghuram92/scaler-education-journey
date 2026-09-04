namespace StudyTracker.Api.Options;

public sealed class BudgetOptions
{
    public const string SectionName = "Budget";

    public decimal DailyCapUsd { get; set; } = 2.00m;

    public int MaxDailyRequests { get; set; } = 500;
}
