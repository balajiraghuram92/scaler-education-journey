# Neuralascent Local-LLM Migration Prompt Pack

**Purpose:** Copy one prompt at a time into the local coding LLM. Each phase is intentionally bounded so the model can inspect, implement, test, and hand off without losing the architecture in a very large context.

**Architecture source:** [`technical-migration-architecture.md`](technical-migration-architecture.md)

**Content source:** [`website-comparison-baseline.md`](website-comparison-baseline.md)

**Execution tracker:** [`migration-execution-tracker.md`](migration-execution-tracker.md)

## How to use this prompt pack

1. Start every new local-LLM session with the **Master Execution Contract**.
2. Append exactly one phase prompt to that contract.
3. Do not ask the LLM to complete multiple phases in one run.
4. Review its code, evidence, and tracker update before approving the next phase.
5. Create a commit after each accepted phase. Do not combine unreviewed phases in one commit.
6. Production backup, deployment, DNS, certificate, database deletion, and public cutover always require explicit human approval.

The prompts use `PHASE-N` as a stable identifier. The same identifier must appear in commits, tracker evidence, reconciliation runs, and handoff notes.

---

## Prompt 00 — Master Execution Contract

Copy this block before every phase prompt.

```text
You are the senior implementation engineer for the Neuralascent migration. Work as an 11+ year backend/full-stack engineer experienced with Java-style domain design, .NET 8, EF Core 8, PostgreSQL 16, React 19, Docker, Nginx, and AWS deployment safety.

Repository root:
/Users/raghuram/Documents/GitHub/scaler-education-journey

Before modifying anything, read these files completely:
1. info/website-reference/technical-migration-architecture.md
2. info/website-reference/website-comparison-baseline.md
3. info/website-reference/redesign-data-migration-plan.md
4. info/website-reference/migration-execution-tracker.md

Then inspect the current repository and Git status. The repository may contain user changes or work from a previous phase. Preserve unrelated work and never reset, checkout, delete, or overwrite it.

Execution rules:
- Implement exactly the requested phase. Do not begin a later phase.
- Treat Course -> CourseModule -> Lesson/Problem as the canonical redesigned curriculum.
- Keep StudyVertical -> StudyTask as the compatibility model until an explicitly approved cleanup phase.
- All schema migrations before cleanup must be additive and backward compatible.
- Do not delete, merge, truncate, drop, or physically archive production data.
- Do not infer that FDE Curriculum and FDE Self-Study are duplicates. Reconcile row-level data first.
- Never hide a migration, API, or persistence failure behind sample data or an optimistic success message.
- Never place a chapter in the first matching course or java-spring-lld as a fallback.
- Keep old API contracts functional until their compatibility exit gate is signed off.
- Use explicit completion state in new APIs. Do not introduce new toggle semantics.
- Use transactions for canonical/legacy progress synchronization and activity insertion.
- New SQL identifiers use lower_snake_case. Existing mixed-case tables and columns must be referenced exactly as they exist.
- EF migrations define schema. Seeder code must not repair schema with raw DDL.
- Never put environment-specific content reconciliation in an EF migration Up() method.
- Never expose secrets, API keys, passwords, connection strings, dumps, or personal notes in logs, tests, screenshots, commits, or tracker evidence.
- A VITE_* value is visible to the browser and is not a secret authentication mechanism.
- Do not deploy, push, change DNS, touch AWS, or execute a production database mutation unless the user explicitly requests it in this session.

Working method:
1. Inspect relevant files and identify assumptions.
2. Record a short implementation plan.
3. Implement the smallest coherent change with clear service boundaries.
4. Add or update tests proportional to the change.
5. Run the required build, lint, tests, migration checks, and git diff checks.
6. Update only the current phase in migration-execution-tracker.md with evidence. Do not mark a checkbox complete without evidence.
7. Stop after the phase handoff. Do not silently continue.

Minimum repository checks:
- git status --short
- dotnet build api/StudyTracker.Api.csproj
- npm run lint --prefix app
- npm run build --prefix app
- git diff --check

Run checks that are relevant to the files changed. If a required tool, runtime, package restore, Docker daemon, or database is unavailable, do not fake success. Mark the tracker item Blocked and provide the exact command and failure summary.

Phase handoff format:
1. Outcome
2. Files changed
3. Database/API/UI behavior changed
4. Compatibility impact
5. Commands run and results
6. Evidence added to the tracker
7. Known risks or blocked checks
8. Rollback instructions
9. Recommended next phase, without starting it

Do not claim the phase is complete unless every mandatory exit criterion is either verified or explicitly marked Blocked with a reason.
```

