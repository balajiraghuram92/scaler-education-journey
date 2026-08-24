# Neuralascent Redesign — Chat Handoff and Current Workspace State

**Date:** 2026-08-23  
**Repository:** `scaler-education-journey`  
**Branch at capture:** `main`  
**Purpose:** Chronological handoff of the decisions, evidence, runtime debugging, and current implementation state from the redesign/migration conversation.

This file is an operational handoff, not a replacement for the existing architecture, migration, content, or phase-evidence documents. Repeated details are intentionally referenced below.

## 1. Source-of-truth document map

Use these existing documents instead of duplicating their detailed material here:

| Need | Existing source of truth |
|---|---|
| Old live website behavior, route inventory, old-to-new content crosswalk, reusable curriculum catalog | [`website-comparison-baseline.md`](website-comparison-baseline.md) |
| Target architecture, class diagrams, PostgreSQL schema, migration phases, invariants, testing, risks | [`technical-migration-architecture.md`](technical-migration-architecture.md) |
| Preserve/migrate/retire decisions and implementation order | [`redesign-data-migration-plan.md`](redesign-data-migration-plan.md) |
| Phase checklist, evidence rules, blockers, and human sign-off | [`migration-execution-tracker.md`](migration-execution-tracker.md) |
| Detailed prompts for the local LLM | [`local-llm-migration-prompts.md`](local-llm-migration-prompts.md) |
| Production deployment, backup, migration, cutover, and rollback procedure | [`runbooks/production-deployment-runbook.md`](runbooks/production-deployment-runbook.md) |
| Earlier phase implementation evidence | [`migration-evidence/`](migration-evidence/) |
| Redesign visual/technical specification and phased tracker | [`../../study-tracker-webpage-redesign.md`](../../study-tracker-webpage-redesign.md) |

### Documentation consistency note

The evidence files were created at different points in the migration. Some older documents say code verification passed or recommend staging review, while the execution tracker and stabilization ledger correctly retain blockers for live PostgreSQL, Docker, backup/restore, reconciliation, and deployment verification. Treat runtime evidence from the current VM and the execution tracker as authoritative for execution status; do not infer production readiness from a code-only audit.

No credentials, API keys, database passwords, raw database dumps, or personal note content belong in this file.

## 2. Original objective captured in the conversation

The requested work was not a visual carbon copy of the old website. The intended redesign was to:

- use the supplied reference images and Warm Editorial visual direction;
- preserve the old website's vital learning data and user-facing meaning;
- re-orient old verticals, tasks, lessons, projects, certifications, profile information, progress, and relationships into the new learning-index experience;
- avoid deleting legacy data before a verified mapping and rollback plan exists;
- decide deliberately what PostgreSQL data is preserved, aliased, migrated, retired, or eventually archived;
- keep old API compatibility while adding structured v2 APIs and new page flows;
- verify the redesigned website page by page against the old content and live behavior.

The supplied old changeset was:

```text
8ac02c2947c3e3096f78517266bb4beb7d9d1969
```

The current branch head during this handoff was:

```text
0828c50 fixed fronend issues on react tolowercase error
```

The old changeset and current redesign comparison are already documented in [`website-comparison-baseline.md`](website-comparison-baseline.md); the full old curriculum catalog should not be copied into this handoff.

## 3. Live website and repository findings

### Live-site access

- The bare IP site `https://98.130.44.145/` had a certificate-name mismatch in browser verification.
- The domain `https://neuralascent.top/` was reachable during the recorded inspection.
- The reachable live domain served the old dashboard, not the new Warm Editorial redesign.
- The old site exposed meaningful content across Home, FDE Curriculum, Lab Projects, Azure Certifications, FDE Self-Study, Java & Spring Architecture, Profile, and Certifications.
- `/lab-projects` on the old site represented a broader FDE specialization/competence workspace, not merely the two seeded project rows.
- The old navigation dynamically exposed meaningful verticals and curriculum entry points that the redesigned navigation initially no longer surfaced.

The route-by-route facts, observed counts, old navigation behavior, and old-to-new crosswalk are maintained in [`website-comparison-baseline.md`](website-comparison-baseline.md), especially its live-site verification, content catalog, and page-by-page comparison sections.

