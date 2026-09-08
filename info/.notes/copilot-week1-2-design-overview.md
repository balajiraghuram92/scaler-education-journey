# Week 1–2 Design Overview — Naive RAG Baseline (hand-coded by user)

**Status:** Design reference only. No implementation code here — the user writes every file themselves. This scopes down the full HLD at [neuralascent-chatbot-hld-python-LangChain.md](Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-python-LangChain.md) to exactly what Weeks 1–2 of the AI-transition plan need: ingestion + naive top-k retrieval, nothing else. No auth, no routing, no guardrails, no chat UI, no reranking. This is deliberately the dumbest version that works — it's the control group the Week 3–8 eval work measures every later improvement against.

## What's different from the full HLD

The full HLD assumes a generic `vertical → course → chapter → lesson → exercise` hierarchy with its own `app_user`/`chat_conversation` tables. This repo's actual schema is simpler: `course_modules → lessons` (see `api/Models/CourseModule.cs`, `api/Models/Lesson.cs`), no separate vertical/chapter layer. Don't copy the HLD's §12 SQL verbatim — adapt column names to what actually exists (`lessons.content_body`, `lessons.content_status`, `course_modules.slug`/`title`).

## Component overview

```mermaid
flowchart LR
    subgraph Ingestion [Ingestion — run manually/on demand, not a live service]
        A[Postgres: lessons + course_modules] --> B[LessonChunker]
        B --> C[EmbeddingClient]
        C --> D[ChunkRepository]
        D --> E[(Postgres: lesson_chunks + pgvector)]
    end

    subgraph Query [Query — FastAPI, live]
        F[POST /query] --> G[RetrievalService]
        G --> C
        G --> E
        G --> H[Langfuse trace]
    end
```

Two independent flows sharing one table. Nothing else exists yet — no orchestrator, no LLM answer generation, no session/conversation state. `/query` returns ranked raw chunks; a human (you) reads the JSON to judge quality. Answer synthesis is Week 7.

## Class diagram

```mermaid
classDiagram
    class LessonChunker {
      +chunk(content_markdown: str, lesson_title: str, token_ceiling: int) list~Chunk~
    }
    class Chunk {
      +heading_path: str
      +chunk_index: int
      +text: str
      +token_count: int
    }
    class EmbeddingClient {
      +embed(texts: list~str~) list~list~float~~
    }
    class ChunkRepository {
      +delete_for_lesson(lesson_id: int)
      +bulk_insert(lesson_id: int, chunks: list~Chunk~, embeddings: list~list~float~~) 
    }
    class ContentIngestionRunner {
      +run() 
    }
    class RetrievalService {
      +naive_top_k(query: str, k: int) list~RetrievedChunk~
    }
    class RetrievedChunk {
      +chunk_id: int
      +heading_path: str
      +text: str
      +distance: float
    }
    class LangfuseTracer {
      +span(name: str)
    }

    ContentIngestionRunner --> LessonChunker
    ContentIngestionRunner --> EmbeddingClient
    ContentIngestionRunner --> ChunkRepository
    LessonChunker --> Chunk
    RetrievalService --> EmbeddingClient
    RetrievalService --> RetrievedChunk
    RetrievalService --> LangfuseTracer
```

Five classes, one script, one endpoint. That's the whole Week 1–2 build. Resist the urge to add `RoutePolicyEngine`, `ContextResolver`, or `ResponseGuardrail` from the full HLD now — those are Weeks 9–13 material once there's an eval harness to prove they're needed.

## Sequence — ingestion (run by hand, e.g. `python -m ingestion.run`)

```mermaid
sequenceDiagram
    participant Runner as ContentIngestionRunner
    participant DB as Postgres (lessons)
    participant Chunker as LessonChunker
    participant Embed as EmbeddingClient
    participant Repo as ChunkRepository
    participant Vec as Postgres (lesson_chunks)

    Runner->>DB: SELECT lessons JOIN course_modules WHERE content_status='Published'
    DB-->>Runner: rows
    loop each lesson
        Runner->>Repo: delete_for_lesson(lesson_id)
        Runner->>Chunker: chunk(content_body, title, ceiling)
        Chunker-->>Runner: list[Chunk]
        Runner->>Embed: embed([chunk.text for chunk in chunks])
        Embed-->>Runner: list[vector]
        Runner->>Repo: bulk_insert(lesson_id, chunks, vectors)
        Repo->>Vec: INSERT ... 
    end
```

## Sequence — query

```mermaid
sequenceDiagram
    actor You as You (curl/Postman)
    participant API as FastAPI /query
    participant RS as RetrievalService
    participant Embed as EmbeddingClient
    participant Vec as Postgres (lesson_chunks)
    participant LF as Langfuse

    You->>API: POST {query, k}
    API->>RS: naive_top_k(query, k)
    RS->>LF: start span
    RS->>Embed: embed([query])
    Embed-->>RS: vector
    RS->>Vec: SELECT ... ORDER BY embedding <=> $1 LIMIT k
    Vec-->>RS: rows
    RS->>LF: end span (latency, k, query)
    RS-->>API: list[RetrievedChunk]
    API-->>You: JSON
```

## Build order (what to write first, in order)

1. **Migration**: `lesson_chunks` table + `vector` extension. Point of friction to know now: `postgres:16-alpine` (current `database` image in `docker-compose.yml`) does not ship pgvector — you'll need to switch to `pgvector/pgvector:pg16` before this table can exist. Small, mechanical compose change; still yours to make since it's part of standing the feature up.
2. **`LessonChunker`** — pure function, no I/O. Write it test-first: paste in a real `content_body` from one lesson, assert the heading paths and chunk boundaries look right before wiring anything else.
3. **`EmbeddingClient`** — thin wrapper, one method, easy to fake in tests.
4. **`ChunkRepository` + `ContentIngestionRunner`** — wire the above three into one script, run it against real lesson data, eyeball what landed in `lesson_chunks`.
5. **`RetrievalService` + `/query` endpoint** — cosine search via pgvector's `<=>` operator (see the full HLD §12.1 for the operator in context, adapt the query to the simpler schema here).
6. **Langfuse tracing** — wrap step 5's call. Self-hosting Langfuse itself is infra setup, not "the job" — fine to follow Langfuse's own self-host docs directly rather than treating it as a design problem.

Nothing here produces an answer to a learner's question yet — that's deliberate. The measuring instrument (Week 3's golden eval set) comes before you're allowed to make this fancier.
