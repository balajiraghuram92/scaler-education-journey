# C11 — `api-python/`: first live parity run against the .NET API

The reviewer started both APIs on identical data and ran `tools/parity.py` with `tools/parity_routes.txt`.

Set-up: one PostgreSQL, schema and reference data created by the .NET API (`--migrate`, `--seed-reference-data`), then the database copied so each API has its own identical copy. Same API key and JWT signing key on both.

Results:

- **Route tables:** the .NET Swagger document and the FastAPI OpenAPI document list the same **102** method + path pairs. Nothing missing, nothing extra.
- **Responses:** **85 of 102** match. The 17 that differ have five causes; four are in the port (Tasks 1 to 4), one is in the data and is not yours to fix (see "Not in this prompt").

Logs in `info/muse-prompts/corrections/round11/`: `parity.log.gz` (full tool output, gzipped, 1.8 MB unpacked), `parity-summary.txt` (the reviewer's line-level differences per route), `net-openapi.json`, `py-openapi.json`.

Limit of this run: `parity.py` sends only the API key, so every route that needs a signed-in user was compared as 401 against 401. Their response bodies are still unverified.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. The C# in `api/` is the authority; do not edit it.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "C11 — parity corrections" before starting the next.

## Task 1 — decimals are sent as JSON strings (9 routes)

```
GET  /api/localization/projects/{slug}/marketplace
POST /api/localization/projects/{slug}/marketplace/{locale}/post
GET  /api/localization/marketplace/jobs/{id}/bids
GET  /api/localization/provider-health
POST /api/localization/provider-health/{provider}/simulate-outage
POST /api/localization/provider-health/{provider}/resolve
GET  /api/localization/vendor/roster
GET  /api/localization/vendor/{id}/awarded-jobs

.NET:    "suggestedPriceLow": 140.00,   "vendorRating": 4.9,   "errorRatePercent": 0.4
Python:  "suggestedPriceLow": "140.00", "vendorRating": "4.9", "errorRatePercent": "0.40"
```

Pydantic serialises `Decimal` as a string in JSON mode. System.Text.Json writes a C# `decimal` as a JSON number. The React app does arithmetic on these fields, so a string is a real break.

Change: in `app/schemas/base.py`, add one shared annotated type next to `DotNetDateTime`, a `Decimal` with a `PlainSerializer` that returns a `float` when used for JSON, and use it for **every** `Decimal` field in every response schema under `app/schemas/`. Known ones (`grep` for the rest, do not rely on this list):

```
app/schemas/localization_dtos.py: 95, 96, 109, 110, 127, 128, 141, 149, 157
app/schemas/chat_dtos.py:         39, 45, 46, 57
```

Optional fields (`Decimal | None`) must still serialise `None` as `null`. Request models that only receive a decimal need no change. Then search `app/routers/` for responses built as plain dicts or `JSONResponse` that contain a `Decimal` (for example `app/routers/admin_endpoints.py:237`) and make those numbers too.

The comparison is numeric: `140.0` equals .NET's `140.00`. Do not try to reproduce trailing zeros.

Add a unit test (no database) that dumps one model of each affected schema file to JSON and asserts the decimal fields are JSON numbers, including a `None` case.

## Task 2 — timestamps carry one digit too many (all timestamp fields)

Same database value, read raw from both servers by the reviewer:

```
.NET:    "postedAt":"2026-11-02T00:15:02.705684Z"
Python:  "postedAt":"2026-11-02T00:15:02.7056840Z"
```

`format_dotnet_datetime` in `app/schemas/base.py:16-29` always writes seven fractional digits (`value.microsecond * 10:07d`). System.Text.Json writes at most seven digits and drops trailing zeros. PostgreSQL stores microseconds, so the seventh digit is always zero and .NET never shows it.

Change in `format_dotnet_datetime` only: build the six-digit microsecond string and strip trailing zeros (`f"{value.microsecond:06d}".rstrip("0")`); keep the existing branch that writes no fraction at all when the microsecond part is zero. Update the docstring.

One thing the reviewer has **not** observed on the live server: a value whose microseconds end in zero (for example `.705680`). Stripping all trailing zeros (`.70568Z`) is what System.Text.Json does to the reviewer's knowledge; say in `PROGRESS.md` that this case is from documentation, not from the run.

`app/main.py:219` uses `datetime.now(UTC).isoformat()` for the health timestamps, which gives `+00:00` instead of `Z`. Compare with what `Program.cs` writes for `/health`, `/health/ready` and `/` and use `format_dotnet_datetime` there if the C# writes a `DateTime`. Same check for `app/services/reading_map_service.py:72`.

Update any existing test that asserts the seven-digit form, and add cases for: no fraction, six significant digits, trailing zeros.

## Task 3 — routes with a typed id answer differently for an id of the wrong type (3 routes found, many more affected)

```
DELETE /api/auth/sessions/1                      .NET 404 (empty body)   Python 401
POST   /api/v2/practice-questions/1/attempts     .NET 404 (empty body)   Python 422 (validation detail)
POST   /api/v2/practice-questions/1/retry        .NET 404 (empty body)   Python 422
```

In C# these are route constraints: `"/sessions/{sessionId:guid}"` (`api/Endpoints/AuthEndpoints.cs:63`). When the segment is not a GUID the route does not match at all, so the answer is a plain 404 before authentication or validation runs. In the port the path is `"/sessions/{session_id}"` with a `UUID` parameter, so the route matches and then either the auth dependency answers 401 or FastAPI answers 422.

Starlette has the same idea: path convertors. `"/sessions/{session_id:uuid}"` only matches a UUID, and `"/items/{item_id:int}"` only matches digits; anything else is a 404 from the router.

Change: for every C# route that has a `:guid` or `:int` constraint, add the matching `:uuid` or `:int` convertor to the Python path. Keep the function parameter's type annotation as it is. The C# list (the reviewer's `grep`, 37 routes; re-run the search yourself and treat the C# as the authority):

```
api/Endpoints/AdminEndpoints.cs:27, 30, 33                         {id:int}
api/Endpoints/AuthEndpoints.cs:63                                  {sessionId:guid}
api/Endpoints/ChatEndpoints.cs:31, 34                              {id:guid}
api/Endpoints/Localization/LocalizationEndpoints.cs:26, 35, 38, 41, 44   {stringId:int}, {stepId:int}
api/Endpoints/Localization/MarketplaceEndpoints.cs:25, 28, 31, 34  {jobId:int}, {bidId:int}
api/Endpoints/Localization/VendorPortalEndpoints.cs:20, 23, 26, 29, 32, 35   {vendorId:int}, {jobId:int}, {stringId:int}
api/Endpoints/MeEndpoints.cs:35, 41, 47, 53                        {lessonId:int}, {problemId:int}
api/Endpoints/V2Endpoints.cs:197, 227                              {presentationId:guid}
api/Program.cs:685, 776, 964, 1057, 1075, 1091, 1151, 1282, 1481   {id:int}
```

Routes whose C# path has **no** constraint (for example `/api/exercises/{exerciseId}`, `{slug}`, `{localeCode}`) must not get a convertor.

Two things to check and report, not guess:

- Whether a convertor changes the path string that `app.openapi()` reports. `tests/exercises/test_exercise_endpoint_mapping.py` and any test that asserts a route path must still describe the same route.
- What the C# returns for an unmatched route: status 404 with an empty body. If the port's 404 for an unmatched route has a different body (FastAPI's default is `{"detail":"Not Found"}`), find how `app/main.py` or `app/errors.py` already handles unknown paths and say in the report whether the bodies match. Do not add a new handler in this task; just report.

## Task 4 — exercise run and check build a Docker client before looking up the exercise (2 routes)

```
POST /api/exercises/java-add-hotel-rooms/run     .NET 404 "Exercise not found."
POST /api/exercises/java-add-hotel-rooms/check   Python 500 "Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, ...))"
```

That id does not exist (see Task 5), and the test machine has no Docker socket. The lookup order inside `ExerciseService.execute_async` is right and matches the C#. The 500 happens earlier: `ExerciseService.__init__` (`app/services/exercises/exercise_service.py:65`) creates `LocalDockerExerciseRunner()`, whose `__init__` (`app/services/exercises/local_docker_exercise_runner.py:62`) calls `docker.DockerClient(...)`, and that constructor contacts the daemon immediately. In C# the Docker client is created by dependency injection without connecting; it first talks to Docker when a run starts.

Change in `local_docker_exercise_runner.py` only: create the client lazily. `__init__` stores the injected client (or `None`) and the options; a private accessor creates `docker.DockerClient(base_url=..., timeout=30)` on first use and caches it. `_api` (line 66-68) and the use at line 202 go through the accessor. An injected client is used as given.

Then check what the C# returns when Docker is unreachable during a real run (the exception handling in `api/Endpoints/ExerciseEndpoints.cs` `ExecuteAsync` and in `ExerciseService.cs`) and make sure the port maps the Docker connection error to the same status and problem body rather than a generic 500. Report what the C# does and what you changed.

Add a unit test with no Docker: constructing `ExerciseService()` with a repository that returns `None` and calling `execute_async` raises `ExerciseNotFoundException` and never constructs a Docker client.

## Task 5 — the parity tool and its route list (`tools/`)

1. `tools/parity.py`, `_render` (line 50-51) returns two list items: the status line and the whole JSON as one string. `difflib` then treats a 6,000-line response as a single changed line, so the output cannot be read. Make `_render` return the status line followed by the JSON split into lines (`json.dumps(...).splitlines()`).
2. Same file: compare numbers by value, so `140.0` on one side and `140.00` on the other is not a difference. JSON parsing already does this; just make sure nothing re-introduces a string comparison.
3. Add `occurredAt` to the default `--ignore` list and to the command in the header of `tools/parity_routes.txt`. It is a request-time timestamp.
4. `tools/parity_routes.txt`: the exercise id `java-add-hotel-rooms` does not exist in `exercises/` (both APIs answer 404 for its metadata). Replace it in all six exercise lines with a real id read from an `exercise.json` under `exercises/java/`, for example `java-lld-bounded-generics-find-max`; confirm the id by reading the file.
5. Keep the three wrong-type-id lines (`/api/auth/sessions/1`, `/api/v2/practice-questions/1/attempts`, `/retry`); after Task 3 they are a deliberate check of the 404. Add a comment line above each group saying so.

## Not in this prompt

`GET /api/courses`, `GET /api/chapters` and `GET /api/v2/learning-paths` differ only in the order of two courses: `high-level-design` (id 3) and `aws-agentic-ai-bootcamp` (id 8) both have `orderIndex` 4. Both codebases sort by `OrderIndex` alone, so the order of a tie is whatever PostgreSQL returns for each query. The content is identical when sorted. That is a data and C# question for the repository owner, not a port bug. Do not add a tie-break to the port.

## Finish

End with a short report: each task done or not done, files changed, the two answers Task 3 asks for, what the C# does when Docker is unreachable (Task 4), and anything that could not be done as written. Never say a test or check passes; you have not run it.