### Redesign intent established

The reference material defines four connected experiences:

1. **Knowledge Atlas / Home** — domains, concepts, prerequisites, relationships, and next lessons.
2. **Reading Map / Progress** — reading queue, revisits, deferrals, activity, and knowledge threads.
3. **Map a New Chapter / Curriculum Import** — Markdown-to-structured-chapter authoring and relationship persistence.
4. **Concept Chapter / Learning** — text-first reading room with contents, prose, code, diagrams, notes, related concepts, and navigation.

The visual direction is Warm Editorial: parchment/paper surfaces, serif display typography, humanist sans-serif body text, sage accents, hairline rules, restrained interactions, and no return to dashboard-heavy gauges, radar charts, percentage donuts, or generic SaaS cards.

## 4. Migration planning completed before runtime work

The conversation produced and stored:

- a senior-level migration architecture with current/target class diagrams;
- additive PostgreSQL schema definitions and EF Core changes;
- ownership rules and legacy compatibility boundaries;
- phased migration sequencing from discovery and recovery through bake review;
- API, app, database, deployment, rollback, observability, and acceptance requirements;
- a phase tracker with evidence gates;
- detailed local-LLM prompts, including a master execution contract and independent audit prompt.

These are already represented by [`technical-migration-architecture.md`](technical-migration-architecture.md), [`redesign-data-migration-plan.md`](redesign-data-migration-plan.md), [`migration-execution-tracker.md`](migration-execution-tracker.md), and [`local-llm-migration-prompts.md`](local-llm-migration-prompts.md). The migration should be restarted from an evidence-first inventory rather than assuming every local-LLM claim is accurate.

### Important planning rule retained

“Implemented in source” is not the same as “migrated and verified.” A phase is complete only when its environment, commands, migration IDs, counts/checksums, API probes, UI probes, and rollback evidence are recorded. The tracker defines the accepted evidence format.

## 5. VM/Docker runtime context

The user runs Docker inside a Linux VM on macOS to simulate an AWS Linux host. Therefore:

- commands shown in this section must be executed in the Linux VM, not assumed to reflect the macOS Docker daemon;
- `localhost` inside the VM and `localhost` in a macOS browser are different endpoints unless VM port forwarding is configured;
- the project directory used in the VM was:

```text
~/Desktop/git-raghu/scaler-education-journey
```

The relevant containers are:

| Container | Role | Port |
|---|---|---:|
| `studytracker-db` | PostgreSQL 16 Alpine | Internal backend network |
| `studytracker-api` | .NET 8 API | VM `5000` → container `8080` |
| `studytracker-app` | React/Vite production bundle served by Nginx | VM `80` |

The normal local-dev Compose invocation is both Compose files together:

```bash
sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  up -d --build --force-recreate
```

`docker-compose.yml` supplies the runtime API and database services. `docker-compose.dev.yml` changes the API/app images to local builds and passes `VITE_API_KEY` as a React build argument.

## 6. Runtime issues found and resolved in the conversation

### 6.1 Earlier database/schema warnings

Historical container logs included errors such as:

```text
relation "reading_map_items" does not exist
column l.difficulty does not exist
```

These indicate that the database schema in that VM was not at the same migration level as the application image at that time. They are separate from API-key authentication. The PostgreSQL locale warning was benign.

The correct migration mode is explicit and must target the exact VM database:

```bash
sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm api dotnet StudyTracker.Api.dll --migrate
```

Do not use `down -v` during troubleshooting because it destroys the PostgreSQL volume and data. Backup/restore and migration evidence requirements remain in [`migration-execution-tracker.md`](migration-execution-tracker.md) and [`runbooks/production-deployment-runbook.md`](runbooks/production-deployment-runbook.md).

### 6.2 API build and tests

The user ran the .NET checks inside the VM:

```text
dotnet build api/StudyTracker.Api.csproj
Build succeeded — 0 warnings, 0 errors

dotnet test tests/StudyTracker.Api.Tests/StudyTracker.Api.Tests.csproj
Passed: 69, Failed: 0, Skipped: 0
```

