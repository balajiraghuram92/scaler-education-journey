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

## G4 — Model gateway: routing, budgets, shadow, upgrades

Status: finished (code written; nothing run — shell unavailable).

Most of G4 already existed on disk from earlier phases; this entry
completes the missing and half-written parts (items 4, 8, 9, 10 below)
and records the per-item state.

Item by item (G4 prompt in `info/muse-prompts/issue-intel/G0-to-G4-prompts.md`):
1. Migration — done (already on disk): `alembic/versions/0005_g4_routing.py`
   (`routing_versions` + one-active partial index, `model_scorecards`,
   `budgets`, four new `model_calls` columns, seeded v1).
2. Versioned routing table — done (already on disk):
   `app/gateway/routing.py` (`get_active`, `create_version`,
   `switch_version`, `rollback`), used by `ModelGateway.route_for` with
   canary support. This round adds the CLI (`list|show|create|switch|
   rollback`) so switching is runnable as one audited command.
3. Budget guard — done (already on disk): `app/gateway/budgets.py`
   (run/day/product, `BudgetExceeded`), hooked into `complete`/`embed`.
4. Result cache + batch mode — done this round: the cache and
   `enqueue_batch`/`execute_batch_job` existed, but the worker rejected
   `batch_call` jobs (`ValueError: unknown job kind`). `app/worker.py`
   now dispatches them and lets `execute_batch_job` own the job status.
5. Fallback — done (already on disk): `ModelGateway.complete`
   retries the route's fallback model and logs `fallback_used`.
6. Shadow mode — done (already on disk): `_maybe_shadow` with
   `ISSUEINTEL_SHADOW_MODEL`/`ISSUEINTEL_SHADOW_SHARE`, `is_shadow`
   logging, never returned. This round adds the isolation test.
7. `quality_verify` step — done (already on disk):
   `app/agents/final_check.py` screens before `final_check`; filtered
   packages are `NEED_MORE_INFO` rows with a `filtered by
   quality_verify: ` reason, counted by the metrics endpoint.
8. Scorecards — done this round (was missing): `evals/run_g4.py`
   (`score --model` stores quality, cost per resolved case, p95
   latency per task type in `model_scorecards`; `report --incumbent
   --candidate` prints them side by side). `outcome_classify` is
   real accuracy vs ground truth; other chat tasks are contract
   conformance; embed is dimension conformance; `--adapter fake` is
   machinery-only. `p95` added to `evals/metrics.py` (+ unit test).
9. Upgrade runbook — done this round (was missing): README G4
   section with offline eval → shadow → canary → switch → rollback
   and the exact commands for each step.
10. Metrics endpoint + dashboard page — done this round (was
    missing): `GET /metrics` (`app/routers/metrics.py`) and the
    dashboard Metrics page (`web/src/MetricsPage.jsx`).

Done-criteria tests (both new in `tests/test_routing.py`):
- switch + rollback of the routing version (needs DB, cleans up).
- shadow output cannot reach a caller (pure, deterministic).

Files created (4): evals/run_g4.py, app/routers/metrics.py,
web/src/MetricsPage.jsx, tests/test_routing.py.
Files changed: app/worker.py (batch_call dispatch), app/gateway/routing.py
(CLI), app/main.py (metrics router), web/src/api.js (getMetrics),
web/src/App.jsx (Metrics view), evals/metrics.py (p95),
tests/test_metrics.py (p95 test), README.md (G4 section, runbook).

Commands NOT RUN (from issue-intel/):
- `alembic upgrade head`
- `python -m app.gateway.routing list`
- `python -m evals.run_g4 score --model tessera-small --adapter fake`
- `python -m evals.run_g4 report --incumbent tessera-small --candidate X`
- `curl localhost:8010/metrics`
- `pytest`, `ruff check .`, `ruff format --check .`, `mypy app`

Prompt-vs-code mismatches:
- Scorecard "quality" is contract conformance except for
  `outcome_classify` (real accuracy); reusing the full G1/G2/G3
  suites per task type would need DB-backed runs per model and is
  left as labelled future work.
- Fix acceptance = MERGED / all FIX PRs; send-back = final checks
  with verdict != OK (includes quality_verify-filtered rows).
