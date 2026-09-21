# Session 2026-09-21 — Ingestion pipeline Phase A (DB + schema + migrations) + provider/scope decisions

**Purpose of this file**: if you're picking this up in a brand-new chat, read
this before doing anything else. It covers everything since
[SESSION-2026-09-20-langfuse-integration-and-docker-compose.md](SESSION-2026-09-20-langfuse-integration-and-docker-compose.md)
(read that one too, and the ones it points back to, for working-style rules).

**This session's job was Phase 1.2's foundation, not the content extractors
themselves.** Phase A (DB connectivity, `content_chunks` schema + indexes,
idempotent migrations) is done and verified live against the real local
database. Phase B (actually reading and chunking lesson content) has not
started — that's the next chat's job.

---

## 0. Orientation — one important change from prior sessions

**`ai-agent/` is now hand-written by the user, not Local-LLM/Gemini-prompted**,
even though `CLAUDE.md`'s AI-integration scope rule would otherwise allow
prompts for this directory. This was an explicit, deliberate call: AI-assisted
coding has eroded raw coding fluency enough to hurt in interviews, so the
user is deliberately writing `ai-agent/`'s Python by hand — even where it's
slower — as practice. (Saved as a standing memory:
`feedback_ai_agent_hand_written.md`.)

**What this means for how Claude should behave here, going forward:**
Claude's role for `ai-agent/*.py` is explain-concepts-and-point-at-files,
the same lighter-touch role already established for
`docker-compose*.yml`/deploy scripts — **not** full working code, and **not**
copy-paste-ready Local-LLM prompts. When asked "what should go in this
file," walk through it field-by-field/step-by-step (imports and why, what
each piece does and why, version-specific gotchas to verify rather than
trust blindly) and let the user type the actual implementation. This was
tested repeatedly this session (`db.py`, `main.py`'s lifespan hook,
`migrate.py`) and worked well — don't regress to writing full files even if
asked to move faster, unless the user explicitly says to drop the rule (they
were asked directly via AskUserQuestion once already and chose "keep the
rule, walk me through it instead").

Everything else about Claude's write permissions is unchanged: only
`CLAUDE.md`, the memory directory, `info/.notes/`, and `exercises/` are
directly editable by Claude. Everything else — including all of `ai-agent/`
— Claude explains, the user writes.

---

## 1. What got done this session

### 1.1 Provider decision: DeepInfra for both embedding and reranking (final)

Long back-and-forth this session, worth NOT re-litigating:

- Priced DeepInfra's `bge-m3` ($0.01/M tokens) against every real
  alternative: AWS Bedrock (Titan Embed V2 at 2× the price; Titan
  Multimodal G1, Cohere Embed v3/v4, Nova Multimodal all 10–13.5×), and
  India-native options (Sarvam AI and Krutrim Cloud both confirmed via live
  checks of their actual model catalogs/pricing pages to have **no
  embedding models at all** — Sarvam is Indic-language/speech-only, Krutrim
  is text-gen/speech/image only; AICredits.in is a real, UPI-billed proxy in
  front of DeepInfra at ~10% markup, viable if payment friction becomes a
  real blocker but not cheaper).
- Same result for reranking: DeepInfra's `bge-reranker-v2-m3` vs. AWS's
  Amazon Rerank 1.0 — Bedrock's flat $0.001/query vs. DeepInfra's
  token-metered pricing works out to roughly 10–125× more expensive on
  Bedrock depending on chunk size, confirmed with real numbers.
- Real AWS Bedrock native models were seriously considered and explicitly
  rejected for a second reason beyond price: Titan/Cohere/Nova are all
  **closed, proprietary weights** — no self-host path — which breaks the
  project's own locked sequencing decision (`bge-m3`/`bge-reranker-v2-m3`
  chosen specifically because they're usable as a cheap cloud API *now* and
  self-hostable on a future local GPU backend *later*, same weights, no
  re-embed needed).
- **User's own DeepInfra risk concern, noted for the record (not disputed,
  a legitimate judgment call):** a prepaid wallet balance at DeepInfra is
  not recoverable if unused for any reason (bad service, business risk,
  etc.) — user already loaded ~$5 and accepts this risk for a personal
  project at this budget scale. If this ever becomes a real blocker,
  AICredits.in (UPI-billed proxy, ~10% markup) is the documented fallback.
- Interview narrative angle (deliberate): Muse Spark 1.3 stays as the model
  for the higher-intelligence agent work (skill analysis, learning-path
  shaping) regardless of "enterprise approval" concerns — that's a
  contained piece where peak capability matters more than vendor
  standing. The RAG backbone (embeddings/reranking) staying on
  DeepInfra/open-weights (not a specific "enterprise-only" vendor) is a
  conscious choice the user plans to defend in interviews directly, not
  something Claude should second-guess or re-raise.

