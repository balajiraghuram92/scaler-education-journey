# api-python — Python port of the .NET API

A faithful, readable Python translation of `api/` (ASP.NET Core 8) for
learning: someone who knows the C# file can open the Python file and find the
same logic in the same place. One C# file maps to one Python module with the
same snake_case name in the same sub-folder; every module docstring names its
C# source. Read `PORT-MAP.md` for the file-by-file map and `PROGRESS.md` for
phase history.

## Run locally

```sh
cd api-python
pip install -r requirements-dev.txt
uvicorn app.main:app --port 8081
```

With Docker (same network and database as the .NET `api` service):

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.python.yml up -d --build api-python
```

The Python API listens on host port **8081**. It reads the same environment
variable names as .NET (`ConnectionStrings__DefaultConnection`, `Auth__…`,
`Jwt__…`, `API_KEY`, …) so both containers share one `.env`. Do not edit any
`.env*` file; new variables are documented here (none yet).

## Tests

```sh
cd api-python
pytest
```

Write tests use the scratch database `studytracker_py`, never the main local one.

### Scratch database setup

Create the database in the local Postgres container:

```sh
docker exec -i studytracker-postgres psql -U studyuser -d studytracker -c "CREATE DATABASE studytracker_py;"
```

Apply the EF migrations to it by running the existing .NET image with
`--migrate` and an overridden connection string (take the password from `.env`):

```sh
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps \
  -e ConnectionStrings__DefaultConnection="Host=database;Port=5432;Database=studytracker_py;Username=studyuser;Password=$POSTGRES_PASSWORD" \
  api --migrate
```

Point tests at it (default assumes localhost with the dev credentials):

```sh
set PY_SCRATCH_DATABASE_URL=postgresql+asyncpg://studyuser:<password>@localhost:5432/studytracker_py
pytest
```

## Parity check

```sh
cd api-python
python tools/parity.py --routes tools/parity_routes.txt
```

`tools/parity_routes.txt` covers all 102 routes; see its header comment for
the run-once-per-fresh-seed procedure and the extra `--ignore` fields that
write routes need. `PARITY_DOTNET_BASE` (default `http://127.0.0.1:5000`) and
`PARITY_PYTHON_BASE` (default `http://127.0.0.1:8081`) select the two servers.
`--ignore` lists volatile fields (default:
`timestamp,traceId,traceid,appliedMigrationsCount`).

## Lint and types

```sh
cd api-python
ruff check .
ruff format --check .
mypy app
```

## Seed data extraction and CLI

The two giant curriculum seed files are extracted to JSON (run once from the repo root):

```sh
python api-python/tools/extract_seed_data.py [--check]
```

CLI modes (same flags and exit codes as the .NET API):

```sh
cd api-python
python -m app.cli --migrate                # schema check only; migrations stay EF-owned
python -m app.cli --seed-reference-data    # full reference-data seed
ADMIN_EMAIL=a@b.c ADMIN_PASSWORD=<16+ chars> python -m app.cli --seed-admin
python -m app.cli --reconcile-content --scope fde --apply
```

## Reading guide for C# developers

### Suggested reading order (one request, start to finish)

Follow a single request through the localization area, then branch out:

1. `app/main.py` — application factory: middleware pipeline, then router
   registration in `Program.cs` map order (lines 196-214).
2. `app/routers/localization/localization_endpoints.py` — route handlers;
   start with `get_project` (lines 69-79): parse params, call the service,
   map exceptions to problem responses.
3. `app/services/localization/localization_project_service.py` — the service
   behind it: explicit queries, DTO construction, domain exceptions
   (`get_project_async`, lines 18-43).
4. `app/models/localization/localization_project.py` — the SQLAlchemy entity
   the query loads (columns lines 32-37, relationships lines 39-68).
5. `app/schemas/localization_dtos.py` — the Pydantic DTOs the service
   returns, e.g. `MarketplaceBidDto` (lines 89-99).
6. `app/errors.py` — the problem-details shape every error path returns
   (`endpoint_problem`, lines 106-120).
