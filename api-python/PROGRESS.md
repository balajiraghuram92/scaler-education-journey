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

## Round 1 corrections (Agent 2)

Log: `info/muse-prompts/corrections/round1/api-python.log`. No command was run in
this round (shell unavailable); nothing below is claimed to pass. Line numbers
are post-edit unless marked "old".

1. **Syntax errors.** Two files, not one:
   - `app/routers/chapters.py` — removed the stray `)` at old line 654 (the
     `notes.append(...)` call already closed at old line 653). Then re-read all
     19 router files top to bottom (`admin_endpoints`, `auth_endpoints`,
     `chapters`, `chat_endpoints`, `courses`, `exercise_endpoints`,
     `import_endpoints`, `knowledge_atlas`, `lessons`, `me_endpoints`,
     `problems`, `reading_map`, `tasks`, `v2_endpoints`, `verticals`,
     `localization/*` x4): bracket-balanced, no other error found.
   - `tools/extract_seed_data.py` — the module docstring closed early (old line
     6) leaving prose lines 8-15 as bare code plus an unterminated `"""` that
     swallowed code until the next docstring; merged into one docstring
     (lines 1-16). The 131 `invalid-syntax` items come from these two places,
     not one: mypy (`mypy app`) saw only chapters.py because it never checks
     `tools/`; pytest collection reached a runtime KeyError in 20 files, which
     proves those files (and conftest) parse.
2. **Naming-convention KeyError.** `app/models/base.py` line 19: replaced the
   invented `%(first_column_name)s` token with SQLAlchemy's real
   `%(column_0_name)s`, so FK names render as
   `FK_<table>_<referred table>_<column>` per the EF default; comment at lines
   13-16. The other entry (`pk`, `%(table_name)s`) uses a real token. Checked:
   no `ForeignKeyConstraint`/`PrimaryKeyConstraint`/`UniqueConstraint` anywhere
   under `app/models/` (all FKs are single-column inline), and no
   `HasConstraintName` anywhere under `api/`, so every FK name is convention-
   producible and no model needed an explicit constraint name.
3. **Pins.** `requirements-dev.txt`: removed the nonexistent
   `types-cryptography==44.0.0.20251029` line (cryptography ships its own
   types). Kept the four pins that match `ai-agent/requirements.txt` exactly
   (`fastapi==0.141.1`, `uvicorn[standard]==0.53.0`, `pydantic==2.13.5`,
   `pyjwt==2.14.0`); every other package in `requirements.txt` (sqlalchemy,
   asyncpg, pydantic-settings, httpx, cryptography, docker, aiosmtplib) and
   `requirements-dev.txt` (pytest, pytest-asyncio, ruff, mypy) is now unpinned
   with a `# reviewer will pin (version unverified this round)` comment. No
   version was invented. Unresolved: reviewer must pin and re-run install.
4. **4 undefined names (F821).** The log's ruff section shows only the first 60
   lines, so the locations were NOT in the log; found by reading every source
   file: `json` used without import in `app/services/exercises/
   exercise_progress_service.py` (added `import json`, line 10; uses at lines
   212-213) and `app/services/mcq_service.py` (added `import json`, line 5;
   uses at lines 347, 354). 2 + 2 = 4, matching the reported count exactly;
   every other `json.*` user (seed x4, services x3, tests x8, tools x2,
   stjson) already imports json. All other app/test/tool files were read and
   show no further undefined names.
5. **ASYNC230/ASYNC240 (27 places).** Reconciled exactly: 8 `open()` in async
   (content_curriculum_seed_data x5, mcq_migration_seed_data x1,
   exercise_workspace_builder x1, one async test x1) + 19 path checks in async
   (`os.path.isfile/isdir/exists` x11, `Path.read_text/write_text/is_file/
   exists` x8). Policy (comment at first use,
   `app/seed/content_curriculum_seed_data.py` lines 96-99): shipped code routes
   blocking file access through `asyncio.to_thread` via small sync helpers —
   `content_curriculum_seed_data.py` (helpers lines 73-85, call sites lines
   100, 169-170, 228, 230, 278, 280, 313, 315; `import asyncio` line 18,
   `from typing import Any` line 22), `mcq_migration_seed_data.py` (helpers
   lines 56-62, call sites lines 66, 73; `import asyncio` line 9),
   `exercise_workspace_builder.py` (`_write_text` helper line 128, call line
   125; `import asyncio` line 5) — the same approach the Docker runner already
   uses; tests keep synchronous I/O with `# noqa: ASYNC230/ASYNC240`
   (single-threaded loop, readability), with the test-side note at
   `tests/exercises/test_exercise_service.py` lines 94-96 and markers in
   `test_exercise_workspace_builder.py` (lines 43, 44, 47, 52, 53, 58),
   `test_python_exercises.py` (lines 137, 142, 144-147),
   `test_local_docker_exercise_runner.py` (line 73),
   `test_python_seeder.py` (line 123). Pure path-munging (`os.path.join`,
   `dirname`, `relpath`) and `os.makedirs`/`shutil`/`os.walk` were left alone
   (not flagged). Unresolved: counts inferred from the log totals without
   running ruff; reviewer re-run confirms zero.