---

## Prompt 01 — Phase 0: Discovery, Production Inventory, and Recovery Proof

```text
PHASE-0

Objective:
Create a read-only, repeatable inventory and recovery-preparation package before any schema or application migration begins. This phase must not mutate PostgreSQL, AWS, Docker containers, or application code except for adding safe diagnostic scripts/documentation if needed.

Required work:
1. Inspect the current EF migrations, StudyTrackerContext, entity models, seeders, Docker Compose files, deployment workflow, and environment examples.
2. Produce a current-state schema/table map that distinguishes quoted legacy tables/columns from lower_snake_case tables.
3. Create a read-only SQL inventory script at:
   info/website-reference/sql/phase-0-production-inventory.sql
4. The SQL must report:
   - PostgreSQL version and current database name;
   - EF migration history;
   - table and column inventory from information_schema;
   - row counts for all application tables;
   - vertical IDs, names, total/completed task counts;
   - course/module/lesson/problem total and completed counts;
   - duplicate normalized vertical, module, lesson, and task title candidates;
   - orphan foreign-key candidates;
   - FDE Curriculum versus FDE Self-Study normalized task comparison;
   - Reading Map seed candidates and synthetic activity rows;
   - ConceptNextLesson rows with and without LessonId.
5. The script must be SELECT-only. It must not contain INSERT, UPDATE, DELETE, ALTER, CREATE, DROP, TRUNCATE, DO blocks, or functions with side effects.
6. Create a production inventory evidence template at:
   info/website-reference/migration-evidence/phase-0-inventory-template.md
7. Document backup and restore commands as templates using explicit placeholders. Do not run them without user approval.
8. Inspect whether a local/rehearsal database is available. If available and authorized, run only read-only inventory. Otherwise mark runtime inventory evidence Pending.
9. Update PHASE-0 in the tracker.

Required verification:
- Review the SQL manually for mutation keywords.
- If PostgreSQL is available, execute it in a read-only transaction against a non-production or explicitly approved target.
- Verify repository builds remain unchanged.
- git diff --check

Exit criteria:
- Inventory SQL exists and is demonstrably read-only.
- Backup/restore procedure is documented but not executed without approval.
- The production evidence template defines every required count and checksum.
- Any repository/schema mismatch is listed.
- No application behavior or database state was changed.

Stop conditions:
- Stop immediately if the target database identity is ambiguous.
- Stop before any production command requiring credentials or mutation.
- Do not mark backup/restore as proven unless an actual authorized restore rehearsal occurred.
```

---

## Prompt 02 — Phase 1: Migration Runtime Hardening

