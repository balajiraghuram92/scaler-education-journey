# NeuralAscent / Scaler Education Journey
# Java-First Rebuild, .NET Migration, AI Evolution & Localization Practice Roadmap

**Document type:** Personal engineering learning + implementation roadmap  
**Primary project:** `scaler-education-journey`  
**Current public site:** `https://neuralascent.top/chapters`  
**Repository:** `https://github.com/balajiraghuram92/scaler-education-journey`  
**Starting backend:** ASP.NET Core / C#  
**Starting frontend:** React / Vite  
**Starting database:** PostgreSQL  
**Target backend:** Java 21 + Spring Boot  
**Target AI direction:** Spring AI + provider-neutral AI gateway + RAG  
**Final practice project:** Rebuild a simplified version of the Unity Localization solution from professional experience  
**Status:** Learning and implementation master plan  
**Last updated:** 2026-09-01

---

# 1. Why This Roadmap Exists

This project is intentionally being used as a **learning vehicle**, not merely as a software product.

The existing NeuralAscent / `scaler-education-journey` application was created with substantial AI assistance. React, ASP.NET Core, architecture diagrams, UI/UX concepts, and much of the implementation were generated through interactions with Claude and Gemini.

That is useful for proving that an idea can be turned into a working system, but it does **not** automatically produce understanding of the codebase.

The next stage therefore has a different objective:

> Rebuild the platform yourself, starting from extremely small building blocks, while using the existing .NET application as the behavioral and architectural reference.

The objective is **not** to become a frontend specialist.

The objective is **not** to memorize Java syntax from a video course.

The objective is:

> Start from basic Java knowledge, progressively understand every backend layer, rebuild the application in Java/Spring, and deliberately introduce increasingly difficult production and AI engineering problems until the system becomes a serious portfolio and learning platform.

This roadmap is therefore a hybrid of:

1. Java/Spring learning;
2. backend engineering practice;
3. frontend literacy sufficient to work with a React application;
4. .NET-to-Java migration practice;
5. AI engineering;
6. production architecture;
7. system design;
8. and finally a much more difficult localization-domain implementation.

The existing technical documents already define a larger target architecture centered around exact application context, policy-controlled tutoring, filtered RAG, cost controls, support workflows, and eventual Spring Boot migration. This roadmap changes the **learning sequence**, not that end-state vision.

---

# 2. The Most Important Constraint: Do Not Treat Yourself as a .NET Developer

The existing application may contain a considerable amount of .NET and React complexity, but that does not mean the first task is to understand all of it.

The learning assumption for this roadmap is:

```text
Current situation

Java:
    roughly known
    some professional experience
    but intentionally reset to "basic Java" for this learning journey

React:
    not known deeply
    AI-generated implementation exists
    only learn enough to understand and modify what is necessary

ASP.NET Core:
    not known deeply
    existing system is the reference implementation

Architecture:
    already designed at a high level with AI assistance
    now needs to be understood through implementation

AI:
    strong interest
    target is AI engineering, not ML model training
```

Therefore the project should never begin with:

```text
"Understand all 29 tables"
"Understand all services"
"Understand Spring Security"
"Understand Spring AI"
"Understand RAG"
"Understand Docker execution"
```

all at once.

Instead:

```text
HTML
  ↓
React page
  ↓
HTTP request
  ↓
Spring Boot controller
  ↓
service
  ↓
repository
  ↓
PostgreSQL
  ↓
response
```

is learned first.

Then:

```text
login
  ↓
identity
  ↓
session
  ↓
authorization
  ↓
user-specific data
```

Then:

```text
content hierarchy
  ↓
progress
  ↓
exercises
  ↓
code execution
```

Then:

```text
AI gateway
  ↓
tutor
  ↓
conversation
  ↓
RAG
  ↓
support
  ↓
administration
```

Then:

```text
production architecture
  ↓
migration
  ↓
localization platform
```

---

# 3. The Learning Philosophy

## 3.1 No traditional video-course progression

Do **not** structure the learning around:

```text
Java Lesson 1
Java Lesson 2
Java Lesson 3
Spring Lesson 1
Spring Lesson 2
...
```

That is not the desired learning model.

Instead:

```text
Real feature requirement
        ↓
What does this feature require?
        ↓
Learn only that concept
        ↓
Implement a tiny version
        ↓
Test it
        ↓
Understand why it works
        ↓
Use it in NeuralAscent
        ↓
Increase complexity
```

This is deliberately **problem-driven learning**.

---

## 3.2 AI is the implementation assistant, not the teacher that replaces understanding

Claude, Gemini, ChatGPT, IDE assistants, etc. can still be used heavily.

But their role changes.

Bad workflow:

```text
"Build Spring Security login for me."

AI generates 2,000 lines.

Copy.

Run.

Move on.
```

Desired workflow:

```text
"I need login."

AI explains:
    Browser
        ↓
    POST /login
        ↓
    authentication manager
        ↓
    user lookup
        ↓
    password verification
        ↓
    session/cookie
        ↓
    authenticated request

Then:

    generate the smallest implementation

Then:

    inspect every class

Then:

    modify one thing manually

Then:

    write/test one failure case

Then:

    move to the next layer
```

AI accelerates the **typing and exploration**.

You must retain the **mental model**.

---

# 4. The Three Versions of the Project