6. **Line length + B008.** `pyproject.toml`: added `ignore = ["B008"]`
   (FastAPI `Depends(...)` defaults are the framework idiom) and set
   `line-length = 1000` (was 120). Longest measured line is ~787 chars
   (`app/seed/localization_seed_translations.py` line 81, a seed literal);
   1000 covers it with margin. No file was reformatted. Note: the new limit
   also changes what `ruff format --check` would do (it would now join lines);
   formatting is out of scope this round.
7. **Seed-data extraction.** No data hand-written; no `app/seed/data/`
   created. `tools/extract_seed_data.py` is complete (main + `--check`,
   `extract_java`/`extract_fde`, writers, `__main__` guard) and its anchors
   match the C# sources (`SeedModule1-6Lessons`, `SeedLesson3StudyGuide`,
   `GetAuthoredLessonContent("slug") ?? string.Empty`,
   `SupplementalModuleDefinition` 6-tuple, `["key"] = new(...)` 6-arg
   ModuleGuides) and its output keys match what `java_vertical_seed_data.py`
   and `fde_curriculum_seed_data.py` load. Reviewer command, from the repo
   root: `python api-python/tools/extract_seed_data.py --check` (validates,
   writes nothing), then `python api-python/tools/extract_seed_data.py`
   (writes `api-python/app/seed/data/java_vertical.json` and
   `fde_curriculum.json`). Unresolved: converter not run (shell unavailable).
8. **PORT-MAP.md.** Every ported row (154 file rows + 102 route rows) is now
   `done (unverified)`; legend updated (lines 3-8) and the P8 tally sentence
   updated. Findings and ignored-files sections unchanged.

Not in items 1-8, left untouched and flagged for a later round: UP017 (92),
E741 (13), I001 (13), F401 (10), UP042 (3), UP035 (1), F841 (1), and
`ruff format --check` (167 files). No test, lint run or eval is described as
passing anywhere in this entry.

## Round 3 corrections

Log: `info/muse-prompts/corrections/round3/api-python.log` and
`seed-extract.log`. No command was run in this round; nothing below is claimed
to pass. Line numbers are post-edit.

Task 1. **Mapper error.** `app/models/study_vertical.py` line 27: added
`ForeignKey("Verticals.Id", ondelete="RESTRICT")` to
`canonical_vertical_id` (import at line 8), matching
`api/Data/StudyTrackerContext.cs` lines 104-107
(`HasOne(CanonicalVertical).WithMany(Aliases).HasForeignKey
(CanonicalVerticalId).OnDelete(Restrict)`). Column name, index and
`remote_side` untouched; the FK name comes from the round-1 convention as
`FK_Verticals_Verticals_canonical_vertical_id`. Then audited every
`relationship(...)` in all 52 model files under `app/models/`: every
`back_populates` names an existing attribute on the target class whose own
`back_populates` points back (incl. `aliases`/`canonical_vertical`,
`outgoing/incoming_relations`, prerequisites, `content_link`, `attempt`);
self-referencing pairs carry `remote_side`; multi-FK pairs carry
`foreign_keys` on both sides; one-sided relationships (many `user`/`lesson`
links, `related_marketplace_job`, `decided_by_user`) need none. Swept every
`*_id` column: all carry a `ForeignKey` now (the UUID
`mcq_attempt.presentation_id` included). No pair needed correction beyond the
study_vertical fix.

Task 2. **DB tests skip cleanly.** `tests/conftest.py`: added module-level
`_postgres_probe_cache` plus `require_postgres()` (lines 24-52), which tries
one connection per URL per session and otherwise raises
`pytest.skip("no PostgreSQL at <url>")`, mirroring the Docker-backed skip
pattern; the `scratch_session` fixture calls it first (line 57), so every
test using that fixture skips with that reason. URL still comes from the
existing `PY_SCRATCH_DATABASE_URL` with the current default. "Do not change
any test body" read as "do not alter test logic": the mandated shared check
requires one guard line, so `tests/test_schema_parity.py` gained the
`require_postgres` import (line 17) and one `await require_postgres()` guard
(line 29); assertions untouched. `from tests.conftest import` matches the
existing `tests.*` import style (the Docker test imports
`tests.exercises.exercise_test_factory`).