```text
PHASE-1

Prerequisite:
PHASE-0 inventory design is accepted. A backup/restore rehearsal may remain operationally Pending, but no production deployment may occur until it is complete.

Objective:
Make schema migration execution deterministic and fail-fast. Separate migration, reference seeding, and normal API startup. Preserve existing endpoint behavior.

Required work:
1. Inspect Program.cs and DbSeeder.cs and confirm all current Database.Migrate and raw-DDL paths.
2. Implement explicit modes:
   - --migrate: run Database.MigrateAsync once; return non-zero on failure.
   - --seed-reference-data: run idempotent reference-data seeding only; no DDL.
   - normal startup: do not swallow migration errors or perform emergency schema repair.
3. Remove duplicate migration execution from DbSeeder.
4. Move emergency ALTER/CREATE repair SQL out of runtime seeding. Do not remove it until equivalent formal migrations are proven present; document any historical repair risk.
5. Add structured logging with correlation/deployment context where feasible.
6. Implement:
   - GET /health/live: process liveness, no database call.
   - GET /health/ready: database connectivity plus pending-migration/required-schema validation.
   - keep GET /health as a compatibility alias to readiness.
7. Add centralized Problem Details handling for unhandled API failures without exposing secrets.
8. Refactor only enough to make lifecycle behavior testable. Do not start v2 curriculum APIs.
9. Add an API test project if none exists. Use .NET 8. Add focused tests for lifecycle decision logic and health response logic. If package restoration is unavailable, create the project and mark execution Blocked rather than claiming tests passed.
10. Update Docker healthcheck documentation only if the path semantics changed; preserve /health compatibility.
11. Update PHASE-1 tracker evidence.

Mandatory tests:
- dotnet build api/StudyTracker.Api.csproj
- dotnet test for all test projects
- verify --migrate returns success against a disposable up-to-date database
- verify a deliberately failing migration/connection produces non-zero exit/readiness failure
- verify normal startup no longer calls schema-repair DDL
- old endpoint smoke test: /api/verticals, /api/courses, /api/knowledge-atlas
- npm lint/build as regression checks
- git diff --check

Design constraints:
- Do not run migrations twice.
- Do not catch and continue after migration failure.
- Do not make readiness a simple CanConnectAsync check.
- Reference-data seeding must be idempotent.
- Do not execute production migration or deployment.

Exit criteria:
- One authoritative migration execution path exists.
- API cannot become ready with missing required schema.
- DbSeeder contains no migration call and no active schema-repair responsibility.
- Existing old API contracts still work.
- Tests demonstrate failure behavior, not only the happy path.
```

---

## Prompt 03 — Phase 2: Additive Bridge Schema and EF Model

```text
PHASE-2

Prerequisite:
PHASE-1 is Done and accepted.

Objective:
Add the canonical/legacy bridge schema and EF entities without backfilling production content or changing old API contracts.

Architecture authority:
Use Sections 6–10 of technical-migration-architecture.md. If the repository state requires a deviation, document an Architecture Decision Record before implementing it.

Required schema/entities:
- StudyVertical compatibility metadata: CanonicalVerticalId, ArchivedAt, UpdatedAt.
- StudyTask UpdatedAt.
- Course PathType and IsPublished.
- Lesson ContentStatus.
- CourseDomainLink.
- LessonConceptLink.
- LessonRelation.
- StudyTaskContentLink with exactly one LessonId or ProblemId.
- ReadingMapItem canonical links/status/schedule/priority/seed/archive metadata.
- LearningActivity with correlation idempotency.
- KnowledgeThreadStep.
- MigrationReconciliation.

Required work:
1. Add explicit C# entity classes and navigation properties.
2. Add DbSet properties and fluent configuration in StudyTrackerContext.
3. Use explicit table/column names for all new fields and entities.
4. Preserve existing mixed-case table/column identifiers exactly.
5. Configure composite keys, unique indexes, check constraints, and delete behaviors described in the architecture.
6. Generate small ordered EF migrations rather than one opaque migration:
   a. AddCurriculumBridgeSchema
   b. AddLinkedReadingAndActivity
   c. NormalizeKnowledgeThreads
   d. AddMigrationReconciliation
7. Review generated Up and Down methods. Down methods must not pretend that reversing after backfill is safe; document operational rollback as binary rollback while migrations remain additive.
8. Update the model snapshot.
9. Add PostgreSQL integration tests for constraints, keys, and delete behavior. SQLite is not sufficient for PostgreSQL check constraints and identifier casing.
10. Do not add content backfill to migration Up methods.
11. Update PHASE-2 tracker evidence, including generated migration names.

Mandatory verification:
- migrate a fresh PostgreSQL 16 database from migration zero
- migrate a restored/reconstructed old schema forward
- run Database.Migrate twice and verify the second run is a no-op
- verify StudyTaskContentLink rejects zero targets and two targets
- verify bridge target deletion is restricted
- verify LearningActivity correlation uniqueness
- verify old endpoints return their previous shape
- dotnet build/test
- npm lint/build
- git diff --check

Exit criteria:
- All additive schema exists and matches EF configuration.
- No production content has been mapped or deleted.
- Old API and old frontend remain compatible.
- PostgreSQL-specific constraints are tested.
```

