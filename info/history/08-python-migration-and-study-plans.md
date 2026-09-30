# 08 — Python Backend Migration (formerly "Java migration") + Study Plans & Trackers

> Consolidated 2026-09-30. Part A = the backend migration plan, **presented as a Python migration**. Part B = interview/cert/study plans and
> trackers (`info/01…04`, curriculum modernization, Azure plan, labs). Originals are recoverable from git at commit `9e6d03f`.

---

# PART A — Python Backend Migration

## A.0 Provenance & terminology (read first)

- The source documents (`info/java_aws_migration_tracker.md`, `info/.notes/Chatbot-implementation/java-migration/**`, the "Phase 12 Java/Spring Boot and Spring AI"
  section of the AI platform TODO tracker, the Java-first rebuild roadmap, the 12-sprint and 85-/30-day learning plans, the "Java reimplementation blueprint" and the
  `study-tracker-webpage-redesign` "Target Migration Stack: Java 21 / Spring Boot 3 (`api-java`)" line) all described the long-term backend target as
  **Java 21 + Spring Boot 3 (+ Spring AI)**, replacing ASP.NET Core.
- **Decision recorded 2026-09-30 (user directive during this consolidation):** present the backend migration as a **Python migration** — FastAPI +
  Pydantic v2 + Pydantic AI + LangGraph (the stack of the AI Learning Agent, `07-ai-learning-agent.md`) — instead of Java/Spring. This matches the
  already-locked 2026-09-08 architecture decision (staged cutover of `neuralascent.top` from .NET to the FastAPI stack in Phase 3.9) and the fact that
  the only backend code actually being written for the "new stack" is `ai-agent/` (Python).
- **What did NOT change:** the *Java LLD / Spring curriculum* (course content about Java) stays Java. Exercises still compile and run Java in
  Maven/JDK Docker runners (`runner/java*`). Only the *platform backend implementation language* changes from "Java (planned)" to "Python".
- Terms in old docs → meaning here: "Java migration", "Java-first rebuild", "Java/Spring migration", "`api-java`", "Spring AI gateway" ⇒ Python migration,
  new Python API service, Python AI gateway. "Java LLD", "Java exercises", "Spring Boot sandbox runner" ⇒ unchanged (curriculum/exercise content).
- Not the same thing (do not confuse): the **redesign data migration** (old StudyVertical/StudyTask dashboard → canonical Course/Module/Lesson, Aug 2026) and the
  **platform/AWS migration plan** (single EC2 → ECS/RDS) in `03-website-redesign-and-platform-migration.md`; and the "Java reconciliation pilot" (PHASE-3A), which migrates
  *Java-vertical curriculum rows*, not the backend language.
- Status of the Python migration: **planning only. Nothing beyond the `ai-agent/` scaffold exists.** No `api-java/` (or Python sibling) directory was ever created
  (verified 2026-09-30; `git ls-files` has no `api-java`). Naming of a possible successor to `api/` is undecided — most likely `ai-agent/` grows into it.
- **Conflict record:** on/around 2026-09-07 the "AI Copilot" planning session stated "explicitly decided against migrating the existing .NET backend to Python 'for the practice'
  (low interview value, high risk, HLD recommends modular monolith addition)". The 2026-09-08 architecture (staged cutover) came after and supersedes it for the *destination*;
  the caution about risk survives as the strangler/contract-first/parity rules below.

## A.1 Timeline of the migration idea

| Date | Event |
|---|---|
| 2026-08-07 | `java_aws_migration_tracker.md` created: "Phase 8 — Migration to Java (Spring Boot 3) & AWS". Source = ASP.NET Core (.NET 8/9) on Azure Container Apps/Static Web Apps; target = Java 21/Spring Boot 3 REST API on AWS (ECR + App Runner/ECS Fargate + S3/CloudFront). **Mentorship & Upskilling Mode**: the user hand-writes code with a local Qwen 2.5/3.5 35B autocomplete; the agent architects and reviews (also recorded in `.agents/memory/migration-plan.md`). Sub-task 8.1 scaffolding "started" (nothing landed). |
| 2026-08-28 (and late Aug) | Interactive-exercise blueprints and the local-LLM pipeline knowledge map state the backend rebuild is a **deliberate long-term learning goal, not started — "do not start it unprompted"**; .NET is the stable behavioural reference. |
| 2026-09-01 | Java-first rebuild roadmap (53 sections), TODO-tracker Phase 12, the 12-sprint learning plan, CLARITY scope doc, 30-day/85-day interview plans. |
| 2026-09-07 | AI Copilot planning: rejects .NET→Python rewrite "for practice" (see conflict record). |
| 2026-09-08 | AI Learning Agent architecture: fresh TS frontend + Python FastAPI, staged cutover, .NET retired or narrowed in Phase 3. |
| 2026-09-30 | Directive: present the migration as Python (this document). |

