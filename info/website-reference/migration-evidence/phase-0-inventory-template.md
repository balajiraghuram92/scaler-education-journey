# Neuralascent Phase 0 — Production Inventory & Recovery Evidence

**Phase ID:** `PHASE-0`  
**Execution Type:** Discovery, Production Inventory, and Recovery Proof  
**Execution Timestamp:** 2026-08-23T13:17:00Z  
**Executed By:** Senior Implementation Engineer  
**Script Executed:** [`info/website-reference/sql/phase-0-production-inventory.sql`](../sql/phase-0-production-inventory.sql)  

---

## 1. Environment & Target Database Identity

| Property | Template Field / Value | Verified Target Value |
|---|---|---|
| **Target Environment** | `production` \| `staging` \| `local-rehearsal` | *[Pending Remote Execution]* |
| **Database Host / Container** | `database` (Docker container: `studytracker-db`) | *[Pending Remote Execution]* |
| **Database Port** | `5432` | *[Pending Remote Execution]* |
| **Database Name** | `studytracker` | *[Pending Remote Execution]* |
| **Database User** | `studyuser` | *[Pending Remote Execution]* |
| **PostgreSQL Version** | Target: `PostgreSQL 16.x-alpine` | *[Pending Remote Execution]* |
| **Transaction State** | `pg_is_in_recovery() = false` (Primary RW instance) | *[Pending Remote Execution]* |
| **Git Commit SHA** | Baseline repository HEAD | `a0d02fc` / current HEAD |
| **Container Image API** | `ghcr.io/balajiraghuram92/scaler-education-journey-api` | `latest` |
| **Container Image App** | `ghcr.io/balajiraghuram92/scaler-education-journey-app` | `latest` |

---

## 2. EF Core Migration History Baseline

*Expected migrations recorded in `__EFMigrationsHistory`:*

| Migration ID | Product Version | Expected Status |
|---|---|---|
| `20260707082251_InitialCreate` | `8.0.x` / `9.0.x` | Applied |
| `20260818221200_AddCoursesAndLessonsHierarchy` | `8.0.x` / `9.0.x` | Applied |
| `20260819133000_AddKnowledgeAtlasTables` | `8.0.x` / `9.0.x` | Applied |
| `20260820150000_AddReadingMapTables` | `8.0.x` / `9.0.x` | Applied |
| `20260821040000_AddLessonDifficultyAndChapterTables` | `8.0.x` / `9.0.x` | Applied |

---

## 3. Current-State Schema & Casing Map

### Legacy vs. Redesign Table Naming & Quoting Matrix

| Table Name | PostgreSQL Identifier Type | EF Model Entity | Primary Key | Key Foreign Keys |
|---|---|---|---|---|
| `"Verticals"` | **Quoted PascalCase** | `StudyVertical` | `"Id"` (SERIAL) | — |
| `"Tasks"` | **Quoted PascalCase** | `StudyTask` | `"Id"` (SERIAL) | `"VerticalId"` → `"Verticals"("Id")` |
| `courses` | lower_snake_case | `Course` | `id` (SERIAL) | `vertical_id` → `"Verticals"("Id")` |
| `course_modules` | lower_snake_case | `CourseModule` | `id` (SERIAL) | `course_id` → `courses(id)` |
| `lessons` | lower_snake_case | `Lesson` | `id` (SERIAL) | `module_id` → `course_modules(id)` |
| `problems` | lower_snake_case | `Problem` | `id` (SERIAL) | `lesson_id` → `lessons(id)` |
| `lesson_resources` | lower_snake_case | `LessonResource` | `id` (SERIAL) | `lesson_id` → `lessons(id)` |
| `knowledge_domains` | lower_snake_case | `KnowledgeDomain` | `id` (SERIAL) | — |
| `knowledge_concepts` | lower_snake_case | `KnowledgeConcept` | `id` (SERIAL) | — |
| `domain_concept_connections` | lower_snake_case | `DomainConceptConnection` | `id` (SERIAL) | `domain_id` → `knowledge_domains`, `concept_id` → `knowledge_concepts` |
| `concept_prerequisites` | lower_snake_case | `ConceptPrerequisite` | `id` (SERIAL) | `concept_id` → `knowledge_concepts`, `prerequisite_concept_id` → `knowledge_concepts` |
| `concept_relations` | lower_snake_case | `ConceptRelation` | `id` (SERIAL) | `source_concept_id` → `knowledge_concepts`, `target_concept_id` → `knowledge_concepts` |
| `concept_next_lessons` | lower_snake_case | `ConceptNextLesson` | `id` (SERIAL) | `concept_id` → `knowledge_concepts`, `lesson_id` → `lessons(id)` (nullable) |
| `reading_map_items` | lower_snake_case table, **PascalCase columns** | `ReadingMapItem` | `"Id"` (SERIAL) | — |
| `reading_activity_logs` | lower_snake_case table, **PascalCase columns** | `ReadingActivityLog` | `"Id"` (SERIAL) | — |
| `knowledge_threads` | lower_snake_case table, **PascalCase columns** | `KnowledgeThread` | `"Id"` (SERIAL) | — |
| `lesson_code_comparisons` | lower_snake_case | `LessonCodeComparison` | `id` (SERIAL) | `lesson_id` → `lessons(id)` |
| `lesson_diagrams` | lower_snake_case | `LessonDiagram` | `id` (SERIAL) | `lesson_id` → `lessons(id)` |
| `lesson_notes` | lower_snake_case | `LessonNote` | `id` (SERIAL) | `lesson_id` → `lessons(id)` |