---

## Prompt 04 — Phase 3A: Reconciliation Engine and Java Pilot

```text
PHASE-3A

Prerequisite:
PHASE-2 is Done and accepted.

Objective:
Build a deterministic, rerunnable reconciliation engine and prove it by mapping Java legacy tasks to existing canonical lessons/problems. Do not migrate FDE, Azure, or Labs in this phase.

Required work:
1. Implement command modes:
   - --reconcile-content --scope java --dry-run
   - --reconcile-content --scope java --apply
   - --reconcile-content --scope java --verify
2. Keep the engine outside EF migration Up methods and outside normal HTTP startup.
3. Use deterministic normalization and SHA-256 source checksums.
4. Write MigrationReconciliation rows with PHASE-3A migration key.
5. Use transactions per course/path aggregate.
6. Produce a dry-run report containing proposed, exact, conflict, and unmapped rows.
7. Map:
   - 13 Java lesson tasks to Lesson rows;
   - five OOP-2 problem tasks to Problem rows;
   - evaluate four Spring/capstone tasks and create Outline lessons only when no canonical lesson exists.
8. Do not infer completion conflict resolution. Report conflicts. For exact verified mappings, preserve existing completion and ensure the approved canonical rule is explicit.
9. Add Java CourseDomainLinks for Foundations, Backend, and Reliability after resolving actual domain IDs by slug.
10. Add exact LessonConceptLinks for Java concurrency where verified.
11. Add verification queries/reports that prove the old visible 8/22 is preserved.
12. Add unit and PostgreSQL integration tests for normalization, idempotent reruns, interruption/retry, and mapping classification.
13. Update PHASE-3A tracker evidence.

Non-negotiable rules:
- Dry-run performs no domain-content writes.
- Apply is rerunnable without duplicate rows.
- Verify performs no repair unless explicitly designed and documented.
- No FDE mapping in this phase.
- No old row deletion or archival.

Mandatory verification:
- run dry-run twice; reports are stable
- apply to disposable/rehearsal DB
- apply a second time; no duplicate rows or changed counts
- verify Java mapping coverage and 8/22 progress invariant
- simulate an interrupted aggregate and rerun safely
- dotnet build/test
- old /vertical/5 API smoke test
- new schema query smoke test
- git diff --check

Exit criteria:
- Java mappings are 100% classified.
- Every Verified mapping has exactly one Lesson or Problem target.
- Java progress counts are preserved.
- Reconciliation can resume and rerun safely.
```

---

## Prompt 05 — Phase 3B: FDE, Azure, Labs, Atlas, Reading, and Threads Backfill

