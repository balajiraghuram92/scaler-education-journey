# Localization Lab — Full Build Prompt for Gemini 3.8 Flash

> Copy-paste this entire file into Gemini 3.8 Flash as one prompt. It covers
> Phase 1 (Foundation + Orchestrator + Build Lock), Phase 2 (Google MT +
> Credits), Phase 2.5 (Vendor Marketplace), and the buildable UI/plumbing
> portion of Phase 3 (AI Vertical) — everything except the hand-written AI
> logic, which is explicitly carved out below and must NOT be generated.
>
> Repository: `scaler-education-journey`. Backend: C# ASP.NET Core minimal
> APIs + EF Core/Npgsql (`api/`). Frontend: React + Vite (`app/`). This is a
> new, self-contained feature — it does not touch any existing lesson/course
> content, auth, or chatbot code. Route root: `/lab-projects/localization`.

---

## 0. Read this first — repository conventions you MUST follow exactly

These are not suggestions; every new file must match these patterns byte-for-byte in style, because they will sit next to existing files reviewed by a human.

### 0.1 Backend model convention (from `api/Models/Lesson.cs`)

```csharp
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("lessons")]
public class Lesson
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Column("module_id")]
    public int ModuleId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ModuleId))]
    public CourseModule? Module { get; set; }

    [Required]
    [MaxLength(150)]
    [Column("slug")]
    public string Slug { get; set; } = string.Empty;
    // ...
}
```

Rules: PascalCase C# properties, `[Column("snake_case")]` for every column, `[Table("snake_case_plural")]` on the class, `[Required]`/`[MaxLength]` where applicable, navigation properties marked `[JsonIgnore]` with `[ForeignKey(nameof(XId))]`, default `= string.Empty` for non-nullable strings, nullable reference types (`?`) for optional relations.

### 0.2 DbContext convention (from `api/Data/StudyTrackerContext.cs`)

```csharp
public DbSet<Lesson> Lessons { get; set; } = null!;
public DbSet<Course> Courses { get; set; } = null!;
```

Every new entity gets one `public DbSet<T> PluralName { get; set; } = null!;` line added to `StudyTrackerContext.cs`. Do not create a second DbContext.

### 0.3 Minimal API endpoint convention (from `api/Endpoints/ExerciseEndpoints.cs`)

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using StudyTracker.Api.Models;
using StudyTracker.Api.Services.Exercises;

namespace StudyTracker.Api.Endpoints;

public static class ExerciseEndpoints
{
    public static void MapExerciseEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/exercises");

