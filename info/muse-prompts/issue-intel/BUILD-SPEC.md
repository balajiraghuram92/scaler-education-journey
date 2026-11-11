# Issue Intelligence & Bug-Fix Agent — build specification

Every phase prompt (`G0` … `G4`) tells Muse to read this file first.

## What this is

A practice-scale, self-contained Python system that does what an enterprise "issue intelligence" platform does:

1. recovers knowledge that was lost when a company migrated its bug tracker, source control and chat tools;
2. investigates each new ticket automatically against that history, with citations and permission checks;
3. drafts code fixes and backports for a safe, allow-listed part of a codebase, with tests and a human as the gate;
4. routes model calls by cost and quality, and changes models only on evidence.

It is built to be read and learned from, and to be demonstrated end to end on a laptop.

## Hard rules

- **Synthetic data only.** The company, product, tickets, chat threads, people and code are all invented by this project. Do not use, imitate or reference any real company's internal systems, ticket ids, repository names, people or data. The fictional company is **Tessera Engines**, its product is the **Tessera Editor**, and its support organisation is **Sustained Engineering (SE)**.
- **Everything lives under a new top-level folder `issue-intel/`.** Nothing else in the repository is edited. The repo's `CLAUDE.md` is addressed to a different assistant and its "no Python" rule does not apply to this task.
- **No real external services.** Jira, Slack, GitHub and the documentation service are local fakes behind adapter interfaces. No network call leaves the machine except to the configured model endpoint.
- **A human approves every write.** Nothing is posted to the (fake) tracker or chat, and no branch is merged, without a recorded approval.
- **Leakage must be zero.** No evidence a viewer is not entitled to may reach a prompt, a response or a log for that viewer. This is tested, not assumed.

## Stack

Python 3.12 · FastAPI · Pydantic v2 · pydantic-settings · SQLAlchemy 2 (async, asyncpg) · Alembic (this project owns its own database, `issueintel`, in the local `pgvector/pgvector:pg16` container) · pgvector + PostgreSQL full-text search · `httpx` · the official Python MCP SDK · `pytest` · `ruff` · `mypy`.

No agent framework. The investigation pipeline is a fixed sequence of plain functions; the fix agent is an explicit, bounded tool-calling loop written by hand, so every step can be read and traced.

Background work uses a simple database-backed job table and a worker process. Do not add Celery, Redis or a message broker.

## Model access

One internal `ModelGateway` is the only code allowed to call a model.

- Adapters: an OpenAI-compatible HTTP adapter (chat and embeddings; base URL, key and model names from settings), and a deterministic, scriptable fake used by every test.
- Callers ask for a **task type** (`ticket_parse`, `module_check`, `relevance`, `synthesis`, `outcome_classify`, `fix_plan`, `fix_patch`, `conflict_resolve`, `quality_verify`, `final_check`, `embed`), never for a model name. In phases G0–G3 a static table in settings maps task type to model. G4 replaces the table with a versioned routing table.
- Every call is logged: task type, model, tokens in and out, cost, latency, run id.

## Layout

```
issue-intel/
  README.md
  docker-compose.yml           api, worker, db (pgvector), all local
  alembic/
  app/
    main.py  settings.py  db.py
    gateway/                   ModelGateway, adapters, routing, budgets
    ingest/                    extract, normalise, crosswalk, outcomes, chunk+embed, ownership
    search/                    hybrid search, rerank, lineage expansion
    pipeline/                  run manager and stages S1..S8
    governance/                entitlements, RLS context, redaction, audience profiles, approvals
    agents/                    fix agent, backport agent, final check, sandbox, tools
    adapters/                  fake tracker, fake chat, fake code host, fake docs service
    mcp_server/                MCP tools
    routers/                   HTTP API
    models/  schemas/
  evals/                       golden data, metric functions, runners, reports
  synthetic/                   generators and the generated corpus
  sample_repo/                 small C# solution with tests; the code the fix agent works on
  web/                         dashboard (G2)
  tests/
```

## Data model (grows by phase)

G1: `cases` (source `LEGACY|TRACKER|SUPPORT`, source key, module, title, body, status, raw resolution, normalised `outcome` `WONT_FIX|BY_DESIGN|HW_LIMITATION|DUPLICATE|REGRESSION|FIXED|UNKNOWN`, fixed-in version, customer reference, acl) · `threads`, `messages` · `changes` (commit or PR, author, reviewers, files, merged at, legacy id) · `chunks` (owner, text, embedding, tsvector, acl) · `links` (from, to, kind `SAME_ISSUE|DUPLICATE_OF|FIXED_BY|MENTIONS|CAUSED_BY|AUTHORED_BY`, evidence, confidence) · `people` (status `ACTIVE|LEFT`, team) · `ownership` (path or module → current owner) · `acl` (modules, departments, restriction `OPEN|SE|CUSTOMER_RESTRICTED`) · `users`, `entitlements` · `eval_cases`.

G2: `runs` (ticket, trigger `NEW|UPDATE|RERUN|MANUAL`, pipeline version, content hash, status, cost) · `run_stages` (stage, model, input and output JSON, tokens, latency, status, error) · `evidence` · `reviews` (decision `APPROVED|NEED_INFO|WRONG|NOTIFY_OWNER`, edits, reason) · `writebacks` · `module_rollout` · `jobs`.

