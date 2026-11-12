using System;

namespace StudyTracker.Api.Models.Localization;

public static class ServiceTiers
{
    public const string Silver = "Silver";
    public const string Gold = "Gold";
    public const string Platinum = "Platinum";

    public static int MembersFor(string tier) => tier switch
    {
        Silver => 3,
        Gold => 6,
        Platinum => 10,
        _ => throw new ArgumentException($"Unknown service tier '{tier}'.", nameof(tier))
    };
}