The current workspace shell is macOS and does not have `dotnet` installed, so the additional backend changes made in this handoff must be rebuilt and tested again inside the VM.

### 6.3 API-key failure and final working configuration

The API returned:

```text
401 Unauthorized — Invalid or missing API Key.
```

The cause was identified precisely:

- the API container had its configured `API_KEY`;
- the shell initially sent a different placeholder key;
- the VM reported that `sudo -E` was ignored, so exported shell variables did not reach Compose;
- `VITE_API_KEY` was initially missing or different, and React receives it at build time rather than runtime;
- Nginx only forwards the browser's `x-api-key` header and does not inject one.

The durable solution is to keep matching values in the VM `.env` file:

```env
API_KEY=<one actual local/VM value>
VITE_API_KEY=<the exact same value>
```

Then always use `--env-file .env` with Compose. Do not rely on `sudo -E` in this VM. The API-key hash was used for comparison during debugging but the raw key must not be committed or documented.

The diagnostic sequence proved:

1. API container key hash matched `.env` `API_KEY`.
2. The React build argument existed but initially had the wrong length/hash.
3. The proxy route worked when curl supplied the correct key.
4. The browser bundle eventually embedded `VITE_API_KEY`.

The API key is intentionally visible in a Vite client bundle in this VM test design. That is not a suitable production authentication model; the AWS design should use a proper user/session or server-side secret boundary as described in [`technical-migration-architecture.md`](technical-migration-architecture.md).

### 6.4 Knowledge Atlas `toLowerCase` crash

After authentication was fixed, the browser showed:

```text
TypeError: e.toLowerCase is not a function
```

The cause was a response-contract mismatch:

- `GET /api/v2/knowledge-atlas` returned object arrays for `outgoingRelations`, `nextLessons`, and `prerequisites`.
- The React popover treated lesson entries as strings and called `.toLowerCase()`.
- The initial selected concept opened the popover immediately, exposing the mismatch during the first render.

This was fixed in the current workspace by:

- adding display labels and target slugs in [`api/Services/AtlasQueryService.cs`](../../api/Services/AtlasQueryService.cs);
- normalizing string/object prerequisite and lesson values in [`app/src/pages/Home.jsx`](../../app/src/pages/Home.jsx);
- making [`app/src/components/ConceptDetailPopover.jsx`](../../app/src/components/ConceptDetailPopover.jsx) defensive for both legacy strings and v2 objects.

No database migration is required for this UI/API contract fix.

## 7. Current workspace changes and verification

The latest workspace changes from this session are currently uncommitted in:

```text
api/Services/AtlasQueryService.cs
app/src/pages/Home.jsx
app/src/components/ConceptDetailPopover.jsx
```

Local verification completed in the macOS workspace:

```text
npm run lint   — passed with existing warnings
npm run build  — passed
git diff --check — passed
```

The lint warnings are existing cleanup items, including unused imports, an unused graph variable, Fast Refresh export warnings, hook dependency warnings, and a duplicate style key. They did not prevent the build.

Backend verification for the latest C# change remains pending in the Linux VM:

```bash
dotnet build api/StudyTracker.Api.csproj
dotnet test tests/StudyTracker.Api.Tests/StudyTracker.Api.Tests.csproj
```

After that, rebuild the VM images:

```bash
sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  build --no-cache api app

sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  up -d --force-recreate api app
```

## 8. What is known to be working now

- Dockerized PostgreSQL, .NET API, and React/Nginx services can run in the Linux VM.
- The API can authenticate with the configured VM API key.
- The same-origin Nginx `/api` proxy forwards a correct `x-api-key`.
- The React production bundle can embed the matching `VITE_API_KEY` when Compose receives the correct `.env` value.
- The Knowledge Atlas endpoint can return data and the frontend now handles its relation object shapes.
- The frontend production build succeeds.

These statements do not prove that every old data item is reachable from the redesigned UI, that the live AWS database is migrated, or that all routes are visually correct.

## 9. Known gaps to carry into the fresh restart

