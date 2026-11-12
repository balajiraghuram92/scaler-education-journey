using System;
using System.Collections.Generic;
using System.Linq;
using StudyTracker.Api.Models.Localization;

namespace StudyTracker.Api.Data;

public static class LocalizationSeedData
{
    public static void Seed(StudyTrackerContext context)
    {
        if (!context.LocalizationProjects.Any())
        {
        var now = DateTime.UtcNow;

        // 1. Seed Project: auroraline-hud-v3
        var project = new LocalizationProject
        {
            Slug = "auroraline-hud-v3",
            Name = "Auroraline Automotive — HUD Strings",
            SourceLocale = "en-US",
            ClientAlias = "Client Team Kestrel",
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

        var additionalStrings = new List<LocalizationString>
        {
            // ~18 Short UI Labels (2-4 words each)
            new() { ProjectId = project.Id, Key = "hud.gear.park", SourceText = "Park gear selected", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.gear.neutral", SourceText = "Neutral gear active", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.gear.drive", SourceText = "Drive gear engaged", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.tire.frontleft", SourceText = "Front left tire", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.tire.frontright", SourceText = "Front right tire", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.tire.rearleft", SourceText = "Rear left tire", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.tire.rearright", SourceText = "Rear right tire", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.media.play", SourceText = "Resume media playback", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.media.pause", SourceText = "Pause audio playback", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.media.next", SourceText = "Skip next track", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.media.volume", SourceText = "Adjust volume level", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.climate.fanspeed", SourceText = "Fan speed setting", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.climate.autoclimate", SourceText = "Automatic climate control", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.settings.brightness", SourceText = "Display screen brightness", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.settings.language", SourceText = "Select system language", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.nav.recalculating", SourceText = "Recalculating navigation route", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.nav.arrived", SourceText = "Destination reached ahead", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.battery.low", SourceText = "Low battery level", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.battery.fastcharge", SourceText = "Fast charging active", CreatedAt = now.AddDays(-25) },

            // ~14 Medium Warning/Status Messages (8-16 words each)
            new() { ProjectId = project.Id, Key = "hud.warning.enginetemp", SourceText = "Engine coolant temperature high. Reduce speed and stop vehicle safely when convenient.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.warning.tirepressure", SourceText = "Low tire pressure detected in rear left tire. Please inspect and reinflate promptly.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.assist.lanedeparture", SourceText = "Lane departure alert: Unintended drift detected. Please keep both hands firmly on steering wheel.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.assist.forwardcollision", SourceText = "Forward collision warning: Obstacle detected directly ahead. Apply emergency braking immediately.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.assist.blindspot", SourceText = "Blind spot alert: Vehicle detected in adjacent blind zone. Do not change travel lanes.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.sensor.parkingrear", SourceText = "Rear ultrasonic parking sensors active. Obstacle detected within three feet of rear bumper.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.connect.bluetooth", SourceText = "Driver smartphone paired successfully over wireless Bluetooth. Audio streaming and hands-free calls ready.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.nav.tollroad", SourceText = "Approaching toll road plaza in two miles. Move into open electronic transponder lane.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.system.otaavailable", SourceText = "New system software update is ready for installation. Park vehicle and connect to Wi-Fi.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.service.oilchange", SourceText = "Engine oil and filter change recommended within the next five hundred driving miles.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.service.brakewear", SourceText = "Front brake pad wear limit reached. Schedule maintenance inspection with authorized dealer promptly.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.assist.adaptivecruise", SourceText = "Adaptive cruise control enabled. Following distance set to three vehicle lengths ahead.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.alert.tractioncontrol", SourceText = "Electronic traction control engaged. Slippery road conditions detected on current roadway surface.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.alert.washerfluid", SourceText = "Windshield washer fluid reservoir is low. Please refill with recommended washer fluid.", CreatedAt = now.AddDays(-25) },

            // ~8 Longer Instructional/Legal Strings (80-120 words each)
            new() { ProjectId = project.Id, Key = "hud.legal.assistdisclaimer", SourceText = "Driver assistance systems, including adaptive cruise control, lane centering, and forward collision mitigation, are supplemental conveniences designed to support safe vehicle operation. These automated features do not replace an attentive driver or sound operational judgment. You must keep both hands on the steering wheel, monitor surrounding traffic conditions continuously, and remain prepared to resume manual vehicle control at any moment. Adverse weather, severe road glare, degraded pavement markings, and sensor contamination can impair system reliability. The vehicle operator remains fully responsible for safe driving and compliance with all motor vehicle traffic safety laws.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.dataprivacy", SourceText = "Connected vehicle services collect and transmit real-time telemetry data, including precise geographic location, operational diagnostics, trip durations, and driving performance indicators, to secure cloud servers. This information is utilized solely to enhance navigation accuracy, deliver remote diagnostic troubleshooting, facilitate emergency roadside response, and improve safety systems. You may manage data transmission preferences, request data export, or revoke cloud analytics permissions at any time through the privacy settings menu. Anonymous technical diagnostics may continue to be collected to fulfill statutory compliance, warranty administration, and mandatory automotive recall obligations.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.appstoreterms", SourceText = "Access to and use of third-party downloadable applications through the Auroraline In-Vehicle Digital Marketplace is governed by these Terms of Use and individual application developer licensing agreements. Certain applications may require active subscription services, supplementary cellular data connectivity, or paired mobile device integration to function properly. Applications must never be operated while driving if doing so causes driver distraction or creates safety hazards. Auroraline assumes no liability for external software errors, unauthorized in-app payment transactions, third-party content availability, or intermittent service disruptions caused by telecommunications network outages.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.otaconsent", SourceText = "Over-the-air software updates provide essential vehicle enhancements, operating system upgrades, security patches, and regulatory compliance adjustments. During installation, the vehicle must be safely parked in a secure location with the transmission in Park and the engine completely turned off. Select safety-critical electronic systems and drive functionality may be temporarily disabled while updates are applied. Do not attempt to operate the vehicle until the installation progress bar finishes and the infotainment display indicates successful completion. Failure to install mandatory firmware updates in a timely manner may impact warranty coverage and vehicle operations.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.sosfeature", SourceText = "The Automated Emergency Assistance SOS feature automatically initiates a hands-free voice call to emergency dispatch personnel whenever vehicle crash sensors register severe collision impact or airbag deployment. If occupants cannot respond verbally, vehicle location coordinates, travel direction, and impact severity telemetry are automatically transmitted to first responders. You may also initiate an emergency voice call manually by pressing and holding the overhead SOS button for three consecutive seconds. Emergency dispatch services depend on active mobile cellular network coverage and global positioning satellite reception in your operational territory.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.teendriver", SourceText = "The Teen Driver and Valet Monitoring configuration enables primary account holders to establish customized driving constraints, including maximum vehicle speed governors, audio volume limits, and mandatory seatbelt audio mutes. When activated, the system records comprehensive driving telemetry, including severe braking instances, forward collision alerts, high-speed travel events, and stability control interventions. A detailed driving report card is generated and accessible through the connected mobile application following each completed trip. These monitoring capabilities encourage safe, disciplined driving behaviors and reinforce responsible operational habits for newly licensed secondary operators.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.roadsideassist", SourceText = "Auroraline 24/7 Roadside Assistance provides prompt, professional emergency support for flat tires, unexpected mechanical breakdowns, high-voltage battery depletion, lockouts, and emergency towing services. When requested via the in-vehicle head-up display or connected smartphone application, your exact GPS coordinates, vehicle identification number, and current system diagnostics are automatically dispatched to the nearest authorized roadside assistance provider. Service availability, tow mileage allowances, and reimbursement coverage vary based on vehicle warranty terms and active membership tier. Emergency roadside services are subject to local traffic safety regulations, hazardous weather restrictions, and regional service provider availability.", CreatedAt = now.AddDays(-25) },
            new() { ProjectId = project.Id, Key = "hud.legal.telemetrydisclosure", SourceText = "This vehicle continuously records diagnostic trouble codes, component temperatures, braking pressure histories, battery charge cycles, and powertrain efficiency metrics. Telemetry records are stored in non-volatile onboard electronic control modules and intermittently synchronized with engineering monitoring databases during service visits and secure wireless sessions. Collected diagnostic telemetry is utilized by automotive service technicians and development engineers to investigate unexpected component failures, design resilient hardware revisions, and refine onboard energy management algorithms. No biometric voice recordings or passenger visual imagery are ever captured or preserved as part of standard engineering telemetry datasets.", CreatedAt = now.AddDays(-25) }
        };

        context.LocalizationStrings.AddRange(strSpeed, strFuel, strNav, strTemp, strDoor, strGear);
        context.LocalizationStrings.AddRange(additionalStrings);
        context.SaveChanges();

        // 4. Seed de-DE Translations
        var translations = new List<LocalizationTranslation>
        {
            new() { StringId = strSpeed.Id, LocaleCode = "de-DE", TargetText = "Aktuelle Geschwindigkeit", Stage = "Approved", TranslationSource = "Manual", NeedsReview = false, UpdatedAt = now.AddDays(-2) },
            new() { StringId = strFuel.Id, LocaleCode = "de-DE", TargetText = "Kraftstoff niedrig", Stage = "Reviewed", TranslationSource = "Manual", NeedsReview = false, UpdatedAt = now.AddDays(-3) },
            new() { StringId = strNav.Id, LocaleCode = "de-DE", TargetText = "Links abbiegen", Stage = "Translated", TranslationSource = "Manual", NeedsReview = false, UpdatedAt = now.AddHours(-12) },
            // hud.climate.temp has no translation row seeded -> New
            new() { StringId = strDoor.Id, LocaleCode = "de-DE", TargetText = "Tür offen", Stage = "Approved", TranslationSource = "Manual", NeedsReview = false, UpdatedAt = now.AddDays(-5) },
            new() { StringId = strGear.Id, LocaleCode = "de-DE", TargetText = "Rückwärtsgang eingelegt", Stage = "Reviewed", TranslationSource = "Manual", NeedsReview = false, UpdatedAt = now.AddDays(-1) }
        };
        context.LocalizationTranslations.AddRange(translations);

        // fr-FR and es-ES translations delivered through the marketplace. A job can only be
        // "Submitted for Review" or "Approved" once every string has target text, so these two
        // locales are fully translated: fr-FR awaiting owner review, es-ES already approved.
        var seededStrings = new List<LocalizationString> { strSpeed, strFuel, strNav, strTemp, strDoor, strGear };
        seededStrings.AddRange(additionalStrings);
        foreach (var str in seededStrings)
        {
            var (french, spanish) = LocalizationSeedTranslations.ByKey[str.Key];
            context.LocalizationTranslations.Add(new LocalizationTranslation
            {
                StringId = str.Id,
                LocaleCode = "fr-FR",
                TargetText = french,
                Stage = "Translated",
                TranslationSource = "Marketplace",
                NeedsReview = false,
                UpdatedAt = now.AddDays(-1)
            });
            context.LocalizationTranslations.Add(new LocalizationTranslation
            {
                StringId = str.Id,
                LocaleCode = "es-ES",
                TargetText = spanish,
                Stage = "Approved",
                TranslationSource = "Marketplace",
                NeedsReview = false,
                UpdatedAt = now.AddDays(-1)
            });
        }

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

        // 7. Seed 5 vendor teams (real names stay; aliases face the client). Every
        // project locale below is covered by at least one team's Languages, so no
        // Languages extension was needed.
        var vendorMaria = new Vendor { Name = "Maria Fischer", Alias = "Vendor Team Larch", Languages = "de-DE,fr-FR" };
        var vendorKenji = new Vendor { Name = "Kenji Sato", Alias = "Vendor Team Osprey", Languages = "ja-JP,ko-KR" };
        var vendorAiko = new Vendor { Name = "Aiko Tanaka", Alias = "Vendor Team Juniper", Languages = "ja-JP" };
        var vendorMarcus = new Vendor { Name = "Marcus Webb", Alias = "Vendor Team Heron", Languages = "ja-JP,zh-CN,ko-KR" };
        var vendorElena = new Vendor { Name = "Elena Rostova", Alias = "Vendor Team Cedar", Languages = "de-DE,es-ES" };

        context.LocalizationVendors.AddRange(vendorMaria, vendorKenji, vendorAiko, vendorMarcus, vendorElena);
        context.SaveChanges();

        // 8. Seed Translation Jobs (assigned teams only; the open-for-bidding job is gone)
        var allStrings = context.LocalizationStrings.Where(s => s.ProjectId == project.Id).ToList();
        var totalStringCount = allStrings.Count;
        var totalWordCount = allStrings.Sum(s => s.SourceText.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length);

        // de-DE: Assigned to Maria Fischer's team
        var jobDe = new TranslationJob
        {
            ProjectId = project.Id,
            LocaleCode = "de-DE",
            Status = "Assigned",
            StringCount = totalStringCount,
            WordCount = totalWordCount,
            VendorId = vendorMaria.Id,
            CreatedAt = now.AddDays(-5)
        };
        context.LocalizationTranslationJobs.Add(jobDe);
        context.SaveChanges();

        // fr-FR: Submitted for Review
        var jobFr = new TranslationJob
        {
            ProjectId = project.Id,
            LocaleCode = "fr-FR",
            Status = "SubmittedForReview",
            StringCount = totalStringCount,
            WordCount = totalWordCount,
            VendorId = vendorMaria.Id,
            CreatedAt = now.AddDays(-7),
            SubmittedAt = now.AddDays(-1)
        };
        context.LocalizationTranslationJobs.Add(jobFr);
        context.SaveChanges();

        // es-ES: Approved
        var jobEs = new TranslationJob
        {
            ProjectId = project.Id,
            LocaleCode = "es-ES",
            Status = "Approved",
            StringCount = totalStringCount,
            WordCount = totalWordCount,
            VendorId = vendorElena.Id,
            CreatedAt = now.AddDays(-10),
            SubmittedAt = now.AddDays(-3),
            ApprovedAt = now.AddDays(-1)
        };
        context.LocalizationTranslationJobs.Add(jobEs);
        context.SaveChanges();

        // Ledger entry for approved job
        context.LocalizationLedgerEntries.Add(new LedgerEntry
        {
            ProjectId = project.Id,
            Source = "Marketplace",
            Amount = 195m,
            RelatedMarketplaceJobId = jobEs.Id,
            CreatedAt = now.AddDays(-1)
        });

        // 8b. Seed the demo project's Gold service agreement (every locale covered)
        var agreement = new ServiceAgreement
        {
            ProjectId = project.Id,
            Tier = ServiceTiers.Gold,
            ValidFrom = now.AddDays(-30),
            CreatedAt = now
        };
        context.LocalizationServiceAgreements.Add(agreement);
        context.SaveChanges();
        context.LocalizationTeamAssignments.AddRange(
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendorMaria.Id, LocaleCode = "de-DE", MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold) },
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendorKenji.Id, LocaleCode = "ja-JP", MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold) },
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendorMarcus.Id, LocaleCode = "zh-CN", MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold) },
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendorMaria.Id, LocaleCode = "fr-FR", MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold) },
            new TeamAssignment { AgreementId = agreement.Id, VendorId = vendorElena.Id, LocaleCode = "es-ES", MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold) });
        context.SaveChanges();

        // 9. Seed 2 Provider Health Rows
        var healthAzureTranslator = new ProviderHealthSnapshot
        {
            Provider = "AzureTranslator",
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
        context.LocalizationProviderHealth.AddRange(healthAzureTranslator, healthAzure);

        // 10. Seed usage caps for the demo project
        context.LocalizationUsageCaps.AddRange(
            new LocalizationUsageCap { ProjectId = project.Id, Kind = UsageCapKinds.MachineTranslation, MonthlyLimit = 2000000, UpdatedAt = now },
            new LocalizationUsageCap { ProjectId = project.Id, Kind = UsageCapKinds.Llm, MonthlyLimit = 5000000, UpdatedAt = now });

        context.SaveChanges();
        }

        SeedGlossaryTerms(context);
    }

    public static void EnsureUsageCaps(StudyTrackerContext context)
    {
        var project = context.LocalizationProjects.FirstOrDefault(p => p.Slug == "auroraline-hud-v3");
        if (project is null)
        {
            return;
        }

        var wanted = new[]
        {
            (UsageCapKinds.MachineTranslation, 2000000L),
            (UsageCapKinds.Llm, 5000000L)
        };
        var existing = context.LocalizationUsageCaps
            .Where(c => c.ProjectId == project.Id)
            .Select(c => c.Kind)
            .ToList();
        var added = false;
        foreach (var (kind, limit) in wanted)
        {
            if (existing.Contains(kind))
            {
                continue;
            }

            context.LocalizationUsageCaps.Add(new LocalizationUsageCap
            {
                ProjectId = project.Id,
                Kind = kind,
                MonthlyLimit = limit,
                UpdatedAt = DateTime.UtcNow
            });
            added = true;
        }

        if (added)
        {
            context.SaveChanges();
        }

        EnsureServiceAgreement(context, project);
    }

    private static void EnsureServiceAgreement(StudyTrackerContext context, LocalizationProject project)
    {
        var realAliases = new Dictionary<string, string>
        {
            ["Maria Fischer"] = "Vendor Team Larch",
            ["Kenji Sato"] = "Vendor Team Osprey",
            ["Aiko Tanaka"] = "Vendor Team Juniper",
            ["Marcus Webb"] = "Vendor Team Heron",
            ["Elena Rostova"] = "Vendor Team Cedar"
        };
        var vendors = context.LocalizationVendors
            .Where(v => realAliases.Keys.Contains(v.Name))
            .ToList();
        foreach (var vendor in vendors)
        {
            if (vendor.Alias == $"Vendor Team {vendor.Id}")
            {
                vendor.Alias = realAliases[vendor.Name];
            }
        }

        if (project.ClientAlias == $"Client Team {project.Id}")
        {
            project.ClientAlias = "Client Team Kestrel";
        }

        var agreement = context.LocalizationServiceAgreements
            .FirstOrDefault(a => a.ProjectId == project.Id);
        if (agreement is null)
        {
            agreement = new ServiceAgreement
            {
                ProjectId = project.Id,
                Tier = ServiceTiers.Gold,
                ValidFrom = DateTime.UtcNow,
                CreatedAt = DateTime.UtcNow
            };
            context.LocalizationServiceAgreements.Add(agreement);
            context.SaveChanges();
        }

        var byName = vendors.ToDictionary(v => v.Name, v => v.Id);
        var wanted = new[]
        {
            ("de-DE", "Maria Fischer"),
            ("ja-JP", "Kenji Sato"),
            ("zh-CN", "Marcus Webb"),
            ("fr-FR", "Maria Fischer"),
            ("es-ES", "Elena Rostova")
        };
        var assigned = context.LocalizationTeamAssignments
            .Where(t => t.AgreementId == agreement.Id)
            .Select(t => t.LocaleCode)
            .ToList();
        foreach (var (localeCode, vendorName) in wanted)
        {
            if (assigned.Contains(localeCode) || !byName.TryGetValue(vendorName, out var vendorId))
            {
                continue;
            }

            context.LocalizationTeamAssignments.Add(new TeamAssignment
            {
                AgreementId = agreement.Id,
                VendorId = vendorId,
                LocaleCode = localeCode,
                MemberCount = ServiceTiers.MembersFor(ServiceTiers.Gold)
            });
        }

        context.SaveChanges();
    }

    private static void SeedGlossaryTerms(StudyTrackerContext context)
    {
        if (context.LocalizationGlossaryTerms.Any())
        {
            return;
        }

        var project = context.LocalizationProjects.FirstOrDefault(p => p.Slug == "auroraline-hud-v3");
        if (project is null)
        {
            return;
        }

        var terms = new List<GlossaryTerm>
        {
            // de-DE
            new() { ProjectId = project.Id, LocaleCode = "de-DE", SourceTerm = "HUD", TargetTerm = "HUD", Notes = "Keep untranslated; system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "de-DE", SourceTerm = "ABS", TargetTerm = "ABS", Notes = "Keep untranslated; safety-system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "de-DE", SourceTerm = "Turn left", TargetTerm = "Links abbiegen", Notes = "Navigation instruction; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "de-DE", SourceTerm = "Low fuel warning", TargetTerm = "Kraftstoffwarnung", Notes = "Warning label; prefer the single-noun form." },
            new() { ProjectId = project.Id, LocaleCode = "de-DE", SourceTerm = "Door ajar", TargetTerm = "Tür offen", Notes = "Alert label; short form for the HUD." },
            // ja-JP
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", SourceTerm = "HUD", TargetTerm = "HUD", Notes = "Keep untranslated; system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", SourceTerm = "ABS", TargetTerm = "ABS", Notes = "Keep untranslated; safety-system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", SourceTerm = "Turn left", TargetTerm = "左折", Notes = "Navigation instruction; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", SourceTerm = "Low fuel warning", TargetTerm = "燃料残量警告", Notes = "Warning label; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "ja-JP", SourceTerm = "Door ajar", TargetTerm = "ドアが開いています", Notes = "Alert label; approved HUD rendering." },
            // zh-CN
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", SourceTerm = "HUD", TargetTerm = "HUD", Notes = "Keep untranslated; system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", SourceTerm = "ABS", TargetTerm = "ABS", Notes = "Keep untranslated; safety-system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", SourceTerm = "Turn left", TargetTerm = "左转", Notes = "Navigation instruction; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", SourceTerm = "Low fuel warning", TargetTerm = "燃油不足警告", Notes = "Warning label; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "zh-CN", SourceTerm = "Door ajar", TargetTerm = "车门未关", Notes = "Alert label; approved HUD rendering." },
            // fr-FR
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", SourceTerm = "HUD", TargetTerm = "HUD", Notes = "Keep untranslated; system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", SourceTerm = "ABS", TargetTerm = "ABS", Notes = "Keep untranslated; safety-system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", SourceTerm = "Turn left", TargetTerm = "Tournez à gauche", Notes = "Navigation instruction; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", SourceTerm = "Low fuel warning", TargetTerm = "Avertissement de carburant bas", Notes = "Warning label; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "fr-FR", SourceTerm = "Door ajar", TargetTerm = "Porte entrouverte", Notes = "Alert label; approved HUD rendering." },
            // es-ES
            new() { ProjectId = project.Id, LocaleCode = "es-ES", SourceTerm = "HUD", TargetTerm = "HUD", Notes = "Keep untranslated; system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "es-ES", SourceTerm = "ABS", TargetTerm = "ABS", Notes = "Keep untranslated; safety-system acronym." },
            new() { ProjectId = project.Id, LocaleCode = "es-ES", SourceTerm = "Turn left", TargetTerm = "Gire a la izquierda", Notes = "Navigation instruction; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "es-ES", SourceTerm = "Low fuel warning", TargetTerm = "Advertencia de combustible bajo", Notes = "Warning label; approved HUD rendering." },
            new() { ProjectId = project.Id, LocaleCode = "es-ES", SourceTerm = "Door ajar", TargetTerm = "Puerta entreabierta", Notes = "Alert label; approved HUD rendering." },
        };
        context.LocalizationGlossaryTerms.AddRange(terms);
        context.SaveChanges();
    }
}
