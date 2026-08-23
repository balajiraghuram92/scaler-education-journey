# Neuralascent Website Comparison Baseline

**Captured:** 2026-08-23

**Repository:** `scaler-education-journey`
**Purpose:** A working inventory for comparing the current website with the redesigned experience after the AWS deployment is triggered.

For the database, API, and app-layer migration decisions that follow from this comparison, see [`redesign-data-migration-plan.md`](redesign-data-migration-plan.md).

## Inspection status

The repository and checked-in reference images were inspected locally. The public domain `https://neuralascent.top/` was subsequently reachable and its rendered pages were inspected. The bare IP URL `https://98.130.44.145/` still presents `ERR_CERT_COMMON_NAME_INVALID`; use the domain for browser verification.

The last known container output showed the application running inside the VM, but the historical logs contained schema errors from an earlier deployment. The AWS verification should use fresh logs and fresh page requests.

### Live-site verification — 2026-08-23

The reachable domain is serving the **old dashboard**, not the current Warm Editorial redesign. This makes it a useful source of truth for the data and behavior that the redesign must re-orient.

| Live route | Verified rendered purpose/data |
|---|---|
| `/` | Predictive Study Analytics Hub, Cross-Competence Spider Dashboard, five Study Vertical cards, and AI Insights. The visible counts are FDE Curriculum 4/104, Lab Projects 0/2, Azure Certifications 0/2, FDE Self-Study 4/104, and Java & Spring Architecture 8/22. |
| `/vertical/1` | FDE Curriculum: eight-module FDE curriculum, 4% completion. |
| `/vertical/2` | Lab Projects: WMS Defect Detection and Unity Localization Platform, 0/2. |
| `/vertical/3` | Azure Certifications: AI-103 and AI-200, 0/2. |
| `/vertical/4` | FDE Self-Study: the same visible eight-module FDE structure and 4/104 progress as FDE Curriculum. This is a data-reconciliation candidate, not proof that either record is safe to delete. |
| `/vertical/5` | Java practice workspace, currently focused on OOP-2; it includes study-guide topics and solvable coding problems. |
| `/lab-projects` | An FDE specialization/competence dashboard, despite its route name. This reinforces that the old Projects menu was not a simple two-project page. |
| `/profile` and `/certifications` | Candidate profile, Azure credential plans, professional background, and core architectural pillars; `/certifications` redirects to `/profile`. |

The live navigation exposes Home, Projects, Lessons, and Profile. Its content confirms the source-level inventory, including the legacy dashboard UI that the redesign should not reproduce.

## Git checkpoints

| Revision | Meaning |
|---|---|
| `dd31d06` | Old dashboard/current-website snapshot |
| `73c6028` | Earlier visual issue snapshot |
| `1268c35` | Additional redesign issue snapshot |
| `c2148ca` | New redesign reference images and prompts |
| `f036d2a` | Warm Editorial branding and Knowledge Atlas foundation |
| `d889b14` | Reading Map backend and frontend implementation |
| `7102e4d` | Curriculum Import and Concept Chapter implementation |

## Old-to-new changeset evidence

The supplied baseline `8ac02c2947c3e3096f78517266bb4beb7d9d1969` is especially useful because it captures the complete pre-redesign application immediately before the Warm Editorial work. The old commit is not only a visual reference; it records the navigation and data-discovery behavior that the redesign must preserve in a new form.

### What the old Home page actually did

The old `Home.jsx` fetched `GET /api/verticals` and rendered four functional areas:

1. **Predictive Study Analytics Hub** — calculated total tasks, completed tasks, and overall progress, then displayed a percentage donut.
2. **Cross-Competence Spider Dashboard** — displayed a radar chart for Agent Interaction, Prompt Engineering, RAG Systems, API Integration, Model Tuning, and Infrastructure.
3. **Study Verticals** — rendered every API vertical as a `VerticalCard`, including its description, task count, progress, and link to `/vertical/:id`.
4. **AI Insights** — displayed focus and consistency recommendations.

The current Home page replaces all four areas with the Knowledge Atlas graph. This correctly follows the new reference direction by removing the dashboard charts, but it also removes the old Home page's only direct rendering of the complete vertical list.

### What the old Navbar actually did