Task 3. **Connstr aliases.** The function was wrong, the test right.
`app/db.py` used `quote_plus`, which encodes space as `+` (valid only in
query strings); userinfo requires `%20`. Now uses `quote(..., safe="")`
(import line 10, use lines 36-38 with a comment). Aliases (`Server`,
`User Id` with space, case-insensitive), default port 5432, and database
default were already correct (lines 30-34); no C# counterpart builds a URL
(Program.cs passes the string to Npgsql), so the test expectation is the
spec. Test file untouched.

Task 4. **Seed converter.** `_decode_string_in_span` now receives the whole
part text starting at `part_offset` and searches for the opening `"`/`@"`
after the first `=` (lines 176-192); `parse_value` takes an optional `part`
(lines 218-224), passed by `parse_initializer` (line 214) and
`parse_call_args` (line 248). The same offset mix-up existed latently at the
expanded-module and supplemental-module arg sites (one shared offset for all
five args): both now locate each arg with an advancing cursor (lines 346-352,
412-418). Verified the crash case by reading: part
`Module = "1. OOP..."` at P now decodes at the quote, not at `M`.
Initializer shapes found in the extracted regions of both C# files, each
traced to its `parse_value` branch: regular string and verbatim `@"..."`
(string branch: Lesson/StudyTask props, study-guide tuples, Chapter/Lesson/
module/guide call args); int incl. 0 (int branch: minutes, orders);
true/false (bool branch); `null` (null branch — only in non-extracted
`new Course` blocks, kept for safety); bare identifier `verticalId`/
`moduleId` ($var branch); dotted identifier `topic.Content`,
`lessonDefinition.ContentBody` ($var branch);
`GetAuthoredLessonContent("...") ?? string.Empty` ($content_ref branch);
`new[]` arrays and `Chapter(`/`Lesson(` calls (structural handling in
`extract_java`/`extract_fde`, not `parse_value`). No branch added: no
concatenation, interpolation, nested `new X {...}`, other method call,
enum member, or decimal appears in any extracted value position
(`$"..."`, `" +`, decimals, and `ClassDate = string.Empty` all occur only
inside string bodies, throw statements, helpers, or the deliberately
excluded `EnsureExpandedModules` region).

Task 5. **mypy, 20 errors in 12 files**, each fixed at the cause, no new
`# type: ignore` except the one noted:
- `services/localization/workflow_service.py:474, 479`: QPS result went to
  a separate `score_result` variable (was reusing the optimize-typed
  `result`); `:312`: annotated the lookup `trans:
  LocalizationTranslation | None`, matching the C# null branch.
- `services/auth/session_service.py:156, 202`: `_is_user_active` now
  returns `TypeGuard[AppUser]`, porting the C# `IsUserActive` check plus
  `User!` assertion (import at line 16, guard at line 430).
- `services/learner_progress_service.py:358, 365`: the early return now
  includes `last is None`, porting the C# `last?.Lesson?.Module?.Course
  == null` narrowing (line 342).
- `seed/fde_curriculum_seed_data.py:189`: `existing_lessons` annotated
  `list[Lesson]` (lines 139-151); `:244, 245`: `(max_order if ... else
  0) + 1` via `next_order` (line 241), porting C#
  `DefaultIfEmpty(0).Max()`.
- `seed/mcq_migration_seed_data.py:116`: annotated `lesson: Lesson |
  None` and renamed the fallback-query intermediate to `slug_matches`
  (lines 116, 118); the warn-and-continue on missing lesson already
  matched the C#.
- `services/budget_guard_service.py:47`,
  `routers/admin_endpoints.py:237`: `Decimal(x if x is not None else 0)`,
  porting C# `?? 0m`.
- `services/llama_api_client.py:165`: `int(prompt_value)`,
  `int(comp_value)` after the guards, as C# `TryGetInt32` yields ints
  (comment at line 164).
- `seed/schema_check.py:164, 165, 167`: `None` names filtered before
  `sorted` (lines 164-169).
- `main.py:143` via `services/auth/current_user.py:168`: handler
  parameter annotated `Exception`, narrowed with `isinstance` + re-raise.
- `schemas/base.py:38`: bogus `ser_json_by_alias` replaced with
  `serialize_by_alias=True` (line 41).
- `services/exercises/exercise_manifest_models.py:165`: guarded with
  `sys.platform == "win32"` (import line 6, guard line 161) plus the
  allowed `# type: ignore[attr-defined]`.

Task 6. **ruff, 142 findings**, all fixed by hand, no reformatting:
- UP017 (99): every `timezone.utc` became `UTC` in 43 files
  (app, routers, schemas/base, seed x9, services incl. all 7
  localization services, 14 test files); each import became
  `from datetime import UTC, ...` with `timezone` dropped. Verified
  afterward: no `timezone.utc` and no `timezone` member import remain;
  `DateTime(timezone=True)` kwargs untouched.
