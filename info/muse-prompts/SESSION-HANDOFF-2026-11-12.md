# Session handoff: Neuralascent, state on 12 November 2026

## 1. Purpose and how to use this note

This note lets a new chat session pick up the Neuralascent project without the owner re-explaining it. It describes the repository, the working method, what has been built and verified, what Claude changed directly, the main open piece of work (the Localization Lab rebuild, called track R), and what still waits on the owner.

Read sections 2 and 3 first. Read section 6 before doing anything to the Localization Lab. Read section 7 before the owner says the rebuild is finished. Section 10 lists mistakes from this session that should not be repeated.

Where this note and a file in the repository disagree, the file is right. Section 10 lists the points that were checked against files and the points that could not be checked.

## 2. Who does what

### Roles

| Who | Role |
|---|---|
| The owner (the user) | Decides scope, runs Muse Code, supplies any API keys, approves any paid provider call, and pushes the branch to the remote when all work is done. |
| Muse Code (called Muse) | An agentic coding command-line tool that the owner runs inside the repository. Muse builds the work from prompt files that Claude writes. Muse cannot run shell commands in this setup. The prompts tell Muse not to run commands and not to commit. |
| Claude | Reads the code, writes precise prompts for Muse, then verifies Muse's output by actually running builds, tests and checks against a real stack. Claude then either writes a correction prompt or reports that the work is green. |

Term: a "prompt" here is a Markdown file in `info/muse-prompts/` that Muse reads and carries out. A "correction prompt" is a prompt written after a check found a problem; they are named `C1` to `C16` (section 3).

### Rules that matter

