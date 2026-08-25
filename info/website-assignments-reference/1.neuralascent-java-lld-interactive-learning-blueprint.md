# Neuralascent — Java LLD Interactive Learning Implementation Blueprint

**Status:** Initial implementation blueprint / source of truth  
**Primary starting point:** `Chapters → Java Low-Level Design & Spring Architecture → Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems`  
**Initial implementation stack:** React/Vite frontend + existing .NET API + PostgreSQL + Docker  
**Initial infrastructure target:** Existing small EC2 instance (currently 1 GB RAM)  
**Long-term learning goal:** Use the finished .NET implementation as a stable reference and later manually migrate the backend to Java/Spring Boot.

---

## 1. Why We Are Building This

Neuralascent already provides the **learning/reading layer**:

```text
Pathway
  → Module
    → Lesson / Chapter
      → Concepts
      → Backend scenarios
      → Practice loop
      → Evidence of understanding
      → Notes
```

The next goal is to make the chapter itself interactive without turning Neuralascent into a clone of Scaler, LeetCode, HackerRank, or a browser IDE.

The desired learning loop is:

```text
Read
  → Think
  → Answer a contextual question
  → Write a small amount of code
  → Run / check it
  → Understand failures
  → Correct the implementation
  → Record progress / evidence
  → Continue reading
```

The most important product decision is:

> **Practice remains part of the chapter. It does not initially become a separate coding website or separate lab page.**

The implementation should preserve Neuralascent's existing visual identity and reading experience.

---

# 2. Confirmed Product Decisions

The following decisions are considered agreed starting assumptions.

## 2.1 Start with Java LLD

The first implementation targets:

```text
Chapters
→ Java Low-Level Design & Spring Architecture
→ Lesson 1 — Intro to LLD for Scalable & AI-Ready Systems
```

We will prove the complete architecture with one lesson before attempting broad curriculum coverage.

After the vertical slice works well, exercises can progressively be added to the first three Java LLD modules.

---

## 2.2 Two Inline Interaction Types

A lesson can contain both:

1. **Concept / choose-the-correct-answer interactions**
2. **Java coding exercises**

They should appear naturally within or near the relevant lesson content.

The purpose is not to add quizzes merely for gamification. Each interaction should reinforce the concept immediately surrounding it.

---

## 2.3 LLM-Assisted Exercise Authoring

An LLM may be used during content authoring to analyze a lesson and propose:

- conceptual questions,
- multiple-choice questions,
- distractors,
- explanations,
- small coding exercises,
- starter code,
- expected learning outcomes,
- visible tests,
- hidden tests,
- possible edge cases,
- design checks.

However:

> **The LLM is an authoring assistant, not automatically the source of truth for correctness.**

Generated exercises/tests should be reviewed before becoming part of the curriculum.

For the initial version, exercise definitions should be deterministic and stored with the application/database rather than dynamically asking an LLM to judge every user submission.

This keeps runtime cost, latency, unpredictability, and infrastructure complexity low.

---

# 3. UX Principle: Extend the Existing Chapter

Neuralascent should retain its current editorial/technical-book character.

The coding experience must not suddenly look like a different product.

Existing characteristics to preserve include:

- warm/off-white reading background,
- restrained cards,
- thin borders,
- generous spacing,
- serif/editorial headings,
- restrained green/teal accent usage,
- existing breadcrumbs,
- existing chapter/module navigation,
- current left/right contextual panels where applicable,
- minimal visual noise.

Scaler is inspiration for the **learning workflow**, not for Neuralascent's visual design.

---

# 4. Interaction Type A — Contextual Concept Question

A concept check should be lightweight and embedded directly into the lesson.

Example:

```text
CHECK YOUR UNDERSTANDING
────────────────────────────────────────

Why does separating responsibilities generally
make a system easier to evolve?

○ It guarantees better runtime performance

○ It reduces the number of classes

● Changes to one responsibility are less likely
  to affect unrelated behavior

○ It removes the need for interfaces

                         Check answer
```

After checking:

```text
✓ Correct

Separating responsibilities reduces coupling.
A change in persistence, validation, or transport
logic is therefore less likely to require changes
to unrelated parts of the system.

Continue →
```

For an incorrect answer:

```text
Not quite.

Think about which parts of the system would need
to change when one responsibility evolves.

Try again
```

### Requirements

A concept question should support:

- question text,
- 2+ choices,
- one or potentially multiple correct answers later,
- explanation,
- optional hint,
- attempt count,
- completion state,
- linkage to lesson/chapter,
- ordering/placement in lesson,
- optional evidence/progress contribution.

