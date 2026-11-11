# Python port of the .NET API — standing rules

Every phase prompt (`P0` … `P8`) tells Muse to read this file first. It holds the rules that do not change between phases.

## Purpose

`api/` is an ASP.NET Core 8 minimal API (C#, EF Core, PostgreSQL). The owner wants a complete Python version of it **to read and learn from**. So the port has two jobs, in this order:

1. Be a faithful, readable translation: someone who knows the C# file can open the Python file and find the same logic in the same place.
2. Actually run against the same database and return the same responses, so its correctness can be checked rather than assumed.

The .NET API stays the real, deployed API. Nothing in `api/`, `app/`, `ai-agent/`, `deploy/`, `scripts/`, `.github/` or the existing compose files is edited by this work.

## Authorisation

`CLAUDE.md` at the repo root is written for a different assistant and says that assistant must not write Python. That rule does not apply to this task: the repository owner has asked for this port. You may create and edit files **only under `api-python/`**, plus the one compose override file named in P0.

## Stack (do not substitute)

- Python 3.12
- FastAPI, Uvicorn
- SQLAlchemy 2.x, async, with `asyncpg`; declarative models with `Mapped[...]` / `mapped_column`
- Pydantic v2 for request and response models; `pydantic-settings` for configuration
- `httpx` for outbound HTTP
- `PyJWT`, `cryptography`
- `pytest`, `pytest-asyncio`, `httpx.AsyncClient` for tests
- `ruff` for lint and format, `mypy` for types

Pin exact versions in `api-python/requirements.txt`. Where `ai-agent/requirements.txt` already pins the same package, use the same version.

## Layout

```
api-python/
  README.md              how to run, how to read the code
  PORT-MAP.md            one row per C# source file: C# path | Python path | phase | status | notes
  requirements.txt, requirements-dev.txt, pyproject.toml, Dockerfile
  app/
    main.py              application factory, middleware, router registration   (Program.cs)
    cli.py               --seed-reference-data, --seed-admin, --reconcile-content (Program.cs CLI modes)
    settings.py          all configuration                                       (api/Options/*.cs, appsettings.json)
    db.py                engine and session dependency                           (StudyTrackerContext wiring)
    errors.py            problem-details responses and exception classes
    models/              SQLAlchemy entities                                     (api/Models/*.cs, StudyTrackerContext.cs)
    schemas/             Pydantic DTOs                                           (DTOs.cs, *Dtos.cs)
    services/            one module per C# service, same sub-folders             (api/Services/**)
    routers/             one module per endpoint file                            (api/Endpoints/**, inline routes in Program.cs)
    seed/                seeders and their data                                  (api/Data/*SeedData.cs)
  tests/
  tools/parity.py        calls both APIs and diffs the JSON
```

## Translation rules

- **One C# file → one Python module**, same name in `snake_case`, same sub-folder. Record every pair in `PORT-MAP.md`.
- Every Python module starts with a docstring naming the C# file it was ported from.
- Keep class, method and field names recognisable: `MarketplaceService.AwardBidAsync` → `MarketplaceService.award_bid`. Keep methods in the same order as the C# file.
- Keep the C# comments that explain *why*. Add a short comment only where Python does something a C# reader would not expect (for example, explicit eager loading instead of `Include`).
- Port behaviour, not bugs you can prove are bugs. If you find one, port the C# behaviour as it is and add a row to the "Findings" section of `PORT-MAP.md`. Do not silently fix or silently change anything.
- No clever abstractions the C# does not have. No generic repository layer, no base service class, no metaprogramming.

## Compatibility rules (these make parity checkable)

- **The database schema is owned by EF Core migrations.** The Python code never creates, alters or drops tables and has no Alembic. Models must map the existing tables and columns exactly, taking names from the `[Table]` / `[Column]` attributes and the Fluent configuration in `api/Data/StudyTrackerContext.cs`.
- **Routes**: same path, same method, same status codes as the C#.
- **JSON**: same property names (camelCase, as ASP.NET emits them), same null handling, same date-time format, same enum/string values. Configure this once in a shared Pydantic base model.
- **Errors**: same `application/problem+json` body shape the C# `Problem(...)` helpers produce.
- **Configuration**: read the same environment variable names the .NET app reads (for example `ConnectionStrings__DefaultConnection`, `Jwt__…`, `Auth__…`), so both containers can share one `.env`.
- **Auth artefacts must be interchangeable**: a password hash, session, JWT or TOTP secret written by one API must be accepted by the other. If you cannot make something byte-compatible, stop and report it; do not invent an alternative.
- Decimal columns use `Decimal`, never `float`.

## Safety

- Only ever connect to the local Docker database. Never to a production host.
- Tests that write use a scratch database (created in P0), never the main local one.
- Do not print or commit secrets. Do not edit any `.env*` file; if a new variable is needed, document it in `api-python/README.md`.

## Definition of done for every phase

1. `ruff check`, `ruff format --check`, `mypy app` and `pytest` all pass inside `api-python/`.
2. `PORT-MAP.md` is updated: every C# file in the phase is marked `done`, `partial` (with the reason) or `blocked` (with the reason).
3. For every route in the phase, `tools/parity.py` shows no difference against the .NET API, or the difference is listed under "Findings".
4. Your final message lists: files created, the exact command output for step 1, the parity result, and every Finding. If something in the prompt did not match the code, say so instead of guessing.