The same project should be understood as three progressively deeper systems.

## Version A — Learning Version

Purpose:

> Teach Java/Spring/backend fundamentals.

Characteristics:

- very small number of tables;
- very few endpoints;
- no premature abstraction;
- no RAG;
- no microservices;
- no complicated authentication initially;
- no production-grade orchestration initially.

---

## Version B — Migration Version

Purpose:

> Recreate the behavior of the existing .NET system.

Characteristics:

- progressively introduce real entities;
- reproduce real APIs;
- reproduce real curriculum behavior;
- migrate progress behavior;
- migrate exercise execution;
- migrate atlas/knowledge relationships;
- reproduce operational behavior.

The .NET application becomes a **reference implementation**.

It should not be copied blindly.

For every migrated component ask:

```text
What does the .NET component do?

What input does it receive?

What state does it modify?

What database data does it read?

What error conditions exist?

What output does the frontend expect?

What invariants must remain true?

How should this behavior look in idiomatic Java/Spring?
```

---

## Version C — Evolution Version

Purpose:

> Add capabilities that make the project more advanced than the original .NET application.

These include:

- stronger identity;
- user isolation;
- AI gateway;
- quotas;
- token accounting;
- cost control;
- conversation persistence;
- current-context tutoring;
- support assistant;
- admin operations;
- RAG;
- pgvector;
- evaluation;
- observability;
- safe cross-vertical retrieval;
- progressive solution disclosure;
- production hardening.

This is the point where the project becomes an AI-engineering portfolio system rather than merely a migration exercise.

---

# 5. Master Progression

The project should evolve approximately as follows:

```text
PHASE 0
Understand the existing application

        ↓

PHASE 1
"NeuralAscent" page

        ↓

PHASE 2
First Java REST API

        ↓

PHASE 3
First PostgreSQL table

        ↓

PHASE 4
Basic login/session

        ↓

PHASE 5
Java LLD chapters

        ↓

PHASE 6
Courses / modules / lessons

        ↓

PHASE 7
Users + progress

        ↓

PHASE 8
Exercises + code state

        ↓

PHASE 9
Docker Java execution

        ↓

PHASE 10
.NET feature parity

        ↓

PHASE 11
AI gateway

        ↓

PHASE 12
Current-context tutor

        ↓

PHASE 13
Conversation memory

        ↓

PHASE 14
Admin dashboard

        ↓

PHASE 15
Support assistant

        ↓

PHASE 16
pgvector + RAG

        ↓

PHASE 17
Knowledge graph / cross-vertical retrieval

        ↓

PHASE 18
Seeders / reconcilers / tooling

        ↓

PHASE 19
Observability / hardening / productionization

        ↓

PHASE 20
Strangler migration + .NET retirement

        ↓

PHASE 21
Localization practice system
```

Each phase should produce a usable increment.

---

# 6. Phase 0 — Understand What Already Exists

## Goal

Before rebuilding anything, understand the current product as a **user and a backend system**.

Do not attempt to understand every implementation detail.

### Tasks

Create:

```text
docs/learning/current-system-map.md
```

Document:

```text
Frontend
    ↓
routes
    ↓
API calls
    ↓
backend endpoints
    ↓
services
    ↓
database
```

Create a very simple table:

| Feature | Frontend page | API | Backend responsibility | Database |
|---|---|---|---|---|
| Chapters | Chapters page | chapter APIs | chapter/content retrieval | curriculum tables |
| Progress | lesson/exercise UI | progress APIs | completion state | learner progress |
| Exercise | exercise UI | execution APIs | code execution | exercise data |
| Knowledge Atlas | atlas UI | atlas APIs | graph traversal | atlas tables |

Do not worry about every class yet.

### Learning outcome

You should be able to explain:

> "When I click this button in the browser, this request eventually reaches this backend code and this database data."

That is the first real skill.

---

# 7. Phase 1 — The Smallest Possible Website

## Goal

Build the first website completely independently of the large existing application.

Target:

```text
+-----------------------------+
| NeuralAscent                |
+-----------------------------+
| Welcome to NeuralAscent     |
|                             |
| My first Java/Spring page   |
+-----------------------------+
```

Frontend:

```text
React/Vite
```

Backend:

```text
Spring Boot
```

### First React objectives

Only learn:

- component;
- JSX;
- props;
- state concept;
- event handler;
- API call;
- basic routing;
- rendering a list.

Do not learn advanced React architecture yet.

### First Spring objectives

Learn:

- `@SpringBootApplication`;
- `main`;
- controller;
- `@GetMapping`;
- request/response;
- service;
- dependency injection at a basic level.

First endpoint:

```http
GET /api/hello
```

Response:

```json
{
  "message": "Hello from NeuralAscent"
}
```

### Success condition

You understand:

```text
React component
      ↓
fetch()
      ↓
HTTP
      ↓
Spring Controller
      ↓
JSON
      ↓
React renders response
```

---

# 8. Phase 2 — First Database Connection

## Goal

Make the system persistent.

Create the smallest possible table:

```text
lesson
```

with perhaps:

```text
id
title
slug
```

Do not initially create all 29 tables.

### Learn

- PostgreSQL;
- JDBC concept;
- Spring Data;
- entity;
- repository;
- service;
- database transaction concept;
- migrations.

Preferred tooling:

```text
Spring Boot
Spring Data JPA
PostgreSQL
Flyway
```

### Endpoint

```http
GET /api/lessons
GET /api/lessons/{id}
```

### Success condition

You understand this chain:

```text
HTTP
 ↓
Controller
 ↓
Service
 ↓
Repository
 ↓
JPA/Hibernate
 ↓
PostgreSQL
```

---

# 9. Phase 3 — Basic Login

## Goal

Introduce users without immediately building enterprise identity infrastructure.

First create:

```text
app_user
```

Fields:

```text
id
email
display_name
password_hash
```

Create:

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

Initially learn:

- password hashing;
- authentication;
- session concept;
- cookies;
- authenticated request;
- current user;
- logout.

Use Spring Security, but keep the first implementation extremely small.

### Important

This phase is about understanding:

```text
What is authentication?
```

not:

```text
What is every Spring Security feature?
```

### Later hardening

The full technical plan eventually requires:

- controlled registration;
- session lifecycle;
- account states;
- CSRF;
- invitation-based registration;
- role-based authorization;
- secure cookies;
- ownership validation.

Those belong later.

---

# 10. Phase 4 — Java LLD Chapters: The First Real Product

## Goal

Turn NeuralAscent into an actual learning site.

Start with only:

```text
Vertical
    ↓
Course
    ↓
Chapter
    ↓
Lesson
```

Initial seed:

```text
Java LLD
    ├── OOP
    ├── Interfaces
    ├── Inheritance
    ├── Polymorphism
    ├── Design Patterns
    └── SOLID
```

The first version can use a very small dataset.

### Frontend

Build:

```text
/chapter
/chapter/{slug}
/lesson/{slug}
```

### Backend

Build:

```http
GET /api/verticals
GET /api/courses
GET /api/chapters
GET /api/chapters/{slug}
GET /api/lessons/{id}
```

### Java concepts learned

- classes;
- constructors;
- interfaces;
- enums;
- collections;
- service classes;
- repository interfaces;
- DTOs;
- exceptions.

---

# 11. Phase 5 — Expand the Curriculum Hierarchy

Now gradually migrate the actual hierarchy.

Target:

```text
Vertical
    ↓
Course / Pathway
    ↓
Module / Chapter
    ↓
Lesson
    ↓
Exercise / Problem
    ↓
Resources
```

Do not move all data at once.

Suggested order:

```text
Java LLD
    ↓
FDE
    ↓
other verticals
```

This mirrors the way the platform will actually grow.

### Important learning rule

For every newly added entity:

1. understand the table;
2. understand the relationship;
3. create Java domain model;
4. create migration;
5. create repository;
6. create service;
7. create endpoint;
8. consume from React;
9. test;
10. seed a tiny dataset.

---

# 12. Phase 6 — User Progress

Now make the platform genuinely user-specific.

Introduce:

```text
learner_lesson_progress
learner_exercise_progress
```

Start simple:

```text
user
lesson
status
completed_at
```

Then add:

```text
started_at
updated_at
completion_source
```

Eventually introduce:

```text
attempt_count
highest_hint_level
solution_revealed
```

### Core endpoints

```http
GET  /api/me/progress
POST /api/lessons/{id}/complete
POST /api/lessons/{id}/reopen
GET  /api/exercises/{id}/progress
```

### Learning objectives

This phase teaches:

- authenticated user context;
- ownership;
- transactions;
- concurrency;
- idempotent operations;
- database constraints.

This is where the backend begins to resemble a real application.

---

# 13. Phase 7 — Exercises and Code State

Now introduce the learning exercises.

An exercise should eventually have:

```text
Exercise
 ├── instructions
 ├── objectives
 ├── constraints
 ├── starter files
 ├── learner code
 ├── tests
 ├── hints
 └── solution policy
```

But introduce them gradually.

First:

```text
exercise
exercise_file
```

Then:

```text
learner_code_snapshot
```

Then:

```text
compiler/test results
```

### Frontend

Introduce:

- code editor;
- selected file;
- selected code;
- save;
- run;
- result display.

You do not need deep React knowledge.

You need enough understanding to know:

```text
Editor
   ↓
selected code
   ↓
POST /run
   ↓
backend
   ↓
executor
   ↓
result
   ↓
UI
```

---

# 14. Phase 8 — Docker Java Execution Sandbox

This is an important transition from CRUD into systems engineering.

The target subsystem is conceptually:

```text
Browser
  ↓
API
  ↓
Exercise Runner
  ↓
Workspace Builder
  ↓
Docker Container
  ↓
Maven
  ↓
Surefire / test output
  ↓
Parser
  ↓
Normalized result
  ↓
Browser
```

First implement only:

```text
POST /api/exercises/{id}/run
```

with a controlled Java project.

Then introduce:

- workspace isolation;
- execution timeout;
- bounded resources;
- concurrency limiter;
- output size limit;
- test-result parsing;
- cleanup.

### Critical learning boundary

Never jump immediately into "secure arbitrary code execution".

First understand:

```text
How does a backend launch a process?
How does it provide files?
How does Docker isolate the process?
How do we capture output?
How do we stop it?
```

Security hardening comes after basic comprehension.

---

# 15. Phase 9 — Knowledge Atlas and Learning Graph

Now introduce the more complex knowledge model.

Conceptually:

