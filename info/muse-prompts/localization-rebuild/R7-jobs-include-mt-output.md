# R7 — Jobs include machine output for vendor post-editing (.NET backend + React)

Owner decision, 12 Nov 2026: machine-translated strings go to the vendor team for post-editing. Until now a job only covered strings with no translation, so once "Auto-Translate via Azure Translator" had filled a locale, "Create Translation Jobs" skipped it and vendors never saw machine output.

The contract was amended for this: `info/muse-prompts/localization-rebuild/CONTRACT.md`, section 2.5 ("Job scope", "vendor-reviewed", `completedPercent`) and section 3 (PUT and submit rules, `inJob`, `vendorReviewed`, the "machine steps never overwrite vendor work" rule). Those paragraphs are the authority; do not edit the contract.

Run after R1-R5 (committed). Independent of C17. R8 ports this to `api-python/` afterwards.

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository: ASP.NET Core 8 API in `api/`, xUnit tests in `tests/StudyTracker.Api.Tests/`, React app in `app/`. For this task you may edit files under `api/`, `tests/StudyTracker.Api.Tests/` and `app/src/`.

Do not touch `api-python/`, `localization-ai/`, migrations, the model snapshot, compose files, `.env*`, deploy scripts or workflows. No schema change is needed: everything below is computed from existing columns. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `info/muse-prompts/localization-rebuild/PROGRESS.md` under "R7".

## Read these first, in full

- `info/muse-prompts/localization-rebuild/CONTRACT.md` sections 2.5 and 3
- `api/Services/Localization/TranslationJobService.cs`
- `api/Services/Localization/VendorPortalService.cs`
- `api/Services/Localization/WorkflowService.cs` (the `RunMtOptimize`, `ScoreQuality` and `AutoRoute` branches)
- `api/Services/Localization/LocalizationDtos.cs` (the vendor string row DTO)
- `app/src/pages/Localization/Vendor/VendorMyJob.jsx`, `app/src/pages/Localization/LocalizationJobs.jsx`
- `tests/StudyTracker.Api.Tests/Localization/TranslationJobServiceTests.cs`, `VendorPortalServiceTests.cs`, `LocalizationTestFixture.cs`

## Task 1 — one definition of "open" and "vendor-reviewed"

Add a small static class `JobScope` in `api/Services/Localization/` (new file `JobScope.cs`) with:

- `public const string VendorSource = "Marketplace";` and `public const string MachineSource = "AI";`
- `static bool IsOpen(LocalizationString s, string localeCode)`: true when the string has no translation for the locale, or that translation's `TargetText` is blank, or its `Stage` is not `"Approved"`.
- `static bool IsVendorReviewed(LocalizationTranslation? t)`: `t != null && t.TranslationSource == VendorSource && !string.IsNullOrWhiteSpace(t.TargetText)`.
- `static int CompletedPercent(IEnumerable<LocalizationString> strings, string localeCode, int stringCount, string jobStatus)`: CONTRACT 2.5 exactly. `"Approved"` gives 100; `stringCount == 0` gives 0; otherwise count the strings whose translation for the locale is vendor-reviewed and not `Approved`, `* 100 / stringCount` (integer division), capped at 100.

Replace the two private `CompletedPercent` methods (in `TranslationJobService` and `VendorPortalService`) with calls to `JobScope.CompletedPercent`, and use `JobScope.VendorSource` where `VendorPortalService` writes `"Marketplace"` today.

## Task 2 — job creation and the jobs list

In `TranslationJobService`:

1. `GetJobsForProjectAsync`, `NotCreated` rows: `stringCount`/`wordCount` over the open strings (`JobScope.IsOpen`) instead of the untranslated ones; `completedPercent` 0.
2. Rows for existing jobs: `completedPercent` from `JobScope.CompletedPercent(..., job.Status)`.
3. `CreateJobAsync`: the job's `StringCount`/`WordCount` are taken over the open strings. The "nothing left to translate" 409 fires only when there are no open strings. Keep every other rule (team check, existing-job check) as it is.
4. `CountWords` is unchanged.

## Task 3 — the vendor portal

In `VendorPortalService`:

1. Vendor string row DTO: add `bool InJob` and `bool VendorReviewed` as the last two fields (JSON `inJob`, `vendorReviewed`). `InJob = JobScope.IsOpen(str, job.LocaleCode)`; `VendorReviewed = JobScope.IsVendorReviewed(translation)`. Update every place that builds the row.
2. Update string (the PUT): if the existing translation's stage is `"Approved"`, throw `InvalidJobStateException` (409) with the message "String {stringId} is already approved for {localeCode}." Otherwise behave as today. Sending the same text that is already there is allowed and still sets the source to `JobScope.VendorSource`: that is how a vendor accepts a machine draft. Leave `RawMtText` and the scores as they are.
3. Submit: keep the "every string has non-blank text" rule, and add: if any string of the locale is open and its translation's source is `JobScope.MachineSource`, throw `InvalidJobStateException` with "{n} machine-translated strings still need review before the job can be submitted." where `n` is that count.
4. Job rows (`VendorJobRowAsync` and the list): `completedPercent` from `JobScope.CompletedPercent(..., job.Status)`.

## Task 4 — machine steps never overwrite vendor work

In `WorkflowService.RunStepAsync`:

1. `RunMtOptimize`: today it acts on every translation with a non-blank `RawMtText`, so it would overwrite text a vendor has edited. Skip any translation whose `TranslationSource` is not `"AI"` or whose `Stage` is `"Approved"`; such strings are not counted as optimized, failed or skipped.
2. `ScoreQuality` and `AutoRoute`: they already require `TranslationSource == "AI"`; add the same `Stage != "Approved"` condition.

Do not change the outcome text formats.

## Task 5 — React: vendor workspace and jobs page

`app/src/pages/Localization/Vendor/VendorMyJob.jsx`:

1. For each row with `inJob` true and `vendorReviewed` false and non-blank `targetText`, show an "Accept draft" button in the ACTION column. It calls the existing update-string API with the row's current `targetText`, then refreshes the row from the response. Disable it while the request runs. Match the style of the existing row action button in this file.
2. Show a small "Reviewed" label on rows where `vendorReviewed` is true, and nothing extra for rows with `inJob` false (approved). Keep the score grouping and filters as they are.
3. In the header, show "{reviewed} of {inJob} strings reviewed", counting from the rows.
4. When submit returns 409, show the server's detail text in the page's existing error area (as the page already does for other 409s; if it does not, use the same pattern as `LocalizationWorkflow.jsx` uses for `err.problemDetails?.detail || err.message`).

`app/src/pages/Localization/LocalizationJobs.jsx`: no logic change needed. If the page has explanatory text saying a job covers untranslated strings, change it to "One job per locale covers every string not yet approved, including machine drafts for the vendor team to post-edit."

Update `app/src/__tests__/components/VendorMyJob.test.jsx`: a row with `inJob: true, vendorReviewed: false` shows "Accept draft", and clicking it calls the update API with the row's text; a reviewed row shows "Reviewed" and no button; a submit 409 shows the detail.

## Task 6 — .NET tests

Add to `TranslationJobServiceTests.cs` / `VendorPortalServiceTests.cs` (use the fixture; write `Microsoft.Extensions.Options.Options.Create(...)` in full if you need options):

1. A locale where every string has an `"AI"` translation at stage `"Translated"`: `CreateJobAsync` succeeds and `StringCount` equals the number of strings. Before this change it threw.
2. A locale where every string is `Approved`: `CreateJobAsync` throws the "nothing left to translate" exception.
3. The `NotCreated` row counts open strings: two strings, one `Approved`, one `AI`/`Translated` gives `stringCount` 1.
4. `completedPercent`: 4 open strings, 1 accepted by the vendor gives 25; the job approved gives 100.
5. Accepting a draft: PUT with the same text sets `TranslationSource` to `"Marketplace"`, keeps `RawMtText`, flips `VendorReviewed` to true, and moves an `Assigned` job to `InProgress`.
6. PUT on an `Approved` string: 409.
7. Submit with one unreviewed `"AI"` open string: 409 whose message contains "1 machine-translated strings still need review"; after accepting it, submit succeeds.
8. `RunMtOptimize` does not change a translation whose source is `"Marketplace"` even though it has `RawMtText` (use the existing fake optimizer and assert its call count and the text).

Then fix any existing test that relied on the old rules (untranslated-only scope, old `completedPercent`, submit without review). List each edit and why.

## Finish

End with a short report: each task done or not done, every file created or changed, the existing tests you edited and why, and anything that could not be done as written. Never say a build or test passes; you have not run it.
