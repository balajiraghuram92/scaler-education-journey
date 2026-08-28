# Neuralascent Interactive Java Exercise Platform

## Architecture, Engineering Decisions, Implementation Retrospective, and Java Reimplementation Blueprint

**Purpose:** A detailed engineering handoff and learning blueprint for
rebuilding the completed Neuralascent lesson-embedded Java exercise
capability as a company-style Java/Spring project.

**Scope:** Product intent, responsive lesson UI, multi-file exercise
model, Run pipeline, reference-solution reveal, trusted package
contract, Docker isolation, ARM64 deployment, CI lessons, persistence
design, class/sequence/ER diagrams, and a staged Java reimplementation
plan.

------------------------------------------------------------------------

# 1. Why this system was built

Neuralascent is primarily a structured engineering-learning portal, not
a generic browser IDE. The objective was to move lessons from passive
reading to an active loop:

1.  read a concept;
2.  understand a practical scenario;
3.  answer conceptual checks;
4.  open an exercise inside the lesson;
5.  edit one or more Java files;
6.  run the code against trusted tests;
7.  inspect compiler/test evidence;
8.  optionally reveal a trusted reference solution;
9.  continue the lesson without leaving its context.

This product distinction drove the architecture. A generic online IDE
tends to expose arbitrary projects, terminals, dependencies, build
commands, and runtime configuration. Neuralascent deliberately owns the
exercise definition, tests, Maven configuration, runner image, limits,
and evidence model. The learner controls only explicitly editable source
files.

The implementation began with Java LLD/OOP content and the multi-file
`Point` / `ThreedPoint` polymorphism exercise. Supporting multiple files
from the first real exercise prevented the system from becoming a
one-file demo.

------------------------------------------------------------------------

# 2. Core architecture decisions

The design converged on these principles:

-   **Lesson embedded:** exercises belong in the shared ChapterReader
    rather than a separate IDE product.
-   **Compact first:** lesson prose remains primary; the coding
    workspace expands when requested.
-   **Multi-file first:** metadata, editor state, API requests,
    workspace construction, and solutions all use file collections.
-   **Trusted infrastructure / untrusted learner source:** the browser
    cannot control tests, POM, Docker image, Docker command, resource
    policy, Docker socket, or secrets.
-   **Disposable execution:** each Run uses a fresh temporary workspace
    and disposable container.
-   **Git/filesystem exercise source of truth:** `exercise.json`,
    starter files, tests, solution, and trusted POM are versioned with
    the repository.
-   **Same EC2 execution initially:** appropriate for a small personal
    system and avoids premature distributed infrastructure.
-   **Execution and answer reveal are separate:** Run evaluates learner
    code; View Solution reveals trusted reference code.
-   **Immutable production artifacts:** runner/API/frontend images are
    deployed through GHCR, with the Java runner referenced by digest.
-   **Preserve the existing database:** the exercise feature and
    deployment redesign must not replace the known-good PostgreSQL data
    volume or connection semantics.

------------------------------------------------------------------------

# 3. System context

``` text
+-------------------------+
| Browser / React UI      |
| ChapterReader           |
| ImplementationExercise  |
+------------+------------+
             |
             | HTTPS / JSON
             v
+-------------------------+
| StudyTracker API        |
| Current: ASP.NET Core   |
| Future: Java/Spring     |
+-----+---------------+---+
      |               |
      v               v
+-----------+   +-----------------------+
|PostgreSQL |   | Exercise package      |
|portal data|   | Git/filesystem        |
+-----------+   +-----------+-----------+
                            |
                            v
                    +------------------+
                    | Execution service|
                    | Docker adapter   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Disposable Java  |
                    | Maven/JDK runner |
                    +------------------+
```

The most important trust boundary is between the API/orchestrator and
the disposable learner-code container.

------------------------------------------------------------------------

# 4. Canonical exercise package

Representative package:

``` text
exercises/java/java-lld/oop-3/point-threedpoint/
├── exercise.json
├── pom.xml
├── starter/
│   └── src/main/java/
│       ├── Point.java
│       └── ThreedPoint.java
├── solution/
│   └── src/main/java/
│       ├── Point.java
│       └── ThreedPoint.java
└── tests/
    └── src/test/java/
        └── ThreedPointTest.java
```

The package has four trust categories:

-   `exercise.json`: trusted manifest and product contract;
-   `starter/`: learner-visible starting code;
-   `tests/`: trusted server-owned behavioral tests;
-   `solution/`: trusted golden/reference implementation;
-   `pom.xml`: trusted build configuration.

The manifest describes identity, lesson association, language,
difficulty, estimated time, editable file definitions, display order,
and evidence definitions. The platform must never hardcode `Point.java`
or `ThreedPoint.java` into generic UI/backend logic. The manifest is
what turns the feature into an exercise engine.

A conceptual manifest is:

