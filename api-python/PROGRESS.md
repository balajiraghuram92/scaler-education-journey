# Progress — agent-2-python-port-a, agent-2-python-port-b (P6, P8)

## P0 — Scaffold, configuration, parity tooling

Files created or changed:
- api-python/requirements.txt, requirements-dev.txt, pyproject.toml, Dockerfile
- api-python/app/__init__.py, app/settings.py, app/db.py, app/errors.py, app/main.py, app/cli.py
- api-python/app/schemas/__init__.py, app/schemas/base.py
- api-python/app/models/__init__.py, app/services/__init__.py, app/seed/__init__.py
- api-python/app/routers/__init__.py + 15 empty router modules (verticals, tasks, courses, lessons, problems, knowledge_atlas, reading_map, chapters, v2_endpoints, import_endpoints, exercise_endpoints, auth_endpoints, me_endpoints, admin_endpoints, chat_endpoints) + routers/localization/__init__.py + 4 empty localization router modules
- api-python/tools/__init__.py, tools/parity.py, tools/parity_routes.txt
- api-python/tests/conftest.py, tests/test_db_connstr.py
- api-python/README.md, PORT-MAP.md, PROGRESS.md
- docker-compose.python.yml (repo root override, adds api-python on host port 8081)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- `cd api-python && python tools/parity.py --routes tools/parity_routes.txt` (needs both APIs running; health endpoints parity not verified)
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.python.yml up -d --build api-python`

Prompt-vs-code mismatches:
- None for P0. Minor: P0 names the scratch DB only; chose `studytracker_py` per README convention. /health/ready pending-migration detail simplified (Finding 1 in PORT-MAP.md).

## P1 — Entities

Files created or changed:
- api-python/app/models/base.py, app/models/types.py (JsonbText), app/models/__init__.py
- 38 top-level entity modules (app_user through user_session, incl. user_exercise_state with 2 classes)
- api-python/app/models/localization/__init__.py + 17 localization entity modules
- api-python/tests/test_schema_parity.py
- api-python/PORT-MAP.md (P1 section all done; Findings 2-3)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest` (incl. tests/test_schema_parity.py against the scratch DB — needs PY_SCRATCH_DATABASE_URL)

Prompt-vs-code mismatches:
- The C# model is ahead of its migrations: 5 entities have no tables and localization_translations has 3 unmigrated columns (Findings 2-3). The P1 proof test therefore cannot pass with "zero ignored tables"; it names these exact exceptions and fails on anything else. Models keep the C# properties for behavioural fidelity.

## P2 — Authentication, sessions, users

