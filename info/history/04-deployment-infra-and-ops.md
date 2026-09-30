# 04 — Deployment, EC2 / Docker / Infra History & Operational Gotchas

> Consolidated 2026-09-30 from `SESSION-HANDOFF-STATUS.md` (2026-08-31), `SESSION-HANDOFF-2026-09-22.md`, the infra parts of
> `SESSION-2026-09-08 / 09-10 / 09-13 / 09-20`, `fde-lessons/2026-09-01-ec2-fde-deployment-investigation.md` (detail in `02-…` §4) and the runbooks/platform plan (`03-…` §§6, 8).
> Deep AI-agent-specific infra detail lives in `07-ai-learning-agent.md` §§8–9; this file is the platform-wide view. Originals at commit `9e6d03f`.

## 1. Production topology (as of 2026-09-22)

- **One EC2 host, arm64 only** (`deploy-single-ec2.sh` hard-fails on any other architecture), Amazon Linux 2023 (RPM host; container images are Debian-based `python:3.12-slim` etc. — host OS is independent of image OS). Domain `neuralascent.top` (IP `98.130.44.145`; bare-IP HTTPS has a cert-name mismatch — use the domain), subdomain `tutor.neuralascent.top` → same IP/Nginx → `ai-agent`. Originally a 1 GB RAM instance (exercise concurrency = 1 for that reason).
- **Containers (plain `docker run`, not Compose):** `studytracker-postgres` (`pgvector/pgvector:pg16`, volume `scaler_postgres_data`, network `scaler-network`), `studytracker-api` (.NET 8), `studytracker-app` (Nginx + React bundle; ports 80/443), `ai-agent` (FastAPI, port 5001 on host → 8000), plus the **dynamic runner image** (`neuralascent-java-runner`, referenced by digest, protected from prune by a local `:deployed` tag) used by the API to launch disposable exercise containers.
- **Prod DB name = `StudyTrackerDB`** (mixed case; user `studyuser`); compose's `studytracker` is only a fallback default. **Never** assume the fallback.
- **Secrets:** AWS SSM Parameter Store `/neuralascent/prod/api-env` (SecureString) → pulled **once** by `scripts/bootstrap-single-ec2.sh` (only `if [ ! -f /etc/studytracker/api.env ]`) into `/etc/studytracker/api.env`; `deploy-single-ec2.sh` reads it (`--env-file`). Editing local `.env`/compose/`.env.example` does nothing for prod. Consider changing the bootstrap guard to always refresh. `Auth__JwtSigningKey` (.NET) and `JWT_SIGNING_KEY` (ai-agent) must be **identical**.
- **TLS:** Let's Encrypt via `certbot certonly --standalone`; cert SAN covers `neuralascent.top` + `tutor.neuralascent.top` (manual `certbot --expand` 2026-09-08; expires 2026-12-07). The deploy script only issues `certonly` for a first-ever cert and only `renew`s afterwards → **every future new subdomain needs a manual `--expand`**.
- **x-api-key:** every `/api/*` request except `/health`, `/swagger`, `OPTIONS` requires the key; prod Nginx injects the real `API_KEY` server-side into `proxy_set_header x-api-key` for the whole `/api` location (secret never reaches the browser). Local dev value in `.env` is literally `your_api_key_here` (deliberate). Do **not** exempt `/api/auth` from the key check (an early Gemini plan tried; reverted).
- **CI/CD:** `.github/workflows/deploy-api.yml` — runs only on `[deploy]` in the commit message (or manual `workflow_dispatch`) → verify API/frontend → build+push `api`, `app`, `ai-agent`, `runner` to GHCR (`ghcr.io/balajiraghuram92/scaler-education-journey-*`) → verify platform manifests → OIDC to AWS → SSM `send-command` (`AWS-RunShellScript`) that `curl`s `bootstrap-single-ec2.sh` + `deploy-single-ec2.sh` from `raw.githubusercontent.com` at the commit SHA (**repo is private → needs `Authorization: token ${{ secrets.GITHUB_TOKEN }}`**, fixed 2026-09-10) → script pulls images **by digest**, takes a pre-migration Postgres backup to S3, runs `--migrate` then `--seed-reference-data` as one-shot containers, starts `api`/`app`/`ai-agent`, health-checks, rolls back on failure (`rollback()` removes the crashed container *before* logs can be read). SSM output is captured to S3 (`--output-s3-bucket-name`, prefix `deploy-logs/${GITHUB_SHA}`) because `get-command-invocation` truncates at a few KB; IAM role `StudyTrackerEC2SSMRole` was widened to `s3:GetObject/PutObject` on `deploy-logs/*` (no delete).
- **Migrations/seeding are not automatic on API start** — only via `--migrate` / `--seed-reference-data` (and `--reconcile-content`, `--seed-admin`). `ALLOW_CREATE_DATABASE=false` and `RESTORE_LATEST_BACKUP=true` are set in the workflow; the DB container is never recreated by a normal deploy.
- **Dev-only Compose:** `docker-compose.yml` + `docker-compose.dev.yml` (dev overrides to local builds); `scripts/local-stack.sh` runs `api --migrate` before `up` — a plain `docker compose up` on a fresh volume leaves the API crashing on pending EF migrations (exit 139). Base compose `image:` tags pull GHCR; dev file `build:`s. Run dev: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`.

## 2. Timeline

| Date | Event |
|---|---|
| 2026-08-23/24 | VM/Docker (macOS host, Linux VM) redesign runtime debugging; platform migration plan written (`03-…`) |
| 2026-08-31 | Handoff: 17 exercises wired locally, MCQ migration (95 q) + Lessons 18–20 content unpushed; deploy-tag discipline lesson (18 commits silently undeployed); last prod HEAD `1542598` (Module 4 self-heal) |
| 2026-09-01 | FDE content stale on EC2 despite green deploys → write-once seeding guard; manual reseed; DR delete/recreate proof (152/152) |
| 2026-09-08 | Phase 0 infra: `ai-agent` skeleton, Nginx `tutor.` blocks, CI + deploy script wiring (`c3742f6`, `f2db042`), DNS (GoDaddy A record), TLS SAN |
| 2026-09-09/10 | First real pipeline runs: .NET test-compile errors, React hooks crash, private-repo curl 404 (`c617bc8`), stale `/etc/studytracker/api.env` missing `Auth__JwtSigningKey` |
| 2026-09-12/13 | SSM value fixed → deploy green; JWT trust bridge verified; **pgvector image swap in prod** |
| 2026-09-20 | Compose dev integration (Podman arc); SSM updated with Muse/Langfuse; first EC2 deploy of `ai-agent` — `--env-file` omission (`b37b78a`), S3 log capture (`a3d6c14`), quoted SSM value; green |
| 2026-09-22 | Exercise-grading debugging (WSL2): Docker-socket permission fix applied & verified; second bug (workspace missing non-editable files) prompt written — pending |

## 3. Environments & how to work in them

- **User's WSL2 (primary dev):** Windows host `DESKTOP-15NDNUT`, WSL2 distro `Ubuntu`, clone at `/home/rbalaji/scaler-education-journey` (a **separate clone** from the Windows-side checkout Claude's file tools saw — always `git pull`/`git push` to sync). Runs **rootless Podman** as the Docker backend (`DOCKER_HOST=unix:///run/user/1000/podman/podman.sock`, set in the login profile).
  - Claude (in earlier sessions) reached it via `wsl.exe -d Ubuntu -- bash -lc "…"` from Git Bash: **always a login shell** (`-lc`; else `docker` silently talks to an empty native Docker), prefix `MSYS_NO_PATHCONV=1` for paths like `/tmp/x`, prefer a real `.sh` file over long inline strings (variable expansion silently corrupted once — an `rm -rf $WORK` almost hit an empty/wrong path; **echo variables in their own step before anything destructive**).
  - `docker build -t x .` (no compose) doesn't persist the image with the `docker-container` buildx driver — **always `--load`**; `/tmp` doesn't reliably bind-mount into rootless containers — use a path under `/home/rbalaji`; rootless Podman can't `rm -rf` root-written files in bind mounts (needs `sudo`).
  - Podman/rootless fixes used 2026-09-20: `systemctl --user enable --now podman.socket`; unprivileged port 80 via `net.ipv4.ip_unprivileged_port_start=80`; stale `docker-proxy` after partial `up` → stop/remove old container; `EXERCISE_DOCKER_SOCKET_PATH=/run/user/1000/podman/podman.sock` + `EXERCISE_DOCKER_SOCKET_GID` in `.env`. `apt autoremove` would have removed podman/buildah/netavark — don't sweep blindly. Containers: `studytracker-api`, `studytracker-postgres`/`database`, `studytracker-app`, `neuralascent-ai-agent`; local DB user `studyuser`, db `studytracker` (check `.env`).
