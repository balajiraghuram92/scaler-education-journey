# Learner State: Data Contract for the AI Tutor

Added on 2026-10-21 with session management and per-user progress. These are the facts an AI tutor can use to know what you studied, where you stopped, and where you are weak. Everything is keyed by `app_users.id`, which is the `nameid` claim in the `na_auth` JWT that `ai-agent/auth.py` already validates.

## Tables (PostgreSQL, readable directly by `ai-agent`)

| Table | One row per | Key columns |
|---|---|---|
| `user_lesson_progress` | (user, lesson) | `status` (`InProgress`/`Completed`), `first_opened_at`, `last_opened_at`, `completed_at`, `last_section_id` (heading anchor such as `concepts-covered`), `scroll_percent`, `visit_count`, `time_spent_seconds` |
| `user_problem_progress` | (user, coding assignment) | `status` (`NotStarted`/`Attempted`/`Solved`), `solution_revealed_at`, `solved_at` |
| `mcq_presentations` + `mcq_attempts` | each time a question is shown or answered | `mcq_presentations.user_id`, `question_id`, `displayed_option_order`; `mcq_attempts.selected_option_key`, `is_correct`, `answered_at`. Retries create new presentations; the **latest** attempt per question is the learner's current answer. |
| `mcq_questions` / `mcq_options` | question / option | `category` (`Checkpoint`/`Assignment`/`Additional`), `source_type`, `explanation`, `legacy_key`; `mcq_options.is_correct` |
| `learning_activity` | event | `user_id`, `event_type` (`LessonOpened`, `LessonCompleted`, `LessonReopened`, `McqAnswered`, `ProblemAttempted`, `ProblemCompleted`, `ProblemReopened`, `SolutionRevealed`, …), `lesson_id`, `problem_id`, `occurred_at`, `metadata` (jsonb; for `McqAnswered` it holds `questionId`, `legacyKey`, `category`, `selectedOptionKey`, `isCorrect`) |
| `lesson_notes` | note | `user_id` (null = editorial), `note_type = 'PersonalNote'`, `content_body` |
| `user_sessions` | signed-in device | session lifecycle only. The tutor should not need it. |

Lessons resolve through `lessons → modules → courses`. The full slug is `course.slug/module.slug/lesson.slug`, and the reader URL is `/chapter/{fullSlug}`.

## HTTP endpoints (same cookie; all scoped to the caller)

- `GET /api/me/summary`: totals and per-course progress, MCQ accuracy, and assignments solved.
- `GET /api/me/resume`: last lesson opened (with section and scroll position) and the next unfinished lesson.
- `GET /api/me/mcq-performance?course=python-engineering`: per-lesson accuracy, weakest first.
- `GET /api/me/activity?limit=50&before=<iso>`: the event log, newest first.
- `GET /api/me/lessons/progress`: every lesson-progress row.

## Useful queries

```sql
-- Weakest lessons by latest-attempt accuracy (one user)
WITH latest AS (
  SELECT DISTINCT ON (p.question_id) p.question_id, a.is_correct
  FROM mcq_attempts a JOIN mcq_presentations p ON p.id = a.presentation_id
  WHERE p.user_id = :user_id
  ORDER BY p.question_id, a.answered_at DESC)
SELECT l.slug, l.title, count(*) AS answered, round(100.0 * avg(latest.is_correct::int)) AS accuracy
FROM latest JOIN mcq_questions q ON q.id = latest.question_id JOIN lessons l ON l.id = q.lesson_id
GROUP BY l.slug, l.title ORDER BY accuracy, answered DESC;

-- Questions currently answered wrong, with the explanation to tutor from
SELECT q.legacy_key, q.question_text, q.explanation
FROM mcq_questions q JOIN LATERAL (
  SELECT a.is_correct FROM mcq_attempts a JOIN mcq_presentations p ON p.id = a.presentation_id
  WHERE p.user_id = :user_id AND p.question_id = q.id ORDER BY a.answered_at DESC LIMIT 1) last ON NOT last.is_correct;
```

## Session notes for `ai-agent`

- `na_auth` is now a **30-minute** access token, with a custom claim `na_sid` for the session id. The SPA refreshes it through `POST /api/auth/refresh` (cookie `na_refresh`, path `/api/auth`) about every 20 minutes while a tab is open, so the ai-agent sees a valid cookie on every call. It doesn't need to change.
- Revoking a session cuts off `/api` calls within about 30 s. The ai-agent validates signatures only, so a revoked token stays valid there until it expires (at most 30 min). To make revocation immediate in the ai-agent too, check `user_sessions.revoked_at IS NULL AND expires_at > now()` for the `na_sid` claim.