### 1.2 Exercise content source corrected — `problems` table is NOT it

Scanned the actual workspace rather than assuming: the `problems` DB table
(only 5 rows in the local dev DB, confirmed via direct query; admin-only
manual-insert endpoint, no bulk seed data) is **not** the real exercise
content. The real, substantial, already-fully-wired-into-the-live-app
exercise system is **`exercises/java/java-lld/**/exercise.json`** on disk:

- **65 real exercises** across **9 topics** (`advanced-collections`,
  `applied-machine-coding`, `concurrency`, `design-patterns`, `oop-1`
  through `oop-4`, `solid-principles`), covering **17 distinct lessons**
  (linked via `lessonSlug`, a string match to `lessons.slug` — not a DB
  foreign key).
- Each exercise folder: `exercise.json` (manifest with `id`, `lessonSlug`,
  `title`, `difficulty`, `runtime`, `files[]`, `testSuite`, and an
  `evidence[]` array — each entry a plain-English claim like *"findMax(...)
  returns the largest Integer in the array"* mapped to a JUnit test method),
  `pom.xml`, `starter/`, `solution/`, `tests/`.
- Fully wired into the live app already:
  [api/Services/Exercises/ExerciseRepository.cs](../../api/Services/Exercises/ExerciseRepository.cs)
  loads manifests at API startup (with real security hardening — rejects
  symlinks, validates no path escapes the exercise root, requires
  `pom.xml`, requires the test file to exist),
  [ExerciseService.cs](../../api/Services/Exercises/ExerciseService.cs)/
  [ExerciseWorkspaceBuilder.cs](../../api/Services/Exercises/ExerciseWorkspaceBuilder.cs)
  run the sandboxed Maven test execution,
  [ExerciseEndpoints.cs](../../api/Endpoints/ExerciseEndpoints.cs) exposes
  it, and
  [ImplementationExercise.jsx](../../app/src/components/learning/ImplementationExercise.jsx)/
  [useExerciseWorkspace.js](../../app/src/hooks/useExerciseWorkspace.js) is
  the real in-browser UI.

**Implication for ingestion (Phase D, not started):** exercise ingestion
reads from `exercises/**/exercise.json` + `solution/**/*.java` on disk, not
from `problems`. `problems` is settled as out of scope — 5 rows isn't
worth building a pipeline for, and it's not what the live app actually uses
for exercises anyway.

### 1.3 Ingestion content scope, finalized: three types

1. **Lessons (prose)** — `lessons.content_body`, filtered
   `content_status = 'Published'`, hierarchical H2→H3→H4 chunking. No
   lesson `.md` files exist on disk anymore (checked, confirmed) — the DB
   row is the only source, the `.md` was purely an authoring-time input to
   the original `.md → Local LLM → seed data → Postgres` pipeline.
2. **MCQs** — embedded inside `content_body`, not a separate table. Extract
   atomically (one MCQ = one chunk) before/during the hierarchical split so
   an MCQ never gets sliced mid-block.
3. **Exercises** — from `exercises/**/exercise.json` (see §1.2), resolved to
   `lesson_id` via `lessonSlug → lessons.slug`. Three sub-chunk-types per
   exercise: manifest (atomic), evidence entries (atomic, one per array
   item), solution code (AST-chunked via tree-sitter — not yet set up).

### 1.4 Phase A — ingestion pipeline foundation, built and verified live

Five-phase build order was planned this session (A: shared foundation, B:
lessons, C: MCQs, D: exercises, E: embedding + orchestration). **Only Phase
A is done.** Built by the user, by hand, with Claude walking through
each piece conceptually (imports and why, not finished code) — see §0 above
for why that mattered this session specifically.

**A1 — DB connectivity** ([ai-agent/db.py](../../ai-agent/db.py),
[ai-agent/main.py](../../ai-agent/main.py)):
- `psycopg[binary]==3.3.6` (async mode) + `psycopg_pool==3.3.2` +
  `pgvector==0.5.0` — versions pinned properly in
  [requirements.txt](../../ai-agent/requirements.txt) after an early bug
  where `==3.2.x` (literal `.x`, invalid PEP 440 syntax) was caught and
  fixed before it ever reached a real build failure.
- `AsyncConnectionPool` built module-level in `db.py`, `open=False`
  (required behavior for `psycopg_pool` 3.2+ — verified against real docs,
  not assumed), with a `configure=` callback running
  `await register_vector_async(conn)` (the async-specific variant of
  `pgvector.psycopg`'s type registration — confirmed this distinct function
  exists and matters, not just the sync `register_vector`).
- Pool lifecycle wired via a FastAPI `lifespan` context manager in
  `main.py`: `await pool.open()` before `yield`, `await pool.close()`
  after.
- `config.py` got a new `DATABASE_URL` read, same fail-fast pattern as the
  existing `JWT_SIGNING_KEY`/`MUSE_AI_API_KEY` vars.
- `docker-compose.yml`'s `ai-agent.environment` block got
  `DATABASE_URL: postgresql://${POSTGRES_USER:-studyuser}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB:-studytracker}`
  — reusing `api`'s existing DB credential vars, not inventing new ones.

**Real debugging arc worth knowing about, not just the end state:**
1. `DATABASE_URL environment variable is unset` even after the compose edit
   — root cause was a **stale container**, kept crash-looping by
   `restart: unless-stopped` without ever re-reading the updated compose
   file. `restart` (policy-triggered or `docker compose restart`) reuses a
   container's existing baked-in environment; only a fresh `docker rm -f`
   + `up -d --build` picks up compose file changes. Confirmed via
   `docker inspect <container> --format '{{json .Config.Env}}' | grep
   DATABASE_URL` returning nothing on the stale container.
2. `POSTGRES_PASSWORD` resolved to the literal placeholder string
   `your_secure_password_here` — same class of bug as the
   `JWT_SIGNING_KEY`/`TOTP_ENCRYPTION_KEY` placeholder-not-replaced gotcha
   from the Sep-13 session, different variable this time. Turned out to
   already be the real local dev password (Postgres only applies
   `POSTGRES_PASSWORD` on first volume init, so whatever was in `.env` at
   that moment is what stuck) — not actually broken, just insecure and
   worth rotating later, not blocking.
3. `vector type not found in the database` at pool-connect time — the
   `vector` extension check via `CREATE EXTENSION IF NOT EXISTS vector`
   reported "already exists, skipping" when finally run explicitly, so this
   resolved itself (likely already present from earlier local dev work);
   restarting `ai-agent` to get fresh pool connections after that cleared
   it.
4. `AttributeError: 'AsyncConnection' object has no attribute 'executr'` —
   a typo the user caught and fixed themselves, committed as `efb31f1
   Fixed compiler error`.

**A2/A3 — schema + indexes**
([ai-agent/migrations/002_create_content_chunks.sql](../../ai-agent/migrations/002_create_content_chunks.sql)):

```sql
CREATE TABLE content_chunks (
    id              BIGSERIAL PRIMARY KEY,
    content_hash    TEXT NOT NULL UNIQUE,
    lesson_id       INT NOT NULL REFERENCES lessons(id),
    module_id       INT NOT NULL,
    chunk_type      TEXT NOT NULL,
    section_path    TEXT,
    concept_tags    TEXT[] NOT NULL DEFAULT '{}',
    content_quality_tier TEXT,
    source_type     TEXT,
    raw_text        TEXT NOT NULL,
    token_count     INT,
    embedding       VECTOR(1024),
    search_vector   TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', raw_text)) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX content_chunks_embedding_idx ON content_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX content_chunks_search_idx ON content_chunks USING GIN (search_vector);
```

Design reasoning (won't re-derive if asked again — see this session's full
chat log for the complete why/what/how/when on every column and index
choice if a deeper rationale is ever needed):
- `module_id`/`concept_tags` denormalized onto the chunk row (not joined at
  query time) — retrieval-latency tradeoff, values essentially never change.
- `chunk_type` lets one table hold three structurally different content
  types (prose/mcq/exercise_manifest/exercise_evidence/exercise_code)
  without a UNION across separate tables.
- `search_vector` is a `GENERATED ALWAYS AS ... STORED` column deliberately
  — can never drift out of sync with `raw_text`, no manual maintenance.
- `HNSW` over `IVFFlat` — no upfront `lists` tuning needed, better recall
  at this corpus's small scale (a few hundred to low thousands of chunks).
- `VECTOR(1024)` — `bge-m3`'s native dense dimension; **not yet verified
  against a real DeepInfra API response**, only against general knowledge —
  confirm this on the first real embedding call in Phase E.

**A4 — idempotent migrations**
([ai-agent/migrate.py](../../ai-agent/migrate.py),
[ai-agent/migrations/](../../ai-agent/migrations/)):
- `001_enable_pgvector_extension.sql` (`CREATE EXTENSION IF NOT EXISTS
  vector;`) + `002_create_content_chunks.sql` above.
- `schema_migrations(filename PRIMARY KEY, applied_at)` tracking table,
  created unconditionally (`IF NOT EXISTS`) on every run.
- Runner: lists `migrations/*.sql` sorted by filename (numeric prefix =
  execution order), skips anything already recorded, otherwise runs the
  file's SQL + records it in one `conn.transaction()` block (atomic —
  never half-applied-but-unrecorded or vice versa).
