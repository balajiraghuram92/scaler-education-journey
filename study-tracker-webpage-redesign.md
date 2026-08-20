# Neuralascent Study Tracker Webpage Redesign — Technical Specifications & Phased Implementation Tracker

**Architecture Mode:** Warm Editorial "Knowledge Atlas" System  
**Reference Document:** `info/images-newdesign/Study-tracker.png` (Panel B: Progress / Reading Map)  
**Full Suite Reference:** 4-Panel Composite Architecture (`Home-page.png`, `Study-tracker.png`, `Curiculam-updator.png`, `Learning-homepage.png`)  
**Active Stack:** React 19 + ASP.NET Core 8 Minimal API + PostgreSQL 16 (ARM64 Docker Compose)  
**Target Migration Stack:** Java 21 / Spring Boot 3 + Spring Data JPA (`api-java`)  

---

## 1. Executive Summary & Design Vision

The Neuralascent Webpage Redesign completely supersedes legacy fitness-tracker/SaaS dashboard chrome (gauges, percentage rings, radar spider-charts) with an authentic, tactile **"Warm Editorial Knowledge Atlas"** reading and progression experience.

### Core Aesthetic Pillars
* **Canvas Background:** Warm Parchment (`#F8F6F0` / `#F7F3EA`) with crisp paper contrast (`#FFFFFF`).
* **Editorial Typography:**
  * Primary Headlines & Quotations: *Newsreader* / *Playfair Display* literary serifs.
  * Body & Lists: *Plus Jakarta Sans* / *Inter* humanist sans-serif.
  * Code & Pipelines: *JetBrains Mono* / *Berkeley Mono*.
* **Ink & Accent Palette:**
  * Ink Text: Deep Charcoal `#1A1A1A` / Muted Slate `#4A5568`
  * Primary Sage Accent: `#2C5E55` (Subtle highlights, active indicators)
  * Hairline Rules & Dividers: `#E5E0D8` (Replaces heavy card borders and drop-shadows)

---

## 2. Technical Architecture & End-to-End Data Pipeline

