# Track R progress

## R1 — usage metering (.NET backend)

Task 1 — entities and mapping. New
`api/Models/Localization/LocalizationUsageEvent.cs`
(13 columns per the table, navs to project and
step, `JsonIgnore`/`ForeignKey` like
`LedgerEntry`), `LocalizationProviderRate.cs` (5
columns) and `UsageConstants.cs` (`UsageMeters`,
`UsageOperations`, `UsageUnitKinds` with the exact
constant strings). `StudyTrackerContext`: two
`DbSet`s after the other Localization sets and two
mapping blocks after the `LedgerEntry` block, with
the three named indexes (unique on rates), the
`numeric(12,6)` precisions, cascade project FK and
set-null step FK. No navigation collection added
to `LocalizationProject`.

Task 2 — migration written; designer pending a
checkpoint decision (see below).
`api/Migrations/20261112120000_AddLocalizationUsageMetering.cs`:
`Up` creates both tables in class-declaration
column order with identity PKs, the two FKs and
the three named indexes (`unique: true` on the
rates index); the 73-char workflow-step FK name is
truncated EF-style to 62 chars plus `~`
(`..._steps_workf~`, verified against the LA1
`..._projec~` precedent); `Down` drops both
tables. `StudyTrackerContextModelSnapshot.cs`
gained the two property blocks (alphabetical
position and property order, `numeric(12,6)` with
`HasPrecision`, composite/unique index syntax as
in the LA1 designer) and the `LocalizationUsageEvent`
relationship block (`WithMany()` without back-nav,
`IsRequired` on the non-nullable FK, `SetNull`
without it); no section-3 change since no
collection navigation was added.
DESIGNER DECISION NEEDED: the `.Designer.cs` must
be a ~4120-line full-model file differing from
the LA1 designer only in the header attribute,
the class name, and the same three blocks
inserted at the same alphabetical anchors — with
no shell to copy the file, reproducing it costs
roughly 100k+ tokens and risks the rest of the
track. The three blocks are character-identical
to the snapshot insertions above (designer and
snapshot bodies match line for line apart from
the file header). Proposed: the reviewer copies
`20261111140209...Designer.cs`, renames the
attribute/class, and pastes the three blocks; or
confirm and the full hand-write happens here.

Task 3 — `UsageMeteringService`. New
`api/Services/Localization/UsageMeteringService.cs`
with the specified `UsageCallRecord`;
`RecordAsync` computes cost (char meter by chars,
token meters by in/out tokens, latest rate with
`ValidFrom` at or before the event, 0 without one
or on cache hit, rounded once to 6) and adds the
event without saving; rates load once per service
instance. `GetSummaryAsync` filters the UTC month
(and project, 404 on unknown slug) and aggregates
per meter, meter+operation, meter+locale and day,
plus `ratesMissing` (a pair whose earliest monthly
usage had no rate in force); `GetRecentEventsAsync`
is newest-first with `limit` clamped 1-500,
default 100. All queries group/order scalar and
anonymous projections before materialising, per
the `GetUsageByUserAsync` lesson. DTOs appended to
`LocalizationDtos.cs` (summary, four total shapes,
missing-rate, event, rate, add-rate request);
service registered scoped in `Program.cs`.

Task 4 — one event per provider call.
`WorkflowService` takes optional trailing
`UsageMeteringService? usage = null` (existing
direct constructions keep compiling) with a
null-tolerant `RecordUsageAsync` helper. MT
records after both `TranslateAsync` calls with
source-text length; existing ledger arithmetic
untouched. Optimize records on success with the
result's tokens and cache flag; outright failure
records nothing. QPS plumbing:
`AiQpsScoreResult` gained `InputTokens`/
`OutputTokens` (deserialised case-insensitively;
only constructed by the deserializer),
`QualityScoreResult` trailing optionals (fixture
fake untouched), `LocalizationAiException` two
settable token properties filled by
`QpsScoringService` on fallback-throw and
returned on success; both workflow calls record
on success and record `Succeeded = false` in the
catch when tokens are known. Auto-Route
untouched. Every event carries project, step and
the run timestamp.

Task 5 — operations endpoints. New
`api/Endpoints/Localization/UsageEndpoints.cs`,
group `/api/localization/ops`, mapped after
`MapProviderHealthEndpoints`: usage summary
(`month` defaults to current UTC month,
`yyyy-MM` parse else 400; unknown project 404),
recent events (`limit` default 100, clamped in
the service), rates newest-first, and add-rate
(unknown meter/kind or negative/missing price
400, duplicate triple 409, 201 with the rate).
Field names match CONTRACT 4.1/4.2 exactly;
`caps` left out for R2. All four check the admin
role first with the same 403 body.
`LoadApprovedAdminAsync` moved verbatim to new
`api/Endpoints/AdminAuthorization.cs`; call
sites resolve it through one `using static`, so
`AdminEndpoints.cs` is otherwise untouched.

Task 6 — tests. New
`tests/StudyTracker.Api.Tests/Localization/UsageMeteringTests.cs`
(9 facts): MT events per translated pair with
source lengths and none for the pre-translated
pair; optimize events with tokens and a zero-cost
cache hit under an existing rate; QPS success
with both calls; fallback-with-tokens records
`Succeeded = false`; zero-token failure records
nothing; rate-in-force-at-event-time wins
(0.14/0.24); no rate means cost 0 plus a
`ratesMissing` entry; two-month two-project
summary exactness plus the all-projects sum;
unmetered `WorkflowService` runs all eight
actions (phase-3 unconfigured ones throw
`NotImplementedException`, never NRE) and
records nothing. Existing tests edited: NONE —
the optional constructor parameter, trailing
optional record parameters and additive
exception properties keep every existing
construction compiling. Item 8: the test project
has NO endpoint-calling infrastructure (no
`WebApplicationFactory`, `TestServer` or
`HttpClient` anywhere), so no endpoint test was
added and none invented.

## R1 — reviewer check (12 Nov 2026)

Run in containers against a real PostgreSQL 16 database. Result: **green after five small fixes made by the reviewer**.

- Designer: generated from the snapshot with a script (`20261112120000_AddLocalizationUsageMetering.Designer.cs`). From R2 on, Muse writes no designer; the reviewer generates it.
- EF model check (`dotnet ef migrations add` on the finished code): the first run produced a non-empty migration, an index on `localization_usage_events.workflow_step_id` that EF creates for every foreign key. Added `ix_localization_usage_events_workflow_step_id` to the mapping, the migration and the snapshot; the model check is now empty.
- Migrations apply from an empty database; the history ends with `20261112120000_AddLocalizationUsageMetering`.
- Tests: `UsageMeteringTests.cs` did not compile (`Options.Create` resolved to the `StudyTracker.Api.Options` namespace); fixed with the full name. Then two failures: an expected list in the wrong order (test), and the summary returning `unitsOut: 0` instead of `null` for the character meter (service: SQL `SUM` is wrapped in `COALESCE`). Both fixed. A nullable warning on `e.Project.Slug` fixed. Now 190 passed, 1 skipped (the existing skip), no warnings.
- Real stack (database, .NET API, `localization-ai` with fake providers): machine translation recorded 136 events with source characters; MT Optimize twice recorded 272 events, 136 of them cache hits; QPS with the fake judge recorded 136 failed events with their tokens. `GET /ops/usage` is 403 signed out and 200 for a signed-in admin; rate add 201, duplicate 409, unknown meter 400, malformed month 400, unknown project 404; events newest first.
- Line endings: Muse's LF files are fine; git stores LF and converts on checkout (`core.autocrlf=true`).
