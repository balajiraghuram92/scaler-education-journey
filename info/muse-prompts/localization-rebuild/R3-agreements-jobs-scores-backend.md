# R3 — Localization Lab rebuild: agreements, jobs by assignment, 1-5 scores (.NET backend)

Third and last backend step of track R. **Run it only after R2 has been reviewed and committed.** This is the step that removes things: bidding, credits and client-visible scores.

Authority for every route, field name and fixed string: `info/muse-prompts/localization-rebuild/CONTRACT.md` (sections 1, 2, 3, 4.4 and 6). Do not edit the contract.

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository (ASP.NET Core 8 minimal API in `api/`, xUnit tests in `tests/StudyTracker.Api.Tests/`). For this task you may edit files under `api/` and `tests/`.

Work only in `api/` and `tests/StudyTracker.Api.Tests/`. Do not touch `app/`, `api-python/`, `localization-ai/`, compose files, `.env*`, deploy scripts or workflows. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `info/muse-prompts/localization-rebuild/PROGRESS.md` under "R3" before starting the next. Find code by name; line numbers have moved since R1 and R2.

## The model being built

- A project has one **service agreement** with a **tier**. The tier is team capacity only: Silver 3 linguists per team, Gold 6, Platinum 10.
- The agreement assigns one **vendor team** to each locale. A translation job for a locale goes to that team. Nobody bids and nothing has a price.
- **Aliases both ways.** A client response never carries a vendor's real name. A vendor response never carries a project's real name or slug. Operations responses carry both.
- **Scores are 1 to 5 and vendor-only.**

## Read these first, in full

- `info/muse-prompts/localization-rebuild/CONTRACT.md` and `PROGRESS.md`
- `api/Models/Localization/` (every file)
- `api/Services/Localization/MarketplaceService.cs`, `VendorPortalService.cs`, `CreditLedgerService.cs`, `WorkflowService.cs`, `LocalizationStringService.cs`, `LocalizationProjectService.cs`, `LocalizationDtos.cs`, `LocalizationExceptions.cs`, `AutoRoutingService.cs`, `QpsScoringService.cs`
- `api/Endpoints/Localization/` (every file)
- `api/Data/LocalizationSeedData.cs` and the Localization blocks of `api/Data/StudyTrackerContext.cs`
- `tests/StudyTracker.Api.Tests/Localization/` (every file)

## Task 1 — schema

Entity changes (keep the existing attribute style):

1. `Vendor` (table `localization_vendors`, kept): add `Alias` (`alias`, varchar(100), required, unique index `ux_localization_vendors_alias`). `Name` stays and is the **real** name. Remove `Rating` and the `Bids` collection. Rename the `AwardedJobs` collection to `Jobs`.
2. `LocalizationProject`: add `ClientAlias` (`client_alias`, varchar(100), required). Change the C# default of `QpsThreshold` to 4. Remove the `LedgerEntries` collection only if nothing else needs it; the `LedgerEntry` entity and table stay as history.
3. New `ServiceAgreement`, table `localization_service_agreements`: `Id`; `ProjectId` (FK cascade, **unique**); `Tier` (varchar(20), required); `ValidFrom`; `ValidTo` (nullable); `Notes` (text, nullable); `CreatedAt`.
4. New `TeamAssignment`, table `localization_team_assignments`: `Id`; `AgreementId` (FK cascade); `VendorId` (FK restrict); `LocaleCode` (varchar(20), required); `MemberCount` (int). Unique index on `(AgreementId, LocaleCode)`.
5. Rename the C# class `MarketplaceJob` to `TranslationJob`. **Keep the table name `localization_marketplace_jobs` and the existing column names**, to avoid a table rename with its constraint renames; say so in a comment on the class. Property changes: remove `SuggestedPriceLow`, `SuggestedPriceHigh`, `AwardedAt` and `Bids` (their columns are dropped); rename `AwardedVendorId`/`AwardedVendor` to `VendorId`/`Vendor`, still mapped to the column `awarded_vendor_id`; rename `PostedAt` to `CreatedAt`, still mapped to `posted_at`. Default `Status` is `"Assigned"`. Rename the `DbSet` and the project's collection to match.
6. Delete `MarketplaceBid` and its `DbSet` and mapping.
7. `LocalizationTranslation`: keep the columns `qps_score` and `raw_mt_qps_score`; they now hold 1 to 5. Add two check constraints, `ck_localization_translations_qps_score_range` and `ck_localization_translations_raw_mt_qps_score_range` (null, or between 1 and 5).
8. A static `ServiceTiers` class: the three names and `MembersFor(tier)` returning 3, 6, 10.

