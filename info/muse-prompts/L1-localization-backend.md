# L1 — Localization Lab: backend corrections (.NET)

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository (ASP.NET Core 8 minimal API in `api/`, React in `app/`, xUnit tests in `tests/StudyTracker.Api.Tests/`). The repo's `CLAUDE.md` is addressed to a different assistant; for this task you are authorised to edit the files listed under "Files you may change" and nothing else.

## Background

The "Localization Lab" feature was generated in one shot from a build prompt. An audit against the original spec found that the marketplace job lifecycle is not enforced on the server, and that the Workflow service duplicates logic that belongs to other services. Your job is to correct those deviations without changing the database schema, the routes, or the JSON shapes.

The intended job lifecycle is:

```
(no job) --post--> Open --award--> Awarded --first vendor edit--> InProgress
InProgress --vendor submit--> SubmittedForReview
SubmittedForReview --owner approve--> Approved
SubmittedForReview --owner send back--> NeedsRevision --first vendor edit--> InProgress
```

Bids: `Pending -> Awarded` (the chosen one) and `Pending -> Declined` (all siblings, at award time). Once a job leaves `Open`, it accepts no new bids.

## Read these first, in full

- `api/Services/Localization/MarketplaceService.cs`
- `api/Services/Localization/VendorPortalService.cs`
- `api/Services/Localization/WorkflowService.cs`
- `api/Services/Localization/CreditLedgerService.cs`
- `api/Services/Localization/LocalizationExceptions.cs`
- `api/Services/Localization/LocalizationDtos.cs`
- `api/Endpoints/Localization/LocalizationEndpoints.cs`
- `api/Endpoints/Localization/MarketplaceEndpoints.cs`
- `api/Endpoints/Localization/VendorPortalEndpoints.cs`
- `api/Data/LocalizationSeedData.cs` (read only, to know the seeded states)
- Two existing test files in `tests/StudyTracker.Api.Tests/` of your choice, to learn how tests build a database and call services or endpoints.

## Files you may change

- `api/Services/Localization/MarketplaceService.cs`
- `api/Services/Localization/VendorPortalService.cs`
- `api/Services/Localization/WorkflowService.cs`
- `api/Services/Localization/LocalizationExceptions.cs`
- `api/Endpoints/Localization/LocalizationEndpoints.cs`
- `api/Endpoints/Localization/MarketplaceEndpoints.cs`
- `api/Endpoints/Localization/VendorPortalEndpoints.cs`
- New test files under `tests/StudyTracker.Api.Tests/Localization/`

## Changes

### 1. `MarketplaceService.PostToMarketplaceAsync`

Current behaviour: it accepts any locale code, reuses and resets an existing job row to `Open` whatever state it is in (an Awarded or Approved job silently becomes Open again with its old bids and vendor still attached), and when a locale has nothing left to translate it invents numbers (all strings, or a hard-coded 50 words).

Required behaviour:
- If `localeCode` is not one of the project's `LocalizationLocale` rows, throw a new `LocalizationLocaleNotFoundException` (add it to `LocalizationExceptions.cs`, same style as the existing ones). Endpoint maps it to 404.
- Find the most recent job for the project and locale (highest `Id`). If one exists and its status is anything other than `Approved` or `Closed`, throw `InvalidJobStateException` with a message naming the current status. Endpoint maps it to 409.
- Count only strings that have no non-empty `TargetText` in that locale. If that count is zero, throw `InvalidJobStateException` ("nothing left to translate"). Delete both fallbacks.
- Always insert a **new** `MarketplaceJob` row. Never mutate an existing row in this method.

### 2. `MarketplaceService.AwardBidAsync`

Throw `InvalidJobStateException` unless the job status is `Open` and the chosen bid status is `Pending`.

### 3. `MarketplaceService.ApproveSubmissionAsync` and `SendBackForRevisionAsync`

- Both throw `InvalidJobStateException` unless the job status is `SubmittedForReview`.
- Approve: if there is no bid with status `Awarded`, throw `InvalidJobStateException`. Remove the fallback to `SuggestedPriceLow`.
- Approve: advance to `Approved` only the translations in that project and locale that have a non-empty `TargetText`.
- Keep the ledger entry and the status changes in the single `SaveChangesAsync` call that exists today.

### 4. `VendorPortalService.SubmitBidAsync`