### Initial recommendation

V1 should support **single-answer multiple choice only**.

Multiple-answer, free-text, matching, ordering, etc. are future extensions.

---

# 5. Interaction Type B — Inline Java Coding Canvas

The Java editor initially appears as a small embedded component.

Example collapsed/compact state:

```text
PRACTICE LOOP

Separate responsibilities in this small service.

┌─────────────────────────────────────────────────────┐
│ JAVA                                      ↗ Expand │
├─────────────────────────────────────────────────────┤
│ 1  public Order createOrder(OrderRequest request) {│
│ 2      // implement this                           │
│ 3                                                  │
│ 4  }                                               │
├─────────────────────────────────────────────────────┤
│                                Run   Check solution │
└─────────────────────────────────────────────────────┘
```

The initial height should remain small enough that the lesson continues to feel like a reading experience.

---

# 6. Expanded Coding Canvas

Clicking **Expand** expands the same component in place.

It must not initially navigate to another page.

Example:

```text
┌───────────────────────────────────────────────────────────┐
│ JAVA                                        ↙ Collapse   │
├───────────────┬───────────────────────────────────────────┤
│ FILES         │ OrderService.java                         │
│               │                                           │
│ Order.java    │ public class OrderService {               │
│ Request.java  │                                           │
│ Service.java  │     public Order createOrder(...) {       │
│               │         // TODO                           │
│               │     }                                     │
│               │ }                                         │
├───────────────┴───────────────────────────────────────────┤
│                                      Run   Check solution │
└───────────────────────────────────────────────────────────┘
```

V1 may expose only one editable file, but the component/data model should not assume exercises will always be single-file.

LLD will naturally require multi-file exercises later.

---

# 7. Results and Failure Drawer

Do not permanently reserve large screen space for a terminal.

Successful result:

```text
✓ 6 / 6 tests passed                         ∨ Details
```

Failure:

```text
✕ 4 / 6 tests passed                         ∨ View failures
```

Expanding the result:

```text
TEST RESULTS
────────────────────────────────────────────

✓ shouldRejectNullRequest
✓ shouldValidateInventory
✓ shouldCreateOrder
✓ shouldPersistOrder

✕ shouldNotPersistInvalidOrder

  Expected repository.save() to never be called,
  but it was called once.

  OrderServiceTest.java:74

✕ shouldPropagateRepositoryFailure

  Expected: RepositoryException
  Actual:   NullPointerException

                                      ∧ Collapse
```

Raw Maven/Gradle/JUnit logs should **not** be the primary feedback UI.

They can be available under an advanced section:

```text
Advanced
  → Raw execution log
```

The backend should return structured results that Neuralascent renders consistently.

---

# 8. Run vs Check Solution

These actions should have different semantics.

## Run

Purpose:

> Help the learner iterate quickly.

Possible behavior:

```text
Compile
  → run visible tests
  → return results
```

It should not necessarily mark the exercise complete.

---

## Check Solution

Purpose:

> Determine whether the implementation satisfies the exercise.

Possible behavior:

```text
Compile
  → visible tests
  → hidden tests
  → design/architecture checks where applicable
  → record submission
  → update learning progress
```

This distinction should be maintained even if V1 temporarily shares some implementation internally.

---

# 9. Core Architectural Decision: Browser Session != Java Execution Session

The editor does not require a running JVM/container while the learner is thinking or typing.

```text
Browser editor
     │
     │  React state / saved draft
     │
     └─────────────────────────────┐
                                   │
Only Run / Check requires compute  │
                                   ▼
                           Execution request
```

Therefore:

> **Do not keep one Java container alive for five minutes waiting for editor inactivity.**

Instead, create a short-lived execution environment only when code is executed.

This is especially appropriate for the current 1 GB EC2 target.

---

# 10. High-Level Architecture

Initial architecture:

```text
                         Browser
                            │
                    React / Vite UI
                            │
                            ▼
                        .NET API
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
        PostgreSQL     Curriculum       Execution
        progress       / exercises      Orchestrator
                                            │
                                            ▼
                                  Ephemeral Java Sandbox
                                            │
                                      compile + tests
                                            │
                                            ▼
                                     structured result
```

No new distributed infrastructure should be introduced unless measurements demonstrate a need.

Specifically, V1 does **not** require:

- Kubernetes,
- Kafka,
- RabbitMQ,
- Redis,
- ECS,
- Lambda,
- microservices,
- a permanent worker pool,
- a separate Java application server.