- Leakage metric counts `LeakageError` stage failures; per-viewer
  leakage stays in the G1/G2 eval runners.

## Round 1 corrections

Reviewer log: `info/muse-prompts/corrections/round1/issue-intel.log`.
Nothing run this round (no shell); no test, lint run or eval is
described as passing.

1. Install failure — fixed. `pyproject.toml:27-28` adds
   `[tool.setuptools.packages.find]` with `include = ["app*",
   "evals*", "synthetic*"]`, so `web/`, `sample_repo/` and
   `alembic/` are excluded from the build. New
   `requirements.txt` (runtime set, pins reused from
   `ai-agent/requirements.txt` and
   `localization-ai/requirements.txt`) and new
   `requirements-dev.txt` (`-r requirements.txt` + pytest,
   pytest-asyncio, ruff, mypy). sqlalchemy, asyncpg, alembic,
   mcp, aiosqlite and pytest-asyncio are left unpinned with a
   "reviewer will pin" comment: no version verifiable offline.
2. Nine test files read against the code — one real bug fixed,
   two lint-adjacent fixes (see item 3):
   - `tests/test_tokens.py:20`: arguments were scrambled
     (`validate_token("run1", "TES-1", "merge_pr", token, ...)`),
     which only proved that an unknown token fails. Now a
     correct-order wrong-payload check (`pr_id` 999), which also
     proves a failed validation does not consume the token.
   - `tests/test_failure_policy.py:73`: loop-variable closure
     (`raise error` bound late); now bound as a default arg.
   - `tests/test_rls.py:13`: dropped unused `Acl` import.
   - The other six files (`test_allowlist`, `test_gateway_fake`,
     `test_health`, `test_ingest_idempotent`, `test_rendering`,
     `test_wrong_module`) match their code: signatures, imports,
     counts and idempotency expectations verified by reading;
     no changes.
3. mypy 56 + ruff 24 — all 24 ruff errors fixed by hand; 24
   mypy errors fixed at their causes:
   - One missing import caused ruff F821 + mypy name-defined:
     `app/pipeline/manager.py:17` now imports `run_stage`.
   - `app/search/hybrid.py:55-69`: `_rrf` rewritten with
     separate score/row dicts (removes the mistyped list and
     the wrong-`ignore` comment); `:87` fixes a real bug
     (`query_text and query_vector` passed where a vector was
     required); `:40-42` wrapped (E501).
   - `app/ingest/run.py:30-45`: one reused loop variable
     caused all 6 errors; now `raw_case`/`raw_person`/
     `raw_change`/`raw_thread`.
   - no-any-return fixed with explicit `... | None`
     annotations: `app/ingest/normalise.py:16,37,57,76,93`,
     `app/gateway/routing.py:38-44,65-70`,
     `app/agents/candidates.py:26`; `app/gateway/cache.py:44`
     returns `int(job.id)`; `app/db.py:21` gains `-> AsyncEngine`.
   - ruff I001 fixed by hand (straight imports first, matching
     the files ruff already passed): `alembic/env.py:11-19`,
     `alembic/versions/0001:10-11`, `0002:10-11`, `0003:10-12`,
     `0004:10-12`, `0005:11-13`, `app/mcp_server/server.py:16-20`.
   - ruff E501 wrapped without behaviour change:
     `alembic/versions/0002:22-34` (SQL split across lines),
     `app/agents/sandbox.py:30-34`, `app/settings.py:42-44`,
     `evals/run_g1.py:185-190`,
     `sample_repo/setup-history.py:84-85` (same commit string),
     `synthetic/world.py:248-250`.
   - ruff F401 removed: `app/adapters/fake_tracker.py:7`,
     `app/gateway/cache.py:8`, `evals/run_g3.py:33`,
     `tests/test_rls.py:13`.
   - `UP041`: `app/agents/sandbox.py:27`
     (`asyncio.TimeoutError` → `TimeoutError`); `B007`:
     `app/pipeline/stage_fns.py:163` (`base` → `_base`);
     `E741`: `synthetic/world.py:87` (`l` → `last`).
   - NOT fixed (32 mypy errors: 12 `misc` subclass-of-Any, 20
     `untyped-decorator`): these come from fastapi/pydantic/
     sqlalchemy/mcp being unimportable in the reviewer's
     container (install failed, `ignore_missing_imports`
     turned them into `Any`). They should clear once item 1
     lets the install succeed; adding ignores would become
     unused-ignore errors under `strict` in that world.
   - `ruff format --check` (89 files) left alone: reformatting
     is out of scope for this round.
