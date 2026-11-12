# R2 — Localization Lab rebuild: usage caps, kill switch, Azure Translator (.NET backend)

Second backend step of track R. **Run it only after R1 has been reviewed and committed**: it edits the same files.

Authority for every route, field name and fixed string: `info/muse-prompts/localization-rebuild/CONTRACT.md` (sections 1, 2.1, 2.3, 4.1, 4.3 and 5). Do not edit the contract.

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository (ASP.NET Core 8 minimal API in `api/`, xUnit tests in `tests/StudyTracker.Api.Tests/`). For this task you may edit files under `api/` and `tests/`.

Work only in `api/` and `tests/StudyTracker.Api.Tests/`. Do not touch `app/`, `api-python/`, `localization-ai/`, compose files, `.env*`, deploy scripts or workflows. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `info/muse-prompts/localization-rebuild/PROGRESS.md` under "R2" before starting the next.

Line numbers below are from before R1 and will have moved. Find code by the names given.

## Read these first, in full

- `info/muse-prompts/localization-rebuild/CONTRACT.md`
- `info/muse-prompts/localization-rebuild/PROGRESS.md` (what R1 built)
- `api/Services/Localization/WorkflowService.cs`, `UsageMeteringService.cs`, `GoogleTranslateProviderService.cs`, `ProviderHealthService.cs`
- `api/Options/GoogleTranslateOptions.cs`, `api/Options/LocalizationAiOptions.cs`
- `api/Data/LocalizationSeedData.cs`
- `api/Endpoints/Localization/UsageEndpoints.cs`, `LocalizationEndpoints.cs`
- The R1 migration and the model snapshot in `api/Migrations/`

## Task 1 — caps and the kill switch: model

1. `LocalizationProject`: add `AiEnabled` (`ai_enabled`, bool, not null). C# default `true`.
2. New entity `LocalizationUsageCap`, table `localization_usage_caps`: `Id`; `ProjectId` (FK, cascade); `Kind` (varchar(30), required: `"machine-translation"` or `"llm"`); `MonthlyLimit` (`monthly_limit`, bigint); `UpdatedAt`. Unique index `ux_localization_usage_caps_project_kind` on `(ProjectId, Kind)`. Constants in a `UsageCapKinds` class beside the R1 constants.
3. Hand-write migration `20261112130000_AddLocalizationUsageControls` with its designer and the snapshot update. `Up` adds the column with `defaultValue: true` for existing rows (as the `qps_threshold` column was added in `20261111140209_AddLocalizationAiLayer`), creates the table and index. `Down` reverses it.
4. `LocalizationSeedData`: the demo project gets caps of 2,000,000 machine-translation characters and 5,000,000 llm tokens. The seeder only runs on an empty localization dataset; add a separate idempotent "ensure" step, called from the same place the seeder is called, that inserts the two cap rows for the demo project when they are missing, so an existing database gets them too.

## Task 2 — caps and the kill switch: behaviour

In `UsageMeteringService` add:

- `Task<UsageBudget> BeginRunAsync(int projectId, DateTime nowUtc, CancellationToken ct)`: loads the project's caps and this UTC month's used totals per cap kind (rules in CONTRACT section 5) in at most two queries, and returns an in-memory `UsageBudget`.
- `UsageBudget` (a small class in the same file): `bool CanSpend(string capKind, int knownUnits)` and `void Spent(string capKind, int units)`. For `"machine-translation"`, `CanSpend` is false when `used + knownUnits > limit`. For `"llm"`, call it with `knownUnits = 0`; it is false when `used >= limit`. No cap row means always true. It also exposes `Used(kind)` and `Limit(kind)` for messages.
- `RecordAsync` stays as it is; the workflow calls `budget.Spent(...)` with the same units right after recording (cache hits spend 0).

In `WorkflowService.RunStepAsync`, for the four provider actions (machine translation, MT Optimize, QPS scoring, Auto-Route):

1. If `project.AiEnabled` is false: throw a new `LocalizationAiDisabledException(projectSlug)`. Map it in `LocalizationEndpoints` to **409** with title "AI assistance is switched off" in the existing problem shape. Auto-Route is included even though it makes no model call: it is part of the AI pipeline.
2. For the three actions that call a provider: get the budget once at the start of the branch. If the cap for that action's kind is already reached before the first call, throw `LocalizationUsageCapReachedException(kind, used, limit)`, mapped to **409** with title "Monthly usage cap reached" and a detail naming kind, used and limit.
3. Inside the loops, before each provider call, ask `CanSpend`. When it is false, do not call the provider, leave the string as it is, count it as skipped, and continue the loop without making further calls of that kind.
4. Outcome text when `skipped > 0`: the normal outcome followed by `, {skipped} skipped: monthly {kind} cap reached ({used} of {limit})`. Exact wording is in CONTRACT 2.3.

When `UsageMeteringService` is null (old tests), there is no budget and nothing is capped, as in R1.

## Task 3 — controls endpoints and the usage summary

Add to `UsageEndpoints.cs` (same admin check as R1):

