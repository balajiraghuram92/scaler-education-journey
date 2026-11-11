-- Minimal test schema mirroring the LA1 table/column names. The real schema is
-- owned by the .NET EF Core migrations; these tables exist only so the eval
-- harness tests run against real SQL without the .NET stack.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE localization_projects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(150) NOT NULL UNIQUE,
    name VARCHAR(250) NOT NULL,
    source_locale VARCHAR(20) NOT NULL DEFAULT 'en-US',
    qps_threshold INTEGER NOT NULL DEFAULT 70,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE localization_glossary_terms (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES localization_projects (id) ON DELETE CASCADE,
    locale_code VARCHAR(20) NOT NULL,
    source_term VARCHAR(200) NOT NULL,
    target_term VARCHAR(200) NOT NULL,
    notes VARCHAR(500) NULL
);

CREATE TABLE localization_eval_golden_cases (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES localization_projects (id) ON DELETE CASCADE,
    locale_code VARCHAR(20) NOT NULL,
    source_text TEXT NOT NULL,
    gold_translation TEXT NOT NULL,
    category VARCHAR(30) NOT NULL,
    notes VARCHAR(500) NULL
);

CREATE TABLE localization_eval_runs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES localization_projects (id) ON DELETE CASCADE,
    pipeline_config VARCHAR(50) NOT NULL,
    run_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    avg_comet_kiwi NUMERIC(5, 4) NULL,
    avg_qps_score NUMERIC(5, 2) NULL,
    glossary_adherence_rate NUMERIC(5, 4) NULL,
    placeholder_preservation_rate NUMERIC(5, 4) NULL,
    cache_hit_rate NUMERIC(5, 4) NULL,
    avg_latency_ms INTEGER NULL,
    total_cost_usd NUMERIC(12, 6) NULL
);

CREATE TABLE localization_eval_case_results (
    id SERIAL PRIMARY KEY,
    eval_run_id INTEGER NOT NULL REFERENCES localization_eval_runs (id) ON DELETE CASCADE,
    eval_golden_case_id INTEGER NOT NULL REFERENCES localization_eval_golden_cases (id) ON DELETE CASCADE,
    produced_translation TEXT NOT NULL,
    comet_kiwi_score NUMERIC(5, 4) NULL,
    qps_score INTEGER NULL,
    glossary_adherence_ok BOOLEAN NULL,
    placeholder_preserved_ok BOOLEAN NULL,
    latency_ms INTEGER NULL,
    cache_hit BOOLEAN NULL,
    cost_usd NUMERIC(12, 6) NULL
);

CREATE TABLE localization_translation_cache_entries (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES localization_projects (id) ON DELETE CASCADE,
    locale_code VARCHAR(20) NOT NULL,
    source_text TEXT NOT NULL,
    source_embedding vector(384) NULL,
    cached_translation TEXT NOT NULL,
    hit_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_hit_at TIMESTAMPTZ NULL
);