```text
Knowledge Domain
      ↓
Knowledge Concept
      ↓
Concept Connections
      ↓
Prerequisites
      ↓
Next Lessons
      ↓
Reading Map
```

The system can eventually answer:

```text
"What should I learn before Strategy Pattern?"

"Which concepts lead into Dependency Injection?"

"What lesson teaches this concept?"

"What should I learn next?"
```

This is a good point to learn:

- graph-like relationships in relational databases;
- recursive queries;
- joins;
- traversal;
- indexing;
- data modeling.

Do not introduce a graph database merely because the data is graph-shaped.

Understand the relational representation first.

---

# 16. Phase 10 — Reach Functional Parity With the .NET Application

At this stage stop adding major new features.

Your objective becomes:

> The Java implementation should reproduce the important observable behavior of the .NET application.

Build an explicit parity matrix.

Example:

| Capability | .NET | Java | Status |
|---|---:|---:|---|
| Health | ✅ | ✅ | parity |
| Chapters | ✅ | ✅ | parity |
| Lessons | ✅ | ✅ | parity |
| Progress | ✅ | ✅ | parity |
| Exercises | ✅ | ✅ | parity |
| Docker runner | ✅ | ✅ | parity |
| Knowledge Atlas | ✅ | ✅ | parity |
| Reading map | ✅ | ✅ | parity |
| Seeding | ✅ | pending | migrate later |
| Reconcilers | ✅ | pending | migrate later |

Do not declare parity because endpoints exist.

Verify behavior.

---

# 17. How to Compare .NET and Java During Migration

For each component:

```text
.NET implementation
       ↓
Behavior inventory
       ↓
Contract
       ↓
Java design
       ↓
Java implementation
       ↓
Comparison tests
```

Capture:

```text
Input
Expected result
Side effects
Database state
Error behavior
HTTP status
Response shape
```

The .NET project is therefore a **living specification**.

This also allows you to learn Java by asking:

> "How would I express this behavior in Java?"

instead of asking:

> "How do I learn Java in general?"

---

# 18. Phase 11 — Refactor Toward the Target Java Architecture

Only after you understand the system should you move toward the modular target.

Suggested structure:

```text
com.neuralascent
├── identity
├── authorization
├── curriculum
├── progress
├── exercises
├── execution
├── knowledge
├── conversation
├── tutor
├── support
├── ai.gateway
├── retrieval
├── administration
├── observability
└── shared
```

The exact package structure can evolve.

The important principle is:

> Organize by business capability rather than creating a giant controller/service/repository bucket.

---

# 19. Phase 12 — AI Gateway Before AI Tutor

Do not start with:

```text
POST /chat
```

that directly calls an LLM.

First build:

```text
TutorService
      ↓
AI Gateway
      ↓
Provider adapter
      ↓
LLM
```

Create internal contracts such as:

```java
AiChatRequest
AiChatResponse
AiUsage
AiModel
AiProvider
```

The application should not depend everywhere on provider-specific JSON.

### Why?

Because later you may switch:

```text
Provider A
    ↓
Provider B
    ↓
Provider C
```

without rewriting the tutor domain.

---

# 20. Phase 13 — First Current-Context Tutor

The first tutor should **not use RAG**.

The browser already knows:

```text
lesson
exercise
selected code
current code
compiler errors
failed tests
```

The backend should receive identifiers and learner-generated state.

Then:

```text
Chat request
   ↓
Authentication
   ↓
Authorization
   ↓
Context Resolver
   ↓
Current lesson/exercise
   ↓
Prompt Builder
   ↓
AI Gateway
   ↓
Structured Tutor Response
   ↓
Validation
   ↓
Browser
```

This is the most important first AI architecture.

The existing architecture explicitly prefers exact context before retrieval. That principle should remain unchanged.

---

# 21. Phase 14 — Progressive Tutoring

Do not initially make the bot a solution generator.

Implement:

```text
Level 1
Guiding question

Level 2
Responsibility / design hint

Level 3
Pseudocode

Level 4
Partial implementation

Level 5
Full solution
```

Persist:

```text
highest_hint_level
```

and enforce escalation on the server.

The model should never be trusted to decide:

```text
"the learner is allowed to see the solution."
```

The backend decides that.

This establishes an important AI engineering principle:

> LLM output is not authorization.

---

# 22. Phase 15 — Conversation Persistence

Now add:

```text
chat_conversation
chat_message
conversation_summary
```

Teach:

- conversation ownership;
- bounded history;
- idempotent client request IDs;
- streaming;
- cancellation;
- message persistence;
- summary generation.

Memory should be:

```text
recent messages
+
summary
+
previous hints
+
current lesson
+
current exercise
+
learner state
```

Not:

```text
entire conversation forever
```

This matters for both quality and cost.

---

# 23. Phase 16 — AI Cost and Usage Management

Before exposing the tutor publicly, build the AI admission layer.

The desired pipeline is:

```text
Authenticate
    ↓
Account status
    ↓
Authorization
    ↓
Ownership
    ↓
Payload validation
    ↓
Rate limiting
    ↓
Concurrency limit
    ↓
Token estimate
    ↓
User quota
    ↓
Global budget
    ↓
Idempotency
    ↓
Reserve usage
    ↓
Provider call
    ↓
Actual usage
    ↓
Reconciliation
```