The old `Navbar.jsx` fetched `/api/verticals` and dynamically discovered the IDs for Lab Projects, FDE Self-Study, and Java & Spring Architecture. Its navigation exposed:

- Home
- Lab Projects under a Projects dropdown
- Java & Spring Architecture under a Lessons dropdown
- FDE Self-Study under a Lessons dropdown
- Add Vertical / Markdown import through `MarkdownIngestModal`
- Profile and certifications

The current Navbar is much simpler: Knowledge Atlas, Reading Map, Concept Chapters, and Profile. This is visually closer to the new reference, but it drops the old dynamic vertical discovery and the visible entry points into the existing curriculum.

### What the old Lab Projects route actually did

At the old baseline, `/lab-projects` rendered a full FDE specialization workspace, not the two small database-seeded lab projects alone. It contained:

- Core Architectural Maturity
- FDE Track Competence Balance / radar chart
- Eight specialization cards from Agentic AI Core through Application Engineering, Security & Reliability
- Module completion counts and adherence trends
- A specialization focus list with lessons such as GenAI World, Prompt Engineering, RAG, and Debugging AI
- An AI Path Optimization Insight Panel

In the current branch, `LabProjects.jsx` is only a five-line wrapper around `ReadingMap.jsx`, and both `/lab-projects` and `/reading-map` render the Reading Map. This is the clearest concrete example of old product behavior being replaced without a new route or content crosswalk.

### What was added after the old baseline

The current branch adds the new model and page surfaces:

- `KnowledgeAtlasGraph` and `ConceptDetailPopover`
- Knowledge Atlas database entities and `/api/knowledge-atlas`
- Reading Map entities, seed data, UI, and `/api/reading-map`
- Course/module/lesson chapter model extensions
- `ChapterReader` and `/api/chapters`
- `CurriculumImporter` and `/api/chapters/map`
- Code comparisons, diagrams, notes, prerequisites, related lessons, and next lessons

The implementation direction is therefore sound. The missing work is the bridge between the old navigation/data model and the new editorial model.

### Old-to-new content crosswalk required

| Old behavior/content | New destination that should carry it | Current state |
|---|---|---|
| Study Verticals list | Knowledge Atlas learning paths or domain index | Not surfaced on Home |
| Vertical task counts/progress | Reading Map and course/module/lesson progress | Stored, but not integrated into the new Home flow |
| FDE specialization cards | Atlas domains/modules plus chapter collections | Backend tasks exist; no clear new entry point |
| Lab Projects | Dedicated project/learning-path page | Route currently aliases Reading Map |
| Java & Spring dropdown | Java course/module/chapter navigation | Direct vertical route still exists, but current Navbar no longer exposes it |
| FDE Self-Study dropdown | FDE Atlas path and chapter navigation | Direct vertical route still exists, but current Navbar no longer exposes it |
| Add Vertical Markdown modal | Curriculum Import / Map a New Chapter | New page exists; old modal is no longer the primary entry point |
| AI Insights | Reading Map next action, concept notes, or path recommendations | Old hardcoded insight cards removed; no equivalent yet |
| Overall mastery donut/radar | Reading activity, knowledge threads, and relationship graph | Correctly replaced visually, but progress meaning must still be preserved |

## Product intent from the reference material

The redesign is a reading-first learning system, not a generic analytics dashboard.

The reference set defines four connected experiences:

1. **Knowledge Atlas / Home** — learning domains, concepts, relationships, prerequisites, related lessons, and next lessons.
2. **Reading Map / Progress** — what to read, what was revisited, what was deferred, activity, and knowledge threads.
3. **Map a New Chapter / Curriculum Import** — turn Markdown curriculum into a structured chapter, module, concept, and lesson relationship.
4. **Concept Chapter / Learning** — a serious reading room with table of contents, prose, code comparisons, diagrams, related concepts, notes, and navigation.

The design language is the Warm Editorial system: parchment background, paper surfaces, serif display typography, humanist sans-serif body text, sage accents, hairline rules, and restrained interaction. The v2 prompts explicitly reject gauges, radar charts, percentage donuts, glossy SaaS cards, and decorative dashboard chrome.

Reference assets:

- `../images-newdesign/final-references/Final-Design.png`
- `../images-newdesign/Home-page.png`
- `../images-newdesign/Study-tracker.png`
- `../images-newdesign/Curiculam-updator.png`
- `../images-newdesign/Learning-homepage.png`
- `../images-newdesign/current-website-reference.png`
- `../new-redesign-website/website-redesign-issue.png`
- `../new-redesign-website/website-redesign-issue_1.png`

## Local route inventory

| Route | Current component | Current role | Main data/API |
|---|---|---|---|
| `/` | `Home.jsx` | Knowledge Atlas index with domain/concept graph | `GET /api/knowledge-atlas` |
| `/reading-map` | `LabProjects.jsx` → `ReadingMap.jsx` | Reading Map UI, but routed through a legacy-named wrapper | `GET /api/reading-map`, Reading Map mutations |
| `/lab-projects` | `LabProjects.jsx` → `ReadingMap.jsx` | Currently renders the Reading Map too; the original Lab Projects view is no longer distinct | Reading Map API |
| `/progress` | Redirect | Redirects to `/reading-map` | — |
| `/curriculum-import` | `CurriculumImporter.jsx` | Map a New Chapter / Markdown ingestion workspace | `POST /api/chapters/map`, fallback `POST /api/verticals/ingest` |
| `/map-chapter` | `CurriculumImporter.jsx` | Alias for curriculum import | Same as above |
| `/add-vertical` | `CurriculumImporter.jsx` | Alias retained for older navigation | Same as above |
| `/chapter/:slug` | `ChapterReader.jsx` | Concept Chapter reading room | `GET /api/chapters/{slug}` |
| `/chapter/:vertical/:module/:lesson` | `ChapterReader.jsx` | Hierarchical chapter lookup | `GET /api/chapters/{vertical}/{module}/{lesson}` |
| `/learning` | `ChapterReader.jsx` | Alias for the chapter reading experience | Chapter API |
| `/vertical/:id` | `VerticalDetail.jsx` | Legacy vertical/task detail; Java uses a specialized workspace | `GET /api/verticals`, task and course APIs |
| `/profile` | `Profile.jsx` | Profile and certification information | `GET /api/verticals` plus local profile data |

## Backend content inventory

The old learning content is still present in the backend and should be re-oriented into the new information architecture rather than removed.

### Legacy verticals and tasks

Seeded in `api/Data/DbSeeder.cs`, `api/Data/FdeSeedData.cs`, and `api/Data/JavaVerticalSeedData.cs`:

- **Lab Projects** — WMS Defect Detection and Unity Localization Platform.
- **Azure Certifications** — AI-103 and AI-200 preparation.
- **FDE Self-Study** — Agentic AI prerequisites plus modules covering FDE foundations, backend/data systems, full-stack work, cloud/devops, enterprise communication, agentic systems, application engineering, security, reliability, and system design.
- **Java & Spring Architecture** — Java fundamentals, concurrency, advanced Java, collections, Spring, enterprise architecture, practice problems, and the Java course hierarchy.

### New structured content

- **Knowledge Atlas:** domains, concepts, prerequisite relations, lesson relations, next-lesson relations, and domain/concept connections.
- **Reading Map:** reading items, activity timeline, and knowledge threads.
- **Courses and lessons:** course → module → lesson hierarchy with progress, resources, problems, notes, diagrams, and code comparisons.
- **Curriculum import:** Markdown can create or update a course/module/lesson and associate concepts, prerequisites, and related lessons.

## Reusable old-site content catalog

This is the content that must remain available when the old cards and dashboards are replaced. The titles below are copied from the checked-in seed data and cross-checked against the live pages. They are content identifiers for the redesign, not instructions to preserve the old visual layout.

The reusable source-of-truth files are `api/Data/FdeSeedData.cs`, `api/Data/JavaVerticalSeedData.cs`, and the Lab/Azure entries in `api/Data/DbSeeder.cs`. The FDE and Java seed catalogs are unchanged from the supplied old baseline commit; the Markdown list makes the content easy to use during redesign review without copying the full Java lesson bodies out of source control.

### Track-level content

