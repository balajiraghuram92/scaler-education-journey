# R1 — Localization Lab rebuild: usage metering (.NET backend)

First step of track R (see `R0-index.md`). It adds a record of every paid provider call and an operations-only view of it. It is additive: no existing behaviour, endpoint or screen is removed.

Design reference: `info/localization-design/specs/localization-lab-tier-usage-model-DRAFT.md`, sections 3.2, 3.3 and 3.5. Where this prompt and the draft differ, this prompt wins (the draft is not final).

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository (ASP.NET Core 8 minimal API in `api/`, xUnit tests in `tests/StudyTracker.Api.Tests/`). The repo's `CLAUDE.md` is addressed to a different assistant; for this task you may edit files under `api/` and `tests/`.

Work only in `api/` and `tests/StudyTracker.Api.Tests/`. Do not touch `app/`, `api-python/`, `localization-ai/`, compose files, `.env*`, deploy scripts or workflows. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `info/muse-prompts/localization-rebuild/PROGRESS.md` (create it) under "R1" before starting the next.

## Background

The Localization Lab calls two paid kinds of provider: a machine-translation API and a language model (through the `localization-ai` service). Today the only record is one `LedgerEntry` per workflow run, and it is incomplete:

- `WorkflowService.RunStepAsync`, `AutoTranslateViaGoogleMt` branch (`api/Services/Localization/WorkflowService.cs:339-404`): one ledger row per run, counting the characters of the **translated** text. Translation APIs bill the **source** characters, once per target locale.
- `RunMtOptimize` branch (`:430-496`): one ledger row per run with summed tokens.
- `ScoreQps` branch (`:497-551`): **no record at all**, although every call uses tokens.
- A QPS call where the judge falls back (`QpsScoringService.ScoreAsync`, `api/Services/Localization/QpsScoringService.cs:36-39`) throws `LocalizationAiException`, so its tokens are lost. The reviewer observed such a response from the service: `{"score":null,"inputTokens":531,"outputTokens":2,"tokensUsed":533,"fallback":true}`.
- The cost is always 0 because no price is configured.

The target: one immutable row per provider call, with the units that provider bills, and an operations-only summary. Clients are never shown usage or cost.

## Read these first, in full

- `api/Services/Localization/WorkflowService.cs`
- `api/Services/Localization/LocalizationAiClient.cs`, `QpsScoringService.cs`, `IQualityScorer.cs`, `MtOptimizeService.cs`, `ITranslationProvider.cs`, `LocalizationExceptions.cs`
- `api/Models/Localization/LedgerEntry.cs` (style reference for an entity) and the `LedgerEntry` block in `api/Data/StudyTrackerContext.cs:747-767` (style reference for mapping)
- `api/Endpoints/Localization/ProviderHealthEndpoints.cs` (style reference for an endpoint file) and `api/Endpoints/AdminEndpoints.cs` (`LoadApprovedAdminAsync`, lines 46-64, and how it answers 403)
- `api/Migrations/20261111140209_AddLocalizationAiLayer.cs`, its `.Designer.cs`, and `api/Migrations/StudyTrackerContextModelSnapshot.cs` (you will hand-write a migration in the same style)
- `tests/StudyTracker.Api.Tests/Localization/LocalizationTestFixture.cs` and `LocalizationAiWorkflowTests.cs`

## Task 1 — entities and mapping

Two new entities in `api/Models/Localization/`, written like `LedgerEntry.cs` (attributes for table and column names, snake_case columns).

`LocalizationUsageEvent`, table `localization_usage_events`:

| Property | Column | Type | Notes |
|---|---|---|---|
| `Id` | `id` | int, identity | key |
| `ProjectId` | `project_id` | int | FK to `LocalizationProject`, cascade delete |
| `WorkflowStepId` | `workflow_step_id` | int? | FK to `WorkflowStep`, set null on delete |
| `Meter` | `meter` | varchar(30), required | one of the constants below |
| `Operation` | `operation` | varchar(30), required | one of the constants below |
| `LocaleCode` | `locale_code` | varchar(20)? | target locale of the call |
| `Units` | `units` | int | source characters, or input tokens |
| `UnitsOut` | `units_out` | int? | output tokens; null for characters |
| `CacheHit` | `cache_hit` | bool | true when no model call was made |
| `Succeeded` | `succeeded` | bool | false when the call used units but produced no usable result |
| `CostUsd` | `cost_usd` | numeric(12,6) | computed when the row is written |
| `OccurredAt` | `occurred_at` | timestamptz | UTC |

`LocalizationProviderRate`, table `localization_provider_rates`:

| Property | Column | Type |
|---|---|---|
| `Id` | `id` | int, identity |
| `Meter` | `meter` | varchar(30), required |
| `UnitKind` | `unit_kind` | varchar(20), required |
| `UsdPerMillion` | `usd_per_million` | numeric(12,6) |
| `ValidFrom` | `valid_from` | timestamptz |

