# C13 — `api-python/`: first signed-in parity run

C12 worked: ruff and mypy clean, 187 tests pass with a database, and the API-key-only comparison is **102 of 102** (after the reviewer gave the three file-driven courses distinct `orderIndex` values in their manifests).

This run is new. The reviewer signed in on both APIs the real way (sign up, approve as admin in each database, log in, enrol TOTP, confirm with a computed code) and then called the routes with the session cookies. 128 steps, compared on status, content type, `Set-Cookie` attributes and JSON body. Times and per-side random ids are masked.

Sign-in, TOTP enrolment, cookies, sessions, `/api/me/*`, admin user actions, chat (mock mode), progress, exercise workspace and draft all match. Five things in the port differ (Tasks 1 to 5).

Two differences are **not** yours:

- `GET /api/admin/usage/by-user` returned 500 from the .NET API (EF Core could not translate the query). The port's answer was right. The reviewer has fixed the C# (`api/Endpoints/AdminEndpoints.cs`, `GetUsageByUserAsync`); do not change the port for it.
- Practice-question option order and new ids are random on each side by design.

Logs in `info/muse-prompts/corrections/round15/`: `auth.log` (every step, with diffs), `raw.jsonl.gz` (raw responses from both sides).

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. The C# in `api/` is the authority; do not edit it.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "C13 — signed-in parity corrections" before starting the next.

## Task 1 — jsonb columns come back re-serialised instead of as PostgreSQL's text (`GET /api/me/activity`)

```
.NET:    "metadataJson": "{\"VisitCount\": 1}"
Python:  "metadataJson": "{\"VisitCount\":1}"

.NET:    "{\"Category\": \"Assignment\", \"LegacyKey\": \"lesson-17-behavioural-mcq-01\", \"isCorrect\": false, ...}"
Python:  "{\"Category\":\"Assignment\",\"LegacyKey\":\"lesson-17-behavioural-mcq-01\",\"isCorrect\":false,...}"
```

In C# the property is a `string` mapped to a `jsonb` column, so Npgsql returns PostgreSQL's own text form of the value (a space after each `:` and `,`, keys in jsonb order). The reviewer probed the port's database session:

```
select metadata from learning_activity          -> dict  {'VisitCount': 1}
select(LearningActivity.metadata_json)          -> str   '{"VisitCount":1}'
select metadata::text from learning_activity    -> str   '{"VisitCount": 1}'
```

So the driver hands SQLAlchemy a decoded `dict`, and `JsonbText.result_processor` in `app/models/types.py` (lines 28-38) re-serialises it with `stjson.dumps`, which is compact. The docstring's claim that the string is received as stored is not what happens.

Change in `JsonbText` only: make the column read as text from the database, so the value is PostgreSQL's rendering. The SQLAlchemy hook for this is `column_expression` on the `TypeDecorator`, returning `cast(col, Text)`. Keep a result processor that passes `None` and `str` through; if a `dict` or `list` still arrives, keep the existing fallback. Writes must keep working: the bind side currently sends the string as is; say in `PROGRESS.md` whether the bind side needs `bind_expression` (a cast to JSONB) once the read side is cast, and why. Fix the docstring.

`JsonbText` is also used in `app/models/mcq_presentation.py`, `migration_reconciliation.py` and `user_exercise_state.py`. For each column, read the matching C# property and confirm it is a `string` on a `jsonb` column (then the same change is right for it) or say which one is not. List the columns and the C# property for each in `PROGRESS.md`. Then check every place in `app/services/` that reads one of these columns and parses it (`json.loads`, `stjson`): parsing must still work on the text form.

Add or update a database test (`PY_SCRATCH_DATABASE_URL`): insert a row with `{"VisitCount":1}` and assert the value read back through the ORM equals what `SELECT metadata::text` returns for the same row.

## Task 2 — a lesson that was never opened: `0001-01-01T00:00:00` against `0001-01-01T00:00:00Z` (`GET /api/me/resume`)

```
.NET:    "lastOpenedAt": "0001-01-01T00:00:00"
Python:  "lastOpenedAt": "0001-01-01T00:00:00Z"
```

C# (`api/Services/LearnerProgressService.cs:521`): `row?.LastOpenedAt ?? DateTime.MinValue`. `DateTime.MinValue` has `Kind = Unspecified`, and System.Text.Json writes an unspecified `DateTime` with no offset suffix. Values read from a `timestamp with time zone` column have `Kind = Utc` and get the `Z`.

Port (`app/services/learner_progress_service.py:656-657`): `datetime(1, 1, 1, tzinfo=UTC)`, and `format_dotnet_datetime` (`app/schemas/base.py:16-29`) always appends `Z`; it also turns a naive value into UTC first (line 18-19).

Change:

- `format_dotnet_datetime`: a naive `datetime` (no `tzinfo`) is the port's equivalent of `Kind = Unspecified`; write it with no `Z`. An aware value is converted to UTC and written with `Z`, as now. Update the docstring.
- `learner_progress_service.py:657`: use a naive `datetime(1, 1, 1)`.

