# C8 — `issue-intel/`: first run of the database-backed tests

The reviewer ran the suite against a real PostgreSQL (pgvector, database created and migrated by `tests/db_helper.py`).

Result: **66 passed, 4 failed**. Log: `info/muse-prompts/corrections/round7/issue-intel-db.log`.

The four failures have two causes (Tasks 1 and 3). Looking into the first one turned up a third problem that no test catches yet and that matters more than either: **row-level security is not enforced at all with the project's own database setup** (Task 2).

Paste everything below this line into Muse Code at the repository root.

---

Work only in `issue-intel/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. Read `info/muse-prompts/issue-intel/BUILD-SPEC.md` first.

Do the tasks in order. After each task, append what you did to `issue-intel/PROGRESS.md` under "C8 — database test corrections" before starting the next.

## Task 1 — `SET ... = :v` cannot take a bind parameter (3 failures)

```
tests/test_rls.py::test_unentitled_user_sees_zero_rows
tests/test_tokens.py::test_token_lifecycle
tests/test_tokens.py::test_token_rejections

E  ProgrammingError: syntax error at or near "$1"
E  [SQL: SET LOCAL app.modules = $1]        (rls_session, and tests/test_rls.py:23)
E  [SQL: SET app.modules = $1]              (service_session, app/governance/rls.py:43)
```

PostgreSQL's `SET` is a utility statement and does not accept parameters. Every use of `rls_session` and `service_session` fails on its first statement, so nothing that touches the database through them has ever worked.

The parameterised equivalent is the function `set_config(name, value, is_local)`.

Change in `app/governance/rls.py`:

- `rls_session` (lines 20-29): replace each `text("SET LOCAL app.X = :v")` with `text("SELECT set_config('app.X', :v, true)")`. Same parameters. `true` means "for this transaction only", which is what `SET LOCAL` did.
- `service_session` (lines 43-51): replace each `text("SET app.X = :v")` with `text("SELECT set_config('app.X', :v, false)")`. `false` means "for the session". The three `RESET` statements stay as they are; `RESET` takes no parameter.
- Update the module docstring's first line so it no longer says `SET LOCAL`.

Do not build the SQL by string formatting. The values come from entitlements and must stay bound parameters.

`tests/test_rls.py:23-25` has the same three statements; Task 2 replaces them.

## Task 2 — the database user is a superuser, so row-level security filters nothing

`docker-compose.yml` creates the database with `POSTGRES_USER: issueintel`. In the PostgreSQL Docker image that user is a **superuser**. PostgreSQL superusers bypass row-level security always; `FORCE ROW LEVEL SECURITY` (migration `0002_g1_knowledge.py:165-166`) applies to the table owner but not to a superuser. The comment at `0002_g1_knowledge.py:19-20` assumes otherwise.

The reviewer confirmed this in a throwaway pgvector:pg16 container, logged in as a `POSTGRES_USER` login, table with RLS enabled and forced and a policy on `current_setting('app.m', true)`:

```
superuser, no context set                      -> 2 of 2 rows visible   (no filtering)
after SET LOCAL ROLE to a NOSUPERUSER role:
  no context set                               -> 0 rows
  set_config('app.m','a',true)                 -> 1 row
  INSERT of a row the policy does not allow    -> ERROR: new row violates row-level security policy
```

So once Task 1 is fixed, `test_unentitled_user_sees_zero_rows` will still fail (the unentitled user sees every row), and the running app would show every viewer everything.

Fix: run all data access as a non-superuser role. Do **not** change `docker-compose.yml` or the connection string. The login user stays as it is; the two session helpers switch role.

### 2a — new migration `alembic/versions/0006_app_role.py`

`down_revision` is the 0005 revision id. `upgrade()` executes this SQL, each statement through `op.execute`:

```sql
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'issueintel_app') THEN
    CREATE ROLE issueintel_app NOLOGIN NOSUPERUSER NOBYPASSRLS;
  END IF;