```text
PHASE-3B

Prerequisite:
PHASE-3A Java pilot is Done, reviewed, and accepted.

Objective:
Extend the proven reconciliation engine to FDE, Azure, Labs, Atlas links, Reading Map seed classification, and normalized knowledge threads.

Required work:
1. Add dry-run/apply/verify scopes for fde, azure, labs, atlas, reading-map, and knowledge-threads.
2. FDE dry-run must compare FDE Curriculum and FDE Self-Study by normalized module/title and produce:
   - exact duplicates;
   - completion conflicts;
   - FDE Curriculum-only rows;
   - FDE Self-Study-only rows;
   - ambiguous matches.
3. Stop before choosing a canonical vertical if conflicts or semantic differences require human judgment. Record a decision request in the tracker.
4. After an approved decision, create one canonical FDE Course with prerequisite plus modules 1–8 and 104 Outline lessons.
5. Link verified duplicate legacy tasks to the same canonical lesson when appropriate. Never overwrite completed with incomplete silently.
6. Create Azure Certification and Lab Project canonical paths with correct PathType and exact old titles.
7. Populate CourseDomainLinks using the architecture mapping.
8. Populate only high-confidence LessonConceptLinks automatically. Put uncertain items in reconciliation conflicts.
9. Backfill ConceptNextLesson.LessonId where exact; preserve unresolved text rows.
10. Mark prototype Reading Map rows IsSeeded. Link exact Java/concurrency rows only.
11. Normalize existing RawPath strings into KnowledgeThreadStep rows, attaching exact concept/lesson IDs and preserving labels.
12. Do not create historical LearningActivity from synthetic daily activity counts.
13. Add verification reports for raw and deduplicated FDE totals.
14. Update PHASE-3B tracker evidence and decision log.

Mandatory tests:
- dry-run is deterministic and read-only
- rerun apply produces no duplicates
- all old task counts and completed counts remain unchanged
- both raw and deduplicated FDE reports are available
- Azure 0/2 and Labs 0/2 are preserved unless production data proves otherwise
- knowledge thread step ordering is stable
- unresolved links remain visible, not silently dropped
- dotnet build/test
- API compatibility smoke tests
- git diff --check

Exit criteria:
- Every legacy task is classified.
- FDE conflicts are resolved or explicitly Blocked.
- No old content is deleted or hidden.
- Canonical Java/FDE/Azure/Lab paths exist in the rehearsal database.
- Atlas/Reading/thread backfills are auditable and rerunnable.
```

---

## Prompt 06 — Phase 4: API Services, Compatibility, and Explicit Progress

```text
PHASE-4

Prerequisite:
PHASE-3A is Done. PHASE-3B should be Done for all paths that will be exposed by v2.

Objective:
Introduce clean service boundaries, preserve old contracts, add versioned redesigned read APIs, and make completion synchronization transactional and idempotent.

Required work:
1. Refactor endpoint logic into focused services/features:
   - LearningPathQueryService
   - ProgressService
   - AtlasQueryService
   - ReadingMapService
   - CurriculumMappingService
2. Preserve old endpoint paths and response shapes used by the old frontend.
3. Make old task toggle and existing lesson/problem progress handlers delegate to ProgressService.
4. Add explicit v2 completion endpoints using completed=true/false and correlationId.
5. ProgressService transaction must:
   - lock/load target and bridge;
   - set canonical Lesson or Problem completion;
   - mirror all verified legacy task links;
   - insert one LearningActivity event;
   - commit atomically;
   - return canonical and affected legacy IDs.
6. Add:
   - GET /api/v2/learning-paths
   - GET /api/v2/learning-paths/{slug}
   - GET /api/v2/knowledge-atlas
   - GET /api/v2/reading-map
   - GET /api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}
7. Responses must contain stable slugs, canonical URLs, contentStatus, pathType, real progress, and Atlas destinations.
8. Implement owner/admin-protected migration status only if an authorization mechanism exists. Do not expose reconciliation details publicly.
9. Add ETag/updatedAt or another explicit concurrency strategy where appropriate.
10. Add Problem Details validation responses.
11. Add old-contract snapshot tests and v2 integration tests.
12. Update PHASE-4 tracker evidence.

Mandatory concurrency/idempotency tests:
- same correlationId retry does not duplicate activity
- explicit true twice remains true
- old toggle updates mapped canonical content
- new explicit completion updates linked old task
- concurrent old/new writes produce one valid final state with no partial mirror
- transaction rollback leaves both models unchanged

Mandatory regression checks:
- old Home/vertical APIs work
- Java course/problem APIs work
- Atlas, Reading Map, and chapter APIs work
- dotnet build/test
- npm lint/build
- git diff --check

Exit criteria:
- Old UI can run unchanged against the new API.
- New v2 reads contain only database data.
- Progress synchronization is atomic and tested.
- No endpoint reports success after a failed database commit.
```

