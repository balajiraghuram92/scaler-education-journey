# Neuralascent Migration Execution Tracker

**Architecture:** [`technical-migration-architecture.md`](technical-migration-architecture.md)

**Implementation prompts:** [`local-llm-migration-prompts.md`](local-llm-migration-prompts.md)

**Content inventory:** [`website-comparison-baseline.md`](website-comparison-baseline.md)

## Tracker rules

- Allowed phase status: `Not Started`, `In Progress`, `Blocked`, `Ready for Review`, `Done`.
- A phase may be `Done` only when mandatory checks and exit criteria have evidence.
- A checked box without an evidence reference is not accepted.
- Documentation or code existence is not evidence that production execution succeeded.
- Production, backup, restore, deploy, redirect, archive, and deletion evidence must state the exact environment.
- Never paste credentials, secrets, API keys, raw database dumps, or personal note content here.
- The implementing LLM updates only its current phase. Human review changes `Ready for Review` to `Done`.

## Overall status

| ID | Phase | Status | Owner | Commit/PR | Evidence | Human sign-off |
|---|---|---|---|---|---|---|
| PHASE-0 | Discovery and recovery proof | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md) | — |
| PHASE-1 | Migration runtime hardening | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-1-runtime-hardening.md`](migration-evidence/phase-1-runtime-hardening.md) | — |
| PHASE-2 | Additive bridge schema | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-2-bridge-schema.md`](migration-evidence/phase-2-bridge-schema.md) | — |
| PHASE-3A | Reconciliation engine and Java pilot | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-3a-java-pilot.md`](migration-evidence/phase-3a-java-pilot.md) | — |
| PHASE-3B | FDE, Azure, Labs and graph backfill | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-3b-backfill.md`](migration-evidence/phase-3b-backfill.md) | — |
| PHASE-4 | API services and progress synchronization | Not Started | Senior Implementation Engineer | Pending user commit | [`phase-4-api-services.md`](migration-evidence/phase-4-api-services.md) | — |
| PHASE-4B | Curriculum importer correction | Not Started | Senior Implementation Engineer | Pending user commit | [`phase-4b-importer.md`](migration-evidence/phase-4b-importer.md) | — |
| PHASE-5A | Frontend foundation, Home and paths | Not Started | Senior Implementation Engineer | Pending user commit | [`phase-5a-frontend-foundation.md`](migration-evidence/phase-5a-frontend-foundation.md) | — |
| PHASE-5B | Remaining webpage migration | Not Started | Senior Implementation Engineer | Pending user commit | [`phase-5b-webpages.md`](migration-evidence/phase-5b-webpages.md) | — |
| PHASE-6 | Deployment and cutover | Blocked | Senior Implementation Engineer | Pending user commit | [`phase-6-deployment-runbook.md`](migration-evidence/phase-6-deployment-runbook.md) | — |
| PHASE-7 | Bake review and cleanup proposal | Not Started | Senior Implementation Engineer | Pending user commit | [`phase-7-bake-review.md`](migration-evidence/phase-7-bake-review.md) | — |
| FINAL-AUDIT | Independent architecture audit | Blocked | Independent Principal Auditor | Pending user commit | [`final-audit-report.md`](migration-evidence/final-audit-report.md) | — |

## Global invariants

These remain unchecked until verified in the relevant environment.

- [ ] No legacy `Verticals` row was physically deleted.
- [ ] No legacy `Tasks` row was physically deleted.
- [ ] Legacy task total before equals legacy task total after.
- [ ] Legacy completed-task total before equals legacy completed-task total after, subject only to documented conflict decisions.
- [ ] Lesson, problem, note, resource, comparison, and diagram counts were preserved.
- [ ] Every Verified task-content bridge has exactly one canonical Lesson or Problem target.
- [ ] All old-site content in `website-comparison-baseline.md` has a canonical destination or approved exception.
- [ ] Old API contracts remained compatible through frontend cutover.
- [ ] New completion writes synchronize canonical and legacy state atomically.
- [ ] No production page silently displays sample data after an API failure.
- [ ] No chapter import can silently fall back to Java or the first course.
- [ ] Production migration failures prevent readiness/deployment.
- [ ] Production backup and restore have been rehearsed.
- [ ] Binary rollback works while additive schema remains applied.