- **Earlier macOS host + Linux VM** (Aug 23): `sudo docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml …`; `sudo -E` is ignored; `VITE_API_KEY` is a build arg — rebuild after changing.
- **Claude Code cloud/other sessions** may have no `dotnet`, Docker or Maven; then backend claims are read-only unless the user runs builds.
- **Windows checkouts:** some `exercises/practice-pool` paths exceed Windows path limits — set `git config core.longpaths true`; avoid touching `practice-pool`.

## 4. Postgres / pgvector production migration (2026-09-13) — mistakes to not repeat
Image swap `postgres:16-alpine → pgvector/pgvector:pg16` (arm64 manifest verified with `docker manifest inspect`; the deploy script doesn't verify `POSTGRES_IMAGE` platform). `docker-compose.yml` and `deploy-single-ec2.sh` each define `POSTGRES_IMAGE` (`${POSTGRES_IMAGE:-pgvector/pgvector:pg16}` in the script — a mangled edit `${pgvector/pgvector:pg1}` once killed the script under `set -u`; run `bash -n scripts/deploy-single-ec2.sh` first). The script never recreates an existing DB container → manual `docker stop/rm studytracker-postgres`, then a single deploy with `ALLOW_CREATE_DATABASE=true` (flip back to `false` right after — it's a guard against silently creating an empty DB) which restores the latest S3 backup into the fresh container on the same volume. Mistakes: wrong DB name in manual `pg_dump` (`studytracker` vs `StudyTrackerDB`) → an invalid "backup"; **`docker exec -t` corrupts binary dumps**; `docker exec` can't see host files (use `docker run --rm -v ~/:/backups:ro pgvector/pgvector:pg16 pg_restore --list …`); verify every backup right away (valid: sane date, `dbname: StudyTrackerDB`, positive TOC count, real tables — 324 entries incl. `Tasks`, `app_users`, `chat_conversations`, `concept_prerequisites`). Valid backup: `StudyTrackerDB_backup_20260913_131226.dump` (get it off the host); delete the corrupt `neuralascent_backup_20260913_071003/071038.dump` and `StudyTrackerDB_backup_20260913_130244.dump`. `CREATE EXTENSION vector` was run manually, later captured in `ai-agent/migrations/001` (but not wired into deploy — `07-…` §5.3). SSH `Connection timed out` afterwards unresolved (suspect SG source IP / changed EC2 IP).

