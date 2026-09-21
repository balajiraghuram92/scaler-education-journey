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

CREATE INDEX content_chunks_embedding_idx
    ON content_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX content_chunks_search_idx
    ON content_chunks USING GIN (search_vector);