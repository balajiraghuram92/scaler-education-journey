# Next-session prompt: Python vertical migration

Copy everything below the line into a new chat session.

---

I'm continuing work on the **Python vertical** of Neuralascent (repo `balajiraghuram92/scaler-education-journey`). Read `CLAUDE.md` first and follow it exactly. In short: you may only write inside `info/`, `exercises/`, and the two MCQ JSON files (`api/Data/mcq-migration-data.json` and `scripts/mcq-migration-data.json`, which must stay identical). For everything else, you produce copy-paste-ready prompts for my Local LLM. If anything is unclear, ask me; do not assume.

## What is already done (PR #7, branch `claude/gifted-thompson-knjgj9`)

All source material is in `info/Python-vertical/`:

- `Structure-lessons/Foundations of Object-Oriented Design & Scalable Systems.png`: the course structure image.
- `Lessons/Module-{1,2,3}/Tests/`: question screenshots (`msedge_*.png`) and solution zips. Each zip is a project with a README, code and tests.
- `Lessons/Module-{1,2,3}/Mcqs/`: MCQ screenshots (352 in total).
- `Lessons/Module-{1,2,3}/Tests-solutions.md`: each coding question listed under its lesson (from the screenshot header), with the zip that is its answer. These were verified against OCR and the zip contents.
  - In Module 3, five questions have two zips. The newer `1788…` zip is the answer; the older `1773…` zip is a partial earlier version.
  - Two Module 2 zips (`Singleton_Log-solution` and `Builder_Message-solution`) are Java/Maven projects, not Python.
- `Lessons/Module-{1,2,3}/Mcqs-by-lesson.md`: 351 unique MCQs (128 / 167 / 56).
  - They are grouped by lesson, then by the page's **Assignment** and **Additional Problems** sections.
  - Options are lettered a, b, c, d.
- `Lessons/mcqs-structured.json`: the same 351 MCQs as JSON, with the fields `module`, `lesson`, `section`, `qnum`, `title`, `question`, `options[{optionKey, optionText}]`, `correctOptionKey` (null for all), `note` and `screenshots`. Use this file as the data source rather than re-reading the screenshots.

## What is still left (confirm scope with me before starting)

1. **Define what "the Python migration" covers.** Ask me which of the following I want:
   - a new Python course/vertical in the app, like the existing `java-spring-lld` course;
   - its lessons;
   - its MCQs;
   - its exercises.

   Then propose a plan before making any change.
2. **Course, module and lesson slugs.** None exist yet for Python.
   - Read the structure image, `api/Data/JavaVerticalSeedData.cs`, `api/Data/ChapterSeedData.cs`, `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md` and `info/local-llm-content-pipeline/` to see how the Java vertical is modelled.
   - Propose a lesson/slug map for the Python lessons named in the screenshot headers.
   - The Module 3 "Machine Coding" lessons (TicTacToe, Parking Lot, BookMyShow, Splitwise) may already overlap with Java lessons. Check before duplicating.
3. **Correct answers for the MCQs.** The screenshots show no answers, so `correctOptionKey` is null for every question.
   - `api/Data/mcq-migration-data.json` requires `isCorrect` on each option, plus `explanation` and `sourceType`.
   - Ask me whether I will supply the answer keys, or whether you should propose answers for my review. If you propose them, mark them `LLM_GENERATED` and list every one for me to check.
   - Only after that, add the questions to both MCQ JSON files, with a new unique `legacyKey` for each.
4. **Exercises from the solution zips.**
   - `exercises/` currently holds only Java (`exercises/java/java-lld`). Look at its manifest/pom/stub/test/solution layout.
   - Ask me how Python exercises should be structured before creating any.
   - Wiring an exercise to a lesson (`app/src/data/lessonExerciseAssociations.js`) is my job, not yours.
5. **Lesson content.** Lesson `.md` content and seed data go through the Local LLM pipeline, so produce prompts for that, not direct edits.
6. **One unverified MCQ.** Module 3, *Machine Coding - 13: Code Splitwise 1*, Assignment Q2 ("Command Matching Loop Output", `msedge_gh55xclSkX.png`): its code block reaches the bottom of the screenshot. Ask me to confirm that nothing follows `ex.execute("delete g1")`.

## Tips from the previous session

- **OCR:** `tesseract-ocr` is not preinstalled. Run `apt-get install -y tesseract-ocr`.
- **Image read limit:** reading many images in one session runs into "media removed: request limit". Use OCR and the existing JSON where you can, and read images only to check specific items.
- **Hidden underscores:** the source pages render `_x_` as italics, which hides underscores in identifiers. Watch for this in any text you take from the screenshots.
