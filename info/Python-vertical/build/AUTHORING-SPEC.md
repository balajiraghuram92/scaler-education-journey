# Python Vertical — Authoring Spec (for content agents)

Repo root: `C:\Users\balaj\Documents\GitHub\Raghuram-git\scaler-education-journey` (Windows; Git Bash available).

## Who this is for

The learner already writes Python, C# and C++ and is preparing for **AI Engineer and Forward Deployed Engineer (FDE) interviews**. Their Python needs to read like a **12+ year senior engineer's**. They built a localization FastAPI backend and chatbots, so don't explain basics like what a list is. Teach the mechanism, the trade-off, the production failure mode, and how an interviewer probes it. Target Python **3.12/3.13**. Call out version-specific behaviour (e.g. "3.11+", "free-threaded 3.13t"). Library baselines: FastAPI 0.11x, Pydantic v2, SQLAlchemy 2.0, pytest 8, httpx. **Never invent APIs.** If unsure an API exists, leave it out.

## Hard rules

1. **Write only the output files listed in your task.** Don't edit any other file, and don't run git.
2. **Never create a `.py` file anywhere.** Don't write helper scripts in Python. For processing, use `node -e`, shell, or the Read/Grep tools. To check what a code snippet prints, you may pipe it to the interpreter over stdin without creating a file: `python -I - <<'EOF' ... EOF`. Do this for every code-trace MCQ and every code example whose output you state.
3. Read solution zips **without extracting them**: list with `unzip -l <zip>`, print a file with `unzip -p <zip> <path/inside>`.
4. Your outputs must be valid UTF-8. Check every JSON file with `node -e "JSON.parse(require('fs').readFileSync('<path>','utf8'))"` before you finish.
5. Source material is reference only. Write original teaching prose, and don't paste the notes verbatim. The MCQ question and option text from `mcq-input` is the exception: keep it verbatim.
6. Watch the hidden-underscore problem. The source pages rendered `_x_` as italics, so identifiers such as `__init__`, `_build_dummy_expense` and `settle_up_user` may have lost underscores. Restore the correct Python identifier.

## Output 1 — Lesson markdown: `api/Data/Content/python/lessons/<lesson-slug>.md`

