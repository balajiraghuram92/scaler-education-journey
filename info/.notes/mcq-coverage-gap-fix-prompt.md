# STRICT PROMPT — Author practiceQuestions for the 12 lessons with zero MCQ coverage

Read this entire document before touching any file. This is a content-authoring task on ONE
file: `app/src/data/lessonInteractions.js`. Do not touch any other file — in particular, do
not touch `api/Data/JavaVerticalSeedData.cs` (read-only reference for you, see below).

## Why this is happening

This codebase has exactly one live MCQ mechanism for the Java/Spring course:
`app/src/data/lessonInteractions.js`, a hand-authored JS object keyed by
`"{courseSlug}/{moduleSlug}/{lessonSlug}"`, each entry holding a `practiceQuestions` array
(and, for lessons 1–4 only, an additional `conceptChecks` array — do not add `conceptChecks`
to any of the 12 lessons below, only `practiceQuestions`, matching the pattern every other
lesson from 05 onward already uses). This is consumed by
`app/src/components/learning/PracticeQuestions.jsx` for the interactive quiz widget.

Checked every `java-spring-lld/...` key currently in the file: 16 lessons have real
`practiceQuestions` (01–14 except 15, plus 16, 17). **12 lessons have zero MCQ coverage at
all** — no object key exists for them in the file yet:

- `15-creational-patterns` (module `design-principles-patterns`)
- `18-how-to-approach-design`, `19-machine-coding-tictactoe`,
  `20-machine-coding-parking-lot`, `24-machine-coding-hotel-management` (module
  `applied-machine-coding`)
- `21-machine-coding-bookmyshow`, `22-machine-coding-splitwise`, `23-machine-coding-contest`
  (module `applied-machine-coding` — these three just got real lesson content authored this
  session, see below)
- `14-spring-boot-core`, `15-spring-data-jpa`, `16-spring-rest-api`,
  `17-machine-coding-capstone` (module `spring-enterprise-architecture`)

This gap predates this session — nobody has ever written MCQs for the machine-coding labs or
the Spring module. The task: add a `practiceQuestions` array for each of these 12 keys.

## Source of truth for question content — read before writing

For each lesson, its actual current prose (already restructured with `###` subheadings this
session) lives in `api/Data/JavaVerticalSeedData.cs`, inside the `GetAuthoredLessonContent`
switch, under the matching slug string (e.g. search for `"15-creational-patterns" =>`). **Read
each lesson's full current case in that file before writing its questions** — do not invent
content from the lesson title alone. Write at least one question per `###` subheading in that
lesson's `## Concepts Covered` section (most lessons have 3–5 subheadings after this session's
restructuring), so question coverage maps to the lesson's actual concept breakdown.

## Constraints — read before writing

- Only edit `app/src/data/lessonInteractions.js`. Treat `JavaVerticalSeedData.cs` as read-only
  research material.
- Do not touch any existing lesson entry (01–14, 16, 17) — only add the 12 new keys.
- 6–8 questions per lesson (minimum 5). Exactly 4 options per question (`a`/`b`/`c`/`d`,
  labels `A`/`B`/`C`/`D`), exactly one `correctOptionId`.
- Tag every new question with a leading comment `// SOURCE_TYPE: LLM_GENERATED` (per this
  project's own convention in `CLAUDE.md` — no source markdown exists for these lessons, so
  none of these can be tagged `FROM_MATERIAL`).
- Match the existing code style exactly: single-quoted strings, trailing commas omitted the
  same way the existing entries omit them, same indentation (2 spaces per nesting level, see
  the worked example below), same object key order (`id`, `question`, `options`,
  `correctOptionId`, `explanation`).
- `id` naming: `lesson-{n}-{short-topic-tag}-mcq-{nn}` (zero-padded two digits), where
  `{short-topic-tag}` disambiguates lesson numbers that repeat across modules — this project
  already does this for 14/16/17 (see `lesson-14-solid-mcq-01`, `lesson-16-structural-mcq-01`,
  `lesson-17-behavioural-mcq-01` already in the file). Use these exact tags so there is no id
  collision with existing or sibling entries:
  - `15-creational-patterns` → `lesson-15-creational-mcq-NN`
  - `18-how-to-approach-design` → `lesson-18-approach-mcq-NN`
  - `19-machine-coding-tictactoe` → `lesson-19-tictactoe-mcq-NN`
  - `20-machine-coding-parking-lot` → `lesson-20-parking-mcq-NN`
  - `21-machine-coding-bookmyshow` → `lesson-21-bookmyshow-mcq-NN`
  - `22-machine-coding-splitwise` → `lesson-22-splitwise-mcq-NN`
  - `23-machine-coding-contest` → `lesson-23-contest-mcq-NN`
  - `24-machine-coding-hotel-management` → `lesson-24-hotel-mcq-NN`
  - `14-spring-boot-core` → `lesson-14-springboot-mcq-NN`
  - `15-spring-data-jpa` → `lesson-15-springdata-mcq-NN`
  - `16-spring-rest-api` → `lesson-16-springrest-mcq-NN`
  - `17-machine-coding-capstone` → `lesson-17-capstone-mcq-NN`