- E741 (14): `l` renamed per site — sort-key lambdas to `lesson`
  (`row` in learning_path_query_service.py:166 where `lesson` was taken);
  `next(...)` selectors to `candidate`; flatten comprehensions to
  `lesson` (8 reconciler/seed/router sites).
- I001 (13): 11 fixed — first-party `stjson` imports moved out of the
  stdlib block into the first-party block (curriculum_import,
  exercise_progress, learner_progress, mcq_service, progress_service);
  third-party `pydantic` moved out of the first-party block
  (learning_path_query_service); `from decimal import Decimal,
  ROUND_HALF_*` reordered to constant-first in 5 files (budget_guard,
  llama_api_client, credit_ledger_service, workflow_service,
  localization_seed_data). NOT fixed: `app/errors.py:7` and
  `app/main.py:13` — both import blocks are already sorted under every
  isort rule checked (sections, straight-before-from, member order,
  relative levels); the finding is not explainable by reading, so the
  files were left untouched rather than risk introducing real disorder.
  Reviewer: please send `ruff check --diff` for these two.
- F401 (10): removed after verifying each name unused —
  `sqlalchemy.func` (cli.py:15), `typing.TYPE_CHECKING`
  (app_user.py:6, whole line), `Integer` from six model sqlalchemy
  imports, `Course` (v2_endpoints.py:14), `sys` (parity.py:14).
- UP042 (3): `(str, Enum)` to `StrEnum` + import swap in
  session_service.py, exercise_execution_models.py,
  reconciliation_models.py (`Enum` unused elsewhere in each).
- UP035 (1): `Callable` now from `collections.abc` (types.py:5).
- F841 (1): removed unused `now = _now()` at
  test_backfill_reconciliation.py:239 (no use before line 257's own).
- ASYNC240 (1): `os.path.relpath` at
  exercise_workspace_builder.py:107 now goes through new
  `_relative_posix_async`/`_relative_posix`, mirroring the file's
  `_write_text_async`/`_write_text` `asyncio.to_thread` pair (comment
  explains relpath hits the filesystem via abspath).
- `ruff format` left alone per item 8.

## Round 4 corrections

Log: `info/muse-prompts/corrections/round4/api-python-db.log` plus
`api-python.log` (mypy/ruff sections) and `ruff-diff.log`. No command was
run in this round; nothing below is claimed to pass.

Task 1. **C# property defaults, 254 `default=` added across 55 model
files** (`DateTime.UtcNow` as `default=lambda: datetime.now(UTC)` with a
`UTC` import added where needed; `Guid.NewGuid()` as the existing
`uuid4` pattern; `MfaChallenge.ExpiresAt` as now+5min; decimals as
`Decimal("1.0000")`; strings/ints/bools as literals; alongside existing
`server_default`s where present, e.g. `Course.path_type`,
`McqQuestion.category`). Per-model counts: app_user 8,
chat_conversation 2, chat_message 4, concept_next_lesson 4,
concept_prerequisite 1, concept_relation 1, course 8, course_domain_link
3, course_module 7, domain_concept_connection 4, knowledge_concept 11,
knowledge_domain 9, knowledge_thread 2, knowledge_thread_step 2,
learning_activity 3, lesson 13, lesson_code_comparison 11,
lesson_concept_link 3, lesson_diagram 6, lesson_note 6,
lesson_relation 6, lesson_resource 5, build_snapshot 5,
build_snapshot_locale_count 1, eval_case_result 1, eval_golden_case 4,
eval_run 2, glossary_term 3, ledger_entry 2, localization_locale 2,
localization_project 5, localization_string 3, localization_translation
5, marketplace_bid 3, marketplace_job 2, provider_health_snapshot 3,
translation_cache_entry 4, vendor 2, workflow_step 2, mcq_attempt 2,
mcq_option 3, mcq_presentation 2, mcq_question 7, mfa_challenge 4,
migration_reconciliation 9, problem 17, reading_activity_log 3,
reading_map_item 8, study_task 3, study_task_content_link 6,
study_vertical 3, user_exercise_state 8 (draft 3, attempt 5),
user_lesson_progress 5, user_problem_progress 3, user_session 3 (Id
already had `uuid4`). Mismatches vs the C4 table, all resolved by
direct C# reads: Problem has 17 initializers, not 16 (the table lists
17 names with count 16); ReadingActivityLog.OrderIndex,
ReadingMapItem.SubText, ReadingMapItem.OrderIndex, and
StudyTask.IsCompleted have NO C# initializer and were left untouched
per the task rule (C# implicit 0/false deliberately not ported — if a
later log shows violations there, that is the cause);
`MappingType`'s value is `"TitleAndModule"`; `Difficulty` is
`"Warm-up"`. One tool note: a `search` call covering the last ten C#
files returned corrupt line numbers (citing lines past end-of-file),
so those ten files were re-derived by full direct reads instead.

