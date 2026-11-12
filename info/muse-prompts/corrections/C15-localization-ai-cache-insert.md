# C15 — `localization-ai/`: first run beside the real .NET API and database

The pytest suite is green (81 passed, 7 skipped). This is the first run of the service next to the real stack: PostgreSQL migrated and seeded by the .NET API, the .NET API pointed at the service (`LocalizationAi__BaseUrl`), fake chat and embedding providers, and the React app's Workflow page driving it.

Clicking through the workflow actions on project `auroraline-hud-v3`:

```
Auto-Translate via Google MT   136 strings translated via Google MT
Run MT Optimize                0 strings optimized, 136 failed        <- Task 1
Score QPS                      0 strings scored, 136 failed           (fake judge returns no score; see "Not in this prompt")
Auto-Route                     0 strings processed, 0 flagged         (needs QPS scores)
```

The reviewer applied the Task 1 change to a throwaway container and ran again: `Run MT Optimize` gave `136 strings optimized`, 136 cache rows, and one AI ledger entry with 75,102 tokens.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `localization-ai/`. One agent. Do not run commands. Do not commit. Do not create or switch branches. Append what you did to `localization-ai/PROGRESS.md` under "C15".

## Task 1 — the cache insert relies on column defaults the real table does not have

```
POST /translate-and-optimize  ->  500 Internal Server Error
app/routers/pipeline.py:90   translate_and_optimize
app/pipeline/cache.py:119    translate_with_cache
psycopg.errors.NotNullViolation: null value in column "hit_count" of relation "localization_translation_cache_entries" violates not-null constraint
```

The real table, created by the .NET migrations (EF Core sets these values in C#, so the database has no defaults):

```
hit_count   integer                   not null   (no default)
created_at  timestamp with time zone  not null   (no default)
```

`tests/schema.sql:69-70` declares both with defaults (`DEFAULT 0`, `DEFAULT now()`), so the insert at `app/pipeline/cache.py:119-124`, which lists neither column, passes in the tests and fails on the real database.

Change:

1. `app/pipeline/cache.py`, the `INSERT INTO localization_translation_cache_entries` statement: add `hit_count` and `created_at` to the column list with the values `0` and `now()`. Nothing else in the function changes.
2. `tests/schema.sql`: remove the two defaults from that table so the test schema matches the real one and this class of error fails in the tests.
3. Then compare every table in `tests/schema.sql` with the real schema for the same mismatch. The authority is the EF model snapshot, `api/Migrations/StudyTrackerContextModelSnapshot.cs` (read only; do not edit anything in `api/`): a column has a database default only where the snapshot shows `HasDefaultValue` or `HasDefaultValueSql`. For every `DEFAULT` in `tests/schema.sql` that the snapshot does not have, remove it from `schema.sql`, and make sure every `INSERT` in `app/` supplies that column. List each one in `PROGRESS.md`.

   The reviewer checked the required columns of the four tables the service writes against the live database: `localization_eval_golden_cases`, `localization_eval_runs` and `localization_eval_case_results` inserts already supply every required column; only the cache insert does not. Your comparison should confirm that from the snapshot.
4. Tests that insert into these tables with raw SQL (for example in `tests/test_cache.py`) must now supply the columns too.

## Task 2 — a failure inside `translate_with_cache` reaches the client as a bare 500

The .NET client only sees `500 Internal Server Error` with no body it can log. Read how the other pipeline endpoints in `app/routers/pipeline.py` report a database error, and say in `PROGRESS.md` whether a database error anywhere in the pipeline is turned into a JSON error body or left to the default handler. Do not change behaviour in this task; report only.

## Not in this prompt

With `CHAT_PROVIDER=fake`, the judge's default reply is `{}`, so `/qps-score` answers `"score": null, "fallback": true`, the .NET API counts every string as failed, and Auto-Route has nothing to route. That is the fake provider working as written. Whether the fake stack should produce demo scores is a decision for the repository owner; do not change it.

## Finish

Report: each task done or not done, files changed, the list Task 1 step 3 asks for, the Task 2 finding. Never say a test passes; you have not run it.