- Git: local commits only. Do not push, do not open a pull request, do not create or switch branches. The owner pushes once all tracks are done (from the memory file "Muse work: local commits only").
- Claude commits locally on the current branch after a check is green (and commits prompts and logs as they are written). Claude never pushes. The commit-message attribution line comes from the session's own instructions, not from this note.
- Python: `CLAUDE.md` says Claude must never write a Python file anywhere in the repository. Python work is done by Muse from prompts, and Claude reviews and describes it.
- What Claude may edit, as `CLAUDE.md` reads it. The file has a temporary override dated 2026-10-20 at the top. Under that override Claude may edit and create files in `api/` (including `api/Data/*SeedData.cs`) and `app/`. `CLAUDE.md` says "on a branch with a PR as usual"; the owner's later instruction for this work is local commits only, with no pull request. Under the same override Claude may edit `info/` and `exercises/` as the lower sections allow. The lower section titled "NO DIRECT CODE CHANGES" still makes compose files, `.env*` files, deploy scripts, workflows and `CLAUDE.md` itself read-only for Claude. Its exceptions list is the memory directory, `info/`, `exercises/`, and two MCQ JSON files.
- Scope boundary (set 2026-09-04 in `CLAUDE.md`): the AI vertical is course content about AI topics and is written by hand by the owner. Claude must not generate prompts that write AI-vertical lesson content. AI integration is platform code (the chatbot, provider plumbing in `api/` and `app/`) and does use the prompt workflow.
- Prompt style that has worked: one agent, one project folder, ordered tasks. Each task names the file, the current behaviour, the authority for the correct behaviour (the C# code or a written contract), and the exact change. Each prompt says to append to a `PROGRESS.md` file after each task. Each prompt says "never say a test passes; you have not run it", because Muse cannot run tests.
- Muse said "done" once while it was still writing files. Check that files have stopped changing before verifying anything (section 7).

## 3. Where things are

| What | Path |
|---|---|
| Repository root | `C:\Users\balaj\Documents\scaler-education-journey` |
| .NET API (the running app) | `api\` (ASP.NET Core 8 minimal API, EF Core, xUnit tests in `tests\StudyTracker.Api.Tests\`) |
| React app | `app\` (React and Vite, Vitest tests) |
| PostgreSQL | run through Docker Compose; compose files are read-only for Claude |
| Python port of the API | `api-python\` (FastAPI and async SQLAlchemy). Reading reference only; the .NET API is still the running app. |
| Port map and log | `api-python\PORT-MAP.md`, `api-python\PROGRESS.md`, `api-python\tools\parity.py`, `api-python\tools\parity_routes.txt` |
| Port rules | `info\muse-prompts\python-port\PORT-RULES.md` and `info\muse-prompts\python-port\P0-to-P8-prompts.md` |
| Issue-intelligence bot | `issue-intel\` (its log: `issue-intel\PROGRESS.md`) |
| Localization AI service | `localization-ai\` (its log: `localization-ai\PROGRESS.md`) |
| Localization prompts (first build) | `info\muse-prompts\L1-localization-backend.md`, `L2-localization-owner-frontend.md`, `L3-localization-vendor-frontend.md` (these describe the old marketplace design) |
| Issue-intel and localization-ai prompts | `info\muse-prompts\issue-intel\`, `info\muse-prompts\localization-ai\` |
| Correction prompts | `info\muse-prompts\corrections\C1-round1-corrections.md` to `C16-issue-intel-lint-line.md` |
| Round logs | `info\muse-prompts\corrections\round1\` to `round19\` (logs, parity summaries, probe output) |
| Track R prompts | `info\muse-prompts\localization-rebuild\` (`CONTRACT.md`, `R0-index.md`, `R1-...` to `R6-...`) |
| Localization Lab design draft | `info\localization-design\specs\localization-lab-tier-usage-model-DRAFT.md` (revision 2) |
| Other Localization Lab design docs | `info\localization-design\specs\localization-lab-*.md` (older marketplace-era docs: plan, marketplace flow, build prompt, status tracker) |
| Owner's authoritative notes (outside the repo) | `C:\Users\balaj\Documents\claude-queries\raghuram-resume-docs-AI\` with `claude-take\project1-localization-platform-build-guide.md`, `claude-take\project2-issue-intelligence-build-guide.md`, `resume-builder\localization-ai-evolution-handoff-v1.md`, and the `resume-builder\build-spec-*.md` and `stage*.md` files |
| Reference guide for content | `info\.notes\Neuralascent_Master_Reference_Guide_Updated.md` (named in `CLAUDE.md`; not read in this session) |
| Claude's memory files | `C:\Users\balaj\.claude\projects\C--Users-balaj-Documents-scaler-education-journey\memory\` (index in `MEMORY.md`) |

Untracked at the start of this session: the folder `.claude\` in the repository root. It is not part of any work item.

## 4. State of the three projects

All three were built by Muse and checked by Claude on the "fake model" path. A fake model is a stand-in for a real language model or translation provider, so no paid call was made. Results on the fake path say nothing about output quality.

### 4.1 api-python (the Python port of the .NET API)

| Item | State |
|---|---|
| Lint and types | ruff clean and mypy clean (round 16 logs) |
| Tests | 193 passed and 1 skipped, against a real PostgreSQL database (round 16 log) |
| Route parity, API key only | 102 of 102 routes match the .NET API (round 16 `parity-summary.txt`) |
| Route parity, signed in | 124 of 128 steps match (round 16 `auth-summary.txt`). The four differences are random by design: MCQ option order and newly generated ids. |
| Parity tool | `api-python\tools\parity.py` with `api-python\tools\parity_routes.txt` |
| Status | Usable as a reading reference. Not a replacement for the .NET API. |

How parity was measured: both APIs were started against identical data. The seeded database was copied with `CREATE DATABASE ... TEMPLATE ...` so that both had the same rows. Each route was called and the JSON responses were compared after normalising random values. A `185` versus `185.0` difference was fixed in the tool itself (Muse's correction C12 and the later task 3 in its log).

Known gap: the Localization routes in the port are out of date with the .NET API until track R step R6 runs (section 6).

### 4.2 issue-intel (agentic bug-fix bot)

The bot reads a bug report, finds the code, proposes a fix, and checks it. All data is invented ("Tessera Engines"). The stack is FastAPI, SQLAlchemy, alembic, row-level security (a database feature that restricts which rows a role can read), and a C# sample repository with 12 planted bugs.

| Item | State |
|---|---|
| Tests | 75 passed, with a database (round 18 and round 19 logs) |
| Quickstart | Runs end to end (every step exits 0) |
| Sample repository | Its 12 C# tests pass |
| Evaluation G1, G2, G4 | Reports written with zero leakage |
| Fix benchmark G3 | `offered=10/10 flipped=10`. All 10 backports are `OPEN hidden=True`: the backport pull-request record was opened and the bug's hidden test passes on the release branch. Every fix branch was also verified independently (hidden test and ship tests green). Log: `correctionsound18-g3.log`. |
| Retrieval | Full-text recall at 10 is about 0.115 on the synthetic corpus after the any-word query fix (up from 0.003). It is still low. C14 asks for notes on the causes; those notes are in `issue-intel\PROGRESS.md`. |
| Not judged | Vector retrieval cannot be judged yet, because the test runs use fake embeddings. |
| Known leftovers | Three mypy notes in `app\mcp_server\server.py`. They are tied to a pending upgrade of the MCP library, and that upgrade has not been done. |

### 4.3 localization-ai (AI service for the Localization Lab)

The .NET API calls this FastAPI service for three jobs: machine translation with optimisation ("MT Optimize"), quality scoring, and Auto-Route (which decides whether a string needs human review).

| Item | State |
|---|---|
| Tests | 81 passed, 7 skipped. The 7 skipped tests need a real model. |
| Real-stack run of "Run MT Optimize" | Optimised 136 strings. The correction C15 records 136 cache rows and one AI usage entry of 75,102 tokens, from a run with the Task 1 fix applied. After Muse's fix, a second run was served entirely from the cache: 136 cache hits and 0 tokens (`correctionsound19eal-stack-summary.txt`). |
| Not testable on the fake path | Quality scoring and Auto-Route. The fake judge returns no score, so every string fails the scoring step. |

Fix history: C15 corrected a cache insert that failed on the real database schema. The insert did not name two columns (`hit_count` and `created_at`) that the real table requires without defaults. The test schema had defaults, so the tests passed and the real database failed.

## 5. Changes Claude made directly (not through Muse)

| Change | File | Commit (subject) |
|---|---|---|
| The admin "usage by user" endpoint returned 500. EF Core could not translate an ORDER BY on a record built through its constructor. The fix projects to an anonymous type first. | `api\Endpoints\AdminEndpoints.cs` (route `GET /api/admin/usage/by-user`, handler `GetUsageByUserAsync`) | `5aa292d` |
| Three courses shared order values, so list order was not deterministic. Each now has a distinct `orderIndex`: `python-engineering` 6, `ai-infusion` 7, `aws-agentic-ai-bootcamp` 8. | `api\Data\Content\python\course.json`, `api\Data\Content\ai-infusion\course.json`, `api\Data\Content\aws-agentic-ai-bootcamp\course.json` | `deeae89` |
| A run in the Localization Workflow page with failed strings showed "Run successful". It now shows failed (red) or partial (amber). The page reads the failed count from the outcome text. | `app\src\pages\Localization\LocalizationWorkflow.jsx` | `0a99806` |

Other edits Claude made in this session are the prompt files and the track R documents in `info\`.

## 6. The Localization Lab redesign (the main open work)

### 6.1 Background

The Localization Lab is the part of the app where a client (a project owner) sends UI strings for translation, and vendor teams translate and review them. The first build (prompts L1 to L3, and the commits from `0fed3cd` onward) used a credits-and-bidding marketplace: vendors bid on jobs and spend credits. The owner says that design is wrong.

The owner's real model is in notes outside the repository (section 3). Those notes describe the owner's employer work. Take the model from them. Do not copy employer names, client names or text from them into the repository, which uses invented data only.

### 6.2 The model

- No marketplace. Vendor teams are contracted through a service agreement, and the agreement comes with the service.
- Tiers mean the size and capacity of a vendor team, not quality. The sizes are placeholders: Silver 3 linguists per team, Gold 6, Platinum 10.
- Aliases in both directions. A client never sees a vendor's real name. A vendor never sees a project's real name or slug. Only the operations side sees both.
- Machine help is for vendors only. Azure Translator produces a draft, then a model scores the translation from 1 to 5.
- Usage is tracked on the operations side, per project and per month.

### 6.3 Owner decisions (12 November 2026)

| # | Question | Decision |
|---|---|---|
| 1 | What happens at high usage | Hard monthly cap per project. New provider calls stop at the cap. A call already in flight finishes. |
| 2 | Bidding marketplace | Removed. Jobs go to the team named in the service agreement. |
| 3 | Score scale | 1 to 5, shown to vendors only. |
| 4 | Machine-translation provider | Azure Translator only. Google Translate is removed. |

Also decided: the tier sizes above are placeholders, and the operations role is the existing admin role.

The draft spec `localization-lab-tier-usage-model-DRAFT.md` (revision 2) describes budgets that raise an alert but do not stop work. That was written before decision 1. Where the draft and `CONTRACT.md` differ, the contract wins.

### 6.4 Track R: the rebuild, step by step

Track R is written as six prompts in `info\muse-prompts\localization-rebuild\`. The contract is `CONTRACT.md` (every route, JSON shape and fixed string after the rebuild). No step may change the contract. If something cannot be built as written, the step stops that item and reports it. The reviewer changes the contract and tells every track.

| Step | Folder | What it does | Progress file it writes |
|---|---|---|---|
| R1 | `api\`, `tests\` | Usage events, one event per paid provider call, rates table, operations usage endpoints (`/api/localization/ops/usage`, `/usage/events`, `/rates`). Additive; nothing is removed. | `localization-rebuild\PROGRESS.md` |
| R2 | `api\`, `tests\` | Monthly caps per project (machine-translation characters and model tokens), the AI kill switch (`aiEnabled`), controls endpoints, Azure Translator replaces Google Translate. Provider health name becomes `AzureTranslator`. | `localization-rebuild\PROGRESS.md` |
| R3 | `api\`, `tests\` | Service agreements with a tier, team aliases, jobs assigned to a team (`NotCreated`, `Assigned`, `InProgress`, `SubmittedForReview`, `NeedsRevision`, `Approved`), bidding and credits removed, client-visible scores removed, 1 to 5 scores for vendors only. This step removes the most code. | `localization-rebuild\PROGRESS.md` |
| R4 | `app\` | React: the Marketplace tab becomes a Jobs page; the client Strings view loses scores and raw drafts; the vendor portal shows jobs under the client's alias with scores 1 to 5; a new admin-only Operations page shows usage, caps, the AI switch, rates, teams and agreements. No new npm packages. | `localization-rebuild\PROGRESS-frontend.md` |
| R5 | `localization-ai\` | The judge scores 1 to 5 (prompt version `qps_judge_v2`). A translation whose placeholders do not match the source cannot score above 2. Response fields are added (`fallback`, `vetoed`, `operation`, `model`, `promptVersion`). Auto-Route uses the 1 to 5 score and the project threshold. | `localization-ai\PROGRESS.md` |
| R6 | `api-python\` | Brings the Python port's Localization routes, models and services in line with the C# after R1 to R3. Runs after R3 because it copies that C#. | `api-python\PROGRESS.md` (heading "R6 — Localization rebuild port") |

Constraints from `R0-index.md`:

- R1, R2 and R3 edit the same .NET files and must run in that order. R2 should run only after R1 is reviewed and committed; R3 only after R2 is.
- R6 runs after R3.
- R4 and R5 touch only their own folders. They can run at any time, including in parallel with the backend chain: Session A runs R1, R2, R3, R6; Session B runs R4; Session C runs R5.
- The owner was advised to tell Claude "R1 done" before starting R2, so that the migration style is checked before later steps copy it.

Key contract points a checker needs:

- Routes: client routes stay under `/api/localization/projects…`, `/jobs…` and `/provider-health…` (API key only). Vendor routes are under `/api/localization/vendor…` (API key only). Operations routes are under `/api/localization/ops…` and need a signed-in user with role `Admin` and status `Approved`; anyone else gets 403.
- Removed routes: every marketplace route, and the vendor bid and awarded-job routes.
- Fixed strings include the workflow actions "Auto-Translate via Azure Translator" (was "Auto-Translate via Google MT"), "Create Translation Jobs" (was "Post to Marketplace"), and "Score Quality" (was "Score QPS").
- Cap rule: "used" is the sum for the current UTC month. For machine translation the call is skipped if its size would pass the limit. For a model call the call is skipped once used is at or over the limit. A skipped string is left as it was and the run continues.
- Score rule: a score below the project's `qpsThreshold` (default 4) needs review.
- Alias rule: client responses never contain a vendor's real name, scores, raw machine draft or review flag. Vendor responses never contain a project name or slug.

### 6.5 Status

- All six prompts and `CONTRACT.md` are written and committed (commits `02d61c1`, `e3c2b50`, `773721b`).
- Muse has run none of the six steps. Checked on 12 November 2026: no `localization-rebuild\PROGRESS.md` and no `PROGRESS-frontend.md` exist yet.
- The owner plans to run R1 to R6 one by one in Muse, then ask Claude to check everything.

Paste lines for Muse (from `R0-index.md`), one per step, with R1 shown:

```
Read info/muse-prompts/localization-rebuild/R1-usage-metering-backend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

The same form is used for R2, R3, R4, R5 and R6 with the matching file names.

### 6.6 Parts of the owner's notes that track R does not cover

Each of these is its own later piece of work: XLIFF download and upload as a second vendor mode, placeholder masking before the translation provider, a golden set with a held-out calibration split, batch scoring in word-count chunks, a retranslation bucket chosen by the team lead, a done-guard that blocks submit until scoring finishes, in-editor client review, and content-filter handling.

## 7. Verification plan (when the owner says track R is finished)

Do these in order. Do not run anything until step 1 passes.

1. Confirm Muse has really finished. Check the modification times of the files each prompt names, and check the three progress files (`localization-rebuild\PROGRESS.md`, `localization-rebuild\PROGRESS-frontend.md`, `localization-ai\PROGRESS.md`, `api-python\PROGRESS.md`). Confirm the files have stopped changing. Read `git status --short` (read-only) to see what changed.
2. .NET backend: build the solution and run the xUnit tests in `tests\StudyTracker.Api.Tests\`.
3. Migrations: run the three hand-written R migrations against a real PostgreSQL database in two ways. First from an empty database. Second from a database migrated only to the previous migration. Both must succeed.
4. EF model snapshot: generate a throwaway migration in a container and check that it is empty. A non-empty result means the snapshot file and the model disagree.
5. Real stack: database, .NET API, `localization-ai` with fake providers, and the React app. Then in a browser, signed in as an admin, click through Workflow, Jobs, Strings, the vendor portal and the Operations page.
6. Caps and kill switch: set a very low cap on a project and confirm that the run stops making calls and reports the skipped count. Turn the AI switch off and confirm the four provider actions return 409 and the three stage actions still work.
7. Privacy checks on the responses: client responses must contain no score, no raw draft and no vendor real name. Vendor responses must contain no project name or slug. Check the JSON, not only the screen.
8. `localization-ai`: run lint, type checks and tests. Call `/qps-score` and `/auto-route` directly and check the new response shapes in section 7 of the contract.
9. `api-python`: run lint, type checks and tests with a database. Then run the live parity comparison against the .NET API for both the API-key routes and the signed-in routes (`tools\parity.py`).
10. Where anything fails, write a correction prompt for the folder concerned, using the style in section 2. Commit locally when a folder is green; never push.

Rule from this session: run end to end, not only unit tests (section 10).

## 8. How verification is run on this machine

- Docker runs only inside WSL (Windows Subsystem for Linux). Use WSL for anything that needs Docker. The memory file "Local machine tooling" records that WSL goes idle and stops containers unless something keeps it awake, and that the PATH was once corrupted.
- Python checks run in `python:3.12-slim` containers.
- .NET checks run in `mcr.microsoft.com/dotnet/sdk:8.0` on a tar copy of `api` and `exercises` that excludes `bin` and `obj`. (The .NET SDK is also installed on Windows, per the memory file. Both are true; this session used the container for every .NET check so that the API ran next to the database on the Docker network.)
- WSL scripts are run through the PowerShell tool with `wsl -- bash <script>`. Git Bash mangles paths and quoting for these scripts.
- Keep WSL awake with `wsl -- bash -lc "sleep N"` in the background while a long check runs.
- Real-stack pattern: start a throwaway `pgvector/pgvector:pg16` container. The .NET API runs `--migrate`, then `--seed-reference-data`. For the Python port, copy the seeded database with `CREATE DATABASE ... TEMPLATE ...` so both APIs see identical data.
- Signed-in checks: sign up on each API, approve the account as admin with SQL, log in, enrol a TOTP authenticator (a time-based one-time password app), confirm it with a code computed from the secret, then call routes with the session cookies.
- Probe technique: apply candidate fixes with `sed` to a throwaway copy of a container, to find which failures sit behind the first ones. Only then write the correction prompt. Probe results in the round folders (for example `round17\probe\`) are evidence of what a fix does.
- SQL goes through `psql`, for example `docker exec -i <container> psql ... <<'SQL' ... SQL`. Do not type SQL into the shell directly.
- Database names: local compose uses container `studytracker-postgres`, user `studyuser`, database `studytracker`. Production uses `StudyTrackerDB`. The API container is `studytracker-api`.
- The helper scripts for these steps were kept in a session scratchpad directory that will not exist in a new session. They must be rewritten when needed.
- Seeding gotcha (from `CLAUDE.md`): restarting the API does not seed. Lessons whose `ContentBody` includes the three marker headings are never overwritten by the seeder. To force a reseed, check the content status first, reset the lessons, and run the seeder through Compose. The full steps are in `CLAUDE.md`.

## 9. Waiting on the owner

| Item | Why it waits |
|---|---|
| Real-model and Azure runs for all three projects | They cost money and need the owner's keys and an explicit go-ahead. Claude must not start a paid call on its own. |
| `AzureTranslator__Key`, `AzureTranslator__Region`, optionally `AzureTranslator__Endpoint` | After R2, the owner must add these to the compose and `.env` files. Neither Claude nor Muse edits those files. The Google Translate key can then be removed. |
| Pushing the local commits | Owner only, once all tracks are done. |
| Track R steps R1 to R6 | Owner runs them in Muse one by one and tells Claude when all six are finished (a check after R1 alone was recommended but is the owner's choice). |
| The parts of the owner's notes that track R does not cover (section 6.6) | Not yet scheduled. |
| Decisions on the three mypy notes in `issue-intel` | Depend on the MCP library upgrade. |

## 10. Lessons from this session, and what could not be checked

### Lessons

- Read the C# before prescribing a change to a port. A correction once asked for a title lookup to be case-insensitive. The C# uses ordinal (exact, case-sensitive) comparison, so the instruction was wrong. Always read the authority first.
- A correction once added a rollback to a session helper. The rollback expired loaded objects, and code that read them after the block broke. The unit tests did not cover this; only an end-to-end run showed it. Run end to end, not only the unit tests.
- The first specification draft for the Localization Lab was written from the chat alone, and it had the commercial model wrong. Read the owner's notes folder first, every time.
- Once, Muse reported "done" while it was still writing files. Check that files have settled before verifying.
- Fake-path results prove the wiring, not the output quality. Quality scoring and Auto-Route cannot be proved without a real model.

### Points checked against files

Confirmed from files: the 35 local commits (the count and list in section 11); the round 16 parity figures (102 of 102 and 124 of 128); the 193, 75 and 81 test counts; the G3 result `offered=10/10 flipped=10`; the three course `orderIndex` values; the admin endpoint fix; the Workflow page change; the draft's alert-only wording; the three mypy notes; the fact that no track R progress file exists yet.

Points the note-writing agent could not confirm from files, resolved afterwards by the session that ran the checks:

- The second "Run MT Optimize" run served from the cache is recorded in `correctionsound19eal-stack-summary.txt` (136 hits, 0 tokens).
- `OPEN hidden=True` for a backport means the backport record is open and the hidden test passes on that release branch.
- .NET checks were run in the SDK container; the SDK on Windows also exists.
- `CLAUDE.md` has two sections that disagree about whether Claude may edit `api\` and `app\`. The override at the top (dated 2026-10-20) allows it and says it takes precedence.

The four lessons above describe mistakes made earlier in the same session; they are recorded in the correction prompts C6 (case-insensitive lookup reverted), C14 Task 2 (rollback regression) and in the draft spec's revision note (r1 written from chat alone).

## 11. The local commits on the branch

Branch `muse/tracks-la-p-g`, 35 commits ahead of `main`, listed with `git log --oneline main..HEAD` on 12 November 2026 (newest first):

```
773721b Track R: API contract and all six rebuild prompts (R1-R6), with the owner's four decisions
e3c2b50 R1 prompt: correct the file that defines LocalizationAiException
02d61c1 Track R (Localization Lab rebuild): index and R1 prompt for usage metering
0a99806 Workflow page: show a run with failed strings as failed or partial, not successful
8442aee localization-ai cache insert fixed against the real schema (Muse C15); issue-intel lint line (Muse C16)
11a50e2 issue-intel end-to-end fixes (Muse C14): quickstart, evals and fix benchmark all run; C16 prompt for one lint line
7f557af Rewrite the tier-usage draft from the owner's design notes: capacity tiers, no marketplace, operations-side metering
7d19455 Draft spec: tier-based Localization Lab service with metered Azure Translator and GPT-4.1 usage
3ca32b1 Browser click-through of the localization AI actions against the real stack; C15 prompt
289cd2d First end-to-end run of issue-intel (history, C# tests, ingest, evals): logs and C14 prompt
30515dd api-python signed-in parity fixes (Muse C13): 102 of 102 API-key routes and 124 of 128 signed-in steps match
5aa292d Signed-in parity run of api-python against the .NET API; fix admin usage-by-user 500; C13 prompt
deeae89 Distinct course order values in the content manifests; api-python matches the .NET API on 102 of 102 routes
16c03b0 api-python parity fixes (Muse C12): 99 of 102 routes match the .NET API
57489dd api-python parity fixes (Muse C11): 93 of 102 routes match the .NET API; C12 prompt
a31be52 Parity run of api-python against the .NET API: logs and C11 prompt
7f53f3b issue-intel green against a real database (Muse C10)
0a9c948 issue-intel: service session rollback, token and RLS test fixes (Muse C9); C10 prompt
a306f8c localization-ai green with database tests (Muse C7); issue-intel RLS enforced via app role (Muse C8); C9 prompt
4aac990 api-python green against a real database (Muse round 6); DB-test correction prompts for localization-ai and issue-intel
c8b5528 WIP: Muse round 5 for api-python, round 6 logs and prompt
780d061 WIP: Muse round 4 for api-python, round 5 logs and prompt
8be9d4d issue-intel: Azure OpenAI and Claude in Foundry adapters behind the model gateway (Muse A1)
bafec01 Add A1 Muse prompt: Azure OpenAI and Claude in Foundry behind the model gateway
cf113fd Add Azure managed-services mapping for the bug-fix agent
d242d08 WIP: Muse round 3 for api-python, LA1 migration, seed JSON, round 4 prompt
86e0442 WIP: Muse round 2 corrections, round 3 logs and api-python repair prompt
35407e2 WIP: Muse round 1 corrections, round 2 check logs and correction prompt
4d5538c Add round 1 check logs and correction prompt for the LA, P and G tracks
dfaab0d WIP: Muse output for the LA, P and G tracks, unverified
d9349b6 Add Muse build prompts and restore the Localization Lab spec docs
afa6f90 Correct the Localization Lab vendor portal against the locked-scope design
c85e78a Seed translations for the submitted and approved Localization locales
e812165 Correct the Localization Lab owner app against the design spec
0fed3cd Enforce the Localization Lab marketplace job lifecycle on the server
```

Commits of note: `0fed3cd` to `e812165` and `afa6f90` belong to the first marketplace-era Localization build, which the owner has since rejected. `dfaab0d` and the WIP commits are Muse output that was not verified when committed.
