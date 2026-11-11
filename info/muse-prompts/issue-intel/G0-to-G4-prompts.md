# Issue Intelligence & Bug-Fix Agent — phase prompts

Run in order, one Muse session per phase, with a review between phases. This track touches only `issue-intel/`, so it can run alongside every other track.

Paste **one** block (between two `=====` lines) per session, at the repository root.

=====

## G0 — Scaffold, synthetic world, sample repository

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` in full and follow it.

Build the foundation; no retrieval and no model-driven logic yet.

1. The `issue-intel/` layout, settings, async database session, Alembic set up against a database named `issueintel`, `docker-compose.yml` (api, worker, `pgvector/pgvector:pg16`), health endpoint, lint, type-check and test configuration.
2. `ModelGateway` with the OpenAI-compatible adapter and the scriptable fake adapter, the static task-type table, and per-call logging to a table.
3. `sample_repo/`: a small C# solution, **Tessera Editor Tools**, about 25–35 source files in four modules (`VersionControl`, `Localization`, `UiState`, `AssetImport`) with an xUnit test project. Create it as its own git repository inside `issue-intel/sample_repo/` with a `main` branch and two release branches (`release/2023.3`, `release/2024.3`) that have diverged from `main` by a few commits each. It must build and its tests must pass.
4. Planted bugs: 12 realistic defects, each introduced by a specific commit on `main` (some also present on a release branch), each with a hidden test kept **outside** `sample_repo/` in `evals/fix_cases/` that fails before the fix and passes after, and a reference fix stored there as a patch. Mix: eight single-file bugs, three that need changes in two files, one caused by the interaction of two commits. Two of the twelve are in `AssetImport`, which will be outside the fix allow-list.
5. `synthetic/`: a seeded, deterministic generator producing the Tessera corpus:
   - about 600 legacy tracker cases (ids `LGC-…`) with free-text resolutions, including won't-fix, by-design, hardware-limitation, duplicate and regression outcomes;
   - about 300 current tracker tickets (`TES-…`) and 150 support tickets (`SUP-…`), some of them re-reports of legacy cases under different wording;
   - about 250 chat threads, some containing the real root cause of a case spread over several messages, most of them noise;
   - 40 people, a third of whom have left, with an ownership map of modules and paths to current owners;
   - the commit and PR history of `sample_repo/`, linked to the cases the planted bugs caused;
   - ACLs: three departments, restriction levels, and customer-restricted cases;
   - 15 prompt-injection samples planted in ticket bodies and chat messages.
   The generator writes the corpus to `synthetic/corpus/` as files in three deliberately different raw formats (a legacy CSV export, tracker JSON, a chat export), and writes ground truth separately to `evals/ground_truth/`.
6. A test that fails if any module under `app/` imports from or reads `evals/ground_truth/` or `evals/fix_cases/`.

Done when BUILD-SPEC's definition of done is met, `dotnet test` passes in `sample_repo/`, each hidden test fails on `main` and passes with its reference patch applied (show the table), and running the generator twice with the same seed produces identical output.

=====

## G1 — Knowledge foundation: ingest, links, search, cited answers

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` and `issue-intel/README.md`.

1. Alembic migration for the G1 tables, including the pgvector HNSW index, the `tsvector` column and index, and row-level security policies on every table that carries an `acl_id`.
2. Ingestion, one module per step in `app/ingest/`: extract the three raw formats → normalise to cases, threads and changes → tag ACLs → crosswalk ids between legacy, tracker and support records (from explicit fields first, then ids mentioned in text, then similarity above a high threshold, each link recording how it was found and a confidence) → classify the outcome of every legacy case (`outcome_classify`, in batches) → chunk and embed → build the people and ownership map. Ingestion is idempotent: running it twice changes nothing.
3. Entitlements and the `SET LOCAL` row-level-security context as a FastAPI dependency. Tests prove that a user without access to a module gets zero rows from every query path, including raw SQL issued through the session.
4. Hybrid search in `app/search/`: full-text and vector queries, reciprocal rank fusion, a rerank step over the top 30 (`relevance`), then lineage expansion along `links` (duplicates, fixing change, outcome, current owner when the author has left).
5. `POST /tickets/{key}/similar`: returns ranked past cases with outcomes, fixing changes, who to ask now, and a synthesised answer in which every claim cites an evidence id; a citation check rejects any answer citing an id that was not retrieved.
6. Redaction for restricted fields as the second line of defence.
7. Evals: retrieval recall@5, recall@10 and MRR on the duplicate, regression and won't-fix pairs; outcome-classification accuracy and per-class F1; leakage test across three users with different entitlements. Also report full-text only, vector only and fused, so the value of hybrid search is visible.

Done when the definition of done is met and the leakage rate is 0.

=====

