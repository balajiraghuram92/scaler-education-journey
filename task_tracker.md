# Study Plan Website - Task Tracker

## Phase 1: Foundation (Completed)
- [x] **Project Setup**: Scaffold Vite + React in `app` subfolder
- [x] **FDE Tracker**: Created `04-fde-curriculum-tracker.md`
- [x] **Design System**: Premium "Deep Dark AI Architect" CSS in `index.css`
- [x] **Base Layout**: Navbar, Layout, `App.jsx` components created
- [x] **Landing Page**: Hero Section (`Home.jsx`), `VerticalCard` component, Study Verticals Grid
- [x] **Backend Setup**: ASP.NET Core project in `api` directory
- [x] **Database Configuration**: EF Core Models (`StudyVertical`, `StudyTask`), Context, `Program.cs`
- [x] **Database Migrations**: InitialCreate migration generated successfully

## Phase 2: Backend Integration & Data Seeding (Completed)
- [x] **Sub-task 2.1**: Implement Database Seeding (Seed initial data from `info/` markdown files)
- [x] **Sub-task 2.2**: Implement Minimal API Endpoints (GET endpoints for Verticals and Tasks)
- [x] **Sub-task 2.3**: Configure CORS to allow Vite frontend to consume the API

## Phase 3: Frontend Integration & Features (Completed)
- [x] **Sub-task 3.1**: Connect `Home.jsx` to fetch Verticals from the API instead of hardcoded data
- [x] **Sub-task 3.2**: Create a Detail Page/Component to view tasks within a specific vertical
- [x] **Sub-task 3.3**: Implement task completion toggling (Update UI and send PUT request to API)

## Phase 4: UI Polish & Dynamic Ingestion (Completed)
- [x] **Sub-task 4.1**: Create Markdown parser to ingest all tasks from `04-fde-curriculum-tracker.md`
- [x] **Sub-task 4.2**: Implement progress bars and glassmorphic polish on the Vertical Detail view
- [x] **Sub-task 4.3**: Dynamic Web UI Markdown Ingestion (`POST /api/verticals/ingest` & `MarkdownIngestModal.jsx`)
- [x] **Sub-task 4.4**: Interactive SPA Dashboard (`Home.jsx`) with Multi-Vertical Aggregated Analytics Banner

## Phase 5: Dockerization & Azure Deployment
- [x] **Sub-task 5.1**: Containerize Frontend and Backend (Write `Dockerfile`s & `docker-compose.yml`)
- [x] **Sub-task 5.2**: Azure Frontend: Deploy React App to **Azure Static Web Apps**
- [x] **Sub-task 5.3**: Azure Backend: Deploy ASP.NET Core API to **Azure App Service** (Free Tier)

## Phase 6: Serverless Architecture (Azure Container Apps)
- [x] **Sub-task 6.1**: Update GitHub Actions to build and push the Docker container to **GitHub Container Registry (GHCR)** (Free).
- [x] **Sub-task 6.2**: Deploy the backend to Azure Container Apps (Serverless, $0/month).
- [x] **Sub-task 6.3**: Configure Azure Container App environment variables for passwordless SQL connection.

## Phase 7: UI/UX Redesign & Dynamic Implementations (Completed)
- [x] **Sub-task 7.1**: Implement the Predictive Study Analytics Hub and Cross-Competence Spider Dashboard (as seen in Concept 3b Focus).
- [x] **Sub-task 7.2**: Implement the Markdown Ingestion Portal with hierarchical tree visualization and drag-and-drop support (Concept 3b Refined Model).
- [x] **Sub-task 7.3**: Implement the FDE & Agentic AI Track Specialization Views with progress dials, maturity matrix, and detailed lesson lists.
- [x] **Sub-task 7.4**: Implement the Data-Driven Lab Projects page showcasing architectural maturity, tech stack breadth, and individual project cards with mini-charts.
- [x] **Sub-task 7.5**: Integrate dynamic charts (e.g., using Recharts or Chart.js) and ensure responsive, premium glassmorphic styling across all new views.

## Phase 8: Migration to Java (Spring Boot 3) & AWS Cloud Infrastructure
- [ ] **Sub-task 8.1**: Project Scaffolding & Maven/Gradle Setup (Java 21 + Spring Boot 3 in `api-java`)
- [ ] **Sub-task 8.2**: JPA Entity Data Models & Repository Layer (`StudyVertical`, `StudyTask`, Spring Data JPA)
- [ ] **Sub-task 8.3**: DTOs, Service Layer & Database Seeding Logic (Ingesting markdown data in Java)
- [ ] **Sub-task 8.4**: REST Controller & API Key Security Middleware (`/api/verticals`, `/api/tasks`, `/api/verticals/ingest`)
- [ ] **Sub-task 8.5**: Dynamic Markdown Parser in Java for Curriculum Ingestion
- [ ] **Sub-task 8.6**: Java API Dockerization & Local Integration Testing
- [ ] **Sub-task 8.7**: AWS Infrastructure Setup (AWS ECR, AWS App Runner / ECS Fargate, AWS S3 / CloudFront)
- [ ] **Sub-task 8.8**: GitHub Actions CI/CD Pipeline for AWS Deployment

## Phase 9: Production AWS EC2 ARM64 (t4g.small) Docker Compose Stack
- [x] **Sub-task 9.1**: Repository & Architecture Audit (Baseline captured at `b7faacc384164c99f40dd39553e137316b932f3b`)
- [x] **Sub-task 9.2**: Decouple Azure Services & EF Core PostgreSQL Provider Migration (`Npgsql.EntityFrameworkCore.PostgreSQL`)
- [x] **Sub-task 9.3**: Frontend Dockerfile & Nginx Reverse Proxy Fixes
- [x] **Sub-task 9.4**: Production Docker Compose & Health Check Hardening (ARM64-native `postgres:16-alpine`)
- [x] **Sub-task 9.5**: Security & Environment Standardization (`.env.example`, Fail-Closed API Key Auth)
- [x] **Sub-task 9.6**: GitHub Actions Multi-Arch ARM64 ECR Build & OIDC Deployment Pipeline
- [x] **Sub-task 9.7**: S3 Automated Database Backup & Disaster Recovery Scripts

