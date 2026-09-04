# NeuralAscent Current-System Map

**Purpose:** Phase 0 reference for the Java-first rebuild.

**Observed on:** 2026-09-01

**Principle:** The existing application is a behavioral reference. The Java implementation should reproduce important behavior through explicit contracts, not copy C# files line by line.

## 1. Current system at a glance

| Layer | Current implementation | Java-first target |
|---|---|---|
| Browser | React + Vite | Keep the existing React UI initially |
| API | ASP.NET Core minimal APIs in `api/Program.cs` and endpoint modules | Spring Boot REST API |
| Persistence | Entity Framework Core + Npgsql | Spring Data JPA or deliberate SQL access |
| Database | PostgreSQL | Retain PostgreSQL and migrate schema deliberately |
| Exercise execution | Docker-based Java runner | Port behavior after the core curriculum/progress flow is understood |
| Content tooling | Seeders, importer, reconcilers | Migrate after runtime parity |
| AI | Not part of the current runtime surface | Add provider-neutral gateway before tutor/RAG |

## 2. Browser entry points

Defined in `app/src/App.jsx`:

| User-facing area | Routes |
|---|---|
| Curriculum index | `/chapters` |
| Learning path | `/chapters/:slug`, `/learning-paths/:slug` |
| Chapter/lesson reader | `/chapter/:slug`, `/chapter/:verticalOrCourseSlug/:moduleSlug/:lessonSlug`, `/learning`, `/learning-paths/:courseSlug/:moduleSlug/:lessonSlug` |
| Profile | `/profile`, `/certifications` redirects to `/profile` |
| Legacy vertical view | `/vertical/:id` |
| Lab projects | `/lab-projects` |
| Reading map/progress | `/reading-map`, `/progress` redirects to `/reading-map` |
| Curriculum administration | `/curriculum-import`, `/map-chapter`, `/add-vertical`, `/ingest` |

The browser API client centralizes requests in `app/src/api/client.js`. It adds a correlation ID and parses RFC 7807-style problem responses. The base URL comes from `VITE_API_URL` or `VITE_API_BASE_URL`; otherwise requests are relative and rely on the frontend proxy.

## 3. Current request flow

```text
React route/component
    -> api client or direct fetch
    -> frontend proxy / API base URL
    -> ASP.NET Core middleware
       correlation ID, error handling, CORS, shared x-api-key check
    -> minimal API endpoint
    -> service where the endpoint uses one
    -> EF Core StudyTrackerContext
    -> PostgreSQL
    -> JSON/problem response
    -> React state and rendered UI
```

Important current security boundary: the API uses a shared `x-api-key` middleware and does not yet have per-user identity, sessions, ownership, or role-based authorization. This is a migration gap, not a design to carry forward into the multi-user Java platform.

## 4. API contract inventory

### Health and root

- `GET /`
- `GET /health`
- `GET /health/live`
- `GET /health/ready`

### Legacy vertical/task/curriculum APIs

- `GET /api/verticals`
- `GET /api/verticals/{id}`
- `POST /api/verticals`
- `POST /api/verticals/ingest`
- `PUT /api/tasks/{id}/toggle`
- `GET /api/courses`
- `GET /api/courses/{slugOrId}`
- `GET /api/lessons/{id}`
- `POST /api/lessons`
- `PUT /api/lessons/{id}`
- `PATCH /api/lessons/{id}/progress`
- `GET /api/problems/{id}`
- `POST /api/problems`
- `PATCH /api/problems/{id}/progress`

### Knowledge, reading, and chapter APIs

- `GET /api/knowledge-atlas`
- `GET /api/reading-map`
- `PATCH /api/reading-map/items/{id}/toggle`
- `POST /api/reading-map/items`
- `GET /api/chapters`
- `GET /api/chapters/{slug}`
- `GET /api/chapters/{verticalOrCourseSlug}/{moduleSlug}/{lessonSlug}`
- `POST /api/chapters/{id}/notes`
- `POST /api/chapters/map`