---

## Prompt 07 — Phase 4B: Correct Curriculum Import and Relationship Persistence

```text
PHASE-4B

Prerequisite:
PHASE-4 service boundaries and v2 path APIs are Done.

Objective:
Replace unsafe chapter mapping with explicit, idempotent persistence of course/module/lesson and all submitted relationships.

Required work:
1. Design a v2 request using exact courseSlug/courseId and moduleSlug/moduleId. Display names are not identifiers.
2. Require the destination to exist. Creating a path/module must be a separate explicit operation.
3. Persist:
   - lesson content and content status;
   - lesson-concept links;
   - prerequisite, related, and next lesson relations;
   - unresolved relation labels with Unresolved status;
   - ChapterImported activity with idempotency key.
4. Use one transaction.
5. Return persisted IDs, relationship resolution results, and canonical URL.
6. Remove fallback to java-spring-lld, first course, and /api/verticals/ingest.
7. Never return mapped/saved success after a failed commit.
8. Keep the old ingest endpoint only as a compatibility endpoint; clearly separate its behavior.
9. Add validation limits for title, slug, Markdown size, relationship counts, and valid content status.
10. Ensure logs never include Markdown or notes.
11. Add integration tests for correct destination, idempotent retry, rollback, unknown concepts, unresolved lessons, and duplicate slugs.
12. Update PHASE-4B tracker evidence.

Exit criteria:
- A chapter can only be stored in its explicit destination.
- Every accepted relationship is persisted or returned as an explicit unresolved/validation result.
- Retried requests are idempotent.
- Failed persistence cannot look successful to the client.
```

---

## Prompt 08 — Phase 5A: Frontend Foundation, Home, and Learning Paths

```text
PHASE-5A

Prerequisite:
PHASE-4 v2 learning-path and Atlas APIs are Done.

Objective:
Create the redesigned frontend foundation and migrate Home plus canonical Learning Path pages without breaking old routes.

Required work:
1. Create one shared API client that handles:
   - same-origin/base URL;
   - headers and correlation IDs;
   - timeout/abort;
   - Problem Details parsing;
   - typed/documented response handling.
2. Migrate existing fetch calls incrementally; do not create several incompatible clients.
3. Add explicit loading, empty, degraded, and error states.
4. Introduce a build/runtime rule that forbids silent sample fallback in production. Demo data must require an explicit development flag and visible demo label.
5. Add route-level error boundaries.
6. Home:
   - fetch v2 Atlas and learning paths;
   - retain the Warm Editorial graph;
   - render domains/concepts from API rather than canonical React arrays;
   - add a compact path index exposing Java, FDE, Azure, and Labs with real progress;
   - make graph/path destinations canonical and accessible.
7. Add /learning-paths/:slug:
   - path type, description, progress;
   - modules and ordered lessons;
   - estimated reading time;
   - domain/concept context;
   - visible Outline/Draft/Published labels;
   - chapter links only when an appropriate reader destination exists.
8. Preserve /vertical/:id as compatibility; do not redirect yet unless flag-controlled and verified.
9. Add frontend tests. If no test framework exists, introduce a suitable React/Vite test setup deliberately and document it.
10. Update PHASE-5A tracker with screenshots or route evidence paths.

Mandatory verification:
- npm lint/build/test
- API unavailable: explicit error, no production-looking fallback
- added database domain/path renders without source-code constants
- all five old tracks are discoverable within two navigation actions
- Java path progress matches legacy 8/22 rehearsal evidence
- keyboard navigation and basic accessibility checks
- old /vertical routes still resolve
- dotnet regression build/test
- git diff --check

Exit criteria:
- Home is data-driven.
- Canonical learning path pages work for all migrated path types.
- Production fallback behavior is explicit and safe.
- Old routes remain available.
```