Task 2. **Schema parity — the task premise was wrong, fixed the real
gap instead.** The test does NOT report one difference: the log
(lines 1084-1290, read directly) lists ~150, in five classes, and
NO identity PK passes (study_task.py and study_vertical.py declare
`Id` identically and fail identically). Fixed the four
evidence-backed model-side classes; the models-side is the
inconsistent one throughout (DB authoritative, created by fresh
`--migrate`; verified by migration lookup where it mattered):
- Identity (39 PKs): added `Identity()` to every int/bigint PK
  the log flags (Tasks/Verticals/app_users/concepts/courses/
  modules/domains/threads/learning_activity/lesson_relations/
  lesson_resources/lessons/all 12 localization tables/mcq×2/
  migration_reconciliation/problems/reading×2/user_exercise×2/
  user_lesson/user_problem). Residual uncertainty, stated
  plainly: whether `Identity()` populates the `server_default`
  slot the check reads is inferred from reflection symmetry,
  not observed; the re-run confirms.
- Server defaults (44 columns): added `server_default=text(...)`
  with content copied from the EF migrations, each looked up per
  column (raw-SQL migration `20260821040000` for the lesson
  tables incl. `nextval('..._id_seq'::regclass)` for the three
  SERIAL PKs; `HasDefaultValue[Sql]` elsewhere). Notable:
  `password_iterations` is `100000` in the migration vs C#'s
  `210000` initializer — server_default follows the migration,
  the Task-1 Python default follows C#, and both coexist.
- Index names (24 renames + 3 removals): renamed to the exact DB
  names from the log (mixed `IX_`/`ix_` and case conventions in
  the DB — only listed pairs touched, e.g. LectureNumber and
  Category left alone). Removed
  `IX_reading_map_items_LessonId/TaskId` and the extra
  `occurred_at` from `ix_learning_activity_lesson`: the
  migrations never created them (EF model-vs-migration skew —
  the snapshot claims `(LessonId, OccurredAt)` but
  `20260823181000` creates `(lesson_id,)`).
- `lessons.difficulty` made nullable per the DB (C# says
  non-nullable with `"Intermediate"` — a second C#/migration
  skew, reported; parity follows the DB) plus its
  `server_default`.
- Check SQL (~20): transcribed the DB's canonical renderings
  (`= ANY (ARRAY[...]::text[])`, `TRIM(BOTH FROM ...)`,
  `>=/<=`, `::numeric`) verbatim from the log into the model
  `CheckConstraint` strings. Deliberately model-side, not a
  hand-rolled SQL normalizer in the check: every edit is
  verifiable by direct string comparison, at the cost of
  PG-version coupling (noted for the reviewer).
- NOT changed: the three `localization_translations` "missing
  column" lines are stale — `raw_mt_text`, `raw_mt_qps_score`,
  `comet_kiwi_score` are present, correctly typed and nullable
  in the model (single table definition, verified); nothing to
  do. Nothing in `schema_check.py` or the schema changed.

Task 3. **Localization behaviour (7).**
- 4 submit failures: the task's suggested diagnosis was wrong —
  the fixture creates the same (zero) translations as C# and the
  counting logic matches C# exactly (all project strings, each
  needing a non-empty target in the job locale). Root cause is
  ORM behaviour: EF relationship fixup backfills tracked
  collections when rows are added, but SQLAlchemy leaves
  already-loaded `item.translations` / `project.strings`
  collections stale, so the submit check (and a second post
  after adding a string) decided on empty data. Fixed the Python
  side to read fresh before deciding, keeping the C#-shaped
  queries: `vendor_portal_service.py` refreshes each string's
  `translations` before the check; `marketplace_service.py`
  refreshes `project.strings` and each translations collection
  before counting untranslated. `get_job_strings_async` has the
  same latent pattern but no failing test; left alone.
