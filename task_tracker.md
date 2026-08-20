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
- [x] **Sub-task 13.8**: Update `App.jsx`, `LabProjects.jsx`, and `Navbar.jsx` with routes (`/reading-map`, `/lab-projects`) and navigation tabs