4. G4 entry — written (see G4 section above): disk state
   compared against the ten G4 items; finished the worker
   batch dispatch, scorecard commands, runbook, metrics
   endpoint + dashboard page, and the two done-criteria tests.
5. setup-history.py — confirmed by reading against
   `evals/fix_cases/bugs.json`: `git init -b main`, base commit,
   one commit per bug (bug12 in two per-file commits via
   `git apply -R --include=...`), `release/2023.3` branched
   after bug04 and `release/2024.3` after bug08 with two
   release-note commits each, ends on `main`. Branch contents
   match the manifest (`release/2023.3`: bug01-04;
   `release/2024.3`: bug01-08). Reviewer command (from
   issue-intel/): `python sample_repo/setup-history.py`.
   Unresolved: whether `git apply -R --include=<file>`
   applies cleanly per file for bug12's two-file patch can
   only be shown by running it.
6. Corpus/ground-truth commands (from issue-intel/, verified
   against `synthetic/generate.py:19-41`, which writes the
   corpus to `synthetic/corpus/` and moves ground truth to
   `evals/ground_truth/`):
   `python -m synthetic.generate --seed 20240917`
   (one command produces both; `--seed` defaults to the same
   value in `synthetic/data.py`).

## Round 2 corrections

Reviewer log: `info/muse-prompts/corrections/round2/issue-intel.log`.
Nothing run this round (no shell); no test, lint run or eval is
described as passing.

1. Pins — fixed, except mcp (see item 4). `requirements.txt:10-12,16`
   (`sqlalchemy[asyncio]==2.1.8`, `asyncpg==0.32.0`,
   `alembic==1.20.1`, `aiosqlite==0.22.1`),
   `requirements-dev.txt:6` (`pytest-asyncio==1.4.1.post1`), all
   copied exactly from the log's `pip freeze` section.
   `pyproject.toml:5-21` now carries the same `==` pins in
   `dependencies` and in the `test`/`lint` extras. Header comments
   refreshed; the stale "reviewer will pin" comments are gone.
2. Gate parser — fixed in the parser, tests untouched.
   `app/agents/gate.py:10`: `SUMMARY_RE` now expects the real
   order, `Failed: N ... Passed: M`; `:31-32` assign group 1 to
   `failed` and group 2 to `passed`. Note: the item says padding
   is the cause, but `\s*` already tolerated padding — the actual
   cause was the reversed order (the old pattern wanted
   Passed-before-Failed, while the tests and `dotnet.log:9` show
   Failed-then-Passed). Traced by reading: GREEN yields
   failed=0/passed=12 with no `FAILED_RE` hit; RED yields
   failed=1/passed=11 plus the one `Failed <name>` line.
3. Seven tools — the spec (`BUILD-SPEC.md:101`) lists seven: list
   files, read file, search text, apply patch, run build, run
   tests, read the evidence pack. `test_no_merge.py` untouched.
   - `evidence_pack`: folded in. It was a data field, not a tool,
     but its default made it visible to `dir(Tools)`. Renamed to
     the private field `_evidence_pack` (`app/agents/tools.py:36,
     :120`); `read_evidence` still serves it. Only caller data
     flow is positional (`fix_loop.py:101`), and no code reads
     `.evidence_pack`, so the rename is contained.
   - `patch_files`: removed from `Tools`, now a module-level
     function (`app/agents/tools.py:23-29`); `apply_patch` calls
     it (`:94`). `tests/test_tool_validation.py:10,76-77` now
     imports and calls the module function instead of the
     `Tools.patch_files` static method.
   `dir(Tools)` non-underscore names are now exactly the seven
   the test expects.
