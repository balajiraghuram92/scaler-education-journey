# Local LLM Prompt — Week 1–2 Foundation: FastAPI Copilot Service (naive RAG)

Paste everything below into the Local LLM as-is.

---

## Task

Add a new, isolated **FastAPI service** called `copilot` to this repo, wired into the existing Docker Compose stack, that does **naive RAG** over the `lessons` table: structure-aware markdown chunking, pgvector storage, single embedding model, naive top-k retrieval, and Langfuse tracing on every call. This is a **control-group baseline** — do not add hybrid search, reranking, or query rewriting. Keep it deliberately simple and correct.

## Files to read first (context, do not modify)

- `docker-compose.yml` — prod compose file, defines `database`, `api`, `app` services, network `backend-net`, volume `postgres_data`
- `docker-compose.dev.yml` — dev overlay, only overrides `api`/`app` build context; has no `database` key, so it inherits whatever image `docker-compose.yml` sets for `database`
- `.env.example` — current env var list
- `api/Models/Lesson.cs` — `lessons` table shape (Postgres column names in `[Column("...")]` attributes)
- `api/Models/CourseModule.cs` — `course_modules` table shape
- `api/Data/schema.sql` — actual DDL, confirm column/table names against this before writing SQL

## Hard constraints — do NOT touch