| Legacy track | Description | Live progress observed | Content items |
|---|---|---:|---:|
| FDE Curriculum | Forward Deployment Engineering Track | 4 / 104 (4%) | Same FDE curriculum catalog as the sections below. |
| Lab Projects | Rebuild, Break, Narrate | 0 / 2 (0%) | Rebuild Lab A — WMS Defect Detection; Rebuild Lab B — Unity Localization Platform. |
| Azure Certifications | Cloud Architecture and AI | 0 / 2 (0%) | AI-103 (Apps & Agents) Study & Lab Prep; AI-200 (Cloud Developer) Practice Exams. |
| FDE Self-Study | Agentic AI Track | 4 / 104 (4%) | Same visible eight-module FDE structure as FDE Curriculum; reconcile the underlying rows before merging or removing either path. |
| Java & Spring Architecture | Low-Level Design, Concurrency, Spring Boot & Distributed Enterprise Systems | 8 / 22 (36%) | Four Java modules and the 22 task/lesson items listed below. |

### FDE catalog — 104 items

#### Prerequisite: Agentic AI Core — 11

- GenAI World & LLM Landscape
- Prompt Engineering Basics
- Advanced Prompting & AI Safety Basics
- LLM Built-in Power Tools
- RAG (Retrieval-Augmented Generation)
- n8n Automation Workflow
- What Is an AI Agent?
- Building Agents with n8n
- OpenClaw: Personal 24/7 AI Agent
- Multi-Agent Systems
- Debugging AI

#### Module 1 — FDE Foundations: Python, Workflow & Delivery — 12

- The FDE Role: Customer-Embedded Engineering
- Problem Discovery & Solution Thinking for FDEs
- Python Toolchain & Environment Setup (pyenv, uv, ruff, mypy)
- Iterators, Generators & Comprehensions
- Closures, Decorators & Context Managers
- OOP, Concurrency & Async Python
- Pydantic v2, Structured Logging & Profiling
- Git Internals, GitHub Workflows & AI Dev Tools (Cursor, Claude Code, MCP)
- Testing: pytest, Property-Based Testing & CI
- Software Engineering Best Practices (SOLID, Hexagonal Architecture)
- Linux, Shell & Scripting for FDEs
- Assessment: Python Engineering Challenge

#### Module 2 — Backend Engineering, Observability & Advanced Data Systems — 15

- Introduction to Backend Engineering — HTTP, REST & API Design
- FastAPI: Intro to Deep Dive
- Auth: OAuth2, JWT, OIDC & RBAC
- Building an Order Management Module & its API
- Building Payments & Notifications (Stripe, Celery)
- Building the Demo Frontend
- Real-Time, Queues & Caching (WebSockets, SSE, Redis)
- Observability & Distributed Tracing (OpenTelemetry, Grafana)
- Postgres Advanced: JSONB, Full-Text Search & pgvector
- Postgres Internals: EXPLAIN ANALYZE, Indexing & MVCC
- NoSQL, Document DBs & Vector Databases
- Dimensional Modeling, dbt & Modern Data Stack
- Workflow Orchestration with Airflow & Data Quality
- Event-Driven Architecture & Kafka Fundamentals
- Assessment: Data Pipeline Build & Debug

#### Module 3 — Full-Stack FDE: TypeScript, React & AI-First Frontends — 5

- TypeScript Fundamentals for Python Engineers
- React Essentials for AI Apps
- Next.js for Full-Stack AI Apps
- Vercel AI SDK & Streaming UIs
- AI Product UX & Customer-Facing Polish

#### Module 4 — Cloud, DevOps, Kubernetes & Infrastructure — 12

- AWS Core: IAM, VPC & Networking
- Compute, Storage & Managed Services (EC2, S3, RDS, SQS)
- AWS Security & Secrets Management (KMS, Secrets Manager, CloudTrail)
- Docker: Production Containers
- Kubernetes Architecture & Core Concepts
- EKS, Helm & Production Kubernetes
- Kubernetes Networking, Security & GPU Workloads
- CI/CD Pipelines & GitOps (GitHub Actions, ArgoCD)
- Terraform & Infrastructure as Code
- Serverless & Event-Driven Cloud (Lambda, API Gateway, Step Functions)
- SRE & Reliability Engineering for FDEs
- Assessment: Deploy, Break, Fix on Cloud

#### Module 5 — Enterprise Communication, Consulting & LLM Engineering — 12