---

# 11. Java Runner Strategy

Use a prebuilt runner image rather than building a full environment for every submission.

Conceptual image:

```text
neuralascent-java-runner:<version>
```

It can contain:

- selected JDK version,
- Maven or Gradle,
- JUnit 5,
- required assertion/testing libraries,
- later: ArchUnit,
- later: Checkstyle/PMD/SpotBugs if useful,
- a small execution script,
- test-result export/parsing support.

Exact JDK/build-tool versions are **TBD and should be aligned with the Java curriculum/project requirements before implementation**.

Do not invent versions merely to begin coding.

---

# 12. Exercise Package Concept

Conceptually:

```text
exercises/
└── oop-example-001/
    ├── provided/
    │   └── Order.java
    │
    ├── starter/
    │   └── OrderService.java
    │
    ├── tests/
    │   ├── visible/
    │   │   └── OrderServiceVisibleTest.java
    │   └── hidden/
    │       └── OrderServiceHiddenTest.java
    └── exercise.json
```

Files fall into three categories.

## Provided

Learner can see them but should not necessarily modify them.

## Editable

Starter files shown in the editor and replaced/overlaid with learner code during execution.

## Hidden

Server-owned tests/checks never sent to the browser.

This is preferable to allowing a submission to replace an arbitrary project directory.

The server determines exactly which paths the learner is permitted to change.

---

# 13. Example Exercise Definition

The exact schema is TBD, but the architecture should support something similar to:

```json
{
  "id": "java-lld-lesson-1-exercise-1",
  "lessonId": "java-lld-lesson-1",
  "type": "java",
  "title": "Separate Order Creation Responsibilities",
  "instructions": "Implement the required behavior...",
  "difficulty": "introductory",
  "editableFiles": [
    "src/main/java/example/OrderService.java"
  ],
  "providedFiles": [
    "src/main/java/example/Order.java"
  ],
  "visibleTests": [
    "OrderServiceVisibleTest"
  ],
  "hiddenTests": [
    "OrderServiceHiddenTest"
  ]
}
```

Do not treat this sample as the final persistence contract.

The first vertical slice should determine which fields are actually necessary.

---

# 14. Execution Lifecycle

Recommended per-execution lifecycle:

```text
User clicks Run / Check
          │
          ▼
.NET API validates request
          │
          ▼
Load trusted exercise definition
          │
          ▼
Create unique temporary workspace
          │
          ├── copy provided files
          ├── copy starter/project files
          ├── copy server-owned tests
          └── overlay allowed user-editable files
          │
          ▼
Start restricted Java runner container
          │
          ├── compile
          ├── execute allowed tests
          ├── collect structured output
          └── enforce hard timeout
          │
          ▼
Stop / kill runner
          │
          ▼
Delete temporary workspace
          │
          ▼
Parse / normalize result
          │
          ├── optionally persist attempt
          └── return structured response
          │
          ▼
React renders result drawer
```

The container should be destroyed immediately after execution.

---

# 15. Timeout Model

There are two different concepts:

### Editor inactivity

Does **not** need a Java container.

The learner may spend 30–60 minutes thinking without consuming runner resources.

### Execution timeout

Protects the server against broken or hostile code.

Example:

```java
while (true) {
}
```

must be terminated quickly.

Initial values should be measured rather than assumed.

A reasonable design target is:

```text
Expected simple exercise: a few seconds
Hard execution timeout: short and configurable
```

A 10–15 second hard timeout was discussed as an initial possibility, but it remains **TBD until tested on the actual EC2 instance and runner image**.

---

# 16. Sandbox Security Requirements

Java submissions must be treated as untrusted code even if initially only the owner uses the site.

The sandbox should ultimately enforce:

- non-root execution,
- hard memory limit,
- CPU limit,
- PID/process limit,
- hard execution timeout,
- no outbound network,
- no unnecessary Linux capabilities,
- restricted/read-only filesystem where practical,
- a dedicated temporary writable workspace,
- no application secrets,
- no PostgreSQL credentials,
- no access to the application's filesystem,
- no access to other containers,
- no host network,
- no Docker socket inside the runner,
- cleanup after success/failure/timeout.

### Critical rule

Never expose:

```text
/var/run/docker.sock
```

to submitted Java code.

The runner must not be able to control Docker or the host.

The precise safe mechanism by which the .NET application launches isolated jobs is an implementation decision that must be reviewed carefully before deployment.

---

# 17. 1 GB EC2 Resource Strategy

The current deployment is intentionally small.