## A.2 The original tracker, restated for Python (`java_aws_migration_tracker.md`)

Strategy: source = ASP.NET Core minimal API; target = **Python 3.12 / FastAPI** service on AWS (today the real prod is a single EC2 host with GHCR images deployed via SSM; the
original ECR + App Runner/ECS Fargate + S3/CloudFront wording is the *aspirational* AWS target — see the platform migration plan in file 03). Execution: mentorship mode.

| Sub-task | Original (Java) | Python version | Status |
|---|---|---|---|
| 8.1 | Scaffold `api-java/`, Maven `pom.xml` (Java 21, Spring Boot 3.2+, Web, Data JPA, SQLite/PostgreSQL, Lombok), `application.yml` (DB, port 8080, CORS) | Scaffold the Python API package (`requirements.txt`/`pyproject`, FastAPI app, `config.py`, CORS, port), reuse `ai-agent/` conventions | `ai-agent/` scaffold exists (Dockerfile, FastAPI, config, health) — not the full API |
| 8.2 | JPA entities `StudyVertical`, `StudyTask` + `JpaRepository`s | Data access for the same tables (raw `psycopg` is what `ai-agent/db.py` uses today; SQLAlchemy is an open choice — the Python chatbot HLD suggested SQLAlchemy + Alembic) | Not started |
| 8.3 | DTOs (`VerticalResponseDto`, `TaskResponseDto`, `IngestPayloadDto`), `StudyService`, `DataSeeder` `CommandLineRunner` | Pydantic v2 models, service layer, seed/reconcile CLI modes equivalent to .NET's `--migrate` / `--seed-reference-data` / `--reconcile-content` | Not started |
| 8.4 | `@RestController`s + `ApiKeyFilter` for `x-api-key` | FastAPI routers + a dependency validating `x-api-key` (today's shared-key middleware) and the JWT (`auth.py` already validates the .NET-issued JWT) | JWT validation done; routers beyond `/health`,`/me` not started |
| 8.5 | Markdown ingestion parser + `POST /api/verticals/ingest` | Same parser as a Python service (the curriculum importer) | Not started |
| 8.6 | Multi-stage Dockerfile (Maven build → Temurin 21 JRE) + `api-java` in compose | `python:3.12-slim` Dockerfile (exists for `ai-agent`) + compose service | Done for `ai-agent` |
| 8.7 | AWS ECR repo, App Runner/ECS Fargate, S3 + CloudFront | Same AWS targets (see file 03 staged plan) | Not started; prod is single EC2 |
| 8.8 | GitHub Actions: AWS creds, ECR push, App Runner/ECS deploy; secrets `AWS_ACCESS_KEY_ID`… | Existing `deploy-api.yml` (GHCR + SSM) already builds/pushes the `ai-agent` image | Partly (image build/deploy exists; ECR/ECS not) |

Progress log: 2026-08-07 roadmap initialised; scaffolding for 8.1 started (no artefacts).

## A.3 Python target stack (mapping used by this consolidation — *proposed* except where marked "already in repo")

| Concern | .NET today | Original Java plan | Python target |
|---|---|---|---|
| HTTP/API | ASP.NET Core minimal APIs | Spring `@RestController` | **FastAPI routers** (already in repo) |
| DI | built-in DI | Spring DI | FastAPI `Depends` (already used: `get_current_user`) |
| Auth | JWT (HS256, issuer `neuralascent`, aud `neuralascent-app`, cookie `na_auth`), TOTP, PBKDF2 | Spring Security | PyJWT validation (already in repo); issuing/TOTP stays .NET until cutover, then port |
| Data access | EF Core + Npgsql | JPA/Hibernate, Flyway/Liquibase | `psycopg3` + pool (already in repo) — ORM choice open; migrations via `ai-agent/migrate.py` pattern (already in repo) or Alembic |
| Validation/DTO | records/DTOs | DTOs | **Pydantic v2** (already a dependency) |
| Middleware/errors | middleware, RFC 7807 | filters, `@ControllerAdvice` | FastAPI middleware / exception handlers |
| Tests | xUnit | JUnit + Spring testing | pytest (not yet present in `ai-agent/`) |
| AI gateway | `LlamaApiClient` + `BudgetGuardService` | Spring AI `ChatClient` selectively | **Pydantic AI `Agent`** (already in repo) + LangGraph orchestration; provider-neutral adapter still to build |
| Vector store | — | pgvector via Spring AI | **pgvector** (already in repo, `content_chunks`) |
| Streaming | SSE | SSE/reactive | SSE via FastAPI (not yet built) |
| Contracts | ad-hoc | OpenAPI + contract tests | FastAPI auto-OpenAPI + contract tests (must be shared with .NET side) |
| Deploy | GHCR + SSM + `docker run` | same → ECS | same; `ai-agent` image already in `deploy-api.yml` |

## A.4 Migration principles (carried over verbatim in spirit; language-neutral)

- **Learning vehicle, not a translation exercise.** The user asked for manual migration to understand the system, using the .NET app as the *behavioural reference*; do not ask an LLM to blindly
  translate the backend. (Now reinforced: `ai-agent/` is hand-written; Claude is architect/reviewer only.)
- **Three versions of the project:** A *Learning* (tiny slices: page → API → DB), B *Migration* (recreate .NET behaviour), C *Evolution* (identity, quotas, AI gateway, tutor, support, RAG, observability).
- **For each migrated component ask:** what does it do, inputs, state modified, DB reads, error conditions, output the frontend expects, invariants that must hold, and what is the idiomatic Python form.
- **Strangler pattern + contract-first:** freeze HTTP paths/methods/request/response/error schemas/status codes/streaming protocol/auth expectations; generate OpenAPI; contract tests run against **both** implementations;
  route one capability at a time at the reverse proxy; one authoritative DB schema with controlled ownership; migrate auth only with a documented session/token compatibility plan.
- **Parity testing:** same input to .NET and Python; compare status, relevant headers, response structure, business semantics, DB state, side effects, error behaviour. Prefer automated differential tests for deterministic APIs.
- **Decommission a .NET subsystem only after:** contract parity + integration tests + production metrics + rollback plan + DB ownership validated + traffic verified → route to 0% → monitor → archive → remove.
- **Migration order:** auth/identity → basic curriculum reads → lesson/chapter APIs → progress → exercise APIs → Docker execution → Knowledge Atlas → reading maps → conversations → AI gateway → support → admin → seeders → reconcilers → remaining utilities (tooling can lag as long as .NET tooling stays available).
- **Keep prompts and schemas as data:** `TutorContext` and the `emit_tutor_response` schema as standalone versioned JSON Schema files; tutor/support system prompts as files/DB rows by version; pgvector schema and chunk metadata must not be redesigned mid-migration (framework-agnostic).
- **"One new difficulty at a time"** rule; commit strategy per phase; phase completion checklist: can I explain it / modify it / debug it / break it / test it / compare it with .NET.
- **Compatibility constraint during migration:** the exercise-runner design (trusted tests/POM, fresh workspace, disposable container, no Docker socket in the learner container) must survive unchanged — see file 02.

## A.5 Phase roadmap (from the 53-section Java-first roadmap, stack-neutral wording)

Phase 0 understand the existing app (inventory routes, endpoints, entities, x-api-key use) → 1 smallest possible page → 2 first REST API → 3 first DB table → 4 basic login/session → 5 Java LLD chapters (first real product slice) →
6 curriculum hierarchy → 7 user progress → 8 exercises + code state → 9 Docker execution sandbox → 10 Knowledge Atlas / learning graph → 11 parity with .NET → 12 refactor toward target architecture →
13 AI gateway before AI tutor → 14 current-context tutor → 15 progressive tutoring → 16 conversation persistence → 17 AI cost/usage management → 18 admin AI ops dashboard → 19 support assistant → 20 pgvector + RAG →
21 route policy → 22 cross-vertical learning → 23 engagement/completion → 24 seeders & reconciliation engines → 25 production engineering → 26 security hardening → 27 full migration (strangler) → 28 decommission .NET →
29 embedded advanced-language track → 30 React learning scope → then a **capstone: rebuild a simplified Unity-Localization-style system** (see `05-localization-lab-on-hold.md`).
Final architecture sketch: React/Vite → API with modules identity, curriculum, progress, knowledge atlas, exercises (→ Docker runner), AI gateway (tutor/support/other) → context resolver (current context / RAG) → pgvector → LLM provider; admin/operations (usage, cost, quotas, audit, support, AI controls); tooling (seeders, reconcilers, ingestion, evaluation).
The roadmap's learning-language track (Java concepts per project phase) is **dropped in the Python version** — the user does not want Python syntax taught, and Java is practised through the Java LLD curriculum itself.

## A.6 The 12-sprint learning plan (originally 18–24 weeks, ".NET → Java/Spring", Sprints 1–12; restated)

1 Foundation & identity (users, security config, registration/invitation) · 2 Authorization & access control (access policy model/service, method-level security) · 3 AI gateway & cost management (provider-neutral interfaces, admission-control pipeline, provider adapter) ·
4 Current-context tutor (page context & exact resolver, progressive hints, tutor service, streaming controller) · 5 Admin operations dashboard · 6 Persistent learner state · 7 Conversation memory & ownership · 8 Engagement telemetry & auto-completion · 9 Support assistant & tickets ·
10 Filtered RAG & cross-vertical access · 11 Evaluation & production hardening · 12 Completion & .NET deprecation. Week 0 = environment/setup. (The original also carried ~2,800 lines of worked Java/Spring code for sprints 1–4; those examples are Java-specific and were not carried over — recover from git if a Python port wants the structure.)
CLARITY scope doc (same period): real scope = **29 PostgreSQL tables, 20+ services, Docker exercise sandbox, seeding/reconciliation engines, complex knowledge graph, multiple reconcilers (Java, FDE, Azure Labs, Atlas)**, plus new identity, AI tutor with cost management, pgvector RAG, admin dashboard, support ticketing.
Its 150-day mapping: Phase A (30 d) freeze contracts + auth · B (50 d) core services · C (40 d) everything else · D (30 d) optimise + decommission.

## A.7 Interview-prep plans built on the migration (superseded; kept for history)

- **85-day locked-in plan / 85-day roadmap** (Java → AI engineering → FDE → cloud; senior backend roles in India, 7+ yrs): Phase 1 days 1–30 @~120 h/wk = Sprints 1–9 working platform MVP (~9,000 LOC); Phase 2 days 31–50 @80 h/wk RAG + evaluation (NDCG/MRR, cost per query); Phase 3 days 51–70 @80 h/wk FDE/system-design vertical; Phase 4 days 71–85 @60 h/wk AWS/Docker/K8s.
  Daily routine, Friday checkpoints, GitHub commit strategy, emergency adjustments (fall behind / early interview / illness), 60-second pitch, per-phase interview Q&A. Market claim used: required = Java 17+/Spring Boot 3+, SQL, REST/contract evolution, auth, transactions/idempotency, testing; desired = LangChain/LLM, RAG + eval, DB design, Docker/K8s, AWS, system design; nice = Redis, Kafka, observability.
- **Aggressive 30-day plan:** honest feasibility maths — 12 sprints ≈ 520 h base, ≈ 769 h realistic (debugging, testing, learning, devops, breaks) vs 516 h available at 120 h/wk → ~33% short; lists what gets sacrificed (deep learning, comprehensive tests, docs, perf, refactoring), the non-cuttable security items, and recommends a hybrid (aggressive burst then recovery pace) or the 30-60-90 path.
- **Start-tomorrow checklist:** JDK 21/Maven/Docker/IDE setup, new repo `neuralascent-java-migration`, Postgres+Redis in Docker, Day-1 Spring Boot skeleton.
- These plans assumed Java/Spring interview targeting. The interview target has since become **Applied/GenAI (Python)** with a Sept–Dec 2026 build window (file 07); treat these plans as superseded pacing references, not commitments.

## A.8 P12 of the AI-platform TODO tracker, restated (Python)

- P12.1 Preserve contracts before migration: freeze versioned HTTP contracts (auth, conversations, streaming, progress, tickets, admin usage); OpenAPI + contract tests consumed by .NET and Python; provider-neutral terminology; move business logic out of `Program.cs` into modules before porting; `TutorContext` + `emit_tutor_response` as standalone JSON Schema; prompts as versioned content; pgvector schema framework-agnostic.
- P12.2 Target structure: modules `identity, authorization, curriculum, progress, conversation, tutor, support, ai gateway, retrieval, administration, observability, shared`; JWT/policy enforcement; SQL access (psycopg/SQLAlchemy); Pydantic AI selectively for model integration; custom orchestration for authorization, routing, quota, guardrails; SQL migrations with compatibility tests; PostgreSQL/pgvector retained.
- P12.3 Strangler: no big-bang; start with bounded modules (AI gateway/tutor — which is exactly what `ai-agent/` is); reverse-proxy route selected paths; one authoritative schema; parity tests; auth migration only with compatibility plan; remove .NET modules only after traffic/data/rollback validation.
- P12.4 Demonstrate: async Python and concurrency, modular FastAPI architecture, authorization policies, transactions & idempotency, PostgreSQL indexing, SSE streaming trade-offs, resilience, AI gateway abstraction, RAG security/eval, observability & cost governance, evolutionary architecture .NET → Python.

## A.9 Exercise-platform "reimplementation" blueprint (formerly "Java reimplementation")

The retrospective blueprint (`website-assignments-reference`, see file 03) describes rebuilding the exercise-runner backend "as a company-style Java/Spring project": ADRs 001–008 (Git/filesystem packages, Docker boundary, same-host runner, trusted tests/POM, lazy solution retrieval, attempt persistence, runner profiles, resource limits) → domain + manifest parser → golden runner → workspace builder → Docker adapter → REST API → persistence → frontend → CI/CD → production smoke;
learning order domain → parser → filesystem repo → metadata endpoint → solution endpoint → submission validation → workspace builder → **fake runner first** → run endpoint → Docker runner → Surefire parser → attempt persistence → deploy; ".NET → Spring mapping" (controllers→`@RestController`, DI, EF→JPA, middleware→filters, `@ControllerAdvice`, xUnit→JUnit, Flyway/Liquibase decision later).
In the Python version the mapping is: controllers → FastAPI routers, DI → `Depends`, EF → psycopg/SQLAlchemy, filters → middleware, exception advice → exception handlers, xUnit → pytest. Definition of done (23 checkboxes: manifest validated, multi-file starter, trusted tests never browser-controlled, submission whitelist, fresh workspace, disposable runner, limits/timeout, cleanup verified, golden passes/starter rejected, failures classified, evidence normalised, solution lazy/read-only/isolated, accessible disclosure, responsive shell, real DI/context boot test, version-aware attempts, ARM64 artefact, CI green, prod smoke green) is language-neutral and carried over.

## A.10 Java-migration references found *outside* `info/` (NOT edited — for the user to decide)

- `.agents/memory/migration-plan.md` — "Phase 8: Migration to Java (Spring Boot 3) & AWS", active sub-task 8.1 "Scaffolding & Maven Setup in `api-java`", backend target Java 21 + Spring Boot 3 (`api-java/`), mentorship mode.
- `.agents/AGENTS.md:7` — "Target Migration Stack (Separate Sub-repo for Java): Java 21 / Spring Boot 3 + AWS".
- `task_tracker.md` and `task_tracker.md.orig` (lines ~46–47) — "Phase 8: Migration to Java (Spring Boot 3) & AWS Cloud Infrastructure", sub-task 8.1 "Maven/Gradle Setup (Java 21 + Spring Boot 3 in `api-java`)" (+ later sub-tasks); Sub-task 4.3 "Prepare Java 21 / Spring Boot 3 API equivalent contracts in `api-java`".
- `docs/learning/current-system-map.md` — "Phase 0 reference for the Java-first rebuild", "Java-first target" column, "First Java slice" checklist; `docs/learning/java-spring-course-reference-map.md` (maps rebuild phases "Java LLD chapters / Docker Java execution / .NET behavioral parity / Target Java architecture" to course modules); `docs/learning/stage-1-ui-local-llm-prompt.md` ("The Java/Spring backend will…"). `docs/architecture/current-system-map.md` is the same inventory without the Java framing.
- Not migration references (leave as Java): `api/Services/Reconciliation/JavaReconciler.cs`, `api/Data/JavaVerticalSeedData.cs`, `api/Data/ChapterSeedData.cs`, `app/src/**` lesson data — these are Java *curriculum* content ("Spring Boot 3", "Java 21 StructuredTaskScope").

---

# PART B — Study plans & trackers

## B.1 Curriculum Modernization Tracker (`info/curriculum-modernization-tracker.md`, Aug 2026)

Goal: one canonical **Chapters** experience for the Java LLD and FDE curricula, preserving the legacy tracker, completion history and source lineage. Lesson text is original instructional material (external claims grounded in primary docs); the source curriculum conversion (`pasted-text.txt`, a 57-page AI-tool export) is a planning reference only.
- **Product decisions:** Chapters = curriculum library and only top-level learning entry; active pathways = Java LLD & Spring Architecture, FDE; planned pathways are `ComingSoon` catalog records (no fake progress): DSA, SQL & Data Foundations, HLD & Distributed Systems, Frontend/React, Data Engineering, ML & Deep Learning, AWS Cloud Engineering, DevOps & Platform Engineering. Legacy FDE tasks remain the completion-history source until each is safely linked to one canonical lesson. **No legacy vertical/task/completion is deleted.**
- **Shared-content rule:** one canonical lesson may appear in several pathways; completion recorded once; pathway-specific applications/assessments/capstones are separate lessons. *Constraint:* a lesson currently belongs to one module → shared lessons need a future additive course-membership table.
- **Phases:** 1 inventory ✅ · 2 Chapters experience ✅ · 3 canonical FDE migration (seed + verified-only reconciliation ✅; dry-run report and idempotency proof ☐) · 4 original lesson content (104 FDE core + 48 elective drafts, Java title mappings, idempotent Java backfill ✅; keep FDE `Draft` until editorial review) · 5 validation (all ☐: `/chapters` shows both pathways, breadcrumbs, FDE progress = mapped legacy completions, no stale legacy-only route, run local verification) · 6 Scaler-aligned expansion ✅ (3 FDE elective modules / 48 chapters; Java course additive modules: Databases & SQL, Design Principles & Patterns, Applied Design & Machine Coding, two AI-first backend capstones, Production-Ready AI-Enabled Systems, HLD, Data Engineering = 117 chapters: 13 SQL, 10 patterns, 14 machine-coding, 12 primer, 15 advanced capstone, 8 AI-enabled, 21 HLD, 24 data-engineering).
- **Open exception:** the legacy FDE tracker merges *Agentic System Build & Red-Team* with *Integration War Room* while the reference has them separate — do not split/delete the legacy task without an approved reconciliation.
- **Evidence (2026-08-24):** FDE seed = 104 legacy tasks + 48 elective chapters; Java tracker = 22 legacy items → 17 lessons + Structured Concurrency + 5 practice problems + 117 additive. Seeding/reconciliation/build/browser checks were *not run*; first attempt blocked because the published API image lacked a compatible manifest for the user's Linux platform (use local dev build).
- **Risks:** `FdeReconciler` refuses to fabricate canonical entities; AI-generated source conversion must be reconciled with local legacy tasks; course notes are a later phase; HLD and Data Engineering sit in the Java/backend course until membership modelling exists.

## B.2 FDE Curriculum Tracker (`04-fde-curriculum-tracker.md`, checklist preserved; `[x]` = done)

**Prerequisite — Agentic AI Core (11):** GenAI World & LLM Landscape · Prompt Engineering Basics · Advanced Prompting & AI Safety Basics · LLM Built-in Power Tools · RAG · n8n Automation Workflow · What Is an AI Agent? · Building Agents with n8n · OpenClaw: Personal 24/7 AI Agent · Multi-Agent Systems · Debugging AI.
**M1 FDE Foundations: Python, Workflow & Delivery (12):** FDE Role · Problem Discovery & Solution Thinking · Python Toolchain (pyenv, uv, ruff, mypy) · Iterators/Generators/Comprehensions · Closures/Decorators/Context Managers · OOP/Concurrency/Async Python · Pydantic v2, Structured Logging & Profiling · Git Internals, GitHub Workflows & AI Dev Tools · Testing (pytest, property-based, CI) · SE Best Practices (SOLID, Hexagonal) · Linux/Shell for FDEs · Assessment: Python Engineering Challenge.
**M2 Backend Engineering, Observability & Advanced Data Systems (15):** [x] Intro to Backend Engineering (HTTP/REST/API design) · FastAPI Intro→Deep Dive · Auth: OAuth2/JWT/OIDC/RBAC · Order Management Module & API · Payments & Notifications (Stripe, Celery) · [x] Demo Frontend · Real-Time/Queues/Caching (WebSockets, SSE, Redis) · Observability & Distributed Tracing (OpenTelemetry, Grafana) · Postgres Advanced (JSONB, FTS, pgvector) · Postgres Internals (EXPLAIN ANALYZE, indexing, MVCC) · NoSQL/Document/Vector DBs · Dimensional Modeling/dbt · Airflow & Data Quality · Event-Driven/Kafka · Assessment: Data Pipeline.
**M3 Full-Stack FDE (5):** TypeScript for Python Engineers · [x] React Essentials for AI Apps · Next.js · Vercel AI SDK & Streaming UIs · AI Product UX.
**M4 Cloud, DevOps, K8s & Infra (12):** AWS Core (IAM/VPC) · Compute/Storage/Managed (EC2,S3,RDS,SQS) · AWS Security & Secrets (KMS, Secrets Manager, CloudTrail) · [x] Docker: Production Containers · K8s Architecture · EKS/Helm · K8s Networking/Security/GPU · CI/CD & GitOps (Actions, ArgoCD) · Terraform · Serverless (Lambda, API Gateway, Step Functions) · SRE for FDEs · Assessment: Deploy, Break, Fix.
**M5 Enterprise Communication, Consulting & LLM Engineering (12):** Customer Discovery · Technical Scoping & Solution Docs · Stakeholder Communication · Demo Storytelling & Pushback · LLM Fundamentals for Production · Prompt Engineering for Production · RAG Ingestion & Retrieval · RAG over Customer Docs & Hybrid Search · RAG Evaluation (RAGAS) · LLM Safety/Guardrails/Security · Cost, Latency & Model Routing · Assessment: Discovery Call + RAG PoC.
**M6 Agentic Systems & Enterprise Integrations (11):** Tool/Function Calling & Structured Output · Agentic Patterns & Production Concerns · Agent Debugging/Failure Analysis/Evaluation · MCP & Enterprise Tooling · Multi-Agent & HITL · Enterprise Systems Landscape · API Integration Patterns & Connector Design · Integration Failure Modes · Messy Customer Data & Entity Resolution · Build: CRM-to-AI Support Copilot · Assessments: Agentic System Build & Red-Team, Integration War Room.
**M7 Application Engineering, Security & Reliability (12):** Product Thinking for FDE Apps · Frontend Essentials (React+TS) · Multi-Tenant Design & Background Workflows (RLS, Celery) · Document Processing & AI Extraction · Build: Enterprise Document Review App · DX & API Docs · Enterprise Security (PII, SOC2, GDPR) · Secrets/Encryption/Deployment Topologies · Load Testing (k6) · Incident Response & RCA · Enterprise Readiness & Go-Live · Assessment: Secure Deploy + Incident Simulation.
**M8 System Design, Capstone & Hiring Readiness (14):** Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga) · SD: RAG at Scale · SD: Agentic Platform · SD: Multi-Tenant SaaS · SD: Enterprise Integration Hub · SD Interview Framework · Capstone Sprints 1–4 (Discovery & Design; Core Build & Integration; Harden/Secure/Observe; Red-Team/Eval/Fix) · Capstone Demo Day · Interview Readiness · FDE Mock Engagement · Graduation Review.
(Only the 4 `[x]` items were ticked in this file; the *site* content for all 152 lessons is complete — see file 02. `parse_tasks.py` at repo root reads this file to generate `FdeSeedData.cs`.)