Before changing the formatter, search `app/` for every place a naive `datetime` can reach a `DotNetDateTime` field (for example `datetime.utcnow()`, `datetime(…)` without `tzinfo`, columns declared without timezone). Each of those would lose its `Z` with this change. List them in `PROGRESS.md`; for each, read the C# and say whether the C# value is `Utc` or `Unspecified`, and make the port value aware where the C# is `Utc`. Then search the C# for other uses of `DateTime.MinValue` and `default(DateTime)` that reach a response, and give the port the same naive value there.

Update `tests/test_dotnet_datetime.py`: add the naive case (`datetime(1, 1, 1)` gives `0001-01-01T00:00:00`) and keep the aware cases.

## Task 3 — a failed refresh does not clear the cookies (`POST /api/auth/refresh`)

Observed with a signed-in account whose status was then changed so it is no longer active:

```
.NET:    401 application/problem+json
         Set-Cookie: na_auth     deleted, path=/,         samesite=lax,    httponly
         Set-Cookie: na_refresh  deleted, path=/api/auth, samesite=strict, httponly
Python:  401 application/problem+json        (no Set-Cookie at all)
```

(The reviewer's tool records the cookie name, whether it was deleted, and its attributes, not the raw header. This case is in `round15/auth-inactive.log`, from an earlier pass of the same run.)

The next call then differs too, because the port's client still holds the cookies: .NET answers "No active session. Please sign in." and the port "Your session is no longer valid. Please sign in again."

`SessionService.refresh` does call `self.clear_cookies(request, response)` on every failure path (`app/services/auth/session_service.py:146, 166, 171, 180, 188`), but on the injected `response` object. The endpoint (`app/routers/auth_endpoints.py:445-453`) then returns a **new** response from `endpoint_problem(...)`, and FastAPI sends that one. Headers set on the injected `Response` are only merged into a response that FastAPI builds itself from a returned value; they are dropped when the endpoint returns its own `Response` object.

Change: make the cookie deletions reach the response that is actually sent. In `auth_endpoints.py:refresh`, build the problem response first and pass **that** object to the cookie clearing, or copy the `set-cookie` headers from the injected response onto it; whichever you choose, the result must carry both deletions with the same attributes the C# writes (`SessionService.cs:293-298`: access cookie `Path=/`, `SameSite=Lax`, `HttpOnly`; refresh cookie `Path=/api/auth`, `SameSite=Strict`, `HttpOnly`; `Secure` only on https).

This pattern is not limited to refresh. Search `app/routers/` for every endpoint that receives an injected `Response`, lets a service set or delete cookies on it, and then returns a different `Response` (`endpoint_problem`, `problem_response`, `JSONResponse`, `Response(...)`) or raises `ApiProblem`. List each one in `PROGRESS.md` with the C# behaviour beside it, and fix the ones where the C# sends the cookies. The successful paths (login confirm, verify, refresh, logout, logout-all) matched in the run and must not change.

Add a `TestClient` test without a database if the session lookup can be stubbed, otherwise a database test: a refresh with an unknown refresh token returns 401 and two `Set-Cookie` headers that delete `na_auth` and `na_refresh`.

## Task 4 — the "presentation not found" message is wrapped in extra quotes (`POST /api/v2/practice-questions/{id}/attempts`, `/retry`)

```
.NET:    404 {"error": "Presentation '00000000-0000-0000-0000-000000000000' not found."}
Python:  404 {"error": "\"Presentation '00000000-0000-0000-0000-000000000000' not found.\""}
```

`app/services/mcq_service.py:193` and `:240` raise `KeyError(message)`, and `app/routers/v2_endpoints.py:433-434` and `:451-452` send `str(exc)`. `str()` of a `KeyError` is the `repr` of its argument, so the message gains a pair of quotes. C# throws `KeyNotFoundException` and sends `ex.Message` (`McqService.cs:198, 232`).

Change in the two `except KeyError` handlers: send `exc.args[0]` instead of `str(exc)`. Then search `app/` for any other `str(exc)` or f-string on a caught `KeyError` that reaches a response and fix it the same way; list what you find.

Add a unit test for the handler output if one can be written without a database; otherwise extend the existing MCQ database test with the unknown-presentation case and assert the exact `error` string.

## Task 5 — `GET /` sends JSON; .NET sends plain text

```
.NET:    200 text/plain         StudyTracker API is running. Use /health for service health.
Python:  200 application/json   "StudyTracker API is running. Use /health for service health."
```

`app/main.py:201-203` returns a `str`, which FastAPI serialises as a JSON string, with the quotes. C# (`Program.cs:675`) returns a string from a minimal-API handler, which is written as `text/plain; charset=utf-8`.

Change: return a `PlainTextResponse` (or set `response_class=PlainTextResponse`) so the body has no quotes and the content type is `text/plain; charset=utf-8`.

Then check the other handlers in `app/` that return a bare `str`, and the C# handlers that return a bare string, for the same mismatch. Report what you find.

Add a `TestClient` assertion: `GET /` has content type starting with `text/plain` and a body with no quote characters.

## Finish

End with a short report: each task done or not done, files changed, the lists Tasks 1, 2 and 3 ask for, and anything that could not be done as written. Never say a test or check passes; you have not run it.
