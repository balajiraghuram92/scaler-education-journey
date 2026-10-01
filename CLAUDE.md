# Neuralascent — Claude Working Rules

## ⛔ NO DIRECT CODE CHANGES

Claude does **not** have permission to edit, create, or delete any file in this repository.

This applies to:
- Source code (`.cs`, `.jsx`, `.js`, `.tsx`, `.ts`, `.css`, `.html`)
- Data files (`.json`, `.md` inside `app/` or `api/`)
- Configuration files (`docker-compose.yml`, `.env*`, `*.csproj`, `appsettings*.json`)
- Seed data (`api/Data/*.cs`)
- Any other file in the repo

**The only exception is:**
- The memory directory
- Files inside the `info/` folder (including `info/.notes/` and `info/history/`) — Claude may read and write these (reference guides, notes, trackers, pipeline docs). These are meta/documentation files with no effect on the running app.

Everything else — including `exercises/`, `ai-agent/`, `api/`, `app/`, deploy scripts, compose files, workflows and this file (`CLAUDE.md`) — is read-only for Claude. For those, Claude reviews, explains, and produces prompts or guidance; the user makes the edits.

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
- **Write-once seeding gotcha**: Lessons with `ContentBody` containing `## Practical Backend Scenario`, `## Practice Loop`, and `## Evidence of Understanding` are never overwritten by the seeder. To force a reseed: (1) check status first — `SELECT slug, content_status FROM lessons WHERE slug IN (...)`; the reseed sets `Published` lessons back to `Draft`, so republish them manually after review; (2) run `UPDATE lessons SET content_body = '', content_status = 'Outline' WHERE slug IN ('<slug>', ...);` through `docker exec -i studytracker-postgres psql -U studyuser -d studytracker` (local) — restarting the API alone does NOT seed; (3) run the seeder: `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data` (the `[deploy]` pipeline runs the same step on EC2). `BackfillLessonContent` sets `ContentStatus = 'Draft'` when it writes content.
- **DB names**: local compose uses container `studytracker-postgres`, user `studyuser`, database `studytracker` (lowercase); the API container is `studytracker-api`. Prod (EC2) uses database `StudyTrackerDB`. SQL must go through `psql` (for example `docker exec -i ... psql <<'SQL' ... SQL`), never typed into the shell.

---

## CONTENT QUALITY STANDARD

Reference guide: `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md`

Word count tiers:
- **Foundational / conceptual lessons**: 500–800 words
- **Advanced mechanism lessons** (SOLID, design patterns, concurrency): 1200–1500 words

SOURCE_TYPE convention (for MCQs and exercises in lesson `.md` files):
- `FROM_MATERIAL` — sourced from provided reference material
- `LLM_GENERATED` — added independently by the LLM

---

## AI-VERTICAL vs AI-INTEGRATION — SCOPE BOUNDARY (set 2026-09-04)

Neuralascent has two separate "AI" tracks. Do not conflate them.

1. **AI vertical (curriculum content)** — a learning vertical/course on the site about AI/LLM engineering topics (e.g. the Model Economics Matrix / RAG eval-harness portfolio project). This content is **authored entirely by hand by the user**. Claude must never generate a Local-LLM or Gemini prompt to write, seed, or edit AI-vertical lesson content, and must not treat pasted AI-vertical project descriptions as a request to produce seed-data prompts. Claude's role here is limited to reading/organizing notes (e.g. under `info/.notes/`) if asked — never producing content-generation prompts for it.

2. **AI integration (site infrastructure)** — actual AI/LLM plumbing built into the running app itself (e.g. the learner-facing tutoring chatbot described in `info/.notes/Chatbot-implementation/references/neuralascent-chatbot-hld-dotnet.md`). This is infrastructure work in `api/` (.NET) and `app/` (React), and **is** in scope for the Local-LLM/Gemini prompt workflow described above — read the relevant files, then produce a copy-paste-ready prompt exactly as for any other API/frontend change.

Rule of thumb: if the change would touch `api/Data/*SeedData.cs` or lesson `.md`/content authoring for an AI-topic vertical → hand-authored, no prompt. If the change touches `api/Endpoints`, `api/Services`, `api/Models`, `api/Options`, `api/Program.cs`, `app/src/**`, `docker-compose*.yml`, or `appsettings*.json` to add AI-provider plumbing (e.g. Gemini client, chat endpoints, config) → normal prompt workflow applies.