- Customer Discovery & Requirements Gathering
- Technical Scoping & Solution Documentation (PRD-lite, options matrix, risk register)
- Stakeholder Communication & Written Artifacts
- Demo Storytelling & Handling Pushback
- LLM Fundamentals for Production
- Prompt Engineering for Production Systems
- RAG Architecture: Ingestion & Retrieval
- RAG over Customer Documents & Hybrid Search
- RAG Evaluation & Iteration (RAGAS)
- LLM Safety, Guardrails & Security
- Cost, Latency & Model Routing
- Assessment: Discovery Call + RAG PoC Build

#### Module 6 — Agentic Systems & Enterprise Integrations — 11

- Tool Calling, Function Calling & Structured Output
- Agentic Patterns & Production Concerns
- Agent Debugging, Failure Analysis & Evaluation
- MCP (Model Context Protocol) & Enterprise Tooling
- Multi-Agent Patterns & Human-in-the-Loop
- Enterprise Systems Landscape & Integration Topology
- API Integration Patterns & Connector Design
- Integration Failure Modes & Debugging
- Messy Customer Data & Entity Resolution
- Build: CRM-to-AI Support Copilot
- Assessments: Agentic System Build & Red-Team, Integration War Room

#### Module 7 — Application Engineering, Security & Reliability — 12

- Product Thinking & Architecture for FDE Apps
- Frontend Essentials for FDEs: React + TypeScript
- Multi-Tenant Design & Background Workflows (Postgres RLS, Celery)
- Document Processing & AI Extraction Workflows
- Build: Enterprise Document Review App
- Developer Experience & API Documentation
- Enterprise Security for FDE Systems (PII, SOC2, GDPR)
- Secrets, Encryption & Deployment Topologies
- Load Testing, Capacity Planning & Performance (k6)
- Incident Response & Customer-Facing RCA
- Enterprise Readiness Checklist & Go-Live
- Assessment: Secure Deploy + Incident Simulation

#### Module 8 — System Design, Capstone & Hiring Readiness — 14

- Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga)
- System Design: RAG System at Scale
- System Design: Agentic Platform at Scale
- System Design: Multi-Tenant SaaS Platform
- System Design: Enterprise Integration Hub
- System Design Interview Framework & Practice
- Capstone Sprint 1: Discovery & Solution Design
- Capstone Sprint 2: Core Build & Integration Layer
- Capstone Sprint 3: Harden, Secure & Observe
- Capstone Sprint 4: Red-Team, Eval & Fix
- Capstone Demo Day: Client Panel Presentation
- Interview Readiness & Career Launch
- FDE Mock Engagement: Full Simulation
- Graduation Review: Portfolio Defense & Next Steps

### Java & Spring catalog — 22 legacy items

#### Module 1 — OOP & Design Foundations — 10

- Lesson 01: Intro to LLD for Scalable & AI-Ready Systems
- Lesson 02: OOP-1 Intro Lab (Core OOP Foundations)
- Lesson 03: OOP-2 Access Modifiers, Encapsulation & Inheritance
- OOP-2 Problem 1: Immutable Fare (Warm-up)
- OOP-2 Problem 2: Driver Onboarding (Easy-Mid)
- OOP-2 Problem 3: Vehicle Hierarchy (Mid)
- OOP-2 Problem 4: Trip Copy Semantics (Mid-Hard)
- OOP-2 Problem 5: The equals/hashCode Contract (Hard)
- Lesson 04: OOP-3 Polymorphism, Interfaces & Abstract Classes
- Lesson 05: OOP-4 Library Management System (LMS) Lab

#### Module 2 — Concurrency & Multithreading — 4

- Lesson 06: Concurrency 1: Processes, Threads & PCB Context Switching
- Lesson 07: Concurrency 2: Executors, Thread Pools & Callable/Future
- Lesson 08: Concurrency 3: Synchronization, Race Conditions & Locks
- Lesson 09: Concurrency 4: Semaphores & Bounded Buffer

#### Module 3 — Advanced Java & Collections — 4

- Lesson 10: Java Advanced 1: Generics, Wildcards & Type Erasure
- Lesson 11: Java Advanced 2: Collections Lab & Comparator/Comparable
- Lesson 12: Java Advanced 3: Lambdas, Functional Interfaces & Streams
- Lesson 13: Java Advanced 4: Streams in Depth & Exception Architecture