---

## 4. Application Table Row Count Inventory

| Table Name | Expected Seed Baseline | Live / Target Verified Count | Checksum / Match Status |
|---|---|---|---|
| `"Verticals"` | 4–5 | *[Pending Remote Execution]* | Pending |
| `"Tasks"` | 232+ (FDE: 104, Labs: 2, Azure: 2, Java: 22+) | *[Pending Remote Execution]* | Pending |
| `courses` | 1 (`java-spring-lld`) | *[Pending Remote Execution]* | Pending |
| `course_modules` | 4 (Java Modules 1–4) | *[Pending Remote Execution]* | Pending |
| `lessons` | 22 (Java Lessons) | *[Pending Remote Execution]* | Pending |
| `problems` | 14 (Java Practice Problems) | *[Pending Remote Execution]* | Pending |
| `lesson_resources` | 6+ | *[Pending Remote Execution]* | Pending |
| `knowledge_domains` | 8 (Foundations, Backend, etc.) | *[Pending Remote Execution]* | Pending |
| `knowledge_concepts` | 8 (Concurrency, OOP, RAG, etc.) | *[Pending Remote Execution]* | Pending |
| `domain_concept_connections` | 16 | *[Pending Remote Execution]* | Pending |
| `concept_prerequisites` | 8 | *[Pending Remote Execution]* | Pending |
| `concept_relations` | 12 | *[Pending Remote Execution]* | Pending |
| `concept_next_lessons` | 12 | *[Pending Remote Execution]* | Pending |
| `reading_map_items` | 11 (Prototype Reading Seed) | *[Pending Remote Execution]* | Pending |
| `reading_activity_logs` | 8 (Synthetic Daily Bars) | *[Pending Remote Execution]* | Pending |
| `knowledge_threads` | 5 (Raw Path Seed) | *[Pending Remote Execution]* | Pending |
| `lesson_code_comparisons` | 3+ | *[Pending Remote Execution]* | Pending |
| `lesson_diagrams` | 3+ | *[Pending Remote Execution]* | Pending |
| `lesson_notes` | 6+ | *[Pending Remote Execution]* | Pending |

---

## 5. Vertical & Task Inventory Breakdown

| Vertical ID | Vertical Name | Expected Tasks | Expected Completed | Live Target Verified |
|---|---|---|---|---|
| `1` | FDE Curriculum | 104 | 4 (4%) | *[Pending]* |
| `2` | Lab Projects | 2 | 0 (0%) | *[Pending]* |
| `3` | Azure Certifications | 2 | 0 (0%) | *[Pending]* |
| `4` | FDE Self-Study | 104 | 4 (4%) | *[Pending]* |
| `5` | Java & Spring Architecture | 22+ | 8 (36%) | *[Pending]* |

---

## 6. FDE Curriculum vs. FDE Self-Study Row-Level Reconciliation

*Initial findings from checked-in seed models (`FdeSeedData.cs` vs `04-fde-curriculum-tracker.md`):*
- Both verticals share identical 104 curriculum task titles across 8 modules + Agentic AI Core prerequisites.
- Live website shows 4/104 completed on both tracks.
- **Decision Rule:** Never delete or merge either vertical prior to row-level SQL comparison in Phase 3B. If identical in production, designate one canonical path and link the other as an alias without row loss.

---

## 7. ConceptNextLesson Resolution Matrix