``` json
{
  "id": "java-lld-oop3-point-threedpoint",
  "lessonSlug": "04-oop-3-polymorphism-interfaces",
  "title": "Point & ThreedPoint — Method Overriding",
  "language": "java",
  "files": [
    {"id":"point","path":"src/main/java/Point.java","displayName":"Point.java","editable":true},
    {"id":"threed-point","path":"src/main/java/ThreedPoint.java","displayName":"ThreedPoint.java","editable":true}
  ],
  "evidence": ["...trusted pedagogical evidence definitions..."]
}
```

The same file definitions drive starter loading, submission validation,
workspace writing, solution loading, and frontend tab ordering.

------------------------------------------------------------------------

# 5. Responsive ChapterReader redesign

The old shared reader had a shell around `1380px`, a fixed center
chamber around `760px`, fixed side rails, and large gaps. That was
acceptable for prose but wasted space for a code editor.

The key architectural realization was that **prose width and interaction
width are different constraints**.

The global fix therefore:

-   made the shared shell fluid up to roughly `1880px`;
-   made gutters and column gaps responsive;
-   made TOC/context rails flexible;
-   removed the old fixed center-chamber maximum;
-   retained an approximately `70ch` prose measure for readability;
-   allowed interactive components such as coding exercises to use
    substantially more width;
-   moved the context rail below the main content at medium widths;
-   used a single-column mobile layout;
-   removed expanded-exercise negative-margin hacks.

Desktop is conceptually:

``` text
+-----------+--------------------------------+-----------+
| TOC       | Main lesson + interactions     | Context   |
+-----------+--------------------------------+-----------+
```

Medium:

``` text
+-----------+--------------------------------+
| TOC       | Main lesson                    |
+-----------+--------------------------------+
            | Context below                  |
            +--------------------------------+
```

Mobile becomes one column.

Because the defect came from the shared shell, the correction was made
in shared `ChapterReader` architecture rather than adding a
Lesson-4-specific CSS patch. This is an important engineering rule:
**fix shared architectural causes at the shared boundary.**

------------------------------------------------------------------------

# 6. Frontend state architecture

`ImplementationExercise` conceptually owns independent state machines:

``` text
Metadata:
idle -> loading -> loaded | error

Learner workspace:
workingFiles[]
activeStudentFileId

Execution:
idle -> running -> completed | infrastructure-error

Reference solution:
not-requested -> loading -> loaded | error
isSolutionVisible
activeReferenceFileId
```

The critical invariant is:

> `workingFiles` and `solution.files` are separate state.

Opening a solution must never overwrite learner edits, become the Run
payload, reset the student tab, or mutate the starter workspace.

This separation was explicitly tested.

------------------------------------------------------------------------

# 7. Run semantics and request flow

`Run` means: **evaluate the learner's current source snapshot**.

Conceptual request:

``` http
POST /api/exercises/{exerciseId}/run

{
  "files": [
    {"path":"src/main/java/Point.java","content":"..."},
    {"path":"src/main/java/ThreedPoint.java","content":"..."}
  ]
}
```

The frontend snapshots current working files before execution. Run does
not reveal the solution and does not allow the browser to submit tests
or Maven configuration.

Detailed flow:

``` text
Browser workingFiles[]
  -> POST /run
  -> load trusted manifest
  -> validate submitted paths against editable manifest paths
  -> create fresh temporary Maven workspace
  -> copy trusted pom.xml
  -> copy trusted tests
  -> write learner source only to allowed paths
  -> create disposable Docker runner
  -> mvn test
  -> collect compiler output / Surefire results
  -> normalize ExerciseExecutionResult
  -> return Test Evidence
  -> remove container/workspace
```

Normal learner compile/test failures are domain results, not platform
500 errors.

Useful execution states are:

``` text
QUEUED
PREPARING
RUNNING
PASSED
TEST_FAILED
COMPILE_FAILED
TIMED_OUT
INFRASTRUCTURE_FAILED
CANCELLED
```

A boolean `passed` is insufficient because compiler mistakes, failed
assertions, and Docker failures require different UX and operational
treatment.

------------------------------------------------------------------------

# 8. Why Check Solution was redesigned

Initially, Run and Check Solution both effectively executed learner
code. That created two labels for one operation.

The corrected domain semantics are:

``` text
RUN
  -> execute my current implementation
  -> show compiler/test evidence

VIEW SOLUTION
  -> fetch trusted reference implementation
  -> show it read-only
  -> execute nothing
```

The backend therefore exposes:

``` http
GET /api/exercises/{exerciseId}/solution
```

Solution content is not included in initial metadata. It is lazy-loaded
only when requested.

This improves payload size, answer separation, caching semantics, and
future policy/audit possibilities.

------------------------------------------------------------------------

# 9. Final Reference Solution UX

The first solution implementation still had a UX flaw: the reveal action
was beside Run while Hide Solution appeared elsewhere. One conceptual
toggle moved physically.

The final interaction uses one persistent disclosure header.

Collapsed:

``` text
REFERENCE SOLUTION                         View solution  v
```

Expanded:

``` text
REFERENCE SOLUTION                         Hide solution  ^
-----------------------------------------------------------
Point.java | ThreedPoint.java
<read-only reference code>
```

The old checkmark was removed because a checkmark implies
validation/success rather than disclosure.