- Do not modify anything under `api/` (C#/.NET) or `app/` (React) except reading for reference.
- Do not modify `*.csproj` or `appsettings*.json`.
- All new code lives under a new top-level `copilot/` directory.
- The only existing files you may edit are `docker-compose.yml`, `docker-compose.dev.yml`, and `.env.example` — and only in the specific ways described below.
- Do not add hybrid search, RRF, reranking, query rewriting, or LangChain. This is the naive baseline; later weeks build on top of it separately. If you want a framework for the retrieval/generation call itself, use the provider SDK directly (e.g. `openai` Python SDK) — not LangChain.

## 1. Fix the Postgres image so pgvector is available

`postgres:16-alpine` (currently used by the `database` service in `docker-compose.yml`) does **not** ship the `pgvector` extension. Change the image so both prod and dev (dev inherits `database` from the base file) get it:

**`docker-compose.yml`**, in the `database` service:
```yaml
  database:
    image: pgvector/pgvector:pg16   # was: postgres:16-alpine
```
Everything else about that service (env, volumes, healthcheck, network) stays identical. `pgvector/pgvector:pg16` is a drop-in replacement built on the same Postgres 16 base with the extension pre-installed.

## 2. New migration — `lesson_chunks` table

Create `api/Data/migrations-copilot/001_pgvector_lesson_chunks.sql` (new directory, kept separate from the EF Core `api/Migrations/` folder since this is not an EF-managed table):

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS lesson_chunks (
    id              BIGSERIAL PRIMARY KEY,
    lesson_id       INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    module_slug     TEXT NOT NULL,
    module_title    TEXT NOT NULL,
    lesson_slug     TEXT NOT NULL,
    lesson_title    TEXT NOT NULL,
    heading_path    TEXT NOT NULL,          -- e.g. "Concurrency > Locks > ReentrantLock"
    content_type    TEXT NOT NULL DEFAULT 'lesson',  -- 'lesson' now; 'solution' reserved for later
    chunk_index     INTEGER NOT NULL,
    chunk_text      TEXT NOT NULL,
    token_count     INTEGER NOT NULL,
    embedding       VECTOR(1536) NOT NULL,  -- dimension for text-embedding-3-small; change if a different model is used
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS lesson_chunks_embedding_idx
    ON lesson_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS lesson_chunks_lesson_id_idx ON lesson_chunks (lesson_id);
CREATE INDEX IF NOT EXISTS lesson_chunks_content_type_idx ON lesson_chunks (content_type);
```

This file is applied manually (`psql -f ...` or the ingestion script runs it on startup — see §5) — it is not part of the .NET EF Core migration pipeline.

## 3. `copilot/` service layout

Create this exact structure:

```
copilot/
  Dockerfile
  requirements.txt
  .env.example
  app/
    __init__.py
    main.py
    config.py
    db.py
    tracing.py
    ingestion/
      __init__.py
      chunker.py
      embeddings.py
      ingest_lessons.py
    retrieval/
      __init__.py
      search.py
```

### `copilot/requirements.txt`
```
fastapi==0.115.*
uvicorn[standard]==0.32.*
asyncpg==0.30.*
pydantic==2.9.*
pydantic-settings==2.6.*
openai==1.54.*
tiktoken==0.8.*
langfuse==2.53.*
python-dotenv==1.0.*
```
(Pin exact patch versions available at build time; keep the same major/minor pins shown.)

### `copilot/app/config.py`
Pydantic `Settings` (from `pydantic_settings.BaseSettings`) reading from env, mirroring the naming style already used in `.env.example` (`POSTGRES_DB`, `API_KEY`, etc.):
- `database_url: str` — built from `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` + host `database` port `5432`, same as the API service's `ConnectionStrings__DefaultConnection` in `docker-compose.yml` but as a single asyncpg DSN
- `embeddings_api_key: str` (env `EMBEDDINGS_API_KEY`)
- `embeddings_model: str = "text-embedding-3-small"` (env `EMBEDDINGS_MODEL`)
- `langfuse_public_key: str` (env `LANGFUSE_PUBLIC_KEY`)
- `langfuse_secret_key: str` (env `LANGFUSE_SECRET_KEY`)
- `langfuse_host: str = "http://langfuse:3000"` (env `LANGFUSE_HOST`)
- `chunk_token_ceiling: int = 400` (env `CHUNK_TOKEN_CEILING`)

### `copilot/app/db.py`
An `asyncpg` connection pool, created on FastAPI startup (`lifespan` context manager), exposed via a module-level getter. Read-only access to the `lessons`/`course_modules` tables plus read/write access to `lesson_chunks`.

### `copilot/app/tracing.py`
Initialize a module-level `langfuse` client from the `langfuse` SDK using `config.py` settings. Expose a helper `traced_span(name)` used as a context manager/decorator so every retrieval and generation call in `retrieval/search.py` produces a Langfuse trace with: input query, retrieved chunk ids, latency, and (once generation is wired) token usage. It's fine if generation isn't wired yet in this pass — trace the retrieval call itself end to end so the tracing plumbing exists from the first real call, per the plan.

### `copilot/app/ingestion/chunker.py`
Structure-aware markdown chunker:
- Input: raw markdown string (`lessons.content_body`) plus `lesson_title`.
- Split on heading boundaries (`#`, `##`, `###`, ...), tracking a `heading_path` stack (e.g. joining ancestor headings with `" > "`, prefixed by `lesson_title`).
- Within a heading section, if the section's token count (via `tiktoken.encoding_for_model` or `cl100k_base`) exceeds `chunk_token_ceiling`, split further on paragraph boundaries (blank-line-separated blocks), never mid-paragraph, packing greedily up to the ceiling.
- Return a list of `Chunk` dataclasses: `{heading_path: str, chunk_index: int, text: str, token_count: int}`.
- Pure function, unit-testable with no I/O — write it so it can be tested standalone.

### `copilot/app/ingestion/embeddings.py`
Thin wrapper around the OpenAI Python SDK's embeddings endpoint (`client.embeddings.create(model=..., input=[...])`), batching up to 96 chunks per call, returning `list[list[float]]` in input order. No caching yet — that's Week 16.

### `copilot/app/ingestion/ingest_lessons.py`
Standalone script, run via `python -m app.ingestion.ingest_lessons` inside the container:
1. Apply `api/Data/migrations-copilot/001_pgvector_lesson_chunks.sql` if `lesson_chunks` doesn't exist yet (read the file, execute via the asyncpg connection).
2. Query:
   ```sql
   SELECT l.id, l.slug, l.title, l.content_body, m.slug AS module_slug, m.title AS module_title
   FROM lessons l
   JOIN course_modules m ON l.module_id = m.id
   WHERE l.content_status = 'Published'
   ```
   **Assumption to flag back to the user**: there is no explicit "Tier-1" flag on `lessons` in the current schema — this uses `content_status = 'Published'` as the Tier-1 stand-in. If Tier-1 means a specific module subset, the user should narrow this `WHERE` clause before running ingestion.
3. For each lesson: `DELETE FROM lesson_chunks WHERE lesson_id = $1` (idempotent re-run), chunk via `chunker.py`, embed via `embeddings.py`, bulk-insert into `lesson_chunks` with `content_type = 'lesson'`.
4. Log a per-lesson summary (chunk count, total tokens) to stdout.

### `copilot/app/retrieval/search.py`
`async def naive_top_k(query: str, k: int = 5) -> list[RetrievedChunk]`:
1. Embed the query (same model as ingestion).
2. `SELECT ..., embedding <=> $1 AS distance FROM lesson_chunks ORDER BY distance ASC LIMIT $2` (cosine distance via pgvector's `<=>` operator).
3. Wrap the whole function in the `traced_span` from `tracing.py`.
4. Return chunk text + metadata + distance — no answer synthesis yet, that's Week 7.

### `copilot/app/main.py`
FastAPI app with:
- `GET /health` → `{"status": "ok"}`
- `POST /query` → body `{"query": str, "k": int = 5}`, calls `naive_top_k`, returns the ranked chunks (id, heading_path, chunk_text, distance). No auth for now — internal service, not exposed publicly (no port published to the host in compose; only reachable inside `backend-net`).

### `copilot/Dockerfile`
Match the style of `api/Dockerfile`/`app/Dockerfile` (check those for the base-image and layering convention used elsewhere in this repo) — python:3.12-slim base, install `requirements.txt`, copy `app/`, `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]`.

## 4. Wire into Compose

**`docker-compose.yml`** — add a new service, modeled on how `api` connects to `database`:
```yaml
  copilot:
    build:
      context: ./copilot
    container_name: studytracker-copilot
    restart: unless-stopped

    environment:
      POSTGRES_DB: ${POSTGRES_DB:-studytracker}
      POSTGRES_USER: ${POSTGRES_USER:-studyuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?POSTGRES_PASSWORD must be set}
      EMBEDDINGS_API_KEY: ${EMBEDDINGS_API_KEY:?EMBEDDINGS_API_KEY must be set}
      EMBEDDINGS_MODEL: ${EMBEDDINGS_MODEL:-text-embedding-3-small}
      LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY:-}
      LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY:-}
      LANGFUSE_HOST: ${LANGFUSE_HOST:-http://langfuse:3000}

    depends_on:
      database:
        condition: service_healthy

    networks:
      backend-net:
        aliases:
          - copilot

    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8081/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 15s
```
No `ports:` entry — it's internal-only, reached by other services on `backend-net`, not the host. If the user wants to hit it directly while developing, that's what `docker-compose.dev.yml` is for (next).

**`docker-compose.dev.yml`** — add a dev override that builds locally and publishes the port for local testing:
```yaml
  copilot:
    build:
      context: ./copilot
    image: scaler-journey-copilot:dev
    ports:
      - "127.0.0.1:8081:8081"
```

**`.env.example`** — append:
```
EMBEDDINGS_API_KEY=your_openai_api_key_here
EMBEDDINGS_MODEL=text-embedding-3-small
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://langfuse:3000
```

## 5. Langfuse — do not hand-roll the compose spec

Self-hosted Langfuse (v3) needs Postgres + ClickHouse + Redis + S3-compatible storage (MinIO locally) — non-trivial to hand-write correctly from memory. Instead:

1. Fetch the current official self-hosting Docker Compose reference from `https://langfuse.com/self-hosting/docker-compose` (or the `langfuse/langfuse` repo's `docker-compose.yml`).
2. Save it as a **new, separate** file `docker-compose.langfuse.yml` at the repo root, adjusted only to (a) join the existing `backend-net` network instead of creating its own, and (b) rename its Postgres volume so it doesn't collide with `postgres_data` (e.g. `langfuse_postgres_data`).
3. Do not merge Langfuse's services into `docker-compose.yml` directly — keep it as an addable overlay: `docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.langfuse.yml up -d --build`.
4. After it's up, the user creates a project in the Langfuse UI (`http://localhost:3000` by default) and generates the public/secret key pair to put in `.env`.

State clearly in your output which exact Langfuse version/compose content you used, since it's fetched live rather than specified here.

## Output expected

1. Full contents of every new file under `copilot/`.
2. The exact diff (before/after) for `docker-compose.yml`, `docker-compose.dev.yml`, and `.env.example`.
3. The new `api/Data/migrations-copilot/001_pgvector_lesson_chunks.sql` file, full contents.
4. The fetched `docker-compose.langfuse.yml`, full contents, plus a one-line note on where/when it was fetched from.
5. A short "how to run" block: bring the stack up, run the migration, run `python -m app.ingestion.ingest_lessons` inside the `copilot` container, then `curl` the `/query` endpoint with a sample question.

## Code style

Match this repo's existing conventions: snake_case for Python (new to this repo — no existing Python service to match, so use standard PEP 8), double-quoted strings in YAML where the existing compose files use them, 2-space YAML indentation as seen in `docker-compose.yml`, no trailing comments unless clarifying a non-obvious value (the existing files use sparse comments only where needed).
