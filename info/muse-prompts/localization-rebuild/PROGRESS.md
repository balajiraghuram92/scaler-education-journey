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

R1 review resolutions (found already applied in
the tree when R2 started): the reviewer generated
`20261112120000...Designer.cs`, added the missing
`ix_localization_usage_events_workflow_step_id`
index to the R1 mapping, migration and snapshot,
and fixed the test to the full
`Microsoft.Extensions.Options.Options.Create`
form. Per the R2 rules, no designer is written
for R2 either.

## R2 — caps, kill switch, Azure Translator

Task 1 — caps and kill-switch model.
`LocalizationProject.AiEnabled` (`ai_enabled`,
default true); new `LocalizationUsageCap`
(`localization_usage_caps`: project FK cascade,
`kind`, `monthly_limit` bigint, `UpdatedAt`) with
`UsageCapKinds` constants; `DbSet` plus mapping
with the unique `(ProjectId, Kind)` index (which
starts with the FK column, satisfying the FK
index rule — no extra index needed).
`20261112130000_AddLocalizationUsageControls`
adds the column (`defaultValue: true`, as
`qps_threshold` was) and the table/index; `Down`
reverses; snapshot updated in both sections. No
`.Designer.cs` per the track rules. Seed data:
demo project gets 2M/5M caps in `Seed`, plus
idempotent `EnsureUsageCaps` called from
`DbSeeder` right after `Seed`.

Task 2 — caps and kill-switch behaviour.
`UsageMeteringService.BeginRunAsync` loads caps
plus per-meter monthly usage (cache hits
excluded) in two queries and returns an
in-memory `UsageBudget` (`CanSpend` with the
known-size rule for MT and the at-or-over rule
for llm called with 0, `Spent`, `Used`,
`Limit`). The four provider actions throw
`LocalizationAiDisabledException` first when
`AiEnabled` is false; the three calling actions
take the budget once and throw
`LocalizationUsageCapReachedException` when the
cap is already reached; inside the loops a
failed `CanSpend` skips the string (counted,
loop continues, no further calls); outcomes gain
`, {n} skipped: monthly {kind} cap reached
({used} of {limit})` with end-of-run numbers;
`Spent` follows every record with the same
units (0 on cache hits). Both exceptions are new
in `LocalizationExceptions.cs` with
project/kind/used/limit details, mapped to 409
in the run endpoint with the contract titles.
Null metering service means no budget and no
caps, as in R1.

Task 3 — controls endpoints and summary caps.
`UsageEndpoints` gained `GET`/`PUT
/projects/{slug}/controls` (same admin check;
unknown project 404): GET returns project slug,
`AiEnabled` and per-kind limit-or-null plus
current-month used via `BeginRunAsync`; PUT
reads the body as `JsonElement` so absent
fields stay unchanged while explicit null
removes a cap (non-boolean/non-integer values
and negative limits are 400), then returns the
GET shape. `UsageSummaryDto` gained a
`WhenWritingNull`-omitted `caps` array, present
only when a project is given, computed for the
summary's own month. `LocalizationProjectDto`
gained trailing `AiEnabled` and `Tier` (null in
this step); both service constructions updated.

Task 4 — Azure Translator replaces Google
Translate. New `AzureTranslatorOptions`
(section `AzureTranslator`, default endpoint,
`Key`, `Region`) and
`AzureTranslatorProviderService`
(`ITranslationProvider`): POST
`{Endpoint}/translate?api-version=3.0&from=&to=`
with `Ocp-Apim-Subscription-Key` and optional
region headers, `[{"Text"}]` body, first
translation's text from the array response;
locale codes passed through with no mapping
table; key only ever in a header. No-key and
failure behaviour mirrors the Google service
exactly (production throws
`InvalidOperationException` with an Azure
message, otherwise warn + `[MOCK-{TARGET}]`
text). `Program.cs` binds options, client and
`ITranslationProvider` to Azure; Google
registrations removed.
NOT DONE AS WRITTEN: the two Google files could
not be deleted — file deletion needs a shell
command, which is forbidden here. Reviewer:
delete `api/Options/GoogleTranslateOptions.cs`
and `api/Services/Localization/
GoogleTranslateProviderService.cs` (nothing
references either type anymore; verified by
search). Remaining "google" hits are lesson
content (untouched), one pricing comment in
`LocalizationAiOptions`, and Task 5 items.
`LegacyMtPricePerCharUsd` kept. Owner env vars:
ADD `AzureTranslator__Key` and
`AzureTranslator__Region` (optionally
`AzureTranslator__Endpoint`); REMOVE the Google
key variable. NOTE FOR THE OWNER: Azure's
handling of each seeded locale code (`de-DE`,
`ja-JP`, `zh-CN`, `fr-FR`, `es-ES`) must be
checked against a real key.

