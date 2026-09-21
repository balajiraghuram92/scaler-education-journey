# STRICT PROMPT — Fix ContentStatus semantics, author lessons 21/22/23, add H3 hierarchy

Read this entire document before touching any file. This is a mechanical + editorial
transformation task on ONE file: `api/Data/JavaVerticalSeedData.cs`. Do not touch any other
file. Do not paraphrase, shorten, or "improve" any existing sentence you are not explicitly
asked to change — only insert new `###` headings, and for Part B only, write new lesson
content in the same voice/density as the existing lessons.

## Why this is happening

This codebase seeds a Java/Spring learning platform's lessons into Postgres from this one
seed file, consumed later by a RAG ingestion pipeline that chunks `lessons.content_body` on
markdown heading boundaries (H2 → H3 → H4). Three separate defects were found by reading the
file end to end:

1. **21 of ~24 real lessons have zero `###` subheadings** — each `## Concepts Covered` /
   `## Practical Backend Scenario` section is one dense multi-concept paragraph blob (500–800
   words). A heading-based chunker can only split on `##`, so each chunk ends up covering
   3–4 unrelated concepts at once, which will badly hurt retrieval precision once this
   content is embedded.
2. **`ContentStatus` does not reliably mark which lessons have real content.** Lessons
   `01-intro-to-lld`, `02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation`, and
   `24-machine-coding-hotel-management` set `ContentBody` directly from
   `GetAuthoredLessonContent(slug)` at creation, so they keep the C# default
   `ContentStatus = "Published"`. Every other lesson that HAS a case in
   `GetAuthoredLessonContent`'s switch (04, 05, 06–13, 14-solid-principles,
   15-creational-patterns, 16-structural-patterns, 17-behavioural-patterns-uml,
   18-how-to-approach-design, 19-machine-coding-tictactoe, 20-machine-coding-parking-lot,
   and the Module 6 lessons 14-spring-boot-core, 15-spring-data-jpa, 16-spring-rest-api,
   17-machine-coding-capstone) only gets that real content swapped in later, at runtime, by
   `BackfillLessonContent` (around line 1076), which deliberately sets
   `ContentStatus = "Draft"` when it does so — **this Draft marking is intentional editorial
   semantics (auto-backfilled content pending human review), not a bug — do not change
   `BackfillLessonContent`'s behavior.**
3. **Three lessons have no real content at all and never will, because they have no case in
   `GetAuthoredLessonContent`'s switch:** `21-machine-coding-bookmyshow`,
   `22-machine-coding-splitwise`, `23-machine-coding-contest`. Each is currently a single-line
   stub (e.g. `"# Lesson 22 — Machine Coding: Splitwise\n## Key Topics\n- User and group
   management\n..."`), and because `GetAuthoredLessonContent` returns `null` for these slugs,
   `BackfillLessonContent` skips them (`if (authoredContent == null ...) continue;`) forever.
   They are stuck at the C# default `ContentStatus = "Published"` with garbage content.

## Constraints — read before editing

- Only edit `api/Data/JavaVerticalSeedData.cs`. No other file changes.
- Do not modify `BackfillLessonContent`, `NeedsLessonContent`, or `EnsureExpandedModules` —
  their Draft/Outline logic is intentional and out of scope.
- Do not modify the `Chapter(...)`-generated lessons (`databases-sql`, `high-level-design`,
  `data-engineering` modules, defined via `GetExpandedModules()`) — those are already
  well-structured (short, focused sections) and are out of scope for this task.
- Preserve every existing sentence's substance in Part A (H3 restructuring) — you are
  inserting heading lines at natural concept boundaries, not rewriting prose. Minor
  connective-word edits immediately around a new heading (e.g. removing a "Additionally,"
  that only made sense as a mid-paragraph transition) are acceptable; wholesale rewriting
  is not.
