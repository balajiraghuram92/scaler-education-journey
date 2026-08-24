# Docker Instructions

Reference for the local Docker workflow discussed in this Codex session.

These commands are recorded from the conversation as recommended commands. They
are not a claim that every command was successfully executed in this workspace.

## Project-specific rules

- Use the local Compose overlay for development:
  `docker-compose.yml` + `docker-compose.dev.yml`.
- Build the API and app locally. This avoids pulling a published image that may
  not contain the host architecture.
- The API image already has this entrypoint:
  `dotnet StudyTracker.Api.dll`.
- Therefore, pass only the CLI flag after `api`.

Correct:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --migrate
```

Do not repeat the entrypoint like this:

```powershell
docker compose run --rm api dotnet StudyTracker.Api.dll --migrate
```

## Issue: published image has no matching host architecture

The earlier pull failed with:

```text
no matching manifest for linux/amd64/v4 in the manifest list entries
```

This means the published GHCR image did not include a compatible `linux/amd64`
manifest for the current Docker host. Build the API and app locally instead of
using the published image:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --pull api app
```

The `--pull` option refreshes the base images while the Compose development
overlay ensures the project images are built from the local source.

## Use case: start only PostgreSQL

Start the database before running one-off API migration or seed commands:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d database
```

Check the service state:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

## Use case: apply schema migrations locally

Build the API first, then apply the application's EF Core migrations through its
CLI mode:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml build api
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --migrate
```

## Use case: seed reference and curriculum data

Run the idempotent reference seeder after migrations:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data
```

This seeds or repairs the canonical course data, including the current
top-level pathways:

- Java Low-Level Design & Spring Architecture
- Forward Deployed Engineer (FDE)
- Databases & SQL
- High-Level Design
- Data Engineering

## Use case: inspect content reconciliation before applying changes

Run both reconciliation scopes as dry runs first:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope fde --dry-run
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope java --dry-run
```

Review both reports before applying anything.

## Use case: apply reconciled legacy content

Only run these after the dry-run reports are acceptable and the canonical
course seeding completed successfully:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope fde --apply
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope java --apply
```

## Use case: start the complete local website

After building, migrating, and seeding:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate api app
```

Or rebuild and start everything in one step after source changes:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build --force-recreate
```

## Recommended complete sequence

Use this order for a fresh local update:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d database
docker compose -f docker-compose.yml -f docker-compose.dev.yml build --pull api app
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --migrate
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope fde --dry-run
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --reconcile-content --scope java --dry-run
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate api app
```

Apply reconciliation only after reviewing the two dry-run reports.

## Issue: inspect API or database logs

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=200 api
```

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=200 database
```

Follow API logs live:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f api
```

Check the local API health endpoint:

```powershell
curl.exe http://localhost:5000/health
```

## Issue: verify that standalone courses were seeded

If the local PostgreSQL credentials use the defaults from the Compose file:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec database psql -U studyuser -d studytracker -c "SELECT slug, title, path_type, is_published FROM courses ORDER BY order_index;"
```

The result should include `java-spring-lld`, `fde-curriculum`,
`databases-sql`, `high-level-design`, and `data-engineering`.

## Use case: stop the local environment without deleting data

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml stop
```

To remove the project containers and network while retaining the named
PostgreSQL volume:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

## Intentional database reset only

This removes the PostgreSQL volume and therefore deletes local database data.
Use it only when a clean database reset is explicitly intended:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
```

Do not use this as a normal troubleshooting step when completion state or
authored curriculum data must be preserved.