The same button remains in the same location and changes label/chevron.
It exposes `aria-expanded`, `aria-controls`, normal keyboard button
behavior, and visible text.

Data state and visibility state are intentionally different:

``` text
First View:
  GET /solution -> cache result -> show

Hide:
  hide content, keep loaded data

Second View:
  show cached solution, no duplicate request
```

The solution viewer supports one or many files and maintains its own
active reference tab.

------------------------------------------------------------------------

# 10. Solution filesystem security

A manifest-relative file reader must not blindly concatenate strings.

The solution service needs to:

-   canonicalize the trusted solution root;
-   resolve manifest paths relative to that root;
-   reject `..` traversal;
-   verify the canonical target remains inside the root;
-   use directory-aware containment rather than naïve string prefix
    checks;
-   reject intermediate symlink/reparse-point escapes;
-   reject final-file symlinks where required;
-   enforce file-size limits;
-   read expected UTF-8 content;
-   distinguish missing exercise/solution from infrastructure failures.

Example of a dangerous naïve prefix:

``` text
trusted: /app/exercises/x/solution
evil:    /app/exercises/x/solution-evil
```

A plain string `startsWith` can be wrong. Canonical root containment
must respect path boundaries.

Intentional status semantics:

``` text
unknown exercise       -> 404
missing solution/file  -> 404
unsafe/infrastructure read failure -> 503
```

------------------------------------------------------------------------

# 11. Backend responsibility decomposition

A clean design separates:

``` text
HTTP endpoint/controller
       |
       v
Application use case/service
       |
       +--> ExerciseRepository
       +--> SubmissionValidator
       +--> WorkspaceFactory
       +--> ExerciseRunner
       +--> Result/Evidence parser
```

Representative current responsibilities include metadata service,
execution service, solution service, package repository, workspace
builder, Docker runner, and evidence/result models.

Controllers/endpoints should remain thin and must not directly
manipulate Docker or filesystem internals.

------------------------------------------------------------------------

# 12. Docker execution boundary

The runner is a generic Maven/JDK image; exercise content is separate.

``` text
Runner image
  = Maven + JDK + minimal runtime

Exercise package
  = manifest + trusted POM + tests + source contract
```

The initial profile uses Maven with Java 11 and must support the ARM64
EC2 host.

The API is the trusted orchestrator and currently receives the Docker
socket:

``` text
API container:
  /var/run/docker.sock -> YES

Learner execution container:
  Docker socket -> NEVER
  AWS credentials -> NO
  PostgreSQL credentials -> NO
  API secrets -> NO
  arbitrary host mounts -> NO
```

For a small personal site, same-host Docker execution is a pragmatic
low-cost choice. For a larger public/multi-tenant service, move the
execution daemon to dedicated infrastructure behind an `ExerciseRunner`
port.

------------------------------------------------------------------------

# 13. Resource and concurrency policy

Untrusted execution must be bounded by:

-   timeout;
-   memory;
-   CPU;
-   PID/process limits;
-   controlled workspace mounts;
-   submission/file-size limits;
-   cleanup on every outcome;
-   maximum concurrency.

The initial production setting used:

``` text
ExerciseExecution__MaxConcurrentExecutions=1
```

This protects a small roughly 1 GB-class host and favors predictable
operation over throughput.

A persistent Maven cache volume:

``` text
neuralascent-maven-cache
```

reduces repeated dependency downloads while workspaces/containers remain
disposable.

------------------------------------------------------------------------

# 14. Runner image lifecycle bug and fix

A production issue exposed an operational dependency.

Deployment pulled the runner by immutable digest, then later executed:

``` bash
docker image prune -f
```

Because no persistent container references the Java runner, the
digest-pulled image could be considered dangling and removed. The
application runner intentionally expects the image to already exist and
only inspects it; it does not authenticate/pull on every learner
request.

The fix was:

``` text
pull immutable RUNNER_REF
        +
tag same image locally as <runner-image>:deployed
```

The API still executes the immutable digest. The local non-`latest` tag
merely protects the currently deployed runner from dangling-image
pruning. On the next successful deployment the tag moves to the new
image.

Lesson: **image lifecycle is part of runtime architecture when
applications dynamically launch containers.**

------------------------------------------------------------------------

# 15. Production host model

Production EC2 is a Docker runtime host, not a source development
machine.

Persistent services:

``` text
studytracker-app
studytracker-api
studytracker-postgres
```

plus ephemeral Java exercise containers.

Node, .NET, Maven, Java, and PostgreSQL development tooling do not need
to be installed directly on EC2 for normal operation. Builds/tests
belong in CI or purpose-built containers.

------------------------------------------------------------------------

# 16. PostgreSQL preservation and deployment boundary

The production database already contained real portal data. The
infrastructure redesign deliberately did not combine exercise work with
a database replacement.

Safe boundary:

``` text
deployment changes
+ secret storage changes
        |
        v
/etc/studytracker/api.env
        |
        v
existing DB connection semantics
        |
        v
existing PostgreSQL data preserved
```

Application rollback does not automatically roll back schema/data
migrations. Therefore schema migration is a separate risk domain.