4. mypy — `app/mcp_server/server.py` NOT ported: I do not know the
   MCP 2.x Python SDK server interface for certain, so per the
   item I did not guess. Constrained instead, with a comment in
   each file: `requirements.txt:15`, `requirements-dev.txt:9`
   (`mcp<2`, mirroring the runtime file), `pyproject.toml:15`
   (`mcp>=1.4,<2`). `app/pipeline/manager.py:95-98`: the line-94
   lambda is now a typed nested `async def _call` with the stage
   function bound as a default arg (same pattern as the round-1
   `test_failure_policy` closure fix); signature matches
   `run_stage`'s `Callable[[], Awaitable[dict[str, Any]]]`.
5. ruff I001 — fixed by hand in all six files. Cause:
   `pyproject.toml` lists `alembic` in `known-first-party`, so
   `from alembic import ...` must stand in its own first-party
   block, not grouped with third-party sqlalchemy; straight
   imports stay first within each block. `alembic/env.py:4-18`
   (alembic moved below the `app.models` straight imports),
   `0001:10-12`, `0002:10-12`, `0003:10-13`, `0004:10-13`,
   `0005:11-14` (alembic split into its own block).
6. `ruff format` left alone: no reformatting changes.

Unresolved: the exact mcp 1.x version is unpinned (`mcp<2` /
`mcp>=1.4,<2`) — no 1.x version was verifiable offline, so the
reviewer's install resolves it. Whether the 1.x API then type-
checks clean against `server.py` can only be shown by running
mypy with that install.

## A1 — Azure models

Step 1 of `AZURE-MAPPING.md`. No commands run; nothing here is
claimed to pass.

Task 1. **Settings** (`app/settings.py:20,52-60`): added
`openai_api_key_header` (`Literal["bearer", "api-key"]`, default
`"bearer"`) after `openai_api_key`, and a commented Anthropic block
(`anthropic_base_url` default `""`, `anthropic_api_key`,
`anthropic_version` `"2023-06-01"`, `anthropic_max_tokens` 4096,
`anthropic_model_prefixes` default `["claude-"]`) plus `model_prices`
(default empty dict, USD per 1k tokens (input, output)). Every
existing field and default untouched.

Task 2. **Adapters** (`app/gateway/adapters.py`):
`OpenAICompatAdapter.__init__` gained `key_header` (default
`"bearer"`) and `transport` (default `None`); `_headers` returns the
`api-key` header in api-key mode, Bearer otherwise; both
`AsyncClient` calls pass `transport`. New
`AnthropicMessagesAdapter` (POST `{base}/v1/messages`, `x-api-key`
+ `anthropic-version` headers, `{model, max_tokens, system,
messages}` body, concatenated text blocks, `usage` token counts
defaulting to 0, OpenAI-style latency; `embed` raises
`NotImplementedError`) and new `RoutedAdapter` (first prefix match
wins, else default; both methods; no logging). `price_of` gained
`overrides` (looked up first, then `PRICES`, then the default
rate). `ModelAdapter` and `AdapterResult` untouched.

Task 3. **Wiring** (`app/gateway/gateway.py`): `_build_adapter`
passes `key_header` to the OpenAI adapter and, when
`anthropic_base_url` is non-empty, returns a `RoutedAdapter`
wrapping it with one `(prefix, anthropic)` entry per
`anthropic_model_prefixes` entry; empty base URL returns the
OpenAI adapter alone, `"fake"` unchanged. All five
`price_of(...)` calls (estimate, chat cost, embed estimate,
embed cost, shadow cost) now pass
`self._settings.model_prices` as `overrides`. `complete`,
`embed`, `route_for` and logging otherwise untouched; no
provider logic added to the gateway.

Task 4. **Tests** (new `tests/test_gateway_providers.py`, 8
tests, `asyncio.run` style like `test_gateway_fake.py`, all
HTTP via `httpx.MockTransport`): bearer default (auth
header, no api-key, `/chat/completions` URL, text + token
counts); api-key mode (api-key present, no Authorization);
Anthropic URL/headers/body shape plus two-text-blocks-
concatenated and usage counts; Anthropic `embed` raises;
`RoutedAdapter` prefix selection via two `FakeAdapter`
`calls` lists; cross-provider fallback through a
`_StaticRouteGateway` subclass carrying a fixed
primary-gpt/fallback-Muse `Route`; `price_of` override vs
table; default `Settings()` stays offline (`fake` /
`bearer` / empty base URL). Not covered, as the prompt
allows: the DB-backed versioned-routing path
(`get_active`/`route_from_dict` in `test_routing.py` needs
Postgres), so test 6 drives adapter + gateway objects
directly with a fixed route instead of a routed version.

