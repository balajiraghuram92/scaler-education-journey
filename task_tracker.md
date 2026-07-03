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

## Phase 5: Dockerization & Azure Deployment
- [x] **Sub-task 5.1**: Containerize Frontend and Backend (Write `Dockerfile`s & `docker-compose.yml`)
- [ ] **Sub-task 5.2**: Azure Frontend: Deploy React App to **Azure Static Web Apps**
- [ ] **Sub-task 5.3**: Azure Backend: Deploy ASP.NET Core API to **Azure App Service** (Free Tier)
