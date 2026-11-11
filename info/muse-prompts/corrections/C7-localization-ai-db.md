# C7 — `localization-ai/`: first run of the database-backed tests

The reviewer ran the test suite with Docker available, so the tests that start a throwaway pgvector container ran for the first time.

Result: the run **hangs** on the third test. With the hanging tests left out: **68 passed, 3 failed, 7 skipped** (the 7 need a real model).

Logs in `info/muse-prompts/corrections/round7/`:

- `localization-ai-db.log` — the hang, with a stack dump after 45 seconds
- `localization-ai-db-rest.log` — the rest of the suite with `tests/test_api_pipeline.py` and the three `db_client` tests left out

All four problems are in the tests, not in `app/`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `localization-ai/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. Do not change any file under `localization-ai/app/`.

Do the tasks in order. After each task, append what you did to `localization-ai/PROGRESS.md` under "C7 — database test corrections" before starting the next.

## Task 1 — the connection pool is opened in a throwaway event loop (hang)

Stack dump from the log:

```
File ".../asyncio/runners.py", line 206 in _cancel_all_tasks
File ".../asyncio/runners.py", line 194 in run
File "/w/tests/conftest.py", line 188 in db_client
```

`tests/conftest.py:187-189`:

```python
pool = db_module.create_pool(conninfo)
asyncio.run(pool.open())
asyncio.run(pool.wait())
```

`asyncio.run` creates an event loop, runs one coroutine and then closes the loop, cancelling every task still on it. `AsyncConnectionPool.open()` starts the pool's background worker tasks on that loop. When `asyncio.run` tries to shut the loop down it waits for those workers and never returns. Even if it did return, the pool would belong to a dead loop; `TestClient` runs the app on a different one.

A psycopg async pool has to be opened by the same loop that uses it. The app already does that: `lifespan` in `app/main.py` calls `await app.state.pool.open(wait=False)` and closes the pool on shutdown. `TestClient` runs `lifespan` only when it is used as a context manager.

Change, in both places that have this pattern:

1. `tests/conftest.py`, fixture `db_client`:
   - Create the pool with `db_module.create_pool(conninfo)` and pass it to `build_app(...)` **unopened**. Remove the two `asyncio.run(pool.open())` / `asyncio.run(pool.wait())` lines and the `asyncio.run(pool.close())` after the `yield`.
   - Replace `client = TestClient(application)` / `yield client` with `with TestClient(application) as client:` / `yield client` inside the block. Entering the block runs `lifespan` (opens the pool on the client's loop); leaving it closes the pool.
   - Remove the `import asyncio` inside the fixture if nothing else there uses it.

2. `tests/test_api_pipeline.py`, helper `_client_for` (lines 14-24) and every test that calls it:
   - `_client_for` stops opening the pool. Turn it into a context manager (`@contextlib.contextmanager`) that builds the app with an unopened pool and does `with TestClient(application) as client: yield client`.
   - Every caller changes from `client, pool = _client_for(...)` + `try: ... finally: asyncio.run(pool.close())` to `with _client_for(...) as client:` with the same body. There are `asyncio.run(pool.close())` lines near 56, 79 and 99; find all callers, do not rely on those three numbers.
   - Remove `import asyncio` from the file if it becomes unused.

Check before finishing: `lifespan` also calls `close()` on the chat and embedding providers. Confirm that `FakeChatProvider.close` and `FakeEmbeddingProvider.close` exist (`app/providers/fake.py`) and that any test-local provider class passed to `build_app` in these files has an async `close` too. If one lacks it, add the method to the test class, not to `app/`.

Do not change the plain `client` fixture at `conftest.py:59-61`; unit tests deliberately do not start `lifespan`.

## Task 2 — `tests/test_cache.py::test_cache_is_scoped_to_project_and_locale`

```
tests/test_cache.py:164: other_id = _conn_id(fresh_db)
tests/test_cache.py:77:  INSERT INTO localization_projects (slug, name) VALUES ('c', 'C') RETURNING id
E   psycopg.errors.UniqueViolation: duplicate key value violates unique constraint "localization_projects_slug_key"
```

`_conn_id` always inserts slug `'c'`, and this test calls it twice on the same database. Give `_conn_id` a `slug: str = "c"` parameter, pass it as a bound parameter in the INSERT (`VALUES (%s, 'C')`), and have this test's second call use `slug="d"`. No other test changes.

## Task 3 — two latency assertions in `tests/test_runner_configs.py`

```
test_legacy_optimize_run:                          assert summary.avg_latency_ms == 1   -> got 0
test_legacy_optimize_glossary_cache_miss_then_hit: assert first.avg_latency_ms == 2     -> got 1
```

The tests assume the optimize step reports the fake provider's `latency_ms=1`. It does not: `app/pipeline/mt_optimize.py:105-147` measures wall-clock time with `time.perf_counter()`, which is the right thing in production (it includes a retry) and is 0 ms with a fake. Only the embedding step passes the provider's number through (`app/pipeline/cache.py:131`). The code is right; the literals are wrong, and any exact literal would be timing-dependent.

Change only these two assertions:

- line 58: `assert summary.avg_latency_ms is not None and summary.avg_latency_ms >= 0`
- line 88: `assert first.avg_latency_ms is not None and first.avg_latency_ms >= 1`, with the comment changed to say the 1 is the fake embedding call and the optimize step is measured wall-clock time.

Then search the rest of `tests/` for other exact `latency` equality assertions that depend on wall-clock time (`latencyMs ==`, `latency_ms ==`). Loosen any that go through `mt_optimize` or `qps` in the same way; leave ones that read a provider's own field. List what you found in `PROGRESS.md`.

## Finish

End with a short report: each task done or not done, files changed, and anything that could not be done as written. Never say a test or check passes; you have not run it.
