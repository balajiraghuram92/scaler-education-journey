# Neuralascent Phase 2 — Additive Bridge Schema & EF Model Evidence

**Phase ID:** `PHASE-2`  
**Environment:** `local-codebase` (Target: PostgreSQL 16 on AWS EC2)  
**Date/time and timezone:** 2026-08-23T17:39:00+05:30  
**Commit SHA:** `[Pending user commit]`  
**Database migration IDs:**
1. `20260823180000_AddCurriculumBridgeSchema`
2. `20260823181000_AddLinkedReadingAndActivity`
3. `20260823182000_NormalizeKnowledgeThreads`
4. `20260823183000_AddMigrationReconciliation`  
**Reconciliation run ID:** N/A (Bridge Schema Definition Phase)  

---

## 1. Schema & EF Core Entity Additions

### Additive Schema & Tables Created
1. **Compatibility Extensions on Existing Tables:**
   - `"Verticals"`: `canonical_vertical_id` (FK to `"Verticals"("Id")`, RESTRICT), `archived_at` (timestamptz), `updated_at` (timestamptz DEFAULT now()).
   - `"Tasks"`: `updated_at` (timestamptz DEFAULT now()).
   - `courses`: `path_type` (varchar(32) DEFAULT 'Course' CHECK: `Course, Certification, Project`), `is_published` (boolean DEFAULT true).
   - `lessons`: `content_status` (varchar(32) DEFAULT 'Published' CHECK: `Outline, Draft, Published, Archived`).
   - `reading_map_items`: `lesson_id` (FK to `lessons(id)`, SET NULL), `task_id` (FK to `"Tasks"("Id")`, SET NULL), `status` (varchar(32) DEFAULT 'Planned' CHECK: `Planned, Reading, Completed, Revisited, Deferred, Archived`), `scheduled_for` (date), `priority` (integer DEFAULT 0 CHECK: `0 <= priority <= 100`), `is_seeded` (boolean DEFAULT false), `archived_at` (timestamptz).

2. **New Additive Bridge Tables:**
   - `course_domain_links`: Composite PK `(course_id, domain_id)`, FKs CASCADE to `courses` and `knowledge_domains`, index on `(domain_id, order_index)`.
   - `lesson_concept_links`: Composite PK `(lesson_id, concept_id, relationship_type)`, FKs CASCADE to `lessons` and `knowledge_concepts`, CHECK `ck_lesson_concept_relationship` (`Primary, Related, PrerequisiteContext`), index on `(concept_id, relationship_type, order_index)`.
   - `lesson_relations`: PK `id` (bigserial), FK `source_lesson_id` CASCADE, FK `target_lesson_id` SET NULL, `target_title`, `target_slug`, `relationship_type` CHECK (`Prerequisite, Related, Next`), `resolution_status` CHECK (`Unresolved, Resolved, External`), unique index `ux_lesson_relations_identity` on `(source_lesson_id, relationship_type, LOWER(target_title))`.
   - `study_task_content_links`: PK `task_id` (FK CASCADE to `"Tasks"("Id")`), FK `lesson_id` RESTRICT to `lessons(id)`, FK `problem_id` RESTRICT to `problems(id)`, CHECK `ck_task_content_exactly_one_target` (`num_nonnulls(lesson_id, problem_id) = 1`), CHECK `ck_task_content_mapping_type`, CHECK `ck_task_content_mapping_status`, CHECK `ck_task_content_confidence` (`confidence BETWEEN 0 AND 1`).
   - `learning_activity`: PK `id` (bigserial), `event_type` CHECK, `occurred_at` timestamptz DEFAULT now(), FKs SET NULL to `lessons`, `problems`, `"Tasks"`, `reading_map_items`, `correlation_id` (uuid), `metadata` (jsonb), unique index `ux_learning_activity_correlation_event` on `(correlation_id, event_type)`.
   - `knowledge_thread_steps`: Composite PK `(thread_id, order_index)`, FK CASCADE to `knowledge_threads`, FKs SET NULL to `knowledge_concepts` and `lessons`, CHECK `length(trim(label)) > 0`.
   - `migration_reconciliation`: PK `id` (bigserial), `migration_key`, `source_type`, `source_id`, `target_type`, `target_id`, `source_checksum`, `status` CHECK (`Discovered, Mapped, Applied, Verified, Conflict, Skipped`), `issue_code`, `details` (jsonb), `applied_at`, `updated_at`, unique index `ux_migration_reconciliation_identity` on `(migration_key, source_type, source_id)`.

---

## 2. Files Changed & Created

