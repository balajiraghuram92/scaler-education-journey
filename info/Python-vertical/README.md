# Python Vertical: How It Works and How to Change It

Course slug `python-engineering`: 7 modules and 56 lessons, with 169 coding assignments and 812 MCQs.

## Where things live

| What | File(s) | Notes |
|---|---|---|
| Structure (modules, lessons, titles, minutes, difficulty) | `api/Data/Content/python/course.json` | Canonical. Reorder or rename here. |
| Lesson bodies | `api/Data/Content/python/lessons/<slug>.md` | Canonical. The seeder replaces the stored body when the file changes and sets the lesson back to `Draft`. |
| Coding assignments | `api/Data/Content/python/assignments/<slug>.json` | Stored as `problems` rows (`language = 'python'`). The reference solution is hidden behind a dropdown in the reader. |
| MCQs | `api/Data/mcq-migration-data.json` and `scripts/mcq-migration-data.json` | Keep the two files identical. For `python-engineering`, the seeder **re-syncs existing rows** (text, explanation, category, `isCorrect`), so answer-key fixes reach the DB. |
| MCQ drafts per lesson | `info/Python-vertical/build/mcq-output/<slug>.json` | Source of the merge into the two files above. |
| Answer keys to review | `info/Python-vertical/ANSWER-KEY-REVIEW.md` | Every proposed answer for your reference MCQs. 21 are flagged **⚠ REVIEW**. |
| Authoring rules used | `info/Python-vertical/build/AUTHORING-SPEC.md` | The section headings the reader depends on are listed there. |
| Learner state for the AI tutor | `info/.notes/learner-state-for-ai-tutor.md` | Tables, endpoints and example SQL. |

Seeder: `api/Data/PythonCurriculumSeedData.cs`, which runs inside `--seed-reference-data` before the MCQ seeder.

## Reader layout (why the headings matter)

- **Checkpoint** MCQs render right after `## Concepts Covered`.
- **Assignment** and **Additional** MCQs and the coding assignments render inside `## Practice Loop`.
- Supported markdown: `#`/`##`/`###`, lists, fenced code with a language, tables, `> **Label:**` callouts, inline bold, code and links.

## Verification done before shipping

- Every assignment that ships tests (105 of 169) passes under **real pytest** on Python 3.13 in a clean container with FastAPI, Pydantic v2, SQLAlchemy 2, httpx and NumPy. The other 64 are your original course exercises, which have no tests, plus 2 design exercises and 1 SQL schema exercise.
- The content agents ran code-trace MCQs and stated outputs through the interpreter. Exceptions they reported, worth a skim: SQLAlchemy/asyncpg snippets in py-23 and py-26–py-28, the Django solutions in py-25, mypy/pyright behaviour in py-48, and the 3.14 and free-threaded notes in py-35.
- Exact duplicate reference questions (the course reused 10 Adapter/Facade questions on the Decorator/Flyweight page) were merged once, under py-15.

## Common edits

- **Fix an answer key:** in both MCQ JSON files, flip the `isCorrect` flags and update the `explanation`, then run the seeder.
- **Edit a lesson:** change its `.md`, run the seeder, review the lesson, and publish it again (`content_status = 'Published'`).
- **Add a lesson:** add it to `course.json` and create `lessons/<slug>.md`. Optionally add `assignments/<slug>.json` and an MCQ group with the new `legacyKey`s.
