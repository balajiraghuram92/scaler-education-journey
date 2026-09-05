using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Data;

public static class LocalizationSeedData
{
    public static void Seed(StudyTrackerContext context)
    {
        if (context.LocalizationProjects.Any())
        {
            return;
        }

        var now = DateTime.UtcNow;

        // 1. Seed Project: auroraline-hud-v3
        var project = new LocalizationProject
        {
            Slug = "auroraline-hud-v3",
            Name = "Auroraline Automotive — HUD Strings",
            SourceLocale = "en-US",
            CreatedAt = now.AddDays(-30)
        };
        context.LocalizationProjects.Add(project);
        context.SaveChanges();

        // 2. Seed 5 Locales
        var locales = new List<LocalizationLocale>
        {
            new() { ProjectId = project.Id, LocaleCode = "de-DE", DisplayName = "German (Germany)" },
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", DisplayName = "Japanese (Japan)" },
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", DisplayName = "Chinese Simplified (China)" },
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", DisplayName = "French (France)" },
            new() { ProjectId = project.Id, LocaleCode = "es-ES", DisplayName = "Spanish (Spain)" }
        };
        context.LocalizationLocales.AddRange(locales);
        context.SaveChanges();

        // 3. Seed 6 Strings
        var strSpeed = new LocalizationString { ProjectId = project.Id, Key = "hud.speed.label", SourceText = "Current Speed", CreatedAt = now.AddDays(-25) };
        var strFuel = new LocalizationString { ProjectId = project.Id, Key = "hud.warning.lowfuel", SourceText = "Low fuel warning", CreatedAt = now.AddDays(-25) };
        var strNav = new LocalizationString { ProjectId = project.Id, Key = "hud.nav.turnleft", SourceText = "Turn left ahead", CreatedAt = now.AddDays(-25) };
        var strTemp = new LocalizationString { ProjectId = project.Id, Key = "hud.climate.temp", SourceText = "Cabin temperature", CreatedAt = now.AddDays(-25) };
        var strDoor = new LocalizationString { ProjectId = project.Id, Key = "hud.alert.doorajar", SourceText = "Door ajar", CreatedAt = now.AddDays(-25) };
        var strGear = new LocalizationString { ProjectId = project.Id, Key = "hud.gear.reverse", SourceText = "Reverse gear engaged", CreatedAt = now.AddDays(-25) };

        context.LocalizationStrings.AddRange(strSpeed, strFuel, strNav, strTemp, strDoor, strGear);
        context.SaveChanges();

        // 4. Seed de-DE Translations
        var translations = new List<LocalizationTranslation>
        {
            new() { StringId = strSpeed.Id, LocaleCode = "de-DE", TargetText = "Aktuelle Geschwindigkeit", Stage = "Approved", TranslationSource = "Manual", QpsScore = 95, NeedsReview = false, UpdatedAt = now.AddDays(-2) },
            new() { StringId = strFuel.Id, LocaleCode = "de-DE", TargetText = "Kraftstoff niedrig", Stage = "Reviewed", TranslationSource = "Manual", QpsScore = 88, NeedsReview = false, UpdatedAt = now.AddDays(-3) },
            new() { StringId = strNav.Id, LocaleCode = "de-DE", TargetText = "Links abbiegen", Stage = "Translated", TranslationSource = "Manual", QpsScore = 82, NeedsReview = false, UpdatedAt = now.AddHours(-12) },
            // hud.climate.temp has no translation row seeded -> New
            new() { StringId = strDoor.Id, LocaleCode = "de-DE", TargetText = "Tür offen", Stage = "Approved", TranslationSource = "Manual", QpsScore = 92, NeedsReview = false, UpdatedAt = now.AddDays(-5) },
            new() { StringId = strGear.Id, LocaleCode = "de-DE", TargetText = "Rückwärtsgang eingelegt", Stage = "Reviewed", TranslationSource = "Manual", QpsScore = 89, NeedsReview = false, UpdatedAt = now.AddDays(-1) }
        };
        context.LocalizationTranslations.AddRange(translations);

        // 5. Seed 3 Workflow Steps
        var steps = new List<WorkflowStep>
        {
            new() { ProjectId = project.Id, Order = 1, Trigger = "On Manual Click", Action = "Mark Translated", LastRunAt = now.AddHours(-2), LastRunOutcome = "12 strings affected" },
            new() { ProjectId = project.Id, Order = 2, Trigger = "On Manual Click", Action = "Send to Review", LastRunAt = now.AddDays(-1), LastRunOutcome = "8 strings affected" },
            new() { ProjectId = project.Id, Order = 3, Trigger = "On Manual Click", Action = "Approve", LastRunAt = null, LastRunOutcome = null }
        };
        context.LocalizationWorkflowSteps.AddRange(steps);

        // 6. Seed 3 Build Snapshots
        var snap1 = new BuildSnapshot
        {
            ProjectId = project.Id,
            SnapshotIdentifier = "snap-2026-09-01-a",
            SourceRevision = "r18234",
            LocalizationRevision = "l09981",
            Config = "Production-Default",
            CreatedAt = new DateTime(2026, 9, 1, 14, 0, 0, DateTimeKind.Utc)
        };
        var snap2 = new BuildSnapshot
        {
            ProjectId = project.Id,
            SnapshotIdentifier = "snap-2026-08-22-c",
            SourceRevision = "r17910",
            LocalizationRevision = "l09750",
            Config = "Production-Default",
            CreatedAt = new DateTime(2026, 8, 22, 11, 30, 0, DateTimeKind.Utc)
        };
        var snap3 = new BuildSnapshot
        {
            ProjectId = project.Id,
            SnapshotIdentifier = "snap-2026-08-10-b",
            SourceRevision = "r17402",
            LocalizationRevision = "l09520",
            Config = "Production-Default",
            CreatedAt = new DateTime(2026, 8, 10, 16, 45, 0, DateTimeKind.Utc)
        };
        context.LocalizationBuildSnapshots.AddRange(snap1, snap2, snap3);
        context.SaveChanges();

        // Seed Snapshot Locale Counts
        var snap1Counts = new List<BuildSnapshotLocaleCount>
        {
            new() { BuildSnapshotId = snap1.Id, LocaleCode = "de-DE", ApprovedCount = 128 },
            new() { BuildSnapshotId = snap1.Id, LocaleCode = "ja-JP", ApprovedCount = 94 },
            new() { BuildSnapshotId = snap1.Id, LocaleCode = "zh-CN", ApprovedCount = 156 },
            new() { BuildSnapshotId = snap1.Id, LocaleCode = "fr-FR", ApprovedCount = 140 },
            new() { BuildSnapshotId = snap1.Id, LocaleCode = "es-ES", ApprovedCount = 94 }
        };
        var snap2Counts = new List<BuildSnapshotLocaleCount>
        {
            new() { BuildSnapshotId = snap2.Id, LocaleCode = "de-DE", ApprovedCount = 120 },
            new() { BuildSnapshotId = snap2.Id, LocaleCode = "ja-JP", ApprovedCount = 90 },
            new() { BuildSnapshotId = snap2.Id, LocaleCode = "zh-CN", ApprovedCount = 150 },
            new() { BuildSnapshotId = snap2.Id, LocaleCode = "fr-FR", ApprovedCount = 138 },
            new() { BuildSnapshotId = snap2.Id, LocaleCode = "es-ES", ApprovedCount = 90 }
        };
        var snap3Counts = new List<BuildSnapshotLocaleCount>
        {
            new() { BuildSnapshotId = snap3.Id, LocaleCode = "de-DE", ApprovedCount = 110 },
            new() { BuildSnapshotId = snap3.Id, LocaleCode = "ja-JP", ApprovedCount = 85 },
            new() { BuildSnapshotId = snap3.Id, LocaleCode = "zh-CN", ApprovedCount = 146 },
            new() { BuildSnapshotId = snap3.Id, LocaleCode = "fr-FR", ApprovedCount = 130 }
        };
        context.LocalizationBuildSnapshotLocaleCounts.AddRange(snap1Counts);
        context.LocalizationBuildSnapshotLocaleCounts.AddRange(snap2Counts);
        context.LocalizationBuildSnapshotLocaleCounts.AddRange(snap3Counts);

        // 7. Seed 5 Vendors
        var vendorMaria = new Vendor { Name = "Maria Fischer", Languages = "de-DE,fr-FR", Rating = 4.9m };
        var vendorKenji = new Vendor { Name = "Kenji Sato", Languages = "ja-JP,ko-KR", Rating = 5.0m };
        var vendorAiko = new Vendor { Name = "Aiko Tanaka", Languages = "ja-JP", Rating = 4.7m };
        var vendorMarcus = new Vendor { Name = "Marcus Webb", Languages = "ja-JP,zh-CN,ko-KR", Rating = 4.2m };
        var vendorElena = new Vendor { Name = "Elena Rostova", Languages = "de-DE,es-ES", Rating = 4.8m };

        context.LocalizationVendors.AddRange(vendorMaria, vendorKenji, vendorAiko, vendorMarcus, vendorElena);
        context.SaveChanges();

        // 8. Seed Marketplace Jobs & Bids
        // de-DE: Awarded to Maria Fischer
        var jobDe = new MarketplaceJob
        {
            ProjectId = project.Id,
            LocaleCode = "de-DE",
            Status = "Awarded",
            StringCount = 6,
            WordCount = 1240,
            SuggestedPriceLow = 180m,
            SuggestedPriceHigh = 240m,
            AwardedVendorId = vendorMaria.Id,
            PostedAt = now.AddDays(-5),
            AwardedAt = now.AddDays(-2)
        };
        context.LocalizationMarketplaceJobs.Add(jobDe);
        context.SaveChanges();

        var bidDe = new MarketplaceBid
        {
            MarketplaceJobId = jobDe.Id,
            VendorId = vendorMaria.Id,
            ProposedPrice = 210m,
            Note = "Experienced automotive HUD terminology specialist.",
            Status = "Awarded",
            SubmittedAt = now.AddDays(-3)
        };
        context.LocalizationMarketplaceBids.Add(bidDe);

        // ja-JP: Open with 3 bids
        var jobJa = new MarketplaceJob
        {
            ProjectId = project.Id,
            LocaleCode = "ja-JP",
            Status = "Open",
            StringCount = 6,
            WordCount = 1240,
            SuggestedPriceLow = 180m,
            SuggestedPriceHigh = 240m,
            PostedAt = now.AddDays(-3)
        };
        context.LocalizationMarketplaceJobs.Add(jobJa);
        context.SaveChanges();

        var bidJaKenji = new MarketplaceBid
        {
            MarketplaceJobId = jobJa.Id,
            VendorId = vendorKenji.Id,
            ProposedPrice = 345m,
            Note = "Native Japanese automotive localization expert.",
            Status = "Pending",
            SubmittedAt = now.AddDays(-2)
        };
        var bidJaAiko = new MarketplaceBid
        {
            MarketplaceJobId = jobJa.Id,
            VendorId = vendorAiko.Id,
            ProposedPrice = 298m,
            Note = "Automotive cluster & infotainment UI specialist.",
            Status = "Pending",
            SubmittedAt = now.AddDays(-2).AddHours(4)
        };
        var bidJaMarcus = new MarketplaceBid
        {
            MarketplaceJobId = jobJa.Id,
            VendorId = vendorMarcus.Id,
            ProposedPrice = 420m,
            Note = "Senior technical translator with HUD experience.",
            Status = "Pending",
            SubmittedAt = now.AddDays(-1)
        };
        context.LocalizationMarketplaceBids.AddRange(bidJaKenji, bidJaAiko, bidJaMarcus);

        // fr-FR: Submitted for Review
        var jobFr = new MarketplaceJob
        {
            ProjectId = project.Id,
            LocaleCode = "fr-FR",
            Status = "SubmittedForReview",
            StringCount = 6,
            WordCount = 1240,
            SuggestedPriceLow = 180m,
            SuggestedPriceHigh = 240m,
            AwardedVendorId = vendorMaria.Id,
            PostedAt = now.AddDays(-7),
            AwardedAt = now.AddDays(-4),
            SubmittedAt = now.AddDays(-1)
        };
        context.LocalizationMarketplaceJobs.Add(jobFr);
        context.SaveChanges();

        var bidFr = new MarketplaceBid
        {
            MarketplaceJobId = jobFr.Id,
            VendorId = vendorMaria.Id,
            ProposedPrice = 215m,
            Note = "Automotive translation completed per DIN standards.",
            Status = "Awarded",
            SubmittedAt = now.AddDays(-5)
        };
        context.LocalizationMarketplaceBids.Add(bidFr);

        // es-ES: Approved
        var jobEs = new MarketplaceJob
        {
            ProjectId = project.Id,
            LocaleCode = "es-ES",
            Status = "Approved",
            StringCount = 6,
            WordCount = 1240,
            SuggestedPriceLow = 180m,
            SuggestedPriceHigh = 240m,
            AwardedVendorId = vendorElena.Id,
            PostedAt = now.AddDays(-10),
            AwardedAt = now.AddDays(-6),
            SubmittedAt = now.AddDays(-3),
            ApprovedAt = now.AddDays(-1)
        };
        context.LocalizationMarketplaceJobs.Add(jobEs);
        context.SaveChanges();

        var bidEs = new MarketplaceBid
        {
            MarketplaceJobId = jobEs.Id,
            VendorId = vendorElena.Id,
            ProposedPrice = 195m,
            Note = "Certified Spanish automotive translator.",
            Status = "Awarded",
            SubmittedAt = now.AddDays(-7)
        };
        context.LocalizationMarketplaceBids.Add(bidEs);

        // Ledger entry for approved job
        context.LocalizationLedgerEntries.Add(new LedgerEntry
        {
            ProjectId = project.Id,
            Source = "Marketplace",
            Amount = 195m,
            RelatedMarketplaceJobId = jobEs.Id,
            CreatedAt = now.AddDays(-1)
        });

        // 9. Seed 2 Provider Health Rows
        var healthGoogle = new ProviderHealthSnapshot
        {
            Provider = "GoogleMT",
            P50LatencyMs = 210,
            P99LatencyMs = 640,
            ErrorRatePercent = 0.4m,
            CircuitState = "Closed",
            UpdatedAt = now
        };
        var healthAzure = new ProviderHealthSnapshot
        {
            Provider = "LlmAzureGpt",
            P50LatencyMs = 480,
            P99LatencyMs = 1450,
            ErrorRatePercent = 1.1m,
            CircuitState = "Closed",
            UpdatedAt = now
        };
        context.LocalizationProviderHealth.AddRange(healthGoogle, healthAzure);

        context.SaveChanges();
    }
}
