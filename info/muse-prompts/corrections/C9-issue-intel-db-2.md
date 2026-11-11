# C9 — `issue-intel/`: second database run

C8 worked. Reviewer's run against a real PostgreSQL: **68 passed, 3 failed** (was 66 / 4). ruff clean. mypy: the same three notes in `app/mcp_server/server.py` as before, not part of this prompt.

Row-level security is now enforced: the unentitled viewer sees 0 rows in all five tables, the routing rollback passes, and the new `test_insert_outside_entitlement_is_refused` passes.

The three remaining failures are in tests that could never get this far before, plus one weakness in `service_session` that hides the real error.

Log: `info/muse-prompts/corrections/round8/issue-intel-db.log`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches.

Do the tasks in order. After each task, append what you did to `issue-intel/PROGRESS.md` under "C9 — database test corrections, second run" before starting the next.

## Task 1 — `service_session` hides the original error (`app/governance/rls.py`)

```
app/governance/tokens.py:33  in mint_token
app/governance/rls.py:64     in service_session       (await session.execute(text("RESET app.modules")))
E  PendingRollbackError: This Session's transaction has been rolled back due to a previous exception during flush.
   Original exception was: ForeignKeyViolationError ... "approval_tokens" violates foreign key constraint
```

When the body of `async with service_session()` raises during a flush or commit, the `finally` block runs the `RESET` statements on a session whose transaction has failed. That raises `PendingRollbackError`, which replaces the real error, and the role and the three settings are never reset on that connection before it goes back to the pool.

Change in `service_session` only: make `await session.rollback()` the first statement of the `finally` block, before the three `RESET app.*` statements and `RESET ROLE`. After a successful commit there is nothing to roll back and the call is harmless. Nothing else in the function changes.

`rls_session` needs no change: it runs inside `session.begin()`, which rolls back on error, and everything it sets is transaction-local.

## Task 2 — token tests mint tokens for runs that do not exist (`tests/test_tokens.py`, 2 failures)

```
tests/test_tokens.py::test_token_lifecycle
tests/test_tokens.py::test_token_rejections
E  ForeignKeyViolationError: insert or update on table "approval_tokens" violates foreign key constraint (run_id -> runs.id)
```

`approval_tokens.run_id` is a foreign key to `runs.id` (`alembic/versions/0004_g3_fix.py:81`). The tests call `mint_token("run1", ...)`, `"run2"`, `"run3"` and no such runs exist. The schema is right; the tests must create the runs first. Do not change `app/governance/tokens.py` or the foreign key.

Change in `tests/test_tokens.py`:

- Add a helper that inserts `Run` rows (`app/models/g2.py:14`) through `service_session()` and commits. Fill every non-nullable column without a default: `id`, `ticket_source`, `ticket_key`, `trigger`, `pipeline_version`, `content_hash`. Read the model for the exact list; do not guess.
- Use run ids that are unique per test run, for example `f"tok-{uuid.uuid4().hex[:12]}"`, so the tests can be run repeatedly against a database that is kept. Replace the literals `"run1"`, `"run2"`, `"run3"` with those ids everywhere in the two tests, including the arguments to `validate_token`. The literal `"other"` at the wrong-run check and `"r"` in the forged-token check stay as they are: they are meant not to match.
- Add a clean-up in a `try` / `finally` in each test that deletes the tokens and then the runs it created (tokens first, because of the foreign key), through `service_session()`.
- Do not change any assertion.

## Task 3 — `tests/test_rls.py::test_unentitled_user_sees_zero_rows` counts rows from other tests (1 failure)

```
tests/test_rls.py:71
E  assert 191 == 1
```

The unentitled check passes (`(0, 0, 0, 0, 0)`). The next check expects the `UiState` / `Support` / restriction 0 viewer to see exactly one case, but `tests/test_ingest_idempotent.py` has already ingested a corpus into the same test database, and 190 of its cases are legitimately visible to that viewer. The policy is right; the test is counting rows it did not create.

Change in `_query` inside this test:

- `n_orm`: add `.where(Case.source == "TEST")` to the `select(Case)`.
- `n_raw`: change the SQL to `SELECT id FROM cases WHERE source = 'TEST'`.
- Leave the thread, change and chunk counts as they are. They are only asserted for the unentitled viewer, where they must be 0 across the whole table.

Then add one assertion after `assert n_orm == n_raw == 1`: with full entitlements (`Entitlements.service()`), the same `_query` returns `n_orm == n_raw == 2`. That proves both seeded rows exist and that it is the policy, not the seed, that hides the second one.

Change nothing else in the file.

## Finish

End with a short report: each task done or not done, files changed, and anything that could not be done as written. Never say a test or check passes; you have not run it.