Therefore V1 should optimize for simplicity and low idle resource consumption.

Recommended behavior:

```text
Idle:
React/nginx + .NET API + PostgreSQL

Java execution:
temporarily add one restricted runner

Execution finishes:
runner disappears
```

Do not maintain warm JVM containers initially.

Also initially consider limiting Java execution concurrency.

For example:

```text
Maximum concurrent Java runners = 1
```

may be entirely appropriate for a personal site with approximately 2–10 maximum visitors.

The exact concurrency and memory limits are **TBD after measuring baseline EC2 memory and runner consumption**.

If the workload later demonstrates that 1 GB is insufficient, upgrading to a 2 GB or 4 GB EC2 instance is acceptable. The architecture should not prematurely optimize around avoiding that upgrade at all costs.

---

# 18. Draft Persistence

Learner code should not depend on container lifetime.

Potential model:

```text
React editor state
      │
      ├── local immediate state
      │
      └── autosaved server draft
                │
                ▼
            PostgreSQL
```

V1 choices to evaluate:

- save only in browser/local storage,
- save to API on debounce,
- save when editor loses focus,
- save explicitly,
- combination of local + server persistence.

Recommended direction:

> Keep immediate editing client-side and support server-side draft persistence so a learner can return to the exercise later.

Exact autosave behavior is TBD.

---

# 19. Suggested Domain Model

Avoid creating completely disconnected systems for every exercise type.

A generic learning interaction model should be considered.

Conceptually:

```text
Lesson
  │
  ├── Interaction
  │      │
  │      ├── ConceptQuestion
  │      │
  │      └── CodingExercise
  │
  └── Progress
```

Possible entities:

```text
LearningInteraction
- Id
- LessonId
- Type
- Title
- Position
- IsRequired
- Configuration
```

For questions:

```text
ConceptQuestion
- InteractionId
- Prompt
- Explanation

ConceptQuestionOption
- Id
- QuestionId
- Text
- IsCorrect
- Position
```

For coding:

```text
CodingExercise
- InteractionId
- ExerciseKey
- Language
- Instructions
- Difficulty
- RunnerConfiguration
```

Attempts:

```text
ExerciseAttempt
- Id
- ExerciseId
- UserId
- AttemptType        // Run / Check
- Status
- StartedAt
- CompletedAt
- Duration
- Summary
```

Submitted files should be modeled separately or stored as a versioned payload depending on actual needs.

Question attempts may use their own simple model or a generic attempt abstraction.

### Important

This is a design proposal, not a final EF Core schema.

Before migrations are created, inspect the existing repository/domain model and integrate with existing `Verticals`, `Tasks`, lesson/progress structures rather than duplicating concepts.

---

# 20. API Shape

Exact routes should match existing API conventions after repository inspection.

Conceptual API only:

```text
GET  /api/lessons/{lessonId}/interactions

POST /api/questions/{questionId}/check

GET  /api/exercises/{exerciseId}

GET  /api/exercises/{exerciseId}/draft
PUT  /api/exercises/{exerciseId}/draft

POST /api/exercises/{exerciseId}/run
POST /api/exercises/{exerciseId}/check

GET  /api/exercises/{exerciseId}/attempts
```

Possible Run/Check request:

```json
{
  "files": [
    {
      "path": "src/main/java/example/OrderService.java",
      "content": "public class OrderService { ... }"
    }
  ]
}
```

The server must validate every submitted path against the trusted exercise definition.

The client must never be allowed to choose arbitrary server paths.

---

# 21. Structured Execution Response

Do not make raw console output the primary API contract.

Conceptual response:

```json
{
  "status": "failed",
  "compiled": true,
  "timedOut": false,
  "testsPassed": 4,
  "testsFailed": 1,
  "durationMs": 381,
  "tests": [
    {
      "name": "shouldCreateOrder",
      "status": "passed"
    },
    {
      "name": "shouldRejectInvalidOrder",
      "status": "failed",
      "message": "Expected IllegalArgumentException",
      "location": "OrderServiceTest.java:42"
    }
  ],
  "rawLogAvailable": true
}
```

Other states must include:

```text
queued / starting (only if later needed)
compilation_failed
tests_failed
passed
timed_out
runner_error
```

V1 may not require asynchronous polling if executions remain short enough for a normal request/response lifecycle.

This should be measured before introducing queues.

---

# 22. Compilation Errors

Compilation errors deserve first-class UI treatment.

Example:

```text
COMPILATION FAILED
────────────────────────────────────

OrderService.java:18

cannot find symbol
  symbol:   variable repository
  location: class OrderService

18 │ repository.save(order);
   │ ^^^^^^^^^^
```

The UI should make compiler errors readable and, where practical, map them to editor lines.

Raw compiler logs remain available as secondary information.

---

# 23. LLD-Specific Validation

Java LLD cannot be judged solely by output.

Over time exercises may use three validation layers.

## Functional

```text
✓ correct behavior
✓ edge cases
✓ exception behavior
```

## Structural / Design

Examples:

```text
✓ class implements required interface
✓ dependency is injected
✓ client does not instantiate concrete implementation
✓ field visibility satisfies encapsulation requirement
```

Potential tool later:

- ArchUnit

## Static Quality

Potential later additions:

- Checkstyle,
- PMD,
- SpotBugs.

Do not introduce all tools in V1.

Start with JUnit and only add design/static checks when an actual lesson requires them.

---

# 24. Exercise Progression

Not every lesson needs a large project.

Use several scales.

## Micro Exercise

Approximately a few lines or one method.

Good for:

- syntax,
- encapsulation,
- method behavior,
- small OOP concepts.

## Small Design Exercise

1–3 classes/interfaces.

Good for:

- inheritance,
- composition,
- abstraction,
- SOLID introductions,
- patterns.

## Module Lab

Multi-file mini-project.

Example:

```text
Library Management

Book
Member
Loan
LibraryService
Repository
```

Can contain:

- functional tests,
- design checks,
- reflection/evidence prompts.

This gives the curriculum increasing depth without making every chapter cumbersome.

---

# 25. Lesson 1 Vertical Slice

Do not begin by implementing the entire first three modules.

The first milestone is:

> **One complete, polished interaction flow inside Lesson 1.**

The Lesson 1 content should first be analyzed to determine the most appropriate interaction.

It may contain:

1. at least one contextual concept question, and
2. one very small Java exercise **only if the lesson content genuinely supports a coding task**.

Do not force a coding exercise into a conceptual lesson merely because the feature exists.

If Lesson 1 is primarily conceptual, the initial coding exercise can be intentionally tiny and focus on responsibility/separation/design reasoning.

---

# 26. Phase 0 — Repository Reconnaissance

Before changing code, Codex/LLM should inspect the actual current repository.

Required reconnaissance:

- current frontend routing,
- chapter page components,
- lesson content representation,
- current data-loading path,
- current `.NET` solution/projects,
- EF Core entities/context,
- migrations,
- progress/completion logic,
- authentication/identity assumptions if any,
- Docker Compose,
- nginx/frontend serving,
- current EC2 deployment assumptions,
- tests,
- CI/CD.

The implementation plan should then be reconciled with reality.

### Rule

> **Do not refactor unrelated stable functionality while adding the exercise system.**

The current website is a working reference and should remain stable.

---

# 27. Phase 1 — Concept Question Vertical Slice

Implement one Lesson 1 concept question end-to-end.

Target:

```text
Lesson content
   ↓
Question card
   ↓
Select answer
   ↓
Check
   ↓
Correct/incorrect feedback
   ↓
Explanation
   ↓
Persist attempt/progress if appropriate
```

Acceptance criteria:

- visually consistent with current lesson,
- no page navigation,
- keyboard accessible,
- responsive,
- deterministic grading,
- explanation displayed,
- retry behavior defined,
- existing lesson functionality unaffected.

---

# 28. Phase 2 — Static Coding Canvas

Add the embedded editor UI without execution first.

Requirements:

- compact initial height,
- expand/collapse in place,
- Java syntax highlighting,
- line numbers,
- editable starter code,
- reset-to-starter action,
- responsive behavior,
- no separate page,
- no loss of chapter context.

Monaco Editor is a candidate because it provides a strong browser editing experience, but the exact editor library should be confirmed against bundle size, existing dependencies, and styling needs.

Do not add Monaco solely because it was discussed if a smaller existing editor already fits the repository.

---

# 29. Phase 3 — One Java Runner Vertical Slice

Implement:

```text
one exercise
one editable Java file
one or few JUnit tests
Run
structured result
cleanup
```

Do not add hidden tests/design checks/multi-file complexity until the fundamental sandbox lifecycle works.

Acceptance criteria:

- user code is never executed directly on the host,
- runner has a hard timeout,
- runner has memory/CPU restrictions,
- network disabled,
- no secrets exposed,
- workspace unique per execution,
- workspace cleaned,
- container removed,
- compile success/failure returned cleanly,
- tests returned as structured results,
- infinite loop is terminated,
- application remains healthy after failed execution.

