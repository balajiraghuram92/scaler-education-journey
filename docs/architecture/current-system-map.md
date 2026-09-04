# Neuralascent: Current System Map

**Phase:** 0 — understand the existing application  
**Observed:** 2026-09-02  
**Live site:** `https://neuralascent.top/`  
**Workspace:** this repository, especially `app/src`, `api/`, `api/Data/`, `api/Models/`, `api/Services/`, and `api/Migrations/`

## How to read this document

This is an exploration record, not a proposed redesign.

| Confidence | Meaning |
|---|---|
| **Observed live** | Seen by navigating the deployed site and reading its rendered page state. |
| **Source-backed** | Confirmed in the checked-in frontend/backend source. |
| **Inferred** | The most likely backend/database behavior based on the endpoint implementation and EF Core model. It should be verified with a server-side trace or SQL logging before migration. |

## 1. Executive summary

Neuralascent is a React/Vite single-page application backed by an ASP.NET Core minimal API. The current deployed entry point redirects `/` to `/chapters`, which is the curriculum-library surface. The visible application is organized around learning pathways and chapter readers rather than the older vertical/task dashboard.

The canonical curriculum hierarchy is:

```text
Course / learning path
  -> Course module
    -> Lesson / chapter
      -> Problems
      -> Resources
      -> Code comparisons
      -> Diagrams
      -> Notes
      -> Concept links
      -> Lesson relations
```

There are two API generations:

- **V2/canonical APIs** under `/api/v2`, used by the current curriculum-library, pathway-detail, chapter-reader, reading-map, and curriculum-import pages.
- **Legacy APIs** under `/api`, still used by the compatibility `/vertical/:id` route and the older Java practice dashboard. Several legacy endpoints are also retained as migration bridges.

The browser client sends `Accept: application/json` and a generated `x-correlation-id` for requests made through `app/src/api/client.js`. The client does not add an `x-api-key`; the backend contains shared API-key middleware, so the deployed reverse-proxy/runtime configuration needs to be checked before treating that boundary as operationally complete.

The database is PostgreSQL accessed through Entity Framework Core/Npgsql. The EF model and migrations are more current than `api/Data/schema.sql`: the latter stops after the original Knowledge Atlas tables, while the migrations and `StudyTrackerContext` add lesson enrichment, reading activity, bridge, and reconciliation tables.

## 2. Live site exploration

### 2.1 Global shell

**Observed live:** every explored page had the same small editorial navigation shell:

- left: Neuralascent logo/name, linking to `/` and therefore `/chapters`;
- right: “By Raghuram Balaji”, linking to `/profile`;
- no visible global navigation links for Reading Map, Lab Projects, or Curriculum Import in the current deployed shell. Those surfaces are reachable through direct routes and through older/home components.

### 2.2 Current active pathways

**Observed live at `/chapters`:**

| Pathway | Route | Progress shown | Modules |
|---|---|---:|---:|
| Java Low-Level Design & Spring Architecture | `/chapters/java-spring-lld` | 3 of 88 lessons, 3% | 10 |
| Forward Deployed Engineer (FDE) | `/chapters/fde-curriculum` | 4 of 152 lessons, 3% | 12 |
| Databases & SQL | `/chapters/databases-sql` | 0 of 13 lessons, 0% | 1 |
| High-Level Design | `/chapters/high-level-design` | 0 of 21 lessons, 0% | 1 |
| Data Engineering | `/chapters/data-engineering` | 0 of 24 lessons, 0% | 1 |

The index also showed six planned pathways. They are rendered from the frontend catalog when no matching active API path exists:

- Data Structures & Algorithms
- SQL & Data Foundations
- Frontend Engineering with React
- Machine Learning & Deep Learning
- AWS Cloud Engineering
- DevOps & Platform Engineering

The FDE and Data Engineering entries are present in the static catalog too, but become active when the API returns them.

### 2.3 Pathway detail

**Observed live:** opening a pathway shows:

- breadcrumb back to Chapters;
- pathway title, description, percentage, and completed/total lesson count;
- one card per module;
- module completion counts;
- lesson cards containing title, estimated duration, difficulty, content status, and a `Continue` marker on the first incomplete lesson;
- lesson cards linking to the hierarchical chapter route.

The pathway page is display/navigation oriented. It does not visibly expose a lesson-completion button.

### 2.4 Chapter reader

**Observed live on a database lesson:**