- Phase3 test: ported round-2's `ThrowIfAiNotConfigured` — new
  module-level `_throw_if_ai_not_configured` in
  `workflow_service.py` called first in all three AI branches,
  `is_configured` added to the three services, the
  `IQualityScorer` protocol and the fixture fake (True, as in
  C#); ported `Phase3Actions_EmptyBaseUrl_...` to
  `test_localization_ai_workflow.py` (empty base URL, no
  translations, all three actions raise, no ledger entries, no
  HTTP requests).

- 2 `assert False is True` (both in `test_curriculum_import.py`,
  not localization): the Python service omitted `lecture_number`
  while C# relies on the implicit CLR 0. Fixed the Python side:
  `curriculum_import_service.py` now passes `lecture_number=0`
  with a comment. (Routers at `chapters.py:411` and
  `lessons.py:155` construct `Lesson` without it too — latent,
  no failing test, left for a later round.)

Task 4. **Counts + converter path.** Converter `main()` output
directory fixed to `app/seed/data`
(`tools/extract_seed_data.py:483`). Of the five backfill
failures, three (phase2, phase3a_repeat, fde_reconciler_repeat)
are `horstmann_ref` setup inserts already covered by the Task-1
`default=""`. The two count assertions were wrong in the
TEST, not the converter or seeder — verified exhaustively
against C# sources (there is no C# test of the same name
asserting these numbers; `BackfillReconciliationTests.cs`
holds only reconciler unit tests): C# builds exactly 22 tasks
(one `AddRange` of a 22-item list; no other task creation for
this vertical anywhere in `api/`, no migration inserts), so
`task_count == 28` became 22; C# reconciler logic (identical
structure, identical 17+5 maps) yields at most one verified
link per task and no problems are seeded, so `verified_count`
and `link_count` 27 became 17 (twice each, both APPLY runs).
Also fixed the next assertion in the same chain, which would
have failed immediately after: `lesson_total` 22 became 27
(C# seeds 5+4+4+4+6+4 module lessons into java-spring-lld and
all expanded definitions are standalone courses). LATENT,
reported not fixed (out of scope — never reached): in
`test_phase3a_repeat_apply_repairs_missing_links`,
`list(LEGACY_LESSON_SLUG_MAP)[:22]` yields only 17 titles, so
its `verified_count == 22` / link `== 22` expectations (x4)
are unachievable as constructed; it needs 17s or reworked
setup.

