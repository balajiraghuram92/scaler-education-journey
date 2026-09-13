# Session Summary — Postgres → pgvector Production Migration (2026-09-13)

> **Read this before touching the production database again**, especially
> before any future image swap, container recreation, or manual
> backup/restore on the `neuralascent.top` EC2 host. This documents a real
> production migration that succeeded, plus several concrete mistakes made
> along the way that are worth not repeating. Written to stand alone — no
> other conversation context assumed.

**Session span:** 2026-09-13
**Scope:** switching the production Postgres database to a pgvector-enabled
image, to give the AI Learning Agent (`ai-agent/`, Phase 1 "The Substrate") a
place to store embeddings. See
[ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) for
where this fits in the overall build plan.

---

## What actually changed

1. **`docker-compose.yml`** (local dev only, via `scripts/local-stack.sh`) —
   the `database` service's image changed from `postgres:16-alpine` to
   `pgvector/pgvector:pg16`.
2. **`scripts/deploy-single-ec2.sh`** (production) — this script does **not**
   use `docker-compose.yml` at all; production is a hand-rolled sequence of
   `docker run` commands with its own independent default:
   ```bash
   POSTGRES_IMAGE="${POSTGRES_IMAGE:-pgvector/pgvector:pg16}"
   ```
   **If you're hunting for "why did changing docker-compose.yml not affect
   prod," this is why — always check both places.**
3. **`.github/workflows/deploy-api.yml`** — the SSM deploy command has a
   hardcoded `ALLOW_CREATE_DATABASE=false` flag on the line that invokes
   `deploy-single-ec2.sh`. This has to be temporarily flipped to `true` for
   exactly one deploy run whenever the existing database container is
   intentionally removed (see below) — **then flipped back to `false`
   immediately after**. Leaving it `true` permanently defeats a real safety
   guard (an accidentally-missing container would silently get a brand-new
   *empty* database instead of the deploy failing loudly).

## Why a container removal was needed at all

`deploy-single-ec2.sh` deliberately **never recreates an existing database
container** — if `studytracker-postgres` already exists, it just does
`docker start` on it, regardless of what `POSTGRES_IMAGE` is set to. This is
a safety feature (a routine deploy should never blow away a live database),
but it means an image swap for an *existing* database requires manually
removing the old container first:
```bash
docker stop studytracker-postgres
docker rm studytracker-postgres
```
The data is untouched by this — it lives in the named volume
(`scaler_postgres_data`), completely independent of the container. Once no
recognized Postgres container exists, the *next* deploy run falls into the
script's "create fresh container" branch, pulls the new image, creates a new
container against the same volume, and (via `RESTORE_LATEST_BACKUP=true`,
already permanently on in the workflow) restores the latest S3 backup into
it since the fresh container's database will be empty.

## Mistakes made this session — read before repeating any of these

1. **A bash unbound-variable bug in `deploy-single-ec2.sh` line 16.** The
   intended edit `POSTGRES_IMAGE="${POSTGRES_IMAGE:-pgvector/pgvector:pg16}"`
   got mangled into `POSTGRES_IMAGE="${pgvector/pgvector:pg1}"` — dropping
   the `POSTGRES_IMAGE:-` prefix entirely (so bash tried to look up a
   variable literally named `pgvector`, which doesn't exist, and `set -u`
   killed the script immediately) and losing the trailing `6` from `pg16`.
   **Lesson: run `bash -n scripts/deploy-single-ec2.sh` locally before
   pushing any edit to this file** — it catches this exact class of error
   with zero risk, before it ever reaches a production SSM run.

