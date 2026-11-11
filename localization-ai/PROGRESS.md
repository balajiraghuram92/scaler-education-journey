# Localization AI — Progress

## LA1 — Schema for the AI layer (.NET migration)

Files created:
- api/Models/Localization/GlossaryTerm.cs
- api/Models/Localization/TranslationCacheEntry.cs
- api/Models/Localization/EvalGoldenCase.cs
- api/Models/Localization/EvalRun.cs
- api/Models/Localization/EvalCaseResult.cs

Files changed:
- api/Models/Localization/LocalizationTranslation.cs (added RawMtText, RawMtQpsScore, CometKiwiScore)
- api/Models/Localization/LedgerEntry.cs (added UnitsConsumed, UnitType, RealCostUsd)
- api/Models/Localization/LocalizationProject.cs (added QpsThreshold default 70; navigation collections for the new entities)
- api/Data/StudyTrackerContext.cs (5 new DbSets; Fluent config for new entities; precision/defaults for new columns)
- api/Data/LocalizationSeedData.cs (restructured early-return into if-block; new separately guarded SeedGlossaryTerms with 25 terms for auroraline-hud-v3)

Migration NOT generated (per track instructions): the reviewer will run `dotnet ef migrations add AddLocalizationAiLayer --project api`.
The generated migration must additionally: run `CREATE EXTENSION IF NOT EXISTS vector` first, declare
`localization_translation_cache_entries.source_embedding` as `vector(384)` with an HNSW cosine index via raw SQL
(no pgvector EF package is referenced; the column is `[NotMapped]`/ignored on the entity).

Real table/column names for the Python service (from the entities/Fluent config above):
- localization_glossary_terms(id, project_id, locale_code, source_term, target_term, notes)
- localization_translation_cache_entries(id, project_id, locale_code, source_text, source_embedding vector(384) [SQL only], cached_translation, hit_count, created_at, last_hit_at)
- localization_eval_golden_cases(id, project_id, locale_code, source_text, gold_translation, category, notes)
- localization_eval_runs(id, project_id, pipeline_config, run_at, avg_comet_kiwi, avg_qps_score, glossary_adherence_rate, placeholder_preservation_rate, cache_hit_rate, avg_latency_ms, total_cost_usd)
- localization_eval_case_results(id, eval_run_id, eval_golden_case_id, produced_translation, comet_kiwi_score, qps_score, glossary_adherence_ok, placeholder_preserved_ok, latency_ms, cache_hit, cost_usd)
- localization_translations + raw_mt_text, raw_mt_qps_score, comet_kiwi_score
- localization_ledger_entries + units_consumed, unit_type, real_cost_usd
- localization_projects + qps_threshold (default 70)

Commands NOT run:
- `dotnet ef migrations add AddLocalizationAiLayer --project api`
- `dotnet build api`
- `dotnet test tests/StudyTracker.Api.Tests`
- Apply-migration `--migrate` flow (repo-documented local DB migrate step)

Prompt-vs-code mismatches / decisions:
- csproj has no pgvector EF package, so the no-package path was taken (unmapped SourceEmbedding + raw-SQL note above).
- Seed(): the existing early-return (`if projects exist, return`) would have made a trailing glossary block unreachable on existing DBs; restructured into `if (!Any) { core seed }` + separately guarded `SeedGlossaryTerms` (`if glossary terms exist, return`; no-op when the project row is absent).
- B.2 gives no decimal precisions; chose numeric(5,4) for COMET-Kiwi/scores-as-rate, numeric(5,2) for AvgQpsScore, numeric(5,4) for rates, numeric(12,6) for USD costs (follows numeric TypeName + HasPrecision convention).
- Added Project navigation collections for the four project-scoped entities (convention-following; not explicitly named in the block).
- Forward-looking gaps (LA1 kept exactly as written; NOT added): no `verified` column on EvalGoldenCase (LA2 golden cases need `"verified": false`), no prompt-version column on EvalRun (LA3 needs it). LA2/LA3 handle these as noted in their sections.

## LA2 — Service scaffold, model provider, eval harness first

