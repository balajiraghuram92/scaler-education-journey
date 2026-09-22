# URGENT FIX PROMPT — JavaVerticalSeedData.cs does not compile at all right now

Read this entire document before touching anything. **This is a production-breaking bug in the
current state of the repository.** `dotnet publish` fails with hundreds of cascading syntax
errors starting at line 2222. The API cannot build or run until this is fixed. This takes
priority over any other pending work on this file.

## Root cause, confirmed

The lesson-content restructure done in an earlier pass rewrote the `## Concepts Covered`
sections for lessons `18-how-to-approach-design`, `19-machine-coding-tictactoe`,
`20-machine-coding-parking-lot`, `21-machine-coding-bookmyshow`, and
`22-machine-coding-splitwise` inside `GetAuthoredLessonContent`'s C# **verbatim string literals**
(`@"..."`). In a C# verbatim string, every literal `"` character must be written as `""`
(doubled) to avoid prematurely terminating the string. The new content contains many
un-doubled, single `"` characters — both in markdown emphasis-quotes (e.g. `the "Resist First
Reaction" Discipline`) and inside embedded Java code snippets (e.g.
`new RuntimeException("User not found")`, `mappedBy = "region"`, `input.split(" ")`). Each one
of these terminates the C# string right there, and everything after it gets parsed as raw,
invalid C# — which is why the compiler output shows total chaos for over 800 lines.

**Confirmed bug locations found by direct inspection (not exhaustive — treat this as a starting
list, not the complete list):**
- Line 2222 (lesson 18): `### The Three Interview Formats and the "Resist First Reaction" Discipline`
- Line 2532 (lesson 20): `**"How likely is this set of values to change...`
- Line 2562 (lesson 20): `throw new ParkingFullException("No available spot for this vehicle type");`
- Line 2575 (lesson 20): text referencing quoted terms near "two genuinely distinct `Gate` instances"
- Line 2745 (lesson 21): `**"Same Set for Every Owner" Test**`
- Line 2758, 2763 (lesson 21): `@OneToMany(mappedBy = "region")`, `@JoinColumn(name = "region_id")`
- Lines 2811, 2813, 2821 (lesson 21): multiple `new RuntimeException("...")` calls
- Lines 3002, 3003, 3028 (lesson 22): `input.split(" ")`, `equalsIgnoreCase("SettleUp")`,
  `System.out.println("Unknown command: " + input)`

Lesson 19 (`2363`–`2497`) was scanned and appears clean — no embedded quotes found — but
re-verify it anyway as part of the full pass below.

## Task

1. Read the full text of each of the five case bodies (`18-how-to-approach-design` through
   `22-machine-coding-splitwise`, lines approximately 2216–3082) in
   `api/Data/JavaVerticalSeedData.cs`.
2. For each verbatim string, walk every character and double every literal `"` that is not
   already part of a doubled `""` pair — **except**:
   - The opening `@"` immediately after `=>` (this must stay a single `"`, it's the string's
     start delimiter).
   - The final closing `"` immediately before the trailing `,` at the end of each case's content
     (this must stay a single `"`, it's the string's end delimiter).
3. Do this for markdown emphasis-quotes (`"Resist First Reaction"` → `""Resist First
   Reaction""`) and every embedded Java/code string literal (`"User not found"` →
   `""User not found""`, `"region"` → `""region""`, `" "` → `"" ""`, etc.) — every single
   instance, not just the ones listed above.
4. Do a second, independent pass over the same five blocks looking specifically for any other
   character that has special meaning inside a C# verbatim string and could cause a similar
   problem (there shouldn't be any others, since verbatim strings only treat `"` specially, but
   confirm no stray unescaped `"` was missed by re-running the scan described in the
   verification section below).

## Critical constraint — actually compile it this time

The previous pass that introduced this bug was never verified against a real build, and it
shipped completely broken. Do not repeat that failure:

1. Actually run `dotnet build` or `dotnet publish api/StudyTracker.Api.csproj -c Release -o
   /tmp/verify-build /p:UseAppHost=false` (or the equivalent for your environment) after making
   the fix.
2. Confirm **zero** compiler errors, not just "fewer" errors. Paste the real command output.
3. If you cannot run `dotnet build` in your environment, say so explicitly and clearly, and
   instead provide a definitive, mechanical proof that every `"` in the five blocks is correctly
   paired (e.g., a script that walks each block character-by-character and reports any
   non-doubled `"` that isn't the opening/closing delimiter — do not just eyeball it, given how
   many instances were missed the first time).

## Constraints

- Do not change the actual textual content, meaning, or facts of any lesson — this is purely an
  escaping fix. The words, code examples, and structure must be identical; only the quote
  characters change from `"` to `""` where needed.
- Do not touch any other lesson's content, and do not touch `app/src/data/lessonInteractions.js`
  or any other file.
- Do not re-introduce the `23-machine-coding-contest` case or any other previously-removed
  content.

## Output expectations

Report: the real build output showing zero errors (or an explicit statement that you could not
run a build, plus the mechanical verification script's output instead), and a count of how many
`"` → `""` fixes were made per lesson.

## Verification checklist (self-check before returning the result)

1. `dotnet build`/`dotnet publish` succeeds with zero errors — the actual command output is
   included, not a summary claim.
2. Every one of the confirmed bug locations listed above now shows doubled `""` around the
   quoted text.
3. A full character-level scan of all five case bodies finds no remaining single, non-doubled
   `"` other than each block's opening and closing delimiter.
4. `git diff` on this file shows only quote-doubling changes (character-level `"` → `""`
   substitutions) — no wording, structure, or heading changes.
5. Lessons 18, 19, 20, 21, 22 still each open `## Concepts Covered` and flow into an unchanged
   `## Practical Backend Scenario` afterward, exactly as before this fix.