`/chapter/databases-sql/databases-sql/db-sql-01-introduction-keys` rendered:

- `PANEL D: CURRICULUM CHAPTER` label;
- left table-of-contents rail with section anchors;
- breadcrumb trail: Chapters → pathway → lesson;
- lesson title and description;
- editorial sections such as Concepts Covered, Practical Backend Scenario, Practice Loop, Evidence of Understanding, and Suggested Extension;
- right contextual sidebar with Pathway, Module, Further reading, Personal note, and Upcoming session;
- `+ Note` control, which opens an unsaved note form with a textbox, Save Note, and Cancel;
- on richer Java chapters: concept checks, practice questions, implementation exercises, code comparisons, diagrams, problem cards, previous/next chapter navigation, and sibling lessons.

### 2.5 Reading Map

**Observed live at `/reading-map`:**

- title: Reading Map & Knowledge Flow;
- displayed statistic: `4 / 10 Items Read`, `40% Queue Progress`;
- filter controls: All, ReadThisWeek, Revisited, Deferred, Lists, Prerequisites;
- current items included examples such as Java Concurrency, Spring async and resilience, Virtual threads, Structured concurrency, and deferred/list items;
- Knowledge Threads: Java, Backend, and Cloud paths;
- a recent-activity area is supported by the data contract but was not populated in the visible snapshot.

Clicking a category filter changed the visible list locally and did not navigate.

The current `ReadingMap.jsx` does not render a completion toggle for each item, even though the legacy API has a PATCH endpoint for toggling an item.

### 2.6 Profile

**Observed live at `/profile`:** a mostly static author/profile page with:

- Raghuram Balaji / AI Architect Candidate;
- professional background narrative;
- View GitHub link (`https://github.com` in the checked-in component);
- Azure certification section with AI-103 and AI-200 cards;
- Core Architectural Pillars cards.

No API request is made by `Profile.jsx`; the content is frontend-owned.

### 2.7 Lab Projects

**Observed live at `/lab-projects`:** the page displayed “Engineering Lab Sandboxes”, “Live Project Track”, and the empty state “No active lab project courses found in the curriculum.”

The component first tries to load a canonical `lab-projects` learning path. If it receives 404, it loads all canonical paths and looks for `lab-projects` or `labs`. Development-only fixtures can render sample labs when enabled, but those fixtures were not visible on the deployed site.

### 2.8 Curriculum Import

**Observed live at `/curriculum-import`:** an import/editor page with:

- Import button;
- Markdown template selector: Raw / Default, Java Virtual Threads, Agentic AI & RAG;
- Markdown textarea;
- `.md`/`.markdown` file-load dropzone;
- live table-of-contents/prose/code preview;
- Domain and Module selectors;
- Chapter title input;
- prerequisite selector;
- related-concept chips that can be added/removed locally;
- an admin/IAM notice.

The page can be explored without submitting. Import submission is a write operation and was intentionally not sent during Phase 0.

## 3. Network/action trace

### 3.1 Representative action: click a lesson card

**Scenario:** from the live Databases & SQL pathway, click `Introduction to DBMS & Keys`.

| Step | Result |
|---|---|
| Starting page | `https://neuralascent.top/chapters/databases-sql` |
| Visible control | Lesson link titled `Introduction to DBMS & Keys` |
| Link target | `/chapter/databases-sql/databases-sql/db-sql-01-introduction-keys` |
| Resulting page | `https://neuralascent.top/chapter/databases-sql/databases-sql/db-sql-01-introduction-keys` |
| Frontend component | `ChapterReader` |
| Frontend API method | `api.v2.getChapter(courseSlug, moduleSlug, lessonSlug)` |
| Request | `GET /api/v2/chapters/databases-sql/databases-sql/db-sql-01-introduction-keys` |
| Request body | None |
| Success behavior | JSON is stored in React state and the chapter reader renders. |
| Write side effect | None for the lesson-open request. |

The request is constructed in `app/src/api/client.js` as:

```text
/api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}
```

For requests made through `apiClient`, the frontend also constructs:

```text
Accept: application/json
x-correlation-id: <crypto.randomUUID()>
```

The browser client available for this exploration exposed page DOM, screenshots, and console logs but not a Network-panel event stream. Pressing the DevTools shortcut did not open a panel in the in-app browser. Therefore the exact method/path above is source-backed and validated by the live navigation/rendered result; raw Network-tab timing, response headers, and SQL statements are not claimed as observed here. A future local run with browser DevTools or ASP.NET/EF SQL logging should capture those wire-level details.