## B.3 Azure Certification Plan (`02-azure-certification-plan-2026.md`, prepared 2026-07-02 for the Coforge AI Architect opening)

- **2026 Microsoft overhaul:** AI-102 retired 2026-06-30 → **AI-103** (Azure AI Apps and Agents Developer Associate, GA 2026-06-19); AZ-204 retires 2026-07-31 → **AI-200** (Azure AI Cloud Developer Associate; was in beta); AI-900 exam replaced by AI-901 (cert unchanged, never expires); DP-100 → AI-300; AZ-500 → SC-500; **AZ-104/AZ-305 not retiring**. Retired certs can't be renewed, no auto-migration → don't sprint AZ-204; don't buy AI-102/AZ-204 courses. AZ-305 Expert cert requires an active AZ-104.
- **Recommendation:** Set A — AI-103 ~15–25 Sep 2026, then AI-200 ~25–31 Oct (week-10 checkpoint: if AI-200 still beta/thin materials → swap to AZ-104, AI-200 in November). Set B (safe) — AZ-104 Sep then AI-103 Oct. Optional AI-901 warm-up, GH-300 Copilot cert.
- **AI-103:** USD 165 list, ~120 min, 40–60 questions, pass 700/1000, Pearson VUE, English-only at launch, free annual renewal; built around Microsoft Foundry; weights: generative AI & agentic 30–35%, plan/manage 25–30%, vision/text/extraction 10–15% each; some code items use the **Python** Foundry SDK. Prep: Learn AI-103T00 + study-guide checklist + sandbox + practice assessment when shipped.
- **AI-200 pillars:** containers (ACR/App Service/Container Apps), vector search (Cosmos/pgvector/Managed Redis), messaging (Service Bus/Event Grid), managed identity everywhere. Prep AI-200T00; hands-on = deploy Lab A to Container Apps + vector search + managed identity.
- **Timeline:** Jul wks 1–2 Azure account + Foundry hands-on + Python read-fluency on-ramp; Jul–Aug AI-103 path; mid-Sep AI-103 exam; Sep–Oct AI-200/AZ-104 path + deploy Lab A to Azure; late Oct second exam.
- **Pre-booking checklist:** confirm GA vs beta/language/skills-measured date; diff study guide; confirm practice assessment; register with a **personal MSA** not the Coforge account; online-proctored only if the system test passes (else Pearson VUE Bengaluru).
- Note: the pre-existing `Azure Certifications` vertical on the old dashboard tracked AI-103 and AI-200 (0/2).

