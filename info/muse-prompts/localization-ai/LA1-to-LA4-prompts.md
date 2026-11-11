# Localization AI service (Python) — prompts LA1 to LA4

The AI layer of the Localization Lab: MT Optimize, QPS scoring, Auto-Routing, semantic cache, glossary grounding and the eval harness, as a separate Python FastAPI service in a new top-level folder `localization-ai/`.

Design source: `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md`, Parts B.2, E and F. One decision in that document is reversed by the owner: Part F.3 says the prompt, parsing, routing, cache and eval logic are hand-written. **The owner has now asked for all of it to be implemented.** Everything else in the document stands.

Order: LA1 → LA2 → LA3 → LA4. LA1, LA2 and LA3 can run while the localization fixes L1–L3 are in progress. LA4 edits files that L1 and L2 also edit, so it runs only after both are merged.

Paste **one** block (between two `=====` lines) per Muse session, at the repository root.

=====

## LA1 — Schema for the AI layer (.NET migration)

You are working in the `scaler-education-journey` repository (ASP.NET Core 8 + EF Core + PostgreSQL in `api/`). The repo's `CLAUDE.md` is addressed to a different assistant; for this task you may edit only the files named below.

Read first: `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Part B (all of it), every file in `api/Models/Localization/`, `api/Data/StudyTrackerContext.cs`, the newest two files in `api/Migrations/`, `api/Data/LocalizationSeedData.cs`, `ai-agent/migrations/001_enable_pgvector_extension.sql`, and `api/StudyTracker.Api.csproj`.

Add exactly the schema in Part B.2, following the conventions of the existing Localization entities (attributes, snake_case columns, `localization_` table prefix, navigation properties with `[JsonIgnore]`):

- `LocalizationTranslation`: add nullable `RawMtText`, `RawMtQpsScore`, and nullable `CometKiwiScore` (decimal).
- `LedgerEntry`: add nullable `UnitsConsumed`, `UnitType`, `RealCostUsd`.
- `LocalizationProject`: add `QpsThreshold` (int, default 70).
- New entities: `GlossaryTerm`, `TranslationCacheEntry`, `EvalGoldenCase`, `EvalRun`, `EvalCaseResult`, with the fields listed in B.2. `EvalCaseResult` also gets `CacheHit` (bool?) and `CostUsd` (decimal?).
- `TranslationCacheEntry.SourceEmbedding` is a pgvector column. Check whether the project already references a pgvector EF package. If it does, use it. If it does not, do not add a package: declare the column in the migration with raw SQL (`vector(384)`) plus an HNSW cosine index, and leave it unmapped in the entity with a comment saying the Python service is the only reader and writer of that column. The migration must run `CREATE EXTENSION IF NOT EXISTS vector` first.
- Add the `DbSet` lines and any Fluent configuration next to the existing Localization ones.
- Generate the migration with `dotnet ef migrations add AddLocalizationAiLayer --project api`. Do not hand-write the designer or snapshot files.

Seed (`LocalizationSeedData.cs`): the existing seeder only runs when there are no projects. Add a second, separately guarded block (`if (!context.LocalizationGlossaryTerms.Any())`) that inserts about 25 glossary terms for the `auroraline-hud-v3` project across its five locales (automotive HUD terminology; include terms that must stay untranslated, such as "HUD" and "ABS"). Do not seed golden eval cases here; LA2 owns them.

Do not edit any service, endpoint or frontend file. Do not change existing columns.

Finish: `dotnet build api`, `dotnet test tests/StudyTracker.Api.Tests`, and apply the migration to the local database with the repo's documented `--migrate` flow. Report the files changed, the command output, and the generated SQL for the new tables.

=====

## LA2 — Service scaffold, model provider, eval harness first

You are working in the `scaler-education-journey` repository. The repo's `CLAUDE.md` is addressed to a different assistant; for this task you may create and edit files only under a new top-level folder `localization-ai/`, plus one new compose override file `docker-compose.localization-ai.yml` at the repo root.

Read first: `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Parts B.2, E and F; `info/localization-design/specs/localization-lab-ai-vertical-flow.md`; the entities in `api/Models/Localization/` (after LA1); `ai-agent/requirements.txt`, `ai-agent/config.py`, `ai-agent/Dockerfile` and `ai-agent/auth.py` for the house style of the existing Python service; `docker-compose.yml` and `docker-compose.dev.yml`.

The design is eval-harness-first: the golden set and the metric runner exist and pass before any translation logic is written. Build that foundation in this step.

Stack: Python 3.12, FastAPI, Pydantic v2, pydantic-settings, `psycopg` 3 with a connection pool (as `ai-agent` uses), `httpx`, `pytest`, `ruff`, `mypy`. Pin versions; reuse the versions `ai-agent/requirements.txt` pins where the package is the same. No LangChain or other orchestration framework: the pipeline is linear and should be readable as plain functions.

Build:

1. Layout: `app/main.py`, `app/settings.py`, `app/db.py`, `app/auth.py` (shared-secret header check, same idea as the .NET `x-api-key`), `app/providers/`, `app/pipeline/`, `app/evals/`, `app/routers/`, `tests/`, `evals/golden/`, `Dockerfile`, `README.md`.
2. **Model provider** (`app/providers/`): a small `ChatProvider` protocol and an `EmbeddingProvider` protocol. Implementations: (a) an OpenAI-compatible HTTP client (`/v1/chat/completions`, `/v1/embeddings`) whose base URL, API key and model names come from settings, so it works against a self-hosted vLLM server or any compatible endpoint; (b) a deterministic fake of each, used by every test and selectable in settings for running the service with no model at all. Every call returns token counts and latency. No model name is hard-coded outside settings.
3. **Database access**: the schema is owned by the .NET EF migrations. This service creates no tables. It reads glossary terms, golden cases and project settings, and it is the reader and writer of `translation cache`, `eval run` and `eval case result` rows. Use the real table and column names from the LA1 migration.
4. **Golden set** (`evals/golden/*.jsonl` plus a loader that upserts them into the golden-case table): 40 cases spread over the five locales and the four categories in Part E.1 (`short-label`, `warning-message`, `idiomatic`, `legal-disclaimer`), with at least eight cases containing placeholders such as `{count}` or `{speed}`, and at least ten that use a seeded glossary term. Mark every case `"verified": false`; the owner will check the gold translations by hand, and the README must say so plainly.
5. **Deterministic metrics** (`app/evals/metrics.py`), each a pure, unit-tested function: glossary adherence, placeholder preservation, exact/normalised match against gold, latency and cost aggregation.
6. **COMET-Kiwi** (`app/evals/comet.py`): an optional scorer behind an extra requirements file (`requirements-comet.txt`). When the package or model is not installed the scorer reports "unavailable" and the run records null for that metric; nothing else fails. Document in the README how to install it and that the model download needs a Hugging Face licence acceptance.
7. **Metric runner** (`app/evals/runner.py`) and `POST /run-eval`: for a `pipelineConfig`, run every golden case through the pipeline function registered for that config, compute the metrics, and write one eval-run row and one case-result row per case. In this step register only `legacy-only`, which takes the raw MT text as the output with no LLM call. The other configs are registered in LA3.
8. `GET /health`. Compose override adding the service on an internal port, same network and database as `api`.

Tests: everything runs with the fake providers and needs no network. Include a test that runs the whole `legacy-only` eval against a test database and checks the stored aggregate values by hand-computed expectation.

Finish: `ruff check`, `ruff format --check`, `mypy app`, `pytest`. Report files created, command output, and one sample eval-run row.

=====

## LA3 — The pipeline: cache, MT Optimize, QPS, Auto-Route

You are working in `localization-ai/` in the `scaler-education-journey` repository, on top of LA2. You may edit only files under `localization-ai/`.

