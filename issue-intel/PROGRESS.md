# Issue-intel track progress (Agent 3)

Shell is unavailable in this track: every command below is NOT RUN.
Recorded here exactly as it would be executed from the repository root.

## G0 — Scaffold, synthetic world, sample repository

Status: finished (code written; nothing run — shell unavailable).

Files created (91): PROGRESS.md, README.md, pyproject.toml, docker-compose.yml,
Dockerfile, alembic.ini, .gitignore, app/__init__.py, app/settings.py, app/db.py,
app/main.py, app/worker.py, app/gateway/__init__.py, app/gateway/tasks.py,
app/gateway/adapters.py, app/gateway/gateway.py, app/models/__init__.py,
app/models/gateway.py, app/schemas/__init__.py, app/routers/__init__.py,
app/routers/health.py, alembic/env.py, alembic/script.py.mako,
alembic/versions/0001_g0_base.py, tests/conftest.py, tests/test_gateway_fake.py,
tests/test_import_boundary.py, tests/test_health.py, tests/test_generator.py,
tests/test_history_plan.py, synthetic/__init__.py, synthetic/data.py,
synthetic/world.py, synthetic/writers.py, synthetic/generate.py,
synthetic/corpus/.gitkeep, evals/__init__.py, evals/ground_truth/.gitkeep,
evals/reports/.gitkeep, sample_repo/README.md, sample_repo/.gitignore,
sample_repo/setup-history.py, sample_repo/TesseraEditorTools.sln,
4 module csproj, tests csproj, ToolTests.cs, 27 module .cs files,
evals/fix_cases/FixCases.csproj, evals/fix_cases/README.md,
evals/fix_cases/bugs.json, evals/fix_cases/HiddenTests.cs, 12 bugNN.patch.
Files changed: ToolTests.cs (assertion fix, same phase).

Commands NOT RUN (from issue-intel/ unless noted):
- `docker compose up -d --build`
- `alembic upgrade head`
- `python -m synthetic.generate --seed 20240917` (twice; byte-compare outputs)
- `python sample_repo/setup-history.py`
- `dotnet test sample_repo/TesseraEditorTools.sln`
- `dotnet test evals/fix_cases/FixCases.csproj` (expect fail on main; then apply
  each bugNN.patch and expect pass — 12 iterations)
- `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`

Prompt-vs-code mismatches:
- BUILD-SPEC lists `model_calls` under G4, but G0 requires per-call logging to a
  table: created `model_calls` in migration 0001 with core columns; G4 extends it.
- sample_repo git repo/branches: not built (no shell, no git ops). Left as
  `sample_repo/setup-history.py` + the commands above.
- Corpus and ground truth: not generated (generated only by running the tool).
  Left as `synthetic/` generator + command; never fabricated.
- On-disk sample_repo tree is therefore the clean base; the 12 bugs exist only
  after setup-history.py reverse-applies the reference patches.
- Hidden tests combined into one HiddenTests.cs (12 classes) rather than 12
  files; one test class per bug as specified.

## G1 — Knowledge foundation: ingest, links, search, cited answers

Status: finished (code written; nothing run — shell unavailable).

Files created (31): alembic/versions/0002_g1_knowledge.py, app/models/g1.py,
app/ingest/__init__.py, app/ingest/extract.py, app/ingest/normalise.py,
app/ingest/crosswalk.py, app/ingest/outcomes.py, app/ingest/chunk_embed.py,
app/ingest/ownership.py, app/ingest/run.py, app/governance/__init__.py,
app/governance/entitlements.py, app/governance/rls.py,
app/governance/redaction.py, app/search/__init__.py, app/search/hybrid.py,
app/search/rerank.py, app/search/lineage.py, app/search/citations.py,
app/routers/tickets.py, app/schemas/tickets.py, evals/metrics.py,
evals/run_g1.py, tests/db_helper.py, tests/test_metrics.py,
tests/test_citation_check.py, tests/test_ingest_idempotent.py,
tests/test_rls.py.
Files changed: alembic/env.py (register g1 models), app/main.py (tickets
router), app/ingest/run.py (count cleanup), app/routers/tickets.py (drop dead
redaction stub), pyproject.toml (isort first-party), README.md (G1 section).

Commands NOT RUN (from issue-intel/):
- `alembic upgrade head`
- `python -m app.ingest.run --corpus synthetic/corpus` (twice; second run
  inserts nothing)
- `python -m evals.run_g1 --adapter fake`
- `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`
- `curl -X POST localhost:8010/tickets/TES-0001/similar -H 'x-user-id: 1'`
- DB-backed pytest cases need `issueintel_test` (auto-created+migrated by
  tests/db_helper.py) and skip otherwise

Prompt-vs-code mismatches:
- RLS policies use `FOR ALL ... USING` without `WITH CHECK`: reads are
  filtered (the leakage requirement), inserts stay service-mediated so
  ingestion works without per-commit context juggling.
- `VECTOR(64)` is fixed in migration 0002 and must match
  `Settings.embedding_dim`; real 1536-dim embeddings need a re-migration.