- **Proven live, not just written**: first run applied both files; second
  run printed `already applied, skipping` for both. Verified independently
  via `\d content_chunks` (confirmed exact schema + both indexes present)
  and `SELECT * FROM schema_migrations` (both rows present).
- Multi-statement SQL in one `conn.execute(sql)` call (the three statements
  in `002_...sql`) worked fine in one call on this psycopg3 version — this
  was flagged as uncertain going in, confirmed working empirically, not
  something to worry about further.

### 1.5 Build tracker updated

[ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)
§1.2 now reflects Phase A as done, the `problems`-vs-`exercises/` scope
correction, and the DeepInfra provider decision — read that file's §1.2
directly for the current checkbox state rather than assuming from this
narrative alone (checkboxes are the source of truth per that file's own
stated purpose).

---

## 2. Current git state

Committed already, this session (per `git log`):
```
efb31f1 Fixed compiler error
b5c70e0 Adding SQL Schemas for RAG implementations
bb18fc8 Added pgvector db to docker yaml
d989313 Added psycopg_pool, register_vector_async, lifespan pool open/close
```
Uncommitted as of this session's end: `info/.notes/ai-learning-agent-BUILD-TRACKER.md`
(the update described in §1.5). Run `git status --short` to confirm current
state — not captured with 100% precision at end of session.