## 5. Diagnostics cheat-sheet
- Which container/db am I on? `docker ps -a`; env inside: `docker inspect <c> --format '{{json .Config.Env}}'` (a `restart` reuses baked env; recreate to pick up compose changes).
- Compose var precedence: shell env > `.env` > default (`docker compose … config | grep <VAR>` reveals the winner).
- A 503/error with **no** log line is a red flag for swallowed exceptions (the exercise runner hid a permission error until logging was added).
- A "done" claim is a lead: rebuild, `--force-recreate`, hit the live endpoint (exercise check: real `POST /api/exercises/{id}/run` of a reference solution must return `passed:true`).
- Stale local image: `docker run` doesn't re-pull an existing tag — `docker pull` and pin the digest.
- Fresh-volume dev DB: run `api --migrate` first (`scripts/local-stack.sh` does).
- `api/obj/*` tracked artifacts cause noisy diffs (`git rm -r --cached api/obj api/bin` recommended, never done).
- `.github/workflows/*` edits have always been hand-edited by the user (the local LLM declines to touch them), reviewed by Claude before commit.

## 6. Open ops items
1. Finish exercise-grading bug #2 verification on WSL2, then repeat deploy+verification on EC2 (user's stated order), then AI Tutor work.
2. Decide runbook naming: `runbooks/production-deployment-runbook.md` uses `studytracker-db`/`studytracker`; prod uses `studytracker-postgres`/`StudyTrackerDB` and no Compose (the runbook also says Ubuntu 22.04 while the EC2 host is Amazon Linux 2023).
3. Bootstrap guard `[ ! -f /etc/studytracker/api.env ]` — refresh always? (SSM additions never reach the box otherwise.)
4. Multi-platform image release and digest evidence beyond arm64-only; RDS/ECS/CloudFront stages untouched.
5. SSM `/neuralascent/prod/api-env` will need a DeepInfra key entry when the embedding pipeline starts (never quote values).
6. Confirm SSH access path (SG source IP) after the pgvector session.
7. Copy the valid Sept-13 backup off the EC2 host; delete the corrupt dumps.