        group.MapGet("/{exerciseId}", GetMetadata)
            .WithName("GetExerciseMetadata");
        // ...
    }

    private static IResult GetMetadata(string exerciseId, ExerciseMetadataService metadataService, HttpContext httpContext)
    {
        try
        {
            return Results.Ok(metadataService.GetById(exerciseId));
        }
        catch (ExerciseNotFoundException)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Exercise not found.", "The requested exercise does not exist.");
        }
    }

    private static IResult Problem(HttpContext context, int statusCode, string title, string detail)
    {
        return Results.Json(
            new { type = "https://tools.ietf.org/html/rfc7231", title, status = statusCode, detail, instance = context.Request.Path.Value, traceId = context.TraceIdentifier },
            contentType: "application/problem+json",
            statusCode: statusCode);
    }
}
```

Rules: one `static class XEndpoints` per feature area, one `MapXEndpoints(this IEndpointRouteBuilder app)` extension method, `app.MapGroup("/api/...")`, route handlers are `private static` methods taking route params + injected services + `HttpContext` + (if async) `CancellationToken`, every handler wraps its logic in `try/catch` against specific custom exception types and calls a **private `Problem(...)` helper duplicated in this same file** (do not extract a shared helper — this repo duplicates it per endpoint file), success responses via `Results.Ok(...)`.

### 0.4 Service convention (from `api/Services/LlamaApiClient.cs` and `api/Services/Exercises/*.cs`)

Constructor-injected dependencies (`HttpClient`, `IOptions<TOptions>`, `ILogger<T>`), public methods are `async Task<TResult>` returning a `sealed record` result type declared at the top of the same file, custom exceptions thrown for error paths (not error codes), no static/singleton mutable state beyond what's registered in DI.

### 0.5 Options convention (from `api/Program.cs`)

```csharp
builder.Services.Configure<LlamaApiOptions>(builder.Configuration.GetSection(LlamaApiOptions.SectionName));
```

or, for options needing validation:

```csharp
builder.Services.AddOptions<ExerciseExecutionOptions>()
    .BindConfiguration(ExerciseExecutionOptions.SectionName)
    .Validate(options => !string.IsNullOrWhiteSpace(options.RunnerImage), "Exercise runner image is required.")
    .ValidateOnStart();
```

Every `IOptions<T>` class exposes a `public const string SectionName = "...";`.

### 0.6 Frontend page convention (from `app/src/pages/LabProjects.jsx`)

Function components in `app/src/pages/*.jsx`, data fetched via `api.*` calls inside a `useCallback` + `useEffect`, three explicit render states (`loading` / `error` / empty), inline `style={{ ... }}` objects (no CSS modules, no styled-components, no Tailwind), colors/fonts always via CSS custom properties with hard-coded fallbacks exactly like this:

```jsx
color: 'var(--color-sage, #2C5E55)'
backgroundColor: 'var(--color-parchment-card, #FFFFFF)'
border: '1px solid var(--color-border-subtle, #E2DDD5)'
fontFamily: 'var(--font-serif, "Newsreader", serif)'
color: 'var(--color-ink, #1F2937)'
color: 'var(--color-ink-muted, #6B7280)'
```

Icons from `lucide-react` (already a dependency — see `import { Terminal } from 'lucide-react'`). Loading/error/empty states reuse `app/src/components/common/StateViews.jsx` (`LoadingState`, `ErrorState`, `EmptyState`) — do not build new ones.

### 0.7 Frontend API client convention (from `app/src/api/client.js`)

```js
exercises: {
  getMetadata: (exerciseId, options = {}) =>
    apiClient(`/api/exercises/${encodeURIComponent(exerciseId)}`, { ...options }),
},
```

Add one new namespaced object to the exported `api` object per feature area (e.g. `api.localization.*`, `api.marketplace.*`), each entry a thin arrow function calling the shared `apiClient(endpoint, options)` helper already defined earlier in the file. Always `encodeURIComponent` path params.

### 0.8 Routing convention (from `app/src/App.jsx`)

Every route is wrapped in the shared `<Layout>` component; nested/child pages get their own `<Route>` entries (this repo does NOT use nested `<Routes>` blocks or `<Outlet>` — every full path gets its own flat top-level `<Route>`). Follow this exactly for the new routes (§6).

---

## 1. What you are building — scope summary

A new "Localization Lab" feature living at `/lab-projects/localization`, reachable from the existing "Lab B — Unity Localization" card in `app/src/pages/LabProjects.jsx`. It has two completely separate frontends sharing one backend:

1. **Owner app** (internal, full nav) — 4 tabs: Strings, Workflow, Snapshots, Marketplace.
2. **Vendor portal** (separate, simpler shell, no owner nav) — Open Jobs board, bid submission, My Jobs workspace, at `/lab-projects/localization/vendor`.

Everything is scoped to one demo project, seeded at startup: **`auroraline-hud-v3`** ("Auroraline Automotive — HUD Strings"), source locale `en-US`, target locales `de-DE`, `ja-JP`, `zh-CN`, `fr-FR`, `es-ES`.

---

## 2. Data model — create these EF Core entities in `api/Models/`

All new files go in `api/Models/Localization/` (new subfolder, mirrors the existing `Services/Exercises/` and `Services/Auth/` subfolder pattern). Namespace: `StudyTracker.Api.Models.Localization`.

### 2.1 `LocalizationProject.cs`
```
[Table("localization_projects")]
- Id (int, PK)
- Slug (string, MaxLength 150, unique) e.g. "auroraline-hud-v3"
- Name (string, MaxLength 250) e.g. "Auroraline Automotive — HUD Strings"
- SourceLocale (string, MaxLength 20) e.g. "en-US"
- CreatedAt (DateTime, UTC)
```

### 2.2 `LocalizationLocale.cs`
```
[Table("localization_locales")]
- Id (int, PK)
- ProjectId (int, FK -> LocalizationProject, [JsonIgnore] nav property "Project")
- LocaleCode (string, MaxLength 20) e.g. "de-DE"
- DisplayName (string, MaxLength 100) e.g. "German (Germany)"
```

### 2.3 `LocalizationString.cs`
```
[Table("localization_strings")]
- Id (int, PK)
- ProjectId (int, FK)
- Key (string, MaxLength 200) e.g. "hud.nav.turnleft"
- SourceText (string) e.g. "Turn left ahead"
- CreatedAt (DateTime, UTC)
```

### 2.4 `LocalizationTranslation.cs`
```
[Table("localization_translations")]
- Id (int, PK)
- StringId (int, FK -> LocalizationString)
- LocaleCode (string, MaxLength 20) — denormalized for simple querying, matches LocalizationLocale.LocaleCode
- TargetText (string?, nullable)
- Stage (string, MaxLength 20) — one of: "New", "Translated", "Reviewed", "Approved" (store as string, not a C# enum column, to match this repo's existing pattern of plain string status columns — check LessonNote.cs / StudyTask.cs for precedent and mirror it)
- TranslationSource (string, MaxLength 20) — one of: "Manual", "AI", "Marketplace"
- QpsScore (int?, nullable) — Phase 3 only, 0-100
- NeedsReview (bool, default false) — Phase 3 Auto-Routing flag; when true, the UI shows the flagged state INSTEAD of the dot-track (see §7.3)
- UpdatedAt (DateTime, UTC)

Unique index on (StringId, LocaleCode) — one translation row per string per locale.
```

### 2.5 `WorkflowStep.cs`
```
[Table("localization_workflow_steps")]
- Id (int, PK)
- ProjectId (int, FK)
- Order (int)
- Trigger (string, MaxLength 50) — Phase 1 value is always "On Manual Click"
- Action (string, MaxLength 50) — one of: "Mark Translated", "Send to Review", "Approve" (Phase 1);
  "Auto-Translate via Google MT" (Phase 2); "Post to Marketplace" (Phase 2.5);
  "Run MT Optimize", "Score QPS", "Auto-Route" (Phase 3)
- ConditionExpression (string?, nullable, MaxLength 200) — Phase 3 only, e.g. "QPS < threshold"
- LastRunAt (DateTime?, nullable)
- LastRunOutcome (string?, nullable, MaxLength 200) — e.g. "12 strings affected"
```

### 2.6 `BuildSnapshot.cs`
```
[Table("localization_build_snapshots")]
- Id (int, PK)
- ProjectId (int, FK)
- SnapshotIdentifier (string, MaxLength 50) e.g. "snap-2026-09-01-a"
- SourceRevision (string, MaxLength 50) e.g. "r18234"
- LocalizationRevision (string, MaxLength 50) e.g. "l09981"
- Config (string, MaxLength 100) e.g. "Production-Default"
- CreatedAt (DateTime, UTC)
```

### 2.7 `BuildSnapshotLocaleCount.cs`
```
[Table("localization_build_snapshot_locale_counts")]
- Id (int, PK)
- BuildSnapshotId (int, FK -> BuildSnapshot)
- LocaleCode (string, MaxLength 20)
- ApprovedCount (int)
```

### 2.8 `Vendor.cs`
```
[Table("localization_vendors")]
- Id (int, PK)
- Name (string, MaxLength 150) e.g. "Maria Fischer"
- Languages (string, MaxLength 200) — comma-separated locale codes, e.g. "de-DE,fr-FR"
- Rating (decimal(3,1)) e.g. 4.9
```

### 2.9 `MarketplaceJob.cs`
```
[Table("localization_marketplace_jobs")]
- Id (int, PK)
- ProjectId (int, FK)
- LocaleCode (string, MaxLength 20)
- Status (string, MaxLength 20) — one of: "Draft", "Open", "Awarded", "InProgress", "SubmittedForReview", "Approved", "NeedsRevision", "Closed"
- StringCount (int)
- WordCount (int)
- SuggestedPriceLow (decimal(10,2))
- SuggestedPriceHigh (decimal(10,2))
- AwardedVendorId (int?, FK -> Vendor, nullable)
- PostedAt (DateTime?, nullable)
- AwardedAt (DateTime?, nullable)
- SubmittedAt (DateTime?, nullable)
- ApprovedAt (DateTime?, nullable)
```

### 2.10 `MarketplaceBid.cs`
```
[Table("localization_marketplace_bids")]
- Id (int, PK)
- MarketplaceJobId (int, FK)
- VendorId (int, FK)
- ProposedPrice (decimal(10,2))
- Note (string, MaxLength 500)
- Status (string, MaxLength 20) — one of: "Pending", "Awarded", "Declined", "Withdrawn"
- SubmittedAt (DateTime, UTC)
```

### 2.11 `LedgerEntry.cs`
```
[Table("localization_ledger_entries")]
- Id (int, PK)
- ProjectId (int, FK)
- Source (string, MaxLength 20) — "AI" or "Marketplace"
- Amount (decimal(10,2)) — credits
- RelatedMarketplaceJobId (int?, FK -> MarketplaceJob, nullable)
- CreatedAt (DateTime, UTC)
```

### 2.12 `ProviderHealthSnapshot.cs` (Phase 3)
```
[Table("localization_provider_health")]
- Id (int, PK)
- Provider (string, MaxLength 30) — "GoogleMT" or "LlmAzureGpt"
- P50LatencyMs (int)
- P99LatencyMs (int)
- ErrorRatePercent (decimal(5,2))
- CircuitState (string, MaxLength 20) — "Closed", "Open", "HalfOpen"
- UpdatedAt (DateTime, UTC)
```

**No separate "tenant" entity** — the tenant switcher in the nav (§7) simply lists `LocalizationProject` rows; a "demo tenant" IS a `LocalizationProject`. Do not build a parallel multi-tenancy model.

### 2.13 Update `api/Data/StudyTrackerContext.cs`

Add exactly these 12 lines (matching the exact style of the existing `DbSet<Lesson> Lessons` lines) in a clearly marked new section:

```csharp
// Localization Lab
public DbSet<LocalizationProject> LocalizationProjects { get; set; } = null!;
public DbSet<LocalizationLocale> LocalizationLocales { get; set; } = null!;
public DbSet<LocalizationString> LocalizationStrings { get; set; } = null!;
public DbSet<LocalizationTranslation> LocalizationTranslations { get; set; } = null!;
public DbSet<WorkflowStep> LocalizationWorkflowSteps { get; set; } = null!;
public DbSet<BuildSnapshot> LocalizationBuildSnapshots { get; set; } = null!;
public DbSet<BuildSnapshotLocaleCount> LocalizationBuildSnapshotLocaleCounts { get; set; } = null!;
public DbSet<Vendor> LocalizationVendors { get; set; } = null!;
public DbSet<MarketplaceJob> LocalizationMarketplaceJobs { get; set; } = null!;
public DbSet<MarketplaceBid> LocalizationMarketplaceBids { get; set; } = null!;
public DbSet<LedgerEntry> LocalizationLedgerEntries { get; set; } = null!;
public DbSet<ProviderHealthSnapshot> LocalizationProviderHealth { get; set; } = null!;
```

Add `using StudyTracker.Api.Models.Localization;` to the top of the file. **Do not modify any existing DbSet line.**

After adding these, generate an EF Core migration (`dotnet ef migrations add AddLocalizationLab --project api`) — do not hand-write migration SQL.

---

## 3. Backend services — create in `api/Services/Localization/` (new subfolder)

Namespace: `StudyTracker.Api.Services.Localization`. Each is a `public class`, registered as `AddScoped<T>()` in `Program.cs` (matching existing `ProgressService`/`AtlasQueryService` registration style).

### 3.1 `LocalizationProjectService.cs`
- `Task<LocalizationProjectDto> GetProjectAsync(string slug, CancellationToken ct)` — returns project + its locales.
- Throws `LocalizationProjectNotFoundException` if slug not found.

### 3.2 `LocalizationStringService.cs`
- `Task<IReadOnlyList<LocalizationStringRowDto>> GetStringsAsync(string projectSlug, string localeCode, CancellationToken ct)` — one row per string, joined with its translation for that locale (Stage defaults to "New" with null TargetText if no translation row exists yet).
- `Task<LocalizationStringRowDto> UpdateTranslationAsync(string projectSlug, int stringId, string localeCode, UpdateTranslationRequest request, CancellationToken ct)` — upserts the `LocalizationTranslation` row, sets `TranslationSource = "Manual"`, `Stage = "Translated"` if target text is non-empty, `UpdatedAt = DateTime.UtcNow`.

### 3.3 `WorkflowService.cs`
- `Task<IReadOnlyList<WorkflowStepDto>> GetStepsAsync(string projectSlug, CancellationToken ct)`
- `Task<WorkflowStepDto> AddStepAsync(string projectSlug, AddWorkflowStepRequest request, CancellationToken ct)` — appends at the end (`Order = max(Order) + 1`)
- `Task ReorderStepAsync(string projectSlug, int stepId, string direction, CancellationToken ct)` — `direction` is `"up"` or `"down"`; swaps `Order` with the adjacent step. Throws `InvalidOperationException` if already at the boundary.
- `Task DeleteStepAsync(string projectSlug, int stepId, CancellationToken ct)`
- `Task<WorkflowStepDto> RunStepAsync(string projectSlug, int stepId, CancellationToken ct)` — executes the step's `Action` against every string currently eligible (see §3.6 for what each action does), sets `LastRunAt`/`LastRunOutcome` on the step, returns the updated step. **Phase 3 actions ("Run MT Optimize", "Score QPS", "Auto-Route") must call into the hand-written AI boundary (§5) via its interfaces — never inline AI logic here.**

### 3.4 `SnapshotService.cs`
- `Task<IReadOnlyList<BuildSnapshotDto>> GetSnapshotsAsync(string projectSlug, CancellationToken ct)`
- `Task<BuildSnapshotDto> CutSnapshotAsync(string projectSlug, CancellationToken ct)` — always includes every locale on the project (no partial selection, per the locked design). Generates `SnapshotIdentifier` as `snap-{yyyy-MM-dd}-{next letter suffix for that date}` (e.g. first snapshot on a date is `-a`, second is `-b`). `SourceRevision`/`LocalizationRevision` are simple incrementing placeholders (e.g. `"r" + a running counter`, `"l" + a running counter}") — do not attempt real git integration. Computes `ApprovedCount` per locale by counting `LocalizationTranslation` rows with `Stage == "Approved"`.

### 3.5 `CreditLedgerService.cs`
- `Task<decimal> GetProjectBalanceAsync(string projectSlug, CancellationToken ct)` — sum of `LedgerEntry.Amount` for the project (informational; there is no "funding" flow in this build — treat all entries as spend, balance can go negative, this is fine for a demo).
- `Task<LedgerEntry> RecordEntryAsync(string projectSlug, string source, decimal amount, int? relatedMarketplaceJobId, CancellationToken ct)`
- `Task<(decimal Low, decimal High)> EstimatePriceBandAsync(int wordCount, CancellationToken ct)` — simple formula: `Low = wordCount * 0.145m` rounded to nearest 5, `High = wordCount * 0.19m` rounded to nearest 5 (placeholder rate — matches roughly the 180–240 band already used in the seeded example for ~1,240 words; do not invent a different formula, use exactly this one so seeded numbers stay consistent).

### 3.6 `GoogleTranslateProviderService.cs` (Phase 2 — buildable, NOT part of the hand-written boundary)

This one CAN be fully generated, because it's deterministic provider integration, not AI judgment. Implement `ITranslationProvider` (see §5.1) by calling the actual Google Cloud Translation REST API (`https://translation.googleapis.com/language/translate/v2`) using an API key read from `IOptions<GoogleTranslateOptions>` (new options class, `SectionName = "GoogleTranslate"`, one property `ApiKey`). If the API key is not configured, mirror `LlamaApiClient`'s exact pattern: in non-Production environments, return a clearly-labeled mock translation (e.g. prefix the source text with `"[MOCK-DE] "` for locale `de-DE`) rather than throwing; in Production, throw `InvalidOperationException`.

### 3.7 `MarketplaceService.cs` (owner-side)
- `Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetLocaleOverviewAsync(string projectSlug, CancellationToken ct)` — one row per `LocalizationLocale` on the project, joined to its most recent `MarketplaceJob` if one exists (status "Not Posted" if none).
- `Task<MarketplaceJobDto> PostToMarketplaceAsync(string projectSlug, string localeCode, CancellationToken ct)` — computes `StringCount`/`WordCount` from untranslated strings in that locale, calls `CreditLedgerService.EstimatePriceBandAsync`, creates the `MarketplaceJob` row with `Status = "Open"`, `PostedAt = now`.
- `Task<IReadOnlyList<MarketplaceBidDto>> GetBidsAsync(int marketplaceJobId, CancellationToken ct)`
- `Task<MarketplaceJobDto> AwardBidAsync(int marketplaceJobId, int bidId, CancellationToken ct)` — sets the chosen bid `Status = "Awarded"`, all sibling bids on the same job `Status = "Declined"`, job `Status = "Awarded"`, `AwardedVendorId` set, `AwardedAt = now`.
- `Task<MarketplaceJobDto> ApproveSubmissionAsync(int marketplaceJobId, CancellationToken ct)` — sets job `Status = "Approved"`, `ApprovedAt = now`, records a `LedgerEntry` with `Source = "Marketplace"`, `Amount` = the awarded bid's `ProposedPrice`, advances every `LocalizationTranslation` row in that project+locale to `Stage = "Approved"`.
- `Task<MarketplaceJobDto> SendBackForRevisionAsync(int marketplaceJobId, CancellationToken ct)` — sets job `Status = "NeedsRevision"`.

### 3.8 `VendorPortalService.cs` (vendor-side — note this has NO auth; vendor identity is selected via a plain query param / request field, not a login, per the locked "seeded roster, no signup" decision)
- `Task<IReadOnlyList<VendorDto>> GetVendorRosterAsync(CancellationToken ct)` — for the "Viewing as: ..." picker.
- `Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetOpenJobsForVendorAsync(int vendorId, CancellationToken ct)` — jobs with `Status == "Open"` whose `LocaleCode` is in the vendor's `Languages` list.
- `Task<MarketplaceBidDto> SubmitBidAsync(int marketplaceJobId, int vendorId, decimal proposedPrice, string note, CancellationToken ct)`
- `Task<IReadOnlyList<MarketplaceJobSummaryDto>> GetAwardedJobsForVendorAsync(int vendorId, CancellationToken ct)` — jobs where `AwardedVendorId == vendorId` and status is `Awarded` or `InProgress`.
- `Task<IReadOnlyList<LocalizationStringRowDto>> GetJobStringsAsync(int marketplaceJobId, CancellationToken ct)` — **locked-scope**: only strings for that job's `ProjectId` + `LocaleCode`. This is the enforcement point for "vendor sees only their awarded job" — never expose a generic strings-by-project endpoint to the vendor portal.
- `Task<MarketplaceJobDto> SubmitJobForReviewAsync(int marketplaceJobId, CancellationToken ct)` — sets job `Status = "SubmittedForReview"`, `SubmittedAt = now`. Validate every string in scope has non-null `TargetText` first; throw `InvalidOperationException` if not.

### 3.9 `ProviderHealthService.cs` (Phase 3)
- `Task<IReadOnlyList<ProviderHealthSnapshotDto>> GetHealthAsync(CancellationToken ct)` — reads the two seeded rows (GoogleMT, LlmAzureGpt).
- `Task<ProviderHealthSnapshotDto> SimulateOutageAsync(string provider, CancellationToken ct)` — flips that provider's `CircuitState` to `"Open"`, bumps `ErrorRatePercent` to e.g. 87.5.
- `Task<ProviderHealthSnapshotDto> ResolveOutageAsync(string provider, CancellationToken ct)` — flips back to `"Closed"`, resets `ErrorRatePercent` to a low seeded value (e.g. 0.4).

---

## 4. Backend endpoints — create in `api/Endpoints/Localization/` (new subfolder)

Follow §0.3 exactly. Register each `MapXEndpoints(app)` call in `Program.cs` next to the existing `app.MapExerciseEndpoints();`-style calls (find that line and add the new ones immediately after it).

### 4.1 `LocalizationEndpoints.cs` → `MapLocalizationEndpoints`
```
GET    /api/localization/projects/{slug}
GET    /api/localization/projects/{slug}/strings?locale={localeCode}
PUT    /api/localization/projects/{slug}/strings/{stringId}/translations/{localeCode}   body: { targetText }
GET    /api/localization/projects/{slug}/workflow
POST   /api/localization/projects/{slug}/workflow/steps        body: { trigger, action, conditionExpression? }
POST   /api/localization/projects/{slug}/workflow/steps/{stepId}/reorder   body: { direction: "up"|"down" }
POST   /api/localization/projects/{slug}/workflow/steps/{stepId}/run
DELETE /api/localization/projects/{slug}/workflow/steps/{stepId}
GET    /api/localization/projects/{slug}/snapshots
POST   /api/localization/projects/{slug}/snapshots
```

### 4.2 `MarketplaceEndpoints.cs` → `MapMarketplaceEndpoints` (owner-side)
```
GET    /api/localization/projects/{slug}/marketplace
POST   /api/localization/projects/{slug}/marketplace/{localeCode}/post
GET    /api/localization/marketplace/jobs/{jobId}/bids
POST   /api/localization/marketplace/jobs/{jobId}/bids/{bidId}/award
POST   /api/localization/marketplace/jobs/{jobId}/approve
POST   /api/localization/marketplace/jobs/{jobId}/send-back
```

### 4.3 `VendorPortalEndpoints.cs` → `MapVendorPortalEndpoints` (vendor-side — mount under a distinct `/api/localization/vendor` prefix so it is trivially auditable that these are the only endpoints the vendor frontend calls)
```
GET    /api/localization/vendor/roster
GET    /api/localization/vendor/{vendorId}/open-jobs
POST   /api/localization/vendor/{vendorId}/jobs/{jobId}/bids     body: { proposedPrice, note }
GET    /api/localization/vendor/{vendorId}/awarded-jobs
GET    /api/localization/vendor/jobs/{jobId}/strings
PUT    /api/localization/vendor/jobs/{jobId}/strings/{stringId}   body: { targetText }
POST   /api/localization/vendor/jobs/{jobId}/submit
```

### 4.4 `ProviderHealthEndpoints.cs` → `MapProviderHealthEndpoints`
```
GET    /api/localization/provider-health
POST   /api/localization/provider-health/{provider}/simulate-outage
POST   /api/localization/provider-health/{provider}/resolve
```

All handlers follow §0.3's try/catch + `Problem()` pattern. Define custom exceptions per service in a `LocalizationExceptions.cs` file inside `api/Services/Localization/` (e.g. `LocalizationProjectNotFoundException`, `MarketplaceJobNotFoundException`, `WorkflowStepBoundaryException`), mirroring the naming style of `ExerciseNotFoundException` etc.

---

## 5. The hand-written AI boundary — DO NOT GENERATE THIS LOGIC

This is a hard constraint, not a style preference. Per the project owner's decision, the actual AI reasoning must be written by hand for the owner to defend in a job interview. **You must create the interfaces and stub implementations below, wire them into DI, and leave the actual method bodies throwing `NotImplementedException` with a comment explaining why.** Do not write prompt text, response-parsing logic, or routing/threshold logic for these three pieces, even as a "reasonable placeholder" — a stub is correct; a guess is not.

### 5.1 `ITranslationProvider.cs` (interface only — Google MT implementation in §3.6 is fine, this interface itself is fine to generate)
```csharp
namespace StudyTracker.Api.Services.Localization;

public interface ITranslationProvider
{
    Task<string> TranslateAsync(string sourceText, string sourceLocale, string targetLocale, CancellationToken ct);
}
```

### 5.2 `IQualityScorer.cs` (interface — generate this)
```csharp
namespace StudyTracker.Api.Services.Localization;

public sealed record QualityScoreResult(int Score, IReadOnlyList<string> FlaggedIssues);

public interface IQualityScorer
{
    Task<QualityScoreResult> ScoreAsync(string sourceText, string targetText, string targetLocale, CancellationToken ct);
}
```

### 5.3 `MtOptimizeService.cs` — STUB ONLY, do not implement the body
```csharp
namespace StudyTracker.Api.Services.Localization;

/// <summary>
/// HAND-WRITTEN BOUNDARY: prompt construction for the glossary-aware post-edit
/// pass is written by the project owner, not generated. This method must throw
/// until the owner implements it by hand. Do not fill in prompt text, glossary
/// lookup logic, or LLM call plumbing here.
/// </summary>
public class MtOptimizeService
{
    public Task<string> OptimizeAsync(string rawTranslation, string projectSlug, string targetLocale, CancellationToken ct)
    {
        throw new NotImplementedException(
            "MT Optimize prompt construction is a hand-written component per the project's locked AI boundary. " +
            "Implement this method by hand — do not have an LLM generate this logic.");
    }
}
```

### 5.4 `QpsScoringService.cs` — STUB ONLY, implements `IQualityScorer` by throwing, same pattern as §5.3, with an equivalent comment referencing "the QPS/Auto-LQA scoring rubric is hand-written."

### 5.5 `AutoRoutingService.cs` — STUB ONLY
```csharp
public class AutoRoutingService
{
    /// <summary>
    /// HAND-WRITTEN BOUNDARY: comparing the QPS score against the project's
    /// threshold to decide Approved vs Needs Review is hand-written routing
    /// logic. Do not implement the comparison/decision here.
    /// </summary>
    public Task<bool> ShouldRouteToReviewAsync(int qpsScore, int projectThreshold, CancellationToken ct)
    {
        throw new NotImplementedException("Auto-Routing decision logic is hand-written per the project's locked AI boundary.");
    }
}
```

Register all four (`ITranslationProvider`→`GoogleTranslateProviderService`, `IQualityScorer`→`QpsScoringService`, `MtOptimizeService`, `AutoRoutingService`) in DI as `AddScoped`. The Phase 3 Workflow actions ("Run MT Optimize", "Score QPS", "Auto-Route") in `WorkflowService.RunStepAsync` (§3.3) should call these stubs and let the `NotImplementedException` surface as a clear 501-style API error (add one more case to each endpoint's `Problem()` handling: `catch (NotImplementedException ex) => Problem(httpContext, StatusCodes.Status501NotImplemented, "Not yet implemented.", ex.Message)`), so the owner sees exactly where their hand-written code needs to go when they click the corresponding button in the running app.

---

## 6. Frontend routing — add to `app/src/App.jsx`

Add these routes in the same flat, `<Layout>`-wrapped style as the existing routes (do not touch any existing `<Route>` block):

```
/lab-projects/localization                          → LocalizationStrings.jsx   (default tab: Strings)
/lab-projects/localization/workflow                  → LocalizationWorkflow.jsx
/lab-projects/localization/snapshots                 → LocalizationSnapshots.jsx
/lab-projects/localization/marketplace                → LocalizationMarketplace.jsx
/lab-projects/localization/marketplace/:jobId/bids     → LocalizationBidReview.jsx
/lab-projects/localization/vendor                      → VendorOpenJobs.jsx        (NOT wrapped in <Layout> — see §8)
/lab-projects/localization/vendor/jobs/:jobId          → VendorMyJob.jsx           (NOT wrapped in <Layout>)
```

Update the existing "Lab B — Unity Localization & Asset Delivery Platform" dev-fixture card in `app/src/pages/LabProjects.jsx` (lines ~24-31) so its lessons link out to `/lab-projects/localization` instead of being inert — this is the one existing file you touch, and only to fix that link, nothing else in that file changes.

---

## 7. Frontend — owner app pages, in `app/src/pages/Localization/` (new subfolder)

All four owner pages share one layout: the nav cluster (§7.1) + page header + 4-tab bar (§7.2), each rendering its own content below. Build a shared `LocalizationShell.jsx` component in `app/src/pages/Localization/` that takes `activeTab` and `children` props and renders the nav + header + tabs, used by all four pages, so the shell isn't duplicated four times.

### 7.1 Nav cluster (locked visual spec — implement exactly this, every owner page)

Left: existing site logo mark + "Neuralascent" wordmark (reuse whatever `Navbar.jsx` already renders for these — do not invent a new logo asset). Right, in this exact order with even spacing: (a) a small circular Provider Health status icon (colored dot: sage `#2C5E55` = healthy/Closed, amber `#A6772C` = degraded, red for any provider `Open`) that is a `<button>` opening the Provider Health slide-out panel (§7.5 pattern, reused); (b) a plain `<select>`-style dropdown listing all seeded projects (currently only one — "Auroraline Automotive" — but built as a real list, not hard-coded to one option) — switching does nothing functionally yet beyond changing the displayed project name, since this build has one seed project; (c) a live/fallback indicator: a small filled dot (sage = "Live") + text, non-interactive in this build (Phase 3's actual fallback wiring is out of scope — render it, don't wire a toggle handler that does anything); (d) existing user avatar component from `Navbar.jsx`.

### 7.2 Tab bar
Four plain-text tabs: `Strings | Workflow | Snapshots | Marketplace`. Active tab: `font-weight: 700`, `color: var(--color-ink, #1F2937)`, `border-bottom: 2px solid var(--color-sage, #2C5E55)` on a `<span>` sized to the text (not the full tab width — use `display: inline-block` with no extra padding, or an absolutely-positioned underline sized via `ref` — either is fine). Inactive tabs: `color: var(--color-ink-muted, #6B7280)`, no underline. **Never render any additional text/badge next to a tab label to indicate active state — color + underline only, nothing else.**

### 7.3 `LocalizationStrings.jsx` (Strings tab)

Ruled table (`border-collapse: collapse`, 1px `var(--color-border-subtle, #E2DDD5)` row dividers, no box-shadow, no alternating row background), columns: `#`, `KEY` (monospace font, e.g. `font-family: 'Courier New', monospace`), `SOURCE (EN)`, `TARGET (DE)` (locale-driven header, not hard-coded to DE), `STAGE`, action icon column (pencil icon opens the row drawer).

STAGE column: if `translation.NeedsReview` is `true`, render a single amber flag/exclamation icon (from `lucide-react`, e.g. `<Flag>` or `<AlertTriangle>`) + text label "Needs Review" **instead of** the dot-track. Otherwise render 4 small circles (8px, `border-radius: 50%`), filled `var(--color-sage, #2C5E55)` for stages up to and including the current one (New=0 filled, Translated=1, Reviewed=2, Approved=3, using array index comparison against `["New","Translated","Reviewed","Approved"].indexOf(stage)`), hollow (`border: 1.5px solid var(--color-ink-muted, #6B7280)`, white fill) for the rest, plus a small text label underneath naming only the current stage.

If Phase 3 is active for a row (`translation.QpsScore != null`), also render a `QPS` column between `TARGET` and `STAGE` showing the score, colored sage if `>= project threshold` (hard-code threshold display logic to `>= 70` for this build — there is no per-project threshold-editing UI in scope) else amber `#A6772C`. Rows with no QPS score show a plain em-dash.

Clicking a row opens a right-anchored drawer (dimmed overlay at 40% black opacity behind it, `position: fixed`, full height, 480px wide, white background, `box-shadow: -12px 0 24px rgba(0,0,0,0.12)` only on this one component): heading = the string's `Key` in monospace, repeats the Stage indicator, then a read-only "SOURCE" box (light `var(--color-parchment-card, #F8F6F0)`-tinted background, lock icon top-right) and an editable "TARGET" textarea (`border: 2px solid var(--color-sage, #2C5E55)` when focused), a thin sage divider between them, and two icon-only buttons at the bottom-right: a filled sage circle with a checkmark (`onClick` saves via `PUT .../translations/{localeCode}` then advances to the next untranslated row in the table) and an outlined arrow-right icon (skip without saving). Show one tooltip on the checkmark button reading "Save & Next" — do not add a second, redundant text-labeled button beneath it; this must be a single button.

### 7.4 `LocalizationWorkflow.jsx` (Workflow tab)

Numbered list (not a table with column borders — each "step" is a bordered block), one row per `WorkflowStep`, columns/fields: step number (large serif numeral), a `TRIGGER` labeled `<select>` (Phase 1: only option is "On Manual Click"), an `ACTION` labeled `<select>` populated from the full action list in §2.5 (all phases' actions available, since this is a config screen — the actual execution of Phase 2/2.5/3 actions depends on those services existing, which they do per this same prompt), up/down icon-only reorder buttons (call the `/reorder` endpoint), a delete icon, and beneath the two selects a small muted-grey line showing `LastRunOutcome` if `LastRunAt` is set, else italic "Never run yet". An icon-only "+ Add Step" control at the bottom appends a new step with `Trigger = "On Manual Click"`, `Action = "Mark Translated"` as sane defaults, immediately editable via its own dropdowns after creation.

Add a "▶ Run" icon button per step (not previously called out in the design doc but necessary for a working demo) that calls `POST .../steps/{stepId}/run` and refreshes that row's last-run line — without this, `LastRunOutcome` never updates and the italic "Never run yet" state can never be exercised in the running app.

### 7.5 `LocalizationSnapshots.jsx` (Snapshots tab)

Table, columns: `SNAPSHOT ID` (monospace), `CREATED`, `SOURCE REVISION` (monospace), `LOCALES`, `APPROVED STRINGS`. One icon-only button top-right, a solid sage circle with a camera/checkmark-seal icon (use `lucide-react`'s `<Camera>` or `<BadgeCheck>`), tooltip "Cut Build Snapshot", calling `POST .../snapshots` with no body (always all locales). Clicking a row opens the same drawer pattern as §7.3 (dimmed overlay, right-anchored, monospace heading = `SnapshotIdentifier`), showing the read-only manifest fields and a small `LOCALE | APPROVED` table-within-the-drawer from `BuildSnapshotLocaleCount`. No editable fields, no bottom buttons — purely read-only, terminal.

### 7.6 `LocalizationMarketplace.jsx` (Marketplace tab)

Table, columns: `LOCALE`, `STRINGS REMAINING`, `STATUS` (plain colored text, never a pill/badge — sage bold for "Open"/"Approved" states, muted grey for "Not Posted", plain ink for the rest), `SUGGESTED BAND`, action icon column. Action per row depends on status: "Not Posted" → sage megaphone icon, `onClick` opens a confirm drawer (same overlay pattern, read-only summary of string/word count + suggested band, one icon-only "Post to Marketplace" button) then calls `POST .../marketplace/{localeCode}/post`; "Open" → people/group icon linking to `/lab-projects/localization/marketplace/{jobId}/bids`; "Submitted for Review" → magnifying-glass icon linking back to the Strings tab pre-filtered to that locale (pass `?locale=xx-XX` as a query param the Strings page reads to filter its table, plus render an "Approve Submission" / "Send Back for Revision" icon pair at the top of the filtered Strings view when arriving via this link); "Awarded"/"Approved" → no action icon.

### 7.7 `LocalizationBidReview.jsx` (drill-in from Marketplace, no tab bar of its own — it's not a top-level route tab)

Heading "Bids for {localeCode}" + subtitle with project/string-count/band. Table: `VENDOR` (name + `★{rating}` as one text string, never five separate star icons), `LANGUAGES`, `PROPOSED PRICE` (colored sage if below the low end of the band, amber `#A6772C` if above the high end, plain ink if within — compute this client-side from the job's `SuggestedPriceLow`/`High`), `NOTE`, action column with one icon-only button per row (solid sage filled circle, white checkmark) calling `POST .../bids/{bidId}/award`.

### 7.8 Provider Health slide-out panel (shared component, `app/src/components/Localization/ProviderHealthPanel.jsx`)

Opened from the nav icon (§7.1a) on any owner page. Same drawer overlay pattern. One block per provider: name, `P50 / P99` latency, error rate, circuit state, and one icon-only "Simulate Outage" / "Resolve" toggle button (label via tooltip) calling the corresponding endpoint from §4.4.

---

## 8. Frontend — vendor portal pages, in `app/src/pages/Localization/Vendor/` (new subfolder)

**These pages are NOT wrapped in the site's normal `<Layout>` component** (no main site nav, no sidebar) — build a separate minimal `VendorPortalShell.jsx` wrapper used only by these three vendor routes, containing just: left, the same logo mark + wordmark + a `VENDOR PORTAL` tag (thin-bordered rectangle, sharp corners, small uppercase text) next to it; right, a plain `<select>` populated from `GET /api/localization/vendor/roster`, labeled "Viewing as: {name} ({languages})", stored in a small piece of local state (`useState`, no auth, no persistence needed) that every vendor page reads to know "who" is browsing. **Never render the Provider Health icon, tenant switcher, or live/fallback indicator anywhere in the vendor portal** — this is a deliberate, load-bearing part of the locked-scope design, not an oversight to "fix" later.

### 8.1 `VendorOpenJobs.jsx`
Heading "Open Jobs" + subtitle listing the selected vendor's declared languages. A responsive grid of cards (this is the one screen in the whole product using cards instead of ruled-table rows — sharp corners, 1px border, no shadow), one per open job matching the vendor's languages: project+locale name, string/word count, suggested band (bold sage), "Open N days" (compute from `PostedAt` to now, floor days), and a rectangular sage-bordered **text-label** button "Submit a Bid" (this is the one place text-label buttons are correct, per the vendor portal's distinct convention) opening the bid modal (§8.2).

### 8.2 Bid submission modal (component, not a route — a centered modal, dimmed overlay all around, not right-anchored)
Read-only job summary, a `YOUR PRICE (CREDITS)` number input pre-filled with the band midpoint (`(low + high) / 2`, rounded), a `NOTE TO PROJECT OWNER` textarea, and a solid sage rectangular text-label "Submit Bid" button calling `POST .../jobs/{jobId}/bids`.

### 8.3 `VendorMyJob.jsx`
Heading "My Jobs — {project} ({locale})" + "Awarded job · N strings · Deadline not set". Table, columns `#`, `KEY` (monospace), `SOURCE (EN)`, `TARGET (DE)` (editable inline via pencil icon → opens a simple inline edit, not the full drawer — a lighter-weight interaction is fine here since there's no Stage/QPS complexity to show), **no STAGE column**. Bottom-right: a solid sage rectangular text-label "Submit for Review" button, disabled (lighter sage, `pointer-events: none` styling) while any row's `TARGET (DE)` is empty, calling `POST .../jobs/{jobId}/submit` once enabled.

---

## 9. Frontend API client — add to `app/src/api/client.js`

Add two new namespaces to the exported `api` object, following §0.7's exact pattern:

```js
localization: {
  getProject: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}`),
  getStrings: (slug, locale) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/strings?locale=${encodeURIComponent(locale)}`),
  updateTranslation: (slug, stringId, locale, targetText) =>
    apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/strings/${stringId}/translations/${encodeURIComponent(locale)}`, { method: 'PUT', body: { targetText } }),
  getWorkflow: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow`),
  addWorkflowStep: (slug, body) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps`, { method: 'POST', body }),
  reorderWorkflowStep: (slug, stepId, direction) =>
    apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}/reorder`, { method: 'POST', body: { direction } }),
  runWorkflowStep: (slug, stepId) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}/run`, { method: 'POST' }),
  deleteWorkflowStep: (slug, stepId) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/workflow/steps/${stepId}`, { method: 'DELETE' }),
  getSnapshots: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/snapshots`),
  cutSnapshot: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/snapshots`, { method: 'POST' }),
  getMarketplaceOverview: (slug) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/marketplace`),
  postToMarketplace: (slug, locale) => apiClient(`/api/localization/projects/${encodeURIComponent(slug)}/marketplace/${encodeURIComponent(locale)}/post`, { method: 'POST' }),
  getBids: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/bids`),
  awardBid: (jobId, bidId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/bids/${bidId}/award`, { method: 'POST' }),
  approveSubmission: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/approve`, { method: 'POST' }),
  sendBackForRevision: (jobId) => apiClient(`/api/localization/marketplace/jobs/${jobId}/send-back`, { method: 'POST' }),
  getProviderHealth: () => apiClient('/api/localization/provider-health'),
  simulateOutage: (provider) => apiClient(`/api/localization/provider-health/${provider}/simulate-outage`, { method: 'POST' }),
  resolveOutage: (provider) => apiClient(`/api/localization/provider-health/${provider}/resolve`, { method: 'POST' }),
},

vendorPortal: {
  getRoster: () => apiClient('/api/localization/vendor/roster'),
  getOpenJobs: (vendorId) => apiClient(`/api/localization/vendor/${vendorId}/open-jobs`),
  submitBid: (vendorId, jobId, proposedPrice, note) =>
    apiClient(`/api/localization/vendor/${vendorId}/jobs/${jobId}/bids`, { method: 'POST', body: { proposedPrice, note } }),
  getAwardedJobs: (vendorId) => apiClient(`/api/localization/vendor/${vendorId}/awarded-jobs`),
  getJobStrings: (jobId) => apiClient(`/api/localization/vendor/jobs/${jobId}/strings`),
  updateJobString: (jobId, stringId, targetText) =>
    apiClient(`/api/localization/vendor/jobs/${jobId}/strings/${stringId}`, { method: 'PUT', body: { targetText } }),
  submitJob: (jobId) => apiClient(`/api/localization/vendor/jobs/${jobId}/submit`, { method: 'POST' }),
},
```

---

## 10. Seed data — add a `LocalizationSeedData.cs` in `api/Data/` (mirrors existing `*SeedData.cs` files in that folder — check for one, e.g. any existing seed data class, and match its exact invocation style/hook point in `Program.cs`'s startup sequence)

Seed exactly this data on first run (guard with an `if (!context.LocalizationProjects.Any())` check, same idempotency pattern any existing seeder in this repo uses):

- **1 project**: `auroraline-hud-v3` / "Auroraline Automotive — HUD Strings" / source `en-US`
- **5 locales**: `de-DE` (German), `ja-JP` (Japanese), `zh-CN` (Chinese Simplified), `fr-FR` (French), `es-ES` (Spanish)
- **6 strings** with `de-DE` translations seeded at varying stages, exactly matching the approved reference image data:
  - `hud.speed.label` / "Current Speed" / "Aktuelle Geschwindigkeit" / Approved
  - `hud.warning.lowfuel` / "Low fuel warning" / "Kraftstoff niedrig" / Reviewed
  - `hud.nav.turnleft` / "Turn left ahead" / "Links abbiegen" / Translated
  - `hud.climate.temp` / "Cabin temperature" / (no translation row) / New
  - `hud.alert.doorajar` / "Door ajar" / "Tür offen" / Approved
  - `hud.gear.reverse` / "Reverse gear engaged" / "Rückwärtsgang eingelegt" / Reviewed
- **3 workflow steps**: (1) On Manual Click → Mark Translated, last ran 2h ago, "12 strings affected"; (2) On Manual Click → Send to Review, last ran 1d ago, "8 strings affected"; (3) On Manual Click → Approve, never run.
- **3 build snapshots**: `snap-2026-09-01-a` (r18234/l09981, Production-Default, 5 locales, 612 approved), `snap-2026-08-22-c` (r17910, 5 locales, 588 approved), `snap-2026-08-10-b` (r17402, 4 locales, 471 approved) — with matching `BuildSnapshotLocaleCount` rows for the most recent one: de-DE 128, ja-JP 94, zh-CN 156, fr-FR 140, es-ES 94.
- **5 vendors**: Maria Fischer (de-DE, fr-FR, 4.9), Kenji Sato (ja-JP, ko-KR, 5.0), Aiko Tanaka (ja-JP, 4.7), Marcus Webb (ja-JP, zh-CN, ko-KR, 4.2), plus one more of your choosing for variety.
- **Marketplace state**: de-DE → Awarded to Maria Fischer; ja-JP → Open with 3 bids (Kenji 345, Aiko 298, Marcus 420 — matching the note text already used in the approved reference images); zh-CN → Not Posted; fr-FR → Submitted for Review; es-ES → Approved.
- **2 provider health rows**: GoogleMT (P50 210ms, P99 640ms, 0.4% errors, Closed), LlmAzureGpt (P50 480ms, P99 1450ms, 1.1% errors, Closed).

---

## 11. Explicitly out of scope — do not build any of this

- Continuous/CDN runtime-sync delivery mode (Build-Locked only, per the locked architecture)
- A visual node-canvas Orchestrator builder (config-driven list only)
- Real vendor authentication/signup (seeded roster + a plain picker only)
- Real multi-tenant DB partitioning (one seeded project is enough)
- Real SSO/SCIM, pseudo-localization tooling, in-context live-preview overlay, real fuzzy-match TM engine
- Per-project configurable QPS threshold UI (hard-coded `>= 70` display logic is enough for this build)
- Bid withdrawal by vendors, vendor rating changes over time
- Any actual prompt text, response-parsing, or routing logic for MT Optimize / QPS scoring / Auto-Routing (§5 — stub only)

---

## 12. Acceptance checklist — the build is done when

1. `dotnet ef database update` applies cleanly with no manual SQL edits.
2. Visiting `/lab-projects/localization` shows the seeded Strings table with the nav cluster, 4 tabs, and a working row-detail drawer that saves edits via the API.
3. The Workflow tab can add/reorder/delete/run steps against the real API.
4. The Snapshots tab can cut a new snapshot and view any snapshot's manifest in a drawer.
5. The Marketplace tab shows all 5 seeded locale states correctly and can post `zh-CN` to the marketplace, producing a real `MarketplaceJob` row.
6. The Bid Review screen can award a bid.
7. `/lab-projects/localization/vendor` shows the seeded vendor picker and correctly filters Open Jobs by the selected vendor's languages.
8. A vendor can submit a bid, and it shows up on the owner's Bid Review screen for that job.
9. The Provider Health panel opens from the nav icon and Simulate Outage/Resolve actually flips the stored state.
10. Clicking any Phase 3 workflow action ("Run MT Optimize", "Score QPS", "Auto-Route") returns a clear 501 error naming the hand-written boundary, rather than crashing or silently no-op'ing.