---

# 30. Phase 4 — Check Solution + Hidden Tests

Once Run works:

- distinguish Run from Check,
- add hidden tests,
- persist submissions,
- mark completion only according to explicit rules,
- connect result to chapter progress/evidence.

---

# 31. Phase 5 — Drafts and Learning History

Add:

- saved code draft,
- previous submissions,
- attempt count,
- last result,
- completion state.

Potential UI:

```text
Last attempt: 5 / 6 tests
Attempts: 3
Last worked: ...
```

Avoid over-gamifying the interface.

---

# 32. Phase 6 — Multi-File LLD Exercises

Extend the canvas to support:

```text
FILES
├── Interface.java
├── Service.java
├── Repository.java
└── Model.java
```

Support:

- provided/read-only files,
- editable files,
- tabs/file explorer,
- hidden tests,
- optional architecture tests.

Only introduce this after single-file execution is stable.

---

# 33. Phase 7 — First Three Java LLD Modules

After the engine is stable, use LLM assistance to analyze each lesson in the first three modules.

For every lesson decide:

```text
Does it benefit from:
- no interaction?
- concept question?
- micro coding exercise?
- small design exercise?
```

Do not enforce identical interaction counts across lessons.

The curriculum should determine the exercise, not the feature checklist.

Each LLM-proposed exercise must be reviewed for:

- correctness,
- relevance,
- ambiguity,
- Java conventions,
- test quality,
- hidden-test fairness,
- expected difficulty,
- whether it actually reinforces the lesson.

---

# 34. Learning Evidence Integration

The current chapter concept of **Evidence of Understanding** should become meaningful.

Possible completion model later:

```text
Lesson mastery

Reading                    ✓
Concept check              ✓
Coding practice            ✓
Reflection                 ○

Progress: ...
```

Do not finalize percentages until existing progress semantics are inspected.

A learner should not lose progress because an optional extension is incomplete.

Required vs optional interactions must be represented explicitly.

---

# 35. Reflection

Some exercises should end with a small reflection rather than only "Passed".

Example:

```text
Why is composition preferable to inheritance
in this implementation?

[ field note ]
```

This is particularly valuable for LLD because passing tests does not necessarily demonstrate design understanding.

Reflection can connect to the site's existing notes/evidence model.

---

# 36. Error Handling

The system must distinguish learner errors from platform errors.

Learner-facing:

```text
Compilation failed
Test failed
Timed out
```

Platform-facing:

```text
Runner unavailable
Container startup failed
Workspace creation failed
Result parser failed
Unexpected infrastructure error
```

Do not show internal stack traces, host paths, credentials, Docker internals, or sensitive environment information to the browser.

Provide a safe message:

```text
The execution environment could not complete this run.
Your code has been preserved. Try again.
```

Log the detailed error server-side.

---

# 37. Observability

Keep V1 simple but instrument enough to diagnose the runner.

Log:

- execution/request ID,
- exercise ID,
- attempt type,
- runner start/end,
- elapsed time,
- timeout,
- exit code,
- compile/test outcome,
- cleanup outcome,
- resource failure if detectable.

Do **not** log:

- secrets,
- authentication tokens,
- entire arbitrary source code by default,
- sensitive environment variables.

Metrics can later include:

```text
execution count
average execution duration
timeout count
runner failures
peak concurrent runners
```

No dedicated monitoring stack is required initially if existing logging is sufficient.

---

# 38. Cleanup Strategy

Normal path:

```text
execution ends
  → stop/kill container
  → remove container
  → remove workspace
```

Also implement defensive cleanup for abnormal failures.

Potential strategies:

- `finally` cleanup in orchestrator,
- unique execution labels,
- startup cleanup of stale execution resources,
- periodic cleanup job later if needed.

Do not depend solely on a five-minute inactivity timer.

---

# 39. Concurrency

Because the deployment is small, concurrency should be deliberately bounded.

Initial option:

```text
one Java execution at a time
```

If another execution arrives, possible behaviors include:

- short wait,
- reject with "runner busy, retry",
- simple in-process semaphore.

Do not introduce Redis/queues until concurrent demand justifies them.

Exact UX is TBD.

---

# 40. Authentication / Abuse Protection

Even with 2–10 expected visitors, the public endpoint could theoretically be discovered.

Before enabling arbitrary Java execution publicly, confirm:

- who can execute exercises,
- whether login is required,
- rate limiting,
- request/body-size limits,
- maximum number/size of submitted files,
- maximum source length,
- execution concurrency.