- Insert all 12 new entries immediately before the closing `};` of the `lessonInteractions`
  object (currently followed by the `getLessonInteractions` function and the default export —
  do not reorder or touch those).

## Question-quality bar — this is the "enterprise-oriented" requirement

This site's own stated audience is developers with 7–8+ years of experience (see
`CLAUDE.md`'s "CONTENT QUALITY STANDARD" section) — these are not junior trivia questions.
Look at `lesson-14-solid-mcq-*` and the existing `21`/`22`/`23` lesson prose you'll read as
source material, and write to that same bar:

1. **Scenario-anchored, not definition-recall.** Do not write "What does SRP stand for?" —
   write questions that describe a concrete situation (a specific class doing two things, a
   specific race condition, a specific API design choice) and ask what principle/pattern/fix
   applies and why. Every existing `lesson-21/22/23` prose scenario (BookMyShow seat locking,
   Splitwise debt simplification, the 90-minute interview playbook) already gives you real
   scenario material to adapt into questions — use it.
2. **Plausible distractors, not obviously-wrong filler.** Wrong options should be the mistake
   a competent-but-rushed engineer would actually make (e.g. picking a pattern that's
   *related* but solves a different problem, or a design that works for the happy path but
   breaks under concurrency) — not absurd options nobody would pick.
3. **Explanations teach the distinction, not just restate the correct answer.** State *why*
   the correct option is right AND *why the most tempting wrong option is wrong* — this is
   what makes a question useful for someone who guessed right for the wrong reason.
4. For the four machine-coding lessons with existing exercises on disk
   (`19-machine-coding-tictactoe` → `exercises/java/java-lld/applied-machine-coding/`,
   `24-machine-coding-hotel-management`), you may write one or two questions that probe the
   same design decisions the exercise's `evidence[]` array tests (read the relevant
   `exercise.json` if useful), but do not duplicate an evidence claim verbatim as a question
   stem — that's testing exercise completion, not conceptual understanding.

## Worked example (format reference — copy this shape exactly)

```javascript
  'java-spring-lld/design-principles-patterns/15-creational-patterns': {
    practiceQuestions: [
      // SOURCE_TYPE: LLM_GENERATED
      {
        id: 'lesson-15-creational-mcq-01',
        question:
          'A payments service has a single ConfigManager class responsible for loading environment variables at startup. Two different modules each call `new ConfigManager()` independently, and a bug surfaces where one module\'s config changes are invisible to the other. Which creational pattern directly addresses this, and why?',
        options: [
          { id: 'a', label: 'A', text: 'Factory — because ConfigManager creation logic should be centralized behind a factory method' },
          { id: 'b', label: 'B', text: 'Singleton — because the bug is caused by two independent instances holding separate state; a Singleton guarantees exactly one shared instance' },
          { id: 'c', label: 'C', text: 'Builder — because ConfigManager has many optional fields that should be set fluently' },
          { id: 'd', label: 'D', text: 'Prototype — because cloning an existing ConfigManager avoids repeated environment variable parsing' }
        ],
        correctOptionId: 'b',
        explanation:
          'The bug is a state-divergence bug: two separate objects each hold their own copy of config state. Singleton is the pattern that specifically eliminates multiple independent instances by guaranteeing exactly one, shared everywhere. Factory (A) addresses how an object is constructed, not how many exist; Builder (C) and Prototype (D) solve unrelated construction problems (optional-field assembly and cheap copying) and would not fix the divergence.'
      }
    ]
  },
```

## Output expectations

Produce the complete, modified `app/src/data/lessonInteractions.js` file (or a unified diff,
your choice — state which). After the change, `grep -c "practiceQuestions:"` should increase
by exactly 12, and `grep -c "SOURCE_TYPE: LLM_GENERATED"` should increase by the total new
question count (72–96, since 12 lessons × 6–8 questions each).

## Verification checklist (self-check before returning the result)

1. All 12 new object keys use the exact `courseSlug/moduleSlug/lessonSlug` strings listed
   above — verify each against `api/Data/JavaVerticalSeedData.cs`'s actual module/lesson
   wiring (`SeedModule4Lessons`, `SeedModule5Lessons`, `SeedModule6Lessons`), not assumed.
2. No `id` string is reused across any two questions in the whole file (existing 16 lessons
   included) — grep for each new id prefix and confirm each appears exactly once.
3. Every question has exactly 4 options with ids `a`,`b`,`c`,`d` and a `correctOptionId` that
   matches one of them.
4. No existing lesson entry (01–14, 16, 17) changed at all — diff should show pure additions.
5. The file still ends with the unchanged `getLessonInteractions` function and default export.
