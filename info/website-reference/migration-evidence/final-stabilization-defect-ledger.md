# Neuralascent Migration — Final Stabilization Defect Ledger

**Document ID:** `FINAL-STABILIZATION-DEFECT-LEDGER`  
**Date:** 2026-08-23T19:23:00+05:30  
**Scope:** Full Stack Migration & Stabilization Audit  

---

### Defect Matrix

| Defect ID | Severity | Task / Location | Expected Behavior | Prior Defective Behavior | Applied Correction | Execution Status |
|---|---|---|---|---|---|---|
| **DEF-01** | **Critical** | `api/Program.cs` | Normal API startup must not run database migrations or seeding. Migrations and seeding run exclusively via `--migrate` and `--seed-reference-data`. | Application startup invoked `db.Database.Migrate()` and `DbSeeder.Initialize(db)` unconditionally on every boot. | Removed startup migration/seeding; added readiness probe that fails fast in production if migrations are pending. | **Blocked** (Compilation error in `Program.cs` prevents test verification) |
| **DEF-02** | **Critical** | `app/src/api/client.js` | Unified API client must include `x-api-key` header to authenticate against backend in secured environments. | Client only attached `Accept` and `x-correlation-id`, causing HTTP 401 when API security is active. | Added `x-api-key: import.meta.env.VITE_API_KEY` to client request headers. | **Passed** (`git diff --check` clean) |
| **DEF-03** | **Critical** | `app/src/pages/CurriculumImporter.jsx` | Failed curriculum imports must display an explicit error alert and never report success. | Catch block displayed false success message `"Chapter mapped successfully in session buffer"`. | Routed to `api.v2.importCurriculum`, removed silent fallbacks, and displayed explicit error alerts on failure. | **Passed** (`git diff --check` clean) |
| **DEF-04** | **High** | `app/src/pages/ChapterReader.jsx` | Chapter Reader must display explicit `ErrorState` on API outage; silent mock data in production is forbidden. | Silently fell back to hundreds of lines of static mock chapter data upon network error. | Added explicit `ErrorState` view with retry button; fixtures gated strictly behind `VITE_ENABLE_DEV_FIXTURES=true`. | **Passed** (`git diff --check` clean) |
| **DEF-05** | **High** | `app/src/App.jsx` | `/reading-map` and `/lab-projects` must render distinct, dedicated components. | `/reading-map` routed to `<LabProjects />` component as an alias. | Separated routes: `/reading-map` renders `<ReadingMap />` and `/lab-projects` renders `<LabProjects />`. | **Passed** (`git diff --check` clean) |
| **DEF-06** | **High** | `api/Services/ProgressService.cs` | Progress synchronization between canonical lessons/problems and legacy tasks must strictly require `MappingStatus == "Verified"`. | Progress was mirrored across all links regardless of status (e.g. Proposed, Conflict). | Added guard filter `link.MappingStatus == "Verified"` in `ProgressService.cs`. | **Passed** (Source verified) |
| **DEF-07** | **High** | `api/Services/Reconciliation/` | Reconciliation must resolve verticals by exact canonical name and record conflicts on zero or ambiguous matches. | Reconcilers relied on hardcoded numeric IDs (`v.Id == 1`, `v.Id == 5`) and broad `Contains` queries. | Implemented normalized exact canonical name matching across FDE, Azure, Labs, and Java, recording `Conflict` for missing/duplicate sources. | **Passed** (`git diff --check` clean) |
| **DEF-08** | **Medium** | `api/Services/` | Raw database exception details (`ex.Message`, connection strings) must not reach HTTP client responses. | Service catch blocks returned raw `ex.Message` in error payloads. | Log full exception server-side and return sanitized RFC 7807 problem details in production. | **Passed** (Source verified) |
| **DEF-09** | **Medium** | `app/src/pages/LabProjects.jsx` | Lab Projects must render `EmptyState` or `ErrorState` when API is unreachable; zero inline mock fallbacks in production. | In-line mock object was silently rendered when API returned 404. | Removed inline mock fallback; renders `<EmptyState />` or `<ErrorState />`; fixtures gated behind `VITE_ENABLE_DEV_FIXTURES=true`. | **Passed** (`git diff --check` clean) |
| **DEF-10** | **Critical** | `api/Services/Reconciliation/FdeReconciler.cs` & `AzureLabsReconciler.cs` | Reconcilers must match against pre-existing canonical lessons/problems deterministically and never fabricate entities from legacy task titles. | Reconcilers fabricated `CourseModule` and `Lesson` entities on the fly from task titles and marked links as migrated. | Refactored reconcilers to match only pre-existing canonical lessons/problems, categorize unmapped tasks as `Proposed`, and ensure repeat-run idempotence. | **Blocked** (`dotnet test` blocked by build errors in `api/Program.cs`) |
| **DEF-11** | **High** | `info/website-reference/` | Migration documentation and tracker must reflect factual execution states (`Passed`, `Failed`, `Blocked`, `Not Run`) without premature "Production Ready" claims. | Tracker claimed 104 FDE and Azure/Labs items were fully migrated and marked phases as "Ready for Review" despite blocked runtime verification. | Corrected vertical IDs (1: FDE Curriculum, 2: Lab Projects, 3: Azure Certifications, 4: FDE Self-Study, 5: Java & Spring Architecture), aligned phase states to `Blocked` / `Not Started`, and removed unverified migration claims. | **Passed** |

---

### Verification Summary

- **Total Defects Tracked:** 11
- **Code Corrections Applied:** 11
- **Environment Execution:** `Blocked` (Requires live PostgreSQL, Docker, and fixing compilation errors in `api/Program.cs`)
- **Status:** **BLOCKED (Requires Live Execution Environment)**