- Match the existing code style exactly: verbatim C# string literals (`@"..."`), the same
  em-dash (`—`) and smart-quote conventions already used in the file, doubled `""` for
  literal quotes inside verbatim strings, same section order
  (`## Concepts Covered` → `## Practical Backend Scenario` → `## Practice Loop` →
  `## Evidence of Understanding` → `## Suggested Extension`), same `---\n\nReference: ...`
  footer style where a lesson already has one (lesson 3 has this; most don't — don't add it
  where it doesn't already exist).
- Word count tier for Part B (new lessons 21/22/23): these are "Advanced mechanism" lessons
  (full machine-coding labs) — target 1200–1500 words total, matching the density of
  `05-oop-4-lms-lab` or `24-machine-coding-hotel-management` (read those two in full as your
  density/voice reference before writing 21/22/23).

---

## Part A — H3 restructuring (all 21 flat lessons)

### The rule

For each `GetAuthoredLessonContent` switch case listed below, look at its `## Concepts
Covered` section (and `## Practical Backend Scenario` only if it visibly bundles more than
one distinct scenario — most don't and should be left alone). There are two source shapes;
apply the matching transformation:

**Shape 1 — the paragraph already has informal bold-line sub-labels** (e.g. lesson
`06-concurrency-1-threads` has `**The Office / Company Metaphor:**`, `**Diagnostic
Questions — Concurrency vs. Parallelism:**`, `**Five Real-World Anchors...:**`, `**From Code
to Process in Memory:**`, `**Threads — Lightweight Execution Units:**`, `**Context Switching
& Scheduling Overhead:**`, `**Standard Operating Procedure (SOP) for Multithreading in
Java:**`). Promote each such bold-line label into its own `### ` heading directly above the
paragraph it introduces, and strip the bold markers and trailing colon from the label text
since it's now a real heading, e.g.:

```
BEFORE:
**The Office / Company Metaphor:**
A running system is analogous to an office environment:
- **Company = Process:** ...

AFTER:
### The Office / Company Metaphor
A running system is analogous to an office environment:
- **Company = Process:** ...
```

Do this for every bold-line label in that section — nothing else in the paragraph changes.
Lessons with this shape (confirmed while reading): `06-concurrency-1-threads`,
`07-concurrency-2-executors` (has "The Too-Many-Threads Problem" and likely more bold labels
further in — read the full case before editing). Check every other case below for this same
pattern before assuming it needs Shape 2 — several of the concurrency/advanced-Java lessons
likely already have partial bold-label structure since 06 and 07 do.

**Shape 2 — flowing paragraphs with no existing sub-labels** (e.g. `01-intro-to-lld`,
`02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation`, `04-oop-3-polymorphism-
interfaces`, `05-oop-4-lms-lab` mostly already has bold numbered items like "**1. Abstraction
& System Blueprinting:**" — treat those the same as Shape 1). For genuinely undifferentiated
paragraphs, read the paragraph, identify where the topic shifts to a distinct concept, and
insert a new `### <Concept Name>` heading at that sentence boundary — splitting the
paragraph into two at that point. Choose a heading name that names the concept precisely
(e.g. not "More on Access Modifiers" but "The Four Access Modifier Tiers"). Aim for 2–4
`###` subsections per `## Concepts Covered` section — do not over-fragment down to one
sentence per heading.

Example for `03-oop-2-access-modifiers-encapsulation`'s `## Concepts Covered` (currently two
giant paragraphs — the first covers access modifiers AND final AND the immutability pattern
AND constructor chaining; the second covers copy semantics AND inheritance AND equals/
hashCode). Split into headings such as: `### Access Modifiers and the final Keyword`,
`### The Immutability Pattern and Constructor Chaining`, `### Shallow vs. Deep Copy
Semantics`, `### Inheritance and the equals/hashCode Contract` — four headings, each getting
the sentences that already discuss that concept, in their existing order, with sentence
boundaries as the only split points (no rewriting).

### Cases to restructure (all in `GetAuthoredLessonContent`'s switch)

Apply Part A to every one of these case labels — read each one's current full text in the
file first, then decide Shape 1 vs Shape 2 per section as described above:

- `"04-oop-3-polymorphism-interfaces"`
- `"05-oop-4-lms-lab"` (mostly Shape 1 already — verify and promote its existing
  `**1. ... :**`–`**8. ... :**` numbered bold labels to `###` headings, dropping the leading
  number since heading order already conveys sequence, e.g. `**1. Abstraction & System
  Blueprinting:**` → `### Abstraction and System Blueprinting`)
- `"06-concurrency-1-threads"` (Shape 1, see worked example above)
- `"07-concurrency-2-executors"` (Shape 1 — read full case, promote all bold labels)
- `"08-concurrency-3-synchronization"`
- `"09-concurrency-4-semaphores"`
- `"10-java-adv-1-generics"`
- `"11-java-adv-2-collections-lab"`
- `"12-java-adv-3-lambdas-streams"`
- `"13-java-adv-4-streams-exceptions"`
- `"14-solid-principles"`
- `"15-creational-patterns"`
- `"16-structural-patterns"`
- `"17-behavioural-patterns-uml"`
- `"18-how-to-approach-design"`
- `"19-machine-coding-tictactoe"`
- `"20-machine-coding-parking-lot"`
- `"14-spring-boot-core"`
- `"15-spring-data-jpa"`
- `"16-spring-rest-api"`
- `"17-machine-coding-capstone"`

(`01-intro-to-lld`, `02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation`, and
`24-machine-coding-hotel-management` were read in full during investigation and are included
in this list implicitly EXCEPT 01/02 are Shape 2 and already covered by the general rule —
apply Part A to `01-intro-to-lld`, `02-oop-1-intro-lab`, and
`03-oop-2-access-modifiers-encapsulation` too, using the worked example given above for 03.
`24-machine-coding-hotel-management` already has reasonable internal structure — read it
first; only add headings if its `## Concepts Covered` truly bundles unrelated concepts.)

---

## Part B — author real content for lessons 21, 22, 23

`GetAuthoredLessonContent`'s switch currently ends with:

```csharp
            _ => null
        };
    }
```

Add three new cases immediately before `_ => null`, matching the exact style of
`24-machine-coding-hotel-management`'s case (read that case in full as your template — same
`@"..."` verbatim string, same section headings, same closing `",` syntax). Each new lesson
must use `###` subheadings within `## Concepts Covered` from the start (apply Part A's rule
during writing, not as a follow-up pass) since these are new content, not restructured
content.

- `"21-machine-coding-bookmyshow"` — a seat-booking system machine-coding lab. Use the
  existing lesson metadata as your content brief (already in the file, `SeedModule5Lessons`,
  slug `21-machine-coding-bookmyshow`): event/show/venue modelling, seat locking under
  concurrency, booking confirmation flow, payment state management. `## Concepts Covered`
  should include at minimum `### Seat Locking and Concurrent Booking`, `### Event, Show, and
  Venue Modelling`, `### Booking and Payment State Machine`. `## Practical Backend Scenario`,
  `## Practice Loop`, `## Evidence of Understanding`, `## Suggested Extension` follow the same
  shape as `24-machine-coding-hotel-management`.
- `"22-machine-coding-splitwise"` — an expense-splitting system lab, per its existing
  metadata: expense categories, split strategies (equal/exact/percentage), debt
  simplification, balance sheet computation. `## Concepts Covered` should include at minimum
  `### Split Strategy as a Polymorphic Abstraction`, `### Balance Computation and Debt
  Simplification`, `### Group and Expense Modelling`.
- `"23-machine-coding-contest"` — a timed machine-coding assessment lesson, per its existing
  metadata: applying SOLID and design patterns to a new, unseen problem under interview
  conditions, code review and self-assessment. This one is a process/assessment lesson
  rather than a single system design — structure `## Concepts Covered` around
  `### What a Timed Machine Coding Round Actually Evaluates`, `### A Repeatable Approach
  Under Time Pressure`, `### Common Failure Modes and How to Self-Review`.

After writing each, update its `ContentBody` assignment in `SeedModule5Lessons` (currently at
approximately lines 674–702, but re-locate by searching for
`Slug = "21-machine-coding-bookmyshow"` etc. since line numbers will have shifted after Part
A's edits) from the current inline stub literal to:

```csharp
ContentBody = GetAuthoredLessonContent("21-machine-coding-bookmyshow") ?? string.Empty
```

(and the equivalent for 22 and 23) — this is the exact same pattern already used for
`01-intro-to-lld`, `02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation`, and
`24-machine-coding-hotel-management` (see e.g. line 297). Do not add or change
`ContentStatus` on these three `Lesson` object initializers — leave it unset, so it keeps the
C# model default of `"Published"` (the same mechanism 01/02/03/24 already rely on), which is
correct now that real content backs it.

---

## Output expectations

Produce the complete, modified `api/Data/JavaVerticalSeedData.cs` file (or a unified diff
against it, your choice — state which you're providing). Do not touch any other file in the
repo. After the change, every lesson slug listed in Part A should have at least one `###`
heading inside `## Concepts Covered`, and `GetAuthoredLessonContent` should have exactly 25
non-null cases (22 existing + the 3 new ones from Part B).

## Verification checklist (self-check before returning the result)

1. `grep -c '^### ' api/Data/JavaVerticalSeedData.cs` should increase from 1 (only
   `structured-concurrency` is in a different file — actually 0 in this file before your
   edit) to at least 21 lines matching `^### ` (one per restructured/new lesson at minimum;
   most will have 3-4).
2. `grep -c '"_ => null"'` — unchanged, still exactly one `_ => null` default arm.
3. No lesson's `## Concepts Covered` word count changed by more than ~15% from before your
   edit (Part A must not silently expand or shrink existing prose — only Part B's three new
   lessons are net-new words).
4. Confirm `BackfillLessonContent`, `NeedsLessonContent`, and `EnsureExpandedModules` are
   byte-for-byte unchanged from before your edit.