| Concept Title | Candidate Lesson Title | Stored `LessonId` | Canonical Resolution Target |
|---|---|---|---|
| Structured Concurrency & Virtual Threads | Structured Concurrency in Practice | `NULL` | Resolve to `lessons.slug = 'structured-concurrency-and-virtual-threads'` |
| OOP-2 & Object Model | Access Modifiers & Encapsulation | `NULL` | Resolve to `lessons.slug = 'oop-2-access-modifiers-constructor-chaining-and-immutability'` |
| Memory Models & Equality | The equals/hashCode Contract | `NULL` | Resolve to `lessons.slug = 'the-equalshashcode-contract-and-memory-symmetry'` |
| Autonomous AI Agents | The Observe-Plan-Act Loop | `NULL` | Resolve to FDE Chapter / Lesson |
| RAG & Vector Search | Hybrid Retrieval Pipelines | `NULL` | Resolve to FDE Chapter / Lesson |

---

## 8. Backup and Restore Procedures (Execution Templates)

> [!IMPORTANT]
> **Production Safety Policy:** These commands are documented execution templates. They must NOT be run automatically by the agent without explicit user direction.

### Backup Procedure (PostgreSQL Custom Dump Format)

```bash
# 1. SSH into EC2 or target deployment host
# Set environment variables with explicit placeholders
export TARGET_DB="studytracker"
export TARGET_USER="studyuser"
export TARGET_CONTAINER="studytracker-db"
export BACKUP_TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
export BACKUP_FILE="${TARGET_DB}_backup_${BACKUP_TIMESTAMP}.dump"
export HOST_BACKUP_DIR="/var/backups/studytracker"

# 2. Ensure host backup directory exists outside container volume
mkdir -p "${HOST_BACKUP_DIR}"

# 3. Perform atomic binary pg_dump (Custom format -F c)
docker exec -t "${TARGET_CONTAINER}" pg_dump -U "${TARGET_USER}" -d "${TARGET_DB}" -F c -b -v > "${HOST_BACKUP_DIR}/${BACKUP_FILE}"

# 4. Verify backup file size and integrity
ls -lh "${HOST_BACKUP_DIR}/${BACKUP_FILE}"
file "${HOST_BACKUP_DIR}/${BACKUP_FILE}"

# 5. (Optional) Upload to S3 for disaster recovery
# aws s3 cp "${HOST_BACKUP_DIR}/${BACKUP_FILE}" "s3://scaler-studytracker-backups/database-backups/${BACKUP_FILE}"
```

### Restore Rehearsal Procedure (Isolated Database)

```bash
# 1. Target an isolated rehearsal database (NEVER overwrite production directly for rehearsal)
export REHEARSAL_DB="studytracker_rehearsal"
export TARGET_USER="studyuser"
export TARGET_CONTAINER="studytracker-db"
export HOST_BACKUP_DIR="/var/backups/studytracker"
export BACKUP_FILE="<SPECIFY_BACKUP_FILENAME>.dump"

# 2. Create clean rehearsal database
docker exec -i "${TARGET_CONTAINER}" psql -U "${TARGET_USER}" -c "DROP DATABASE IF EXISTS ${REHEARSAL_DB};"
docker exec -i "${TARGET_CONTAINER}" psql -U "${TARGET_USER}" -c "CREATE DATABASE ${REHEARSAL_DB};"

# 3. Restore backup into isolated rehearsal database
cat "${HOST_BACKUP_DIR}/${BACKUP_FILE}" | docker exec -i "${TARGET_CONTAINER}" pg_restore -U "${TARGET_USER}" -d "${REHEARSAL_DB}" --clean --if-exists --no-owner --no-privileges -v

# 4. Verify row counts in rehearsal database using the inventory script
docker exec -i "${TARGET_CONTAINER}" psql -U "${TARGET_USER}" -d "${REHEARSAL_DB}" -f - < info/website-reference/sql/phase-0-production-inventory.sql
```

---

## 9. Phase 0 Verification & Exit Checklist

- [x] Read-only SQL inventory script created at [`info/website-reference/sql/phase-0-production-inventory.sql`](../sql/phase-0-production-inventory.sql).
- [x] Manual SQL review passed: 100% SELECT-only queries; zero DDL/DML/mutation keywords.
- [x] Table casing and quote matrix documented across all 19 application tables.
- [x] Safe backup and restore procedure templates documented with explicit placeholders.
- [x] Local environment inspection completed (Docker / psql not active locally; remote execution documented as Pending).
- [x] Zero application source code, Docker compose, or database state mutated.