### 3.2 What the backend does for that GET

`V2Endpoints.cs` queries `lessons` by the three-part identity:

```text
lesson.slug       = lessonSlug
module.slug       = moduleSlug
course.slug       = courseSlug
```

It eagerly loads:

- the parent module and course;
- problems;
- lesson resources;
- code comparisons;
- diagrams;
- notes;
- linked concepts and their concept rows;
- outgoing lesson relations.

On success, the response contains lesson metadata/content, parent course/module summaries, and arrays for problems, resources, code comparisons, diagrams, notes, concepts, and related lessons. On a miss it returns a 404 with an error message identifying the requested composite path.

### 3.3 Likely SQL/data path

**Inferred from EF Core navigation loading:** one logical reader request touches the following relational areas:

```text
courses
  -> course_modules
    -> lessons
       -> problems
       -> lesson_resources
       -> lesson_code_comparisons
       -> lesson_diagrams
       -> lesson_notes
       -> lesson_concept_links -> knowledge_concepts
       -> lesson_relations
```

The exact number of SQL statements depends on EF Core query splitting/configuration and should be captured with EF command logging. The important migration contract is the response shape and the identity lookup, not a presumed single SQL statement.

### 3.4 Follow-up actions available from the reader

Opening the lesson itself is read-only. The reader then offers these possible actions:

- click table-of-contents links: local smooth scrolling;
- click sibling/previous/next chapter links: another chapter GET;
- click `+ Note`: local form state only;
- click Save Note: POST `/api/lessons/{lessonId}/notes` and insert a lesson note;
- open an implementation exercise: GET exercise metadata from the filesystem-backed exercise API;
- edit/run an implementation exercise: POST submitted source to the exercise runner;
- answer concept checks/practice questions: local React state; no persistence endpoint in these components.

## 4. Feature → page → API → backend responsibility → database table map

This is the requested current-system map. “No table” means the behavior is frontend-only or filesystem/Docker-backed; it does not mean the feature is unimportant.