## Phase 10: Production-Readiness Review & Remediation Pass
- [x] **Sub-task 10.1**: Comprehensive Audit & Defect Discovery (Identified 3 P0, 4 P1, 1 P2 defects)
- [x] **Sub-task 10.2**: Hardcoded Secret Sanitization & Fail-Closed Environment Security
- [x] **Sub-task 10.3**: ASP.NET Core `/health` Endpoint & Runtime Container Utility Hardening (`curl`)
- [x] **Sub-task 10.4**: Disaster Recovery Script Verification & Strict Error Propagation (`scripts/*.sh`)
- [x] **Sub-task 10.5**: Deterministic Immutable Tag CI/CD Deployment & Health Check Verification
- [x] **Sub-task 10.6**: Root Repository Hygiene & `.gitignore` Protection

## Phase 11: Final Production Architecture & ECR Compliance Audit
- [x] **Sub-task 11.1**: Final Production Architecture Compliance Audit (Strict Section 9 Docker Artifact Rule enforcement)
- [x] **Sub-task 11.2**: Production Compose ECR Image Tag Standardization (`docker-compose.yml` uses `image:` tags, no `build:` on EC2)
- [x] **Sub-task 11.3**: Local Development Override Scaffolding (`docker-compose.override.yml`)
- [x] **Sub-task 11.4**: Internal Container Health Networking Verification (`docker compose exec -T api curl -f http://localhost:5000/health`)
- [x] **Sub-task 11.5**: Complete 44-Point Mandatory Compliance Verification Checklist

## Phase 12: Knowledge Atlas Warm Editorial Redesign (Panel A - Home Page)
- [x] **Sub-task 12.1**: Update `.agents/AGENTS.md` with Autonomous Full Implementation permissions
- [x] **Sub-task 12.2**: Setup Google Fonts (*Newsreader*, *Playfair Display*, *Plus Jakarta Sans*, *JetBrains Mono*) in `app/index.html` & `app/src/index.css`
- [x] **Sub-task 12.3**: Establish Warm Editorial Design Tokens (`--bg-parchment: #F8F6F0`, `--bg-paper: #FFFFFF`, `--accent-sage: #2C5E55`, `--rule-border: #E5E0D8`)
- [x] **Sub-task 12.4**: Refactor `Navbar.jsx` and `Navbar.css` to 3-column editorial header (Wireframe Globe + Centered Neuralascent + Raghuram Balaji profile)
- [x] **Sub-task 12.5**: Implement Anchored `ConceptDetailPopover.jsx` & `ConceptDetailPopover.css` (Prerequisites, Related Lessons, Next Lessons)
- [x] **Sub-task 12.6**: Implement Interactive Bipartite Synaptic Graph (`KnowledgeAtlasGraph.jsx` & `KnowledgeAtlasGraph.css`) with cubic Bézier curve mathematical model
- [x] **Sub-task 12.7**: Assemble Redesigned Knowledge Atlas Index page in `Home.jsx` & `Home.css`
- [x] **Sub-task 12.8**: Backend Knowledge Graph PostgreSQL Schema & Seeding (8 Domains + 8 Concepts + `/api/knowledge-atlas`)

## Phase 13: Reading Map Warm Editorial Redesign (Panel B - Study Tracker)
- [x] **Sub-task 13.1**: Create detailed redesign tracker document `study-tracker-webpage-redesign.md`
- [x] **Sub-task 13.2**: Backend PostgreSQL Entity Models (`ReadingMapItem.cs`, `ReadingActivityLog.cs`, `KnowledgeThread.cs`)
- [x] **Sub-task 13.3**: Register DbSets & indexes in `StudyTrackerContext.cs`
- [x] **Sub-task 13.4**: Implement idempotent seeder `ReadingMapSeedData.cs` matching `Study-tracker.png`
- [x] **Sub-task 13.5**: ASP.NET Core Minimal API endpoints (`GET /api/reading-map`, `PATCH /api/reading-map/items/{id}/toggle`, `POST /api/reading-map/items`)
- [x] **Sub-task 13.6**: Implement `ReadingMap.jsx` with dynamic state management & optimistic updates
- [x] **Sub-task 13.7**: Implement `ReadingMap.css` with 3-column asymmetric layout, custom SVG activity sparkline, and knowledge threads
## Phase 14: Concept Chapter Reader Engine (Panel D - Text-First Reading Room)
- [x] **Sub-task 14.1**: Build `ChapterReader.jsx` with 3-column asymmetric grid (Sticky ScrollSpy TOC Rail + Main Reading Chamber + Contextual Sidebar)
- [x] **Sub-task 14.2**: Implement `ChapterReader.css` with Warm Editorial typography, generous line-height, and paper contrast
- [x] **Sub-task 14.3**: Implement `CodeComparisonSwitcher.jsx` for interactive Before/After code snippet toggle
- [x] **Sub-task 14.4**: Implement dynamic inline SVG architecture diagram renderer
- [x] **Sub-task 14.5**: Add backend API endpoints `GET /api/chapters` and `GET /api/chapters/{slug}` with rich metadata

## Phase 15: Full Java LLD & FDE Curriculum Migration into Text-First Chapters
- [x] **Sub-task 15.1**: Migrate Java LLD Chapter: *Structured Concurrency & Virtual Threads in Java 21*
- [x] **Sub-task 15.2**: Migrate Java LLD Chapter: *OOP-2: Access Modifiers, Constructor Chaining & Immutability*
- [x] **Sub-task 15.3**: Migrate Java LLD Chapter: *The equals/hashCode Contract & Memory Symmetry*
- [x] **Sub-task 15.4**: Migrate FDE Chapter: *Building an Autonomous AI Agent (The Observe-Plan-Act Loop)*
- [x] **Sub-task 15.5**: Migrate FDE Chapter: *RAG (Retrieval-Augmented Generation) & Hybrid Vector Search*
- [x] **Sub-task 15.6**: Update global navigation (`Navbar.jsx`, `App.jsx`, `VerticalDetail.jsx`, `Home.jsx`) linking to the new chapter reading rooms