For a Java rewrite, prefer explicit Flyway/Liquibase migrations and
avoid relying on incidental ORM schema generation in production.

------------------------------------------------------------------------

# 17. SSM, GHCR, and S3 operational architecture

Production secrets are materialized from SSM SecureString parameters:

``` text
/neuralascent/prod/api-env
/neuralascent/prod/ghcr-read-token
```

into root-owned files:

``` text
/etc/studytracker/api.env
/etc/studytracker/ghcr-token
```

with mode `0600`.

The EC2 GHCR credential needs read-only `read:packages`; CI credentials
may require package-write scope. Runtime should not receive unnecessary
write/delete permissions.

A low-cost S3 backup bucket/prefix was added for deployment-time
PostgreSQL backups. IAM was validated using direct list/put/get/delete
preflight operations. This is deliberately lightweight for a personal
project, while still protecting schema-changing deployments.

------------------------------------------------------------------------

# 18. CI failures and engineering lessons

Two failures were especially instructive.

## 18.1 C# compiler/name-resolution issue

New tests used `Options.Create(...)`, but `Options` resolved to the
application's `StudyTracker.Api.Options` namespace rather than
`Microsoft.Extensions.Options.Options`.

The fix fully qualified the intended class.

Lesson: static review is not compilation. Every modified test project
must actually compile.

## 18.2 Endpoint test DI drift

Production correctly registered `ExerciseSolutionService`, but a reduced
endpoint-mapping test built its own DI container and omitted it. ASP.NET
therefore inferred the service parameter as an HTTP body parameter while
materializing a GET endpoint.

The correct fix was to add the service to the test fixture, not change
the production endpoint merely to silence the test.

Lesson: whenever a new constructor/handler dependency is introduced,
trace it through:

``` text
production DI
test DI
integration host
manual ServiceCollection/application context
```

In a Spring rewrite, include at least one real application-context
wiring test so production bean wiring cannot silently diverge from
handcrafted unit fixtures.

------------------------------------------------------------------------

# 19. Testing strategy

## Exercise-package/golden tests

Prove:

1.  golden solution passes all trusted tests;
2.  starter does not falsely pass;
3.  compilation failure is classified;
4.  behavioral failure is classified;
5.  timeout is terminated;
6.  Surefire output is captured and parsed.

## Backend tests

Cover:

-   manifest loading;
-   metadata;
-   submitted-file whitelist;
-   multi-file order;
-   solution loading;
-   missing solution;
-   unknown exercise;
-   traversal;
-   symlink escape;
-   endpoint mapping;
-   DI/context startup.

## Frontend tests

Cover:

-   starter files;
-   student tab switching;
-   edit preservation;
-   immutable Run snapshot;
-   duplicate Run prevention;
-   View Solution does not Run;
-   read-only reference workspace;
-   independent reference tabs;
-   persistent disclosure;
-   `aria-expanded`/`aria-controls`;
-   first reveal fetches once;
-   hide/reopen does not refetch;
-   error/retry.

## Production smoke tests

Verify:

-   API health and DB connectivity;
-   immutable runner image exists;
-   no persistent runner container;
-   Run succeeds;
-   evidence renders;
-   View/Hide Solution works;
-   learner edits survive;
-   responsive chapter pages behave across viewport sizes.

A final browser hard refresh was required once after deployment because
cached frontend assets displayed the previous UI. That was a caching
symptom, not an application defect.

------------------------------------------------------------------------

# 20. Technology-neutral domain model

``` mermaid
classDiagram
    class Exercise {
        +ExerciseId id
        +String lessonSlug
        +String title
        +Language language
        +Difficulty difficulty
        +List~ExerciseFileDefinition~ files
        +List~EvidenceDefinition~ evidence
    }

    class ExerciseFileDefinition {
        +String id
        +RelativePath path
        +String displayName
        +boolean editable
        +int displayOrder
    }

    class ExerciseSubmission {
        +ExerciseId exerciseId
        +List~SubmittedFile~ files
    }

    class SubmittedFile {
        +RelativePath path
        +String content
    }

    class ExerciseSolution {
        +ExerciseId exerciseId
        +List~SolutionFile~ files
    }

    class ExerciseExecutionResult {
        +ExecutionStatus status
        +List~EvidenceResult~ evidence
        +String compilerOutput
        +String testOutput
        +Duration duration
    }

    Exercise "1" o-- "*" ExerciseFileDefinition
    ExerciseSubmission "1" o-- "*" SubmittedFile
    ExerciseSolution "1" o-- "*" SolutionFile
    ExerciseExecutionResult "1" o-- "*" EvidenceResult
```

The important point is responsibility, not exact class names.

------------------------------------------------------------------------

# 21. Recommended Java/Spring package architecture