Task 5 — action and provider renames.
`AutoTranslateViaGoogleMt` became
`AutoTranslateViaAzureTranslator` with value
"Auto-Translate via Azure Translator" (all
three code uses plus the outcome text);
`ProviderHealthService` special-cases
"AzureTranslator"; the seeded health row is now
`AzureTranslator` (local variable renamed to
match); the R2 migration updates both stored
strings (table/column names verified in the
snapshot) and `Down` reverses them. `LlmAzureGpt`
and every other provider name untouched.

Task 6 — tests. Full-argument constructor calls
(explicit trailing nulls, still unmetered) in
the fixture, `LocalizationAiWorkflowTests` and
`WorkflowServiceTests`; old action strings
updated in `LocalizationAiWorkflowTests` and
`UsageMeteringTests`. New `UsageControlsTests`
(6 facts + 1 theory): disabled project throws
the named exception on all four provider
actions; reached MT cap throws with kind/used/
limit and zero provider calls; part-way MT run
skips before and after its one real call with
the exact outcome text and the translation
kept; crossing llm call completes then stops
with the exact outcome; high cap matches
uncapped behaviour for outcomes, events and
ledger. PUT-controls endpoint behaviours are
NOT tested: as established in R1, the project
has no endpoint-calling infrastructure, so per
the R1 rule none was invented — covered
instead: cap rows drive budgets, the flag
drives the kill switch. Item 7 verified:
`UsageMeteringTests` uses the new action name,
the R1 no-metering test is untouched and still
valid, the fixture scorer and fake-handler
response shapes are unchanged.

## R3 — agreements, jobs by assignment, 1-5 scores