7. `app/settings.py`, `app/db.py`, `app/cli.py` — configuration, session
   wiring, and the `--seed-reference-data` / `--reconcile-content` CLI modes.
8. `tools/parity.py` + `tools/parity_routes.txt` — how the port proves it
   matches .NET, route by route.

### C# construct → what the port uses instead

| C# | Python port | Real example |
|---|---|---|
| Dependency injection (`AddScoped`, constructor injection) | Plain constructor arguments, wired per request in the router | `app/services/localization/workflow_service.py:74-90` (`WorkflowService.__init__` takes session + 5 services + options) |
| `IOptions<T>` + `SectionName` | One `pydantic-settings` class per Options file, same env names | `app/settings.py:159-175` (`LocalizationAiSettings`, `LocalizationAi__…` aliases) |
| `async`/`await` + `Task<T>` | `async def` + `await`, no `Task` wrapper | `app/services/localization/workflow_service.py:92-99` (`await self._session.execute(...)`) |
| LINQ query + `Where`/`OrderBy`/`FirstOrDefaultAsync` | SQLAlchemy `select()` + `.where()` / `.order_by()` + `.scalar_one_or_none()` / `.scalars().all()` | `app/services/localization/marketplace_service.py:63-84` |
| `Include` / `ThenInclude` | `selectinload` chains; models use `lazy="raise"` so every load is explicit | `app/services/localization/marketplace_service.py:66-71` |
| Filtered `Include(x => x.Y.Where(...))` | `selectinload` with `.and_(...)` loader criteria | `app/services/localization/localization_string_service.py:47-56` |
| Records + response DTOs | Pydantic `CamelModel` (camelCase JSON like ASP.NET) | `app/schemas/localization_dtos.py:89-99` (`MarketplaceBidDto`) |
| Internal result records | `@dataclass` | `app/services/localization/localization_ai_client.py:42-51` (`OptimizeTranslationResult`) |
| Interfaces (`ITranslationProvider`) | `typing.Protocol` | `app/services/localization/i_translation_provider.py:8-11` |
| Custom exceptions → `Problem(...)` | Same exception names → `endpoint_problem(...)` with the same titles | `app/routers/localization/localization_endpoints.py:73-79` catches, `app/errors.py:106-120` renders |
| `ArgumentException` messages | `ValueError` with the .NET `" (Parameter 'x')"` suffix reproduced verbatim | `app/services/localization/workflow_service.py:550-567` (`_validate_action_and_trigger`) |
| `NotImplementedException` → 501 | `NotImplementedError` → 501 | `app/routers/localization/localization_endpoints.py:214-234` (`run_workflow_step`) |
| Middleware pipeline (`UseCors`, `UseAuthentication`, custom) | `@app.middleware("http")` functions in the same order | `app/main.py:74-103` (correlation + errors), `app/main.py:104-130` (x-api-key check) |
| Hosted CLI modes (`--migrate`, `--seed-*`) | `argparse` in `app/cli.py`, same flags and exit codes | `app/cli.py:27-36` (parser), `app/cli.py:46-74` (`_run_migrate`) |
| `HttpClient` + typed clients | `httpx.AsyncClient`, owned per call unless injected (for `MockTransport` tests) | `app/services/llama_api_client.py:94-104` |
| `decimal.Round(x, 6)` (banker's) | `Decimal.quantize(..., rounding=ROUND_HALF_EVEN)` | `app/services/localization/workflow_service.py` ledger writes in `run_step_async` |
| `DateTime.UtcNow` JSON (`...Z`, 7-digit fraction) | `DotNetDateTime` serializer | `app/schemas/base.py:16-34` (`format_dotnet_datetime`) |

### Conventions worth knowing

- Services `flush()`; routers `commit()`. Read-only handlers never commit.
- Money is always `Decimal`, never `float`.
- The Python code never creates or alters tables: no Alembic, `--migrate`
  only checks the schema (`app/seed/schema_check.py`, via P1's parity test).
- Ported quirks stay ported: anything the C# does that looks wrong is kept
  and recorded in the Findings section of `PORT-MAP.md`, never silently fixed.