---

## Prompt 09 — Phase 5B: Reading Map, Projects, Chapters, Importer, and Profile

```text
PHASE-5B

Prerequisite:
PHASE-5A is Done. PHASE-4B is Done before importer cutover.

Objective:
Complete the redesigned page migration while preserving all old-site content and route compatibility.

Required work:
1. Reading Map:
   - route /reading-map directly to ReadingMap;
   - use v2 linked items and real activity;
   - support manual items visibly;
   - remove literal count titles in favor of server-computed counts;
   - no synthetic activity unless visibly marked demo in development.
2. Lab Projects:
   - make /lab-projects distinct from Reading Map;
   - render WMS Defect Detection and Unity Localization Platform;
   - keep FDE specialization semantics in the FDE path, not as replacement lab data.
3. Chapter Reader:
   - use shared API client and canonical hierarchical URL;
   - preserve prose, TOC, code comparisons, diagrams, resources, problems, notes, related concepts, and navigation;
   - use explicit errors instead of fallback chapters.
4. Curriculum Importer:
   - load path/module/concept choices from API;
   - require explicit destination;
   - preview relationships;
   - show canonical URL only after commit;
   - distinguish an unsaved local draft from saved data.
5. Profile:
   - preserve content listed in website-comparison-baseline.md;
   - remove unused vertical fetch or intentionally use real progress;
   - preserve /certifications -> /profile.
6. Route behavior:
   - /progress -> /reading-map;
   - /learning -> library/path index, not fixed chapter;
   - /chapter/:slug resolves and redirects to canonical hierarchical route;
   - /add-vertical, /map-chapter, /ingest -> /curriculum-import.
7. Add route, state, API-failure, and accessibility tests.
8. Update PHASE-5B tracker with evidence for every migrated route.

Mandatory verification:
- npm lint/build/test
- Playwright or equivalent route checks at desktop and mobile widths
- all required routes load real API data
- API outage is visible and never disguised as sample content
- completion persists after reload and appears in legacy route
- importer success and failure are visually distinguishable
- notes are not lost after reload
- old URLs resolve or redirect without 404
- dotnet build/test
- git diff --check

Exit criteria:
- Every old content category has a redesigned destination.
- Reading Map and Lab Projects are separate.
- Chapter and importer persistence is trustworthy.
- Route compatibility matrix is fully verified.
```

---

## Prompt 10 — Phase 6: Deployment, Cutover, Observability, and Rollback Rehearsal

```text
PHASE-6

Prerequisite:
PHASE-0 through PHASE-5B are Done in a rehearsal environment. Production actions require explicit user approval in the current session.

Objective:
Make deployment deterministic and reversible, then perform a controlled cutover only after the user authorizes each production action.

Required repository work before production:
1. Update deployment to use immutable commit-SHA image tags/digests.
2. Add a one-shot migration container/command before API startup.
3. Abort deployment on migration, reconciliation, or readiness failure.
4. Preserve the previous known-good API/app image; do not prune it before bake acceptance.
5. Record deployment SHA, image digests, migration IDs, reconciliation run, and backup evidence.
6. Add structured logs and metrics from the architecture document.
7. Add feature flags:
   - LearningPathsV2
   - SynchronizedProgressWrites
   - ReadingActivityV2
   - CanonicalVerticalRedirects
   - StrictNoFallbackData
8. Write an explicit production runbook with pre-check, backup, migrate, backfill, API deploy, smoke, web deploy, acceptance, rollback, and escalation commands.
9. Validate the workflow syntax and container healthchecks locally or in CI where possible.
10. Update PHASE-6 tracker. Do not mark production steps Done from documentation alone.

Production action boundary:
- Stop and ask the user immediately before backup execution if credentials/target are not already narrowly approved.
- Stop before running migrations/backfill against production.
- Stop before deploying API/frontend.
- Stop before enabling canonical redirects.
- Do not group these into one vague approval.

Mandatory rehearsal:
- restore production-like backup to isolated DB
- execute migrations and backfill
- deploy API first and verify old client compatibility
- deploy frontend and run route smoke suite
- roll back API and frontend binaries without reversing additive schema
- prove old client still works after binary rollback

Production acceptance evidence:
- valid TLS domain and reachable live DOM
- no migration/missing-table/missing-column errors
- readiness confirms expected migration
- all canonical and legacy routes pass
- reconciliation invariants pass
- completion sync test passes
- no sample fallback in production
- previous images and restore procedure remain available during bake

Exit criteria:
- Deployment and rollback are rehearsed.
- Production is marked Done only with actual evidence and user approval.
- Canonical redirects remain disabled until the bake gate is accepted.
```

