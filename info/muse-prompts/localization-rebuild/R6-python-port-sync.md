# R6 — Localization Lab rebuild: bring `api-python/` back in line with the .NET API

Last step of track R. **Run it only after R1, R2 and R3 are finished**: it ports the C# they produce. Until then the port's Localization routes no longer match the .NET API; that is expected.

Authority, in this order: the C# in `api/` as it stands after R3; `info/muse-prompts/python-port/PORT-RULES.md`; `info/muse-prompts/localization-rebuild/CONTRACT.md` for the route list and JSON shapes. Do not edit the C# or the contract.

Paste everything below this line into Muse Code, opened at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. The C# in `api/` is the authority; do not edit it. The database schema is owned by the EF migrations; the port only maps it.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "R6 — Localization rebuild port" before starting the next.

## Read these first, in full

- `info/muse-prompts/python-port/PORT-RULES.md`
- `info/muse-prompts/localization-rebuild/CONTRACT.md` and `info/muse-prompts/localization-rebuild/PROGRESS.md` (what R1 to R3 built, file by file)
- `api-python/PORT-MAP.md` and `api-python/PROGRESS.md`
- In `api/`: every file under `Models/Localization/`, `Services/Localization/`, `Endpoints/Localization/`, `Options/AzureTranslatorOptions.cs`, the three R migrations in `Migrations/` and `StudyTrackerContextModelSnapshot.cs`, and the Localization registrations in `Program.cs`
- In `api-python/`: `app/models/` (Localization models), `app/services/localization/`, `app/routers/` (the Localization routers), `app/schemas/localization_dtos.py`, `app/schemas/base.py`, `app/settings.py`, `app/main.py`, `tools/parity_routes.txt`, and the Localization tests

## Task 1 — inventory

Before changing anything, write a table in `PROGRESS.md`: every C# file under the three Localization folders after R3, the Python file that ports it today (or "none"), and the action: unchanged, update, new, or delete. Include the C# files that R3 deleted (`MarketplaceService`, `CreditLedgerService`, `MarketplaceEndpoints`, `MarketplaceBid`, `GoogleTranslateProviderService`, `GoogleTranslateOptions`); their ports are deleted too.

## Task 2 — models

Map the schema as the snapshot describes it after the three R migrations: the two usage tables, the caps table, the agreement and assignment tables, the changed `localization_vendors`, `localization_projects` and `localization_marketplace_jobs` columns, the dropped bids table and columns, and the two check constraints. Table and column names come from the snapshot, never from the C# property names. The job model keeps the table name `localization_marketplace_jobs`, as the C# does.

## Task 3 — services

Port each service change one for one, keeping the C# method order and names in snake_case as the port rules say:

- `UsageMeteringService` (record, cost with rate in force, month summary, recent events, the run budget and cap checks).
- `WorkflowService`: one event per provider call, the cap and kill-switch behaviour, the renamed actions and outcome texts, the removed ledger writes, job creation through the job service.
- `TranslationJobService` (replaces the marketplace service) and the changed `VendorPortalService`.
- `AzureTranslatorProviderService` (replaces the Google one): same request shape, headers, mock rule and failure rule as the C#.
- `QpsScoringService`, the AI client result types and the exception's token fields.
- `LocalizationProjectService` (tier, AI switch).

Month boundaries, rounding (6 decimals for cost, round-down for `completedPercent`) and string comparisons must match the C# exactly; say in `PROGRESS.md` how each is matched.

## Task 4 — schemas and routers

- DTOs in `app/schemas/localization_dtos.py`: the client, vendor and operations shapes of the contract. Decimal fields use `DotNetDecimal`; timestamps use `DotNetDateTime`.
- Routers: the job routes, the changed vendor routes, the operations routes (same admin check as the port's admin router, same 403 body), the controls PUT with the absent-versus-null distinction (read the raw JSON body; a Pydantic model with optional fields cannot tell the two apart unless you inspect `model_fields_set`), and removal of every marketplace and bid route.
- Path convertors (`:int`) wherever the C# has a route constraint.
- Registration order in `app/main.py` follows `Program.cs`.
- Settings: `AzureTranslator__Endpoint`, `AzureTranslator__Key`, `AzureTranslator__Region`; remove the Google key.

## Task 5 — parity list and map

- `tools/parity_routes.txt`: remove the marketplace, bid and old vendor lines; add one line per new route with a body that is valid against the seed data (job create for a seeded locale, approve and send-back for job 1, vendor jobs for vendor 1, the operations routes). Rename `GoogleMT` to `AzureTranslator` in the provider-health lines. Update the header counts. The operations routes answer 403 without a signed-in admin on both sides; say so in a comment above them, as the existing comments do for other signed-in routes.
- `api-python/PORT-MAP.md`: update the Localization section to the new files and routes.

## Task 6 — tests

Port the C# tests that R1 to R3 added or changed in `tests/StudyTracker.Api.Tests/Localization/`, case for case, and delete the Python tests for bidding, awarding and price bands. Database tests keep using `PY_SCRATCH_DATABASE_URL`. Update the endpoint-mapping test that compares route tables. List every test added, changed and deleted.

## Finish

End with a short report: the inventory table, each task done or not done, files created, changed and deleted, how month boundaries and rounding are matched, and anything in the C# you could not port as written. Never say a test or check passes; you have not run it.