Files created or changed:
- api-python/app/schemas/auth_dtos.py; app/schemas/base.py (+DotNetDateTime)
- api-python/app/services/auth/__init__.py, i_password_hasher.py, i_jwt_token_service.py, pbkdf2_password_hasher.py, jwt_token_service.py, current_user.py, totp_secret_protector.py, totp_service.py, session_service.py
- api-python/app/services/email/__init__.py, i_email_notification_service.py, smtp_email_notification_service.py
- api-python/app/rate_limit.py (moved from main.py so routers can use it)
- api-python/app/routers/auth_endpoints.py, me_endpoints.py, admin_endpoints.py (filled in)
- api-python/app/main.py (real auth wiring: challenge handler; placeholder removed), app/errors.py (+endpoint_problem)
- api-python/app/models/*.py (uuid defaults for 6 id columns + learning_activity.correlation_id)
- api-python/tests/test_auth_and_user_management.py, test_totp_service.py, test_totp_secret_protector.py, test_session_service.py, test_interchange.py, test_email.py
- api-python/PORT-MAP.md (P2 section all done; Findings 4-5)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- .NET-minted interchange fixtures: start .NET api, signup/login/enroll a user, capture (password hash row, JWT, encrypted TOTP secret + code at fixed time, session row) into tests/fixtures/dotnet_vectors.json, then run `pytest tests/test_interchange.py`
- Parity: `python tools/parity.py --routes tools/parity_routes.txt` after adding auth/me/admin routes (needs both APIs + seeded DB)

Prompt-vs-code mismatches:
- SessionAndLearnerStateTests.cs mixes phases: the 4 session tests are translated here; the 4 LearnerProgress/MCQ tests move to P3 and the seeder test to P7 (noted in the test module docstring).
- JWT raw claim names needed corroboration beyond the prompt's file list: used ai-agent/auth.py (Finding 4).
- The prompt's "value produced by the .NET code" fixtures cannot be produced without running .NET; tests/test_interchange.py pins the same contracts against standard vectors (PBKDF2, RFC 6238, NIST GCM, SHA256) instead.

## P3 — Curriculum, progress, atlas, MCQs

Files created or changed:
- api-python/app/schemas/dtos.py
- api-python/app/services/progress_service.py, learner_progress_service.py, learning_path_query_service.py, atlas_query_service.py, reading_map_service.py, mcq_service.py
- api-python/app/routers/verticals.py, tasks.py, courses.py, lessons.py, problems.py, knowledge_atlas.py, reading_map.py, chapters.py, v2_endpoints.py (filled in)
- api-python/app/schemas/auth_dtos.py (P2 follow-up: request fields now optional like C# binding), app/schemas/base.py (format_dotnet_datetime public + year<1000 fix)
- api-python/app/services/learner_progress_service.py (also satisfies P2 me router) — me/admin routers unchanged
- api-python/tests/test_progress_synchronization.py, test_lifecycle_and_problem_details.py, test_session_learner_state_progress.py
- api-python/PORT-MAP.md (P3 section all done; Findings 6-8; V2 progress auth corrected to RequireAuthorization)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- Parity on every GET route in this phase against the seeded local DB + write routes against scratch DB (needs both APIs running)

Prompt-vs-code mismatches:
- V2 chapter reader needs P4's exercise repository (forward reference within this track; P4 provides get_exercise_repository).
- P0 route table listed V2 progress routes as api-key; C# marks all three RequireAuthorization (table corrected).
- The 4 LearnerProgress/MCQ tests from SessionAndLearnerStateTests.cs are translated here (see P2 note), not with the P3-named C# test files.

## P4 — Exercise runner

Files created or changed:
- api-python/app/schemas/exercise_dtos.py, exercise_metadata_dtos.py
- api-python/app/services/exercises/__init__.py + 15 modules (i_exercise_runner, i_exercise_repository, exercise_execution_exceptions, exercise_execution_models, exercise_manifest_models, exercise_repository, exercise_metadata_service, exercise_solution_service, exercise_submission_validator, exercise_workspace_builder, exercise_execution_classifier, surefire_result_parser, exercise_service, exercise_progress_service, local_docker_exercise_runner)
- api-python/app/routers/exercise_endpoints.py (filled in)
- api-python/tests/__init__.py, tests/exercises/__init__.py, exercise_test_factory.py + 10 test modules (classifier, parser, validator, repository, metadata, solution, service, workspace builder, endpoint mapping, python exercises, docker runner)
- api-python/pyproject.toml (docker marker), PORT-MAP.md (P4 done; Findings 9-10)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest` (non-Docker tests) and `RUN_DOCKER_EXERCISE_TESTS=1 pytest -m docker` (Docker test)
- Parity on exercise routes against both APIs (needs running APIs + runner images)

Prompt-vs-code mismatches:
- None structural. Manifest JSON is camelCase; the port parses case-insensitively like C#. ValidationProblem shape reproduced with per-error files[i] keys exactly as C# builds them.

## P5 — Chat, LLM client, budget guard, import

Files created or changed:
- api-python/app/schemas/chat_dtos.py
- api-python/app/services/llama_api_client.py, budget_guard_service.py, curriculum_import_service.py
- api-python/app/routers/chat_endpoints.py, import_endpoints.py (filled in)
- api-python/app/settings.py (money options float → Decimal)
- api-python/tests/test_curriculum_import.py, test_llama_api_client.py, test_budget_guard.py
- api-python/PORT-MAP.md (P5 done; Findings 11-12)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- Parity on chat/import routes (needs both APIs; chat needs LLAMA_API_KEY or compares mock mode)

Prompt-vs-code mismatches:
- C# LlamaApiClient has no retry and no streaming (single POST); the port matches — nothing to preserve beyond that.
- CurriculumImportService needs P7's NormalizationHelper.generate_slug (forward reference within this track).
- Chat system-prompt newlines assume the Linux container (Finding 11).

## P7 — Seeders, CLI modes, reconciliation

Files created or changed:
- api-python/app/services/reconciliation/__init__.py + 7 modules (normalization_helper, reconciliation_models, reconciliation_engine, java_reconciler, fde_reconciler, azure_labs_reconciler, atlas_reading_reconciler)
- api-python/app/seed/db_seeder.py, fde_seed_data.py, reading_map_seed_data.py, knowledge_atlas_seed_data.py, chapter_seed_data.py, localization_seed_data.py, localization_seed_translations.py, mcq_migration_seed_data.py, content_curriculum_seed_data.py, python_curriculum_seed_data.py, java_vertical_seed_data.py, fde_curriculum_seed_data.py, schema_check.py
- api-python/app/stjson.py (STJ-compatible dumps for DB-stored JSON; call sites in progress/learner/mcq/exercise/import services updated)
- api-python/app/models/types.py (JsonbText bypasses impl processors: no double-encode, no reformat-on-read)
- api-python/tools/extract_seed_data.py (converter; JSON outputs NOT produced — see below)
- api-python/app/cli.py (full CLI), tests/test_schema_parity.py (now uses schema_check)
- api-python/tests/test_backfill_reconciliation.py, test_java_reconciliation.py, test_bridge_schema_constraints.py, test_python_seeder.py
- api-python/README.md (CLI section), PORT-MAP.md (P7 done; Findings 13-14)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- `python api-python/tools/extract_seed_data.py --check` then without --check (produces app/seed/data/*.json)
- `cd api-python && python -m app.cli --seed-reference-data` (twice: idempotency) and the seeded-DB diff proof
- `cd api-python && python -m app.cli --reconcile-content --scope all` (dry-run) and --apply/--verify variants

Prompt-vs-code mismatches:
- The C# model is ahead of migrations in seeder paths too: full seeding writes glossary terms to a nonexistent table (Finding 14), and FDE/Azure apply writes "Proposed" statuses the check constraint rejects (Finding 13). Both ported as-is; the seeded-DB diff cannot pass until the C# side is fixed or the seeder is pointed at a DB with those tables.
- JavaVerticalSeedData content sections differ by construction: module lessons/authored bodies keep CRLF (verbatim literals), expanded Chapter() content uses LF (interpolated strings). The converter preserves raw bytes; hand-ported builders match per site.
- The P7 proof (seeded-DB diff) additionally needs the converter run + both seeders executed; recorded above as not run.

## P6 — Localization Lab (agent-2-python-port-b)

Agent 1 finished LA4 (phases LA1-LA4 complete), so this ports the tree
including LA4: MtOptimizeService, QpsScoringService and AutoRoutingService are
thin HTTP clients over localization-ai, ported as such; no prompt, scoring or
routing logic was written in api-python/.

Files created or changed:
- api-python/app/schemas/localization_dtos.py
- api-python/app/services/localization/__init__.py + 16 modules (localization_exceptions, i_translation_provider, i_quality_scorer, localization_ai_client, mt_optimize_service, qps_scoring_service, auto_routing_service, credit_ledger_service, localization_project_service, localization_string_service, marketplace_service, vendor_portal_service, snapshot_service, provider_health_service, google_translate_provider_service, workflow_service)
- api-python/app/settings.py (+LocalizationAiSettings)
- api-python/app/routers/localization/*.py (4 modules filled in)
- api-python/tests/localization_fixture.py, test_marketplace_service.py, test_vendor_portal_service.py, test_localization_workflow_service.py, test_localization_ai_workflow.py, test_localization_ai_client.py, test_google_translate_provider.py
- api-python/PORT-MAP.md (P6 section all done; Findings 15-24)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest` (incl. the 6 new localization test modules on the scratch DB)
- Parity on all four localization endpoint groups (needs both APIs + seeded DB; routes added to tools/parity_routes.txt in P8)

Prompt-vs-code mismatches:
- The P6 phase prompt predates LA4: two files it does not list exist and were ported (LocalizationAiClient.cs, Options/LocalizationAiOptions.cs — rows added to PORT-MAP.md). The NotImplementedException-stub branch does not apply; the LA4 HTTP-client branch does.
- C# vs design docs: 6 disagreements, all ported as C# (Findings 15-20).
- WorkflowServiceTests.RunStep_Phase3Actions_StillSurfaceNotImplemented is stale post-LA4 (Finding 21): translated verbatim; it fails in both stacks until the C# test is updated.
- The translated RunMtOptimize/ScoreQps/AutoTranslate tests need the pending LA1 migration on the scratch DB (Finding 23). Run order for the reviewer: first `dotnet ef migrations add AddLocalizationAiLayer --project api`, apply it to studytracker_py, then pytest.
- C# ArgumentException Message suffixes (" (Parameter 'x')") are reproduced verbatim in the Python ValueErrors (Finding 22).
- Group routes registered with "/" in C# accept the no-slash form (Finding 24).

## P8 — Full parity sweep and reading guide (agent-2-python-port-b)

1. PORT-MAP audit: every file row (154) and route row (102) is `done`; the
   5 ignored files carry written reasons. Nothing was left `todo`; no new
   porting was needed.
2. `tools/parity_routes.txt` rewritten to cover all 102 routes in PORT-MAP
   order with concrete seeded-DB ids/slugs and well-formed bodies; its header
   documents the run-once-per-fresh-seed procedure and the extra `--ignore`
   fields write routes need. The full parity run itself is NOT RUN (shell
   unavailable) — no difference is claimed fixed or found.
3. React walkthrough NOT RUN (shell unavailable). The one setting that points
   the React dev app at the Python API with no file change is the existing
   env var read by `app/src/api/client.js` line 7: from `app/`, run
   `VITE_API_URL=http://localhost:8081 npm run dev`
   (`set VITE_API_URL=http://localhost:8081 && npm run dev` on Windows).
   Unverified click-through: sign in, open a lesson, answer an MCQ, run one
   Java and one Python exercise, open the Localization Lab.
4. `README.md` rewritten as the reading guide: request walkthrough order
   plus a C#-construct → port-construct table with verified file-and-line
   examples (two citations were fixed after checking: workflow
   `_validate_action_and_trigger` is lines 550-567, not 610-622; router
   `run_workflow_step` is lines 214-234, not 255-283).
5. Final report: PORT-MAP totals 154 files done, 102 routes done, 5 ignored
   with reasons, 24 Findings (1-14 from part A, 15-24 from P6). Parity
   result: NOT RUN — see commands below. Complete Findings list is in
   PORT-MAP.md; no new Findings in P8.

Files created or changed:
- api-python/tools/parity_routes.txt (102 routes)
- api-python/README.md (reading guide)
- api-python/PORT-MAP.md (P8 section marked done)
- api-python/PROGRESS.md (this entry)

Commands NOT run (shell unavailable):
- `cd api-python && ruff check .`
- `cd api-python && ruff format --check .`
- `cd api-python && mypy app`
- `cd api-python && pytest`
- `cd api-python && python tools/parity.py --routes tools/parity_routes.txt --ignore timestamp,traceId,traceid,appliedMigrationsCount,createdAt,updatedAt,postedAt,awardedAt,submittedAt,approvedAt,lastRunAt,lastLoginAt` (needs both APIs on identically seeded DBs, run once)
- React click-through against the Python API (needs both APIs + `npm run dev` with VITE_API_URL set)

Prompt-vs-code mismatches:
- None for P8. The route-table count corroborates part A's inventory: 102 routes (27 inline + 75 endpoint modules).