---

## Prompt 11 — Phase 7: Bake Review and Cleanup Proposal

```text
PHASE-7

Prerequisite:
Production cutover is complete and the agreed bake period has elapsed.

Objective:
Evaluate whether anything can be archived or removed. This phase produces a cleanup proposal first. It performs no destructive operation without a separate explicit user approval.

Required work:
1. Collect bake-period evidence:
   - v1/v2 route traffic;
   - progress synchronization mismatches;
   - unresolved mapping count;
   - importer errors;
   - API failures and latency;
   - fallback/demo-data activation;
   - old route usage.
2. Verify 100% classification of old tasks and all reconciliation invariants.
3. Produce candidates with row IDs/counts and replacement destinations:
   - prototype Reading Map rows;
   - seeded activity logs;
   - raw knowledge paths;
   - duplicate FDE vertical alias;
   - unused old React components/routes.
4. For each candidate specify Archive, Retain, or Delete-Later, with rationale, backup/export, dependencies, and rollback.
5. Prefer soft archive. Do not drop Verticals or Tasks in this phase.
6. Create a separate destructive migration proposal if physical deletion is still desired.
7. Update PHASE-7 tracker evidence.

Mandatory stop:
Do not execute DELETE, DROP, TRUNCATE, destructive EF migration, file deletion, or permanent route removal without a new explicit user request approving exact targets.

Exit criteria:
- Cleanup proposal is evidence-based.
- No destructive action occurred.
- Remaining compatibility dependencies are explicit.
```

---

## Prompt 12 — Independent Final Audit

Use this with a fresh LLM context after all implementation phases. Prefer a model/session that did not author the changes.

```text
FINAL-AUDIT

Act as an independent principal engineer reviewing the completed Neuralascent migration. Do not implement fixes during the first pass. Inspect the repository, migration tracker, architecture, evidence, Git history, and current tests.

Review areas:
1. Architecture conformity.
2. PostgreSQL migration safety and identifier casing.
3. EF model/schema consistency.
4. Backfill idempotency and reconciliation completeness.
5. Progress transaction correctness and concurrent writes.
6. API backward compatibility and v2 contract quality.
7. Chapter importer destination/relationship correctness.
8. React fallback/error behavior and route compatibility.
9. Authentication/API-key exposure.
10. Deployment rollback and backup evidence.
11. Tracker claims versus actual evidence.
12. Old-site content coverage from website-comparison-baseline.md.

Required output:
- Findings ordered by severity: Critical, High, Medium, Low.
- Each finding includes file/line, concrete failure scenario, affected phase, and recommended correction.
- A traceability matrix from architecture Definition of Done to code/test/evidence.
- A list of tracker items marked Done without sufficient evidence.
- Final recommendation: Reject, Conditionally Accept, or Accept.

Do not accept the migration because builds pass. Verify data invariants, failure modes, compatibility, and rollback evidence.
```