---

## 3. Pending — the actual next work

### 3.1 Phase B — lessons prose extractor (next real work, not started)
- Read `lessons.content_body` via the pool from `db.py`, filtered
  `content_status = 'Published'`.
- Join `course_modules` (for `module_id` metadata) and
  `lesson_concept_links → knowledge_concepts` (for `concept_tags`).
- Hierarchical H2→H3→H4 markdown chunking.
- Write chunk rows into `content_chunks` (embedding left null/placeholder
  for now — Phase E wires DeepInfra in last, deliberately, so chunking
  bugs and API-call bugs aren't debugged simultaneously).
- Goal of this phase specifically: prove the whole pipeline shape
  (read → chunk → store → idempotent rerun) end-to-end on the simplest
  content type, not lessons content quality itself.

### 3.2 Phase C — MCQ extraction (after B, shares its read path)
Extract MCQ blocks from the same `content_body` before/during the H2/H3/H4
split, atomic chunks, same lesson-level metadata as their parent section.

### 3.3 Phase D — exercises (after C, most complex — new source + new tool)
Read `exercises/**/exercise.json` + `solution/**/*.java`, resolve
`lessonSlug → lesson_id`, three chunk types (manifest/evidence/code).
Requires setting up tree-sitter + a Java grammar for the code-chunking
piece — not yet done, isolate this risk to its own step rather than mixing
it into B/C's simpler string-splitting logic.

### 3.4 Phase E — embedding wiring + orchestration script (last)
Small reusable DeepInfra `bge-m3` call function, wired in only once B–D
produce stable chunks. Then the top-level `ingest.py` orchestrating all
three extractors → embed → upsert via `content_hash` (same
`ON CONFLICT ... DO UPDATE` idempotency pattern as the migration runner).

### 3.5 Longer-horizon, unchanged
- Deepinfra API key already provisioned and in use (confirmed working via
  this session's ~$5 already loaded) — **no longer a blocker**, remove that
  framing if it appears in older notes.
- Everything under Phase 1.3 (RAG retrieval), 1.4 (Tutor Agent), 1.5 (eval
  harness) in the build tracker — untouched this session.

---

## 4. If you're a fresh session reading this cold

1. `git status --short` — confirm §2's snapshot still holds.
2. Read `CLAUDE.md` — confirm the write-permission rules haven't changed,
   **especially** the `ai-agent/` hand-written-by-user rule from §0 above,
   since that's a recent, easy-to-miss deviation from CLAUDE.md's own
   stated AI-integration scope rule.
3. Read [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)
   §1.2 for the current checkbox state — more authoritative than this
   file's narrative for "what's actually done."
4. Confirm Phase A still holds by re-running the two-command idempotency
   proof:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml exec ai-agent python migrate.py
   ```
   Should print `already applied, skipping` for both files. If it errors or
   re-applies, something regressed — investigate before starting Phase B.
5. Start Phase B per §3.1 above — walk through it the same way A1–A4 were
   done in this session's chat log (step-by-step, why/what/how/when,
   user writes the actual code).