### V2 APIs

- `GET /api/v2/learning-paths`
- `GET /api/v2/learning-paths/{slug}`
- `GET /api/v2/knowledge-atlas`
- `GET /api/v2/reading-map`
- `GET /api/v2/chapters/{courseSlug}/{moduleSlug}/{lessonSlug}`
- `POST /api/v2/progress/lesson`
- `POST /api/v2/progress/problem`
- `POST /api/v2/progress/task`
- `POST /api/v2/curriculum/import`

### Exercise APIs

- `GET /api/exercises/{exerciseId}` for exercise metadata
- `GET /api/exercises/{exerciseId}/solution`
- `POST /api/exercises/{exerciseId}/run`
- `POST /api/exercises/{exerciseId}/check`

Exercise submissions contain files and an optional `clientRequestId`. The backend validates the submission, builds an isolated workspace, invokes the Docker runner, parses Surefire output, classifies the result, and returns a normalized execution result.

## 5. Current domain/data areas

`StudyTrackerContext` currently exposes these groups:

- **Legacy tracker:** `StudyVertical`, `StudyTask`
- **Curriculum:** `Course`, `CourseModule`, `Lesson`, `Problem`, `LessonResource`
- **Knowledge Atlas:** domains, concepts, prerequisites, relations, next lessons, threads, and steps
- **Reading/progress:** reading-map items, activity logs, learning activities
- **Lesson enrichment:** diagrams, notes, code comparisons
- **Bridge/migration:** course-domain links, lesson-concept links, lesson relations, task-content links, migration reconciliation records

The schema already has meaningful relationships and constraints. The Java rebuild should initially model only the smallest slice needed for the current phase, then expand one entity/relationship at a time.

## 6. Existing backend responsibilities

| Responsibility | Current location |
|---|---|
| Database configuration and startup readiness | `api/Program.cs` |
| Curriculum and learning-path queries | `api/Services/LearningPathQueryService.cs` |
| Progress updates and activity records | `api/Services/ProgressService.cs` |
| Knowledge Atlas reads | `api/Services/AtlasQueryService.cs` |
| Reading map | `api/Services/ReadingMapService.cs` |
| Curriculum import | `api/Services/CurriculumImportService.cs` |
| Exercise metadata/solution/submission flow | `api/Services/Exercises/` |
| Docker execution | `api/Services/Exercises/LocalDockerExerciseRunner.cs` |
| Java/FDE/Azure/Atlas reconciliation | `api/Services/Reconciliation/` |

## 7. First Java slice

The first implementation should not attempt to port the whole schema. It should prove this path:

```text
React page
    -> GET /api/hello
    -> Spring Boot controller
    -> small service
    -> JSON response
```

Then add persistence:

```text
GET /api/lessons
    -> controller
    -> lesson service
    -> lesson repository
    -> PostgreSQL lesson table
```

The first Java slice is complete only when the flow can be explained, changed manually, tested, and debugged without blindly regenerating the implementation.

## 8. Migration rules

1. Freeze behavior before changing implementation.
2. For each endpoint record inputs, output shape, status codes, errors, and database side effects.
3. Keep the existing .NET API available as the comparison implementation.
4. Preserve PostgreSQL data and identifiers where practical; do not redesign the whole schema during the first slice.
5. Introduce one primary new difficulty at a time.
6. Add tests before declaring behavioral parity.
7. Add authentication and ownership before exposing user-specific or paid AI features.
8. Add the AI gateway before adding a tutor endpoint; add RAG only after current-context tutoring is reliable.

## 9. Phase 0 completion checklist

- [x] Current frontend routes identified.
- [x] Current API endpoint groups identified.
- [x] Current persistence and service boundaries identified.
- [x] Current shared-key security limitation recorded.
- [ ] Create the first Java/Spring project.
- [ ] Freeze the first endpoint contract.
- [ ] Verify a Java `/api/hello` vertical slice.
- [ ] Add a small Java lesson table and repository test.