| Feature / user action | Page or route | API endpoint(s) | What the backend probably does | Database table(s) |
|---|---|---|---|---|
| Redirect root to curriculum library | `/` | None; React Router redirect to `/chapters` | No server domain work; SPA route redirect | None |
| Load active learning pathways | `/chapters` | `GET /api/v2/learning-paths` | `LearningPathQueryService.GetAllLearningPathsAsync` loads courses, domains, modules, lessons, and problems; computes totals/completion percentages and maps domain names | `courses`, `course_domain_links`, `knowledge_domains`, `course_modules`, `lessons`, `problems` |
| Display planned pathways | `/chapters` | None for planned cards | Filters static `pathwayCatalog` against active API slugs and renders remaining catalog entries | None; frontend catalog in `app/src/content/curriculumCatalog.js` |
| Open a learning pathway | `/chapters/:slug`, `/learning-paths/:slug` | `GET /api/v2/learning-paths/{slug}` | Loads one course with modules/lessons/problems; also loads lesson concept links for concept-slug summaries; computes progress | `courses`, `course_modules`, `lessons`, `problems`, `course_domain_links`, `knowledge_domains`, `lesson_concept_links`, `knowledge_concepts` |
| Mark a pathway as recently opened | Pathway detail/chapter reader | None | Browser utility records recent route activity in local browser storage | None; browser `localStorage` |
| Open hierarchical lesson/chapter | `/chapter/:courseSlug/:moduleSlug/:lessonSlug`, `/learning-paths/:courseSlug/:moduleSlug/:lessonSlug` | `GET /api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}` | Finds lesson by course/module/lesson slug; eager-loads editorial and practice data; returns reader DTO | `courses`, `course_modules`, `lessons`, `problems`, `lesson_resources`, `lesson_code_comparisons`, `lesson_diagrams`, `lesson_notes`, `lesson_concept_links`, `knowledge_concepts`, `lesson_relations` |
| Open legacy chapter by one slug | `/chapter/:slug`, `/learning` | `GET /api/chapters/{slug}` | `BuildChapterDetailResponse` resolves a simple/composite slug, adds sibling/previous/next chapters, concepts, related lessons, editorial enrichments, and notes | Same lesson-reader tables as above; may also read `concept_next_lessons` and other Atlas bridge tables depending on response-building branch |
| Navigate within chapter TOC | Chapter reader `#...` links | None | Prevents default anchor navigation and calls `scrollIntoView`; ScrollSpy updates active section in React | None |
| Render concept checks | Rich chapter reader | None | Questions and answers come from frontend `lessonInteractions.js`; selection/result state is local | None |
| Render practice questions | Rich chapter reader | None | Questions and answer state are local to `PracticeQuestions` | None |
| Load exercise starter workspace | Rich Java chapter reader | `GET /api/exercises/{exerciseId}` | Reads trusted `exercise.json` manifest and editable files under the exercise `starter/` directory; returns normalized metadata/evidence | None; repository filesystem under `exercises/` |
| View reference solution | Expanded exercise | `GET /api/exercises/{exerciseId}/solution` | Reads solution files from the trusted exercise `solution/` directory; returns read-only files | None; repository filesystem under `exercises/` |
| Run edited exercise | Expanded exercise, Run button or Ctrl+Enter | `POST /api/exercises/{exerciseId}/run` | Validates submitted editable files; builds isolated temp workspace; runs trusted Docker/Maven runner; parses Surefire output; classifies success/test failure/compilation failure/timeout; cleans workspace | None; `exercises/`, temp workspace, Docker runner |
| Legacy exercise check | Older exercise clients | `POST /api/exercises/{exerciseId}/check` | Same execution path as run, retained for older clients | None; filesystem/temp/Docker |
| Open chapter note form | Chapter reader `+ Note` | None until Save Note | Toggles local form state | None until submit |
| Save a personal/field note | Chapter reader Save Note | `POST /api/lessons/{id}/notes` | Verifies lesson exists and title/content are present; computes next order index; inserts note; returns created note DTO | `lesson_notes`; FK to `lessons` |
| Render local fallback after note failure | Chapter reader Save Note error path | Same POST, failed | Frontend adds a timestamp-based local note labelled `(Local)` even if the API write failed | None for fallback; only React state |
| Load modern reading map | `/reading-map` | `GET /api/v2/reading-map` | `ReadingMapService` loads map items, knowledge threads/steps/concepts, and recent learning activities; computes queue statistics and returns grouped item/activity DTOs | `reading_map_items`, `knowledge_threads`, `knowledge_thread_steps`, `knowledge_concepts`, `learning_activity`, optionally `lessons` |
| Filter reading queue | `/reading-map` filter pills | None | Filters loaded `readingData.items` by category in React | None |
| Toggle reading-map item (backend capability) | No visible control in current `ReadingMap.jsx` | `PATCH /api/reading-map/items/{id}/toggle` | Legacy endpoint flips `IsCompleted`, updates timestamp, returns item DTO | `reading_map_items` |
| Create reading-map item (backend capability) | No visible current control | `POST /api/reading-map/items` | Validates category/title, assigns next category order, inserts item | `reading_map_items` |
| Load legacy reading map contract | Legacy clients | `GET /api/reading-map` | Loads legacy item/activity/thread DTOs grouped into `ReadThisWeek`, `Revisited`, `Deferred`, `Lists`, and `Prerequisites` | `reading_map_items`, `reading_activity_logs`, `knowledge_threads` |
| Load knowledge atlas | `Home.jsx` component; no current `<Route>` in `App.jsx` | `GET /api/v2/knowledge-atlas` | `AtlasQueryService` loads domains, concepts, prerequisites, concept relations, next lessons, and domain-concept connections; maps graph DTO | `knowledge_domains`, `knowledge_concepts`, `domain_concept_connections`, `concept_prerequisites`, `concept_relations`, `concept_next_lessons`, `lessons` |
| Load legacy knowledge atlas | Legacy clients | `GET /api/knowledge-atlas` | Similar Atlas read through the older inline endpoint implementation | Same Knowledge Atlas tables |
| Visit author profile | `/profile` | None | Renders static profile/certification/pillar content | None |
| Follow GitHub link | `/profile` → external link | External navigation to `https://github.com` | No Neuralascent backend involvement | None |
| Load lab project path | `/lab-projects` | First `GET /api/v2/learning-paths/lab-projects`; on 404 `GET /api/v2/learning-paths`, optionally detail lookup for `labs` | Looks for a canonical learning path with modules; renders empty state if none; development fixtures are local-only | `courses`, `course_modules`, `lessons`, `problems`, plus domain/link tables if populated |
| Change importer template | `/curriculum-import` | None | Replaces local domain/module/title/concept/Markdown state with one of three frontend templates | None |
| Load Markdown file into importer | `/curriculum-import` | None | Browser `FileReader` validates `.md`/`.markdown`, reads text, updates preview/title locally | None; selected file is not uploaded by the explored action |
| Edit importer preview/metadata | `/curriculum-import` | None until Import | Parses headings/code blocks and updates live preview; add/remove concept chips locally | None |
| Import canonical curriculum chapter | `/curriculum-import` Import | `POST /api/v2/curriculum/import` | `CurriculumImportService` validates explicit course/module/title/content; transactionally creates or updates a lesson; links known concepts; persists lesson relations; records idempotent `ChapterImported` activity | `courses` (must already exist), `course_modules` (must already exist), `lessons`, `lesson_concept_links`, `knowledge_concepts`, `lesson_relations`, `learning_activity` |
| Legacy curriculum ingestion | Redirect aliases `/map-chapter`, `/add-vertical`, `/ingest`; old modal component | `POST /api/verticals/ingest` | Parses Markdown into legacy tasks; creates or replaces a vertical’s tasks | `Verticals`/`study_verticals` model table, `Tasks`/`study_tasks` model table |
| Load legacy vertical | `/vertical/:id` | `GET /api/verticals` (component selects requested id) | Loads all verticals with tasks; compatibility page selects one and decides Java/modular/flat rendering | `Verticals`, `Tasks` |
| Load Java legacy practice workspace | Inside `/vertical/:id` when selected vertical is Java/Spring/LLD | `GET /api/courses/java-spring-lld`, then `GET /api/lessons/{id}` when a lesson is selected | Loads hierarchical Java course/lesson/problem/resource DTOs for the older dashboard | `courses`, `course_modules`, `lessons`, `problems`, `lesson_resources` |
| Toggle legacy Java problem progress | Legacy Java dashboard | `PATCH /api/problems/{id}/progress` | Older endpoint flips problem completion directly; the newer V2 service provides atomic/idempotent synchronization but is not used by this fetch-based component | `problems` (legacy endpoint); `learning_activity` is not added by this inline legacy handler |
| Toggle legacy task progress | Non-Java `/vertical/:id` task rows | `PUT /api/tasks/{id}/toggle` | Reads task, calls `ProgressService.SetTaskCompletionAsync`; updates task and, for verified mapping, canonical lesson/problem; records activity transactionally | `Tasks`, `study_task_content_links`, optionally `lessons`, `problems`, `learning_activity` |
| Set canonical lesson progress | Backend/V2 capability; no visible control on current pathway/reader pages | `POST /api/v2/progress/lesson` | Atomic explicit completion update; synchronizes only verified legacy task links; writes idempotent `LessonCompleted`/`LessonReopened` activity | `lessons`, `study_task_content_links`, `Tasks`, `learning_activity` |
| Set canonical problem progress | Backend/V2 capability | `POST /api/v2/progress/problem` | Atomic explicit problem completion update; synchronizes verified legacy task links; records activity | `problems`, `study_task_content_links`, `Tasks`, `learning_activity` |
| Set canonical task progress | Backend/V2 capability | `POST /api/v2/progress/task` | Atomic explicit legacy task update; synchronizes verified lesson/problem mapping; records activity | `Tasks`, `study_task_content_links`, `lessons`, `problems`, `learning_activity` |

