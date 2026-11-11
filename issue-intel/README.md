# Issue Intelligence & Bug-Fix Agent

Practice-scale, self-contained issue-intelligence platform for the fictional
**Tessera Engines** company and its **Tessera Editor** product. All data is
synthetic. No real external services: Jira, Slack, GitHub and docs are local
fakes behind adapter interfaces.

Spec: `info/muse-prompts/issue-intel/BUILD-SPEC.md` (repo root).
Phase prompts: `info/muse-prompts/issue-intel/G0-to-G4-prompts.md`.
Track progress: `issue-intel/PROGRESS.md`.

## Layout

- `app/` — FastAPI app: `gateway/`, `ingest/`, `search/`, `pipeline/`,
  `governance/`, `agents/`, `adapters/`, `mcp_server/`, `routers/`,
  `models/`, `schemas/`
- `synthetic/` — seeded generator; writes `synthetic/corpus/` (CSV + JSON + XML)
- `evals/` — ground truth, fix cases, metric functions, runners, reports
- `sample_repo/` — Tessera Editor Tools C# solution (own git repo once built)
- `web/` — dashboard (G2+)
- `tests/` — pytest suite (fake model adapter, no network)

## Quickstart (from repo root)

```powershell
cd issue-intel
docker compose up -d --build
alembic upgrade head
python -m synthetic.generate --seed 20240917
python sample_repo/setup-history.py
dotnet test sample_repo/TesseraEditorTools.sln
dotnet test evals/fix_cases/FixCases.csproj   # hidden tests: fail before fixes
pytest
ruff check . ; ruff format --check . ; mypy app
```

API: `http://localhost:8010` (`GET /health`). DB: `localhost:5433`, database
`issueintel`. Model calls default to the scriptable fake adapter; set
`ISSUEINTEL_MODEL_ADAPTER=openai` plus `ISSUEINTEL_OPENAI_BASE_URL` /
`ISSUEINTEL_OPENAI_API_KEY` for a real endpoint.

## Ground-truth boundary

`app/` must never import from or read `evals/ground_truth/` or
`evals/fix_cases/`. `tests/test_import_boundary.py` enforces this. Only the
generator (input) and the eval runners (scoring) touch those folders.

## G0 — Scaffold, synthetic world, sample repository

- Settings (`ISSUEINTEL_` env prefix), async SQLAlchemy session, Alembic against
  database `issueintel`, compose stack (api, worker, `pgvector/pgvector:pg16`),
  health endpoint, ruff/mypy/pytest config.
- `ModelGateway`: OpenAI-compatible adapter + scriptable fake, static
  task-type table, per-call logging to `model_calls` (extended in G4).
- `sample_repo/`: Tessera Editor Tools, 27 C# files in `VersionControl`,
  `Localization`, `UiState`, `AssetImport`, xUnit tests. `setup-history.py`
  builds the git history: base commit, one commit per planted bug (two for
  bug12), plus `release/2023.3` (branched after bug04) and `release/2024.3`
  (after bug08), each with two release-note commits.
- 12 planted bugs (`evals/fix_cases/`): hidden xUnit tests + reference
  `fix.patch` each. Eight single-file, three two-file (bug09, bug10, bug11),
  one two-commit interaction (bug12). bug07/bug08 are in `AssetImport`, outside
  the fix allow-list. The on-disk tree is the clean base; bugs are introduced
  by reverse-applying the reference patches in `setup-history.py`.
- Generator: 600 legacy cases, 300 tracker + 150 support tickets, 250 chat
  threads, 40 people (a third LEFT), sample_repo change history (planned
  `SAMPLE-NN` refs), ACLs, 15 prompt-injection samples. Raw formats:
  `legacy_cases.csv`, `tracker_export.json`, `chat_export.xml`. Ground truth:
  duplicates, regressions, outcome labels, chat root cause, injections,
  wrong-module filings.
- Hidden Bug09 test needs ICU data for `tr-TR` casing (present on Windows;
  Linux needs libicu).

## G1 — Knowledge foundation

- Migration 0002: G1 tables, `vector(64)` + HNSW index, `tsvector` + GIN
  index, RLS (`ENABLE` + `FORCE`) with entitlement policies on every table
  carrying `acl_id`. Reads fail closed when the context is unset; inserts are
  service-mediated (`python -m app.ingest.run`).
- Ingest (`app/ingest/`): extract the CSV/JSON/XML corpus → normalise (natural
  keys, idempotent) → ACL tagging → crosswalk (explicit 1.0, mentioned-in-text
  0.9, title similarity ≥ 0.75 at 0.8) → legacy outcome classification
  (`outcome_classify`, batches of 25) → chunk (500 words, 50 overlap) + embed
  → people/ownership map with LEFT-author redirect.
- Entitlements + `SET LOCAL` RLS context as a FastAPI dependency
  (`x-user-id` header, fail closed); `tests/test_rls.py` proves zero rows for
  unentitled users on ORM and raw-SQL paths.
- Hybrid search: FTS + vector + reciprocal-rank fusion, `relevance` rerank
  over the top 30, lineage expansion (duplicates, fixing change, outcome,
  current owner).
- `POST /tickets/{key}/similar`: ranked past cases, lineage, and a synthesis
  whose every claim cites an evidence id; citation check rejects unknown ids.
- Redaction of customer refs/emails for non-SE viewers (second line of
  defence after RLS).
