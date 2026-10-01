# OPUS Run Progress

Branch: `claude/opus-3-stage-d88sa1` (never push `main`; no deploys; no EC2/AWS/SSM; no secrets; never change `content_status`; no DB writes).
Prompt: `info/.notes/opus-cloud-prompt-3-stage-audit-and-ai-agent-hardening.md`

## Status
| Stage | Status |
|---|---|
| 1 Audit | **Complete** (2026-10-01) |
| 2 Chapter updates | **Complete** (2026-10-01), local commit on this branch, not pushed; see Stage 2 below |
| 3 `ai-agent/` hardening | Not started — waits for owner "go Stage 3" and approval of report §B items |

## Stage 1
- Files changed: `info/.notes/OPUS-AUDIT-REPORT.md` (new), `info/.notes/OPUS-RUN-PROGRESS.md` (new). Nothing else.
- Method: 5 parallel Sonnet 5.5 sub-agents (machine-coding inventory, seeded lessons, ai-agent code, deploy/CI, info/ tree); orchestrator re-verified high-severity ai-agent and deploy claims in the code. **Nothing was executed**; runtime behaviour is inferred from code. The orchestrator was Sonnet 5.5, not Opus 5.5.
- Headline findings: (d) `DATABASE_URL` never produced by the deploy path (Critical for prod); unauthenticated `/echo` and `/agent_test` publicly proxied; fresh-DB migration deadlock; rollback deletes crash logs; no Python tests/CI. All defects (a)–(h) confirmed.
- Content headline: Java L2/L3 seed bodies are empty; Splitwise exercises exist but are unwired; BookMyShow has no exercise; MCQ correct answer is the longest option in 94 % of questions; 58 templated lessons thin and effectively locked.
- Decisions made: none beyond audit scope. Locked decisions (bge-m3, LangGraph, Pydantic AI, Langfuse, Muse/Nova/Gemini, HNSW, hybrid retrieval) respected and not re-opened.

## What remains
- Owner answers to report §D (esp. 1, 4, 5, 6).
- Stage 2 and Stage 3 work lists are in report §C.

## Exact next action
Owner reviews and merges the Stage 1 PR, answers §D, then says "go Stage 2" or "go Stage 3" (naming the §A/§B items approved). A fresh session starts from this file, reads the report, and begins with §C item 1 of the named stage.

## EC2 follow-up steps (placeholder, filled in during Stage 3; owner runs later)
To be written in Stage 3. Expected topics: confirm SSM env has `DATABASE_URL` (or `DATABASE_*`), `MUSE_AI_API_KEY`, `LANGFUSE_*`; confirm prod DB image is pgvector; run `migrate.py` once; check `schema_migrations`/`content_chunks`.

## Stage 2 — Java vertical content (2026-10-01)

Authorised by the owner (relayed by the orchestrating session) to edit Java-vertical lesson/exercise content only, overriding CLAUDE.md for this task. No DB writes, no `content_status` changes, no deploys, no push.

### Stage 1 findings re-verified against the code
| Stage 1 claim | Verdict |
|---|---|
| L2/L3 empty bodies (no case in `GetAuthoredLessonContent`) | **False.** Both cases exist as C# `or` patterns (`"02-oop-1-intro-lab" or "02-oop-classes-objects"`, `"03-oop-2-access-modifiers-encapsulation" or "03-oop2-encapsulation-inheritance"`); 1,025 and 1,385 words, all headings. A plain `"slug" =>` grep misses them. No change made. |
| Splitwise exercises unwired to L22 | True. Practice-pool sources are Spring Boot 3 + JPA + Lombok (Java 17). The runner only supports `java-maven` (`ExerciseWorkspaceBuilder` throws for any other profile), so they could not be wired as-is. |
| No BookMyShow exercise anywhere | **False.** `0.Exercises` has 4 BMS zips (`1773391369_aa02…` ratings, also in practice-pool; `1789721304_196f…` create show; `1789729988_b93c…` book ticket; `1789730688_7e2a…` signup/login). None was wired. |
| L17 capstone 357 w, L24 hotel 629 w | True (356 / 628). L24 also misdescribed its own exercises (date ranges, "completed" session, rate × duration). |
| Dangling `ConceptNextLesson` slugs | True: 9 of 10. Note: `KnowledgeAtlasSeedData.Seed` returns early once domains exist, and `ConceptDetailPopover.jsx` ignores `lessonSlug` (it guesses a slug from the title), so the fix only affects fresh databases. |
| Spring L14–17 thin | True (321–363 w). |
| Extra (found this stage) | L21's Practical Backend Scenario contradicted its own Concepts (in-memory lock, `LOCKED`, 5-min TTL versus `BLOCKED`, 15 min, `SERIALIZABLE`, and "synchronized fails across pods"). L5, L21, L22 Practice Loops have 6 steps (contract says 5). L18–L20 Practice Loops do not use `1.` numbering (not checked further). |

