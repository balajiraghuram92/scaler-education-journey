# localization-ai — MT Optimize, QPS, Auto-Routing, eval harness

Python FastAPI service behind the .NET API: the AI layer of the Localization
Lab (design: `info/localization-design/specs/localization-lab-ARCHITECTURE-AND-WORKFLOW.md`,
Parts B.2, E, F). The pipeline is linear on purpose — plain functions, no
LangChain or other orchestration framework.

The design is **eval-harness-first**: the golden set and the metric runner
exist and pass before any translation logic is written. LA2 is that
foundation; the pipeline stages arrive in LA3.

## Layout

- `app/main.py` — FastAPI factory (`uvicorn app.main:create_app --factory`)
- `app/settings.py` — pydantic-settings; every field is an env var (see below)
- `app/db.py` — psycopg pool + read helpers (schema owned by .NET migrations)
- `app/auth.py` — `x-api-key` shared-secret check (same idea as .NET)
- `app/providers/` — `ChatProvider` / `EmbeddingProvider` protocols, an
  OpenAI-compatible HTTP pair (vLLM or any compatible endpoint) and
  deterministic fakes used by every test
- `app/pipeline/` — one module per stage (`cache`, `mt_optimize`, `qps`,
  `auto_route`), cost helpers, structured-output helpers, the config
  registry, and `prompts/` (plain-text templates with versions)
- `app/evals/` — deterministic metrics, optional COMET-Kiwi, golden loader,
  metric runner, comparison report
- `app/routers/` — `GET /health`, `POST /run-eval`, and the four Part F.2
  pipeline endpoints
- `evals/golden/*.jsonl` — the 40-case golden set (see below)
- `tests/` — pytest suite (fakes + throwaway pgvector container for DB tests)

## Golden set — owner must verify by hand

`evals/golden/` holds 40 cases: 8 per locale (de-DE, ja-JP, zh-CN, fr-FR,
es-ES) across the four categories (`short-label`, `warning-message`,
`idiomatic`, `legal-disclaimer`), with 10 placeholder cases (`{count}`,
`{speed}`) and 20 cases using a seeded glossary term.

**Every case is marked `"verified": false`, and that is deliberate: the
gold translations were drafted, not checked. Before trusting any eval
number, read every gold translation by hand, fix what is wrong, and flip
its flag to `true`. A weak gold set produces a meaningless delta.**

Load them into the golden-case table with:

```bash
python -m app.evals.golden_loader --project auroraline-hud-v3
```

The loader upserts (re-running updates changed rows). Note: the flag lives
only in the JSONL — the golden-case table has no `verified` column yet
(LA1 schema gap), so the loader reports verified/unverified counts but
cannot persist the flag.

## COMET-Kiwi (optional)

Reference-free neural MT quality, free per call (local model, no API):

```bash
pip install -r requirements-comet.txt
```

The model download needs a Hugging Face licence acceptance for
`Unbabel/wmt22-cometkiwi-da`: accept it on the model page, `huggingface-cli
login`, then set `COMET_ENABLED=true`. Without the package, the model, or
the flag, the scorer reports "unavailable" and runs record null for the
metric; nothing else fails.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | — | Full conninfo; wins when set |
| `DATABASE_HOST/PORT/NAME/USER/PASSWORD` | localhost/5432/studytracker/studyuser/"" | Parts form |
| `API_SHARED_SECRET` | "" (refuses to start) | `x-api-key`, must match .NET |
| `CHAT_PROVIDER` | `fake` | `fake` or `openai-compat` |
| `CHAT_BASE_URL` | `http://localhost:8001/v1` | vLLM `/v1` root |
| `CHAT_API_KEY` | "" | Bearer token (empty = none) |
| `CHAT_MODEL` | `qwen2.5-7b-instruct` | Chat model name |
| `CHAT_TIMEOUT_SECONDS` | 60 | Per-call timeout |
| `EMBEDDING_PROVIDER` | `fake` | `fake` or `openai-compat` |
| `EMBEDDING_BASE_URL` | `http://localhost:8001/v1` | Embeddings `/v1` root |
| `EMBEDDING_API_KEY` | "" | Bearer token (empty = none) |
| `EMBEDDING_MODEL` | `bge-small-en-v1.5` | Embedding model name |
| `EMBEDDING_DIMENSIONS` | 384 | Must match the `vector(384)` column |
| `COMET_ENABLED` | false | Load COMET-Kiwi at startup |
| `COMET_MODEL` | `Unbabel/wmt22-cometkiwi-da` | Kiwi checkpoint |
| `COMET_GPUS` | 0 | GPUs for COMET inference |
| `CACHE_SIMILARITY_THRESHOLD` | 0.95 | Cache hit at/above this cosine |
| `CHAT_PRICE_PER_1K_INPUT_USD` | 0 | Chat $/1k input tokens |
| `CHAT_PRICE_PER_1K_OUTPUT_USD` | 0 | Chat $/1k output tokens |
| `EMBEDDING_PRICE_PER_1K_USD` | 0 | Embedding $/1k tokens |
| `LEGACY_MT_PRICE_PER_CHAR_USD` | 0 | Legacy MT $/character |
| `ENABLE_DOCS` | false | Expose `/docs` |