Track:

```text
input tokens
output tokens
reasoning tokens where available
total tokens
latency
provider
model
operation
estimated cost
actual cost
```

This phase changes the AI feature from:

```text
"LLM API call"
```

into:

```text
"AI platform capability"
```

---

# 24. Phase 17 — Admin AI Operations Dashboard

Build a minimal administrative dashboard.

Initial capabilities:

```text
AI requests today
Token usage
Estimated spend
Failures
P50/P95 latency
Active streams
Top users
Current quotas
AI kill switch
```

Then add:

```text
Invocation explorer
Quota controls
Model configuration
Operational settings
Audit trail
```

This provides excellent practice in:

- role-based access;
- administrative APIs;
- aggregation queries;
- metrics;
- operational tooling.

---

# 25. Phase 18 — Support Assistant

Create a separate AI boundary.

Do not make the tutor also behave as unrestricted customer support.

Target:

```text
SUPPORT_ASSISTANT
```

with:

- separate prompt;
- separate permissions;
- separate quota;
- separate retrieval scope;
- separate conversation type.

Introduce tickets:

```text
OPEN
  ↓
TRIAGED
  ↓
IN_PROGRESS
  ↓
WAITING_FOR_USER
  ↓
RESOLVED
  ↓
CLOSED
```

The LLM may:

```text
summarize
classify
draft
suggest
```

but the application performs:

```text
ticket creation
status changes
assignment
user suspension
```

This teaches an important architecture principle:

> Models may recommend actions; typed backend commands perform authorized mutations.

---

# 26. Phase 19 — pgvector and RAG

Only now introduce RAG.

The first RAG use case should be very simple:

```text
Learner asks about a previous Java LLD concept.
```

Pipeline:

```text
Question
  ↓
Route
  ↓
Search current vertical
  ↓
Metadata filter
  ↓
Vector search
  ↓
Optional full-text search
  ↓
Rank
  ↓
Evidence
  ↓
Prompt
  ↓
Tutor
```

Metadata should include things such as:

```text
vertical
course
chapter
lesson
exercise
content_type
visibility
lesson_sequence
solution flag
future access policy
version
embedding version
```

The system must filter authorization **before** accepting the evidence.

---

# 27. Phase 20 — Route Policy

Initially use deterministic rules.

Example:

```text
Current code / current exercise
    → CURRENT_CONTEXT

Previous lesson / prerequisite
    → CURRENT_VERTICAL_RAG

Another registered vertical
    → CROSS_VERTICAL_RAG

Generic Java question
    → GENERAL_KNOWLEDGE

Unclear "this/that/the previous one"
    → CLARIFY
```

Do not immediately build a second LLM just to decide which LLM path to use.

Collect real requests first.

Then evaluate whether a small router is justified.

This gives you a real engineering story:

```text
Rules
  ↓
evaluation data
  ↓
measured failure cases
  ↓
optional small router
```

rather than:

```text
"I used an agent because agents are cool."
```

---

# 28. Phase 21 — Cross-Vertical Learning

Now the site becomes a real learning platform.

Example:

```text
Java LLD learner

asks:

"Is this similar to dependency injection in Spring?"
```

The system can do:

```text
Current context
      +
Java LLD evidence
      +
Spring/FDE retrieval
      +
permission policy
```

The learner should never gain access to an entire restricted vertical merely because the AI can search it.

The application decides:

```text
Is this vertical allowed?
Which lessons are visible?
Are future concepts allowed?
Are solutions allowed?
```

---

# 29. Phase 22 — Engagement and Completion

Introduce learning telemetry only after the core system works.

Possible events:

```text
lesson_opened
content_visible
active_reading_heartbeat
bottom_reached
section_reached
mcq_attempted
exercise_opened
exercise_compiled
exercise_tested
exercise_completed
```

Do not send every scroll event.

Aggregate.

Then implement server-side completion rules.

For example:

```json
{
  "required": [
    "BOTTOM_REACHED"
  ],
  "minimumActiveSeconds": 180,
  "mandatoryMcqCompletionRatio": 1.0,
  "exerciseCompletionRequired": false
}
```

The LLM should never directly complete a lesson.

---

# 30. Phase 23 — Seeders and Reconciliation Engines

Only after the runtime platform is understandable should you move the tooling.

This includes:

```text
seed
migrate
reconcile
```

and domain-specific reconcilers such as:

```text
Java reconciler
FDE reconciler
Azure Labs reconciler
Atlas / reading-map reconciler
```

The goal is to understand:

```text
source curriculum
      ↓
normalization
      ↓
comparison
      ↓
desired database state
      ↓
reconciliation
```

This is a very important backend concept.

It teaches:

- idempotency;
- deterministic state;
- synchronization;
- data validation;
- versioning;
- batch processing.

---

# 31. Phase 24 — Production Engineering

Now take the system from:

```text
"works locally"
```

to:

```text
"behaves predictably under failure"
```

Add:

- structured logging;
- correlation IDs;
- metrics;
- tracing;
- health checks;
- timeouts;
- retries;
- circuit breakers;
- idempotency;
- concurrency control;
- transaction boundaries;
- audit events;
- security events.

Use OpenTelemetry concepts.

Observe:

```text
HTTP request
    ↓
service
    ↓
database
    ↓
AI provider
```

through one trace.