``` text
com.neuralascent.exercise
├── domain
│   ├── Exercise.java
│   ├── ExerciseId.java
│   ├── ExerciseFileDefinition.java
│   ├── ExerciseSubmission.java
│   ├── SubmittedFile.java
│   ├── ExerciseSolution.java
│   ├── ExerciseExecutionResult.java
│   ├── EvidenceDefinition.java
│   └── EvidenceResult.java
│
├── application
│   ├── GetExerciseMetadataUseCase.java
│   ├── RunExerciseUseCase.java
│   ├── GetExerciseSolutionUseCase.java
│   ├── SubmissionValidator.java
│   └── ports
│       ├── ExerciseRepository.java
│       ├── ExerciseRunner.java
│       └── WorkspaceFactory.java
│
├── infrastructure
│   ├── filesystem
│   │   └── FileSystemExerciseRepository.java
│   ├── docker
│   │   └── DockerExerciseRunner.java
│   ├── maven
│   │   └── SurefireResultParser.java
│   └── persistence
│       └── ...
│
└── web
    ├── ExerciseController.java
    ├── ExerciseMetadataResponse.java
    ├── RunExerciseRequest.java
    ├── ExerciseExecutionResponse.java
    └── ExerciseSolutionResponse.java
```

This is a pragmatic ports-and-adapters shape. Domain/application code
should not depend directly on Spring MVC, Docker, filesystem paths, or
PostgreSQL.

Suggested ports:

``` java
public interface ExerciseRepository {
    Optional<Exercise> findById(ExerciseId id);
    StarterWorkspace loadStarter(ExerciseId id);
    ExerciseSolution loadSolution(ExerciseId id);
    TrustedExerciseAssets loadTrustedAssets(ExerciseId id);
}

public interface ExerciseRunner {
    ExerciseExecutionResult run(PreparedExerciseWorkspace workspace);
}

public interface WorkspaceFactory {
    PreparedExerciseWorkspace prepare(
        Exercise exercise,
        ExerciseSubmission submission,
        TrustedExerciseAssets assets
    );
}
```

------------------------------------------------------------------------

# 22. Java execution sequence

``` mermaid
sequenceDiagram
    actor Learner
    participant UI
    participant Controller
    participant UseCase as RunExerciseUseCase
    participant Repo as ExerciseRepository
    participant Workspace
    participant Runner
    participant Docker
    participant Maven

    Learner->>UI: Run
    UI->>Controller: POST /exercises/{id}/run
    Controller->>UseCase: run(id, files)
    UseCase->>Repo: find/load trusted package
    Repo-->>UseCase: exercise + trusted assets
    UseCase->>Workspace: prepare trusted workspace
    Workspace-->>UseCase: PreparedWorkspace
    UseCase->>Runner: run(workspace)
    Runner->>Docker: create disposable container
    Docker->>Maven: mvn test
    Maven-->>Docker: exit + Surefire
    Docker-->>Runner: execution artifacts
    Runner-->>UseCase: normalized result
    UseCase-->>Controller: result
    Controller-->>UI: JSON evidence
    UI-->>Learner: Test Evidence
```

Reference solution:

``` mermaid
sequenceDiagram
    actor Learner
    participant UI
    participant Controller
    participant UseCase as GetExerciseSolutionUseCase
    participant Repo

    Learner->>UI: View solution
    UI->>Controller: GET /exercises/{id}/solution
    Controller->>UseCase: getSolution(id)
    UseCase->>Repo: loadSolution(id)
    Repo-->>UseCase: ordered files
    UseCase-->>UI: read-only solution DTO
    Learner->>UI: Hide solution
    Note over UI: hide only; retain loaded data
    Learner->>UI: View again
    Note over UI: reuse cached state
```

------------------------------------------------------------------------

# 23. SQL ownership boundary

Do not put source code into SQL merely because PostgreSQL exists.

A strong boundary is:

``` text
Git/filesystem source of truth:
  exercise manifest
  starter source
  trusted tests
  reference solution
  trusted POM

PostgreSQL transactional data:
  users
  lessons
  exercise catalog projection (optional)
  attempts
  submitted-file snapshots (optional)
  evidence
  drafts (optional)
  progress
```

A future company-style schema could include:

``` sql
CREATE TABLE exercises (
    id                VARCHAR(150) PRIMARY KEY,
    lesson_id         BIGINT NOT NULL,
    title             VARCHAR(250) NOT NULL,
    language          VARCHAR(50) NOT NULL,
    difficulty        VARCHAR(50),
    estimated_minutes INTEGER,
    package_version   VARCHAR(100),
    active            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL,
    updated_at        TIMESTAMPTZ NOT NULL
);

CREATE TABLE exercise_attempts (
    id                UUID PRIMARY KEY,
    exercise_id       VARCHAR(150) NOT NULL,
    user_id           BIGINT NOT NULL,
    status            VARCHAR(40) NOT NULL,
    started_at        TIMESTAMPTZ NOT NULL,
    completed_at      TIMESTAMPTZ,
    duration_ms       BIGINT,
    runner_profile    VARCHAR(100),
    exercise_version  VARCHAR(100),
    passed_tests      INTEGER,
    total_tests       INTEGER,
    failure_category  VARCHAR(80),
    created_at        TIMESTAMPTZ NOT NULL
);

CREATE TABLE exercise_attempt_files (
    attempt_id UUID NOT NULL,
    file_path  VARCHAR(500) NOT NULL,
    content    TEXT NOT NULL,
    PRIMARY KEY (attempt_id, file_path),
    FOREIGN KEY (attempt_id)
      REFERENCES exercise_attempts(id) ON DELETE CASCADE
);

CREATE TABLE exercise_attempt_evidence (
    attempt_id    UUID NOT NULL,
    evidence_id   VARCHAR(150) NOT NULL,
    status        VARCHAR(40) NOT NULL,
    message       TEXT,
    display_order INTEGER NOT NULL,
    PRIMARY KEY (attempt_id, evidence_id),
    FOREIGN KEY (attempt_id)
      REFERENCES exercise_attempts(id) ON DELETE CASCADE
);
```