## B.4 FDE-Lite Self-Study Plan + Local-AI workflow + Master Calendar (`03-fde-ai-self-study-plan.md`, 2026-07-02)

- **Strategy:** the Coforge interview ≠ full FDE syllabus — ~80% of an AI-Architect panel probes Scaler Module 5 (LLM Engineering) and Module 6 (Agentic Systems); learn concepts anywhere, **implement in C#/.NET** (Azure OpenAI + `Microsoft.Extensions.AI`/Semantic Kernel/Agent Framework); "the labs are the curriculum".
- **Resource map (highest priority):** Karpathy "Intro to LLMs" + "Deep Dive into LLMs like ChatGPT"; 3Blue1Brown GPT chapters; DeepLearning.AI short courses (prompting, MCP, red-teaming); Anthropic "Building Effective Agents"; OpenAI "A Practical Guide to Building Agents"; OWASP LLM Top 10; Hamel Husain "Your AI Product Needs Evals"; Chip Huyen "AI Engineering" + free posts; ByteByteGo for system design; Microsoft Presidio (PII), Azure Document Intelligence/Content Understanding; TechWorld with Nana for Docker/K8s. No single 65–100 h course covers FDE (mega-courses skip guardrails/evals/MCP/integration); if paying, Ed Donner's "LLM Engineering". **Must-read shortlist ≈ 6 h.**
- **Scaler full-stack video triage (≤3–4 h/week):** watch React fundamentals + AI-assisted full-stack elective; skim JS runtime; skip polyfills/Kanban/Redux/Next.js/HTML-CSS.
- **Local-AI workflow (ProArt PX13, Ryzen AI Max+ 395, 128 GB):** LM Studio (Vulkan llama.cpp, OpenAI server on :1234) or Ollama; models gpt-oss-120b (smart default), gpt-oss-20b / Qwen3-30B-A3B (fast MoE), Qwen3-Coder-30B (exercise/test authoring); whisper.cpp; ONNX Runtime + DirectML; hybrid routing demo (PII/bulk local, ambiguous cloud); Foundry Local; ~80% local dev / 20% Azure hardening.
- **Master calendar (2026-07-02 → 10-31, 17 weeks):** wks1–4 Foundry/Python on-ramp + Lab A weekends 1–4; wks5–9 AI-103 + Lab A fault injection (2 faults/week → RCA journal), AI-103 exam wk9 (Aug 31–Sep 6); wk10 checkpoint AI-200 GA? else AZ-104; wks10–13 Lab B core/AI layer/eval pipeline; wk14 deploy Lab A to Azure; wk16 second exam (Oct 19); wk17 buffer + resume update. Weekly constants: 2 faults → 2 RCA entries, one 20-minute AI mock interview, ≤4 h Scaler full-stack, everything AI local-first.
- **Interview narrative:** 7 years of RCA work under the Unity runtime; 2018 ML-based automation (video pipeline → CNN defect detection); every claim backed by a repo, journal entry or certificate.
- *Reality check (2026-09-30):* the calendar predates the Sept pivot to the AI Learning Agent as the primary project; the Azure/lab items are a parallel, lower-priority track. Whether AI-103 was sat is not recorded in the docs.