---

# 32. Phase 25 — Security Hardening

Build threat models around actual features.

Test:

```text
User A
  ↓
tries User B conversation

User A
  ↓
tries User B progress

User A
  ↓
changes lessonId

User A
  ↓
tries restricted vertical

User A
  ↓
tries future exercise

User A
  ↓
tries solution endpoint

Browser
  ↓
tries to obtain AI key
```

Also test:

```text
prompt injection from learner code
prompt injection from retrieved curriculum
```

Security checks must happen outside the LLM.

---

# 33. Phase 26 — Full .NET → Java Migration Strategy

Now that the Java system is mature, move toward a true migration architecture.

The migration principle should be:

```text
Existing .NET
      +
New Java
      ↓
Strangler pattern
      ↓
route selected capability
      ↓
Java
      ↓
verify parity
      ↓
retire .NET capability
```

Do not rewrite everything in one giant operation.

---

# 34. Migration Order

Recommended order:

```text
1. Authentication / identity
2. Basic curriculum reads
3. Lesson/chapter APIs
4. Progress
5. Exercise APIs
6. Docker execution
7. Knowledge Atlas
8. Reading maps
9. Conversations
10. AI gateway
11. Support
12. Admin
13. Seeders
14. Reconcilers
15. remaining utilities
```

Tooling and operational components can be migrated after the runtime system is stable, provided the existing .NET tooling remains available during the transition.

---

# 35. Contract-First Migration

Before cutting over major routes:

freeze:

```text
HTTP paths
HTTP methods
request schema
response schema
error schema
status codes
streaming protocol
authentication expectations
```

Generate OpenAPI documentation.

Create contract tests.

Then both:

```text
.NET
Java
```

must satisfy the same contract.

This turns migration from:

```text
"rewrite it and hope"
```

into:

```text
"two implementations of one contract"
```

---

# 36. Parity Testing

For a given request:

```text
Input
  ↓
.NET
  ↓
expected result

Input
  ↓
Java
  ↓
candidate result
```

Compare:

```text
HTTP status
headers where relevant
response structure
business semantics
database state
side effects
error behavior
```

For deterministic APIs, automated differential testing is strongly preferred.

---

# 37. Phase 27 — Decommission .NET

Do not delete .NET because:

```text
"The Java version seems to work."
```

Retire a subsystem only after:

```text
contract parity
+
integration tests
+
production metrics
+
rollback plan
+
database ownership validation
+
traffic verification
```

Then:

```text
.NET route
   ↓
0% traffic
   ↓
monitor
   ↓
archive
   ↓
remove
```

---

# 38. Phase 28 — Advanced Java Learning Track Embedded in the Project

Java concepts should appear naturally as the platform grows.

Suggested sequence:

| Project phase | Java focus |
|---|---|
| Tiny API | classes, methods, constructors |
| Services | interfaces, dependency injection |
| Persistence | generics, collections, exceptions |
| Authorization | enums, predicates, streams |
| Transactions | exceptions, transactional thinking |
| Exercises | records, DTOs |
| Execution | processes, concurrency |
| Conversations | concurrency, immutability |
| AI gateway | interfaces, polymorphism |
| Routing | sealed types / strategy patterns where useful |
| RAG | collections, functional transformations |
| Observability | structured data and abstraction |
| Migration | API contracts, versioning |
| Optimization | profiling, JVM behavior |

Do not force every Java feature into the project.

A feature should be introduced because the project creates a genuine reason for it.

---

# 39. Phase 29 — React Learning Scope

React is not the primary career focus.

Therefore the learning target is:

> Become comfortable enough to maintain and integrate a React frontend with a Java backend.

Learn:

```text
component
props
state
event
effect
API calls
routing
forms
conditional rendering
list rendering
loading states
error states
basic context/state management
```

Later understand:

```text
authentication state
editor state
PageContext
chat streaming
admin tables
support UI
```

You do not need to become a React framework expert unless your career direction changes.

---

# 40. The Special Rule for AI-Generated Code

Every major AI-generated feature must pass this process:

```text
1. Ask AI to create smallest implementation.

2. Read every file.

3. Ask AI to explain the control flow.

4. Identify:
       input
       state
       dependencies
       side effects
       failure modes

5. Change one thing manually.

6. Break it intentionally.

7. Fix it.

8. Add a test.

9. Commit.

10. Continue.
```

Maintain:

```text
docs/learning/
```

with entries such as:

```text
why-this-controller-exists.md
why-transaction-is-here.md
why-session-is-server-side.md
why-rag-is-not-used-here.md
why-this-query-is-authorized.md
```

These notes become your actual learning record.

---

# 41. Commit Strategy

Do not make:

```text
Day 1: huge commit
```

Instead use commits that represent concepts:

```text
feat: add spring boot hello endpoint
feat: render hello response in react
feat: add lesson entity
feat: add lesson repository
feat: add lesson query service
feat: add chapter list page
feat: add user registration
feat: add session login
test: cover lesson ownership
```

A future reviewer should be able to see the evolution of your understanding.

---

# 42. The "One New Difficulty at a Time" Rule

A common failure mode would be:

```text
New Java backend
+
Spring Security
+
PostgreSQL
+
Redis
+
Kafka
+
RAG
+
Docker
+
JWT
+
React
```

all at once.

Do not do this.