Optional drafts:

``` sql
CREATE TABLE exercise_drafts (
    user_id      BIGINT NOT NULL,
    exercise_id  VARCHAR(150) NOT NULL,
    file_path    VARCHAR(500) NOT NULL,
    content      TEXT NOT NULL,
    updated_at   TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, exercise_id, file_path)
);
```

Exercise attempts should record a package version, manifest hash, or Git
SHA plus runner profile. Otherwise historical results become ambiguous
after tests/exercises evolve.

Do not hold a DB transaction open while Maven runs. Prefer:

``` text
TX1: insert attempt RUNNING -> commit
execute Docker outside DB transaction
TX2: update result/evidence -> commit
```

------------------------------------------------------------------------

# 24. ER model

``` mermaid
erDiagram
    LESSON ||--o{ EXERCISE : contains
    EXERCISE ||--o{ EXERCISE_ATTEMPT : receives
    USER ||--o{ EXERCISE_ATTEMPT : makes
    EXERCISE_ATTEMPT ||--o{ EXERCISE_ATTEMPT_FILE : snapshots
    EXERCISE_ATTEMPT ||--o{ EXERCISE_ATTEMPT_EVIDENCE : produces
    USER ||--o{ EXERCISE_DRAFT : owns
    EXERCISE ||--o{ EXERCISE_DRAFT : has
```

------------------------------------------------------------------------

# 25. Recommended Spring mapping

A future portal API can run on Java 21 even if an exercise runner uses
Java 11.

Suggested stack:

``` text
Java 21
Spring Boot
Spring Web
Jakarta Validation
Jackson
PostgreSQL
Flyway
JPA or JdbcTemplate
Docker Java client behind an adapter
JUnit 5
Testcontainers where useful
```

Endpoints:

``` text
GET  /api/exercises/{exerciseId}
POST /api/exercises/{exerciseId}/run
GET  /api/exercises/{exerciseId}/solution
```

Conceptual controller:

``` java
@RestController
@RequestMapping("/api/exercises")
class ExerciseController {
    private final GetExerciseMetadataUseCase metadata;
    private final RunExerciseUseCase runExercise;
    private final GetExerciseSolutionUseCase solution;

    @GetMapping("/{exerciseId}")
    ExerciseMetadataResponse get(@PathVariable String exerciseId) { ... }

    @PostMapping("/{exerciseId}/run")
    ExerciseExecutionResponse run(
        @PathVariable String exerciseId,
        @Valid @RequestBody RunExerciseRequest request) { ... }

    @GetMapping("/{exerciseId}/solution")
    ExerciseSolutionResponse solution(@PathVariable String exerciseId) { ... }
}
```

The controller must not call Docker directly.

HTTP validation and domain validation should be separate.
`@NotEmpty files` is HTTP shape validation; "submitted path is declared
editable by this exercise" is application/domain validation.

------------------------------------------------------------------------

# 26. Security model for the Java rewrite

Threats and controls:

  -----------------------------------------------------------------------
  Threat                              Control
  ----------------------------------- -----------------------------------
  `../../secret` submitted path       whitelist against trusted
                                      manifest + canonical containment

  oversized source                    per-file and aggregate size limits

  fork/process exhaustion             PID, CPU, memory, timeout limits

  Docker daemon compromise            never mount Docker socket into
                                      learner container

  secret exfiltration                 no API/AWS/DB secrets in runner

  host filesystem access              only controlled temporary workspace

  arbitrary dependencies/commands     trusted POM and trusted runner
                                      command

  malicious image selection           manifest maps logical runner
                                      profile to server-owned image

  stale container/workspace           cleanup in `finally`
  -----------------------------------------------------------------------

Current personal-project policy allowed runner internet access. In a
larger public service, network policy should be explicit per runner
profile and disabled unless required.

------------------------------------------------------------------------

# 27. Concurrency and cleanup

A simple Java implementation can initially use a semaphore:

``` java
Semaphore executionPermits = new Semaphore(maxConcurrentExecutions);
```

Conceptual flow:

``` text
acquire
try
  prepare workspace
  start container
  await with timeout
  parse result
finally
  remove container
  delete workspace
  release
```

Cleanup must occur on success, compiler failure, test failure, timeout,
parsing failure, and unexpected exceptions.

At larger scale, evolve to:

``` text
API -> execution queue/job table -> runner workers -> result store
```