## 5. Endpoint inventory by responsibility

### Health and service root

| Method | Endpoint | Purpose | Tables |
|---|---|---|---|
| GET | `/` | API identity string | None |
| GET | `/health/live` | Liveness | None |
| GET | `/health/ready` | Database readiness | Database connectivity check |
| GET | `/health` | Combined health/readiness behavior | Database connectivity/check |

### Legacy vertical/task/curriculum

| Method | Endpoint | Purpose | Tables |
|---|---|---|---|
| GET | `/api/verticals` | All verticals with tasks | `Verticals`, `Tasks` |
| GET | `/api/verticals/{id}` | One vertical with tasks | `Verticals`, `Tasks` |
| POST | `/api/verticals` | Create vertical | `Verticals` |
| POST | `/api/verticals/ingest` | Parse Markdown into a vertical/task set | `Verticals`, `Tasks` |
| PUT | `/api/tasks/{id}/toggle` | Toggle legacy task and invoke progress synchronization | `Tasks`, bridge/mapped canonical rows, `learning_activity` |
| GET | `/api/courses` | All courses with nested modules/lessons/problems and progress | `courses`, `course_modules`, `lessons`, `problems` |
| GET | `/api/courses/{slugOrId}` | One course by slug or numeric id | Same course hierarchy |
| GET | `/api/lessons/{id}` | Legacy lesson detail | `lessons`, `course_modules`, `courses`, `problems`, `lesson_resources` |
| POST | `/api/lessons` | Create a lesson under an existing module | `lessons`, `course_modules` |
| PUT | `/api/lessons/{id}` | Update lesson metadata/content/completion | `lessons` |
| PATCH | `/api/lessons/{id}/progress` | Inline toggle lesson completion | `lessons` |
| GET | `/api/problems/{id}` | One problem | `problems` |
| POST | `/api/problems` | Create problem under existing lesson | `problems`, `lessons` |
| PATCH | `/api/problems/{id}/progress` | Inline toggle problem completion | `problems` |