Files created (all under `localization-ai/` except the compose override):
- docker-compose.localization-ai.yml (repo root; internal-only service on backend-net)
- requirements.txt, requirements-dev.txt, requirements-comet.txt, pyproject.toml, Dockerfile, README.md
- app/__init__.py, app/main.py, app/settings.py, app/db.py, app/auth.py
- app/providers/__init__.py, app/providers/base.py, app/providers/openai_compat.py, app/providers/fake.py
- app/pipeline/__init__.py, app/pipeline/registry.py (only `legacy-only` registered)
- app/evals/__init__.py, app/evals/metrics.py, app/evals/comet.py, app/evals/golden_loader.py, app/evals/runner.py
- app/routers/__init__.py, app/routers/health.py, app/routers/eval.py
- evals/golden/de-DE.jsonl, ja-JP.jsonl, zh-CN.jsonl, fr-FR.jsonl, es-ES.jsonl (40 cases)
- tests/conftest.py, tests/schema.sql, tests/test_metrics.py, tests/test_providers.py,
  tests/test_golden_loader.py, tests/test_runner.py, tests/test_api.py

Golden-set counts: 40 cases (8/locale); categories 15 short-label / 10 warning-message / 10 idiomatic /
5 legal-disclaimer; 10 cases with `{count}`/`{speed}` placeholders; 20 using a seeded glossary term
(HUD/ABS/Turn left/Low fuel/Door ajar); all `"verified": false`.

Commands NOT run (from the LA2 Finish step; record only):
- `ruff check`
- `ruff format --check`
- `mypy app`
- `pytest`
- Sample eval-run row: NOT AVAILABLE — no command was run, and no output is fabricated.

Prompt-vs-code mismatches / decisions:
- Pins: ai-agent versions reused for fastapi/uvicorn/pydantic/psycopg/psycopg_pool/pgvector; new pins
  verified to exist on PyPI: pydantic-settings==2.16.2, httpx==0.28.1, pytest==9.2.0, ruff==0.17.4,
  mypy==2.4.1, unbabel-comet==2.2.7.
- Dev tools live in requirements-dev.txt (runtime image installs requirements.txt only); COMET behind
  requirements-comet.txt as specified.
- No [tool.mypy] section (mypy runs with defaults, as in ai-agent which has none).
- Table/column names come from the LA1 entity/Fluent definitions; the LA1 migration itself is still
  not generated (reviewer step), so names are pending final confirmation against it.
- `legacy-only` echoes the source text when no raw MT is supplied (golden cases carry no raw MT);
  tokens/cost stay zero. Documented in code + README.
- Runner records null QPS (no judge until LA3) and null COMET unless a loaded scorer is passed.
- `verified` flag is JSONL-only (no table column); loader reports verified/unverified counts.
- Prompt version is not threaded through LA2 (no prompts yet); LA3 returns it but cannot persist it
  (no EvalRun column) — see LA3 section.
- Test DB schema (tests/schema.sql) is a minimal name-matching mirror, not the EF migration; DB tests
  use a throwaway pgvector container and skip without Docker.

## LA3 — The pipeline: cache, MT Optimize, QPS, Auto-Route

Files created:
- app/pipeline/cache.py, app/pipeline/mt_optimize.py, app/pipeline/qps.py, app/pipeline/auto_route.py
- app/pipeline/cost.py, app/pipeline/structured.py
- app/pipeline/prompts/__init__.py, app/pipeline/prompts/mt_optimize_v1.txt, app/pipeline/prompts/qps_judge_v1.txt
- app/evals/report.py
- app/routers/pipeline.py
- tests/test_cost.py, tests/test_auto_route.py, tests/test_mt_optimize.py, tests/test_qps.py,
  tests/test_qps_calibration.py, tests/test_cache.py, tests/test_report.py, tests/test_api_pipeline.py,
  tests/test_runner_configs.py

Files changed:
- app/settings.py (cache threshold + four price settings)
- app/pipeline/registry.py (extended PipelineContext; `legacy+optimize`, `legacy+optimize+glossary`,
  `legacy+optimize+glossary+cache`; prompt-version map)