| File | Type | Purpose |
|---|---|---|
| `api/Models/CourseDomainLink.cs` | New | Course to Atlas Domain mapping entity model. |
| `api/Models/LessonConceptLink.cs` | New | Lesson to Knowledge Concept relationship entity model. |
| `api/Models/LessonRelation.cs` | New | Inter-lesson prerequisite, related, and next lesson entity model. |
| `api/Models/StudyTaskContentLink.cs` | New | Legacy StudyTask to canonical Lesson/Problem bridge model. |
| `api/Models/LearningActivity.cs` | New | Real event-sourced activity log model. |
| `api/Models/KnowledgeThreadStep.cs` | New | Normalized knowledge thread sequence step model. |
| `api/Models/MigrationReconciliation.cs` | New | Idempotent reconciliation and backfill tracking model. |
| `api/Models/StudyVertical.cs` | Modify | Added canonical alias, archive, and update metadata. |
| `api/Models/StudyTask.cs` | Modify | Added update metadata and ContentLink navigation. |
| `api/Models/Course.cs` | Modify | Added PathType, IsPublished, DomainLinks navigation. |
| `api/Models/Lesson.cs` | Modify | Added ContentStatus and relationship collections. |
| `api/Models/Problem.cs` | Modify | Added LegacyTaskLinks navigation. |
| `api/Models/KnowledgeDomain.cs` | Modify | Added CourseLinks navigation. |
| `api/Models/KnowledgeConcept.cs` | Modify | Added LessonLinks and ThreadSteps navigation. |
| `api/Models/ReadingMapItem.cs` | Modify | Added canonical links, status, schedule, priority, seed metadata. |
| `api/Models/KnowledgeThread.cs` | Modify | Added Steps navigation collection. |
| `api/Data/StudyTrackerContext.cs` | Modify | Configured DbSets, composite keys, check constraints, delete behaviors. |
| `api/Migrations/20260823180000_AddCurriculumBridgeSchema.cs` | New | EF Migration 1: Bridge schema & compatibility columns. |
| `api/Migrations/20260823181000_AddLinkedReadingAndActivity.cs` | New | EF Migration 2: Reading map links and learning activity events. |
| `api/Migrations/20260823182000_NormalizeKnowledgeThreads.cs` | New | EF Migration 3: Knowledge thread steps table. |
| `api/Migrations/20260823183000_AddMigrationReconciliation.cs` | New | EF Migration 4: Migration reconciliation audit table. |
| `api/Migrations/StudyTrackerContextModelSnapshot.cs` | Modify | Updated full EF Core model snapshot. |
| `tests/StudyTracker.Api.Tests/BridgeSchemaConstraintTests.cs` | New | Integration tests validating bridge constraints and enums. |
| `info/website-reference/migration-execution-tracker.md` | Modify | Updated Phase 2 status and checklist. |

---

## 3. Mandatory Verification Checks

| Check | Result | Evidence / Notes |
|---|---|---|
| Four Ordered Migrations Generated | Verified | `AddCurriculumBridgeSchema` → `AddLinkedReadingAndActivity` → `NormalizeKnowledgeThreads` → `AddMigrationReconciliation`. |
| Exclusive Arc Check (`num_nonnulls(lesson_id, problem_id) = 1`) | Configured | Embedded in EF migration and model snapshot. |
| Restrict Delete Behavior on Content Links | Configured | Deleting canonical Lesson or Problem is blocked if a linked legacy task exists. |
| LearningActivity Correlation Uniqueness | Configured | Unique constraint on `(correlation_id, event_type)` ensures idempotent write retries. |
| Zero Content Mutations / Backfills in `Up()` | Verified | All migrations are 100% additive DDL only; zero DML statements in migration classes. |
| Git Whitespace Check (`git diff --check`) | Passed | Clean exit code `0`. |

---

## 4. Rollback Instructions

Operational rollback for Phase 2 follows the **binary rollback** policy (reverting application code while keeping additive schema in PostgreSQL):
```bash
git checkout -- api/Data/StudyTrackerContext.cs \
                api/Models/ \
                api/Migrations/StudyTrackerContextModelSnapshot.cs \
                info/website-reference/migration-execution-tracker.md
rm -rf api/Models/CourseDomainLink.cs \
       api/Models/LessonConceptLink.cs \
       api/Models/LessonRelation.cs \
       api/Models/StudyTaskContentLink.cs \
       api/Models/LearningActivity.cs \
       api/Models/KnowledgeThreadStep.cs \
       api/Models/MigrationReconciliation.cs \
       api/Migrations/20260823180000_* \
       api/Migrations/20260823181000_* \
       api/Migrations/20260823182000_* \
       api/Migrations/20260823183000_* \
       tests/StudyTracker.Api.Tests/BridgeSchemaConstraintTests.cs \
       info/website-reference/migration-evidence/phase-2-bridge-schema.md
```
