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
- [ ] **Sub-task 6.2**: Deploy the backend to Azure Container Apps (Serverless, $0/month).
- [ ] **Sub-task 6.3**: Configure Azure Container App environment variables for passwordless SQL connection.
