# Neuralascent Phase 7 — Bake-Period Review & Cleanup Proposal

**Document Version:** 1.0.0  
**Status:** Proposal (Zero Destructive Changes Applied)  
**Strict Policy:** No physical database deletions (`DROP TABLE`, `DELETE`, `TRUNCATE`) without explicit human sign-off.

---

## 1. Bake-Period Acceptance Criteria

Following production deployment of Phase 6, a 14-day bake period monitors the following operational metrics:

1. **Traffic & Route Telemetry:** Zero unexpected 404s on legacy routes (`/vertical/*`, `/progress`, `/certifications`).
2. **Progress Synchronization Integrity:** Zero discrepancies between `study_task_content_links` and legacy `Tasks.IsCompleted`.
3. **Reconciliation Audit:** 100% of legacy tasks verified and mapped in `migration_reconciliation`.
4. **API Latency & Error Rate:** Sub-50ms p95 latency on `/api/v2/*` endpoints with zero 500 errors.

---

## 2. Soft-Archival Candidates

| Candidate Entity / Table | Current Row Count | Recommended Action | Justification |
|---|---|---|---|
| Prototype `reading_map_items` | ~10 rows | `Soft-Archive` (`archived_at = now()`) | Prototype mock items superseded by canonical lesson links. |
| Duplicate Vertical `FDE Self-Study` (Id: 2) | 1 vertical | `Soft-Archive` (`canonical_vertical_id = 1`) | FDE Curriculum is the canonical vertical; self-study remains accessible via alias link. |
| Legacy `Verticals` / `Tasks` tables | 5 Verticals / ~250 Tasks | `Retain Indefinitely` | Preserves 100% backward compatibility with legacy endpoints. |

---

## 3. Destructive Migration Exclusion
Physical drops of tables (`"Verticals"`, `"Tasks"`) or columns are **NOT** included in this proposal and will only be considered in a future major architectural version after complete deprecation of legacy clients.