```
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   FRONTEND (React 19 + Vite)                                     │
 │                                                                                                  │
 │  • Component: `ReadingMap.jsx` (`pages/ReadingMap.jsx` / `pages/LabProjects.jsx`)               │
 │  • CSS: `ReadingMap.css` (Fluid Asymmetric 3-Column CSS Grid with clamp() typography)            │
 │  • Visuals: Custom SVG Timeline Activity Sparkline + Directional Semantic Knowledge Badges       │
 │  • State: Dynamic fetching from `/api/reading-map` with robust fallback & local update events    │
 └────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │ HTTP GET / POST / PUT (x-api-key auth)
                                                  │ Content-Type: application/json
                                                  ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   BACKEND (ASP.NET Core 8 Minimal API)                           │
 │                                                                                                  │
 │  • Endpoint: `GET /api/reading-map`, `POST /api/reading-map/items`, `PUT /api/reading-map/toggle`│
 │  • ORM: Entity Framework Core 8 (`Npgsql.EntityFrameworkCore.PostgreSQL`)                        │
 │  • Data Projections: `ReadingMapDto`, `ReadingCategoryGroupDto`, `KnowledgeThreadDto`             │
 │  • Startup Seeder: `ReadingMapSeedData.cs` called in `DbSeeder.cs`                               │
 └────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │ Npgsql TCP Connection (Port 5432)
                                                  │ Strict FK Cascades & Schema Integrity
                                                  ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   DATABASE (PostgreSQL 16 Alpine)                                │
 │                                                                                                  │
 │  • Table: `reading_map_items` (Id, Category, Title, SubText, OrderIndex, IsCompleted, Date)     │
 │  • Table: `knowledge_threads` (Id, Domain, PathDescription, StepsJson, OrderIndex)               │
 │  • Table: `reading_activity_logs` (Id, DayLabel, ActivityCount, LogDate, OrderIndex)             │
 └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema & API Contract Specification

### A. PostgreSQL Tables
```sql
-- Reading Map Items (Categorized streams)
CREATE TABLE IF NOT EXISTS reading_map_items (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL, -- 'ReadThisWeek', 'Revisited', 'Deferred', 'Lists', 'Prerequisites'
    title VARCHAR(255) NOT NULL,
    sub_text VARCHAR(100),
    order_index INT NOT NULL DEFAULT 0,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reading Activity Log (7-day timeline ticks)
CREATE TABLE IF NOT EXISTS reading_activity_logs (
    id SERIAL PRIMARY KEY,
    day_label VARCHAR(10) NOT NULL, -- 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'
    activity_count INT NOT NULL DEFAULT 0,
    order_index INT NOT NULL DEFAULT 0,
    log_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Knowledge Threads (Progression chains)
CREATE TABLE IF NOT EXISTS knowledge_threads (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(50) NOT NULL, -- 'Java', 'Backend', 'Cloud'
    raw_path TEXT NOT NULL,       -- 'Java → concurrency → virtual threads → structured concurrency'
    order_index INT NOT NULL DEFAULT 0
);
```

### B. REST API Endpoints & DTOs
```csharp
// Response DTO for GET /api/reading-map
public record ReadingMapDto(
    List<ReadingMapItemDto> ReadThisWeek,
    List<ReadingMapItemDto> Revisited,
    List<ReadingMapItemDto> Deferred,
    List<ReadingMapItemDto> Lists,
    List<ReadingMapItemDto> Prerequisites,
    List<DailyActivityDto> ActivityTimeline,
    List<KnowledgeThreadDto> KnowledgeThreads
);

public record ReadingMapItemDto(int Id, string Category, string Title, string? SubText, bool IsCompleted, int OrderIndex);
public record DailyActivityDto(int Id, string DayLabel, int ActivityCount, int OrderIndex);
public record KnowledgeThreadDto(int Id, string Domain, string RawPath, List<string> Nodes, int OrderIndex);
```

---

## 4. UI/UX Layout & Component Specifications (`Study-tracker.png`)

### Responsive Design Rules
1. **Desktop (> 1024px):** 3-column asymmetric layout (`1fr 0.8fr 1.4fr`) with generous whitespace, delicate hairline section rules, and horizontal activity sparkline.
2. **Tablet (768px - 1024px):** 2-column layout; Left & Lists stacked on Column 1, Prerequisites, Timeline & Knowledge Threads on Column 2.
3. **Mobile (< 768px):** Single column vertical reading stream with horizontal scroll or auto-wrapping for thread chains, maintaining full tactile legibility.

---

## 5. Phased Implementation Plan & Status Tracker

### Phase 1: Database & Backend Layer (.NET 8 + PostgreSQL)
- [x] **Task 1.1**: Define EF Core Entity Models (`ReadingMapItem.cs`, `ReadingActivityLog.cs`, `KnowledgeThread.cs`) in `api/Models/`
- [x] **Task 1.2**: Register DbSets and relationship mappings in `StudyTrackerContext.cs`
- [x] **Task 1.3**: Implement idempotent database seeder `ReadingMapSeedData.cs` with exact items from `Study-tracker.png`
- [x] **Task 1.4**: Implement Minimal API endpoint `GET /api/reading-map` with fast `AsNoTracking()` projections
- [x] **Task 1.5**: Implement mutation endpoints (`POST /api/reading-map/items`, `PATCH /api/reading-map/items/{id}/toggle`)
- [x] **Task 1.6**: Add EF Core migration (`20260820150000_AddReadingMapTables.cs`) & DDL schema creation safeguard in `DbSeeder.cs`

### Phase 2: Frontend Implementation (React 19 + Warm Editorial CSS)
- [x] **Task 2.1**: Implement `ReadingMap.jsx` component in `app/src/pages/ReadingMap.jsx`
- [x] **Task 2.2**: Implement `ReadingMap.css` with Warm Editorial design tokens (`#F8F6F0`, Newsreader serif, hairline borders)
- [x] **Task 2.3**: Build custom SVG **Reading Activity Sparkline** with dynamic bar heights, timeline labels (`Mon` → `Sun`), and forward arrow
- [x] **Task 2.4**: Build **Knowledge Threads** component rendering linear directional chains (`Java → concurrency → virtual threads → structured concurrency`)
- [x] **Task 2.5**: Wire asynchronous data fetching with optimistic fallback state in `ReadingMap.jsx`
- [x] **Task 2.6**: Update `App.jsx` routing to support `/lab-projects` and `/reading-map`
- [x] **Task 2.7**: Update `Navbar.jsx` and `Home.jsx` with direct navigation to the Reading Map

### Phase 3: Responsive Scaling & Visual Polish
- [x] **Task 3.1**: Implement fluid typography and container clamps (`max-width: 1280px`, padding scales)
- [x] **Task 3.2**: Test and refine layout behavior across 1920px (ultrawide), 1440px (desktop), 1024px (tablet), and 375px (mobile)
- [x] **Task 3.3**: Ensure pixel-perfect typographic fidelity matching `Study-tracker.png` (quotation marks ‘Reading Map’, bullet styling, section rules)
- [x] **Task 3.4**: Verify contrast ratios and accessibility for all ink tones and sage accents

### Phase 4: Full Suite Alignment & Migration Readiness
- [x] **Task 4.1**: Link Panel A (`Home.jsx` Knowledge Atlas) and Panel B (`ReadingMap.jsx`) seamlessly
- [x] **Task 4.2**: Verify Docker Compose build readiness on ARM64 EC2 architecture
- [x] **Task 4.3**: Prepare Java 21 / Spring Boot 3 API equivalent contracts in `api-java` documentation