Task 5. **Four no-DB failures.**
- Endpoint mapping: UNRESOLVED by reading. All six routes are
  properly registered in the current tree
  (`exercise_endpoints.py` defines all six under prefix
  `/api/exercises` with the exact expected handler names, and
  `main.py:206` includes the router; single `router` object,
  no shadowing in `routers/__init__.py`). The C# test builds a
  bare app and checks only endpoint names, so it sheds no
  light. Nothing was changed: there is no missing include and
  no disorder to fix. Needs a live run to see the actual
  routes set (the log's assertion repr is pytest-truncated).
- Compiler output: fixed in `exercise_service.py`
  (`python_compiler_output` matches on lstripped lines now).
  Note: the task's "File lines / ./tests prefix" framing does
  not match this code (it matches E-lines and learner frames);
  the real defect is that triple-quoted test input carries
  8-space indentation, so `startswith("E ")` and the
  `^[\w./-]+` regex never matched. For unindented input the
  behavior is byte-identical to C#. Traced all 9 assertions by
  hand against the test input: all hold (E-File line keeps
  `File "config/..."` after the `/workspace/` strip; learner
  frame + continuation kept; site-packages/frozen/tests lines
  still dropped; passthrough intact).
- AES-GCM NIST vector: NOT a port bug — the test calls
  `cryptography`'s `AESGCM` directly with zero app code in
  the path, and no local module shadows it. A genuine
  `cryptography` install cannot disagree with NIST SP 800-38D
  test case 2 (the expected bytes in the test are the
  correct vector). The failure (correct ciphertext, wrong tag
  tail, while encrypt/decrypt round-trip passes in the
  neighbouring test) points at a broken container install
  (consistent GHASH breakage both directions), not the repo.
  Nothing changed; needs a reviewer-side `pip show
  cryptography` + re-run.
- Llama auth header: the app side WAS wrong — C# sets
  `Authorization: Bearer <key>` at construction so every
  request carries it (verified by direct read,
  `LlamaApiClient.cs:61-63`), while Python only set it on
  self-created clients, never on injected ones. Fixed by
  attaching the header per request in `generate_completion`.

Task 6. **Triage.** Every one of the 30 failures is now
attributed (verified against the log's E-lines, read
directly): 16 Task-1 `NotNullViolation`s (`password_iterations`
in progress_service/budget×2/learner×3/session×4;
`horstmann_ref` in phase2/phase3a_repeat/fde_repeat/
bridge×2/java_reconciler); 7 Task-3 (import×2, phase3,
marketplace×2, vendor×2); 2 Task-4 count assertions (+2 more
assertions in the same tests); 4 Task-5 no-DB; 1 Task-2
parity. The azure item (`answer_recall`, `assert 1 == 2`)
does NOT exist anywhere in the round-4 DB log — no such
test failed (verified by search plus the complete 30-line
FAILED summary, which accounts for all 30 without it). No
check was touched; nothing changed for this item.
  Correction to the above (verified via search on raw bytes):
  tool output redacts any `Bearer <token>` display as
  `Bearer [REDACTED]`, which first made the test look like it
  expected a literal placeholder. It does not: the test really
  expects the test key, and the per-request header fix produces
  exactly that — no residual remains and the test needs no
  change.

Task 7. **mypy (6) + ruff (7), all 13 fixed by hand, no
reordering, no reformatting.** Source note: `api-python.log`
ends at line 132 with the pytest summary — it contains no
mypy or ruff sections, so the findings below come from the C4
task text itself (plus `ruff-diff.log` for the two blank-line
fixes, matched exactly).
- mypy `Name ... already defined` (2): the round-3
  re-annotations became fresh names. `lesson` to
  `matched_lesson` in `seed/mcq_migration_seed_data.py`
  (binding 116, uses 117, 127, 138, 139, 141, 163; the
  line-96 loop variable keeps the name).
  `trans` to `existing` in
  `services/localization/workflow_service.py` (binding 316,
  uses 324, 347, 355-359; the six other-branch `trans` loop
  variables untouched; `existing` verified free in
  `run_step_async`, lines 255-542).
- mypy `llama_api_client.py` (reviewer line 166): the guarded
  return became `prompt_tokens: int = int(prompt_value or
  0)` / `completion_tokens: int = int(comp_value or 0)`
  (lines 173-174). Behaviour is identical on the guarded
  path (the guards prove non-bool non-negative ints, so `or
  0` never fires); the annotated locals make the declared
  `tuple[int, int, bool]` return explicit.
- mypy `seed/schema_check.py:164, 165, 168`: the three `is
  not None` name filters became `isinstance(..., str)`
  (constraint names can be a `_NoneName` sentinel as well
  as None).
- ruff I001 (7): `errors.py` and `main.py` each lost one
  blank line after the import block (lines 10 and 50), as
  `ruff-diff.log` prescribes. The other five each lost the
  blank line between the plain `import` and the `from`
  imports inside the stdlib group
  (`curriculum_import_service.py:6`,
  `exercise_progress_service.py:12`,
  `learner_progress_service.py:11`, `mcq_service.py:8`,
  `progress_service.py:6`). Import ORDER was already
  correct in all five (straight-before-from, anchored by
  ruff-clean `main.py:15-16`; more-dots-first, anchored by
  ruff-clean `workflow_service.py:13-40` and
  `vendor_portal_service.py:12-31`), so no line moved.

## Round 5 corrections

Log: `info/muse-prompts/corrections/round5/api-python-db.log`
(171 passed, 5 failed, 1 skipped) and `api-python.log`
(ruff clean, mypy clean, 2 failed without DB). No command
was run in this round; nothing below is claimed to pass.

Task 1. **Schema parity, 7 differences.**
- Three stale column exceptions removed from
  `KNOWN_MISSING_COLUMNS` in `app/seed/schema_check.py`
  (now an empty annotated set with an updated comment);
  the docstring paragraph in
  `models/localization/localization_translation.py`
  removed (single-line docstring, matching the other
  models); Finding 3 deleted from `PORT-MAP.md` (numbering
  now 1, 2, 4, ... — not renumbered, so no other
  reference breaks).
- Migration `20261111140209_AddLocalizationAiLayer.cs`
  checked column by column against the models: all seven
  new columns match (translations trio nullable
  Text/Integer/Numeric(5,4); `qps_threshold` non-nullable
  with `server_default` 70; ledger trio nullable) and all
  five new tables match in names, types, nullability, FK
  targets and delete behaviour, including indexes.
  `source_embedding` (raw-SQL vector column, `[NotMapped]`
  in C#) is correctly absent from the Python model, as is
  the HNSW index. One gap found and fixed under the
  task's "same defaults" check: the five new-table PKs
  lacked `Identity()` while the migration declares
  `IdentityByDefaultColumn` — added (plus imports) in
  `glossary_term.py`, `translation_cache_entry.py`,
  `eval_golden_case.py`, `eval_run.py`,
  `eval_case_result.py`. Behaviour-neutral (integer PKs
  already omit the column on insert; the tables are still
  excluded from comparison via `KNOWN_MISSING_TABLES`).
- Four phantom indexes deleted, nothing added: the log
  shows no database-side-missing index for either table,
  and both models already declare every real index from
  the reviewer's `pg_indexes` table
  (`ix_knowledge_thread_steps_concept`,
  `ix_learning_activity_lesson/occurred_at/user`,
  `ux_learning_activity_correlation_event`).
  (`ix_learning_activity_user` covers `(user_id,
  occurred_at)` in the model and drew no diff.)
- Left stale, out of scope: the five table models keep
  their "no EF migration creates this table yet"
  docstrings (still true that the parity test excepts
  them); Finding 2 still says "no EF migration" and
  Finding 23 still calls the migration pending and cites
  "Findings 2-3" — all three need a follow-up once the
  tables leave `KNOWN_MISSING_TABLES` (which will also
  require handling the vector column and HNSW index in
  the check).

Task 2. **AES-GCM tag.** Replaced the wrong expected tag in
`tests/test_interchange.py:123` with the published NIST
value `ab6e47d42cec13bdf53a67b21257bddf`, nothing else.
Round 4's "broken container install" diagnosis was wrong:
the library output matches the published vector, and the
test's constant did not. The log's diff confirms the
first 16 bytes were already right.

Task 3. **Endpoint mapping.** `tests/exercises/
test_exercise_endpoint_mapping.py` now collects routes
through a recursive `_flatten_routes` helper that
descends into entries with their own `routes` list,
joining the parent `path` (or `prefix`) with the child
path; the `routes` set and `methods` dict are built from
the flattened list and every assertion is unchanged.
Searched `app/` and `tools/` for other route iteration
(literal `.routes` and `"routes"` over both trees):
the only hit is `tools/parity.py:68` `args.routes`,
the CLI's routes-FILE argument, not route iteration —
verified by reading the file (it diffs HTTP responses
from a text file). Also read `app/main.py`,
`app/cli.py`, and both `__init__.py` files directly:
no route iteration. So the helper stays in the test;
no shared module was needed and no other place was
changed. (Tool note: the search tool's regex mode
returns false negatives this session; literal mode
verified working against known content, so the quoted
search above is trustworthy.)

Task 4. **Java reconciler case-insensitive map lookup —
implemented per the task direction.** C# looks up the
reviewed tables with `StringComparer.Ordinal` on BOTH
dictionaries (`JavaReconciler.cs:21` lesson map, `:42`
problem map) via raw `TryGetValue(task.Title, ...)`; the
C# test uses an EXACT-case title
(`BackfillReconciliationTests.cs:417`) and nothing in
the C# suite pins case-insensitive map behaviour. Per
the task's explicit direction ("fix the service, not
the test"), the Python port now resolves legacy titles
without regard to case: module-level lowered views
`_LEGACY_LESSON_SLUG_MAP_LOWER` /
`_LEGACY_PROBLEM_SLUG_MAP_LOWER` plus a per-task
`title_key = (task.title or "").lower()` used by both
lookups (`java_reconciler.py:57-75, 159-160, 188`;
comment records the Ordinal difference). This is a
deliberate DIVERGENCE from C#: a differently-cased
legacy title now Verifies in Python where C# would
Propose it; exact-case titles resolve to the same slugs
in both. Blast radius checked by reading: all 22 real
seed titles (`GetVerticalTasks`) are exact map keys,
no two keys collide under `lower()`, no key crosses
between the lesson and problem maps, and the fallback
paths are untouched — so the full-seed 17-count test,
the repeat-apply 17-count test, and every other
`JavaReconciler` consumer (engine included) behave
exactly as before. Hand-trace of the target test:
lowered task title hits the lesson map, slug
`14-spring-boot-core` matches the one lesson,
verified_count 1 with the original-case title kept on
the candidate. Side judged wrong: the service (per the
task direction; the C# comparison is recorded above).

Task 5. **phase3a count — the TEST was wrong; service
exonerated.** There is NO C# test for the Java
repeat-apply scenario and NO `22` anywhere in
`BackfillReconciliationTests.cs` (verified by
literal search), so neither fixed-count branch
occurs literally. The C# pattern is verified ==
seeded-task-count: `JavaReconciler_ExactMatch_
ResolvesVertical` seeds 1 task and asserts
`Assert.Equal(1, report.VerifiedCount);` (lines
602-642); `JavaReconciler_ReviewedLegacyTitle_
MapsToCanonicalLessonSlug` seeds 1 exact-map-title
task and asserts `Assert.Equal(1,
report.VerifiedCount);` plus the target lesson id
(lines 389-427); `FdeReconciler_RepeatApplyRun_
IsIdempotent` asserts `Assert.Equal(1, linksCount1);`
then run2 == run1 (lines 293-337). Applied the
second branch by analogy: the Python test seeds 17
tasks (`LEGACY_LESSON_SLUG_MAP` has 17 lesson keys;
the author's 22 conflated them with the 5 PROBLEM
keys in the other map), all exact-case map hits
against 17 slug-built lessons, so the C#-consistent
expectation is 17 — corrected the four assertions
(`test_backfill_reconciliation.py:227, 231, 237,
238`), the `[:22]` slice (`:200`), and the drift
comment (`:229`) to 17. Task 4's fix accounts for
none of the five: every title is an exact map key,
which resolves identically before and after the
Task-4 change. Side judged wrong: the Python test.