The user observed that the website is working but still has missing or incorrectly re-oriented content. The next work should focus on product/data completeness rather than repeating authentication troubleshooting.

Priority gaps already documented in [`website-comparison-baseline.md`](website-comparison-baseline.md):

1. The redesigned Home/Atlas does not yet expose all old FDE, Azure, Java, and Lab curriculum content as discoverable learning paths.
2. Old vertical progress/task meaning is not fully integrated into the new Home and Reading Map flow.
3. Lab Projects and Reading Map need distinct, intentional product destinations and data sources.
4. Old FDE specialization cards and navigation entry points need canonical destinations.
5. Profile/certification information needs a complete old-to-new content crosswalk.
6. Chapter, prerequisite, related-lesson, next-lesson, notes, diagrams, and code-comparison data need end-to-end verification against real rows.
7. Database migration, reconciliation, backup/restore, and idempotency remain environment-specific evidence tasks.
8. The API-key approach is acceptable for this VM simulation only and requires a production security decision before AWS exposure.

## 10. Fresh-start execution sequence

The recommended next sequence is:

### Step A — Freeze the current working baseline

- Record `git status`, branch, current HEAD, and the three uncommitted fixes.
- Run the VM .NET build/tests and Docker rebuild.
- Capture one successful API response and one successful browser load without secrets.
- Commit or otherwise preserve this known-working checkpoint before broader redesign changes.

### Step B — Build a page/data gap matrix

For every route, record:

```text
Route | Old purpose/data | New route/component | API endpoint | DB source | Preserved? | Missing? | Decision
```

Use [`website-comparison-baseline.md`](website-comparison-baseline.md) for the old content inventory and route baseline. Do not copy its full curriculum catalog into another document.

### Step C — Validate API contracts before UI changes

- Capture the JSON shape for each v2 endpoint.
- Define stable DTO contracts for domains, concepts, paths, reading items, chapters, relationships, and progress.
- Add contract tests for object-vs-string shape regressions like the Knowledge Atlas failure.
- Keep legacy endpoint compatibility until the new route is verified.

### Step D — Reconcile data before deciding deletion

- Inventory the exact VM/AWS database identity and migration history.
- Compare legacy vertical/task counts with canonical course/module/lesson/problem counts.
- Resolve FDE Curriculum versus FDE Self-Study as an alias/ownership decision, not an automatic deletion.
- Record unmatched and ambiguous rows as proposed/conflict mappings.
- Do not delete PostgreSQL rows until backup, restore, mapping, and human approval gates are complete.

### Step E — Migrate one vertical/page slice at a time

The safest next pilot is one complete vertical through:

```text
legacy data → canonical mapping → API contract → redesigned route → progress write → browser verification
```

The Java pilot and reconciliation rules already described in the architecture and prompts can be reused, but their live database evidence must be re-run in the VM/AWS target.

### Step F — Re-run the phase tracker and independent audit

Update only the relevant evidence files in [`migration-evidence/`](migration-evidence/), then update [`migration-execution-tracker.md`](migration-execution-tracker.md). Do not mark a phase `Done` from source inspection alone.

## 11. Immediate next commands in the VM

These commands validate the current checkpoint without deleting data:

```bash
cd ~/Desktop/git-raghu/scaler-education-journey

dotnet build api/StudyTracker.Api.csproj
dotnet test tests/StudyTracker.Api.Tests/StudyTracker.Api.Tests.csproj

sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  build --no-cache api app

sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  up -d --force-recreate api app

sudo docker compose ps
sudo docker compose logs --tail=120 api
```

For a schema mismatch, run the explicit migration separately and preserve the PostgreSQL volume:

```bash
sudo docker compose --env-file .env \
  -f docker-compose.yml -f docker-compose.dev.yml \
  run --rm api dotnet StudyTracker.Api.dll --migrate
```

## 12. Handoff conclusion

The immediate runtime path is now functional, but the redesign is not yet a complete old-content migration. The next phase should be a fresh, evidence-backed content and route reconciliation pass. Preserve the existing architecture and baseline documents as references, use this file for the conversation/runtime handoff, and update the tracker only with environment-specific evidence.