## B.5 Project Labs — Rebuild, Break, Narrate (`01-project-labs-rebuild-guide.md`)

Two rebuilds of the user's most JD-relevant past systems (refresh war stories with recency, make ATS-note skills defensible — ASP.NET Core, EF Core, Docker, SQL Server — and host a 2026 GenAI layer):
- **Lab A — iCube machine-breakdown support + WMS (2017–19):** ASP.NET Core 8 + SignalR (chat + signaling broker) + WebRTC P2P + coturn (TURN, HMAC time-limited creds) + SQL Server 2022 (deliberate port from Postgres) + RobotSim console + frame→ONNX/DirectML scorer (feature-flagged) + LLM ticket generator (structured output + validation + guardrail, local LM Studio now/Azure OpenAI later) + MailHog escalation + anomaly detector. Build order: weekend 1 compose/EF/WMS/RobotSim → 2 SignalR chat + WebRTC → 3 coturn + TURN creds + frames stub → 4 ticket generator + email + anomaly alert → 5+ fault injection.
  **10 faults:** TURN removed; offer glare (perfect negotiation); munged SDP codec; 10% loss/100 ms jitter (`clumsy`/`tc netem`); Wi-Fi flap ghost peers; 2 API instances without Redis backplane; undisposed tracks/handlers leak; `.Result` in hub → thread-pool starvation; N+1 + tiny pool (k6); prompt-injection + malformed JSON.
