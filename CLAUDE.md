# Neuralascent — Claude Working Rules

## ⛔ NO DIRECT CODE CHANGES

Claude does **not** have permission to edit, create, or delete any file in this repository.

This applies to:
- Source code (`.cs`, `.jsx`, `.js`, `.tsx`, `.ts`, `.css`, `.html`)
- Data files (`.json`, `.md` inside `app/` or `api/`)
- Configuration files (`docker-compose.yml`, `.env*`, `*.csproj`, `appsettings*.json`)
- Seed data (`api/Data/*.cs`)
- Any other file in the repo

**The only exceptions are:**
- This file (`CLAUDE.md`)
- The memory directory
- Files inside `info/.notes/` — Claude may read and write these (reference guides, notes, pipeline docs). These are meta/documentation files with no effect on the running app.
- Files inside `exercises/` — Claude may create and edit exercise directories (`.json`, `.xml`, `.java` files). These are exercise manifests, pom files, starter stubs, test classes, and reference solutions. Claude must never modify an existing exercise that is already wired and working; only create new ones or fix a broken one the user explicitly flags.

---

## ✅ WHAT CLAUDE CAN DO

1. **Read** any file in the repo freely for analysis and context.
2. **Produce prompts** — detailed, technical, fully self-contained prompts for the Local LLM to execute the actual file changes.

---

## HOW TO PRODUCE A PROMPT

When the user describes a task, Claude must:

1. **Read all relevant files** first — do not write prompts based on assumptions.
2. **Include exact file paths** (relative to repo root) for every file the LLM must read or modify.
3. **Show the before/after** or describe the exact change with enough specificity that there is no ambiguity (line numbers, function names, the exact string to find).
4. **State constraints** — what must NOT be changed alongside what must be changed.
5. **State output expectations** — what the LLM should produce (full file? diff? specific section?).
6. **Include the code style** observed in the file (naming conventions, import order, quote style, spacing) so the LLM matches it.

Prompts must be **copy-paste ready** — the user pastes them directly into the Local LLM without editing.

---

## PROJECT CONTEXT

- **App**: Neuralascent (`neuralascent.top`) — a personal editorial learning platform for Java/Spring backend + applied AI
- **Stack**: React (frontend, `app/`), C# ASP.NET Core (API, `api/`), PostgreSQL (DB via Docker)
- **Content pipeline**: Lesson `.md` file → Local LLM → C# seed data (`JavaVerticalSeedData.cs`) → PostgreSQL
- **Design philosophy**: All content on the same page — no separate quiz or exercise pages
- **Target audience**: Developers with 7–8+ years of experience; content must not be basic
- **Local run**: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`
- **Write-once seeding gotcha**: Lessons with `ContentBody` containing `## Practical Backend Scenario`, `## Practice Loop`, and `## Evidence of Understanding` are never overwritten by the seeder. To force a reseed: `UPDATE lessons SET content_body = '', content_status = 'Outline' WHERE slug = '<slug>';` then restart API — and also ensure `BackfillLessonContent` sets `ContentStatus = 'Draft'` when it writes content.

---

## CONTENT QUALITY STANDARD

Reference guide: `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md`

Word count tiers:
- **Foundational / conceptual lessons**: 500–800 words
- **Advanced mechanism lessons** (SOLID, design patterns, concurrency): 1200–1500 words

SOURCE_TYPE convention (for MCQs and exercises in lesson `.md` files):
- `FROM_MATERIAL` — sourced from provided reference material
- `LLM_GENERATED` — added independently by the LLM