Task 5. **README** (`README.md`): new section "Running against
Azure (optional)" with the `ISSUEINTEL_`-prefixed variable
table (`MODEL_ADAPTER`, `OPENAI_BASE_URL`, `OPENAI_API_KEY`,
`OPENAI_API_KEY_HEADER`, `ANTHROPIC_BASE_URL`,
`ANTHROPIC_API_KEY`, `TASK_MODELS`, `MODEL_PRICES`), an
example `TASK_MODELS` sending `fix_plan`/`fix_patch`/
`final_check` to a fake `claude-` deployment and the rest to
fake OpenAI deployments, and the three required statements
(deployment names; embeddings stay 64 because the adapter
truncates; real-model evals cost money and must be labelled
with model names). Placeholders only; nothing about creating
Azure resources.

## C8 — database test corrections

Nothing run this round (no shell); no test, lint run or eval is
described as passing.

Task 1 — `SET ... = :v` cannot take a bind parameter. Fixed in
`app/governance/rls.py`: `rls_session` now uses
`SELECT set_config('app.X', :v, true)` for the three settings and
`service_session` uses `SELECT set_config('app.X', :v, false)`;
values stay bound parameters, the three `RESET` statements are
unchanged, and the module docstring no longer says `SET LOCAL`.

Task 2a — new migration `alembic/versions/0006_app_role.py`
(`down_revision` 0005_g4_routing): creates role `issueintel_app`
(NOLOGIN NOSUPERUSER NOBYPASSRLS) guarded by `IF NOT EXISTS`,
grants membership to `CURRENT_USER`, schema/table/sequence
privileges and default privileges, each statement through
`op.execute`; `downgrade()` revokes the schema/table/sequence
and default privileges and leaves the role in place. Corrected
only the comment at `0002_g1_knowledge.py:19-20`: `FORCE`
covers the table owner, a superuser still bypasses it, the app
switches to `issueintel_app` (migration 0006).

Task 2b — `app/governance/rls.py`: added `APP_ROLE =
"issueintel_app"`; `rls_session` runs `SET LOCAL ROLE
issueintel_app` first inside `session.begin()`; `service_session`
runs `SET ROLE issueintel_app` first and `RESET ROLE` after the
three `RESET` statements. Full entitlements unchanged.

Task 2c — sessions that do not go through the helpers (one line per call site):
- `app/db.py:31 get_session()`: reads/writes no tables itself and has no callers in the repo; stays as is.
- `app/ingest/run.py:60 _main()`: writes all five RLS tables (`cases`, `threads`, `messages`, `changes`, `chunks`) plus `acls`, `people`, `links`, `ownership`; moved to `service_session()` (service work; multi-commit ingest matches its session-level context).
- `evals/run_g1.py:143 leakage_eval()`: reads only `acls` (plus `rls_session` reads elsewhere); stays as is.
- `evals/run_g1.py:174 _main()`: reads RLS tables (`cases`, `threads`, `changes`, `chunks` via `retrieval_eval`/`outcome_eval`); moved to `service_session()` (service work; read-only, no transaction conflict).
- `evals/run_g4.py:193 cmd_score()`: writes only `model_scorecards`; stays as is.
- `app/governance/rls.py:66-68 rls_session_dep()`: reads only `entitlements` via `resolve_entitlements`; stays as is.

Task 2d — `tests/test_rls.py`: `_seed` and `_cleanup` now run
inside `service_session()` with a commit at the end; the `url`
argument is unused (settings come from the monkeypatched env)
but both signatures are kept because the caller passes `url`.
`test_unentitled_user_sees_zero_rows` gains a `SELECT
current_user` check for `issueintel_app`. New
`test_insert_outside_entitlement_is_refused` (same skip when no
database) creates the `VersionControl`/`SE`/`SE` ACL through
`service_session()`, then expects `DBAPIError` on flush of an
outside-entitlement `Case` inside narrow `rls_session`.

Task 3 — `test_switch_and_rollback`: in `switch_version`
(`app/gateway/routing.py`) added `await session.flush()` after
the deactivate loop and before `target.active = True`, so the
two `UPDATE`s stay ordered in one transaction. Nothing else in
the function changed; index and migration untouched.

