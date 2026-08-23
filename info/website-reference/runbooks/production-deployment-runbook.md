# Neuralascent Production Deployment & Rollback Runbook

**Document Version:** 1.0.0  
**Target Environment:** AWS EC2 Production (Ubuntu 22.04 LTS, Docker Compose, PostgreSQL 16)  
**Applicability:** Phase 6 Cutover and Operational Maintenance  

---

## 1. Pre-Deployment Verification Checklist

Before executing any deployment actions on the remote host, verify the following prerequisites:

- [ ] Current git worktree is clean and tagged with the release commit SHA.
- [ ] Docker images are built with immutable tags (e.g. `studytracker-api:sha-<COMMIT_SHA>`).
- [ ] Database backup target directory on the host has at least 10 GB free disk space.
- [ ] Healthcheck status of running containers is green (`docker compose ps`).

---

## 2. Production Database Backup & Isolated Restore Rehearsal

Execute these commands to take a consistent snapshot and verify restore integrity:

```bash
# 1. Capture snapshot with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec studytracker-db pg_dump -U studyuser -d studytracker -F c -b -v -f /tmp/backup_${TIMESTAMP}.dump

# 2. Copy snapshot outside container to host backup storage
docker cp studytracker-db:/tmp/backup_${TIMESTAMP}.dump ./backups/prod_backup_${TIMESTAMP}.dump

# 3. Verify dump size and readability
ls -lh ./backups/prod_backup_${TIMESTAMP}.dump
```

---

## 3. One-Shot Database Schema Migration & Reconciliation

Execute migrations and deterministic reconciliation backfill:

```bash
# 1. Run additive schema migrations
docker compose run --rm api dotnet StudyTracker.Api.dll --migrate

# 2. Verify migration exit code ($? == 0)
echo "Migration exit code: $?"

# 3. Run reconciliation dry-run
docker compose run --rm api dotnet StudyTracker.Api.dll --reconcile-content --scope all --dry-run

# 4. Apply reconciliation backfill
docker compose run --rm api dotnet StudyTracker.Api.dll --reconcile-content --scope all --apply
```

---

## 4. Blue-Green / Zero-Downtime Container Deployment

```bash
# 1. Pull / Launch updated API and App services
docker compose up -d --no-deps --build api app

# 2. Verify liveness and readiness health probes
curl -f http://localhost:5000/health/live
curl -f http://localhost:5000/health/ready
```

---

## 5. Instant Binary Rollback Procedure

Because all database schema changes are strictly **additive** (no dropped tables, columns, or renamed keys), rollback requires only swapping back the previous container images:

```bash
# 1. Revert container images to previous known-good commit
export PREVIOUS_IMAGE_TAG="sha-previous-good"
docker compose up -d --no-deps api app

# 2. Verify legacy endpoint compatibility
curl -f http://localhost:5000/api/verticals
curl -f http://localhost:5000/api/courses
curl -f http://localhost:5000/health/ready
```
