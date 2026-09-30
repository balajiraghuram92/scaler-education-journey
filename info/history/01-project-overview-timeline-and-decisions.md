# 01 — Neuralascent: Project Overview, Working Rules, Timeline & Cross-Cutting Decisions

> **Start here** (after `00-INDEX.md`). Consolidated 2026-09-30 from `neuralascent-work-status.md`, `SESSION-HANDOFF-STATUS.md`, `local-llm-content-pipeline/00`, the
> Master Reference Guide header, `CLAUDE.md`, `agent.md`, `.agents/**` and every dated status header in `info/`. Written so a fresh LLM session needs no other context to orient.

## 1. What this is
- **Neuralascent** (`https://neuralascent.top`, repo `balajiraghuram92/scaler-education-journey`) — a **personal editorial learning platform** for Java/Spring backend + applied AI, and a portfolio/interview artifact. Owner/learner: **Raghuram Balaji** (`balajiraghuram92@gmail.com`; Coforge, India). Target audience of content: developers with **7–8+ years** of experience — content must not be basic.
- **Design philosophy:** everything for a lesson on **one page** (no separate quiz/exercise pages); warm-editorial visual identity, *not* a SaaS dashboard.
- **Stack (2026-09):** React 19 + Vite (`app/`) → Nginx → ASP.NET Core 8 minimal-API (`api/`, EF Core/Npgsql, C#) → PostgreSQL 16 (pgvector image since 2026-09-13); Python FastAPI `ai-agent/` (AI Tutor); Docker/Compose (dev only), GitHub Actions → GHCR → SSM → EC2 arm64; Java exercise runners `runner/java`, `runner/java-spring`; content in `api/Data/*SeedData.cs`; exercises `exercises/java/java-lld/**`.
- **Repo map:** `api/` .NET API · `app/` React · `ai-agent/` Python AI service · `exercises/` (`java/java-lld` wired, `practice-pool` raw source — long Windows paths) · `runner/` Docker exercise runners · `scripts/` deploy/backup/verify scripts (+ `mcq-migration-data.json`) · `deploy/` single-EC2 automation proposals · `docs/` (architecture map, learning docs) · `tests/StudyTracker.Api.Tests` · `.github/workflows/deploy-api.yml` · `info/` documentation (this history in `info/history/`) · `CLAUDE.md`, `agent.md`, `.agents/` agent rule files · `task_tracker.md` (old phase tracker, plus `.orig`).

## 2. Tracks and current status (2026-09-30)
| Track | Status | Read |
|---|---|---|
| **AI Learning Agent / AI Tutor (Python)** | **PRIMARY.** Phase 0 + 1.1 + 1.2-A done; ingestion extractors onward not started | `07` |
| Java LLD + FDE curriculum, exercise engine | Content largely authored (FDE 152/152; Java Modules 1–6+ authored; Lessons 21–23 authored later); exercise grading being debugged (bug #2 fix pending verification) | `02` |
| Website redesign / data migration | Redesign implemented (Aug); data reconciliation evidence still `Blocked` at capture; navigation later simplified to Chapters-only | `03` |
| Deployment / infra | Single arm64 EC2, digest-pinned SSM deploys working; RDS/ECS/CloudFront not started | `04` |
| Auth / TOTP / AI chat ($2/day) | Completed, committed (`a660f95`) — precursor of the AI Learning Agent | `06` |
| Localization Lab | **ON HOLD** — .NET/React side built; AI service unbuilt; not actually disabled in the app | `05` |
| Backend → Python migration (formerly "Java migration") | Planning only; strangler/contract-first principles; `ai-agent/` is the first slice | `08` |
| AI-vertical curriculum content (Model Economics Matrix etc.) | **Parked; hand-authored only** | `05`, `06` |
| Study plans / Azure certs / labs | Parallel interview-prep track (Jul 2026); AI-103/AI-200 plan | `08` |
Order of work (user, 2026-09-08): AI Learning Agent (all phases) → Localization Lab → everything else. (User's later explicit plan on 2026-09-22: finish exercise-grading verification on WSL2, repeat on EC2, *then* return to `ai-agent/`.)

## 3. Working rules — read before acting (from `CLAUDE.md`, memory, session handoffs)
1. **`CLAUDE.md` NO-DIRECT-CODE-CHANGES rule:** Claude may edit only `CLAUDE.md`, the memory directory, `info/.notes/**` and `exercises/**` (create new exercises; never modify an existing working one unless the user flags it broken). Everything else (`.cs`, `.jsx/.js/.ts/.tsx`, `.css`, `.html`, `.json`/`.md` inside `app/`,`api/`, compose, `.env*`, `*.csproj`, `appsettings*.json`, seed data) is changed by a **copy-paste-ready prompt** for the user's Local LLM ("Gemini"/3.8 Flash/Qwen), after Claude has *read* the relevant files: exact paths, before/after or exact change, constraints ("must NOT change"), output expectations, observed code style. Exception granted 2026-09-30 for the `info/` restructuring task only.
2. **AI Learning Agent exception:** `ai-agent/` and its supporting infra are **hand-written by the user**; Claude is architect/reviewer/concept-teacher only, no scaffolds or prompts (`07` §1).
3. **AI-vertical vs AI-integration** scope rule (`06` §1). AI-vertical lesson content: never generate prompts for it.
4. **Never trust a "done" report; re-verify** by rebuilding, recreating containers and hitting live endpoints. A 503 with no log line = suspect swallowed exceptions.
5. **Do not fabricate:** if a step conflicts with the file, STOP and report; ask when ambiguous. Ground technical claims; verify library facts against live docs (2026 versions postdate training data).
6. **Source-type labelling:** `FROM_MATERIAL` vs `LLM_GENERATED` for MCQs/exercises. Word counts: foundational 500–800, advanced mechanism 1200–1500.
7. **Windows gotcha:** some `exercises/practice-pool` paths are too long for Windows checkouts (`git config core.longpaths true`); avoid touching practice-pool.
8. **Deploy discipline:** only commits with `[deploy]` (or manual dispatch) deploy; workflow files are hand-edited by the user (agents suggest YAML only); `agent.md`/`.agents/AGENTS.md` (other agents) say the agent must not commit/push — the user does; `.agents/memory/git-policy.md` (Muse) says commit automatically, always ask before push; `.agents/memory/user-preferences.md`: never run builds directly, give Docker-Compose (WSL2) commands and the seeder command `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data`.  These rule sets differ by agent/tool — follow the one the active session declares.
9. **Write-once seeding gotcha** and its reseed recipe (`02` §4). **Local run:** `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build` (run `api --migrate` first on a fresh volume; `scripts/local-stack.sh` does it).
10. **Prod ≠ Compose:** prod = GHCR + SSM + `docker run`; prod secrets live in SSM; prod DB name `StudyTrackerDB` (`04`).
11. **Teaching style (AI-agent work):** don't teach Python syntax; do teach backend/AI concepts from scratch, just-in-time (`07` §1).

## 4. Master timeline (all dates 2026 unless noted)
| Date | Event |
|---|---|
| Jun 22–Jul 31 | Scaler class notes captured (raw notes in `info/.notes/scaler-raw-notes`, `input-notes`, `final-notes`) |
| Jul 2 | Interview-prep plans written: labs rebuild guide, Azure cert plan, FDE self-study + master calendar (Coforge AI Architect opening) — `08` |
| Aug 7 | "Migration to Java (Spring Boot 3) & AWS" tracker created (Phase 8; mentorship mode) — now Python migration, `08` |
| Aug 20 | Reading Map/Study-tracker redesign implemented (`20260820150000_AddReadingMapTables`) — `03` |
| Aug 23 | Redesign data-migration architecture + tracker + local-LLM prompt pack; VM/Docker runtime handoff; stabilization ledger (11 defects) — `03` |
| Aug 24 | Curriculum modernization (FDE 104 + 48 elective drafts; Java +117 chapters); future AWS platform-migration plan — `03`, `08` |
| Aug 28 | Master Reference Guide v2.3; knowledge map; Tier-1/Tier-2 quality tiers verified live — `02` |
| Aug 31 | Session handoff (17 exercises wired, MCQ migration, Lessons 18–20); chatbot HLD drafts — `02`, `06` |
| Sep 1 | FDE 152/152 authored; EC2 stale-content investigation; TODO tracker; Java-first roadmap — `02`, `06`, `08` |
| Sep 4–6 | Auth/approval/TOTP + $2/day Llama chat built; regression saga; AI-helper course review; two-track scope rule — `06` |
| Sep 5 | Localization Lab built and verified end-to-end; AI-service pivot to Python/FastAPI/vLLM — `05` |
| Sep 7 | AI Learning Agent design locked (cascade, memory, single-project decision); Localization disable prompt produced (not executed) — `07`, `05` |
| Sep 8 | Infra/tech-stack revision (Mac Studio inference, fresh TS + FastAPI, staged cutover); Phase 0 infra built — `07` |
| Sep 9–10 | Deploy debugging (test-compile errors, React hooks crash, private-repo curl, stale env file) — `04` |
| Sep 12–13 | JWT trust bridge live on EC2; production Postgres → pgvector — `04`, `07` |
| Sep 15 | Working-style rules; Phase 1 kickoff — `07` |
| Sep 18–19 | LangGraph scaffold, ADR-001 — `07` |
| Sep 20 | Langfuse tracing, Compose integration, first real EC2 deploy of `ai-agent` — `07`, `04` |
| Sep 21 | Ingestion Phase A (pool, `content_chunks`, migrations); DeepInfra decision; H3 hierarchy + MCQ coverage prompts — `07`, `02` |
| Sep 22 | Exercise-grading fixes (socket permission ✅, workspace files pending); dynamic MCQ DB schema (1182 questions); URGENT C# quote-escape fix — `02` |
| Sep 30 | **This consolidation** (info/ → `info/history/`, Java→Python migration reframing, AI-agent real-status audit) |
| Oct 16 | Gemini 2.5 Flash-Lite shutdown (eval-judge model must change) |
| mid-Oct / late-Nov / late-Dec | Phase 1 / 2 / 3 targets of the AI Learning Agent; **Dec 7** TLS cert expiry (renewal script) ; **Jan 2027** interview season |

## 5. Cross-cutting decisions index (details in the linked files)
Provider cascade & memory & embeddings (`07` §3) · orchestration ADR (`07` §3.1) · staged cutover .NET → Python (`08` §A) · write-once seeding (`02` §4) · dynamic MCQ schema (`02` §8) · exercise engine trust model (`02` §7) · Build-Locked localization + hand-written AI boundary (`05` §1) · auth architecture and no-hardcoded-secrets rule (`06` §2) · redesign additive-migration rule "no destructive change without evidence + human sign-off" (`03` §4–6) · single EC2, digest-pinned deploys, prod secrets in SSM (`04` §1) · Lombok stripped from exercises (`02` §7) · never delete legacy Verticals/Tasks rows (`02` §4, `03` §4).

## 6. Known documentation hazards
- Several docs carried stale "as of" statements (AI-agent "design only", runbook DB names, tracker "Phase 1 🚧"); this history states the verified position and flags the rest.
- Session handoffs quote commit hashes and line numbers that drift; run `git log`/`git status` before trusting them.
- Dates on prompt files are git-import dates (2026-09-05) rather than authoring dates.
- Info files never affect the running app (CLAUDE.md), but `parse_tasks.py` (repo root) reads `info/04-fde-curriculum-tracker.md`; `CLAUDE.md` cites the Master Reference Guide and the .NET chatbot HLD.