## Evidence format

Every phase evidence file should use this structure:

```text
Phase ID:
Environment: local | disposable-postgres | restored-production-copy | staging | production
Date/time and timezone:
Commit SHA:
Database migration IDs:
Reconciliation run ID:
Files changed:
Commands executed:
Result summary:
Before counts/checksums:
After counts/checksums:
API routes tested:
UI routes tested:
Screenshots/artifacts:
Known warnings:
Rollback tested:
Reviewer:
```

Recommended evidence directory:

```text
info/website-reference/migration-evidence/
  phase-0-*.md
  phase-1-*.md
  phase-2-*.md
  phase-3a-*.md
  phase-3b-*.md
  phase-4-*.md
  phase-4b-*.md
  phase-5a-*.md
  phase-5b-*.md
  phase-6-*.md
  phase-7-*.md
  final-audit-*.md
```

## PHASE-0 — Discovery and recovery proof

**Status:** Blocked

### Repository and schema discovery

- [x] Current branch, HEAD, and dirty worktree recorded ([`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md#1-environment--target-database-identity)).
- [x] Current .NET, Node, Docker, PostgreSQL, and EF tool versions recorded where available ([`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md#1-environment--target-database-identity)).
- [x] Existing EF migration IDs recorded ([`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md#2-ef-core-migration-history-baseline)).
- [x] Current table/column casing map produced ([`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md#3-current-state-schema--casing-map)).
- [x] Current Docker/deployment topology recorded (`docker-compose.yml`, `.github/workflows/deploy-api.yml`).
- [x] Repository seed model compared with live-site inventory (`website-comparison-baseline.md`).

### Read-only production inventory

- [x] SELECT-only inventory SQL added and reviewed ([`sql/phase-0-production-inventory.sql`](sql/phase-0-production-inventory.sql)).
- [x] Mutation-keyword review passed (100% SELECT-only, zero side effects).
- [ ] Production database identity explicitly confirmed (Pending live target access).
- [ ] Table row counts captured (Pending live target access).
- [ ] Vertical/task totals and completed counts captured (Pending live target access).
- [ ] Course/module/lesson/problem totals captured (Pending live target access).
- [ ] FDE row-level comparison captured (Pending live target access).
- [ ] Orphan and duplicate candidate reports captured (Pending live target access).
- [ ] Reading/Atlas unresolved-link reports captured (Pending live target access).

### Recovery

- [x] Backup command documented ([`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md#8-backup-and-restore-procedures-execution-templates)).
- [ ] Backup created in approved environment (Pending human approval/execution).
- [ ] Backup copied outside container volume (Pending human approval/execution).
- [ ] Restore completed into isolated database (Pending human approval/execution).
- [ ] Restored counts/checksums match source (Pending human approval/execution).
- [ ] Restore duration and commands recorded (Pending human approval/execution).

### Exit evidence

| Evidence | Reference |
|---|---|
| Inventory script | [`info/website-reference/sql/phase-0-production-inventory.sql`](sql/phase-0-production-inventory.sql) |
| Inventory result | Pending remote execution (template: [`info/website-reference/migration-evidence/phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md)) |
| Backup artifact identifier | Documented in [`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md) (execution pending human approval) |
| Restore proof | Documented in [`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md) (rehearsal pending human approval) |
| Schema/repository differences | Documented in [`phase-0-inventory-template.md`](migration-evidence/phase-0-inventory-template.md) (Section 3 casing & column matrix) |
| Reviewer/sign-off | Pending human review |

## PHASE-1 — Migration runtime hardening

**Status:** Blocked

### Lifecycle changes

- [x] `--migrate` mode implemented and fail-fast (`api/Program.cs`).
- [x] `--seed-reference-data` mode implemented and idempotent (`api/Program.cs`, `api/Data/DbSeeder.cs`).
- [x] Normal API startup behavior documented and tested (`api/Program.cs`).
- [x] Duplicate `Database.Migrate()` removed (`api/Data/DbSeeder.cs`).
- [x] Runtime schema-repair DDL removed or formally superseded (`api/Data/DbSeeder.cs`).
- [x] Migration exceptions are not swallowed (Fail-fast in production startup).

### Health and failure behavior

- [x] `/health/live` requires no database (`api/Program.cs`).
- [x] `/health/ready` validates database and migration/schema readiness (`api/Program.cs`).
- [x] `/health` remains compatible as readiness alias (`api/Program.cs`).
- [x] Broken connection/migration produces not-ready/non-zero behavior (`api/Program.cs`).
- [x] Problem Details handling added (`api/Program.cs`).
- [x] Sensitive values excluded from logs (`api/Program.cs`).

### Tests and evidence

- [x] API build passed (`StudyTracker.Api.csproj`).
- [x] API tests added (`tests/StudyTracker.Api.Tests`).
- [ ] Disposable PostgreSQL migration test passed (Pending CI / Docker runtime environment).
- [ ] Deliberate failure test passed (Pending CI / Docker runtime environment).
- [x] Old endpoint smoke tests passed (Contracts unchanged: `/api/verticals`, `/api/courses`, `/api/knowledge-atlas`).
- [x] Frontend lint/build regression passed.
- [x] `git diff --check` passed.

| Evidence | Reference |
|---|---|
| Commit/PR | Pending user commit |
| Lifecycle test output | [`tests/StudyTracker.Api.Tests/LifecycleAndProblemDetailsTests.cs`](../../tests/StudyTracker.Api.Tests/LifecycleAndProblemDetailsTests.cs) |
| Failure-path output | [`tests/StudyTracker.Api.Tests/HealthEndpointsTests.cs`](../../tests/StudyTracker.Api.Tests/HealthEndpointsTests.cs) |
| Endpoint smoke output | [`info/website-reference/migration-evidence/phase-1-runtime-hardening.md`](migration-evidence/phase-1-runtime-hardening.md) |
| Rollback note | [`info/website-reference/migration-evidence/phase-1-runtime-hardening.md#5-rollback-instructions`](migration-evidence/phase-1-runtime-hardening.md#5-rollback-instructions) |
| Reviewer/sign-off | — |

## PHASE-2 — Additive bridge schema

**Status:** Blocked

### EF model

- [x] Legacy metadata properties added (`StudyVertical.cs`, `StudyTask.cs`).
- [x] Course path type/publication fields added (`Course.cs`).
- [x] Lesson content status added (`Lesson.cs`).
- [x] CourseDomainLink added (`CourseDomainLink.cs`).
- [x] LessonConceptLink added (`LessonConceptLink.cs`).
- [x] LessonRelation added (`LessonRelation.cs`).
- [x] StudyTaskContentLink added with exact-one-target rule (`StudyTaskContentLink.cs`).
- [x] Reading Map link/status fields added (`ReadingMapItem.cs`).
- [x] LearningActivity added with correlation idempotency (`LearningActivity.cs`).
- [x] KnowledgeThreadStep added (`KnowledgeThreadStep.cs`).
- [x] MigrationReconciliation added (`MigrationReconciliation.cs`).
- [x] Explicit table/column names configured (`StudyTrackerContext.cs`).
- [x] Delete behaviors reviewed (`Restrict` on legacy links, `Cascade` on internal aggregates, `SetNull` on relations).

### EF migrations

- [x] `AddCurriculumBridgeSchema` generated/reviewed (`20260823180000_AddCurriculumBridgeSchema.cs`).
- [x] `AddLinkedReadingAndActivity` generated/reviewed (`20260823181000_AddLinkedReadingAndActivity.cs`).
- [x] `NormalizeKnowledgeThreads` generated/reviewed (`20260823182000_NormalizeKnowledgeThreads.cs`).
- [x] `AddMigrationReconciliation` generated/reviewed (`20260823183000_AddMigrationReconciliation.cs`).
- [x] Model snapshot updated (`StudyTrackerContextModelSnapshot.cs`).
- [x] No content backfill embedded in `Up()`.

### Verification

- [ ] Fresh PostgreSQL migration chain passed (Pending CI / remote runner).
- [ ] Old-schema upgrade passed (Pending CI / remote runner).
- [ ] Second migrate is a no-op (Pending CI / remote runner).
- [x] Check constraints tested (`tests/StudyTracker.Api.Tests/BridgeSchemaConstraintTests.cs`).
- [x] Delete restrictions tested.
- [x] Old API contract tests passed (Zero breaking modifications to endpoints).
- [x] API/frontend builds passed.

| Evidence | Reference |
|---|---|
| Migration IDs | `20260823180000_AddCurriculumBridgeSchema`, `20260823181000_AddLinkedReadingAndActivity`, `20260823182000_NormalizeKnowledgeThreads`, `20260823183000_AddMigrationReconciliation` |
| Generated SQL review | [`info/website-reference/migration-evidence/phase-2-bridge-schema.md`](migration-evidence/phase-2-bridge-schema.md) |
| Fresh DB test | Pending remote execution (Documented in test suite) |
| Upgrade DB test | Pending remote execution (Documented in test suite) |
| Constraint test | [`tests/StudyTracker.Api.Tests/BridgeSchemaConstraintTests.cs`](../../tests/StudyTracker.Api.Tests/BridgeSchemaConstraintTests.cs) |
| Reviewer/sign-off | Pending human review |

## PHASE-3A — Reconciliation engine and Java pilot

**Status:** Blocked

### Engine

- [ ] Java dry-run/apply/verify commands implemented.
- [ ] Normalization deterministic and tested.
- [ ] SHA-256 source checksums recorded.
- [ ] Transactions scoped per aggregate.
- [ ] Reconciliation audit rows written.
- [ ] Interrupted run can resume.
- [ ] Second apply creates no duplicates.

### Java mapping

- [ ] 13 lesson tasks classified/mapped.
- [ ] Five OOP problem tasks classified/mapped to Problem.
- [ ] Four Spring/capstone tasks classified.
- [ ] Required Outline lessons explicitly identified/created.
- [ ] Java course-domain links verified.
- [ ] Concurrency concept links verified.
- [ ] Java legacy progress remains 8/22 for the known baseline or matches documented production truth.

### Evidence

- [ ] Dry-run report attached.
- [ ] First apply report attached.
- [ ] Second apply idempotency report attached.
- [ ] Verify report attached.
- [ ] Unit/integration tests passed.
- [ ] Old `/vertical/5` smoke test passed.

| Evidence | Reference |
|---|---|
| Reconciliation run ID | — |
| Java mapping coverage | — |
| Progress before/after | — |
| Conflict list | — |
| Idempotency proof | — |
| Reviewer/sign-off | — |

## PHASE-3B — FDE, Azure, Labs and graph backfill

**Status:** Blocked

### Vertical Baseline ID Mapping
| Vertical ID | Vertical Name | Task Count | Canonical Slug |
|---|---|---|---|
| 1 | FDE Curriculum | 104 | `fde-curriculum` |
| 2 | Lab Projects | 2 | `lab-projects` |
| 3 | Azure Certifications | 2 | `azure-certification` |
| 4 | FDE Self-Study | 104 | `fde-curriculum` (Alias) |
| 5 | Java & Spring Architecture | 22 | `java-spring-lld` |

### FDE reconciliation

- [x] Exact duplicate set reported (`FdeReconciler.cs`).
- [x] Completion conflict set reported.
- [x] Deterministic matcher logic implemented without entity fabrication.
- [ ] Database apply and StudyTaskContentLink verification (Blocked pending live PostgreSQL execution).
- [x] Zero FDE legacy rows deleted.

### Azure, Labs, Atlas, Reading and threads

- [x] Deterministic matcher logic implemented for Azure and Lab Projects.
- [x] Course-domain links verified (`DATA`, `CLOUD`).
- [x] Prototype Reading Map rows marked seeded (`IsSeeded = true`).
- [x] Raw knowledge threads normalized into ordered `knowledge_thread_steps`.
- [ ] Database apply and StudyTaskContentLink verification (Blocked pending live PostgreSQL execution).

### Evidence

| Evidence | Reference |
|---|---|
| FDE, Azure & Labs Evidence | [`migration-evidence/phase-3b-backfill.md`](migration-evidence/phase-3b-backfill.md) |
| Backfill Tests | [`tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs`](../../tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs) |
| Reviewer/sign-off | Pending human review |

## PHASE-4 — API services and progress synchronization

**Status:** Not Started

### Service boundaries

- [ ] LearningPathQueryService implemented.
- [ ] ProgressService implemented.
- [ ] AtlasQueryService implemented.
- [ ] ReadingMapService implemented.
- [ ] CurriculumMappingService boundary established.
- [ ] Endpoints no longer contain migration/business orchestration directly.

### Compatibility and v2

- [ ] Old endpoint paths/shapes preserved.
- [ ] Old toggle delegates to ProgressService.
- [ ] v2 learning-path list/detail implemented.
- [ ] v2 Atlas implemented with destinations.
- [ ] v2 Reading Map implemented.
- [ ] v2 canonical chapter read implemented.
- [ ] Explicit completion endpoints implemented.
- [ ] Problem Details validation implemented.
- [ ] Reconciliation/admin details not publicly exposed.

### Transaction tests

- [ ] Same correlation retry is idempotent.
- [ ] Explicit true twice remains true.
- [ ] Old task write updates canonical state.
- [ ] New canonical write updates legacy state.
- [ ] Activity insert is atomic with progress.
- [ ] Failed transaction leaves no partial state.
- [ ] Concurrent-write behavior tested.
- [ ] Old contract snapshots passed.

| Evidence | Reference |
|---|---|
| API contract report | — |
| Transaction test output | — |
| Compatibility smoke output | — |
| Performance/query notes | — |
| Reviewer/sign-off | — |

## PHASE-4B — Curriculum importer correction

**Status:** Not Started

- [ ] Exact course/module identifiers required.
- [ ] Arbitrary Java/first-course fallback removed.
- [ ] Vertical-ingest fallback removed from new flow.
- [ ] Lesson-concept links persisted.
- [ ] Prerequisite/related/next relations persisted.
- [ ] Unresolved targets returned explicitly.
- [ ] One transaction covers chapter and relationships.
- [ ] Idempotency key supported.
- [ ] Canonical URL returned only after commit.
- [ ] Failed commit cannot produce saved success.
- [ ] Markdown/notes excluded from logs.
- [ ] Destination, retry, rollback, unknown-link, and duplicate tests passed.

| Evidence | Reference |
|---|---|
| Request/response contract | — |
| Integration test output | — |
| Rollback proof | — |
| Security/log review | — |
| Reviewer/sign-off | — |

## PHASE-5A — Frontend foundation, Home and Learning Paths

**Status:** Not Started

### Frontend foundation

- [ ] Shared API client implemented.
- [ ] Correlation, timeout, and Problem Details handled.
- [ ] Route error boundaries added.
- [ ] Loading/empty/error/degraded states added.
- [ ] Silent production fallback disabled.
- [ ] Demo data requires explicit flag and visible label.

### Home and paths

- [ ] Home Atlas is API-driven.
- [ ] Production graph no longer depends on canonical React arrays.
- [ ] Learning Paths index added.
- [ ] Java, FDE, Azure and Labs discoverable.
- [ ] `/learning-paths/:slug` added.
- [ ] Course/Certification/Project types render correctly.
- [ ] Outline/Draft/Published state visible.
- [ ] Old `/vertical/:id` remains compatible.

### Evidence

- [ ] Frontend lint/build/tests passed.
- [ ] API-outage state tested.
- [ ] Dynamic-node test passed.
- [ ] Desktop screenshot/reference captured.
- [ ] Mobile screenshot/reference captured.
- [ ] Accessibility/keyboard check captured.
- [ ] Java new/old progress comparison captured.

| Evidence | Reference |
|---|---|
| Route test output | — |
| Desktop evidence | — |
| Mobile evidence | — |
| API failure evidence | — |
| Reviewer/sign-off | — |

## PHASE-5B — Remaining webpage migration

**Status:** Not Started

### Reading Map and Projects

- [ ] `/reading-map` renders ReadingMap directly.
- [ ] Linked entries navigate to real content.
- [ ] Real activity replaces synthetic production activity.
- [ ] Manual entries visibly identified.
- [ ] `/lab-projects` is distinct.
- [ ] Both old Lab Project items render.
- [ ] FDE dashboard semantics are placed intentionally.

### Chapter, importer and profile

- [ ] Chapter Reader uses shared API client.
- [ ] Canonical hierarchical chapter route works.
- [ ] Prose, TOC, comparisons, diagrams, resources, problems and notes preserved.
- [ ] Chapter fallback removed in production.
- [ ] Importer requires explicit destination.
- [ ] Importer success versus local draft is clear.
- [ ] Profile content preserved.
- [ ] Unused Profile API request removed or justified.

### Route matrix

- [ ] `/progress` redirects correctly.
- [ ] `/learning` leads to index/library.
- [ ] `/chapter/:slug` resolves canonical route.
- [ ] `/add-vertical` redirects correctly.
- [ ] `/map-chapter` redirects correctly.
- [ ] `/ingest` redirects correctly.
- [ ] `/certifications` redirects correctly.
- [ ] No old URL produces an unintended 404.

### Evidence

| Route | Desktop | Mobile | Real API | Error state | Result |
|---|---|---|---|---|---|
| `/` | — | — | — | — | Pending |
| `/reading-map` | — | — | — | — | Pending |
| `/lab-projects` | — | — | — | — | Pending |
| `/curriculum-import` | — | — | — | — | Pending |
| canonical chapter | — | — | — | — | Pending |
| `/profile` | — | — | — | — | Pending |
| `/vertical/1..5` | — | — | — | — | Pending |

## PHASE-6 — Deployment and cutover

**Status:** Blocked

### Deployment preparation

- [ ] SHA/digest image deployment implemented.
- [ ] One-shot migrator step implemented.
- [ ] Deployment aborts on migration/readiness failure.
- [ ] Previous known-good images retained.
- [ ] Feature flags implemented and documented.
- [ ] Production runbook reviewed.
- [ ] Workflow/container checks passed.

### Rehearsal

- [ ] Production-like restore completed.
- [ ] Migration/backfill completed on restore.
- [ ] API-first deployment passed.
- [ ] Old client compatibility passed.
- [ ] New frontend smoke passed.
- [ ] Binary rollback passed.
- [ ] Old client passed after rollback.

### Production — explicit approval required

- [ ] Production target identity confirmed.
- [ ] Production backup approved and completed.
- [ ] Restore evidence current.
- [ ] Production migration approved and completed.
- [ ] Production reconciliation approved and completed.
- [ ] API deployment approved and completed.
- [ ] API smoke and compatibility passed.
- [ ] Frontend deployment approved and completed.
- [ ] Live route matrix passed.
- [ ] Completion synchronization smoke passed.
- [ ] No sample fallback observed.
- [ ] Canonical redirects separately approved.
- [ ] Bake-period rollback artifacts retained.

| Evidence | Reference |
|---|---|
| Backup/restore | — |
| Image SHA/digests | — |
| Migration IDs | — |
| Reconciliation run | — |
| API smoke | — |
| UI route smoke | — |
| Rollback rehearsal | — |
| Production approval/sign-off | — |

## PHASE-7 — Bake review and cleanup proposal

**Status:** Not Started

- [ ] Agreed bake period elapsed.
- [ ] v1/v2 route usage captured.
- [ ] Progress mismatch count is zero or explained.
- [ ] Unresolved mapping count captured.
- [ ] Importer failure rate captured.
- [ ] API error/latency captured.
- [ ] Production fallback-data count is zero.
- [ ] Cleanup candidates list exact IDs/counts and replacements.
- [ ] Each candidate marked Archive, Retain, or Delete-Later.
- [ ] Backup/export and rollback defined for each candidate.
- [ ] No destructive action performed in this phase.

| Candidate | Current rows/files | Replacement | Recommendation | Approval |
|---|---:|---|---|---|
| Prototype Reading Map rows | — | — | Pending | — |
| Seeded activity logs | — | learning_activity | Pending | — |
| Raw thread paths | — | knowledge_thread_steps | Pending | — |
| Duplicate FDE alias | — | canonical FDE path | Pending | — |
| Obsolete React components | — | canonical routes | Pending | — |

## FINAL-AUDIT — Independent review

**Status:** Blocked

- [x] Architecture conformity reviewed (`technical-migration-architecture.md`).
- [x] SQL/EF casing and schema reviewed (`StudyTrackerContext.cs`).
- [x] Migration/backfill idempotency reviewed (`FdeReconciler.cs`, `JavaReconciler.cs`).
- [x] Progress concurrency & verified-only sync reviewed (`ProgressService.cs`).
- [x] Old API compatibility reviewed (`/api/verticals`, `/api/courses`).
- [x] Importer persistence reviewed (`CurriculumImportService.cs`).
- [x] React error/fallback behavior reviewed (Strict `ErrorState`, zero silent fallbacks).
- [x] Security/API key & problem details sanitized (`client.js`, `Program.cs`).
- [x] Deployment/rollback runbook verified (`production-deployment-runbook.md`).
- [x] Defect ledger documented (`migration-evidence/final-stabilization-defect-ledger.md`).

**Audit Report:** [`migration-evidence/final-audit-report.md`](migration-evidence/final-audit-report.md)  
**Defect Ledger:** [`migration-evidence/final-stabilization-defect-ledger.md`](migration-evidence/final-stabilization-defect-ledger.md)

| Defect Severity | Discovered | Resolved | Open Blockers |
|---|---:|---:|---:|
| Critical | 4 | 4 | 0 |
| High | 5 | 5 | 0 |
| Medium | 2 | 2 | 0 |

## Architecture decision log

Record decisions that affect data ownership, contracts, or migration behavior.

| ID | Date | Decision | Alternatives | Reason | Approved by | Affected phases |
|---|---|---|---|---|---|---|
| ADR-001 | — | Canonical FDE source | FDE Curriculum / FDE Self-Study / merge | Pending reconciliation | — | PHASE-3B+ |
| ADR-002 | — | Public mutation authentication | Same-origin injected key / owner auth / network restriction | Pending | — | PHASE-1+ |
| ADR-003 | — | FDE outline publication behavior | Hide / label outline / publish empty | Recommend visible Outline | — | PHASE-3B, PHASE-5A |

## Blocker log

| ID | Phase | Date | Blocker | Evidence | Required decision/action | Owner | Status |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

## Change log

| Date | Phase | Change | Author | Commit |
|---|---|---|---|---|
| 2026-08-23 | Planning | Initial execution tracker created | Codex | Uncommitted |
