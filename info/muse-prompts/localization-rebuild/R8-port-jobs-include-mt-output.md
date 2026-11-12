# R8 — api-python: port R7 (jobs include machine output)

Run **after C17** (`info/muse-prompts/corrections/C17-api-python-track-r.md`) **and after R7**: it ports R7's C# to the Python port and edits the same files C17 does.

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository. Edit files under `api-python/` only. Do not touch `api/`, `app/`, `localization-ai/`, `tests/StudyTracker.Api.Tests/`, compose files, `.env*`, deploy scripts or workflows. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

The C# side is the reference and has already changed. Read, in full:

- `info/muse-prompts/localization-rebuild/CONTRACT.md` sections 2.5 and 3 (amended: job scope, vendor-reviewed, `completedPercent`, `inJob`, `vendorReviewed`, the PUT and submit rules, machine steps never overwrite vendor work)
- `info/muse-prompts/localization-rebuild/R7-jobs-include-mt-output.md` and the "R7" section of `info/muse-prompts/localization-rebuild/PROGRESS.md`
- the C# files R7 changed: `api/Services/Localization/JobScope.cs`, `TranslationJobService.cs`, `VendorPortalService.cs`, `WorkflowService.cs`, `LocalizationDtos.cs`, and the R7 tests in `tests/StudyTracker.Api.Tests/Localization/`
- their Python counterparts under `api-python/app/services/localization/`, `api-python/app/schemas/localization_dtos.py`, and the tests under `api-python/tests/`

## Tasks

1. Add `app/services/localization/job_scope.py` mirroring `JobScope.cs` (constants `VENDOR_SOURCE = "Marketplace"`, `MACHINE_SOURCE = "AI"`; `is_open`, `is_vendor_reviewed`, `completed_percent`). Replace the two `_completed_percent` helpers with it. Integer division and the cap at 100 must match C#.
2. `translation_job_service.py`: the R7 Task 2 changes (open-string scope for `NotCreated` rows and job creation, `completed_percent` with the job status).
3. `vendor_portal_service.py` and the vendor string row schema: `in_job` and `vendor_reviewed` (JSON `inJob`, `vendorReviewed`, last two fields, same order as C#); the PUT 409 on an approved string; the submit 409 with the exact C# message; job rows use the new percent. Error messages must be character-for-character the C# ones.
4. `workflow_service.py`: the R7 Task 4 filters on "Run MT Optimize", "Score Quality" and "Auto-Route".
5. Port the eight R7 tests (same names in snake_case) and update any existing Python test the C# side had to update, listing each.
6. Append what you did under "R8 — jobs include machine output" in `api-python/PROGRESS.md`.

## Finish

End with a short report: each task done or not done, every file created or changed, the tests you edited and why, and anything that could not be ported as written. Never say a test or lint passes; you have not run them.