Instead:

```text
New page
      ↓
New endpoint
      ↓
New database concept
      ↓
New security concept
      ↓
New distributed concept
      ↓
New AI concept
```

Every phase should have **one primary new difficulty**.

---

# 43. Phase Completion Checklist

Never mark a phase complete simply because the code runs.

Each phase should answer:

### Can I explain it?

If someone asks:

> "What happens when this request arrives?"

you should be able to answer.

### Can I modify it?

You should be able to make a small change without asking AI to rewrite the entire feature.

### Can I debug it?

You should know where to put logs/breakpoints and how to trace the request.

### Can I break it?

You should know at least one meaningful failure mode.

### Can I test it?

You should have at least one automated test for important behavior.

### Can I compare it with .NET?

For migrated components, you should know whether Java preserves the required behavior.

---

# 44. Recommended Learning Checkpoints

After the first basic phases:

```text
Checkpoint A

I can build:
React → Spring → PostgreSQL
without blindly copying code.
```

After curriculum:

```text
Checkpoint B

I can design:
entities
repositories
services
controllers
DTOs
transactions
```

After auth/progress:

```text
Checkpoint C

I understand:
authentication
authorization
ownership
sessions
user-scoped data
```

After exercise runner:

```text
Checkpoint D

I understand:
process execution
Docker
timeouts
concurrency
result parsing
```

After AI tutor:

```text
Checkpoint E

I understand:
AI gateway
prompt assembly
structured output
streaming
cost control
```

After RAG:

```text
Checkpoint F

I understand:
embeddings
vector search
metadata filtering
retrieval policy
grounding
evaluation
```

After migration:

```text
Checkpoint G

I can explain:
.NET → Java migration
contract compatibility
strangler pattern
parity testing
incremental cutover
```

---

# 45. The Final NeuralAscent Architecture

At the end of this learning journey, the conceptual platform should look approximately like:

```text
                         React / Vite
                              |
                              v
                       Spring Boot API
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
   Identity             Curriculum             Progress
        |                     |                     |
        v                     v                     v
 Authorization          Knowledge            Exercises
        |                   Atlas                 |
        |                     |                   v
        |                     |              Docker Runner
        |                     |
        +----------+----------+
                   |
                   v
             AI Gateway
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
     Tutor      Support     Other AI
       |
       v
   Context Resolver
       |
       +--------+
       |        |
       v        v
 Current     RAG
 Context      |
       |       v
       |   pgvector
       |       |
       +---+---+
           |
           v
        LLM Provider

Admin / Operations
       |
       +--> usage
       +--> cost
       +--> quotas
       +--> audit
       +--> support
       +--> AI controls

Tooling
       |
       +--> seeders
       +--> reconcilers
       +--> content ingestion
       +--> evaluation
```

---

# 46. Final Learning Outcome

The goal is not:

> "I converted a .NET application to Java."

The stronger outcome is:

> "I started with basic Java knowledge, understood an AI-generated React/.NET learning platform from the outside in, rebuilt it incrementally in Java and Spring Boot, reproduced its core behavior, introduced secure multi-user architecture, built an AI gateway and context-aware tutor, implemented cost governance, conversation and support workflows, added metadata-filtered RAG, introduced observability and production safeguards, and finally migrated the platform toward a Java-first architecture."

That story is much more valuable because it demonstrates **understanding**, not merely code generation.

---

# 47. Final Project: Unity Localization Practice System

Once NeuralAscent is mature, build a second system inspired by the localization engineering work from your professional history.

The professional context describes work on a Unity Localization solution involving backend/service integration, automated translation, machine translation, later AI/LLM translation, translation cost/credit handling, production support, testing, and enterprise workflows. The retained project dossier explicitly distinguishes confirmed experience from reconstructed architecture, so the personal practice implementation must remain a **new system inspired by the domain**, not a reconstruction of confidential Unity internals. 

Relevant engineering concepts from that experience include:

```text
source strings
      ↓
change detection
      ↓
translation job
      ↓
provider abstraction
      ↓
machine translation / LLM
      ↓
usage / cost estimation
      ↓
translation result
      ↓
review / approval
      ↓
build artifact
```

The practice system can therefore become:

```text
Localization Project
   ↓
Locales
   ↓
String resources
   ↓
Translation jobs
   ↓
Provider abstraction
   ├── conventional MT
   └── AI/LLM
   ↓
Cost estimator
   ↓
Review workflow
   ↓
Approval
   ↓
Export
   ↓
Build package
```

Then progressively introduce:

```text
batch processing
provider adapters
pricing strategies
async jobs
idempotency
retry handling
quality checks
translation memory
terminology
AI context
RAG
admin operations
audit
```

This becomes the **advanced capstone** after NeuralAscent.

---

# 48. Localization Capstone Learning Mapping

The capstone should deliberately reuse concepts learned in NeuralAscent.

| NeuralAscent learning | Localization capstone reuse |
|---|---|
| User identity | customer/project identity |
| Authorization | project/locale permissions |
| PostgreSQL | localization data |
| Transactions | translation job state |
| Idempotency | duplicate translation requests |
| AI gateway | translation provider gateway |
| Cost tracking | translation credits |
| RAG | terminology/context retrieval |
| Background jobs | large translation batches |
| Admin dashboard | translation operations |
| Support tickets | translation failures |
| Observability | provider/job tracing |
| Docker | worker execution |
| Contract testing | provider adapter compatibility |
| Strangler migration | legacy localization migration |