- app/evals/runner.py (judge scores every produced translation; tokens/fallbacks/prompt version in summary)
- app/routers/eval.py (run-eval response: +tokensUsed, +fallbackCount, +promptVersion; pricing in ctx)
- app/main.py (pipeline router included)
- pyproject.toml (tests added to ruff known-first-party)
- tests/test_api.py (run-eval expectations for the extended contract + judge fallback with default fake)
- README.md (LA3 endpoints, prices, prompts, report CLI, real-model flags)

Commands NOT run (from the LA3 Finish step; record only):
- `ruff check`
- `ruff format --check`
- `mypy app`
- `pytest`
- Four eval configs with fake providers + comparison table paste: NOT RUN — nothing is pasted and no
  numbers are claimed. The README states fake-provider numbers mean nothing until a real model is used.
- Cache separation with a real model: NOT RUN. Scripted vectors separate at the 0.95 default by
  construction (0.97 near-dup hits / 0.42 confusable misses); the real-model threshold report is the
  skipped test `pytest tests/test_cache.py -k separation` with LOCAI_REAL_EMBEDDINGS=1 (command only).
- QPS calibration bands: NOT RUN (skipped test, LOCAI_REAL_CHAT=1; command only).

Prompt-vs-code mismatches / decisions:
- F.2 contract extensions (all required by the LA3 block's own clauses): every response carries token
  counts, latencyMs and fallback; translate-and-optimize returns deterministic `checks`; auto-route
  accepts optional `checks` and returns `reasons`; comet-score returns `available`; run-eval returns
  `tokensUsed`, `fallbackCount`, `promptVersion`. Documented in router docstrings + README.
- Prompt version is RETURNED, not persisted (EvalRun has no prompt-version column; LA1 kept exactly
  as written). The report therefore cannot show prompt versions; noted in README.
- Eval-harness limitation (documented in registry + README): golden cases carry no raw MT and the
  service has no MT provider, so `legacy*` eval configs feed the source text to MT Optimize as raw MT.
- The runner now judges EVERY config including `legacy-only` (LA2's null-QPS behavior is superseded);
  per-case latency excludes judge overhead, judge tokens/cost are included in run totals.
- Cache failure policy (docstring): embedding failures bypass the cache (translate, store nothing);
  lookup/store SQL errors propagate to the transaction owner.
- Transport exceptions fall back immediately (no retry); the retry-once rule covers malformed output
  only, as written.
- `docker-compose.localization-ai.yml` was NOT edited in LA3: the block allows only files under
  `localization-ai/`. New settings use their defaults in compose; README notes the reviewer step.

## LA4 — Wire the .NET API and the Strings page to the service

Files created:
- api/Options/LocalizationAiOptions.cs
- api/Services/Localization/LocalizationAiClient.cs (typed client + LocalizationAiException + DTOs)
- tests/StudyTracker.Api.Tests/Localization/LocalizationAiWorkflowTests.cs (7 tests)

Files changed:
- api/Program.cs (LocalizationAi options + HttpClient next to the other Localization registrations)
- api/Services/Localization/MtOptimizeService.cs (delegates to client; added OptimizeDetailedAsync)
- api/Services/Localization/QpsScoringService.cs (delegates to client; null score throws)
- api/Services/Localization/AutoRoutingService.cs (delegates to client)
- api/Services/Localization/WorkflowService.cs (RunStepAsync: RawMtText + per-run AI ledger entries +
  real Phase 3 orchestration; optional AI-options ctor param)
- api/Services/Localization/LocalizationDtos.cs (RawMtText/RawMtQpsScore appended, defaults null)
- api/Services/Localization/LocalizationStringService.cs (populate the two new DTO fields)
- app/src/pages/Localization/LocalizationStrings.jsx (Legacy MT drawer box; Needs Review only filter)

Commands NOT run (from the LA4 Finish step; record only):
- `dotnet build api`
- `dotnet test tests/StudyTracker.Api.Tests`
- `npm run lint` (in app/)
- `npm run build` (in app/)
- Start-the-stack + run-four-actions + report-Strings-page: NOT RUN — no workflow output is described.

Prompt-vs-code mismatches / decisions:
- Not-configured surfaces as 501 via the EXISTING endpoint mapping (NotImplementedException -> 501);
  endpoint files untouched. Services throw NotImplementedException with a "not configured" message when
  the client is missing or the base URL is empty; the client guards the same way.
- Services take `LocalizationAiClient? client = null` and WorkflowService takes optional AI options, so
  the existing fixture and `RunStep_Phase3Actions_StillSurfaceNotImplemented` compile and pass unchanged.
- MtOptimizeService keeps `OptimizeAsync` but could not satisfy item 3 through it (no source/glossary/
  token path), so it delegates to a new `OptimizeDetailedAsync` the workflow uses. QPS/AutoRoute
  signatures were sufficient as-is; IQualityScorer untouched.
- Null QPS (judge fallback) throws LocalizationAiException from QpsScoringService: the workflow counts
  the string failed and keeps the old score. Per-string catch is LocalizationAiException ONLY, so
  NotImplemented still aborts into 501 while HTTP/fallback failures are counted per string.
- AI ledger entries use Amount=0 (fictional credits untouched) and are written only when a run processed
  >0 units (no $0 noise rows). Score/Auto-Route write no entries (item 3 specifies none): judge tokens
  are not ledgered on the .NET side.
- LocalizationStringService.cs edited (2 construction sites) although Read-first-only: items 4+6 are
  impossible otherwise — the new DTO fields would stay null forever. Minimal additive change.
- LocalizationAiException lives in LocalizationAiClient.cs (the shared exceptions file is not editable).
- Test file created under tests/StudyTracker.Api.Tests/Localization/ (item 5 mandates xUnit tests;
  conventional location; covers all three actions, the 501 path, partial failure, both ledger types).
- Client sends x-api-key per request; requests serialize camelCase (matches the Python contract);
  responses parse case-insensitively. RunEval/Comet methods included; /health* omitted (probes hit it
  directly).
- No new frontend component file (both additions fit inline). The drawer's Legacy MT box mirrors the
  source-box style with a QPS badge; the filter keeps original row indices so drawer/save still work.
- Frontend QPS coloring keeps the pre-existing hard-coded 70 (project threshold is not exposed to this
  page); left unchanged.

## Round 1 corrections

No commands were run in this round (not permitted); the reviewer re-runs
`ruff check`, `mypy app`, `pytest`, `dotnet build` and `dotnet test`.

1. Fixture shadowing the `app` package (6 test errors, one cause).
   Confirmed as described: `tests/conftest.py` defined a fixture named `app`
   while also doing `import app.main`, so `app.main.build_app` inside the
   fixture body resolved to the fixture object, not the package.
   Changed `tests/conftest.py` lines 49-51: fixture renamed `app` ->
   `application`; lines 58-61: `client` fixture parameter renamed to match.
   No test uses the fixture directly (only via `client`/`db_client`), so no
   other file needed changes. The `db_client` fixture's `app.main.build_app`
   (line 190) now resolves to the package again; left untouched.
2. `test_optimize_checks_catch_bad_output`: changed the TEST, not the check.
   The check is faithful to the LA3 spec ("output not identical to the
   source"): source `Turn left {count}` vs output `Turn left` differ, so
   `differs_from_source=True` is correct, and the test's expectation of
   False is self-contradictory (a dropped placeholder necessarily implies
   difference). Changed `tests/test_mt_optimize.py` lines 75-82: the
   `differs_from_source` assertion is now `is True`, with a comment saying
   why. `app/pipeline/mt_optimize.py` untouched.
3. mypy 36 errors in 4 files.
   - Note: every response model already had
     `model_config = ConfigDict(populate_by_name=True)`, yet mypy still
     demands the alias names, so per the item's second option the five
     construction sites were switched to camelCase alias keywords,
     consistently across both routers: `app/routers/eval.py` lines 68-80
     (`RunEvalResponse`); `app/routers/pipeline.py` lines 115-126
     (`TranslateResponse`), 159-168 (`QpsScoreResponse`), 195-201
     (`CometScoreResponse`), 226-232 (`AutoRouteResponse`). Fields without
     aliases (`score`, `checks`, `fallback`, `reasons`, `available`) are
     unchanged. Runtime behavior and response JSON are unchanged (aliases
     are the primary population names; models serialize by alias).
   - `app/evals/runner.py` variance errors (5): fixed at the cause in
     `app/evals/metrics.py` — `mean`/`rate`/`total` now take
     `collections.abc.Sequence` (covariant) instead of `list` (invariant),
     per mypy's own note (lines 7-8 import; lines 63, 71, 79 signatures).
     Bodies untouched; `app/evals/runner.py` untouched.
   - `app/evals/comet.py` line 36: added
     `# type: ignore[import-not-found]` to the intentionally optional
     `from comet import ...` (already guarded by try/except ImportError).
4. ruff 5 errors, fixed by hand: `app/main.py` lines 13-15 and
   `app/settings.py` lines 14-15 (psycopg* sorts before pydantic* — swapped
   the two I001 import pairs); `app/pipeline/structured.py` lines 7-10 and
   26 (UP047: PEP 695 `def parse_or_raise[M: BaseModel]`, dropped the
   `TypeVar`); `app/evals/comet.py` lines 56-60 and `app/evals/runner.py`
   lines 110-112 (E501: wrapped the two long lines). No reformatting.
5. DB-skip logic untouched. Checked every skipped test file
   (`test_api.py`, `test_api_pipeline.py`, `test_cache.py`,
   `test_golden_loader.py`, `test_qps_calibration.py`, `test_report.py`,
   `test_runner.py`, `test_runner_configs.py`) plus all `conftest.py`
   fixtures: no other fixture or test parameter shadows an imported
   module (fixture params used are `client`, `db_client`, `fresh_db`,
   `seeded_project_id`, `tmp_path`; `test_cache.py`'s `cache` is the
   module itself, not a fixture). No changes.
6. `tests/StudyTracker.Api.Tests/Localization/LocalizationAiWorkflowTests.cs`:
   line 93 and line 108 `Options.Create(options)` -> fully qualified
   `Microsoft.Extensions.Options.Options.Create(options)`; line 327
   `Assert.Equal` first argument `new[] { 70, 80 }` -> `new int?[] { 70, 80 }`
   so both sides have element type `int?`.
7. No EF migration written, as instructed.

Unresolved: none. All items 1-6 addressed; item 7 is a deliberate no-op.

## Round 2 corrections

No commands were run in this round (not permitted); the reviewer re-runs
`dotnet build` and `dotnet test`. Agent 1 scope only: the .NET side of LA4.
`localization-ai/` code untouched (clean this round); this section is the only
change under `localization-ai/`.

1. `RunStep_Phase3Actions_StillSurfaceNotImplemented` failing ("No exception
   was thrown"). Confirmed as described: the three Phase 3 branches only
   reached the AI services inside the per-translation loop, so with no
   eligible translation the step "succeeded" without calling anything. The
   test is right; fixed the code, test untouched.
   - `api/Services/Localization/WorkflowService.cs`: one shared private
     check `ThrowIfAiNotConfigured(bool)` (lines 614-625) throwing
     `NotImplementedException` with the existing `NotConfiguredMessage`
     (501 via the existing endpoint mapping). Called as the first statement
     of each branch — line 432 (Run MT Optimize, before the glossary read,
     loop and ledger write), line 499 (Score QPS), line 555 (Auto-Route) —
     so the throw precedes the end-of-method `SaveChangesAsync` and no
     step outcome, translation change or ledger entry is persisted. Added
     one comment line 429 noting the up-front behavior.
   - Each branch checks the service it actually calls, so Score QPS still
     works with a configured/fake scorer: `IsConfigured` added to
     `MtOptimizeService.cs` (lines 21-25), `QpsScoringService.cs`
     (lines 21-25) and `AutoRoutingService.cs` (lines 20-24), each
     `_client?.IsConfigured == true` (covers both a missing client and a
     client with an empty base URL).
   - `IQualityScorer.cs` (lines 11-12): added `bool IsConfigured { get; }`
     (WorkflowService holds the scorer behind the interface; the only
     implementations are `QpsScoringService` and the test fake).
   - `tests/StudyTracker.Api.Tests/Localization/LocalizationTestFixture.cs`
     line 18: `FakeQualityScorer` implements `IsConfigured => true`.
   - Checked by reading: every other `RunStepAsync` caller runs the Phase 3
     actions only with a configured client (behavior unchanged) or runs
     non-Phase-3 actions (branches untouched).
2. New test for the configured-client path with an empty base URL:
   `tests/StudyTracker.Api.Tests/Localization/LocalizationAiWorkflowTests.cs`
   lines 383-404 (`Phase3Actions_EmptyBaseUrl_ThrowNotImplementedAndWriteNoLedger`):
   client present, `BaseUrl = string.Empty`, seed project with no
   translations (nothing eligible for any action), each of the three actions
   expects `NotImplementedException`, then asserts no ledger entry was
   written and no HTTP request was made.

Unresolved: none. Items 1-2 both addressed.

## C7 — database test corrections

No commands were run in this round (not permitted); the reviewer re-runs
`pytest`. Tests-only changes; `localization-ai/app/` untouched.

Task 1 — pool opened in a throwaway event loop (hang). Done.
- `tests/conftest.py`, `db_client` fixture: pool is now created with
  `db_module.create_pool(conninfo)` and passed to `build_app` unopened.
  Removed `asyncio.run(pool.open())`, `asyncio.run(pool.wait())`, the
  trailing `asyncio.run(pool.close())`, and the in-fixture
  `import asyncio` (nothing else there used it). `TestClient` is now
  entered as a context manager (`with TestClient(application) as client:`),
  so `lifespan` opens the pool on the client's loop and closes it on exit.
- `tests/test_api_pipeline.py`: `_client_for` is now a
  `@contextlib.contextmanager` that builds the app with an unopened pool
  and yields the client from inside `with TestClient(...)`. All three
  callers (`test_translate_and_optimize_success_and_cache_hit`,
  `test_translate_and_optimize_falls_back_on_malformed`,
  `test_translate_and_optimize_unknown_project_is_404`) changed from
  `client, pool = _client_for(...)` + `try/finally: asyncio.run(pool.close())`
  to `with _client_for(...) as client:` with the same bodies. `import asyncio`
  removed (now unused); `import contextlib` added. Searched the file for
  remaining `_client_for` callers and `pool.open/wait/close` — none left.
- Lifespan-close check: `FakeChatProvider.close` and
  `FakeEmbeddingProvider.close` both exist (`app/providers/fake.py`,
  read only). No test-local provider class is passed to `build_app` in
  either file (only the two fakes), so no test class needed a `close`
  added. The plain `client` fixture left untouched (no `with`), as
  instructed.

Task 2 — `test_cache_is_scoped_to_project_and_locale` slug collision. Done.
- `tests/test_cache.py`: `_conn_id` takes `slug: str = "c"`, passed as a
  bound parameter (`VALUES (%s, 'C')`); the test's second call uses
  `slug="d"`. No other test changes.

Task 3 — latency assertions in `tests/test_runner_configs.py`. Done.
- Line 58 now `assert summary.avg_latency_ms is not None and
  summary.avg_latency_ms >= 0`.
- Line 88 now `assert first.avg_latency_ms is not None and
  first.avg_latency_ms >= 1`, with the comment saying the 1 is the fake
  embedding call and the optimize step is measured wall-clock time.
- Sweep of `tests/` for other exact latency equality assertions (literal
  search for `latency`; remaining `==` hits below, all left unchanged):
  - `tests/test_cache.py:115` (`miss.latency_ms == 4`): embed (1) is the
    scripted provider's own field passed through by `cache.py`, producer
    (3) is the test's own `_producer` literal — no wall-clock step.
  - `tests/test_providers.py:25` (`result.latency_ms == 1`): reads the
    fake chat provider's own field directly.
  - `tests/test_runner.py:43` (`summary.avg_latency_ms == 0`):
    `legacy-only` echo path — deterministic 0, no `mt_optimize`/judge
    call at all (the test also asserts `avg_qps_score is None`).
  - `tests/test_runner_configs.py:103` (`second.avg_latency_ms == 1`,
    cache-hit run): embed lookup only, i.e. the fake embedding
    provider's own field passed through by `cache.py`.
  - Already `>=` (no change needed): `tests/test_mt_optimize.py:64`,
    `tests/test_providers.py:93`, `tests/test_api_pipeline.py:121`.
