# EC2 Update Tracker

Living checklist of everything that must happen on the EC2 instance to bring prod up to date with `main`.
Update the **Status** column and the **Log** at the bottom after each step. Commands print variable **names** only — never paste secret values into this file or chat.

- Created: 2026-10-01 · Source of truth for the deploy mechanics: `scripts/deploy-single-ec2.sh`, `info/history/04-deployment-infra-and-ops.md`.
- Last prod deploy before this list: **unknown — fill in** `____`.
- Local state (WSL): already updated and verified on 2026-10-01 (images rebuilt, six lessons reseeded). Nothing below has been run on EC2.
- Deploy trigger: push to `main` with `[deploy]` in the **head** commit message, or run the workflow manually (`.github/workflows/deploy-api.yml`). Merging a PR does not deploy unless the merge commit message contains `[deploy]`.

Status key: `[ ]` not done · `[x]` done on EC2 · `[-]` not needed

---

## 1. What changed since the last prod deploy

| # | Change (PR) | Needs on EC2 | Status |
|---|---|---|---|
| 1 | `ai-agent/` hardening (PR #2): safe DB connection from `DATABASE_*`/`DATABASE_URL`, auth on `/echo` and `/agent_test`, strict JWT, rate limit, non-root image, `/health/ready`, tests + CI | New env contract (section 2 step 1); deploy | `[ ]` |
| 2 | `migrate.py` fixed for empty DBs, one transaction per file | Run once by hand after deploy (section 2 step 7); never run automatically | `[ ]` |
| 3 | nginx tutor block: rate limit, 1 MB body limit, 120 s timeout, `/health` now proxied to FastAPI, runtime lookup of `ai-agent` | `app` image redeploy (done by the deploy); verify tutor URLs | `[ ]` |
| 4 | Deploy script: env check before touching containers, container logs captured before rollback | None (ships with the repo) | `[ ]` |
| 5 | Java lessons rewritten in seed: `14-spring-boot-core`, `15-spring-data-jpa`, `16-spring-rest-api`, `17-machine-coding-capstone`, `24-machine-coding-hotel-management`, plus the `21-machine-coding-bookmyshow` scenario fix | **Reseed those 6 slugs** (section 2 step 6). The seeder is write-once, so a deploy alone does not update them | `[ ]` |
| 6 | New exercises `splitwise-create-delete-group`, `splitwise-manage-group-members`, `bms-book-ticket`, wired to L21/L22 (frontend + API image) | Nothing extra; verify after deploy (section 2 step 8). Confirm the runner finds them | `[ ]` |
| 7 | Knowledge Atlas `ConceptNextLesson` slug fixes | None — only applies to a fresh atlas seed; the site ignores them today | `[-]` |
| 8 | `CLAUDE.md` reseed procedure + DB names (PR #3) | None (docs) | `[-]` |

---

## 2. Ordered runbook (do in this order)

Prod names (from the repo notes — confirm before use): DB container `studytracker-postgres`, user `studyuser`, database `StudyTrackerDB`, API container `studytracker-api`, ai-agent container `neuralascent-ai-agent` (compose) or `ai-agent` (deploy script; check with `docker ps`), network `scaler-network`, env file `/etc/studytracker/api.env`.

### Step 1 — Environment variable names (`[ ]`)
```bash
sudo cut -d= -f1 /etc/studytracker/api.env | sort
```
Required for ai-agent: `Auth__JwtSigningKey` (32+ bytes), `MUSE_AI_API_KEY`, and either `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` (+ optional `DATABASE_PORT`) **or** `DATABASE_URL` (percent-encoded password). `DATABASE_NAME` must be `StudyTrackerDB`.
Recommended: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (without them tracing is off). Optional: `DEEPINFRA_API_KEY`. No quotes around values.
The bootstrap script only fetches SSM when `/etc/studytracker/api.env` is missing, so after changing SSM refresh the file by hand (or move it aside so bootstrap recreates it). The deploy now **fails before touching any container** if the database names or `MUSE_AI_API_KEY` are missing.

### Step 2 — Prod DB is pgvector (`[ ]`)
```bash
docker inspect --format '{{.Config.Image}}' studytracker-postgres          # expect pgvector/pgvector:pg16
docker exec studytracker-postgres psql -U studyuser -d StudyTrackerDB -tAc "SELECT extversion FROM pg_extension WHERE extname='vector'"
docker exec studytracker-postgres psql -U studyuser -d StudyTrackerDB -tAc "SELECT to_regclass('schema_migrations'), to_regclass('content_chunks')"
```

### Step 3 — Backup (`[ ]`)
The deploy takes a pre-migration `pg_dump` and verifies it (`backup_database` in the script). For an extra manual copy before the lesson reseed:
```bash
docker exec studytracker-postgres pg_dump -U studyuser -F c StudyTrackerDB > /var/backups/studytracker/manual_$(date +%Y%m%d_%H%M).dump
```

### Step 4 — Note which lessons are Published (`[ ]`)
```bash
docker exec -i studytracker-postgres psql -U studyuser -d StudyTrackerDB <<'SQL'
SELECT slug, content_status, length(content_body) AS chars FROM lessons
WHERE slug IN ('14-spring-boot-core','15-spring-data-jpa','16-spring-rest-api',
               '17-machine-coding-capstone','21-machine-coding-bookmyshow','24-machine-coding-hotel-management')
ORDER BY slug;
SQL
```
Write the result in the Log. The reseed sets these back to `Draft`; republish the reviewed ones afterwards.

### Step 5 — Deploy (`[ ]`)
Merge to `main`, then deploy with a `[deploy]` commit message or the manual workflow. The script backs up, runs `api --migrate` and `api --seed-reference-data`, and replaces the api, ai-agent and app containers. Check:
```bash
curl -s localhost:5001/health                  # {"status":"ok"}
curl -s localhost:5001/health/ready            # database: ok
curl -s https://tutor.neuralascent.top/health  # now FastAPI JSON, not a fixed "healthy"
curl -s -o /dev/null -w '%{http_code}\n' https://tutor.neuralascent.top/echo    # 401
curl -s -o /dev/null -w '%{http_code}\n' https://tutor.neuralascent.top/docs    # 404
```
If it fails, the script prints container state and the last 100 log lines before rolling back (SSM output and the S3 `deploy-logs/<sha>/` prefix). Rollback does **not** undo database changes.

### Step 6 — Reseed the six lessons (`[ ]`) — only after step 5 succeeded
Deploy first so the new API image carries the new text. There is a short window where those six lessons are empty.
```bash
docker exec -i studytracker-postgres psql -U studyuser -d StudyTrackerDB <<'SQL'
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN ('14-spring-boot-core','15-spring-data-jpa','16-spring-rest-api',
               '17-machine-coding-capstone','21-machine-coding-bookmyshow','24-machine-coding-hotel-management');
SQL
API_IMAGE=$(docker inspect --format '{{.Config.Image}}' studytracker-api)
docker run --rm --network scaler-network --add-host host.docker.internal:host-gateway \
  --env-file /etc/studytracker/api.env "$API_IMAGE" --seed-reference-data
```
Restarting the API alone does **not** seed. Verify (expect `Draft`, roughly 8,500–15,700 chars, all three heading columns `t`):
```bash
docker exec -i studytracker-postgres psql -U studyuser -d StudyTrackerDB <<'SQL'
SELECT slug, content_status, length(content_body) AS chars,
       content_body LIKE '%## Practical Backend Scenario%' AS has_scenario,
       content_body LIKE '%## Practice Loop%' AS has_loop,
       content_body LIKE '%## Evidence of Understanding%' AS has_evidence
FROM lessons
WHERE slug IN ('14-spring-boot-core','15-spring-data-jpa','16-spring-rest-api',
               '17-machine-coding-capstone','21-machine-coding-bookmyshow','24-machine-coding-hotel-management')
ORDER BY slug;
SQL
```

### Step 7 — Run `migrate.py` once for the ai-agent tables (`[ ]`)
Needs `lessons` to exist (the deploy's `api --migrate` creates it).
```bash
docker exec neuralascent-ai-agent python migrate.py    # use the container name from `docker ps`
# expect: 001_...: applied, 002_...: applied, "migrate: done (2 applied)"; run again -> "already applied, skipping"
docker exec -i studytracker-postgres psql -U studyuser -d StudyTrackerDB -c "SELECT filename, applied_at FROM schema_migrations"
docker restart neuralascent-ai-agent                   # so pooled connections register the vector type
```
Undo of 002 if ever needed (keep the extension): `DROP TABLE content_chunks; DELETE FROM schema_migrations WHERE filename = '002_create_content_chunks.sql';`
Where `migrate.py` runs long-term is still an open decision.

### Step 8 — Verify content and exercises (`[ ]`)
Open lessons 21 and 22 on the site: L21 shows the BookMyShow exercise, L22 both Splitwise exercises. Run one exercise to confirm the runner accepts them. Skim L14–17 and L24 (L17 and L14–16 are `LLM_GENERATED`).

### Step 9 — Republish what you reviewed (`[ ]`)
Publishing is the manual review gate. Only the tutor-ingested content (`content_status = 'Published'`) reaches the RAG store.
```bash
docker exec -i studytracker-postgres psql -U studyuser -d StudyTrackerDB <<'SQL'
UPDATE lessons SET content_status = 'Published' WHERE slug IN ('<reviewed-slug-1>','<reviewed-slug-2>');
SQL
```

---

## 3. Rollback notes
- `rollback()` restores the previous api/ai-agent/app images only; database changes (EF migrate, seed, `migrate.py`) stay. `migrate.py` changes are additive (extension + a new table), so old images ignore them.
- A rollback to the **previous** ai-agent image needs `DATABASE_URL` (old code). If the env file lacks it, that container crash-loops; the main site stays up and only `tutor.` returns 502.
- Lesson reseed is undone by restoring the manual dump from step 3 (or re-running step 6 with the old text from git).

## 4. Add new items here
When a change needs an EC2 action (env var, one-off command, reseed, certificate), add a row to section 1 and a step to section 2 in the same PR that introduces it. Reusable pattern for any lesson reseed: check status, clear rows, run `--seed-reference-data`, verify, republish (see `CLAUDE.md`).

## 5. Log

| Date | Step | Result / notes |
|---|---|---|
| 2026-10-01 | Local (WSL) | Images rebuilt, six lessons reseeded and verified, L21 and L24 republished locally. EC2 untouched. |