The site renders a limited Markdown subset. Use only these:
- `# Title` (first line, exactly once), `## Section`, `### Subsection`
- paragraphs, `- ` bullet lists, `1. ` numbered lists (no nesting)
- fenced code with a language: ```` ```python ````, ```` ```bash ````, ```` ```text ````, ```` ```sql ````, ```` ```toml ````
- tables: `| a | b |` with a `|---|---|` separator row
- callouts: lines starting with `> `. Begin with a bold label, e.g. `> **Interview tip:** ...`, `> **Pitfall:** ...`, `> **Production note:** ...`
- inline `**bold**`, `` `code` ``, and links `[text](https://...)`
No HTML, no images, no nested lists, no footnotes.

**Required section order.** The `##` headings must be spelled exactly like this, because the app attaches quizzes to two of them:

```
# <Lesson title from course.json>

<Hook paragraph: why this matters in production and in an interview. 2–4 sentences.>

## Concepts Covered
### <subtopic> ...      (the core teaching: mechanisms + runnable code examples)

## Practical Backend Scenario
<A realistic AI/FDE/backend situation where this concept decides the outcome.>

## Practice Loop
<Numbered steps the learner performs at their keyboard.>

## Evidence of Understanding
<What the learner can now explain or demonstrate, written as checkable statements.>

## Interview Questions to Rehearse
<4–6 questions an interviewer would ask, each followed by a concise senior-level model answer. Use "### Q: ..." subheadings followed by the answer paragraph.>

## Common Pitfalls
<Bullet list of real mistakes and how to spot them.>

## Suggested Extension
<One stretch task.>
```

The app inserts **Checkpoint MCQs right after "Concepts Covered"**. It puts the **Assignment and Additional MCQs and the coding assignments inside "Practice Loop"**.

**Length:** about **1,300–2,000 words of prose** for Advanced lessons and **900–1,300** for Intermediate or Foundational ones. Code blocks don't count toward this. Include **at least 4 substantial code examples** per lesson, each correct, idiomatic, typed where it helps, and with its output shown when relevant. Prefer real backend and AI domains: ride-hailing, payments, LLM gateways, document pipelines, ticketing. Avoid toy `Animal/Dog` examples.

## Output 2 — MCQs: `info/Python-vertical/build/mcq-output/<lesson-slug>.json`

```json
{
  "lessonSlug": "py-05-processes-threads-gil",
  "questions": [
    {
      "legacyKey": "python-engineering/py-05/assignment/q03",
      "category": "Assignment",
      "sourceType": "FROM_MATERIAL",
      "questionText": "Markdown. Code goes in ```python fences.",
      "explanation": "Markdown. See rules below.",
      "reviewFlag": null,
      "options": [
        { "optionKey": "a", "optionText": "...", "isCorrect": false },
        { "optionKey": "b", "optionText": "...", "isCorrect": true },
        { "optionKey": "c", "optionText": "...", "isCorrect": false },
        { "optionKey": "d", "optionText": "...", "isCorrect": false }
      ]
    }
  ]
}
```

- **Reference MCQs** come from `info/Python-vertical/build/mcq-input/<lesson-slug>.json`, if that file exists. Include **every** one. Keep `legacyKey`, `category`, question text and option text (fix only the underscore and OCR damage described above). Set `sourceType: "FROM_MATERIAL"`. The source has **no answer key**, so you decide the answer. Mark **exactly one** option `isCorrect: true`. Verify code-trace questions by actually running them (rule 2). If a question is ambiguous, has more than one defensible answer, or none, still pick the best one, and set `reviewFlag` to a one-sentence reason.
- **New MCQs** that you write: `sourceType: "LLM_GENERATED"`.
  - For a lesson **with** reference MCQs, add **3** `"Checkpoint"` questions.
  - For a lesson **without** reference MCQs, add **4** `"Checkpoint"` and **8** `"Assignment"` questions.
  - Use keys `python-engineering/<py-NN>/checkpoint/g01`, `.../g02` … and `python-engineering/<py-NN>/assignment/g01` … (`<py-NN>` is the first two slug parts, e.g. `py-05`).
  - Write them at senior level: code-trace, "what breaks in production", design trade-off, or interview-trap questions. No trivia, no "which keyword defines a function". Always 4 options, keys `a`–`d`, and vary which letter is correct.
- **Explanation** (shown in a dropdown after answering), 90–220 words:
  - Start with `**Answer: (x)**` and one sentence on why.
  - Add one short line per wrong option explaining why it is wrong.
  - End with a `**Deeper:**` sentence connecting it to production or interview reasoning.
  - Put code in fences if needed.

## Output 3 — Coding assignments: `api/Data/Content/python/assignments/<lesson-slug>.json`

```json
{
  "lessonSlug": "py-05-processes-threads-gil",
  "assignments": [
    {
      "slug": "py-05-adder-thread",
      "title": "Multi-threaded Adder",
      "difficulty": "Warm-up",
      "source": "FROM_MATERIAL",
      "sourceZip": "Module-1/Tests/1773391917_5c8abab669d1955b.zip",
      "problemStatement": "Markdown: the task, as a precise spec.",
      "requirements": "Markdown bullet list: classes, signatures, behaviour, constraints, edge cases.",
      "workedExample": "Markdown: example input/output or usage, in fences.",
      "hints": "Markdown: 2–4 progressive hints, without giving the solution.",
      "referenceSolution": "Markdown: short approach paragraph, then the solution code in ```python fences (one fence per file, preceded by **`path/file.py`**), then the test command.",
      "runCommand": "pytest -q"
    }
  ]
}
```

- `difficulty` is one of `Warm-up`, `Core`, `Stretch`.
- **Reference lessons:** each module has a `Tests-solutions.md` that lists questions under their lesson, together with the zip holding the answer. Create **one assignment per listed question** for your lessons. Take the problem from that entry and the zip README, and look at the question screenshot in `Tests/` only when the text is unclear. `referenceSolution` must contain the solution code **copied from the zip** (read it with `unzip -p`), not rewritten. Leave out boilerplate such as `__pycache__`, `.idea`, empty `__init__.py`, and pom files.
  - Two Module 2 zips are Java/Maven projects. Make those assignments Python anyway: write the Python spec, and in `referenceSolution` give a short approach plus a note that the original reference was Java. Mark them `LLM_GENERATED`.
  - In Module 3, prefer the newer `1788…` zip where two exist.
  - Also add **1** `LLM_GENERATED` assignment per lesson that pushes past the reference to senior level, for example concurrency safety, tests, or typing.
- **Lessons without reference tests:** write **2** `LLM_GENERATED` assignments: one `Core` and one `Stretch`. Their reference solutions must be correct, typed and idiomatic, and include pytest tests. Check them by running the code over stdin (rule 2).
- If a lesson genuinely has no sensible coding exercise (for example UML), write one design exercise. Its "solution" is a written model answer, possibly in ```` ```text ```` diagrams.

## Before you finish

- Re-read each lesson file top to bottom and check that the section headings match the spec exactly.
- Validate every JSON file (rule 4).
- Your final message should be a short report: the files written; the MCQ count per lesson (reference / new); the assignment count per lesson; and every `reviewFlag` you set, as a list. Don't paste file contents.