- **Lab B — Unity localization platform (2020–22):** ASP.NET Core 8 workflow state machine (Submitted → InReview → Approved/Rejected → Synced), outbox + background worker, SignalR notifications, EF Core/SQL Server, AI layer (PreTranslator, PlaceholderValidator, GlossaryChecker, BatchSummarizer, Classifier, ModelRouter local↔cloud, eval pipeline: back-translation similarity/placeholder diff/glossary adherence), React review dashboard, Unity Editor `LocSync.cs`. **11 faults:** Shift-JIS/ANSI CSV; Turkish-İ culture bug; dropped `{0}` placeholder; conflicting concurrent approvals (`rowversion`); dashboard restart loses SignalR events; email retries without idempotency; renamed scene orphans path-keyed strings (→ GUID keys); synchronous full-catalog export; per-string LLM calls on a 5,000-string batch; deleted runtime key; optional P/Invoke marshaling bug.
- **Practice method:** write the tricky cores yourself, AI for scaffolding/tests/boilerplate; **bug roulette** prompt (AI introduces exactly one subtle bug on a branch `bug/NN`, hint ladder "hint 1/hint 2/reveal", time-box 45–90 min with real tools first); **RCA journal** (six lines per bug; example RCA-013 ghost peers after Wi-Fi flap); target 15–20 entries by late October; weekly "grill me as a skeptical Coforge AI Architect panel" mock; Azure hand-off weeks 14–16 (Container Apps/App Service + Azure SignalR + Azure OpenAI + App Insights).
- Relationship to Neuralascent's **Localization Lab** (`05-…`): Lab B's ideas were re-implemented at practice scale inside Neuralascent as a portfolio product (now on hold). Lab A/B as standalone repos are not in this repo.