Do not introduce queueing complexity before workload requires it.

------------------------------------------------------------------------

# 28. Why behavioral tests matter more than solution comparison

The golden solution is not the correctness oracle by source equality.

Two implementations can be behaviorally correct while looking different.

Therefore:

``` text
trusted tests = correctness contract
golden solution = package validation + learner reference
```

Never compare learner source text with solution source to decide
correctness.

------------------------------------------------------------------------

# 29. Runner profiles and future evolution

The manifest can later declare a logical profile:

``` json
{"runnerProfile":"java-11"}
```

Server configuration maps that logical name to a trusted immutable
image.

Possible profiles:

``` text
java-11
java-17
java-21
spring-java-21
```

The browser must never submit arbitrary Docker image names.

Current infrastructure:

``` text
Browser -> API -> local Docker daemon -> disposable runner
```

Growth path:

``` text
Browser -> API -> execution queue -> dedicated runner service/host pool
```

Because application code depends on `ExerciseRunner`, the infrastructure
can evolve without rewriting the domain/use cases.

------------------------------------------------------------------------

# 30. Company-style implementation plan for rebuilding by hand

## Phase 0 --- Architecture and ADRs

Write ADRs before framework code:

``` text
ADR-001 Git/filesystem exercise packages
ADR-002 Docker execution boundary
ADR-003 Same-host runner initially
ADR-004 Trusted tests/POM
ADR-005 Lazy reference-solution retrieval
ADR-006 Attempt persistence/versioning
ADR-007 Runner profiles
ADR-008 Resource/concurrency limits
```

Draw C4 Context/Container, class, ER, and Run sequence diagrams.

## Phase 1 --- Domain + manifest parser

Implement value objects, exercise model, repository port, JSON parser,
filesystem repository, path validation, starter loading, solution
loading.

No Docker.

## Phase 2 --- Golden runner

Build runner image and prove golden pass, starter failure, compile
failure, behavioral failure, timeout, Surefire capture.

## Phase 3 --- Workspace builder

Construct fresh trusted Maven workspace. Browser source may replace only
manifest-editable files.

## Phase 4 --- Docker adapter

Implement `ExerciseRunner`, limits, timeout, cleanup, Maven cache.

## Phase 5 --- REST API

Expose metadata, Run, and solution.

## Phase 6 --- persistence

Add attempts/evidence/drafts only when required. Version attempts.

## Phase 7 --- frontend

Implement compact/expanded editor, multi-file tabs, Run, evidence, and
persistent View/Hide Solution disclosure.

## Phase 8 --- CI/CD

Compile/tests, build ARM64 images, publish immutable artifacts, deploy
runner/API/frontend.

## Phase 9 --- production smoke validation

Verify real browser, runner, evidence, solution isolation, responsive
layout, and health.

A particularly good learning order is:

``` text
domain
-> manifest parser
-> filesystem repository
-> metadata endpoint
-> solution endpoint
-> submission validation
-> workspace builder
-> fake ExerciseRunner
-> Run endpoint
-> DockerExerciseRunner
-> Surefire parser
-> attempt persistence
-> production deployment
```

Using a fake runner first keeps infrastructure complexity from hiding
application-design mistakes.

------------------------------------------------------------------------

# 31. Java test matrix

Repository:

``` text
loads valid manifest
preserves manifest order
rejects missing starter
rejects traversal
rejects symlink escape
loads multi-file solution
reports missing solution
```

Workspace:

``` text
writes only editable learner files
copies trusted tests/POM
rejects undeclared path
rejects duplicate paths
enforces size limits
```

Runner:

``` text
golden passes
starter fails
compile error classified
assertion failure classified
timeout classified
container removed
workspace removed
```

REST:

``` text
metadata 200
unknown exercise 404
run valid 200
malformed submission 400
solution 200
missing solution 404
runner infrastructure failure 503
```

Spring DI:

``` text
plain unit tests
@WebMvcTest controller slices
@SpringBootTest real application context
```

When a constructor dependency is added, review production bean
registration, slice-test mocks/imports, integration context, and
manually constructed subjects. This directly addresses the DI fixture
failure encountered in the existing implementation.

------------------------------------------------------------------------

# 32. Observability

Use a generated execution ID and structured fields:

``` text
exerciseExecutionId
exerciseId
exerciseVersion
runnerProfile
containerId
durationMs
status
failureCategory
```

Useful metrics later:

``` text
run count
pass/test-fail/compile-fail rates
timeout rate
runner startup latency
execution duration
queue wait
infrastructure failure rate
```

Never log platform secrets.

------------------------------------------------------------------------