Constants, in a static class beside the entities (`UsageMeters`, `UsageOperations`, `UsageUnitKinds`):

```
Meter:      "machine-translation" | "llm-optimize" | "llm-score"
Operation:  "mt-draft" | "mt-optimize" | "qps-score"
UnitKind:   "char" | "input-token" | "output-token"
```

The meter names describe the kind of provider, not a vendor, because the machine-translation provider will change in a later step.

`StudyTrackerContext`: add the two `DbSet`s next to the other Localization sets (lines 54-70) and two `modelBuilder.Entity<…>` blocks after the `LedgerEntry` block. Indexes: `ix_localization_usage_events_project_occurred` on `(ProjectId, OccurredAt)`, `ix_localization_usage_events_meter_occurred` on `(Meter, OccurredAt)`, and a unique index `ux_localization_provider_rates_meter_kind_from` on `(Meter, UnitKind, ValidFrom)`. No database defaults: values are set in C#, as everywhere else in this model.

Do not add a navigation collection to `LocalizationProject`; query the events through the `DbSet`.

## Task 2 — migration

Hand-write `api/Migrations/20261112120000_AddLocalizationUsageMetering.cs`, its `.Designer.cs`, and update `StudyTrackerContextModelSnapshot.cs`, in the same style as `20261111140209_AddLocalizationAiLayer`. `Up` creates the two tables, the foreign keys and the three indexes; `Down` drops them. The snapshot and the designer must describe exactly the model from Task 1; the reviewer will compare them by running EF against a real database.

Seed no rate rows. Prices are entered by the operator (Task 5).

## Task 3 — `UsageMeteringService`

New file `api/Services/Localization/UsageMeteringService.cs`, registered as scoped in `api/Program.cs` next to the other Localization services (lines 137-153).

```csharp
public sealed record UsageCallRecord(
    int ProjectId, int? WorkflowStepId, string Meter, string Operation, string? LocaleCode,
    int Units, int? UnitsOut, bool CacheHit, bool Succeeded);
```

- `Task RecordAsync(UsageCallRecord call, DateTime occurredAtUtc, CancellationToken ct)`: computes `CostUsd` and **adds** the event to the context. It does not call `SaveChangesAsync`; the caller's existing save at the end of `RunStepAsync` (line 600) writes the events together with the run's other changes.
- Cost: for a character meter, `Units x rate("char") / 1,000,000`. For a token meter, `Units x rate("input-token") / 1,000,000 + UnitsOut x rate("output-token") / 1,000,000`. The rate for a meter and unit kind is the row with the latest `ValidFrom` that is not after `occurredAtUtc`. No matching rate means that part of the cost is 0. A cache hit costs 0. Round to 6 decimals.
- Load the rates once per service instance (one query, kept in a field), not once per call: a run records hundreds of events.
- `Task<UsageSummaryDto> GetSummaryAsync(string? projectSlug, int year, int month, CancellationToken ct)`: for the calendar month in UTC, totals per meter (`calls`, `failedCalls`, `cacheHits`, `units`, `unitsOut`, `costUsd`), the same per meter and operation, per meter and locale, and per day (`date`, `meter`, `units`, `unitsOut`, `costUsd`). Also `ratesMissing`: every meter and unit kind that had usage in the month but no rate, so a 0 cost is not read as free. An unknown project slug throws `LocalizationProjectNotFoundException`. A null slug means all projects.
- `Task<IReadOnlyList<UsageEventDto>> GetRecentEventsAsync(string? projectSlug, int limit, CancellationToken ct)`: newest first; `limit` clamped to 1-500, default 100.

Put the DTOs in `api/Services/Localization/LocalizationDtos.cs` with the existing ones. Decimals stay `decimal`.

The aggregation queries must translate to SQL on PostgreSQL. Group by scalar columns and project to anonymous types before ordering; do not order by a property of a record created through its constructor (that exact mistake produced a 500 in `AdminEndpoints.GetUsageByUserAsync` and was fixed on 12 Nov).

## Task 4 — record one event per provider call

`WorkflowService` gets `UsageMeteringService` as a constructor parameter. Add it as the **last** parameter and make it optional (`UsageMeteringService? usage = null`), so the existing tests that construct `WorkflowService` directly keep compiling; when it is null, nothing is recorded.

Keep the two existing `LedgerEntry` writes exactly as they are. Removing them is a later step.

**4a. Machine translation** (`AutoTranslateViaGoogleMt`, lines 339-404). After each of the two `TranslateAsync` calls (lines 350 and 372), record:

```
Meter "machine-translation", Operation "mt-draft", LocaleCode locale.LocaleCode,
Units = str.SourceText.Length, UnitsOut = null, CacheHit = false, Succeeded = true
```

Units are the **source** characters. Do not change the existing `characterCount` ledger arithmetic.

**4b. MT Optimize** (`RunMtOptimize`, lines 430-496). After a successful `OptimizeDetailedAsync` (line 457), record:

