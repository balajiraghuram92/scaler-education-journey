# AI Engineering migration (balajiraghuram92.github.io → neuralascent.top/chapters)

Done on 2026-11-01. Every lesson page from the old site is now a native Neuralascent course,
seeded into Postgres like the Python course, so the tutor's embedding and reranker stages see it
in the same tables (`lessons.content_body`, `lesson_diagrams`, `mcq_questions`).

## What moved where

| Old site | New course (`api/Data/Content/…`) | Modules |
|---|---|---|
| `index.html`, `AI-Infusion/`, `help/`, `Learnings/Class-*` | `ai-infusion/` | Start Here, Lesson 1, 2, 3–4, 5, 6, 7, 8, 9–10 |
| `AWS-Bootcamp/**` | `aws-agentic-ai-bootcamp/` | Overview, Week 1 Part 00 + Lessons 1–6 + Projects 1–2, Week 2 Project 1 |

- 27 pages became **81 chapters** (long pages are split on their own section boundaries,
  roughly 1,800–4,200 words each), **206 diagrams** and **195 MCQs**.
- Both courses sit under one new vertical, **AI Engineering**.
- Project zips are served from `app/public/downloads/ai-engineering/` (all 10 public zips from
  the old repo; the Class 1–6 zips were in the repo but not linked from the old site, and are
  linked from each lesson's resources box now).

## How content maps to the reader

| Old page element | Native form |
|---|---|
| Prose, lists, tables, callouts | Markdown in `lessons/<slug>.md` |
| Pseudo code → **View code** toggle | ` ```pseudo title="…" ` block, then ` ```python reveal title="…" ` (collapsed, with Copy) |
| Inline SVG diagrams | `diagrams/<slug>.json`, placed inline with `{{diagram:N}}`; page CSS is inlined into each SVG |
| "Check your understanding" quizzes | `mcqs/<slug>.json` → native Checkpoint MCQs (attempts tracked) |
| Glossary pop-ups (`data-k` buttons) | A **Glossary** section at the end of the lesson |
| Step-through diagrams, tabs, simulators | Their text written out in order as lists under the diagram |

## Coverage

`coverage.txt` is the final check: every text run from each original page (HTML text nodes and
script string literals) searched in the assembled content. All pages are 96.9–100%. What is not
present is, by inspection of every remaining run:

- widget control labels (`Start the race`, `Next step →`, `Reset to case study`, `Save as PDF` …),
- JavaScript source fragments picked up by the string scan (regexes, DOM code),
- live widget output that depends on slider/input values; the agents wrote out the default state.

Things worth a human read before publishing (agent notes):

- Some script-only self-check quizzes (10 questions each in several bootcamp lessons) are now
  written out as Markdown with answers, not as MCQs.
- A few inserts carry short labels the agents added (`Step 3 ·`, `Answer:`), and a few dynamic
  numbers are shown as placeholders (`n / 6`, `<ratio>`).
- Class 9: three bench status lines use `…` for live numbers.

## Re-running

The pipeline lives in `tools/` (Node 20+, `npm install` in that folder):

1. `node convert.mjs <siteRoot> <page.html> <key> out/<key>.json` per page (HTML → sections, diagrams, MCQs).
2. Agent supplements (`supplements/<key>.json`, brief in `tools/AGENT_BRIEF.md`) add script-held text verbatim at exact anchors.
3. `node assemble.mjs <api/Data/Content>` groups sections into chapters using `structure.json`,
   renumbers diagrams, places MCQs by where each quiz sat, resolves links between pages.
4. `final-check.sh` (edit the `S=` path) re-runs the coverage check.

Seeding is file-canonical (`ContentCurriculumSeedData`): changed lesson files replace the stored
body and set the lesson back to `Draft`; diagrams and MCQs update in place.
