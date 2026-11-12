# C12 — `api-python/`: second live parity run

C11 worked. Reviewer's runs after it:

- ruff clean, mypy clean (173 files). Tests: 120 passed without a database; **183 passed, 1 skipped** with one.
- Live parity against the .NET API on identical data: **93 of 102** routes match (was 85). The decimal, timestamp, Docker-client and typed-id status-code differences are gone.

Of the nine that still differ, three are the course-order tie in the data (not a port bug, unchanged) and six have the three small causes below.

Logs in `info/muse-prompts/corrections/round12/`: `parity.log.gz`, `parity-summary.txt`.

Paste everything below this line into Muse Code at the repository root.

---

Work only in `api-python/`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. The C# in `api/` is the authority; do not edit it.

Do the tasks in order. After each task, append what you did to `api-python/PROGRESS.md` under "C12 — parity corrections, second run" before starting the next.

## Task 1 — an unmatched route answers with a body; .NET answers with none (3 routes)

```
DELETE /api/auth/sessions/1
POST   /api/v2/practice-questions/1/attempts
POST   /api/v2/practice-questions/1/retry

.NET:    404, empty body
Python:  404, {"detail": "Not Found"}
```

The status is now right (the convertors from C11 work). The body is Starlette's default for a path no route matches. ASP.NET writes no body in that case.

`app/main.py` registers handlers for `ApiProblem` (line 132) and `ChallengeException` (line 143) but none for the router's own "no route matched" error.

Change in `app/main.py`: register a handler for `starlette.exceptions.HTTPException`. When the status is 404 **and** the detail is Starlette's default text `"Not Found"`, return `Response(status_code=404)` with no body and no content type. For every other case, delegate to FastAPI's stock handler (`fastapi.exception_handlers.http_exception_handler`) so nothing else changes.

Before writing it, list in `PROGRESS.md` every place in `app/` that raises `HTTPException` (FastAPI's or Starlette's) with status 404, and confirm none of them relies on the default detail and expects a JSON body. Endpoints that answer 404 through `ApiProblem` or `endpoint_problem` are unaffected. If one would be affected, do not change its behaviour; say which and stop that case for the reviewer.

Also check the same default for 405 (path matches, method does not): compare with what ASP.NET returns for a wrong method on a mapped path. Report what you find; change it only if the C# answer is clear from the code.

Add a unit test with `TestClient`: an unknown path under `/api/` with a valid API key returns 404 with an empty body; a known typed-id route called with a non-numeric id does the same.

## Task 2 — exercise files lose their line endings (2 routes)

```
GET /api/exercises/java-lld-bounded-generics-find-max
GET /api/exercises/java-lld-bounded-generics-find-max/solution

.NET:    "starterContent": "package org.example;\r\n\r\n// TODO ..."
Python:  "starterContent": "package org.example;\n\n// TODO ..."
```

The reviewer's checkout is on Windows, so the exercise files on disk have CRLF line endings. C# `File.ReadAllText` returns the file's characters unchanged. Python's `open(path, encoding="utf-8")` uses universal newlines and turns every `\r\n` into `\n`. On a Linux checkout the files have LF and the two agree, which is why no test shows it, but the port should return what is on disk, as the C# does.

Change: add `newline=""` to the two reads that return file content to the client:

- `app/services/exercises/exercise_metadata_service.py:79` (C#: `ExerciseMetadataService.cs:65`)
- `app/services/exercises/exercise_solution_service.py:68` (C#: `ExerciseSolutionService.cs:57`)

`File.ReadAllText` also strips a UTF-8 byte-order mark. Check whether the Python read would keep one (`encoding="utf-8"` keeps it, `"utf-8-sig"` strips it) and match the C#.

Leave `app/services/exercises/exercise_repository.py:66` alone: it feeds a JSON parser, where line endings do not matter. `exercise_workspace_builder.py:130` already writes with `newline=""`.

Then check the draft and workspace paths: when a learner's saved file content is stored and returned (`ExerciseProgressService`), does either side change line endings? Read the C# and the port and report; change nothing unless they differ.

Add a unit test that writes a small file containing `\r\n` to a temporary directory and asserts the metadata service and the solution service return it byte-for-byte.

## Task 3 — the parity tool reports `185` and `185.0` as different (1 route, tool only)

```
GET /api/localization/projects/auroraline-hud-v3/marketplace
-    "suggestedPriceHigh": 185,
+    "suggestedPriceHigh": 185.0,
```

.NET writes a `decimal` with no fractional digits as `185`; the port writes `185.0`. As JSON numbers they are equal. `tools/parity.py` compares the re-rendered text, where an `int` and a `float` print differently.

Change in `tools/parity.py`, `_normalize` (lines 42-47): add a branch so that a `float` whose value is integral becomes an `int` (`isinstance(value, float) and value.is_integer()`); `bool` values must pass through untouched. Nothing else in the tool changes.

## Not in this prompt

`GET /api/courses`, `GET /api/chapters`, `GET /api/v2/learning-paths`: still the order of the two courses that share `orderIndex` 4. Leave it.

## Finish

End with a short report: each task done or not done, files changed, the list Task 1 asks for, the 405 finding, the line-ending finding for drafts, and anything that could not be done as written. Never say a test or check passes; you have not run it.