- Evals (`python -m evals.run_g1 --adapter fake`): recall@5/recall@10/MRR on
  duplicate + won't-fix pairs and regression change-hit@5, each in fulltext /
  vector / fused modes; outcome accuracy + per-class F1; leakage rate across
  three users (must be 0). Report: `evals/reports/g1.json`.

## G2 — Investigation pipeline, review, MCP, dashboard

- Migration 0003: `runs`, `run_stages`, `evidence`, `reviews`, `writebacks`,
  `module_rollout`, `jobs`.
- Fake tracker/chat/docs adapters; `python -m app.adapters.replay_cli --n 10`
  replays ticket events into `POST /webhooks/tracker`.
- Run manager: dedupe, `NEW|UPDATE|RERUN` triggers, cache on (ticket, content
  hash, pipeline version `g2.1`), job enqueue. Worker polls `jobs` and runs
  S1–S8, one `run_stages` row per stage (input, output, model, tokens,
  latency, attempt, status, error).
- Failure policy: transient errors (rate limit, timeout, malformed JSON)
  retry twice; anything else stops at `FAILED_AWAITING_HUMAN`. A test covers
  each error class.
- Per-viewer rendering: evidence filtered by entitlement, claims citing
  removed evidence withheld, snippets redacted. Wrong-module tickets show
  only the alert + request-access / notify-owner actions.
- Review API: approve-and-post (tracker adapter + `writebacks` row),
  need-info, wrong, notify-owner; edits and wrong marks become eval cases.
- MCP server (`python -m app.mcp_server.server`, stdio): read-only
  `get_ticket_intelligence`, `search_archives`, `get_change_lineage`; the
  host passes the verified user id, tools reuse HTTP code paths. Claude
  Desktop config: `{"mcpServers": {"issue-intel": {"command": "python",
  "args": ["-m", "app.mcp_server.server"], "cwd": "<repo>/issue-intel"}}}`.
- Dashboard (`web/`, React + Vite, plain CSS): run list, review page with
  citations + review actions, trace page with expandable stage JSON.
  `cd web && npm install && npm run dev` (expects API at `localhost:8010`).
- Evals (`python -m evals.run_g2`): wrong-module F1, change-attribution
  precision@1 (planted bugs incl. the two-commit interaction bug), citation
  correctness, leakage violations per viewer (must be 0), 15 injection
  samples (pass = nothing posted, no payload echo). With `--adapter fake`
  the model-driven metrics use static stage outputs and are labelled
  machinery-only; real numbers need `--adapter openai`.

## G3 — Fix agent, backport agent, approvals

- Migration 0004: `fix_candidates`, `fix_attempts`, `fix_prs`, `final_checks`,
  `approval_tokens`, `audience_profiles`, `developer_profiles`.
- Sandbox: fresh git worktree per attempt under `sandboxes/`; seven tools
  (list, read, search, apply-patch, build, test, evidence) with path
  validation (no absolute paths, no `..`, no symlink escape, writes only to
  `src/<allow-listed module>/`). No shell, network or integration tool — a
  test proves it.
- Fix loop (`app/agents/fix_loop.py`, one readable file): baseline, then
  plan → patch → build → test → revise, bounded by `fix_max_cycles` (3) and
  `fix_token_budget`. Gave-up attempts keep their trace. Offered only when
  ship tests are green and a previously failing test now passes (baseline
  failures, or the caller's hidden check).
- Candidates: module in server allow-list (`VersionControl`, `Localization`,
  `UiState`), S7 confidence ≥ 0.7, module owner opted in. `AssetImport`
  tickets are never attempted (tested).
- PR records in the fake code host (root cause, citations, risk, test
  results, diff); humans approve and integrate through the API; the agent
  cannot integrate.
- Backport agent: cherry-picks integrated fixes to release branches,
  resolving only textual conflicts in allow-listed files
  (`conflict_resolve`), same gate, one PR per branch.
- Final check (`final_check`): `OK|NEED_MORE_INFO|BLOCK` over evidence,
  synthesis, diff and test output; approve requires `OK`.
- Approval tokens: short-lived, single-use, bound to run + ticket + payload
  hash. Dashboard approve mints a `merge_pr` token; MCP write tools
  (`publish_status`, `request_fix`, `approve_backport`) do nothing without a
  valid token. Tests cover expired, reused, wrong-payload and forged tokens.
- Audience profiles (`SE_ENGINEER`, `SUPPORT_PARTNER`, `VENDOR`) applied to
  every outward view including PR records.
- Dashboard fix page: attempts, diff, test output, final-check verdict,
  approve/merge control, backport control.
- Benchmark (`python -m evals.run_g3`): per bug — hidden test flips,
  ship tests green, attempts, tokens, cost — plus the backport benchmark on
  release branches. With `--adapter fake` the loop runs scripted reference
  patches (machinery-only). Against a real model:

```powershell
$env:ISSUEINTEL_MODEL_ADAPTER = "openai"
$env:ISSUEINTEL_OPENAI_BASE_URL = "https://<endpoint>/v1"
$env:ISSUEINTEL_OPENAI_API_KEY = "<key>"
python -m evals.run_g3 --adapter openai
```

Prerequisites for either mode: built sample_repo history, `dotnet restore`
once (NuGet), ingested postgres, generated ground truth.

## G4 — Model gateway (planned)

Versioned routing table, budgets, result cache + batch mode, fallback, shadow
mode, quality-verification step, scorecards + upgrade runbook, metrics
endpoint and dashboard page.