## Phase 16: Curriculum Import & Chapter Mapper Redesign (Panel C - Map a New Chapter)
- [x] **Sub-task 16.1**: Remove always-on legacy "Import" modal trigger from global `Navbar.jsx` to prevent public spamming.
- [x] **Sub-task 16.2**: Design and build `CurriculumImporter.jsx` (Panel C: "Map a New Chapter") with Warm Editorial 3-column layout (Markdown Editor + Live Rendered Chamber + Domain/Module/Prereqs/Concept Tags rail).
- [x] **Sub-task 16.3**: Implement `CurriculumImporter.css` matching `info/images-newdesign/Curiculam-updator.png` and `Final-Design.png` (Panel C) with Newsreader serif, sage `#2C5E55` import button, and interactive tag chips.
- [x] **Sub-task 16.4**: Re-map the entry point to Curriculum Mapping into Concept Chapter (`ChapterReader.jsx` Panel D) — added upcoming session card with IAM-authenticated `+ Map Chapter` admin action and left TOC rail trigger.
- [x] **Sub-task 16.5**: Register routes (`/curriculum-import`, `/map-chapter`, `/add-vertical`) in `App.jsx`.
- [x] **Sub-task 16.6**: Add backend Minimal API endpoint `POST /api/chapters/map` in ASP.NET Core `Program.cs` and `DTOs.cs` to persist mapped chapters, modules, and concept associations into PostgreSQL.
- [x] **Sub-task 16.7**: Comprehensive verification of 4-panel Warm Editorial suite (Panel A: Home, Panel B: Reading Map, Panel C: Curriculum Import, Panel D: Concept Chapters).

## Phase 17: Portable Single-EC2 Delivery Automation
- [x] **Sub-task 17.1**: Replace invalid `get-docker.sh` HTML artifact with an idempotent Linux/EC2 bootstrap entry point.
- [x] **Sub-task 17.2**: Add one-command native local build, migration, seed, and startup for AMD64/ARM64 Docker hosts and WSL2.
- [x] **Sub-task 17.3**: Add fail-closed single-EC2 deployment with database discovery, deployment locking, digest references, health rollback, TLS renewal, and PostgreSQL volume preservation.
- [x] **Sub-task 17.4**: Add validated pre-migration PostgreSQL dumps, S3 upload, and fresh-host restore from the latest checksum-verified backup.
- [x] **Sub-task 17.5**: Add server-side Nginx API-key injection and loopback-only API host binding for the proposed production workflow.
- [x] **Sub-task 17.6**: Prepare reviewed multi-platform GitHub Actions workflow proposal with CI validation, immutable digests, SSM polling, and timeout cancellation.
- [x] **Sub-task 17.7**: Add Luna-authored future Terraform/RDS/ECS/ALB/S3/CloudFront migration plan.
- [ ] **Sub-task 17.8**: User reviews and manually activates `deploy/deploy-api.proposed.yml` as `.github/workflows/deploy-api.yml` per workflow-freeze policy.
- [ ] **Sub-task 17.9**: User configures encrypted SSM parameters and runs the first local and EC2 deployment verification.

## Phase 18: .NET API Java Exercise Runner Integration
- [x] **Sub-task 18.1**: Add manifest-driven exercise configuration, contracts, and repository.
- [x] **Sub-task 18.2**: Add submission validation and isolated workspace construction.
- [x] **Sub-task 18.3**: Add `IExerciseRunner` and Docker.DotNet local execution backend.
- [x] **Sub-task 18.4**: Add Surefire parsing and learner/infrastructure outcome classification.
- [x] **Sub-task 18.5**: Add `ExerciseService`, Minimal API endpoints, and dependency injection.
- [x] **Sub-task 18.6**: Integrate trusted exercise assets and Docker socket access into Compose packaging.
- [x] **Sub-task 18.7**: Add exercise unit, endpoint-mapping, service, and opt-in Docker integration tests.
- [x] **Sub-task 18.8**: Run .NET tests, Phase 1 regression validation, and actual Docker end-to-end scenarios.

## Feature Phase 3: Learner Exercise Workspace Integration
- [x] **Sub-task 19.1**: Add learner-safe exercise metadata endpoint and trusted starter delivery.
- [x] **Sub-task 19.2**: Replace fixture-driven exercise UI with metadata-driven multi-file workspace execution.
- [x] **Sub-task 19.3**: Add immutable execution snapshots, stale-result handling, and keyboard/accessibility behavior.
- [x] **Sub-task 19.4**: Add focused Vitest and React Testing Library coverage.