2. **The actual production database name is `StudyTrackerDB` (mixed case),
   not `studytracker`.** The lowercase `studytracker` is only a *fallback
   default* baked into `docker-compose.yml` and the deploy script's own
   `env_value_or_default POSTGRES_DB studytracker` calls — it's used only if
   the real `api.env` file is missing the key entirely. The real `api.env`
   has `POSTGRES_DB=StudyTrackerDB` explicitly set, and the deploy script
   correctly reads that everywhere internally. **A person manually running
   `psql`/`pg_dump` against this host must use the real name,
   `"StudyTrackerDB"` (quoted, since it's mixed-case), not the script's
   fallback default** — assuming the fallback is the real name produces a
   `FATAL: database "studytracker" does not exist` error that looks like
   data loss but isn't.

3. **`docker exec -t` corrupts binary output.** The first two manual
   `pg_dump -F c` backup attempts this session used `docker exec -t
   studytracker-postgres pg_dump ... > file.dump`. The `-t` flag allocates a
   pseudo-terminal, which is fine for interactive text sessions but **can
   corrupt raw binary streams** redirected through it — confirmed here by
   `pg_restore --list` reporting nonsense (`out of memory`, a garbage TOC
   entry count, an impossible creation year like `34335`) on files produced
   with `-t`. **Never use `-t` (or `-it`) on a `docker exec` whose stdout is
   being redirected to a file for binary data.** The working, verified
   command (no `-t`):
   ```bash
   docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" studytracker-postgres \
     pg_dump -U studyuser -d "StudyTrackerDB" -F c \
     > "StudyTrackerDB_backup_$(date +%Y%m%d_%H%M%S).dump"
   ```

4. **Always verify a backup immediately after taking it, before trusting
   it as a safety net for anything risky.** The first two backups taken this
   session (before the container removal) were silently invalid — mistake #2
   above meant `pg_dump -d studytracker` was targeting a database that
   didn't exist. No data was actually lost, because the deploy script's own
   internal backup/restore cycle used the correct name throughout and worked
   correctly — but the manually-taken "safety net" backup was never real,
   and this was only caught *after* the fact by explicitly running
   `pg_restore --list` against it. Verification command:
   ```bash
   docker run --rm -v ~/:/backups:ro pgvector/pgvector:pg16 \
     pg_restore --list /backups/<filename>.dump | head -30
   ```
   A valid dump shows a sane creation date, `dbname: StudyTrackerDB`, a
   positive TOC entry count, and real table names. A corrupt/invalid one
   shows garbage values or errors outright.

5. **`docker exec` cannot see files on the host filesystem at all** —
   containers have their own isolated filesystem. A file living at
   `/home/ec2-user/foo.dump` on the EC2 host is invisible to `docker exec
   studytracker-postgres ...` unless the container was started with that
   path bind-mounted. To run `pg_restore --list` (or anything else) against
   a host file using a tool that only exists inside a Postgres image, use a
   disposable container with an explicit volume mount instead:
   ```bash
   docker run --rm -v ~/:/backups:ro pgvector/pgvector:pg16 pg_restore --list /backups/<filename>.dump
   ```

6. **Verified before touching production: `pgvector/pgvector:pg16` does
   publish a genuine `arm64` manifest** (checked via `docker manifest
   inspect pgvector/pgvector:pg16` on the EC2 host, which is arm64-only —
   `deploy-single-ec2.sh` hard-fails on any other architecture). Worth
   re-checking with the same command if this ever needs to be repeated
   against a different image/tag in the future — not every image on Docker
   Hub publishes every architecture, and `deploy-single-ec2.sh` does not
   verify `POSTGRES_IMAGE`'s platform the way it does for the `api`/`app`/
   `ai-agent`/`runner` images.

## Current state — what's actually done, and what's still open

- ✅ Production `studytracker-postgres` container now runs
  `pgvector/pgvector:pg16` (confirmed genuine arm64 build).
- ✅ All existing data confirmed intact post-migration (verified via a real,
  valid `pg_restore --list` against a fresh manual backup — 324 TOC entries,
  real table names: `Tasks`, `app_users`, `chat_conversations`,
  `concept_prerequisites`, etc.)
- ✅ `ALLOW_CREATE_DATABASE` in `.github/workflows/deploy-api.yml` confirmed
  flipped back to `false` after the migration deploy succeeded.
- ✅ One genuinely valid backup exists:
  `StudyTrackerDB_backup_20260913_131226.dump` (on the EC2 host as of this
  writing — **get this off the host**, e.g. `scp` or S3, a backup that lives
  only on the box you just modified isn't a real safety net).
- ✅ `CREATE EXTENSION IF NOT EXISTS vector;` has been run manually against
  `StudyTrackerDB` — `vector` now shows up in `\dx`.
- ⚠️ **OPEN — not yet fixed:** the `CREATE EXTENSION vector` step above was
  run **manually, once, directly against the live database** — it is not
  recorded in any migration or init script. If this database is ever
  recreated from scratch again (new host, disaster recovery, a future
  `ALLOW_CREATE_DATABASE=true` scenario), **nobody will know to re-run this**,
  and Phase 1.2 ingestion work will fail with a missing-extension error
  until someone remembers this file exists. **Before this is considered
  production-hardened, decide where this belongs long-term** — most likely
  either as a `.NET` EF Core migration (so the API's own `--migrate` step
  handles it automatically, same as any other schema change) or a Postgres
  init script that runs on container/volume creation. This was flagged to
  the user and intentionally left as a decision for them, not fixed inline.
- ⏳ Two known-corrupt files still exist on the EC2 host and should be
  deleted so nobody mistakes them for real backups:
  `neuralascent_backup_20260913_071003.dump`,
  `neuralascent_backup_20260913_071038.dump`, and
  `StudyTrackerDB_backup_20260913_130244.dump` (the `-t`-corrupted one).

## Cross-references

- [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) —
  Phase 1.2 (content ingestion pipeline) is the next real work, and depends
  on the `vector` extension being enabled (done, but see the open item
  above) and on a working embedding-model call (Deepinfra
  `BAAI/bge-m3`/`bge-reranker-v2-m3`, cloud-API-first per the 2026-09-13
  sequencing decision already recorded there).
- [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md)
  — full project context, locked architecture decisions.
- `docker-compose.yml`, `scripts/deploy-single-ec2.sh`,
  `.github/workflows/deploy-api.yml` — the three files actually touched this
  session.