# 33. Architecture decision summary

  ---------------------------------------------------------------------------
  Decision                Approach                Why
  ----------------------- ----------------------- ---------------------------
  Placement               lesson embedded         preserve learning context

  Editor                  compact/expanded        lesson first, IDE second
                          multi-file              

  Exercise source         Git/filesystem          versionable and reviewable

  Evaluation              trusted tests           behavioral correctness

  Build config            trusted POM             learner cannot alter judge

  Execution               disposable Docker       reproducibility/isolation

  Initial runner host     existing EC2            low cost and simplicity

  Architecture            ARM64 runner            match production host

  Cache                   Maven named volume      faster disposable runs

  Concurrency             1 initially             protect small host

  Solution                lazy GET                separate answer from
                                                  execution

  Solution UI             persistent disclosure   stable semantic interaction

  DB                      preserve PostgreSQL     avoid unrelated migration
                                                  risk

  Secrets                 SSM -\> `0600` files    controlled production
                                                  secret delivery

  Images                  GHCR + immutable digest reproducible deployments

  Prune protection        local `:deployed` tag   retain dynamic runner image

  Backup                  S3 pre-migration        low-cost deployment safety

  CI                      compile/test before     stop broken artifacts
                          deploy                  
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

# 34. Mistakes that became design lessons

1.  **Fixed reader width:** prose-oriented width constrained coding UI.\
    **Lesson:** readable prose and interactive workspace require
    separate width policies.

2.  **Run and Check did the same thing:** labels did not map to distinct
    intentions.\
    **Lesson:** UI actions should represent distinct domain operations.

3.  **Reveal/Hide moved locations:** one toggle had two physical
    controls.\
    **Lesson:** disclosure controls should remain spatially stable.

4.  **Runner pruned:** generic cleanup removed a dynamically used
    image.\
    **Lesson:** runtime image lifecycle must be modeled.

5.  **`Options.Create` compiler collision:** static inspection missed
    name resolution.\
    **Lesson:** compilation is mandatory evidence.

6.  **Test DI drift:** production DI was correct while a test
    composition root was incomplete.\
    **Lesson:** trace every new dependency through every composition
    root.

7.  **Stale browser assets:** deployed frontend looked unchanged until
    hard refresh.\
    **Lesson:** distinguish client caching from code/deployment failure.

------------------------------------------------------------------------

# 35. Review checklist

``` text
DOMAIN
[ ] Generic, not exercise-specific?
[ ] Correct aggregate/service responsibility?

API
[ ] Request/response contract?
[ ] Intentional status/error model?
[ ] New dependencies wired?

FILESYSTEM
[ ] Canonical containment?
[ ] Traversal/symlink escape rejected?
[ ] Size limits?

EXECUTION
[ ] Trusted POM/tests?
[ ] Fresh workspace?
[ ] Disposable container?
[ ] Timeout/memory/CPU/PID controls?
[ ] Cleanup always?
[ ] No Docker socket/secrets in learner container?

FRONTEND
[ ] Student/reference state isolated?
[ ] Duplicate Run prevented?
[ ] Loading/error/retry?
[ ] Accessibility?
[ ] Responsive?
[ ] No lesson-specific CSS hack?

TESTING
[ ] Source and tests compile?
[ ] Unit tests?
[ ] DI/context boot test?
[ ] Golden runner tests?
[ ] Production smoke test?

DEPLOYMENT
[ ] Immutable images?
[ ] ARM64?
[ ] Runner survives prune?
[ ] Secrets least privilege?
[ ] DB migration/backup risk understood?
```

------------------------------------------------------------------------

# 36. Definition of done for the Java rewrite

``` text
[ ] manifest parsed and validated
[ ] multi-file starter served
[ ] student state independent
[ ] trusted tests never browser-controlled
[ ] submission whitelist enforced
[ ] fresh workspace per Run
[ ] disposable runner
[ ] resource limits and timeout
[ ] cleanup verified
[ ] golden passes
[ ] starter rejected
[ ] compile/test failures classified
[ ] evidence normalized
[ ] solution lazy-loaded
[ ] solution read-only
[ ] solution isolated from student state
[ ] persistent accessible View/Hide disclosure
[ ] responsive chapter shell
[ ] real Spring context/DI test
[ ] version-aware attempts if persisted
[ ] ARM64 production artifact
[ ] CI green
[ ] production smoke test green
```

------------------------------------------------------------------------

# 37. Final engineering perspective

The browser experience is intentionally simple:

``` text
learn -> edit -> Run -> understand evidence -> View solution
```

The engineering system underneath separates:

``` text
curriculum
exercise definition
learner working state
trusted tests
trusted solution
workspace construction
execution orchestration
container infrastructure
evidence
persistence
deployment
```

That separation is the reason the implementation can grow beyond one
`Point`/`ThreedPoint` exercise.

When rebuilding it manually in Java, do not translate C# classes
line-for-line. Reproduce the responsibilities, invariants, trust
boundaries, and deployment lessons using idiomatic Java/Spring.

The central rule is:

> **The platform owns the learning contract and execution environment;
> the learner owns only the explicitly allowed solution source.**

Before writing production Java, create four artifacts yourself:

1.  C4 Context/Container diagram;
2.  domain/application class diagram;
3.  ER diagram for attempts/progress;
4.  Run sequence diagram.

Then implement the system vertically, with a fake runner before Docker.
That process will exercise the same skills expected in a real backend
project: requirements analysis, domain modeling, API design, SQL design,
dependency injection, security, container orchestration, testing, CI/CD,
deployment, and operational debugging.