## Phase 20: Curriculum Pipeline — Lesson 3 Ingestion (Completed)
- [x] **Sub-task 20.1**: Ingest Lesson 3 chapter body into `api/Data/JavaVerticalSeedData.cs` (`GetAuthoredLessonContent`).
- [x] **Sub-task 20.2**: Wire Lesson 3 concept checks (2 gated MCQs) and practice questions (8 MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 20.3**: Associate Lesson 3 coding exercise with `app/src/data/lessonExerciseAssociations.js`.
- [x] **Sub-task 20.4**: Update task tracking and provide Docker verification commands.

## Phase 21: FDE Curriculum Pipeline — Module 3: Full-Stack FDE (Lessons 1-5 of 5) (Completed)
- [x] **Sub-task 21.1**: Ingest 5 Lesson chapter bodies for `full-stack-ai-frontends` into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 21.2**: Wire 10 Concept Checks (2 per lesson) and 33 Practice Questions across all 5 lessons into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 21.3**: Add architecture diagram for Lesson 4 (`04-vercel-ai-sdk-and-streaming-uis`) highlighting the server-side secrets and streaming lifecycle boundary.
- [x] **Sub-task 21.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 21.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 22: FDE Curriculum Pipeline — Module 4: Cloud, DevOps, Kubernetes & Infrastructure (Lessons 1-6 of 12) (Completed)
- [x] **Sub-task 22.1**: Ingest 6 Lesson chapter bodies for `cloud-devops-infrastructure` into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 22.2**: Wire 12 Concept Checks (2 per lesson) and 39 Practice Questions across all 6 lessons into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 22.3**: Add architecture diagram for Lesson 5 (`05-kubernetes-architecture-and-core-concepts`) visualizing the control-plane vs. worker-node topology.
- [x] **Sub-task 22.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 22.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 23: FDE Curriculum Pipeline — Module 4: Cloud, DevOps, Kubernetes & Infrastructure (Lessons 7-12 of 12 — MODULE 4 COMPLETE) (Completed)
- [x] **Sub-task 23.1**: Ingest 6 Lesson chapter bodies for `cloud-devops-infrastructure` (Lessons 7-12) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 23.2**: Wire 12 Concept Checks (2 per lesson) and 39 Practice Questions across all 6 lessons into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 23.3**: Add architecture diagram for Lesson 8 (`08-ci-cd-pipelines-and-gitops-github-actions-argocd`) illustrating the CI push / ArgoCD pull reconciliation loop meeting at the manifests-repo commit boundary.
- [x] **Sub-task 23.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 23.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 24: FDE Curriculum Pipeline — Module 5: Enterprise Communication, Consulting & LLM Engineering (Lessons 1-6 of 12) (Completed)
- [x] **Sub-task 24.1**: Ingest 6 Lesson chapter bodies for `enterprise-consulting-llm` (Lessons 1-6) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 24.2**: Wire 12 Concept Checks (2 per lesson) and 38 Practice Questions across all 6 lessons into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 24.3**: Confirm architecture diagrams are omitted for Lessons 1-6 (process/communication & linear flows).
- [x] **Sub-task 24.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 24.5**: Update task tracker and provide Docker Compose / SQL verification steps.
## Phase 25: FDE Curriculum Pipeline — Module 5: Enterprise Communication, Consulting & LLM Engineering (Lessons 7-12 of 12 — MODULE 5 COMPLETE) (Completed)
- [x] **Sub-task 25.1**: Ingest 6 Lesson chapter bodies for `enterprise-consulting-llm` (Lessons 7-12) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 25.2**: Wire 12 Concept Checks (2 per lesson) and 41 Practice Questions across all 6 lessons (53 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 25.3**: Confirm architecture diagrams are omitted for Lessons 7-12 per §8a inclusion test criteria.
- [x] **Sub-task 25.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 25.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 26: FDE Curriculum Pipeline — Module 6: Agentic Systems & Enterprise Integrations (Lessons 1-6 of 11) (Completed)
- [x] **Sub-task 26.1**: Ingest 6 Lesson chapter bodies for `agentic-systems-integrations` (Lessons 1-6) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 26.2**: Wire 12 Concept Checks (2 per lesson) and 38 Practice Questions across all 6 lessons (50 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 26.3**: Confirm architecture diagrams are omitted for Lessons 1-6 per §8a inclusion test criteria.
- [x] **Sub-task 26.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 26.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 27: FDE Curriculum Pipeline — Module 7: Application Engineering, Security & Reliability (Lessons 1-6 of 12) (Completed)
- [x] **Sub-task 27.1**: Ingest 6 Lesson chapter bodies for `application-security-reliability` (Lessons 1-6) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 27.2**: Wire 12 Concept Checks (2 per lesson) and 39 Practice Questions across all 6 lessons (51 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 27.3**: Confirm architecture diagrams are omitted for Lessons 1-6 per §8a inclusion test criteria.
- [x] **Sub-task 27.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 27.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 28: FDE Curriculum Pipeline — Module 6: Agentic Systems & Enterprise Integrations (Lessons 7-11 of 11 — MODULE 6 COMPLETE) (Completed)
- [x] **Sub-task 28.1**: Ingest 5 Lesson chapter bodies for `agentic-systems-integrations` (Lessons 7-11) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 28.2**: Wire 10 Concept Checks (2 per lesson) and 33 Practice Questions across all 5 lessons (43 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 28.3**: Add architecture diagram for Lesson 10 (`10-build-crm-to-ai-support-copilot`) highlighting the multi-actor webhook/orchestrator/MCP-worker/human-approval topology.
- [x] **Sub-task 28.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 28.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 29: FDE Curriculum Pipeline — Module 7: Application Engineering, Security & Reliability (Lessons 7-12 of 12 — MODULE 7 COMPLETE) (Completed)
- [x] **Sub-task 29.1**: Ingest 6 Lesson chapter bodies for `application-security-reliability` (Lessons 7-12) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 29.2**: Wire 12 Concept Checks (2 per lesson) and 36 Practice Questions across all 6 lessons (48 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 29.3**: Confirm architecture diagrams are omitted for Lessons 7-12 per §8a inclusion test criteria.
- [x] **Sub-task 29.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 29.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 30: FDE Curriculum Pipeline — Module 8: System Design, Capstone & Hiring Readiness (Lessons 1-5 of 14) (Completed)
- [x] **Sub-task 30.1**: Ingest 5 Lesson chapter bodies for `system-design-capstone` (Lessons 1-5) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 30.2**: Wire 10 Concept Checks (2 per lesson) and 35 Practice Questions across all 5 lessons (45 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 30.3**: Add architecture diagrams for Lessons 2, 3, 4, and 5 illustrating tiered vector index retrieval, agent platform isolation topology, multi-tier SaaS isolation, and enterprise integration hub respectively.
- [x] **Sub-task 30.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 30.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 31: FDE Curriculum Pipeline — Module 8: System Design, Capstone & Hiring Readiness (Lessons 6-10 of 14) (Completed)
- [x] **Sub-task 31.1**: Ingest 5 Lesson chapter bodies for `system-design-capstone` (Lessons 6-10) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 31.2**: Wire 10 Concept Checks (2 per lesson) and 32 Practice Questions across all 5 lessons (42 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 31.3**: Add architecture diagram for Lesson 8 (`08-capstone-sprint-2-core-build-and-integration-layer`) illustrating the orchestrator-worker recommendation flow with highlighted human-approval gate.
- [x] **Sub-task 31.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 31.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 32: FDE Curriculum Pipeline — Module 8: System Design, Capstone & Hiring Readiness (Lessons 11-14 of 14 — MODULE 8 & ENTIRE FDE CORE CURRICULUM COMPLETE) (Completed)
- [x] **Sub-task 32.1**: Ingest 4 Lesson chapter bodies for `system-design-capstone` (Lessons 11-14) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 32.2**: Wire 8 Concept Checks (2 per lesson) and 24 Practice Questions across all 4 lessons (32 total MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 32.3**: Confirm architecture diagrams are omitted for Lessons 11-14 per §8a inclusion test criteria.
- [x] **Sub-task 32.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 32.5**: Update task tracker and provide final Docker Compose / SQL verification steps across all 104 lessons.

## Phase 33: FDE Elective Pipeline — Containerization & Orchestration (Lessons 1-6 of 17) (Completed)
- [x] **Sub-task 33.1**: Ingest 6 Lesson chapter bodies for `elective-containerization-orchestration` (Lessons 1-6) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 33.2**: Wire 12 Concept Checks (2 per lesson) and 39 Practice Questions across all 6 lessons (51 total MCQs, including 6 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 33.3**: Confirm architecture diagrams are omitted for Lessons 1-6 per §8a inclusion test criteria.
- [x] **Sub-task 33.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 33.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 34: FDE Elective Pipeline — Containerization & Orchestration (Lessons 7-12 of 17) (Completed)
- [x] **Sub-task 34.1**: Ingest 6 Lesson chapter bodies for `elective-containerization-orchestration` (Lessons 7-12) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 34.2**: Wire 12 Concept Checks (2 per lesson) and 41 Practice Questions across all 6 lessons (53 total MCQs, including 6 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 34.3**: Add architecture diagram for Lesson 10 (`10-kubernetes-architecture`) modeling the 6-actor control-plane to worker handoff path.
- [x] **Sub-task 34.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 34.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 35: FDE Elective Pipeline — Containerization & Orchestration (Lessons 13-17 of 17 — MODULE COMPLETE) (Completed)
- [x] **Sub-task 35.1**: Ingest 5 Lesson chapter bodies for `elective-containerization-orchestration` (Lessons 13-17) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 35.2**: Wire 10 Concept Checks (2 per lesson) and 33 Practice Questions across all 5 lessons (43 total MCQs, including 5 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 35.3**: Add architecture diagram for Lesson 13 (`13-kubernetes-networking`) modeling the Service, Endpoints, and NetworkPolicy decoupled routing path.
- [x] **Sub-task 35.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 35.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 36: FDE Elective Pipeline — AWS Multi-Region Cloud Deep Dive (Lessons 1-6 of 17) (Completed)
- [x] **Sub-task 36.1**: Ingest 6 Lesson chapter bodies for `elective-aws-multi-region-cloud-deep-dive` (Lessons 1-6) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 36.2**: Wire 12 Concept Checks (2 per lesson) and 43 Practice Questions across all 6 lessons (55 total MCQs, including 12 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 36.3**: Confirm architecture diagrams are omitted for Lessons 1-6 per §8a inclusion test criteria.
- [x] **Sub-task 36.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 36.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 37: FDE Elective Pipeline — AWS Multi-Region Cloud Deep Dive (Lessons 7-12 of 17) (Completed)
- [x] **Sub-task 37.1**: Ingest 6 Lesson chapter bodies for `elective-aws-multi-region-cloud-deep-dive` (Lessons 7-12) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 37.2**: Wire 12 Concept Checks (2 per lesson) and 40 Practice Questions across all 6 lessons (52 total MCQs, including 12 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 37.3**: Confirm architecture diagrams are omitted for Lessons 7-12 per §8a inclusion test criteria.
- [x] **Sub-task 37.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 37.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 38: FDE Elective Pipeline — AWS Multi-Region Cloud Deep Dive (Lessons 13-17 of 17 — MODULE COMPLETE) (Completed)
- [x] **Sub-task 38.1**: Ingest 5 Lesson chapter bodies for `elective-aws-multi-region-cloud-deep-dive` (Lessons 13-17) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 38.2**: Wire 10 Concept Checks (2 per lesson) and 32 Practice Questions across all 5 lessons (42 total MCQs, including 12 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 38.3**: Confirm architecture diagrams are omitted for Lessons 13-17 per §8a inclusion test criteria.
- [x] **Sub-task 38.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 38.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 39: FDE Elective Pipeline — Storage, Networking & Reliability for FDEs (Lessons 1-7 of 14) (Completed)
- [x] **Sub-task 39.1**: Ingest 7 Lesson chapter bodies for `elective-storage-networking-reliability` (Lessons 1-7) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 39.2**: Wire 14 Concept Checks (2 per lesson) and 44 Practice Questions across all 7 lessons (58 total MCQs, including 8 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 39.3**: Confirm architecture diagrams are omitted for Lessons 1-7 per §8a inclusion test criteria.
- [x] **Sub-task 39.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 39.5**: Update task tracker and provide Docker Compose / SQL verification steps.

## Phase 40: FDE Elective Pipeline — Storage, Networking & Reliability for FDEs (Lessons 8-14 of 14 — MODULE & ENTIRE FDE CURRICULUM COMPLETE) (Completed)
- [x] **Sub-task 40.1**: Ingest 7 Lesson chapter bodies for `elective-storage-networking-reliability` (Lessons 8-14) into `api/Data/FdeCurriculumSeedData.cs` (`GetAuthoredFdeLessonContent`).
- [x] **Sub-task 40.2**: Wire 14 Concept Checks (2 per lesson) and 47 Practice Questions across all 7 lessons (61 total MCQs, including 12 code-block MCQs) into `app/src/data/lessonInteractions.js`.
- [x] **Sub-task 40.3**: Add architecture diagrams for Lesson 10 (`10-designing-for-high-availability-multi-region-active-active`) and Lesson 11 (`11-fault-tolerance-engineering-circuit-breakers-retries-and-backoff`).
- [x] **Sub-task 40.4**: Confirm `app/src/data/lessonExerciseAssociations.js` remains unchanged (no coding exercises in this phase).
- [x] **Sub-task 40.5**: Update task tracker and provide final Docker Compose / SQL verification steps across all 152 authored lessons.

## Phase 41: Authentication Infrastructure & Administrator User Governance (Completed)
- [x] **Sub-task 41.1**: Add `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.28) package reference to `api/StudyTracker.Api.csproj`.
- [x] **Sub-task 41.2**: Implement `AppUser` entity model with snake_case column mappings, role/status constraints, and `DbSet<AppUser> Users` in `StudyTrackerContext.cs`.
- [x] **Sub-task 41.3**: Add sealed DTO records (`SignupRequest`, `LoginRequest`, `RejectUserRequest`, `UserDto`) in `api/Models/AuthDtos.cs`.
- [x] **Sub-task 41.4**: Implement zero-external-dependency PBKDF2 password hashing service (`Rfc2898DeriveBytes.Pbkdf2`) and constant-time verification.
- [x] **Sub-task 41.5**: Implement provider-agnostic SMTP notification service (`SmtpEmailNotificationService`) with safe logging fallback.
- [x] **Sub-task 41.6**: Implement JWT token generation and cookie-based extraction with `AllowCredentials()` CORS policy in `Program.cs`.
- [x] **Sub-task 41.7**: Add minimal-API endpoints (`/api/auth/signup`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/admin/users`, `/api/admin/users/{id}/approve`, `/api/admin/users/{id}/reject`) with RFC 7807 problem details.
- [x] **Sub-task 41.8**: Seed initial system administrator account in `DbSeeder.cs` (`admin@neuralascent.local`).
- [x] **Sub-task 41.9**: Create EF Core schema migration `20260904103000_AddAppUsersTable.cs` and update model snapshot.
- [x] **Sub-task 41.10**: Implement Frontend client credentials support (`client.js`), `AuthContext`, `ProtectedRoute`, Warm Editorial `AuthPage.jsx`, and `AdminDashboard.jsx`.
- [x] **Sub-task 41.11**: Add comprehensive unit tests in `AuthAndUserManagementTests.cs`.

## Phase 42: Mandatory Time-Based One-Time Password (TOTP) Second-Factor Authentication (Completed)
- [x] **Sub-task 42.1**: Extend `AppUser` entity with `totp_secret_encrypted`, `totp_enabled`, and `last_accepted_totp_counter`.
- [x] **Sub-task 42.2**: Implement `MfaChallenge` entity (`mfa_challenges` table) with 5-minute expiry, purpose check constraint (`'Enrollment'`, `'Login'`), attempt tracking, and cascade delete on `AppUser`.
- [x] **Sub-task 42.3**: Implement zero-dependency AES-GCM secret encryption wrapper `TotpSecretProtector` with 12-byte random nonces and 16-byte authentication tags.
- [x] **Sub-task 42.4**: Implement RFC 6238 TOTP engine `TotpService` with 20-byte cryptographically random secrets, RFC 4648 unpadded Base32 encoding, Google Authenticator/Authy `otpauth://` URI generation, RFC 4226 dynamic truncation HMAC-SHA1 codes, and counter-based replay attack protection.
- [x] **Sub-task 42.5**: Configure ASP.NET Core Fixed Window Rate Limiter policy (`"AuthPolicy"`, 10 req/min) on sensitive auth endpoints.
- [x] **Sub-task 42.6**: Refactor `POST /api/auth/login` to return single-purpose `challengeId` and withhold JWT session cookie until 2FA completes.
- [x] **Sub-task 42.7**: Implement `POST /api/auth/totp/enroll/start`, `POST /api/auth/totp/enroll/confirm`, and `POST /api/auth/totp/verify` with brute-force lockout (burn challenge after 5 failures).
- [x] **Sub-task 42.8**: Create EF Core database schema migration `20260904111500_AddTotpMfaChallenges.cs` and update `StudyTrackerContextModelSnapshot.cs`.
- [x] **Sub-task 42.9**: Update Docker Compose environment variables with `Auth__TotpEncryptionKey`.
- [x] **Sub-task 42.10**: Update frontend API client (`api.auth.totpEnrollStart`, `totpEnrollConfirm`, `totpVerify`), `AuthContext`, Warm Editorial 2-step setup and verification UI in `AuthPage.jsx`, and custom styles in `AuthPage.css`.
- [x] **Sub-task 42.11**: Add unit tests in `TotpServiceTests.cs`, `TotpSecretProtectorTests.cs`, and `AuthAndUserManagementTests.cs`.

## Phase 43: Consolidated Auth Hardening, Offline QR, Admin Operations & Lesson-Scoped AI Chat ($2/day Hard Cap) (Completed)
- [x] **Sub-task 43.1**: Password Hashing & Sanitation — Updated PBKDF2 default iterations to 210,000; removed default admin seeding from `DbSeeder.cs`; implemented `--seed-admin` CLI command in `api/Program.cs` reading from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars.
- [x] **Sub-task 43.2**: Auth & Rate Limiter Hardening — Implemented enumeration protection on signup; updated `"AuthPolicy"` rate limiter window to 10 req / 15 min; unified JWT cookie name to `na_auth` with 12h lifetime.
- [x] **Sub-task 43.3**: Admin Operations & TOTP Reset — Enforced fresh DB caller check (`LoadApprovedAdminAsync`) on every admin endpoint; added `POST /api/admin/users/{id}/reset-totp` with emergency SQL recovery documentation; added `GET /api/admin/usage/today` and `GET /api/admin/usage/by-user`.
- [x] **Sub-task 43.4**: Sustainability & Notifications — Added required sustainability notice to `SmtpEmailNotificationService.cs` approval emails.
- [x] **Sub-task 43.5**: Chat Models & Budget Guard — Created `ChatConversation`, `ChatMessage`, and DTOs; registered DbSets and entity constraints in `StudyTrackerContext.cs`; implemented `BudgetGuardService` enforcing $2.00/day aggregate spend cap and 500 requests/day volume backstop.
- [x] **Sub-task 43.6**: Llama API Client — Implemented direct `HttpClient` Llama API integration with 30s timeout, isolated `TryParseUsage` with character fallback estimation (`ceil(chars/4.0)`), and lesson-grounded prompt assembly.
- [x] **Sub-task 43.7**: Chat Endpoints — Implemented `POST /api/chat/conversations`, `POST /api/chat/conversations/{id}/messages` (with idempotency, budget checks, lesson grounding, and history context), and `GET /api/chat/conversations/{id}/messages`.
- [x] **Sub-task 43.8**: Database Migrations — Created EF Core migration `20260904120000_AddChatTables.cs` and Designer file; updated `StudyTrackerContextModelSnapshot.cs`.
- [x] **Sub-task 43.9**: Frontend Offline QR Code & Admin Operations — Integrated `qrcode` for client-side offline QR code rendering in `AuthPage.jsx`; added Reset TOTP action and AI compute budget tracking card in `AdminDashboard.jsx`.
- [x] **Sub-task 43.10**: Floating Chat Widget — Implemented `ChatWidget.jsx` and `ChatWidget.css` using Warm Editorial Knowledge Atlas design tokens; integrated `<ChatWidget lessonId={chapter?.id} />` in `ChapterReader.jsx`.
- [x] **Sub-task 43.11**: Security & Fail-Fast Hardening — Eliminated hardcoded fallback keys in `Program.cs`, `JwtTokenService.cs`, and `TotpSecretProtector.cs` with ephemeral dev keys and production fail-fast `InvalidOperationException`; restored `${VAR:?VAR must be set}` validation in `docker-compose.yml`; gated Llama API mock fallback behind non-production in `LlamaApiClient.cs`.
- [x] **Sub-task 43.12**: Decouple JwtTokenService & Neutralize JwtOptions — Removed redundant `JwtOptions` merge logic from `JwtTokenService.cs` making `AuthOptions` the single source of truth; set `JwtOptions.SecretKey = string.Empty` eliminating the last hardcoded fallback secret in the codebase.

## Phase 44: Localization Lab — Foundation, Workflow Orchestrator, Snapshots, Google MT, Vendor Marketplace & AI Boundary (Completed)
- [x] **Sub-task 44.1**: EF Core Entity Models — Implemented 12 entity models (`LocalizationProject`, `LocalizationLocale`, `LocalizationString`, `LocalizationTranslation`, `WorkflowStep`, `BuildSnapshot`, `BuildSnapshotLocaleCount`, `Vendor`, `MarketplaceJob`, `MarketplaceBid`, `LedgerEntry`, `ProviderHealthSnapshot`) in `api/Models/Localization/`.
- [x] **Sub-task 44.2**: DbContext & Schema Migration — Registered 12 `DbSet<T>` properties, constraints, and unique indices in `StudyTrackerContext.cs`; created migration `20260905120000_AddLocalizationLab.cs`, Designer file, and updated `StudyTrackerContextModelSnapshot.cs`.
- [x] **Sub-task 44.3**: Options, Exceptions & DTOs — Implemented `GoogleTranslateOptions.cs`, domain-specific exceptions in `LocalizationExceptions.cs`, and sealed DTO records in `LocalizationDtos.cs`.
- [x] **Sub-task 44.4**: Hand-Written AI Boundary Stubs — Created `ITranslationProvider` and `IQualityScorer` interfaces; implemented `MtOptimizeService`, `QpsScoringService`, and `AutoRoutingService` stubs throwing `NotImplementedException` (501 response).
- [x] **Sub-task 44.5**: Backend Services — Implemented `LocalizationProjectService`, `LocalizationStringService`, `WorkflowService` (actions execution & reordering), `SnapshotService`, `CreditLedgerService` (price band formula), `GoogleTranslateProviderService`, `MarketplaceService` (job posting, awarding, approving), `VendorPortalService`, and `ProviderHealthService`.
- [x] **Sub-task 44.6**: Minimal API Endpoints & DI Wiring — Created `LocalizationEndpoints.cs`, `MarketplaceEndpoints.cs`, `VendorPortalEndpoints.cs`, and `ProviderHealthEndpoints.cs` with RFC 7807 problem details; registered all services and endpoint groups in `Program.cs`.
- [x] **Sub-task 44.7**: Database Seeding — Implemented `LocalizationSeedData.cs` seeding project `auroraline-hud-v3`, 5 locales, 6 strings with `de-DE` stage data, 3 workflow steps, 3 snapshots, 5 vendors, marketplace states, and provider health; wired into `DbSeeder.cs`.
- [x] **Sub-task 44.8**: Frontend API Client & Route Registration — Added `api.localization` and `api.vendorPortal` namespaces to `client.js`; configured flat routes in `App.jsx`; updated Lab B card and lessons in `LabProjects.jsx` to link to `/lab-projects/localization`.
- [x] **Sub-task 44.9**: Owner App Pages & Components — Implemented `LocalizationShell.jsx` (nav cluster, provider health button, project picker, live dot, user profile, 4-tab bar), `ProviderHealthPanel.jsx` (metrics drawer & outage toggle), `LocalizationStrings.jsx` (ruled table, dot-track, needs-review flag, edit drawer with Save & Next, review banner), `LocalizationWorkflow.jsx` (step cards, reordering, run button with 501 boundary notice, add step), `LocalizationSnapshots.jsx` (snapshots table, cut snapshot, manifest drawer), `LocalizationMarketplace.jsx` (locale status overview, post confirmation drawer), and `LocalizationBidReview.jsx` (bids table & award action).
- [x] **Sub-task 44.10**: Standalone Vendor Portal — Implemented `VendorPortalShell.jsx` (isolated header, vendor roster switcher, no owner nav), `VendorOpenJobs.jsx` (matching open jobs grid, card layout), `BidSubmissionModal.jsx` (centered modal, midpoint price estimation), and `VendorMyJob.jsx` (awarded job workspace, inline translations, no stage column, submit for review).

## Phase 45: AI Agent Service Infrastructure & Routing Scaffold (Completed)
- [x] **Sub-task 45.1**: Docker Compose Integration — Added `ai-agent` service to `docker-compose.yml` with backend network isolation, JWT environment variables, and health check; added `ai-agent` dependency to `app` service.
- [x] **Sub-task 45.2**: Nginx Routing Scaffold — Added HTTP-to-HTTPS redirect and reverse proxy server blocks for `tutor.${DOMAIN_NAME}` pointing to `http://ai-agent:8000` in `app/default.conf.template`.
- [x] **Sub-task 45.3**: Python FastAPI Service Skeleton — Created `ai-agent/requirements.txt`, `ai-agent/Dockerfile`, and `ai-agent/main.py` with public `/health` endpoint, startup check for `JWT_SIGNING_KEY`, `get_current_user` dependency validating .NET-issued JWT tokens (via `Authorization: Bearer <token>` or `na_auth` cookie), and protected `/me` endpoint.

## Phase 46: Dynamic Practice Questions Architecture Migration (Completed)
- [x] **Sub-task 46.1**: One-Time MCQ Extraction — Created `scripts/migrate-mcqs-to-db.mjs` and extracted 1,182 unique questions across 181 lesson entries (1,200 question instances, 4,800 options, 146 `FROM_MATERIAL`, 1,054 `LLM_GENERATED`) into `scripts/mcq-migration-data.json` and `api/Data/mcq-migration-data.json`.
- [x] **Sub-task 46.2**: EF Core Entity Models & Migration — Implemented `McqQuestion`, `McqOption`, `McqPresentation`, and `McqAttempt` in `api/Models/`; configured relationships and unique constraints in `StudyTrackerContext.cs`; created migration `20260922050000_AddMcqDynamicTables.cs` and Designer file.
- [x] **Sub-task 46.3**: Idempotent Database Seeder — Implemented `McqMigrationSeedData.cs` resolving `(courseSlug, moduleSlug, lessonSlug)` to real `lesson_id`s with batch saving (every 250 records) and `legacy_key` deduplication; wired as step 10 in `DbSeeder.cs`.
- [x] **Sub-task 46.4**: Backend Service & Minimal APIs — Created `McqService.cs` with server-side option shuffling and `McqPresentation` logging (excluding `isCorrect` and `explanation`), and idempotent attempt submission with race-condition recovery; registered in `Program.cs` and added `GET /api/v2/practice-questions/{courseSlug}/{moduleSlug}/{lessonSlug}` and `POST /api/v2/practice-questions/{presentationId}/attempts` in `V2Endpoints.cs`.
- [x] **Sub-task 46.5**: Frontend Integration & Static Fallback — Extended `app/src/api/client.js` with `api.v2.getPracticeQuestions` and `api.v2.submitPracticeAttempt`; updated `PracticeQuestions.jsx` to fetch dynamic questions on mount, render server-shuffled order, and evaluate attempts via POST with fallback; wired course/module/lesson slugs in `ChapterReader.jsx`.
- [x] **Sub-task 46.6**: Non-Destructive Verification — Preserved `app/src/data/lessonInteractions.js` in place as fallback data source; verified zero syntax issues and complete schema integrity.

## Phase 47: Parking Lot Coding Exercises Live Grading Wiring (Completed)
- [x] **Sub-task 47.1**: Author `generate-parking-ticket` Exercise (`java-lld-generate-parking-ticket`) — Created lean `pom.xml`, copied 32 solution Java files, created 32 starter Java files with TODO stubs for 7 editable files (`TicketServiceImpl`, 4 in-memory repos, 2 assignment strategies), copied `TestTicketController.java`, and configured `exercise.json` with 7 evidence items mapped to `@Test` methods.
- [x] **Sub-task 47.2**: Author `display-parking-lot-capacity` Exercise (`java-lld-display-parking-lot-capacity`) — Created lean `pom.xml`, copied 24 solution Java files, created 24 starter Java files with TODO stubs for 3 editable files (`ParkingLotServiceImpl`, `InMemoryParkingLotRepositoryImpl`, `ParkingFloorUtils`), copied `ParkingLotControllerTest.java`, and configured `exercise.json` with 7 evidence items mapped to `@Test` methods.
- [x] **Sub-task 47.3**: Wire Lesson 20 Exercise Associations — Registered both exercise IDs under `java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot` in `app/src/data/lessonExerciseAssociations.js`.
- [x] **Sub-task 47.4**: Comprehensive Contract Audit — Executed `scripts/verify_parking_lot_exercises.py` confirming 100% manifest schema validity, file existence, test method reflection mappings, and non-editable file byte parity.

## Phase 48: Additive Spring Boot (Java 17) Exercise Sandbox Extension (Completed)
- [x] **Sub-task 48.1**: Create Java 17 Runner Image — Authored `runner/java-spring/Dockerfile` using `maven:3.9.9-eclipse-temurin-17` and copied `run.sh` from `runner/java/run.sh` leaving `runner/java/*` 100% untouched.
- [x] **Sub-task 48.2**: Extend Execution Options — Added `RunnerImagesByProfile` dictionary to `ExerciseExecutionOptions.cs`, increased global `MaxExecutionSeconds` from 120 to 240, and expanded `MemoryLimitBytes` from 768MB to 1.5GB (`1_610_612_736`).
- [x] **Sub-task 48.3**: Dynamic Profile Resolution — Implemented `ResolveRunnerImage` in `LocalDockerExerciseRunner.cs` supporting per-profile resolution with hyphen/underscore normalization and fallback to default `RunnerImage`.
- [x] **Sub-task 48.4**: Docker Compose Wiring — Added `ExerciseExecution__RunnerImagesByProfile__java-maven-spring` mapping to `docker-compose.yml`.
- [x] **Sub-task 48.5**: Regression Verification — Verified all 67 existing exercises continue using `java-maven` and resolve to `neuralascent-java-runner:dev` via `scripts/verify_spring_runner_extension.py`.