## C9 — database test corrections, second run

Reviewer log: `info/muse-prompts/corrections/round8/issue-intel-db.log`
(68 passed, 3 failed). Nothing run this round (no shell); no
test, lint run or eval is described as passing.

Task 1 — `service_session` hid the original error. In
`app/governance/rls.py`, `await session.rollback()` is now
the first statement of the `finally` block, before the
three `RESET app.*` statements and `RESET ROLE`, so the
resets run on a usable transaction and the real error
surfaces. Nothing else in the function changed;
`rls_session` untouched (its `session.begin()` already
rolls back, and its settings are transaction-local).

Task 2 — token tests mint tokens for runs that do not
exist. In `tests/test_tokens.py`: new `_make_runs`
helper inserts `Run` rows through `service_session()`
with a commit, filling the non-nullable columns read
from the model (`id`, `ticket_source`, `ticket_key`,
`trigger`, `pipeline_version`, `content_hash`;
`status`/`cost_usd`/`created_at` have Python-side
defaults, `finished_at` is nullable). Both tests use
unique ids (`f"tok-{uuid.uuid4().hex[:12]}"`) in place
of the `"run1"`/`"run2"`/`"run3"` literals everywhere,
including `validate_token` arguments; `"other"` and
`"r"` stay literal as specified. Each test wraps its
body in `try`/`finally` calling new
`_delete_runs_and_tokens`, which deletes tokens then
runs for those ids through `service_session()`. No
assertion changed; `tokens.py` and the foreign key
untouched. Verified by search: no `"run1/2/3"`
literals remain.

Task 3 — RLS test counted other tests' rows. In
`tests/test_rls.py` `_query`: `n_orm` selects
`select(Case).where(Case.source == "TEST")` and
`n_raw` runs `SELECT id FROM cases WHERE source =
'TEST'` (both wrapped to stay within the 100-char
limit). Added after `assert n_orm == n_raw == 1`:
with `Entitlements.service()` (the same full
entitlements `service_session` uses),
`full_orm == full_raw == 2`, proving both seeded
rows exist and the policy hides the second one.
Thread/change/chunk counts and everything else in
the file unchanged.

## C10

Reviewer log: `info/muse-prompts/corrections/round9/issue-intel-db.log`
(70 passed, 1 failed). Nothing run this round (no shell);
nothing here is claimed to pass.

The one task — `_make_runs` gave every run the same
`(ticket_key, content_hash, pipeline_version)`, violating
`uq_runs_ticket_hash_version` on the second insert. In
`tests/test_tokens.py` only:
`content_hash=hashlib.sha256(run_id.encode()).hexdigest()`
(unique per run since the run ids are unique), plus
`import hashlib` in alphabetical stdlib order.
`ticket_key`, `pipeline_version`, and everything else
unchanged.

## C14 — end-to-end run corrections

Reviewer logs: `info/muse-prompts/corrections/round17/`
(first-run failures plus a probe patch confirming the
fixes work together). Nothing run this round (no
shell); nothing here is claimed to pass.

Task 1 — xUnit test projects now import `Xunit`.
Added the `<Using Include="Xunit" />` `ItemGroup` to
`sample_repo/tests/TesseraEditorTools.Tests/
TesseraEditorTools.Tests.csproj` and
`evals/fix_cases/FixCases.csproj`, and the same
`Using` line to `HIDDEN_CSPROJ` in `evals/run_g3.py`
next to the `Compile` item. No `using Xunit;` added
to any `.cs` file. README quickstart now records the
expected `FixCases` result on `main` (16 failed, 5
passed — the bugs are still planted).