Set real (or amortized-GPU) prices or every cost stays zero and the ledger
story is meaningless. The compose override leaves the new LA3 variables at
their defaults; export them there when wiring a real deployment.

## Endpoints

- `GET /health` — liveness, no auth. `GET /health/ready` — DB + pgvector.
- `POST /run-eval` — `{projectSlug, pipelineConfig}` → the Part F.2
  aggregates plus `tokensUsed`, `fallbackCount`, `promptVersion`. Configs:
  `legacy-only`, `legacy+optimize`, `legacy+optimize+glossary`,
  `legacy+optimize+glossary+cache`. Every produced translation is judged,
  so `avgQpsScore` is populated for all configs.
- `POST /translate-and-optimize` — `{rawMtText, sourceText, targetLocale,
  projectSlug, glossaryTerms}` → `{optimizedTranslation, cacheHit, checks,
  ...tokens/latency/cost/fallback}`. Checks the semantic cache first (E.5
  stages 2–3).
- `POST /qps-score` — `{sourceText, targetText, targetLocale}` → `{score
  (0–100, null on fallback), flaggedIssues, ...}`.
- `POST /comet-score` — `{sourceText, targetText, targetLocale}` → `{score
  (0–1, null when unavailable), available, ...}`. No LLM call.
- `POST /auto-route` — `{qpsScore, projectThreshold, checks?}` →
  `{needsReview, reasons, ...}`. Pure function.

All except `/health*` require the `x-api-key` header.

Eval-harness limitation, stated plainly: golden cases carry no raw MT and
this service has no MT provider, so `legacy*` eval configs feed the source
text to MT Optimize in place of raw MT. Numbers from the fake providers
mean nothing about quality — point the service at a real model first.

## Comparison report

```bash
python -m app.evals.report --project auroraline-hud-v3
```

One row per pipeline config (latest run wins), one column per metric: the
baseline-to-delta table. Prompt versions are returned by `/run-eval` but
not yet persisted per run (no `EvalRun` column — LA1 schema gap), so the
report cannot show them.

## Real-model checks (skipped by default)

- QPS calibration bands: `LOCAI_REAL_CHAT=1 LOCAI_REAL_CHAT_BASE_URL=...
  LOCAI_REAL_CHAT_MODEL=... pytest tests/test_qps_calibration.py`
- Cache separation report: `LOCAI_REAL_EMBEDDINGS=1
  LOCAI_REAL_EMBEDDING_MODEL=... pytest tests/test_cache.py -k separation`
  (prints per-pair cosines and the suggested threshold midpoint)

## Checks

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format --check .
mypy app
pytest
```

DB-backed tests spin up a throwaway `pgvector/pgvector:pg16` container and
skip cleanly when Docker is unavailable.

## Schema notes

- Table/column names follow the LA1 entities (`localization_*`,
  snake_case). The `source_embedding` column is SQL-only (`vector(384)` +
  HNSW index in the migration); this service is its only reader/writer.
- The `EvalRun` table has no prompt-version column yet: the prompt version
  is returned by `/run-eval` but cannot be persisted until the column exists.
- The golden-case table has no `verified` column yet: the flag lives only
  in the JSONL files.