#### Module 4 — Spring & Enterprise Architecture — 4

- Spring Boot 3 Core: Inversion of Control & Dependency Injection
- Data Layer: Spring Data JPA, Hibernate & PostgreSQL 16
- API Architecture: RESTful Services, Validation & Security
- Contest Capstone: Java, OOP & Concurrency Machine Coding

The Java structured course also carries richer chapter data for the first modules: descriptions, dates, Horstmann references, estimated reading time, Markdown content, five OOP-2 practice problems, code comparisons, diagrams, notes, and completion state. Preserve those fields when moving the Java path into the new chapter reader.

### Profile and certification content

The old `/profile` page is part of the product content, not only a decorative page. Preserve these facts when the profile is redesigned:

- **Identity:** Raghuram Balaji — AI Architect Candidate.
- **Background:** seven years of runtime/root-cause analysis under Unity; a 2018 ML/CNN video pipeline for supply-chain defect detection; current work on structured LLM ticket triage, guardrails, evaluation, human-in-the-loop review, and hybrid local/cloud model routing.
- **AI-103 — Agentic AI & OpenAI:** Azure AI Apps and Agents Developer; target timeline 2026; Azure OpenAI/model routing, Semantic Kernel and agent workflows, vector search and knowledge indexing.
- **AI-200 — Cloud Architecture:** Azure AI Cloud Developer; target timeline 2026; Azure App Service and Container Apps, enterprise security/guardrails, scalable APIs and microservices.
- **Core architectural pillars:** Agentic AI & Systems; 7+ Years Core Engineering; ML & Computer Vision; Production Guardrails.
- **Profile action:** View GitHub. Preserve the external destination when the profile is moved into the new navigation.

### Old dashboard meaning to carry forward

The old dashboard's numbers and labels explain the user's mental model even though the redesign should not reproduce its charts:

- Overall mastery was shown as a 7% predictive study analytics score.
- FDE competency dimensions were Agentic, FDE, Backend, Full-Stack, Cloud, and Enterprise; the project dashboard also showed Backend, Frontend, Cloud-Native, LLM Design, Deployment, and Data Flow.
- AI insights emphasized Agent Integration as a focus area and projected the FDE Architect path at 45 days at the current pace.
- The FDE project dashboard highlighted GenAI World, Prompt Engineering, Advanced Prompting & Safety, LLM Built-in Power Tools, RAG, n8n automation, AI agents, OpenClaw, and Debugging AI, with a recommendation to strengthen Cloud/DevOps/Infrastructure.

These should become explainable Reading Map recommendations, Atlas relationships, or path summaries. They should not remain unexplained hard-coded percentages after the redesign.

Relevant endpoints are defined in `api/Program.cs`:

- `/api/verticals`, `/api/tasks/{id}/toggle`
- `/api/courses`, `/api/lessons`, `/api/problems`
- `/api/knowledge-atlas`
- `/api/reading-map`
- `/api/chapters`, `/api/chapters/map`, `/api/chapters/{id}/notes`

## Page-by-page comparison baseline

### 1. Home / Knowledge Atlas

**Current local behavior:** The Home page loads only the Knowledge Atlas graph. It renders learning domains and concepts, with links to Reading Map and Concept Chapters. If the API is unavailable, it uses the default graph dataset.

**Reference intent:** The Home page should act as the learning index. The old verticals and their substantial task/module content should be represented as meaningful learning paths, domains, concepts, or connected chapter collections.

**Current gap:** The old vertical/task data remains in the API, but the redesigned Home page does not surface it. A visitor can see the graph but cannot naturally discover the full FDE, Azure, Java, or Lab curriculum from the new Home experience.

**Focused change candidate:** Add a learning-path layer to the Home page or connect Atlas domains/concepts to vertical/course/module views. Preserve the graph; do not recreate the old dashboard.

### 2. Reading Map / Progress

**Current local behavior:** The Reading Map contains Read this week, Revisited, Deferred, Lists, Prerequisites, a small activity timeline, knowledge threads, and an Add Entry flow.

