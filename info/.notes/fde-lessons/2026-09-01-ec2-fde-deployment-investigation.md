# FDE Vertical — EC2 Deployment Investigation & Fix

**Date:** 2026-09-01
**Trigger:** After completing the full FDE curriculum content (Phase 1–27, 152 authored lessons), needed to verify the AWS/EC2 production deployment pipeline actually picks up seed-data changes, and confirm the live site reflected the authored content.

---

## TL;DR

The live site (`https://98.130.44.145/`, `neuralascent.top`) was serving **generic placeholder lesson content** for the entire FDE curriculum, not the authored Phase 1–27 text, even though every deploy since Phase 1 had "succeeded." Root cause: a write-once seeding guard in `FdeCurriculumSeedData.cs` permanently protects any lesson row that already has non-empty `content_body` — and every FDE lesson row had already been created with generic placeholder text back in late August, before any authoring existed. Fixed by manually blanking the affected rows and re-running the seeder on EC2. Verified twice: once via a targeted fill-in-the-blanks reseed, and again via a full delete-and-recreate of the `fde-curriculum` course to prove the from-scratch path also works.

---

## How the deploy pipeline actually works

- `.github/workflows/deploy-api.yml` triggers on push to `main`, **only if the commit message contains `[deploy]`** (or via manual `workflow_dispatch`). Plain pushes without that tag are silently skipped — this caused EC2 to lag behind local `main` for most of the FDE authoring phases.
- On trigger: builds `api`, `app`, and `runner` images, pushes to GHCR (`ghcr.io/balajiraghuram92/...`), then dispatches `scripts/deploy-single-ec2.sh` to the EC2 instance via SSM `send-command`.
- **Migrations and seeding are NOT automatic on API container startup.** `Program.cs`'s `app.Run()` never calls `MigrateAsync`/`DbSeeder.Initialize` — they only run via explicit CLI flags (`--migrate`, `--seed-reference-data`), which `deploy-single-ec2.sh` invokes as one-off `docker run --rm ... <image> --migrate` / `--seed-reference-data` containers *before* starting the long-lived API container (lines ~416–427 of the script).
- The DB container (`studytracker-postgres`) is **persistent** across deploys — reused via the `scaler_postgres_data` volume, not recreated. `RESTORE_LATEST_BACKUP` only fires `if database_is_empty` (a genuinely fresh host); on a normal redeploy it just takes a fresh `pg_dump` backup to S3 first, then reuses the existing DB.

## Root cause of stale FDE content

`api/Data/FdeCurriculumSeedData.cs` seeds lessons with this pattern (`Seed()` method, ~line 300 and ~line 394):

```csharp
var content = GetAuthoredFdeLessonContent(lessonSlug) ?? BuildLessonContent(task.Title, guide);
...
if (string.IsNullOrWhiteSpace(lesson.ContentBody)) lesson.ContentBody = content;
```

- `GetAuthoredFdeLessonContent(slug)` (the dictionary of real authored Phase 1–27 content) was only added recently — before that, every lesson row got the generic `BuildLessonContent`/`BuildSupplementalLessonContent` placeholder template.
- The lesson-creation loop has existed since the file was first added (Aug 24), and multiple successful deploys ran before any authored content existed. So by the time Phase 1–27 content was written, **every FDE lesson row on EC2 already had non-empty `content_body`** (the placeholder text).
- The write-once guard (`if IsNullOrWhiteSpace(...) ...`) means a normal redeploy — even with correct authored content compiled into the new image — will never touch an already-populated row. This matches the documented "write-once seeding gotcha" in the root `CLAUDE.md`, just discovered to apply to the *entire* FDE curriculum, not a single lesson.

## Diagnostic detours (documented so we don't repeat them)

1. **Wrong database name.** `docker-compose.yml`'s fallback is `POSTGRES_DB:-studytracker` (lowercase), but the actual EC2 `api.env` sets `POSTGRES_DB=StudyTrackerDB` (mixed-case). Postgres db names are case-sensitive — early queries against `-d studytracker` hit a near-empty decoy database (2 migrations, 17 lessons total) and looked like a catastrophic migration failure. The real DB (`StudyTrackerDB`) had all 9 migrations applied and 298 lessons.
2. **Stale local Docker image cache.** An ad-hoc `docker run ...:latest --migrate` reused a locally-cached image from Aug 24 instead of pulling fresh (`docker run` doesn't auto-pull an existing tag). Re-ran with `docker pull` first, then pinned the exact digest for all subsequent debug commands.

## Fix applied

**1. Targeted reseed** (fill only the placeholder rows):
```sql
UPDATE lessons l
SET content_body = '', content_status = 'Outline'
FROM course_modules m, courses c
WHERE l.module_id = m.id AND m.course_id = c.id AND c.slug = 'fde-curriculum'
  AND l.content_body NOT LIKE '%## Practical Backend Scenario%';
```
then:
```bash
sudo docker run --rm --network scaler-network \
  --add-host host.docker.internal:host-gateway \
  --env-file /etc/studytracker/api.env \
  ghcr.io/balajiraghuram92/scaler-education-journey-api@sha256:c62025e0a336a30ef9c6844fcce4b7a1af9f269ca9dfe7eb3a36a8b62bc4ae88 --seed-reference-data
```
Result: **152/152 lessons authored, 0 placeholder.**

**2. Full disaster-recovery style verification** (delete the whole `fde-curriculum` course, confirm the seeder recreates it correctly from scratch):
```sql
-- Backup first (pg_dump -F c), then:
DELETE FROM courses WHERE slug = 'fde-curriculum';  -- cascades to course_modules, lessons, lesson_resources, problems, course_domain_links
```
Re-ran the same `--seed-reference-data` command. Result: identical — **152/152 authored, 0 placeholder.**

Verification method used both times: fingerprint check on `content_body LIKE '%## Practical Backend Scenario%'` — this heading only appears in authored content (the generic placeholder uses `## Worked scenario` instead), giving an exact, DB-side pass/fail with no need to scrape the live rendered site.

## FK safety notes (for next time this needs doing)

Confirmed via the migration files (`api/Migrations/*.cs`) before deleting anything:
- `courses` → `course_modules` → `lessons` → `lesson_resources`/`problems`/`course_domain_links`: all `ON DELETE CASCADE`.
- Cross-links to `lessons` from knowledge-atlas / reading-map / curriculum-bridge tables: mostly `SET NULL`.
- The one `RESTRICT` FK (`study_task_content_links.lesson_id`) had 0 rows at the time — didn't block the delete. **Check this table's row count again before repeating a full course delete in the future** — if it's ever populated, `courses` deletion will fail until those rows are cleared or remapped.
- **Never delete the `Verticals`/`Tasks` rows for `FDE Curriculum` / `FDE Self-Study`** — those are the seeder's source outline; if they're gone, `FdeCurriculumSeedData.Seed()` returns early and nothing gets recreated.

## Structural takeaway

This isn't a one-off bug — it's how the seeder is designed to behave. **Any future edit to an already-seeded lesson's content will silently no-op on redeploy** unless that row's `content_body` is blanked first (same manual SQL step used here). Worth remembering whenever *revising* (not just adding) FDE lesson content going forward.
