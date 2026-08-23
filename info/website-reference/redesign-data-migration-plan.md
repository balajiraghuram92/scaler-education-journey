# Neuralascent Redesign — Data, API, and App Migration Plan

**Prepared:** 2026-08-23

**Companion inventory:** [`website-comparison-baseline.md`](website-comparison-baseline.md)

**Detailed architecture, schema, and execution plan:** [`technical-migration-architecture.md`](technical-migration-architecture.md)

**Local-LLM implementation prompts:** [`local-llm-migration-prompts.md`](local-llm-migration-prompts.md)

**Phase verification tracker:** [`migration-execution-tracker.md`](migration-execution-tracker.md)
**Baseline comparison:** `8ac02c2947c3e3096f78517266bb4beb7d9d1969` → `7102e4d`

## Decision rule

The redesign should change the way the curriculum is discovered and read; it should not discard the curriculum that was already entered. Treat the current PostgreSQL data as source material. Make additive schema changes, backfill links, verify the new pages against real data, then archive or remove obsolete seed-only records. Do not delete a legacy table or user progress merely because its old dashboard is no longer part of the visual design.

The public live site could not be inspected directly during this assessment: `https://98.130.44.145/` presents a TLS certificate whose name does not match the host. The conclusions below use the old baseline commit, current source, checked-in reference assets, API, migrations, and seed data. Re-run the production checklist after AWS has a valid certificate and a reachable API.

## What exists now

| Data area | Current PostgreSQL representation | What it contains | Redesign role |
|---|---|---|---|
| Legacy curriculum | `StudyVertical` → `StudyTask` | Lab Projects, Azure Certifications, FDE Self-Study, Java & Spring Architecture, completion flags, and module labels | Retain as the legacy source and as a compatibility path while the content is mapped to courses and chapters. |
| Structured curriculum | `Course` → `CourseModule` → `Lesson` | A richer Java hierarchy plus lessons, resources, problems, diagrams, comparisons, notes, completion and duration | The canonical reading and learning-path model. Extend it to cover FDE, Azure, and Labs. |
| Knowledge Atlas | `KnowledgeDomain`, `KnowledgeConcept`, domain/concept edges, prerequisites, relations, `ConceptNextLesson` | Eight seeded domains and concepts with graph relationships | The redesign's discovery index. It needs real links into courses and lessons. |
| Reading Map | `ReadingMapItem`, `ReadingActivityLog`, `KnowledgeThread` | A mix of prototype reading items, manually seeded activity bars, and raw text paths | A valid UI concept, but its content must move from sample strings to real curriculum/progress. |
| Importer input | `MapChapterRequest` and `POST /api/chapters/map` | Domain, module, chapter, Markdown, prerequisites, related concepts, next lessons, difficulty and duration | The intended editorial entry point, but it currently persists only the basic course/module/lesson fields. |

## Preserve, migrate, and retire

### Preserve now

Keep all of the following through at least one accepted AWS deployment and a data reconciliation pass:

- Every `StudyVertical`, `StudyTask`, task completion flag, and module label.
- Existing Java courses, modules, lessons, resources, problems, code comparisons, diagrams, notes, and lesson completion flags.
- Knowledge Atlas domains, concepts, and their existing prerequisite/relation records.
- `ConceptNextLesson` text fields until every row that has a real lesson can be linked by `LessonId`.
- User-entered Reading Map rows and any future real activity data.

The old charts, radar values, UI-only AI insight copy, and now-unused dashboard components are code/design debt, not PostgreSQL records. They can be removed after their routes have a verified replacement; they do not require a database cleanup.

### Replace or archive after backfill

The following records are useful as design samples but should not become the long-term progress source:

| Current seed pattern | Evidence in the current app | Recommended disposition |
|---|---|---|
| Duplicate or placeholder Reading Map titles, including repeated Structured Concurrency and labels such as `Next sometime` / `Deferred tomorrow` | `ReadingMapSeedData` | Replace each with a linked, intentional reading item; archive the seed row only after the replacement is visible. |
| List-like titles such as `Structured concurrency (8)` and `APIs in (2)` | `ReadingMapSeedData` | Model these as computed collection counts in the API/UI, not literal database titles. |
| Eight manually seeded activity counts and day labels | `ReadingActivityLog` seed data | Retire after activity is computed from genuine completion, revisit, defer, and note events. Do not use the seed bars as progress history. |
| Raw arrow-separated knowledge paths | `KnowledgeThread.RawPath` | Backfill normalized steps, keep the raw text temporarily for display compatibility, then migrate it out. |
| Text-only `ConceptNextLesson` records | Seeded concept relations | Link to `LessonId` where possible; retain text only for external or not-yet-created lessons. |