**Reference intent:** This is the progress surface, not a project dashboard. Its job is to orient the next reading action and show relationships between topics.

**Current gaps:**

- `/reading-map` and `/lab-projects` both render the same component.
- The component is implemented in `ReadingMap.jsx`, but the route still uses the `LabProjects.jsx` wrapper.
- The seeded data is representative and centered on Java concurrency; it does not yet summarize the full legacy curriculum.

**Focused change candidate:** Make `/reading-map` directly render `ReadingMap`, restore a distinct Lab Projects route, and later derive Reading Map entries from real course/module/lesson progress.

### 3. Curriculum Import

**Current local behavior:** The import workspace parses Markdown, previews a chapter and table of contents, exposes domain/module/chapter/prerequisite/related-concept controls, and submits to the chapter mapping API.

**Reference intent:** This is the editorial equivalent of “Map a New Chapter.” It should feel like a structured authoring tool while retaining the actual curriculum content.

**Current status:** The route and backend endpoint exist. This is one of the closest functional matches to the intended redesigned panel.

**Verification needed after AWS:** Submit or preview a known Markdown sample and verify that the resulting chapter appears in `/chapter/:slug` with its relationships intact.

### 4. Concept Chapter / Learning

**Current local behavior:** The chapter reader provides a table-of-contents rail, reading chamber, breadcrumbs, related lesson/prerequisite/further-reading sidebar, prose, code comparison, diagrams, problems, notes, and previous/next navigation.

**Reference intent:** A text-first reading room where the data and explanatory relationships are more important than dashboard metrics.

**Current status:** The structure is present locally and is aligned with the reference intent. The seeded Structured Concurrency chapter is the primary known example.

**Verification needed after AWS:** Check that the chapter API returns the new difficulty/content fields and that the chapter renders without falling back to placeholder content.

### 5. Legacy vertical detail

**Current local behavior:** `/vertical/:id` still contains the old modular dashboard treatment, including progress dials/radar-style visualizations for some verticals. Java has a specialized practice dashboard.

**Reference intent:** Legacy content should be retained, but its presentation should eventually be translated into the editorial learning-path/chapter system.

**Focused change candidate:** Keep this route working as a compatibility surface for now. Do not redesign it until the new Home/Atlas path can reach the same data.

## Focused gaps to address first

### P0 — Verify after AWS deploy

1. The live host/certificate must expose the actual application, not an unrelated or mismatched HTTPS listener.
2. `/api/knowledge-atlas`, `/api/reading-map`, and `/api/chapters/structured-concurrency` must return successful responses.
3. The deployed database must contain the migrations for Reading Map and chapter fields.

### P1 — Small, high-value product fixes

1. Make `/reading-map` render `ReadingMap.jsx` directly.
2. Restore a distinct Lab Projects page or explicitly reframe it as a learning path.
3. Add a visible way to reach the existing FDE, Azure, Java, and Lab content from the redesigned Home/Atlas page.
4. Fix graph sizing and label wrapping where long domain names overlap or create excessive empty space.
5. Derive Reading Map content from real lesson/task progress after the navigation model is settled.

## AWS verification checklist

After triggering the AWS deployment, capture the following:

```bash
sudo docker ps
sudo docker logs --since 30m studytracker-api
sudo docker logs --since 30m studytracker-app
sudo docker logs --since 30m studytracker-db
```

Then verify these URLs in order:

1. `/`
2. `/reading-map`
3. `/lab-projects`
4. `/curriculum-import`
5. `/chapter/structured-concurrency`
6. `/profile`
7. A real `/vertical/:id` route from the API response

For each page, compare:

- Does the page load actual API data rather than fallback data?
- Does the route preserve the intended content from the old website?
- Does the visual hierarchy match the corresponding reference panel?
- Can a user move naturally from a domain to a concept, reading item, chapter, and next lesson?
- Are the old verticals/tasks still discoverable somewhere in the new information architecture?

## Working conclusion

The redesign foundation is present locally, including all four intended panels. The main remaining problem is information architecture: the old curriculum is still stored and partly accessible, but it is not yet re-oriented into the new Atlas → Reading Map → Chapter flow. The safest next pass is therefore a focused navigation/data-integration pass, followed by small visual corrections, rather than a complete rewrite.