This creates a deliberate progression:

```text
simple CRUD
    ↓
real backend
    ↓
enterprise backend
    ↓
AI backend
    ↓
distributed workflow
    ↓
domain-specific AI system
```

---

# 49. What "Starting From Scratch" Means in This Roadmap

"Starting from scratch" does **not** mean:

```text
forget all previous Java experience
```

It means:

```text
do not assume you understand the modern Java/Spring stack
just because you have professional Java experience.
```

You will deliberately rebuild your mental model of:

```text
Java
↓
Spring
↓
Spring Boot
↓
Web
↓
Persistence
↓
Security
↓
Concurrency
↓
Distributed behavior
↓
AI engineering
```

The advantage is that every concept is tied to something you are actually building.

---

# 50. What Not To Do

Do not:

```text
❌ rewrite all 29 entities on Day 1
❌ copy .NET classes line by line
❌ introduce microservices immediately
❌ introduce Kafka because it looks enterprise
❌ add an LLM router before real data exists
❌ use RAG for current-context questions
❌ put provider keys in React
❌ trust model output for authorization
❌ let the browser define user permissions
❌ build admin tooling before the underlying feature works
❌ optimize infrastructure before measuring it
❌ learn every React feature
❌ learn every Spring feature
❌ use AI-generated code without understanding the flow
```

Instead:

```text
✅ build a tiny thing
✅ understand it
✅ test it
✅ expand it
✅ compare with .NET
✅ refactor only when justified
```

---

# 51. Recommended Repository Learning Structure

Add a dedicated learning area:

```text
docs/
├── architecture/
│   ├── current-system-inventory.md
│   ├── target-java-architecture.md
│   ├── migration-strategy.md
│   ├── ai-provider-decision.md
│   └── security-model.md
│
├── learning/
│   ├── phase-01-web-basics.md
│   ├── phase-02-spring-basics.md
│   ├── phase-03-persistence.md
│   ├── phase-04-authentication.md
│   ├── phase-05-curriculum.md
│   ├── phase-06-progress.md
│   ├── phase-07-exercises.md
│   ├── phase-08-docker-runner.md
│   ├── phase-09-knowledge-atlas.md
│   ├── phase-10-net-parity.md
│   ├── phase-11-ai-gateway.md
│   ├── phase-12-tutor.md
│   ├── phase-13-conversations.md
│   ├── phase-14-admin.md
│   ├── phase-15-support.md
│   ├── phase-16-rag.md
│   ├── phase-17-routing.md
│   ├── phase-18-reconcilers.md
│   └── phase-19-production.md
│
├── migration/
│   ├── parity-matrix.md
│   ├── api-contracts.md
│   └── cutover-plan.md
│
└── experiments/
    ├── java/
    ├── spring/
    ├── ai/
    └── postgres/
```

This keeps your learning history independent of the application implementation.

---

# 52. A Practical Rule for Every New Feature

Before implementing:

```text
What problem does this solve?
```

Then:

```text
What is the smallest version?
```

Then:

```text
Which Java/Spring concept does this teach?
```

Then:

```text
What does the browser send?
```

Then:

```text
What does the server trust?
```

Then:

```text
What database state changes?
```

Then:

```text
What can fail?
```

Then:

```text
How do I test it?
```

Only after that:

```text
Can this be made more production-grade?
```

---

# 53. Final End-State Roadmap

The complete journey is:

```text
START
  |
  |  Existing AI-generated product
  v
Understand the product
  |
  v
Tiny React + Spring Boot
  |
  v
Simple PostgreSQL
  |
  v
Basic authentication
  |
  v
Java LLD curriculum
  |
  v
FDE + additional verticals
  |
  v
User progress
  |
  v
Exercises
  |
  v
Docker Java execution
  |
  v
Knowledge Atlas
  |
  v
.NET behavioral parity
  |
  v
Spring architecture refinement
  |
  v
AI Gateway
  |
  v
Context Tutor
  |
  v
Conversation Memory
  |
  v
Cost / Quotas
  |
  v
Admin Operations
  |
  v
Support Assistant
  |
  v
RAG / pgvector
  |
  v
Cross-vertical retrieval
  |
  v
Evaluation
  |
  v
Seeders / Reconcilers
  |
  v
Observability / Security
  |
  v
Strangler Migration
  |
  v
.NET Retirement
  |
  v
LOCALIZATION CAPSTONE
  |
  v
Advanced AI + workflow platform
  |
  v
END
```

---

# 54. The Real Goal

The final target is not simply a GitHub repository that says:

```text
"Java version of NeuralAscent"
```

The real target is that, after completing this journey, you can look at a system and reason about it from first principles:

```text
UI
 ↓
API
 ↓
Domain
 ↓
Persistence
 ↓
Security
 ↓
Concurrency
 ↓
Infrastructure
 ↓
External services
 ↓
AI
 ↓
Observability
 ↓
Operations
```

and ask:

```text
What does this component do?

Why is it here?

What does it trust?

What can fail?

What state does it own?

How is it tested?

How would I migrate it?

How would I scale it?

How would I make an AI system safe around it?
```

That is the capability this roadmap is designed to build.