If the existing site has no authentication, execution access may initially need to be restricted rather than assuming obscurity is sufficient.

This is an explicit **open decision**.

---

# 41. SQL Reuse Later

The immediate target is Java LLD.

However, the interaction architecture should be reusable.

Later:

```text
LearningInteraction
      │
      ├── ConceptQuestion
      └── CodingExercise
              │
              ├── JavaRunner
              └── SqlRunner
```

SQL can use the same concepts:

- inline editor,
- Run,
- Check,
- structured results,
- attempts,
- progress,
- expandable details.

The execution implementation will differ.

SQL should use a restricted practice database role/environment and must never execute arbitrary learner SQL using the application's privileged database credentials.

SQL implementation is intentionally out of scope for the first Java vertical slice.

---

# 42. Future Spring Labs

Later Java/Spring exercises can become larger:

```text
Build POST /orders

Requirements:
- request validation
- service boundary
- persistence
- transaction
- correct HTTP status
```

Potential execution:

```text
student Spring project
       +
tests
       +
temporary PostgreSQL/test environment
       ↓
integration tests
```

This is significantly more resource-intensive and should not be designed into V1 beyond keeping the exercise model extensible.

---

# 43. Future .NET → Spring Boot Migration

This is a core learning goal, not merely a technology replacement.

The sequence is intentionally:

```text
1. Keep stable .NET backend.
2. Build interactive learning system in .NET.
3. Use Neuralascent to practise Java/LLD/Spring.
4. Reach sufficient confidence.
5. Manually reimplement the backend in Spring Boot.
6. Compare behavior against the known-good .NET implementation.
7. Migrate capability by capability.
```

This creates a real migration exercise covering concepts such as:

```text
ASP.NET Controllers       → Spring @RestController
.NET dependency injection → Spring DI
EF Core                   → JPA/Hibernate
LINQ/data access          → repositories/JPQL/SQL
middleware                → filters/interceptors
exception handling        → @ControllerAdvice
configuration             → application configuration
xUnit                     → JUnit
integration tests         → Spring testing
database migrations       → Flyway/Liquibase (decision later)
```

The goal is to perform this migration manually for learning rather than asking an LLM to blindly translate the entire backend.

The existing .NET system remains the behavioral reference.

---

# 44. Testing Strategy

## Frontend

Test:

- concept question selection,
- correct/incorrect states,
- retry,
- editor expansion/collapse,
- draft preservation,
- Run loading state,
- structured results,
- compilation errors,
- timeout UI,
- raw-log drawer,
- responsive behavior,
- keyboard/accessibility basics.

## API

Test:

- exercise retrieval,
- question checking,
- allowed file validation,
- rejected arbitrary paths,
- Run vs Check semantics,
- result parsing,
- attempt persistence,
- progress updates,
- malformed payloads,
- size limits,
- concurrency control.

## Runner

Must test:

- valid Java,
- compilation failure,
- test failure,
- all tests pass,
- infinite loop,
- excessive memory attempt,
- process spawning attempt,
- network access attempt,
- forbidden filesystem access,
- timeout,
- cleanup after crash.

## End-to-End

At minimum:

```text
Open Lesson 1
→ answer concept question
→ open coding canvas
→ modify starter code
→ Run
→ see failure
→ correct code
→ Check solution
→ pass
→ refresh
→ progress/draft/submission state remains correct
```

---

# 45. Definition of Done for the First Vertical Slice

The first implementation is successful when:

- Lesson 1 still looks and behaves like Neuralascent.
- A contextual concept question is embedded naturally.
- A compact Java coding canvas is embedded in the same page.
- The editor expands/collapses without navigation.
- User code survives normal UI interactions.
- Run executes Java in an isolated ephemeral environment.
- A broken infinite-loop solution cannot permanently consume the EC2.
- Compile errors are shown clearly.
- Test failures are shown as structured feedback.
- Error details expand/collapse.
- Check Solution can determine pass/fail.
- The container/workspace is removed after execution.
- Existing chapter/progress behavior is not broken.
- The architecture can later support multi-file exercises.
- No unnecessary distributed infrastructure has been added.
- Security assumptions and remaining TBDs are documented.

---

# 46. Explicit Non-Goals for V1

Do not build:

- a Scaler clone,
- LeetCode/HackerRank clone,
- a complete browser VS Code,
- collaborative editing,
- real-time multi-user coding,
- Kubernetes,
- distributed runner workers,
- a persistent Java container per learner,
- AI grading of every submission,
- dynamic AI-generated exercises on every page load,
- full first-three-module exercise coverage before proving Lesson 1,
- SQL execution before Java vertical slice is stable,
- Spring integration labs,
- the Spring Boot backend migration.

These can be revisited only after the core workflow is proven.

---

# 47. Open Decisions / TBDs

These should be resolved from repository inspection and measurement rather than guessed.

1. Exact Java/JDK version.
2. Maven vs Gradle for runner exercises.
3. Editor library (Monaco vs a lighter alternative).
4. Existing lesson-content storage format and best interaction insertion mechanism.
5. Exact EF Core schema integration.
6. Exact progress/completion semantics.
7. Authentication/authorization for code execution.
8. Rate limiting.
9. Runner memory limit.
10. Runner CPU limit.
11. Hard execution timeout.
12. Maximum concurrent executions.
13. Exact mechanism used by .NET to launch isolated Docker workloads.
14. Whether raw logs are persisted.
15. How long attempts/submitted source are retained.
16. Draft autosave policy.
17. Whether `Run` results are persisted or only `Check` submissions.
18. Visible vs hidden test policy.
19. Exact Lesson 1 question/exercise content.
20. Whether exercise definitions live in DB, repository files, or a hybrid.
21. CI strategy for validating exercise packages/tests.
22. EC2 resource baseline after the runner image exists.

---

# 48. Recommended First Codex Work Session

The first implementation session should **not start by writing the runner**.

Ask Codex to:

```text
1. Inspect the current repository thoroughly.
2. Map the current lesson/chapter frontend architecture.
3. Map the current .NET API/domain/EF Core architecture.
4. Map current Docker/Compose/deployment behavior.
5. Identify the exact files/components/entities that should change.
6. Compare repository reality against this blueprint.
7. Report conflicts/TBDs.
8. Propose the smallest Lesson 1 vertical-slice change set.
9. Do not implement until the proposed plan has been reviewed.
```

After that review:

```text
Lesson 1 concept question
        ↓
static coding canvas
        ↓
runner prototype
        ↓
Run
        ↓
structured result
        ↓
Check
        ↓
progress
```

This minimizes the chance that an LLM performs a large speculative refactor.

---

# 49. Guiding Engineering Principles

Throughout implementation:

### Preserve the working reference

The existing site works. Extend it incrementally.

### Build one vertical slice first

One excellent Lesson 1 experience is more valuable than 100 partially implemented exercises.

### Curriculum drives interaction

Do not force code onto lessons where a concept question/reflection is more appropriate.

### Keep editing and execution separate

Browser editing is cheap; Java execution is temporary compute.

### Treat code as untrusted

Even personal tooling should have a proper execution boundary.

### Return structured domain results

Neuralascent should render useful feedback, not expose infrastructure logs as its UX.

### Measure before scaling

Stay on the current EC2 while it is sufficient. Upgrade when actual measurements justify it.

### Avoid premature distributed architecture

The expected user count does not justify queues, Kubernetes, worker fleets, etc.

### Use the project itself for upskilling

Building the exercise system teaches backend/system design; using it teaches Java/LLD; manually migrating the stable backend later teaches Spring in a real system.

---

# 50. Target Learning Journey

The resulting Neuralascent experience should eventually feel like:

```text
                   NEURALASCENT

                      Learn
                        │
                        ▼
                 Read the concept
                        │
                        ▼
                 Think / question
                        │
                        ▼
                 Write small code
                        │
                        ▼
                 Run and observe
                        │
                        ▼
                  Diagnose failure
                        │
                        ▼
                 Correct the design
                        │
                        ▼
                 Check solution
                        │
                        ▼
              Record understanding
                        │
                        ▼
                  Continue learning
```

The platform is therefore not merely a curriculum tracker and not merely a coding judge.

It becomes a personal engineering learning environment where **reading, reasoning, implementation, testing, debugging, reflection, and progress live in the same chapter experience**.

---

## Final Starting Scope

For the next implementation session, the scope is deliberately narrow:

> **Start at Java LLD Lesson 1. Analyze the real lesson content. Add one contextually appropriate concept interaction and design one small inline Java exercise if appropriate. Preserve the existing chapter UI. Build toward an expandable coding canvas and an ephemeral, restricted, per-execution Java/JUnit Docker runner orchestrated by the existing .NET backend. Validate the entire vertical slice before expanding to other lessons or modules.**

This document should be updated as decisions are confirmed during implementation rather than allowing assumptions to silently become architecture.