G3: `fix_candidates` · `fix_attempts` · `fix_prs` (kind `FIX|BACKPORT`) · `final_checks` (verdict `OK|NEED_MORE_INFO|BLOCK`) · `approval_tokens` · `audience_profiles` · `developer_profiles`.

G4: `routing_versions` · `model_calls` · `model_scorecards` · `budgets`.

## Permission model

- Every chunk, case, thread and change carries an `acl_id`.
- A request resolves the user to entitlements (modules, departments, maximum restriction level), opens a transaction, sets them with `SET LOCAL`, and PostgreSQL row-level security filters every query. Retrieval therefore cannot return what the user may not see; redaction afterwards is a second line of defence, not the first.
- An investigation run is computed **once per ticket version** under a service identity with full SE access and cached. Each viewer then gets a view of it rendered under their own entitlements and audience profile (`SE_ENGINEER`, `SUPPORT_PARTNER`, `VENDOR`): evidence they may not see is removed and any sentence of the synthesis that cites removed evidence is withheld.
- Text from tickets, chat and code is untrusted. It is always passed to models inside delimited data blocks, it can never choose a tool, a filter or an ACL, and tool arguments are never taken from evidence text without validation against the database.

## The investigation pipeline (G2)

| Stage | Task type | Does |
|---|---|---|
| S1 ticket parse | `ticket_parse` | module, version, error strings, stack frames, legacy ids |
| S2 module check | `module_check` | is the ticket filed under the right module? (wrong-module detection) |
| S3 ticket retrieval | `relevance` | hybrid search over cases + lineage expansion |
| S4 chat retrieval | `relevance` | thread-level vector search, top 15 → relevance filter → read whole selected threads |
| S5 code lineage | — then `relevance` | candidate changes = version window × implicated files × linked cases; single-change or multi-change regression |
| S6 docs | — | product documentation lookup through the fake docs adapter |
| S7 synthesis | `synthesis` | structured answer: seen before?, outcomes, likely cause, fix or workaround, who to ask now; every claim cites an evidence id |
| S8 checks | — | schema validation, citation check (every cited id exists in the evidence), leakage check |

Failure policy: a failed stage stops the run at `FAILED_AWAITING_HUMAN`. Only transient errors (rate limit, timeout, malformed JSON) retry, at most twice. No stage is ever skipped silently.

## The fix agent (G3)

- A ticket becomes a fix candidate only if its module is in a server-side allow-list of paths in `sample_repo/`, the synthesis confidence is at or above a threshold, and the module owner has opted in.
- The agent works in a fresh git worktree of `sample_repo/` inside a sandbox directory. Its tools are: list files, read file, search text, apply patch, run build, run tests, read the evidence pack. Tools reject any path outside the worktree and any path outside the allow-list for writes. There is no shell tool and no network tool.
- Loop: plan → patch → build → test → read failures → revise. Bounded by a maximum number of build/test cycles (default 3) and a token budget per fix. When a bound is hit, the attempt ends as `GAVE_UP` with its trace kept.
- The gate is `dotnet build` and `dotnet test` on the worktree. A fix that does not make a previously failing test pass, or breaks a passing one, is not offered.
- Output: a branch in the local repository plus a "PR" record in the fake code host (title, root cause, evidence citations, risk note, test results, diff). A human approves and merges through the API; the agent cannot merge.
- Backport agent: after a fix is merged on `main`, cherry-pick it to each affected release branch; resolve only textual conflicts in allow-listed files with the `conflict_resolve` task; run the same gate; open one PR record per branch.
- Final check: a `final_check` call over the whole package (evidence, synthesis, diff, test output) returns `OK`, `NEED_MORE_INFO` or `BLOCK`, stored on the run and shown before the human approves.

## Evaluation (every phase adds to it)

Metric functions are pure and unit-tested; runners write results to the database; a report command prints the table.

- Retrieval: recall@k and MRR on known duplicate, regression and repeated won't-fix pairs.
- Outcome classification: accuracy and per-class F1 on labelled legacy cases.
- Pipeline: wrong-module F1, change-attribution precision, citation correctness.
- Safety: leakage rate per audience profile (must be 0); prompt-injection cases planted in tickets and chat (the planted instruction must have no effect).
- Fix agent: tests pass, matches the known fix's behaviour (the planted bug's hidden test passes), attempts used, cost per accepted fix.
- Gateway: quality, cost per resolved case, latency per model and task type.

Because the corpus is generated, the generator also writes the ground truth (which cases are duplicates, which change caused which regression, what the fix is). The system under test never reads the ground-truth files; only the eval runners do, and a test enforces that import boundary.

## Definition of done for every phase

1. `ruff check`, `ruff format --check`, `mypy app` and `pytest` pass in `issue-intel/` with the fake model adapter and no network.
2. The phase's eval runner runs and its report is pasted in the final message. Numbers produced with the fake adapter are labelled as such.
3. `README.md` is updated: what the phase added, how to run it, how to read it.
4. The final message lists files created, command output, and anything in the prompt or this spec that could not be done as written. Report problems; do not work around them silently.