```
Meter "llm-optimize", Operation "mt-optimize", LocaleCode trans.LocaleCode,
Units = result.InputTokens, UnitsOut = result.OutputTokens, CacheHit = result.CacheHit, Succeeded = true
```

In the `catch (LocalizationAiException)` (the call failed outright), record nothing: no tokens are known.

**4c. QPS** (`ScoreQps`, lines 497-551). Token counts do not reach this code today. Fix that in three places:

1. `LocalizationAiClient.cs`, `AiQpsScoreResult` (lines 40-45): add `int InputTokens` and `int OutputTokens`. The service already returns `inputTokens` and `outputTokens`; deserialisation is case-insensitive.
2. `IQualityScorer.cs`, `QualityScoreResult`: add `int InputTokens = 0, int OutputTokens = 0` as trailing optional parameters, so other implementations and tests keep compiling.
3. `LocalizationAiClient.cs`, `LocalizationAiException` (lines 15-26): add two settable `int` properties, `InputTokens` and `OutputTokens`, default 0. `QpsScoringService.ScoreAsync` fills them when it throws because the judge fell back (line 36-39), and returns the counts in `QualityScoreResult` on success.

Then in the workflow, for **both** `ScoreAsync` calls (lines 513 and 533):

```
on success:  Meter "llm-score", Operation "qps-score", Units = result.InputTokens,
             UnitsOut = result.OutputTokens, CacheHit = false, Succeeded = true
in the catch: if ex.InputTokens + ex.OutputTokens > 0, the same with Succeeded = false
```

The two catches currently read `catch (LocalizationAiException)`; they need the variable.

**4d. Auto-Route** makes no model call. Record nothing.

Every event carries `ProjectId = project.Id`, `WorkflowStepId = step.Id` and the run's `now`.

## Task 5 — operations endpoints

New file `api/Endpoints/Localization/UsageEndpoints.cs`, mapped from wherever `MapProviderHealthEndpoints` is called, group `/api/localization/ops`:

| Method | Path | Returns |
|---|---|---|
| GET | `/usage?project={slug}&month={yyyy-MM}` | `UsageSummaryDto`. `month` defaults to the current UTC month; a malformed value is 400 |
| GET | `/usage/events?project={slug}&limit={n}` | list of `UsageEventDto` |
| GET | `/rates` | all rates, newest `ValidFrom` first |
| POST | `/rates` | body `{ meter, unitKind, usdPerMillion, validFrom? }`; adds a rate; `validFrom` defaults to now; unknown meter or unit kind, or a negative price, is 400; a duplicate `(meter, unitKind, validFrom)` is 409 |

All four are for the operations role only. Use the same check as the admin endpoints: the signed-in user must exist with `Role == "Admin"` and `Status == "Approved"`, otherwise 403 with the same problem body `AdminEndpoints` returns ("Forbidden", "Administrative privileges required."). Do not copy `LoadApprovedAdminAsync`: move it to a small shared static helper that both files call, and change nothing else in `AdminEndpoints.cs`.

An unknown project is 404 in the problem shape the other Localization endpoints use.

## Task 6 — tests

In `tests/StudyTracker.Api.Tests/Localization/`, following `LocalizationAiWorkflowTests.cs` and the fixture:

1. Machine translation run: one event per string and locale translated; `Units` equals the source text length; none for strings that already had a translation.
2. MT Optimize run: one event per optimised translation with the fake result's token counts; a cache hit is recorded with `CacheHit = true` and cost 0 even when a rate exists.
3. QPS run with a scorer that succeeds: events with tokens and `Succeeded = true`, including the second call that scores the raw MT.
4. QPS run where the scorer throws `LocalizationAiException` carrying tokens: one event with `Succeeded = false`; an exception with zero tokens records nothing.
5. Cost: with two rates for the same meter and unit kind, the one in force at the event time is used; with no rate the cost is 0 and the summary lists the pair in `ratesMissing`.
6. Summary: events in two months and two projects; totals for one month and one project are exact; the all-projects total is the sum.
7. `WorkflowService` constructed without a metering service still runs every action.
8. Endpoints: if the test project already has a way to call endpoints with and without an admin user (look at `AuthAndUserManagementTests.cs`), add a 403 and a 200 case for `GET /api/localization/ops/usage`. If it does not, say so in the report and do not invent one.

Existing tests must not be edited except where a constructor or record signature you changed forces it; list every such edit.

## Not in this prompt

- The React operations page (R2).
- Budgets, alerts and the kill switch (R3).
- Removing the `LedgerEntry` "AI" writes, credits or the marketplace.
- `api-python/`: the port will be brought in line in its own step once the .NET side has stopped changing. Its route list will be out of date until then; that is expected.

## Finish

End with a short report: each task done or not done, every file created or changed, the existing tests you had to edit and why, the answer to Task 6 item 8, and anything that could not be done as written. Never say a build or test passes; you have not run it.