## G2 — Investigation pipeline, review, MCP, dashboard

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` and `issue-intel/README.md`.

1. Migration for the G2 tables.
2. Fake tracker, chat and docs adapters. The tracker fake accepts webhooks from a small CLI that replays ticket events (created, updated, commented) from the corpus.
3. Run manager: dedupe events, classify `NEW | UPDATE | RERUN`, cache on (ticket, content hash, pipeline version), enqueue a job. The worker executes stages S1–S8 exactly as BUILD-SPEC describes, writing one `run_stages` row per stage with its input, output, model, tokens, latency and status.
4. The failure policy from BUILD-SPEC, with a test for each class of error.
5. Per-viewer rendering of a cached run under the viewer's entitlements, including withholding synthesis sentences whose citations were removed.
6. Review API: approve and post, need more info, mark wrong, notify owner. Approval writes the comment through the fake tracker adapter and records a `writebacks` row. A reviewer's edit or "wrong" mark is stored as a new eval case.
7. Wrong-module handling: when S2 says the ticket belongs to a module the viewer cannot access, the viewer sees the alert and the two actions (request access, notify the owning team) and none of the restricted evidence.
8. MCP server with three **read-only** tools: `get_ticket_intelligence`, `search_archives`, `get_change_lineage`. It authenticates the caller, resolves the same entitlements as the HTTP API, and reuses the same code paths. Document in the README how to connect a local MCP client to it.
9. Dashboard in `issue-intel/web/` (React + Vite, plain CSS, no component library): a ticket list, a review page (synthesis, evidence with citations, the review actions) and a trace page (one row per stage, expandable input and output JSON).
10. Evals: wrong-module F1, change-attribution precision (including the two-commit interaction bug), citation correctness, leakage per viewer, and the 15 injection samples (pass means the planted instruction changed nothing in tools called, filters applied or text posted).

Done when the definition of done is met, leakage is 0, and replaying ten ticket events produces ten reviewable runs in the dashboard.

=====

## G3 — Fix agent, backport agent, approvals

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` and `issue-intel/README.md`.

1. Migration for the G3 tables.
2. Sandbox and tools in `app/agents/`: fresh worktree per attempt, the seven tools from BUILD-SPEC, path validation on every call (reject absolute paths, `..`, symlinks out of the worktree, writes outside the allow-list). Unit-test the validation with hostile inputs.
3. The fix agent loop as BUILD-SPEC describes: explicit, bounded, traced. Each iteration stores what the model asked for, what the tool returned, and tokens used. The loop code must be readable top to bottom in one file; no framework.
4. The gate: `dotnet build` and `dotnet test` in the worktree, with timeouts. Parse results into pass/fail counts and the failing test names and messages that are fed back to the model.
5. Fix candidates: allow-list (`VersionControl`, `Localization`, `UiState`; `AssetImport` excluded), confidence threshold, owner opt-in. A test proves a ticket in `AssetImport` is never attempted.
6. PR records in a fake code host adapter; a human approves and merges through the API. The agent has no merge capability; a test proves it.
7. Backport agent and final check as BUILD-SPEC describes.
8. Approval tokens: approving in the dashboard mints a short-lived, single-use token bound to the run, the ticket and a hash of the payload. Add MCP **write** tools (`publish_status`, `request_fix`, `approve_backport`) that do nothing without a valid token. Tests cover expired, reused, wrong-payload and forged tokens.
9. Audience profiles applied to every outward view, including PR records.
10. Dashboard: a fix page showing attempts, the diff, test output, the final-check verdict and the approve/merge control.
11. Evals: run the agent on the ten in-scope planted bugs. Report, per bug and in total: hidden test passes, no existing test broken, attempts used, tokens, cost. Run the backport benchmark on the bugs present on release branches. These need a real model; with the fake adapter, drive the loop with scripted responses that apply the reference patch, to prove the machinery, and label the result as machinery-only.

Done when the definition of done is met and the README explains how to run the fix benchmark against a real model endpoint.

=====

## G4 — Model gateway: routing, budgets, shadow, upgrades

Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` and `issue-intel/README.md`.

1. Migration for the G4 tables.
2. Replace the static task-type table with a versioned routing table stored in the database: per task type a primary model, a fallback, a token limit and a mode (`SYNC | BATCH`). Exactly one version is active; switching version is one audited operation and the previous version stays available for rollback.
3. Budget guard per run, per day and per product; a call that would exceed a budget fails with a clear error and is logged.
4. Result cache for identical inputs, and a batch mode that queues non-urgent calls and runs them together through the worker.
5. Fallback: on a provider error the gateway uses the fallback model and records that it did.
6. Shadow mode: a configurable share of live calls is also sent to a candidate model; the candidate's output is stored for comparison and never returned to the caller.
7. A quality-verification step (`quality_verify`) before the final check, so that only packages that pass a cheaper check reach the expensive one; record how many are filtered.
8. Scorecards: an eval command that runs every task suite against a named model and writes quality, cost per resolved case and p95 latency per task type. A report command prints incumbent against candidate.
9. An upgrade runbook in the README following: offline eval → shadow → canary on one module → switch routing version → rollback path, with the exact commands for each step in this project.
10. Metrics endpoint and dashboard page: cost per resolved case, share of calls going to the most expensive tier, final-check send-back rate, fix acceptance rate, leakage.

Done when the definition of done is met, a test demonstrates a full switch and rollback of the routing version, and a test demonstrates that shadow output cannot reach a caller.