- `GET /api/localization/ops/projects/{slug}/controls`
- `PUT /api/localization/ops/projects/{slug}/controls`

Shapes and rules: CONTRACT 4.3. The PUT body distinguishes "field absent" from "field present and null": read the body as a `JsonElement` (or a `JsonNode`) and check each property with `TryGetProperty`, because a nullable record property cannot tell the two apart.

Add the `caps` array to the usage summary when a project is given (CONTRACT 4.1).

`LocalizationProjectDto` gets `bool AiEnabled` and `string? Tier` as trailing fields (CONTRACT 2.1). `Tier` is always null in this step; R3 fills it. Update `LocalizationProjectService` and every place that constructs the DTO.

## Task 4 — Azure Translator replaces Google Translate

1. New `api/Options/AzureTranslatorOptions.cs`, section `AzureTranslator`: `Endpoint` (default `https://api.cognitive.microsofttranslator.com`), `Key`, `Region`.
2. New `api/Services/Localization/AzureTranslatorProviderService.cs` implementing `ITranslationProvider`, modelled on `GoogleTranslateProviderService`:
   - Request: `POST {Endpoint}/translate?api-version=3.0&from={source}&to={target}` with headers `Ocp-Apim-Subscription-Key: {Key}` and, when `Region` is not empty, `Ocp-Apim-Subscription-Region: {Region}`; body `[{"Text": "<source text>"}]`.
   - Response: `[{"translations":[{"text":"…","to":"…"}]}]`; return the first translation's text.
   - Locale codes are passed as stored (`de-DE`, `zh-CN`). Do not invent a mapping table; say in the report that Azure's handling of each of the five seeded locale codes must be checked against a real key.
   - No key: same rule as the Google service. In production throw the same kind of configuration error with an Azure message; otherwise log a warning and return `[MOCK-{TARGET}] {sourceText}`.
   - A failed call outside production falls back to the mock text, as the Google service does; in production it throws.
   - The key goes in a header, never in the URL or a log line.
3. `Program.cs` (the Localization DI block): register the options and an `HttpClient` for the new service, and bind `ITranslationProvider` to it. Remove the Google registrations.
4. Delete `GoogleTranslateProviderService.cs` and `GoogleTranslateOptions.cs`. Search `api/` and `tests/` for every remaining reference to either, including `appsettings*.json`; `appsettings*.json` may be edited to rename the section, but add no secret values. Compose files and `.env*` are not yours to edit: list in the report the environment variable names the owner must add (`AzureTranslator__Key`, `AzureTranslator__Region`, optionally `AzureTranslator__Endpoint`) and the Google one to remove.
5. `LocalizationAiOptions.LegacyMtPricePerCharUsd` stays; it is still used by the legacy ledger write.

## Task 5 — rename the action and the provider-health row

Fixed strings: CONTRACT section 1.

1. `WorkflowActions`: rename the constant `AutoTranslateViaGoogleMt` to `AutoTranslateViaAzureTranslator` with the value `"Auto-Translate via Azure Translator"`. Update every use and the list of valid actions.
2. Outcome text: `"{n} strings translated via Azure Translator"`.
3. `ProviderHealthService`: the special case on the provider name `"GoogleMT"` becomes `"AzureTranslator"`. `LocalizationSeedData`: the seeded health row's `Provider` becomes `"AzureTranslator"`.
4. Existing databases hold the old strings. In the R2 migration's `Up`, after the schema changes, add two `migrationBuilder.Sql(...)` statements: update `localization_workflow_steps.action` from the old to the new value, and `localization_provider_health.provider` from `'GoogleMT'` to `'AzureTranslator'`. Read the two table and column names from the snapshot; do not guess them. `Down` reverses both.

Do **not** rename "Post to Marketplace" or "Score QPS" in this step; R3 does that.

## Task 6 — tests

1. Cap already reached: the run throws the cap exception and makes no provider call (use a counting fake provider).
2. Machine-translation cap reached part-way: exactly the strings that fit are translated; the rest are untouched; the outcome ends with the skipped clause with the right numbers; the events recorded sum to no more than the limit.
3. Llm cap: the call that crosses the limit completes and is recorded; no call is made after it.
4. No cap row: nothing is skipped.
5. `AiEnabled = false`: each of the four provider actions throws the disabled exception; "Mark Translated" still runs.
6. Controls PUT semantics at the service level: absent field unchanged; explicit null removes the cap; a number sets it; negative is rejected.
7. Azure provider with a fake `HttpMessageHandler`: the request URL, headers and body are as specified; the response is parsed; no key outside production returns the mock text; no key in production throws.
8. Update existing tests that name the Google provider, the old action string or the old outcome text. List each edit.

## Not in this prompt

Agreements, teams, jobs, removal of the marketplace and credits, and the score scale (all R3). The React app (R4). `api-python/` (R6).

## Finish

End with a short report: each task done or not done, every file created, changed or deleted, the environment variables the owner must set or remove, the existing tests you edited and why, and anything that could not be done as written. Never say a build or test passes; you have not run it.