### Knowledge, reading, and chapters

| Method | Endpoint | Purpose | Tables |
|---|---|---|---|
| GET | `/api/knowledge-atlas` | Legacy Atlas graph DTO | Atlas tables |
| GET | `/api/reading-map` | Legacy reading-map DTO | `reading_map_items`, `reading_activity_logs`, `knowledge_threads` |
| PATCH | `/api/reading-map/items/{id}/toggle` | Legacy item completion toggle | `reading_map_items` |
| POST | `/api/reading-map/items` | Create reading item | `reading_map_items` |
| GET | `/api/chapters` | Full chapter hierarchy with filters `vertical`, `course`, `module` | Course hierarchy plus lesson enrichment tables |
| GET | `/api/chapters/{slug}` | Simple/composite chapter lookup | Lesson hierarchy/enrichment/relations |
| GET | `/api/chapters/{verticalOrCourseSlug}/{moduleSlug}/{lessonSlug}` | Hierarchical legacy chapter lookup | Lesson hierarchy/enrichment/relations |
| POST | `/api/chapters/{id}/notes` | Create chapter note | `lesson_notes`, `lessons` |
| POST | `/api/chapters/map` | Older map/import endpoint that can find/create course/module/lesson | `courses`, `course_modules`, `lessons` |

### Canonical V2

| Method | Endpoint | Purpose | Tables |
|---|---|---|---|
| GET | `/api/v2/learning-paths` | Learning-path index | Course/domain/module/lesson/problem tables |
| GET | `/api/v2/learning-paths/{slug}` | Learning-path detail | Course/domain/module/lesson/problem/concept tables |
| GET | `/api/v2/knowledge-atlas` | Atlas graph | Atlas tables |
| GET | `/api/v2/reading-map` | Reading map, threads, recent activity | Reading/thread/activity tables |
| GET | `/api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}` | Canonical chapter reader | Lesson hierarchy/enrichment/concept/relation tables |
| POST | `/api/v2/progress/lesson` | Explicit lesson completion update | `lessons`, verified bridge links, `learning_activity` |
| POST | `/api/v2/progress/problem` | Explicit problem completion update | `problems`, verified bridge links, `learning_activity` |
| POST | `/api/v2/progress/task` | Explicit task completion update | `Tasks`, verified bridge links, canonical rows, `learning_activity` |
| POST | `/api/v2/curriculum/import` | Transactional canonical chapter import | Curriculum, concept-link, relation, activity tables |

### Exercises

| Method | Endpoint | Purpose | Storage |
|---|---|---|---|
| GET | `/api/exercises/{exerciseId}` | Trusted metadata and starter files | Repository filesystem |
| GET | `/api/exercises/{exerciseId}/solution` | Trusted reference solution | Repository filesystem |
| POST | `/api/exercises/{exerciseId}/run` | Execute learner files | Repository filesystem, temp workspace, Docker |
| POST | `/api/exercises/{exerciseId}/check` | Compatibility alias for execution | Repository filesystem, temp workspace, Docker |

## 6. Database table inventory

The table names below follow the current EF Core model/migrations. Some older SQL scripts use different quoted names; those differences must be resolved against the actual deployed PostgreSQL schema before a Java migration.