Task 1 — schema. `Vendor` gained required
unique `Alias`, lost `Rating` and `Bids`,
`AwardedJobs` became `Jobs`;
`LocalizationProject` gained required
`ClientAlias`, `QpsThreshold` defaults to 4,
and the `LedgerEntries` collection is gone
(verified: only the mapping referenced it).
New `ServiceAgreement` (unique `ProjectId`)
and `TeamAssignment` (unique
`(AgreementId, LocaleCode)`, restrict vendor
FK) entities plus `ServiceTiers` (3/6/10).
`MarketplaceJob` became `TranslationJob` on
the same table and columns (prices, awarded-at
and bids dropped; vendor/created renamed in
C# only; status defaults to `Assigned`);
`MarketplaceBid` and its `DbSet`/mapping are
gone; translation score columns kept with the
two new range checks. `DbSet`s renamed/added
to match; FK index rule holds (new FKs each
start an index: the two unique indexes and
`ix_localization_team_assignments_vendor_id`).
Migration `20261112140000` follows the
specified order (nullable add, exact-string
backfill, alter, alias index, tables, data
fixes, checks, drops); `Down` reverses the
schema with an explicit unrestorable-data
comment, re-adding non-nullable columns with
`defaultValue: 0m` so it runs on non-empty
tables. Snapshot updated in all three
sections; verified free of the removed
members. No `.Designer.cs` per the track
rules. `MarketplaceJob.cs`/`MarketplaceBid.cs`
are emptied pending reviewer deletion (no
shell to delete); `LedgerEntry`'s
`RelatedMarketplaceJob` names stay, type
repointed.

Task 1 (R3) — schema. `Vendor`: required
unique `Alias`, `Rating`/`Bids` gone,
`AwardedJobs`→`Jobs`. `LocalizationProject`:
required `ClientAlias`, `QpsThreshold`
default 4, `LedgerEntries` collection
removed (verified: only the mapping
referenced it). New `ServiceAgreement`
(unique project) and `TeamAssignment`
(unique agreement+locale, restrict vendor
FK) plus `ServiceTiers` (3/6/10).
`MarketplaceJob`→`TranslationJob` on the
same table/columns (prices, awarded-at,
bids dropped; vendor/created renamed in C#
only; status defaults `Assigned`);
`MarketplaceBid`/its `DbSet`/mapping gone;
score range checks on translations.
`DbSet`s renamed/added; every new FK starts
an index (unique agreement index, vendor
index). Migration `20261112140000` in the
specified order with exact-string backfill
and data fixes; `Down` restores schema with
an unrestorable-data comment
(non-nullable re-adds carry `defaultValue:
0m` so it runs). Snapshot updated in all
three sections and verified clean of
removed members. No designer per track
rules. Old entity files emptied pending
reviewer deletion.

Task 2 (R3) — seed data. Vendors keep real
names with aliases Larch/Osprey/Juniper/
Heron/Cedar in order (ratings dropped);
project gets `Client Team Kestrel` plus a
Gold agreement: de→Maria, ja→Kenji,
zh→Marcus, fr→Maria, es→Elena at 6 members
each. Every locale was already covered by
its team's Languages — no extension needed.
Jobs kept: de Assigned, fr SubmittedForReview,
es Approved (vendor ids, no prices, no bids);
the open ja job and all bids removed.
Ledger history kept. Five seeded 0-100
scores nulled (required, though unlisted:
fresh seeding would otherwise violate the
new checks, matching the migration's
treatment). `EnsureUsageCaps` extended with
`EnsureServiceAgreement`: creates a missing
Gold agreement with the same five
assignments and repairs backfilled
`… {id}` aliases to the real ones.

Task 3 (R3) — services. New
`TranslationJobService`: per-locale job rows
incl. live-count NotCreated rows; `CreateJobAsync`
takes the team from the agreement
(`NO_TEAM_FOR_LOCALE`/job-exists 409s, counts
as today, `Assigned`); `ApproveAsync`/
`SendBackAsync` keep state rules and bulk
changes minus the ledger (no awarded-bid
check can exist); agreement read (null when
none) and create-or-replace save with 400
validation. `VendorPortalService`
rewritten: alias roster, vendor jobs
newest-first, strings/submit on vendor DTOs,
Assigned first-edit rule, bid methods
deleted, marketplace dependency removed.
`WorkflowService`: `CreateTranslationJobs`
action, `ScoreQuality` with out-of-1..5 =
failed call (tokens spent, nothing stored),
both AI ledger writes plus their counters
removed, `TranslationJobService` injected.
Project service fills `Tier`; DI swapped;
the two deleted service files emptied
pending reviewer deletion. Judgment calls:
zero-count create still throws (so the
workflow action skips finished locales
instead of creating empty jobs), and the
old `*NotFoundException`/`InvalidJobState`
names are reused unchanged.

Task 4 (R3) — DTOs and audience separation.
Client string row trimmed of the four
score/draft/flag fields; new vendor string
row (client fields + score, needsReview,
rawMtText, rawMtScore), client + vendor job
rows, team + ops-team DTOs, client + ops
agreement DTOs and shapes, and the save
request, all with exact contract field
names. Deleted `MarketplaceBidDto`,
`MarketplaceJobSummaryDto`, `MarketplaceJobDto`,
`SubmitBidRequest`, `VendorDto`; updated the
two string-service constructions (verified:
no other constructions remain).
Audience audit, every Localization endpoint:
CLIENT — projects list/get
(`LocalizationProjectDto`), strings list/
update (`LocalizationStringRowDto`), all
workflow routes (`WorkflowStepDto`/success/
204), snapshots (`BuildSnapshotDto`), jobs
list/create/approve/send-back
(`TranslationJobRowDto`), agreement read
(`ServiceAgreementDto`); VENDOR — roster
(`VendorTeamDto`), jobs
(`VendorJobRowDto`), strings read/update
(`VendorStringRowDto`), submit
(`VendorJobRowDto`); OPS — usage, events,
rates, controls, teams
(`OpsVendorTeamDto`), agreement read/save
(`OpsServiceAgreementDto`), provider
health. CONFIRMED by reading: no client
DTO carries a vendor real name (only
aliases), a score, a raw draft or a review
flag; no vendor DTO carries a project
name, slug or id (only the client alias).

Task 5 (R3) — endpoints. New `JobEndpoints`
(jobs list/create/approve/send-back and the
client agreement read) replaces
`MarketplaceEndpoints` (file emptied pending
reviewer deletion; `Program.cs` remapped);
`VendorPortalEndpoints` rewritten to roster,
vendor jobs, strings read/update and submit;
`UsageEndpoints` gained ops teams plus ops
agreement read/save. Route shapes, `:int`
constraints, 404 titles and the
invalid-state 409 mapping all follow the
existing files; new 409s reuse it, save
validation is 400. Verified by search: no
references remain in `api/` to the removed
routes, bid/award/balance methods or DTOs.

Task 6 (R3) — tests. Deleted
`MarketplaceServiceTests` (file emptied
pending reviewer deletion); rewrote
`VendorPortalServiceTests` to roster, jobs,
strings and submit (bidding tests gone);
adapted `WorkflowServiceTests` (create-jobs
action tests with agreement setup),
`LocalizationAiWorkflowTests` (in-range
scores, threshold-4 auto-route, empty
ledger, renames), `UsageMeteringTests` and
`UsageControlsTests` (renames, in-range
fake scores, no-metering score expectation
now all-failed); fixture `Marketplace()`
became `Jobs()` with all call sites
updated. New `TranslationJobServiceTests`
covers create/team/409s, the full lifecycle
plus terminal and send-back branches,
completedPercent (75 on a mixed fixture,
0 on empty), all four save validations
plus tier-capacity update, and audience
separation by serialized JSON keys. Item 6
verification: exhaustive search finds zero
references in live code and tests to old
actions, statuses, providers, prices,
bids, ratings, `PostedAt`/`AwardedAt` or
removed DTOs/methods/routes (only frozen
old-migration histories plus the
intentional `RelatedMarketplaceJob*` and
not-found-exception keeps). Item 7 holds:
fixture scorer and fake-handler shapes
untouched. Endpoint-handler specifics
remain untested per the R1 no-endpoint-
infrastructure rule.

## R1 — reviewer check (12 Nov 2026)

Run in containers against a real PostgreSQL 16 database. Result: **green after five small fixes made by the reviewer**.

- Designer: generated from the snapshot with a script (`20261112120000_AddLocalizationUsageMetering.Designer.cs`). From R2 on, Muse writes no designer; the reviewer generates it.
- EF model check (`dotnet ef migrations add` on the finished code): the first run produced a non-empty migration, an index on `localization_usage_events.workflow_step_id` that EF creates for every foreign key. Added `ix_localization_usage_events_workflow_step_id` to the mapping, the migration and the snapshot; the model check is now empty.
- Migrations apply from an empty database; the history ends with `20261112120000_AddLocalizationUsageMetering`.
- Tests: `UsageMeteringTests.cs` did not compile (`Options.Create` resolved to the `StudyTracker.Api.Options` namespace); fixed with the full name. Then two failures: an expected list in the wrong order (test), and the summary returning `unitsOut: 0` instead of `null` for the character meter (service: SQL `SUM` is wrapped in `COALESCE`). Both fixed. A nullable warning on `e.Project.Slug` fixed. Now 190 passed, 1 skipped (the existing skip), no warnings.
- Real stack (database, .NET API, `localization-ai` with fake providers): machine translation recorded 136 events with source characters; MT Optimize twice recorded 272 events, 136 of them cache hits; QPS with the fake judge recorded 136 failed events with their tokens. `GET /ops/usage` is 403 signed out and 200 for a signed-in admin; rate add 201, duplicate 409, unknown meter 400, malformed month 400, unknown project 404; events newest first.
- Line endings: Muse's LF files are fine; git stores LF and converts on checkout (`core.autocrlf=true`).

## R2-R6 — reviewer check (2026-11-12)

Reviewer-side changes:
- Deleted the 20 files Muse emptied for deletion (.NET marketplace/credits/Google files, the four old React marketplace pages, eight api-python files).
- Fixed three C# compile breaks: `AzureTranslatorProviderService` read `_options.ApiKey` (the option is `Key`); `VendorPortalService.GetJobsForVendorAsync` passed a job where `VendorJobRowAsync` takes its id; the test fixture set the removed `Vendor.Rating` (now `Alias = "Test Team"`).
- `StudyTrackerContext`: the `qps_threshold` default was still 70 in the mapping while the snapshot and migration say 4; the model check failed until it was 4.
- Designers: `20261112140000_LocalizationAgreementsAndJobs.Designer.cs` generated from the snapshot; `20261112130000_AddLocalizationUsageControls.Designer.cs` carries only the `[DbContext]`/`[Migration]` attributes (its target model would be the snapshot between R2 and R3, which no longer exists as a file; the later designer holds the full model).
- Two stale C# tests: raw score 55 -> 2 (1-5 rule); the high-cap test now asserts no ledger rows (R3 removed the writes).
- React: `LocalizationWorkflow.test.jsx` referred to an undefined `Detail`.

Results:
- .NET: build clean, EF model probe empty, R1-R3 migrations apply to an empty database, tests 202 passed / 1 skipped.
- React: vitest 81/81, oxlint 0 errors, `vite build` ok.
- localization-ai: 92 passed / 7 skipped, ruff and mypy clean (`ruff format --check` would reformat 7 files; not checked in earlier rounds).
- Real stack (.NET + localization-ai with fake providers): client JSON carries no vendor real names and no score fields; vendor JSON carries no project name or slug; job lifecycle Assigned -> InProgress -> SubmittedForReview -> NeedsRevision -> InProgress -> SubmittedForReview -> Approved; kill switch 409 on provider actions and Auto-Route, Mark Translated still runs; MT cap cut a run part-way (22 translated, 72 skipped, 22,526 of 22,527 used); llm cap lets the crossing call finish then skips, next run 409; controls PUT absent/null/negative rules; agreement validation 400s, Platinum save sets member counts to 10, a locale without a team gives NO_TEAM_FOR_LOCALE; Auto-Route flags scores below the threshold of 4; removed marketplace routes 404; provider health shows AzureTranslator. Browser: Jobs, Strings, Workflow and vendor workspace pages checked; the Operations page was not clicked through (pane hidden), its component tests pass.
- Scoring through the fake model always falls back (no score), as in R1; the 1-5 path is covered by tests only until a real model key is set.
- api-python: 7 failed / 209 passed, 2 ruff and 3 mypy errors, seeder imports deleted modules -> `info/muse-prompts/corrections/C17-api-python-track-r.md`. Parity run after C17.

Design point for the owner: a translation job covers only strings with no translation yet (as the marketplace did). After "Auto-Translate via Azure Translator" fills a locale, "Create Translation Jobs" skips it, so vendors never see machine output to post-edit.

## R7 — jobs include machine output for vendor post-editing (.NET + React)

Task 1 — one definition of "open" and "vendor-reviewed". New
`api/Services/Localization/JobScope.cs`: `VendorSource`
("Marketplace") and `MachineSource` ("AI") constants;
`IsOpen` (no translation, blank text, or stage not
"Approved"); `IsVendorReviewed` (source "Marketplace",
non-blank text); `CompletedPercent` per CONTRACT 2.5
(100 when "Approved", 0 when `stringCount` is 0, else
vendor-reviewed non-Approved count * 100 / stringCount,
capped at 100). Deleted the private `CompletedPercent`
in `TranslationJobService` and `VendorPortalService`;
the three client call sites and the vendor call site
now call `JobScope.CompletedPercent` with the job
status. `VendorPortalService` writes
`JobScope.VendorSource` instead of the "Marketplace"
literal (two spots in `UpdateJobStringAsync`).

Task 2 — job creation and the jobs list. In
`TranslationJobService`: `NotCreated` rows count
`stringCount`/`wordCount` over `JobScope.IsOpen`
strings with `completedPercent` 0 (per the contract,
not computed); existing-job rows and `JobRowAsync`
use `JobScope.CompletedPercent` with the job status
(wired in task 1); `CreateJobAsync` freezes
`StringCount`/`WordCount` over the open strings and
throws the unchanged "nothing left to translate" 409
only when no string is open. Team, existing-job and
`CountWords` rules untouched.

Task 3 — the vendor portal. `VendorStringRowDto`
gains `InJob` and `VendorReviewed` as the last two
fields (JSON `inJob`, `vendorReviewed` via the
camelCase default); the single `VendorStringRow`
builder sets them from `JobScope.IsOpen` and
`JobScope.IsVendorReviewed`. PUT on a string whose
translation stage is "Approved" throws 409 ("String
{stringId} is already approved for {localeCode}.");
otherwise unchanged, so re-sending the same text
accepts a machine draft (source becomes
"Marketplace", `RawMtText`/scores untouched).
Submit keeps the non-blank rule and adds the
machine-review rule ("{n} machine-translated strings
still need review before the job can be submitted.").
Vendor job rows use `JobScope.CompletedPercent`
(wired in task 1).

Task 4 — machine steps never overwrite vendor work.
`RunMtOptimize` now skips translations whose source
is not "AI" or whose stage is "Approved" before the
`RawMtText`/cap checks, so they count as neither
optimized, failed nor skipped. `ScoreQuality` and
`AutoRoute` gained the same `Stage != "Approved"`
condition alongside their existing `"AI"` source
check. Outcome text formats unchanged.

Task 5 — React: vendor workspace and jobs page.
`VendorMyJob.jsx`: unreviewed in-job rows with text
get an "Accept draft" button (borderless sage, like
the row edit button) that PUTs the row's own text
and refreshes from the response, disabled via
`savingId` while running; reviewed rows show a
"Reviewed" label; approved rows show nothing extra;
the header shows "{reviewed} of {inJob} strings
reviewed"; submit 409s now surface
`err.problemDetails?.Detail` (the
`LocalizationWorkflow.jsx` pattern). Score grouping
and filters untouched. `LocalizationJobs.jsx`
unchanged: its explainer ("One job per locale,
handled by the vendor team ...") never claimed
untranslated-only scope, so the conditional text
swap did not apply. `VendorMyJob.test.jsx` gains a
"draft review" block: accept button renders and
PUTs the row text, reviewed rows show the label
without the button, approved rows show neither,
the header count renders, and a submit 409 shows
the server detail.

Task 6 — .NET tests. New in
`TranslationJobServiceTests.cs`: all-AI locale
creates a job over all strings; all-Approved locale
throws "nothing left to translate"; `NotCreated`
row counts open strings (Approved + AI/Translated
gives 1); 4 open strings with 1 vendor accept gives
25 and approval gives 100. New in
`VendorPortalServiceTests.cs`: PUT-with-same-text
accepts a draft (source "Marketplace", `RawMtText`
kept, `VendorReviewed` true, Assigned -> InProgress);
PUT on an Approved string is 409; submit with one
unreviewed AI string is 409 and succeeds after the
accept; `RunMtOptimize` skips a Marketplace
translation with `RawMtText` (1 call, vendor text
untouched) via a new `CountingOptimizeHandler` —
no reusable fake optimizer existed (`FakeAiHandler`
is private to `LocalizationAiWorkflowTests`), so
this test carries its own counting handler and
writes `Microsoft.Extensions.Options.Options.Create`
in full per the brief. Existing-test fixes: the old
finished-stages percent test is rewritten to the
new rule (renamed
`CompletedPercent_CountsVendorReviewedNonApprovedOverJobTotal`,
now expects 50); `AudienceSeparation` passes the
two new DTO fields and asserts the `inJob` /
`vendorReviewed` JSON names; `WorkflowServiceTests`
skip test seeds Approved stages (Translated is now
open, so jobs would be created); `UsageMeteringTests`
`WorkflowWithoutMetering` expects "0 strings scored"
(the translations are Approved by then, so Score
Quality skips them instead of failing on the fake
score of 90).

## R7 — reviewer check (2026-11-12)

No reviewer edits needed. .NET 210 passed / 1 skipped; React 86/86. Real stack: after Auto-Translate, Create Translation Jobs made ja-JP and zh-CN jobs (47 strings each; before R7 it skipped them); submit refused with "47 machine-translated strings still need review…"; accept-by-resend kept text and raw draft and set the vendor source; completedPercent 4 after 2 of 47, 100 after all; MT Optimize skipped the vendor-reviewed strings (134 of 136) and left "VENDOR EDIT 1" alone, also after approval; edits after approval 409; a new job with nothing open 409. C17/R8 (api-python): 3 failed / 221 passed, ruff and mypy clean -> C18.

## R6, C17, R8, C18 — reviewer check (2026-11-12)

api-python against a PostgreSQL database migrated by the .NET API: 224 passed / 1 skipped; ruff and mypy clean (`ruff format --check` would reformat 187 files, the port's long-standing state, not enforced). Parity: 108/108 routes match the .NET API on the same seed. Seeder: an empty database seeded by the Python seeder and one seeded by the .NET seeder agree on all 14 localization table checks (projects, locales, strings, translations, vendors and aliases, agreement, team assignments, jobs, caps, provider health, ledger, workflow steps, glossary, snapshots). Track R is complete.