Add these checks, in this order, each throwing the named exception:
- job status is not `Open` → `InvalidJobStateException`
- the job's `LocaleCode` is not in the vendor's comma-separated `Languages` (compare case-insensitively, trimmed, the way `GetOpenJobsForVendorAsync` already does) → new `VendorLanguageMismatchException` → endpoint returns 403
- the vendor already has a `Pending` bid on this job → `InvalidJobStateException`
- `proposedPrice <= 0` → `ArgumentException` → endpoint returns 400

### 5. `VendorPortalService.UpdateJobStringAsync`

- Throw `InvalidJobStateException` unless the job status is `Awarded`, `InProgress` or `NeedsRevision`. Today a vendor can still edit strings after the job is Approved.
- On a successful edit, move the job to `InProgress` when it is `Awarded` **or** `NeedsRevision` (today only `Awarded` is handled).

### 6. `VendorPortalService.SubmitJobForReviewAsync`

Throw `InvalidJobStateException` unless the job status is `Awarded`, `InProgress` or `NeedsRevision`. Keep the existing "every string must have a non-empty target" check.

### 7. `WorkflowService` — the "Post to Marketplace" action

Lines 341–377 re-implement the price formula inline and compute the word count from **all** strings, which disagrees with `MarketplaceService`. Replace the body of that case:
- Inject `MarketplaceService` into `WorkflowService`.
- For each locale on the project, call `PostToMarketplaceAsync`. Catch `InvalidJobStateException` per locale and treat it as "skipped".
- Outcome text: `"{posted} marketplace jobs posted, {skipped} skipped"`.
- Delete the inline formula. `CreditLedgerService.EstimatePriceBandAsync` must be the only place the band is computed.

### 8. `WorkflowService` — action and trigger validation

- Add one `public static class WorkflowActions` (in `WorkflowService.cs`) holding the eight action names as constants plus an `All` set, and one `WorkflowTriggers` holding `"On Manual Click"`.
- `AddStepAsync` and `UpdateStepAsync`: throw `ArgumentException` when the action is not in `WorkflowActions.All` or the trigger is not a known trigger.
- `RunStepAsync`: replace the string literals in the `switch` with the constants, and make the `default` branch throw `InvalidOperationException` instead of recording a fake "Executed action" outcome.
- Do **not** change the three Phase 3 cases (`Run MT Optimize`, `Score QPS`, `Auto-Route`) beyond swapping the literal for the constant. They must still call the stubs and surface as 501. Do not touch `MtOptimizeService.cs`, `QpsScoringService.cs` or `AutoRoutingService.cs`.

### 9. Endpoints

In the three endpoint files, add `catch` clauses so that, wherever the service can now throw them:
- `InvalidJobStateException` → 409
- `LocalizationLocaleNotFoundException` → 404
- `VendorLanguageMismatchException` → 403
- `ArgumentException` → 400

Follow the existing pattern exactly: specific `catch` blocks before the general `catch (Exception ex)`, each calling the file's own private `Problem(...)` helper. Do not extract a shared helper.

### 10. Tests

Add xUnit tests under `tests/StudyTracker.Api.Tests/Localization/`, in the style of the existing tests. Cover at least:
- post to an unknown locale → locale-not-found
- post when a job is already Open → invalid state, and no row was changed
- post after Approved → a second job row exists and the first is untouched
- bid on a non-Open job, bid in a language the vendor does not have, duplicate pending bid
- award on a non-Open job
- vendor edit on an Approved job is rejected; vendor edit on NeedsRevision moves the job to InProgress
- approve and send-back on a job that is not SubmittedForReview
- approve advances only translations that have target text, and writes exactly one ledger entry equal to the awarded bid's price
- the "Post to Marketplace" workflow action produces the same string count, word count and band as calling `PostToMarketplaceAsync` directly
- adding a workflow step with an unknown action is rejected

## Do not

- Do not add, rename or remove any entity property, table, column, DTO field or route. No EF migration.
- Do not edit `api/Data/LocalizationSeedData.cs`, `api/Program.cs` beyond what dependency injection strictly requires (it should require nothing: `MarketplaceService` is already registered), or anything under `app/`.
- Do not implement any AI logic.
- Do not reformat code you are not changing.

## Finish

Run `dotnet build api` and `dotnet test tests/StudyTracker.Api.Tests`. Then report: the list of files changed, the test results as printed, and anything in this prompt that did not match what you found in the code (do not guess around a mismatch — report it).