Read first: `localization-ai/README.md` and the code from LA2; `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Parts E and F.

Implement the pipeline of Part E.5 and the endpoints of Part F.2. Each stage is one module in `app/pipeline/` with one public function, a docstring stating its inputs, outputs and failure behaviour, and its own tests.

1. **Semantic cache** (`cache.py`): embed the source text, cosine-search the cache table within the same project and locale, treat similarity at or above a configurable threshold (default 0.95) as a hit, increment the hit count, and on a miss store the new translation after it has been produced. Include a test set of near-duplicate pairs that must hit and "looks similar, means something different" pairs that must not (for example "Turn left" / "Turn right", "Door open" / "Door closed"), and report the threshold at which they separate.
2. **MT Optimize** (`mt_optimize.py`): build a post-edit prompt from the source text, the raw MT text, the target locale and only the glossary terms that actually occur in the source. Source and raw MT text are untrusted input: place them in clearly delimited data blocks and instruct the model to treat them as text to translate, never as instructions. Ask for structured JSON output; validate it with Pydantic; on malformed output retry once with the validation error, then fall back to the raw MT text and record the fallback. After the model answers, run deterministic checks (placeholders preserved, glossary terms present, output not empty, output not identical to the source for a different language) and record each result.
3. **QPS scoring** (`qps.py`): a separate judge call that scores accuracy, fluency, terminology and tone, each 0–25 with a one-line justification, summed to 0–100, plus a list of flagged issues. The judge never sees which system produced the translation. Structured output, validated, same retry rule. Include a calibration test file of hand-written good and bad translations with expected score bands, runnable against a real model with a flag and skipped by default.
4. **Auto-Route** (`auto_route.py`): `needs_review` is true when the score is below the project threshold, or when any deterministic check from step 2 failed regardless of score. One pure function, table-driven tests.
5. **Endpoints** exactly as Part F.2: `POST /translate-and-optimize`, `POST /qps-score`, `POST /comet-score`, `POST /auto-route`, and `POST /run-eval` extended with the configs `legacy+optimize`, `legacy+optimize+glossary` and `legacy+optimize+glossary+cache`. Every response includes tokens used, latency and whether a fallback occurred.
6. **Cost**: settings hold a price per 1,000 input and output tokens for each configured model and a price per character for legacy MT. Every pipeline call returns a computed cost; eval runs sum it.
7. **Report** (`app/evals/report.py` and a CLI entry): print the comparison table across the stored eval runs for a project (one row per config; columns for each metric), which is the baseline-to-delta table of Part F.6.

Prompts live in `app/pipeline/prompts/` as plain text templates, one file per prompt, with a version string that is stored on every eval run so results can be tied to the prompt that produced them.

Tests run with the fake providers. The fake chat provider must be scriptable per test (return this JSON, return malformed output, raise a timeout) so every branch above is covered.

Finish: `ruff check`, `ruff format --check`, `mypy app`, `pytest`. Run all four eval configs with the fake providers and paste the comparison table. State clearly that these numbers come from the fake provider and mean nothing about quality until the owner points the service at a real model.

=====

## LA4 — Wire the .NET API and the Strings page to the service

Run only after L1, L2 and LA3 are merged.

You are working in the `scaler-education-journey` repository. The repo's `CLAUDE.md` is addressed to a different assistant; for this task you may edit only the files named below.

Read first: `localization-ai/README.md` and its routers; `api/Services/Localization/WorkflowService.cs`, `MtOptimizeService.cs`, `QpsScoringService.cs`, `AutoRoutingService.cs`, `IQualityScorer.cs`, `CreditLedgerService.cs`, `LocalizationDtos.cs`, `LocalizationStringService.cs`; `api/Services/LlamaApiClient.cs` and `api/Options/LlamaApiOptions.cs` for the house pattern of an outbound HTTP client; the Localization registrations in `api/Program.cs`; `app/src/pages/Localization/LocalizationStrings.jsx` and `app/src/components/Localization/StageIndicator.jsx`; `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md` Parts E.5, F.1, F.4, F.6 and `localization-lab-ai-vertical-flow.md` §2–§3.

Backend:

1. `api/Options/LocalizationAiOptions.cs` (`SectionName = "LocalizationAi"`: base URL, shared secret, timeout, price settings) and `api/Services/Localization/LocalizationAiClient.cs`, a typed `HttpClient` with one method per service endpoint. Register both in `Program.cs` next to the existing Localization registrations. When the base URL is not configured, the three Phase 3 actions keep returning 501 with a message saying the AI service is not configured.
2. Replace the bodies of `MtOptimizeService`, `QpsScoringService` and `AutoRoutingService` with calls to the client. Keep the class names, method signatures and the `IQualityScorer` interface. They contain no prompt, scoring or threshold logic; that stays in the Python service.
3. `WorkflowService.RunStepAsync`:
   - `Auto-Translate via Google MT`: also store the provider output in `RawMtText`, and write one ledger entry per run with `Source = "AI"`, `UnitType = "characters"`, the character count, and `RealCostUsd` from the configured rate.
   - `Run MT Optimize`: for every translation that has `RawMtText`, send the source, raw text, locale and that locale's glossary terms; write the result to `TargetText`; one ledger entry per run with `UnitType = "tokens"`.
   - `Score QPS`: score every translation whose `TranslationSource` is `AI` and store `QpsScore`; also score the raw text once into `RawMtQpsScore` when it is null.
   - `Auto-Route`: for every AI translation with a score, call the service with the project's `QpsThreshold` and set `NeedsReview`.
   - Remove the placeholder arguments (`"sample"`, `"de-DE"`, `85`, `70`). Outcome text states how many strings were processed and how many were flagged.
   - A failure of the AI service for one string must not abort the run: count it, continue, and include the failure count in the outcome.
4. Add `rawMtText`, `rawMtQpsScore` to `LocalizationStringRowDto` (new optional fields at the end; do not reorder existing ones).
5. xUnit tests with a fake `HttpMessageHandler`: each of the three actions, the not-configured 501 path, the partial-failure path, and the ledger entries.

Frontend (`LocalizationStrings.jsx` only, plus a new component file if needed):

6. In the drawer, when the row has `rawMtText`, show a read-only "Legacy MT" box above the target box with its QPS score, so the before and after are visible together.
7. Add the "Needs Review only" filter described in `localization-lab-ai-vertical-flow.md` §3.1: a small toggle near the table header that filters the visible rows.

Do not change routes, the vendor portal, or the marketplace code. One EF migration is not needed; LA1 already added the columns.

Finish: `dotnet build api`, `dotnet test tests/StudyTracker.Api.Tests`, `npm run lint` and `npm run build` in `app/`. Then start the stack with the localization-ai service using its fake provider, run the four workflow actions in order from the Workflow tab, and report what the Strings page shows. Report files changed and all command output.