Hand-write migration `20261112140000_LocalizationAgreementsAndJobs` and the snapshot update. Do not write the `.Designer.cs` (the reviewer generates it). Every new foreign key needs an index that starts with its column, as R2's migration rules say; `TeamAssignment.VendorId` is one. Order inside `Up` matters:

1. Add `alias` and `client_alias` as nullable; backfill with `migrationBuilder.Sql`: `alias = 'Vendor Team ' || id`, `client_alias = 'Client Team ' || id`; then alter both to not null; then create the unique index.
2. Create the two new tables.
3. Data fixes with `migrationBuilder.Sql`: set `qps_score` and `raw_mt_qps_score` to null everywhere (the old values are on a 0 to 100 scale and mean nothing now) and `needs_review` to false; set `qps_threshold` to 4 on every project and change the column default to 4; rename workflow actions `'Post to Marketplace'` → `'Create Translation Jobs'` and `'Score QPS'` → `'Score Quality'`; map job statuses `'Open'` → `'Assigned'` and `'Awarded'` → `'Assigned'`; delete jobs that have no vendor (`awarded_vendor_id is null`), since an unassigned job cannot exist in the new model.
4. Add the check constraints (after the scores are nulled).
5. Drop `localization_marketplace_bids`; drop the three job columns and `localization_vendors.rating`.

Read every table and column name from the snapshot. `Down` restores the schema; it cannot restore deleted data, and should say so in a comment.

## Task 2 — seed data

`LocalizationSeedData`:

- The five vendors become teams: keep the existing names as real names and give each an alias: `Vendor Team Larch`, `Vendor Team Osprey`, `Vendor Team Juniper`, `Vendor Team Heron`, `Vendor Team Cedar`, in the existing order.
- The demo project gets `ClientAlias = "Client Team Kestrel"` and a `Gold` agreement that assigns a team to each of its five locales. Choose for each locale a team whose `Languages` contains it; if a locale has no such team, extend that team's `Languages` in the seed and say which in the report.
- Seeded jobs: keep the ones that had an awarded vendor, with the new statuses; remove seeded bids and any seeded job that was only open for bidding.
- Seeded ledger rows stay as history.
- Extend the idempotent "ensure" step from R2: when the demo project exists without an agreement, create the agreement and assignments, and set real aliases on the five seeded vendors and the demo project if they still have the backfilled `… {id}` form.

## Task 3 — services

Replace `MarketplaceService` with `TranslationJobService` (new file; delete the old one and `CreditLedgerService.cs`):

- `GetJobsForProjectAsync(slug)`: one row per project locale (CONTRACT 2.5), including locales with no job.
- `CreateJobAsync(slug, localeCode)`: team from the agreement; `NO_TEAM_FOR_LOCALE` and the "job exists" case as 409s; counts computed from the strings as `PostToMarketplaceAsync` computes them today; status `Assigned`; `CreatedAt = now`.
- `ApproveAsync(jobId)` and `SendBackAsync(jobId)`: same state rules and same bulk stage changes as `ApproveSubmissionAsync` and `SendBackForRevisionAsync` today, minus the ledger entry.
- `GetAgreementAsync(slug, forOperations)` and `SaveAgreementAsync(slug, request)` (CONTRACT 2.4 and 4.4).

`VendorPortalService`:

- `GetVendorRosterAsync` returns id, alias, languages.
- `GetJobsForVendorAsync(vendorId)` replaces the open-jobs and awarded-jobs methods.
- Delete `SubmitBidAsync` and `GetOpenJobsForVendorAsync`.
- The first-edit rule (`Assigned` or `NeedsRevision` → `InProgress`) replaces the old `Awarded` rule. Everything else in `UpdateJobStringAsync` and `SubmitJobForReviewAsync` is unchanged.
- Vendor rows use the vendor DTOs (below).

`WorkflowService`:

- `PostToMarketplace` becomes `CreateTranslationJobs` with the value `"Create Translation Jobs"`; it calls `CreateJobAsync` per locale and reports `"{created} jobs created, {skipped} skipped"`; a locale with no team or with an existing job counts as skipped.
- `ScoreQps` becomes `ScoreQuality` with the value `"Score Quality"`. A score outside 1 to 5 from the scorer is treated as a failed call for that string (not stored).
- Remove the two `LedgerEntry` writes with `Source = "AI"`. Usage events from R1 are the record now. Remove the constructor dependency on the marketplace service and inject `TranslationJobService`.
- `AutoRoute` is unchanged in code: it already passes the score and `project.QpsThreshold`. The meaning is now "a score below the threshold needs review" on the 1 to 5 scale.

`LocalizationProjectService`: fill `Tier` from the agreement.

## Task 4 — DTOs and audience separation

In `LocalizationDtos.cs`, per CONTRACT sections 2 and 3:

- `LocalizationStringRowDto` (client): remove `QpsScore`, `NeedsReview`, `RawMtText`, `RawMtQpsScore`.
- New `VendorStringRowDto`: the client fields plus `Score`, `NeedsReview`, `RawMtText`, `RawMtScore`.
- New `TranslationJobRowDto` (client) and `VendorJobRowDto` (vendor): exactly the fields in the contract. The vendor one has `ClientAlias` and no project id, name or slug.
- New `VendorTeamDto` (id, alias, languages) and `OpsVendorTeamDto` (adds `RealName`).
- Agreement DTOs for the client and operations shapes.
- Delete `MarketplaceBidDto`, `MarketplaceJobSummaryDto`, `MarketplaceJobDto`, `SubmitBidRequest`, `VendorDto`.

Then prove the separation by reading: list in `PROGRESS.md`, for every Localization endpoint, its audience and the DTO it returns, and confirm that no client DTO has a property carrying a vendor real name, a score, a raw draft or a review flag, and that no vendor DTO carries a project name, slug or id.

## Task 5 — endpoints

Per CONTRACT sections 2.4, 2.5, 3 and 4.4:

- Replace `MarketplaceEndpoints.cs` with `JobEndpoints.cs`: project jobs list and create, job approve and send-back, client agreement read. Remove every marketplace route and its registration.
- `VendorPortalEndpoints.cs`: roster, `GET /{vendorId:int}/jobs`, strings read and update, submit. Remove the three removed routes.
- `UsageEndpoints.cs` (operations): `GET /teams`, `GET` and `PUT /projects/{slug}/agreement`.
- Keep the route constraints (`:int`) and the problem shapes used today. New 409s use the existing invalid-state mapping.

## Task 6 — tests

Delete the tests for bidding, awarding and price bands. Add or adapt, following the fixture:

1. Job creation takes the team from the agreement; a locale without a team gives `NO_TEAM_FOR_LOCALE`; a second create for the same locale is refused unless the first is `Approved`.
2. Lifecycle: `Assigned` → first vendor edit → `InProgress` → submit → `SubmittedForReview` → approve → `Approved`; send-back → `NeedsRevision` → edit → `InProgress`. Illegal transitions are refused.
3. `completedPercent` on a fixture with a known mix of stages.
4. Agreement save: member count follows the tier; unknown tier, foreign locale, unknown team and duplicate locale are rejected.
5. Audience separation, as assertions on serialised JSON: a client job row and string row contain neither the seeded vendor real name nor the property names `score`, `qpsScore`, `rawMtText`, `needsReview`; a vendor job row and string row contain neither the project's name nor its slug.
6. "Create Translation Jobs" action outcome counts.
7. "Score Quality": a scorer returning 4 stores 4; a scorer returning 87 stores nothing and counts a failure.
8. Auto-Route with threshold 4: scores 1 to 3 are flagged, 4 and 5 are not.

List every existing test you deleted or edited and why.

## Not in this prompt

The React app (R4), the AI service's judge scale (R5), `api-python/` (R6). The AI service will return 0 to 100 scores until R5 lands; Task 3's range rule makes those count as failed rather than being stored.

## Finish

End with a short report: each task done or not done, every file created, changed or deleted, the audience table from Task 4, the seed choices from Task 2, deleted and edited tests, and anything that could not be done as written. Never say a build or test passes; you have not run it.