- Regression "pairs" for retrieval eval are scored as change-hit@5 through
  lineage expansion (the corpus has one case per change, so case→case
  regression pairs do not exist).

## G2 — Investigation pipeline, review, MCP, dashboard

Status: finished (code written; nothing run — shell unavailable).

Files created (32): alembic/versions/0003_g2_runs.py, app/models/g2.py,
app/adapters/__init__.py, app/adapters/fake_tracker.py, app/adapters/fake_chat.py,
app/adapters/fake_docs.py, app/adapters/replay_cli.py, app/pipeline/__init__.py,
app/pipeline/stages.py, app/pipeline/stage_fns.py, app/pipeline/manager.py,
app/pipeline/render.py, app/routers/runs.py, app/routers/reviews.py,
app/mcp_server/__init__.py, app/mcp_server/server.py, web/package.json,
web/vite.config.js, web/index.html, web/src/main.jsx, web/src/api.js,
web/src/App.jsx, web/src/styles.css, evals/run_g2.py,
tests/test_failure_policy.py, tests/test_rendering.py, tests/test_wrong_module.py.
Files changed: alembic/env.py (register g2 models), app/main.py (CORS, routers),
app/worker.py (job polling), app/governance/entitlements.py (is_visible),
app/governance/rls.py (service_session), app/gateway/adapters.py (FakeAdapter
per-system-prompt defaults for machinery runs), evals/run_g2.py (import
cleanup), tests/test_wrong_module.py (helper cleanup), README.md (G2 section).

Commands NOT RUN (from issue-intel/):
- `alembic upgrade head`
- `python -m app.adapters.replay_cli --n 10` (with API + worker up; expect ten
  reviewable runs in the dashboard)
- `python -m evals.run_g2 --adapter fake` and `--adapter openai`
- `cd web && npm install && npm run dev`
- `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`

Prompt-vs-code mismatches:
- Service compute uses session-level `SET` (not `SET LOCAL`) in
  `service_session()`, because per-stage commits would drop a LOCAL context;
  per-request paths still use `SET LOCAL`.
- S5 version window: corpus changes carry no versions, so the window is
  recorded from the ticket and applied only when a change has `merged_at`.
- RERUN with identical content deletes the cached run first (unique
  constraint on ticket+hash+version), then recomputes.
- Injection pass criteria are side-effect checks (nothing posted, no payload
  echo, evidence stable) rather than a stripped-body A/B, which would mutate
  corpus rows.

## G3 — Fix agent, backport agent, approvals

Status: finished (code written; nothing run — shell unavailable).

Files created (24): alembic/versions/0004_g3_fix.py, app/models/g3.py,
app/agents/__init__.py, app/agents/sandbox.py, app/agents/tools.py,
app/agents/gate.py, app/agents/candidates.py, app/agents/fix_loop.py,
app/agents/backport.py, app/agents/final_check.py,
app/adapters/fake_codehost.py, app/governance/tokens.py,
app/governance/audience.py, app/routers/fixes.py, app/routers/approvals.py,
web/src/FixPage.jsx, evals/run_g3.py, tests/test_tool_validation.py,
tests/test_allowlist.py, tests/test_no_merge.py, tests/test_tokens.py,
tests/test_gate_parse.py.
Files changed: alembic/env.py (register g3 models), app/settings.py (fix +
sandbox + token settings), app/agents/tools.py (drop pre-check with inherited
stdin; drop unused import), app/agents/fix_loop.py (PATCH_SYSTEM syntax fix),
app/main.py (fix/approval routers), app/worker.py (fix/backport dispatch),
app/mcp_server/server.py (publish_status, request_fix, approve_backport),
app/routers/fixes.py (run filter + candidate detail), web/src/App.jsx (fix
view), web/src/api.js (fix endpoints + getCandidate), README.md (G3 section).

Commands NOT RUN (from issue-intel/):
- `alembic upgrade head`
- `dotnet restore sample_repo/TesseraEditorTools.sln` (once, needs NuGet)
- `python -m evals.run_g3 --adapter fake` (machinery-only)
- `$env:ISSUEINTEL_MODEL_ADAPTER='openai'; ... ; python -m evals.run_g3
  --adapter openai` (real benchmark; see README)
- `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`

Prompt-vs-code mismatches:
- Without a hidden check and with green baselines, the offer rule falls back
  to "green + non-empty diff" (documented in fix_loop.py); the strict
  fail-to-pass rule applies whenever baseline failures or hidden checks exist.
- Machinery benchmark seeds PENDING candidates directly (scripted S7
  confidence is 0.0 and would be REJECTED); eligibility logic itself is
  covered by unit tests, and openai mode uses consider_run.
- Backport benchmark runs backport_pr on OFFERED (not yet human-integrated)
  commits in throwaway worktrees; release branches are never mutated.
- `git apply --check` pre-flight was dropped: it inherited stdin and could
  hang; `git apply` itself validates, after the allow-list pre-check.
