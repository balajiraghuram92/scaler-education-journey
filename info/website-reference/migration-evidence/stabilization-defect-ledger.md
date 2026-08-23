# Neuralascent Migration — Stabilization Defect Ledger (FINAL-00 to FINAL-02A)

**Document ID:** `DEFECT-LEDGER-01`  
**Date:** 2026-08-23T19:14:30+05:30  
**Scope:** Full Stack Stabilization Audit  

---

### Defect Ledger

| Defect ID | Severity | File & Location | Expected Behavior | Current / Prior Behavior | Applied Correction | Status |
|---|---|---|---|---|---|---|
| **DEF-01** | **Critical** | `api/Program.cs` | Normal API startup must not run database migrations or seeding. Migrations and seeding run exclusively via `--migrate` and `--seed-reference-data`. | Application startup invoked `db.Database.Migrate()` and `DbSeeder.Initialize(db)` unconditionally on every boot. | Removed startup migration/seeding; added readiness probe that fails fast in production if migrations are pending. | **Resolved** |
| **DEF-02** | **Critical** | `app/src/api/client.js` | Unified API client must include `x-api-key` header to authenticate against backend in secured environments. | Client only attached `Accept` and `x-correlation-id`, causing HTTP 401 when API security is active. | Added `x-api-key: import.meta.env.VITE_API_KEY` to client request headers. | **Resolved** |
| **DEF-03** | **Critical** | `app/src/pages/CurriculumImporter.jsx` | Failed curriculum imports must display an explicit error alert and never report success. | Catch block displayed false success message `"Chapter mapped successfully in session buffer"`. | Routed to `api.v2.importCurriculum`, removed silent fallbacks, and displayed explicit error alerts on failure. | **Resolved** |
| **DEF-04** | **High** | `app/src/pages/ChapterReader.jsx` | Chapter Reader must display explicit `ErrorState` on API outage; silent mock data in production is forbidden. | Silently fell back to hundreds of lines of static mock chapter data upon network error. | Added explicit `ErrorState` view with retry button; fixtures gated strictly behind `VITE_ENABLE_DEV_FIXTURES=true`. | **Resolved** |
| **DEF-05** | **High** | `app/src/App.jsx` | `/reading-map` and `/lab-projects` must render distinct, dedicated components. | `/reading-map` routed to `<LabProjects />` component as an alias. | Separated routes: `/reading-map` renders `<ReadingMap />` and `/lab-projects` renders `<LabProjects />`. | **Resolved** |
| **DEF-06** | **High** | `api/Services/ProgressService.cs` | Progress synchronization between canonical lessons/problems and legacy tasks must strictly require `MappingStatus == "Verified"`. | Progress was mirrored across all links regardless of status (e.g. Proposed, Conflict). | Added guard filter `link.MappingStatus == "Verified"` in `ProgressService.cs`. | **Resolved** |
| **DEF-07** | **High** | `api/Services/Reconciliation/` | Reconciliation must resolve verticals by exact canonical name and fail on zero or multiple ambiguous matches. | Reconcilers relied on hardcoded numeric IDs (`v.Id == 1`, `v.Id == 5`) and broad `Contains` queries. | Implemented exact canonical name lookups and explicit ambiguity validation throwing `InvalidOperationException`. | **Resolved** |
| **DEF-08** | **Medium** | `api/Services/` | Raw database exception details (`ex.Message`, connection strings) must not reach HTTP client responses. | Service catch blocks returned raw `ex.Message` in error payloads. | Log full exception server-side and return sanitized RFC 7807 problem details in production. | **Resolved** |
| **DEF-09** | **Medium** | `app/src/pages/LabProjects.jsx` | Lab Projects must render `EmptyState` or `ErrorState` when API is unreachable; zero inline mock fallbacks in production. | In-line mock object was silently rendered when API returned 404. | Removed inline mock fallback; renders `<EmptyState />` or `<ErrorState />`; fixtures gated behind `VITE_ENABLE_DEV_FIXTURES=true`. | **Resolved** |