| Table | Role | Important relationships/notes |
|---|---|---|
| `Verticals` / legacy `study_verticals` | Legacy learning verticals | Has many `Tasks`; self-reference for canonical/alias verticals in the current EF model. |
| `Tasks` / legacy `study_tasks` | Legacy checklist tasks | Belongs to a vertical; may map to one canonical lesson/problem through `study_task_content_links`. |
| `courses` | Canonical learning paths | Slug, title, description, path type, publication state; optional link to a legacy vertical. |
| `course_modules` | Ordered modules in a course | Unique by `(course_id, slug)`; cascades from course. |
| `lessons` | Canonical chapter/lesson content and progress | Unique by `(module_id, slug)`; owns problems/resources/enrichments/relations. |
| `problems` | Practice/problem definitions and completion | Belongs to lesson; can map back to legacy tasks. |
| `lesson_resources` | Further-reading/resource content | Belongs to lesson and is ordered. |
| `knowledge_domains` | Top-level Atlas domains | Linked to concepts and courses. |
| `knowledge_concepts` | Atlas concept nodes | Linked to domains, prerequisites, relations, next lessons, lesson links, and thread steps. |
| `domain_concept_connections` | Domain-to-concept edges | Stores primary flag, relevance weight, role, and order. |
| `concept_prerequisites` | Concept prerequisite edges | Two concept FKs; unique concept/prerequisite pair. |
| `concept_relations` | Concept-to-concept relation edges | Source/target concept IDs and relationship type. |
| `concept_next_lessons` | Concept-to-next-lesson recommendations | Can point to a lesson but preserves title/module/slug text. |
| `reading_map_items` | Curated reading queue | Category/status/order/completion; optional lesson/task links; scheduled date and priority in current model. |
| `reading_activity_logs` | Older daily activity chart data | Used by legacy reading-map endpoint; separate from newer `learning_activity`. |
| `knowledge_threads` | Human-readable cross-domain paths | Domain and raw path; owns ordered thread steps. |
| `knowledge_thread_steps` | Normalized thread steps | Optional concept/lesson links; composite key `(thread_id, order_index)`. |
| `lesson_code_comparisons` | Before/after code examples | Belongs to lesson; stores labels, languages, code, explanation. |
| `lesson_diagrams` | Inline lesson diagrams | Belongs to lesson; stores SVG and optional diagram spec JSON. |
| `lesson_notes` | Chapter notes/marginalia | Belongs to lesson; note type, optional anchor section, content, order. Current note endpoint inserts here. |
| `course_domain_links` | Course-to-Atlas-domain bridge | Composite key `(course_id, domain_id)` and primary/order metadata. |
| `lesson_concept_links` | Lesson-to-Atlas-concept bridge | Composite key `(lesson_id, concept_id, relationship_type)`. |
| `lesson_relations` | Lesson-to-lesson or unresolved relation records | May hold target lesson FK or unresolved target title/slug. |
| `study_task_content_links` | Legacy-to-canonical mapping | Exactly one canonical lesson or problem target; mapping status/confidence/checksum. |
| `learning_activity` | New activity/event journal | Lesson/problem/task/reading item optional FKs; correlation ID supports idempotency; metadata is JSONB. |
| `migration_reconciliation` | Import/reconciliation audit state | Source/target identity, checksum, status, issue code, JSONB details. |

### 6.1 Progress synchronization invariant

The newer `ProgressService` is deliberately more than a boolean flip:

1. It opens a database transaction.
2. It updates the requested lesson, problem, or task.
3. It synchronizes mapped legacy/canonical records only when the bridge mapping is `Verified`.
4. It inserts a corresponding activity event only if the `(correlation_id, event_type)` pair does not already exist.
5. It commits as one unit.

This is the behavioral contract to preserve during migration. The older inline `PATCH /api/lessons/{id}/progress` and `PATCH /api/problems/{id}/progress` handlers do not use this full synchronization path; they directly toggle the requested row.

### 6.2 Schema source-of-truth warning

`api/Data/schema.sql` is useful as an early relational sketch, but it is not a complete representation of the current model. For example, the current EF context includes `difficulty`, `content_status`, lesson enrichments, bridge tables, learning activity, thread steps, and reconciliation records. Use the current migrations plus `StudyTrackerContext.OnModelCreating` to reconstruct the deployed schema, then compare with `information_schema` in the target database.

## 7. Frontend/backend boundary observations

### 7.1 Modern pages are mostly read-only

The current pathway index, pathway detail, chapter reader, reading-map filters, profile, and empty lab page are primarily read surfaces. The main current visible writes are:

- chapter note creation;
- code-exercise execution against a filesystem/Docker runner;
- curriculum import, which is an admin/content write but was not submitted during exploration.

The V2 progress APIs exist, but no visible completion button was found on the modern pathway detail or chapter reader pages during this pass.

### 7.2 There are two curriculum UX generations

The modern experience uses canonical V2 learning paths and hierarchical chapter URLs. The older `/vertical/:id` experience uses legacy vertical/task APIs and a separate Java practice dashboard. Both remain compiled, and bridge tables/services exist to synchronize them.

### 7.3 Importer contract mismatch to verify

The frontend importer derives `courseSlug` from the selected Domain value. The default selected Domain is `Neuralascent`, producing `neuralascent` after slugification, while `CurriculumImportService` requires the destination course and module to already exist and rejects missing destinations. The frontend default therefore appears likely to fail unless a course with that exact slug exists in the deployed database or another runtime layer transforms the payload. This was not tested by submitting the form because it would mutate curriculum data.

### 7.4 Note fallback can hide persistence failure

`ChapterReader` catches any note-save error and immediately adds a local note to React state. A user can therefore see a note after a failed POST, but a reload will remove it. This should be treated as an existing UX behavior and a data-observability concern.

### 7.5 Exercise data is not relational curriculum data

Exercise metadata, starter files, trusted tests, and solutions live under `exercises/` and are loaded by the backend repository. Exercise execution uses a temporary workspace and Docker. The lesson-to-exercise association is frontend data in `lessonExerciseAssociations.js`; an exercise run does not write a learning-progress row in the current service.

### 7.6 Knowledge Atlas homepage is currently orphaned by routing

`Home.jsx` fetches the Knowledge Atlas and learning-path index and links to Reading Map, Lab Projects, and Curriculum Import. However, `App.jsx` redirects `/` to `/chapters` and contains no route rendering `Home`. The Atlas fetch is therefore source-backed but not reachable through the current route table unless another build/runtime route exists outside this repository.

## 8. Security and operational observations

- The API has correlation-ID middleware: it accepts `x-correlation-id`, uses it as the request trace identifier, and returns it in the response header.
- The API has centralized problem-details handling for unhandled exceptions and exercise-specific problem responses.
- The API-key middleware exempts health, Swagger, and OPTIONS requests; other requests require `x-api-key` when configured.
- The UI copy calls curriculum import “IAM Protected”, but the checked-in endpoint implementation is shared API-key middleware, not per-user IAM/role enforcement. Treat the UI copy as an intention, not proof of an implemented identity boundary.
- There is no user identity/ownership field in the visible curriculum/progress model. Completion, notes, and reading-map state appear global to the database in the current design.
- Exercise execution is protected by validation, path-safety checks, a concurrency semaphore, file/output/time limits, and workspace cleanup. These controls are part of the current backend behavior even though the feature has no database table.

## 9. Phase 0 conclusions

The smallest meaningful current-system slice is:

```text
/chapters
  -> GET /api/v2/learning-paths
  -> /chapters/{courseSlug}
  -> GET /api/v2/learning-paths/{courseSlug}
  -> click lesson
  -> GET /api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}
  -> render lesson content and enrichments
```

The first state-changing slice to preserve is:

```text
chapter reader + Note
  -> POST /api/lessons/{lessonId}/notes
  -> lesson_notes row
```

The first progress slice to preserve is not the old boolean toggle; it is the newer transactional `ProgressService` contract with verified bridge synchronization and idempotent `learning_activity` events.

## 10. Follow-up evidence needed before implementation

1. Capture one real browser Network-panel export or local DevTools trace for the lesson-open request, including status, response headers, and timing.
2. Enable ASP.NET/EF Core SQL logging for the same request and record the actual SQL/query count.
3. Query PostgreSQL `information_schema.tables` and the migration history table to resolve `Verticals`/`Tasks` versus `study_verticals`/`study_tasks` naming in the deployed database.
4. Verify whether the deployed frontend receives an API key through a reverse proxy or whether the production API-key middleware is currently disabled/unconfigured.
5. Verify whether the V2 progress endpoints are reachable from any current UI or are backend-only migration capabilities.
6. Verify the importer’s default generated `courseSlug`/`moduleSlug` against actual course/module rows without submitting a content mutation.
7. Decide whether global progress/notes are intentional or whether user ownership must be added before multi-user or AI features are introduced.

