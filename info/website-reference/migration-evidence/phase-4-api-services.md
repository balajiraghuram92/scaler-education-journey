# Neuralascent Phase 4 — API Services & Explicit Progress Evidence

**Phase ID:** `PHASE-4`  
**Environment:** `local-codebase` (Target: PostgreSQL 16 on AWS EC2)  
**Date/time and timezone:** 2026-08-23T17:43:00+05:30  
**Commit SHA:** `[Pending user commit]`  

---

## 1. Executive Summary
Phase 4 refactors backend logic into dedicated service boundaries (`ProgressService`, `LearningPathQueryService`, `AtlasQueryService`, `ReadingMapService`), introduces versioned `/api/v2/*` endpoints, and guarantees transactional progress synchronization between canonical entities and legacy tasks.

---

## 2. Endpoints Implemented

| Endpoint | Method | Service | Description |
|---|---|---|---|
| `/api/v2/learning-paths` | GET | `LearningPathQueryService` | List all canonical paths with progress and domains |
| `/api/v2/learning-paths/{slug}` | GET | `LearningPathQueryService` | Detailed path hierarchy, modules, and lessons |
| `/api/v2/knowledge-atlas` | GET | `AtlasQueryService` | Complete domain/concept graph |
| `/api/v2/reading-map` | GET | `ReadingMapService` | Reading map items, normalized threads, and real activities |
| `/api/v2/chapters/{course}/{module}/{lesson}` | GET | Context | Hierarchical Chapter Reader with rich metadata |
| `/api/v2/progress/lesson` | POST | `ProgressService` | Explicit boolean lesson completion with legacy task sync |
| `/api/v2/progress/problem` | POST | `ProgressService` | Explicit boolean problem completion with legacy task sync |
| `/api/v2/progress/task` | POST | `ProgressService` | Explicit boolean task completion with canonical sync |

---

## 3. Atomic Progress Synchronization Invariant
- **Single Database Transaction:** Locking target and bridge rows, updating canonical lesson/problem, updating legacy `Tasks` rows, and logging `LearningActivity` with correlation ID idempotency.
- **Legacy Compatibility:** Old toggle endpoint `/api/tasks/{id}/toggle` delegates to `ProgressService`.

---

## 4. Rollback Instructions
```bash
git checkout -- api/Services/ api/Endpoints/ api/Program.cs
rm -rf tests/StudyTracker.Api.Tests/ProgressSynchronizationTests.cs \
       info/website-reference/migration-evidence/phase-4-api-services.md
```
