# Neuralascent Phase 3B — FDE, Azure, Labs & Graph Backfill Evidence

**Phase ID:** `PHASE-3B`  
**Environment:** `local-codebase` (Target: PostgreSQL 16 on AWS EC2)  
**Date/time and timezone:** 2026-08-23T19:23:00+05:30  
**Commit SHA:** `[Pending user commit]`  
**Reconciliation Scope:** `fde`, `azure-labs`, `atlas-reading`, `knowledge-threads`  
**Execution Status:** **`Blocked`** (Live PostgreSQL required for reconciliation apply and database verification)  

---

## 1. Executive Summary
Phase 3B implements deterministic cross-vertical reconciliation logic across FDE Curriculum and Self-Study tracks, Azure Certifications, Lab Projects, Atlas Domain links, Reading Map seed tagging, and Knowledge Thread normalization into `knowledge_thread_steps`. Tasks without pre-existing canonical lesson or problem entities are categorized as `Proposed` without fabricating database records.

---

## 2. Vertical Baseline Inventory & ID Mapping

| Vertical ID | Vertical Name | Legacy Task Count | Canonical Path Slug | Path Type | Link Creation Status |
|---|---|---|---|---|---|
| **1** | FDE Curriculum | 104 | `fde-curriculum` | Course | Deterministic matcher implemented; unmapped tasks categorized as `Proposed` without fabricating entities. DB apply: `Blocked`. |
| **2** | Lab Projects | 2 | `lab-projects` | Project | Deterministic matcher implemented; unmapped tasks categorized as `Proposed`. DB apply: `Blocked`. |
| **3** | Azure Certifications | 2 | `azure-certification` | Certification | Deterministic matcher implemented; unmapped tasks categorized as `Proposed`. DB apply: `Blocked`. |
| **4** | FDE Self-Study | 104 | `fde-curriculum` (Alias) | Course | Duplicate alias matcher implemented; soft-aliased (`CanonicalVerticalId = 1`) on apply. DB apply: `Blocked`. |
| **5** | Java & Spring Architecture | 22 | `java-spring-lld` | Course | Deterministic matcher implemented (13 Lessons, 5 Problems, 4 Outline items). DB apply: `Blocked`. |

---

## 3. Knowledge Graph & Reading Map Backfill
- **Reading Map:** Existing prototype items tagged with `IsSeeded = true`; exact Java lessons linked where pre-existing.
- **Knowledge Threads:** `knowledge_threads.RawPath` parsed and normalized into `knowledge_thread_steps` table preserving step sequence order.
- **CourseDomainLinks:** Populated for Data (`DATA`), Cloud (`CLOUD`), and Foundations/Backend/Reliability domains.

---

## 4. Rollback Instructions

```bash
git checkout -- api/Services/Reconciliation/ \
                tests/StudyTracker.Api.Tests/BackfillReconciliationTests.cs \
                info/website-reference/migration-execution-tracker.md
rm -rf info/website-reference/migration-evidence/phase-3b-backfill.md
```