### Files changed
- `api/Data/JavaVerticalSeedData.cs`: replaced bodies of `24-machine-coding-hotel-management` (628 → 1,216 w), `17-machine-coding-capstone` (356 → 1,338 w), `14-spring-boot-core` (321 → 1,216 w), `15-spring-data-jpa` (363 → 1,221 w), `16-spring-rest-api` (325 → 1,233 w). All have the 5 contract sections with `###` sub-headings, 5-step loops, and a one-line Reference; each case carries a `// SOURCE_TYPE:` comment (L24 FROM_MATERIAL with LLM_GENERATED scenario figures; the other four LLM_GENERATED, needing owner review). Rewrote one paragraph of the L21 scenario to match its Concepts. No metadata, `ContentStatus`, or seeding logic touched.
- `api/Data/KnowledgeAtlasSeedData.cs`: 8 `LessonSlug` values now resolve (`java-concurrency` → `06-concurrency-1-threads`; the 7 FDE targets → their real FDE slugs). `next-security` left as is (ambiguous; see Questions).
- New exercises (`java-maven`, Java 11, in-memory repositories; Lombok, JPA and Spring stripped, following the hotel-* precedent):
  - `exercises/java/java-lld/applied-machine-coding/splitwise-create-delete-group/` (`java-lld-splitwise-create-delete-group`, 6 tests). FROM_MATERIAL: Scaler zip `1773391465_1711…` / practice pool.
  - `exercises/java/java-lld/applied-machine-coding/splitwise-manage-group-members/` (`java-lld-splitwise-manage-group-members`, 14 tests). FROM_MATERIAL: Scaler zip `1773391463_7dc9…` / practice pool.
  - `exercises/java/java-lld/applied-machine-coding/bms-book-ticket/` (`java-lld-bms-book-ticket`, 8 tests). FROM_MATERIAL: Scaler zip `1789729988_b93c…` (6 tests ported); 2 tests LLM_GENERATED (unavailable-id reporting, and an 8-thread race that uses a slow-`getStatus` `ShowSeat` subclass so a lock-free solution fails deterministically). Uses typed exceptions instead of the original's bare `Exception`.
  - Ported tests keep the original scenarios and assertions, with Spring DI replaced by constructor wiring and `.toList()` replaced by `Collectors.toList()` for Java 11. A few assertions were added (creator is the admin, group survives an unauthorised delete, a member row exists before delete, seats untouched on failure).
- `app/src/data/lessonExerciseAssociations.js`: added entries for L21 (`java-lld-bms-book-ticket`) and L22 (both Splitwise ids). No existing entry changed.
- `info/.notes/verify-new-exercises.sh`: appended the 3 new exercise paths.

### Validation run
- `mvn test` (JDK 21 with `-Dmaven.compiler.release=11`, plus the repo verify script): all 3 solutions pass (6/6, 14/14, 8/8); all 3 starters compile and fail. The race test failed a lock-free variant 3/3 (8 of 8 bookings succeeded) and passed the reference 5/5.
- `dotnet build`: **not run.** No SDK in the container and `builds.dotnet.microsoft.com` is blocked by proxy policy. Substitute: a tree-sitter C# parse of both seed files reports 0 syntax errors (negative control: an injected unescaped quote produced 109 errors), and each new body round-trips byte-for-byte from the C# verbatim string to the Markdown draft. **Owner must still run `docker compose ... build api` or `dotnet build api`.**
- Association test (vitest, isolated copy): 4/4 pass. All 20 association ids resolve to an `exercise.json` with a matching `lessonSlug` (70 manifests).

### Remaining / not done
- **Write-once gotcha.** Existing DB rows for L14–17 (Spring) and L24 already contain all three headings, so `BackfillLessonContent` will **not** overwrite them; the new text reaches only fresh databases unless the owner reseeds those 5 slugs (CLAUDE.md procedure). L21's scenario fix has the same limitation. The atlas fix applies only to a fresh atlas seed.
- No new MCQs were written. MCQs for L17 and L14–16 remain LLM_GENERATED.
- BMS zips for create-show, ratings, and signup are still unwired. Unwired practice-pool items remain.
- The 6-step Practice Loops (L5, L21, L22) were not normalised.

### Questions for owner
1. Reseed the 5 rewritten slugs (and L21) locally/in prod using the CLAUDE.md procedure? That resets `content_status` to Draft for those rows.
2. `next-security` (title "Next Security", module "Application Engineering & Reliability", under the concurrency concept): which lesson should it point to, or should the row be removed?
3. OK that ported exercises changed the original contract slightly: typed BMS exceptions, extra assertions, and an LLM-added concurrency test?
4. Wire the other three BMS zips (create show, ratings, signup/login) next?
5. Normalise L5/L21/L22 Practice Loops to 5 steps, or are 6 steps acceptable for machine-coding lessons?
6. Is the advanced tier (1,200–1,500 w) right for the Spring lessons, or do you want them at the foundational 500–800?

### Exact next action
Owner runs `dotnet build api` (or the docker compose build) and the API container locally, opens L17, L21, L22, L24, and L14–16 after reseeding (Q1), runs one exercise from each new directory through the UI, answers the Questions, then says "go Stage 3".