END
$$;
GRANT issueintel_app TO CURRENT_USER;
GRANT USAGE ON SCHEMA public TO issueintel_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO issueintel_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO issueintel_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO issueintel_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO issueintel_app;
```

The `IF NOT EXISTS` matters: roles belong to the whole server, and the test database and the main database share one server.

`downgrade()`: revoke the same privileges and default privileges in this database. Do not drop the role (another database on the server may use it).

Also correct the comment at `0002_g1_knowledge.py:19-20` to say that `FORCE` covers the table owner, that a superuser still bypasses it, and that the app therefore switches to `issueintel_app` (migration 0006). Change only the comment in that file.

### 2b — `app/governance/rls.py`

Add a module constant `APP_ROLE = "issueintel_app"`.

- `rls_session`: the first statement inside `session.begin()`, before the three `set_config` calls, is `SET LOCAL ROLE issueintel_app`. The role name is a fixed identifier from the constant, not user input, so it may be formatted into the statement text.
- `service_session`: the first statement is `SET ROLE issueintel_app`; in the `finally` block add `RESET ROLE` after the three existing `RESET` statements.

`service_session` keeps full entitlements through the three settings, as now. It no longer depends on being a superuser.

### 2c — sessions that do not go through the helpers

These open a session with `create_session_factory()` directly and so still run as the superuser:

```
app/db.py:31
app/ingest/run.py:60
evals/run_g1.py:143, 174
evals/run_g4.py:193
app/governance/rls.py:66-68   (rls_session_dep, resolving entitlements)
```

Read each one and write a line per call site in `PROGRESS.md`: which tables it reads or writes. The five RLS tables are `cases`, `threads`, `messages`, `changes`, `chunks`.

- A call site that reads or writes any of those five tables moves to `service_session()` (ingest and the eval runners are service work), unless it is specifically a per-viewer query, in which case it uses `rls_session(ent)`.
- A call site that touches only other tables (users, entitlements, routing, budgets, model calls) stays as it is.
- If moving one is not straightforward (for example it relies on its own transaction handling that `service_session` would break), leave it, and say exactly why in `PROGRESS.md` and in the final report. Do not guess.

### 2d — `tests/test_rls.py`

- `_seed` (lines 19-39): seed inside `async with service_session() as session:` instead of a raw factory session with three `SET LOCAL` statements, and commit at the end. The current seed sets a narrow context (`UiState` / `SE`) and then inserts a `VersionControl` row; under real row-level security that insert is refused, which is correct behaviour. Seeding is service work and needs full entitlements. `service_session()` uses the default settings, and the test already sets `ISSUEINTEL_DATABASE_URL` with `monkeypatch` before calling `_seed`; check that `_seed` no longer needs the `url` argument for anything else, and keep the signature if other callers pass it.
- `_cleanup` (lines 42-51): same change, so the delete runs as the app role with full entitlements.
- Add one assertion to `test_unentitled_user_sees_zero_rows` after the existing ones: inside an `rls_session(open_ent)`, `SELECT current_user` returns `issueintel_app`.
- Add a second test, `test_insert_outside_entitlement_is_refused`: inside `rls_session(Entitlements({"UiState"}, {"Support"}, 0))`, adding a `Case` whose ACL is the `VersionControl` / `SE` / `SE` one raises a database error (`sqlalchemy.exc.DBAPIError` or a subclass). Create the ACL row beforehand through `service_session()`. Skip the test the same way the first one does when no database is reachable.

## Task 3 — `tests/test_routing.py::test_switch_and_rollback` (1 failure)

```
app/gateway/routing.py:87   in switch_version   (await session.commit())
E  IntegrityError: duplicate key value violates unique constraint "uq_routing_one_active"
E  [SQL: UPDATE routing_versions SET active=$1::BOOLEAN, activated_at=..., activated_note=... WHERE routing_versions.id = $4::INTEGER]
```

`switch_version` (lines 69-88) sets `active = False` on the current row and `active = True` on the target, then commits once. SQLAlchemy sends the two `UPDATE`s in primary-key order, not in the order the attributes were assigned. Switching forward (old row has the lower id) happens to deactivate first and works. Rolling back (target has the lower id) activates the target first, while the other row is still active, and the partial unique index `uq_routing_one_active` rejects it. The index is doing its job.

Change in `switch_version` only: after the loop that sets `row.active = False`, add `await session.flush()` before `target.active = True`. Both statements stay in the same transaction, so the "one audited operation" property is unchanged. Nothing else in the function changes. Do not touch the index or the migration.

## Finish

End with a short report: each task done or not done, files changed, the Task 2c table of call sites, and anything that could not be done as written. Never say a test or check passes; you have not run it.
