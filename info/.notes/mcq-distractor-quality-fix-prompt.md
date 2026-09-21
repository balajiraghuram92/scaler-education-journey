# STRICT PROMPT — Replace implausible distractors in the 12 newly-added MCQ lessons

Read this entire document before touching any file. This is a targeted content-quality fix on
ONE file: `app/src/data/lessonInteractions.js`. Do not touch any other file.

## Context

In the previous pass, you added `practiceQuestions` arrays for 12 lessons that previously had
zero MCQ coverage:

- `java-spring-lld/design-principles-patterns/15-creational-patterns`
- `java-spring-lld/applied-machine-coding/18-how-to-approach-design`
- `java-spring-lld/applied-machine-coding/19-machine-coding-tictactoe`
- `java-spring-lld/applied-machine-coding/20-machine-coding-parking-lot`
- `java-spring-lld/applied-machine-coding/21-machine-coding-bookmyshow`
- `java-spring-lld/applied-machine-coding/22-machine-coding-splitwise`
- `java-spring-lld/applied-machine-coding/23-machine-coding-contest`
- `java-spring-lld/applied-machine-coding/24-machine-coding-hotel-management`
- `java-spring-lld/spring-enterprise-architecture/14-spring-boot-core`
- `java-spring-lld/spring-enterprise-architecture/15-spring-data-jpa`
- `java-spring-lld/spring-enterprise-architecture/16-spring-rest-api`
- `java-spring-lld/spring-enterprise-architecture/17-machine-coding-capstone`

Each question's correct answer and explanation are solid — technically accurate,
scenario-anchored, senior-level. **The problem is the wrong options (distractors).** Most
questions pad 2 of their 3 wrong options with technical nonsense that no competent engineer
would ever consider plausible, e.g. (real examples pulled from the current file):

- "Java garbage collection cannot process collections containing more than two User objects."
- "Storing Split objects is mandatory for applying the Singleton pattern to user profiles."
- "User balances cannot be updated without converting expenses into XML documents."
- "The PostgreSQL JDBC driver has a bug that crashes if IDENTITY is used with transactions
  larger than 10 records."
- "GenerationType.IDENTITY stores IDs in an external cache instead of PostgreSQL, requiring an
  HTTP bridge."
- "Hibernate disables batching because IDENTITY forces table-level write locks across the
  entire cluster."
- "The reviewer is incorrect because Java's garbage collector writes mutated objects directly
  to the database socket before freeing memory."

These are "obviously wrong" filler — nobody with real experience would pick them, so the
question degrades into a free 50/50 (or better) guess instead of testing understanding. This
directly violates the original quality bar: *distractors must be the mistake a rushed-but-
competent senior engineer would actually make* — a design that's real but solves a different
problem, works for the happy path but breaks under load/concurrency, is a common
misconception, or confuses two similar-sounding mechanisms.

## Task

Audit **all 72 questions** across the 12 lesson keys listed above (6 questions each). For every
question, evaluate each of its 3 wrong options against this test: *"Would a developer with
7-8 years of experience, working quickly, plausibly believe this and pick it?"*

- If an option passes (it's a real but wrong technical claim, a related-but-different pattern,
  a partial/incomplete fix, or a common misconception) — **leave it untouched, verbatim.**
- If an option fails (invokes garbage collection doing something it doesn't do, made-up driver
  bugs, XML/HTTP bridges materializing from nowhere, sockets, caches, or any other fabricated
  mechanism unrelated to the real technical domain of the question) — **rewrite only that
  option's `text` field** with a plausible, domain-relevant wrong answer.

## Constraints — read before writing

- Only edit `app/src/data/lessonInteractions.js`, and only within the 12 lesson keys listed
  above. Do not touch any of the other existing lesson entries.
- Do NOT change: `id`, `question`, `correctOptionId`, `explanation`, or the correct option's
  `text`, for any question. Do NOT add, remove, or reorder questions or options.
- When you rewrite a distractor's `text`, its `explanation` already states why the *original*
  wrong answer was wrong — if the original explanation specifically named that fabricated
  option (e.g. "Options B, C, and D are absurd technical distractors" or "Option B is false"),
  update the explanation's reference to that option so it now correctly refutes the new,
  plausible distractor instead. Do not remove correct reasoning that already applies to
  distractors you leave unchanged.
- A rewritten distractor must be:
  1. Grammatically and stylistically consistent with the other options in that question
     (same sentence shape, similar length).
  2. Wrong for a reason a reader could actually learn from — not merely "less wrong" than the
     original nonsense, but a genuine, specific, plausible technical error.
  3. Clearly distinguishable from the correct answer once the explanation is read, but not
     trivially eliminable on a skim.
- Preserve exact code style: single-quoted strings, existing indentation, existing key order
  (`id`, `question`, `options`, `correctOptionId`, `explanation`).
- If, on review, a question's distractors are already all plausible, leave that question
  completely untouched — do not "improve" what already meets the bar.

## Output expectations

Produce the complete, modified `app/src/data/lessonInteractions.js` file (or a unified diff —
state which). Report how many distractor options you rewrote, broken down by lesson key.

## Verification checklist (self-check before returning the result)

1. All 12 lesson keys still have exactly 6 questions each, unchanged `id`s, unchanged
   `correctOptionId`s, unchanged `question` and `explanation` text (except where an explanation
   was updated solely to refer to a rewritten distractor, per the constraint above).
2. No option's `id` (`a`/`b`/`c`/`d`) or ordering changed.
3. Every rewritten distractor text no longer contains fabricated mechanisms (no garbage
   collector doing I/O, no invented driver bugs, no XML/HTTP/cache/socket claims unrelated to
   the question's real domain).
4. No lesson outside the 12 listed keys was touched — diff should show only line-level changes
   inside those 12 blocks, no additions/removals of question or lesson objects.
5. File still parses as valid JS (balanced braces/brackets) and still ends with the unchanged
   `getLessonInteractions` function and default export.