Before any archive or deletion: take a PostgreSQL backup, export the affected rows, record their IDs in the migration, and use an `ArchivedAt`/`IsSeeded` marker first. Physical deletion should be a later maintenance task, not part of the visual redesign.

## Additive PostgreSQL changes

These migrations give the new pages a reliable bridge to the old content without duplicating the curriculum.

| Add/change | Why it is needed | Migration/backfill approach |
|---|---|---|
| `course_domain_links` (`CourseId`, `DomainId`, `OrderIndex`) | A course can span several Atlas domains; the existing nullable `Course.VerticalId` cannot describe that relationship. | Link Java to Foundations, Backend, and Reliability; FDE modules/courses to the appropriate domains; Azure to Cloud and Agentic AI. |
| `lesson_concept_links` (`LessonId`, `ConceptId`, `RelationshipType`, `OrderIndex`) | The importer collects prerequisite/related concepts but does not persist them. This lets a chapter reader and Atlas point to the same lesson. | Backfill Structured Concurrency → Concurrency first, then map existing Java/FDE lessons by module and title. |
| `study_task_lesson_links` (`StudyTaskId`, `LessonId`, `LinkType`) | Preserves legacy task completion while a task is represented as a new chapter or lesson. | Create a one-to-one link wherever a task maps cleanly; leave unmatched tasks visible in the legacy route until authoring is complete. |
| Linked Reading Map fields: nullable `LessonId`, nullable `StudyTaskId`, `Status`, `ScheduledFor`, `Priority`, `IsSeeded`, `ArchivedAt` | Turns a free-text board into an actionable reading queue without losing the ability to add manual entries. | Convert known Java items to lesson links; mark demo rows as seeded; retain manual rows as unlinked entries. |
| `learning_activity` event table (`OccurredAt`, `EventType`, `LessonId?`, `StudyTaskId?`, `ReadingMapItemId?`) | Replaces artificial daily bars with auditable activity. | Start recording new events only; do not invent historical activity from the current sample counts. |
| `knowledge_thread_steps` (`KnowledgeThreadId`, `OrderIndex`, `ConceptId?`, `LessonId?`, `Label`) | Makes a thread navigable and lets it survive a title or route change. | Split existing `RawPath` values into labelled steps, then attach known concept/lesson IDs. |

Keep the current tables and add these links rather than trying to merge `StudyTask` and `Lesson` immediately. They represent different levels of fidelity, and an explicit bridge makes migration reversible.

## Curriculum mapping to backfill

The old content should appear as learning paths, not as a recreation of the old analytics dashboard.

| Existing source | New editorial destination | First backfill |
|---|---|---|
| FDE Curriculum and FDE Self-Study | One or two explicitly named FDE paths, depending on the row-level reconciliation | Compare task IDs, titles, modules, completion state, and intended ownership first. The live site renders both as 4/104 with the same visible eight-module structure; if they are duplicates, choose one canonical path and preserve the other as an archived alias until links and progress are verified. |
| Java & Spring Architecture vertical and existing Java course | Java learning path, reachable from Atlas and chapter/library navigation | Link course to Foundations, Backend, Reliability; link concurrency lessons to the Concurrency concept. |
| FDE Self-Study prerequisites and eight modules | FDE learning path with modules and chapter collections | Create/complete an FDE course hierarchy linked to the existing vertical; map modules broadly to Agentic AI, Foundations, Backend, Full-stack, Cloud, Enterprise, Agent Systems, and Reliability. |
| Azure Certifications tasks | Cloud/Agentic AI certification path | Create a course/module/lesson representation and retain the original task links until the chapters are authored. |
| Lab Projects: WMS Defect Detection and Unity Localization | Dedicated Projects path, not Reading Map | Preserve the tasks; add project metadata or a project page model only if the existing task detail cannot give each project a useful destination. |
| Existing Atlas domains/concepts | Home graph plus path/lesson links | Add links to existing courses/lessons rather than hard-coding domain-specific destinations in React. |

## Required API corrections

### Fix the current importer before relying on it

`POST /api/chapters/map` accepts `Prerequisites`, `RelatedConcepts`, and `NextLessons`, but it currently saves none of them. It also searches for a course by a loose title match and, on a miss, falls back to `java-spring-lld` or the first course. A non-Java chapter can therefore be silently stored in Java.

The endpoint should:

1. Resolve a domain by stable slug/ID, not a display-name substring.
2. Require an explicit course/learning path selection when a domain has more than one possible destination.
3. Create a new course only when the request explicitly authorizes it; never silently use the first existing course.
4. Persist `lesson_concept_links`, concept prerequisites/relations, and normalized next-lesson links from the submitted fields.
5. Return the persisted course, module, lesson, concept-link IDs, and canonical chapter URL.
6. Reject unknown concept/relationship names with a useful validation response instead of claiming session-buffer success.

The frontend fallback from `/api/chapters/map` to `/api/verticals/ingest`, followed by an optimistic success message on any error, should be removed or changed to a visibly labelled draft-only mode. An author must be able to distinguish “saved to PostgreSQL” from “not saved.”

### Build read APIs around real links

Prefer a small set of composed read endpoints over recreating the old dashboard metrics:

- `GET /api/learning-paths` and `GET /api/learning-paths/{slug}`: course/vertical summary, modules, lesson counts, completion, and linked Atlas domains.
- Extend `GET /api/knowledge-atlas` with path/lesson destinations so every graph node can navigate to real content.
- Make `GET /api/reading-map` return linked items plus activity calculated from `learning_activity`; keep manual entries as a supported secondary type.
- Return a chapter's concept, prerequisite, related-lesson, and next-lesson links from the chapter endpoint rather than depending on frontend fallback data.

For deployment safety, an EF migration failure must make readiness fail. The current startup flow can log and swallow a migration exception while `/health` reports that PostgreSQL is merely connectable. Health should verify the expected migration version or the API should refuse readiness until migrations complete.

## Required app changes

| Surface | Change needed | Do not do |
|---|---|---|
| Home / Knowledge Atlas | Preserve the graph but add a compact, real-data learning-path index and dynamic graph destinations. Make graph nodes data-driven so added domains/concepts render without React constants. | Restore the old donut/radar/dashboard cards. |
| Navigation | Expose Atlas, Reading Map, Learning Library, and a clear path to Java, FDE, Azure, and Projects. Keep old vertical URLs as compatibility links while migration is underway. | Hide the legacy content merely because the redesign uses fewer top-nav items. |
| Reading Map | Route `/reading-map` directly to `ReadingMap`; derive sections and activity from linked data. | Continue aliasing `/lab-projects` to Reading Map. |
| Lab Projects | Restore a distinct projects page/route using the two existing projects and their real data. | Treat a project collection as a reading backlog. |
| Curriculum Import | Load valid paths/modules/concepts from API, make destination selection explicit, and show the saved canonical URL after success. | Fall back to a Java course or announce success after a failed save. |
| Chapter Reader | Use the configured API base URL and authentication headers for every chapter/notes request; show an explicit unavailable state rather than silently using a production-looking static chapter. | Let fallback sample content mask a failed API or broken migration. |
| Profile/legacy detail | Remove the unused vertical fetch from Profile or render real linked progress. Keep legacy vertical details until each has a confirmed editorial replacement. | Delete legacy route/data before crosswalk acceptance. |

## Safe implementation order

1. **Protect and inspect:** take a database backup; deploy migrations; check API/database logs; compare counts for verticals, tasks, courses, modules, lessons, notes, and completion states.
2. **Add links:** introduce the additive tables/fields, backfill Java first, then FDE, Azure, and Labs. Leave legacy rows untouched.
3. **Correct writes:** repair `chapters/map`, remove the false-success fallback, and add the composed learning-path/Atlas/Reading Map reads.
4. **Expose content:** update routes/navigation, separate Lab Projects, and make Home graph and paths use the new APIs.
5. **Replace prototypes:** convert or archive Reading Map demo rows; begin recording actual activity; normalize knowledge threads.
6. **Retire only after acceptance:** remove obsolete UI components/routes and eventually delete archival seed rows only after a production data check confirms every retained curriculum item has a destination.

## AWS acceptance checklist

- The public hostname has a valid TLS certificate and the live DOM is reachable.
- API logs since deployment have no migration, missing-table, or missing-column errors.
- `/api/knowledge-atlas`, `/api/reading-map`, and a real `/api/chapters/...` response contain database data, not frontend fallback samples.
- Java, FDE, Azure, and the two Lab Projects can each be discovered from the redesigned navigation or Atlas path.
- Importing a test Markdown chapter creates it only in the selected path, stores its relationships, and returns a navigable canonical URL.
- A task/lesson marked complete is reflected consistently in its path and Reading Map.
- Only after these checks may the team mark prototype Reading Map rows and unused legacy UI for archive/removal.