Task 2 — `service_session` detaches before rollback.
`finally` is now `session.expunge_all()`, then
`await session.rollback()`, then the RESETs;
docstring says why both lines exist (detached rows
keep loaded values; rollback keeps RESETs usable
after a failed flush). Call sites checked
(`service_session` unless noted; "inside" means the
block result is plain data or fully consumed
before exit):
- ESCAPED before, fixed by expunge: `candidates.
consider_run` (:22, returns the row),
`render_for_viewer` (`render.py:43`),
`_approve_backport` (`mcp_server:206`,
`candidate.*` after), `_execute_fix`
(`worker.py:33`, `attempt.*` after),
`leakage_per_viewer` (`run_g2:140`),
`_seed_candidate` (`run_g3:94`, returns the row),
`_run_bug` (`run_g3:143`, `attempt.*` after),
`_backport_benchmark` (`run_g3:197`, `made` rows
after), `cmd_report` (`run_g4:229`).
- Inside/safe: `candidates:73`, `cache.py`
(38,46,57,77,84), gateway `routing.py`
(111,127,144,151,158), `audience.py` (19,36),
`tokens.py` (33,51), `ingest/run.py:61`,
`mcp_server` (35,101,149,161,178,189,232),
`manager.py` (42,81), `approvals.py`
(48,79,118,132), `fixes.py` (27,35,45,61,81,
112,130 — the `consider_run` row at 27/33 is
covered by the candidates fix), `metrics.py:29`,
`reviews.py` (34,71,94), `runs.py` (32,52,82),
`worker.py` (38,61,66,98,105), `run_g1.py:174`,
`run_g2.py` (62,112,171,188,214,233 —
188 only tests list emptiness), `run_g3.py`
(187,221).
- `rls_session`: `rls.py:84` yields the session by
design; `mcp_server` (119,129) JSON inside;
`run_g1.py:161` counts inside; `run_g1.py:146`
reads loaded `acl_id` after exit but the block
commits via `session.begin()` with
`expire_on_commit=False` (confirmed
`app/db.py:27`), so nothing expires — safe.
New DB `tests/test_service_session.py`: a row
loaded inside the block stays readable after it,
and a duplicate-key flush still raises the
original `IntegrityError` (no C9 test file
existed for that behaviour, so this file pins
it too).

Task 3 — `await` inside `sum()` generator. In
`evals/run_g1.py`, `_entitled` is now a plain
`def` (it does no I/O) and line 158 drops the
`await`; it has no other caller. Sweep of `app/`
and `evals/`: all `sum(` (19 sites), `any(` (2),
`sorted(` (13), `max(` (9) call sites iterate
plain sync data with no `await`; no builtin
`min(` or `all(` call exists (the `all(` hits are
`.all()`, `.findall()` and `*Call(`). Nothing
else to fix.

Task 4 — sandbox root is absolute. `create_sandbox`
starts with `root = root.resolve()`; nothing else
in the function changed. The `issue-intel/` prefix
workarounds in `fix_loop.py:97-99` and
`backport.py:35-37` are left as is. Sandbox
directory in both cases is `<repo>/issue-intel/
sandboxes/`: from `issue-intel/` the relative root
`sandboxes` resolves against the process CWD;
from the repo root the workaround prefixes
`issue-intel/` first and the same absolute path
results. Added `sandboxes/` to `.gitignore` (was
not ignored). New `tests/test_sandbox.py` (skips
without git on `PATH`): relative root yields an
absolute existing path, `remove_sandbox` removes
it.

Task 5 — verification directory gains its parents.
`hidden_passing` in `evals/run_g3.py:72` now uses
`proj_dir.mkdir(parents=True, exist_ok=True)`, so
the `hidden_dir / "verify"` and backport `tmp /
f"bp-{row.id}"` calls work when `tmp` does not
exist yet.

Task 6 — full-text matches any term. `_fulltext`
in `app/search/hybrid.py` uses the reviewer's
probe form verbatim in both places
(`replace(plainto_tsquery(...)::text, '&',
'|')::tsquery`, still ordered by `ts_rank`):
plainto output contains only `&` operators, so
the rewrite is exact for these queries, and an
empty or all-stop-word query yields an empty
tsquery that matches no rows without raising.
Recall-limit notes for the reviewer: (a) chunks
are whole-message/section pieces, so one shared
word retrieves a long chunk and `ts_rank` (default
normalisation) dilutes single-term matches
against longer texts; (b) the query is a whole
ticket title plus body, whose rare discriminating
terms drown among common words once OR-ed; (c)
lexeme mismatch (stemmer splits compounds and
identifiers the writers kept whole) still drops
true duplicates. No tuning done. New DB
`tests/test_hybrid_search.py`: a chunk sharing
most query words is returned, one sharing none
is not (seeded rows removed afterwards).
