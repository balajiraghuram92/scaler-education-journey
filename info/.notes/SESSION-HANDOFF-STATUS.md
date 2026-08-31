# Neuralascent Session Handoff — Read This First

**Purpose of this file**: if you're picking this up in a brand-new chat (possibly on a
different machine), read this entire file before doing anything else. It tells you exactly
what's done, what's verified, what's still sitting uncommitted, what's not started, and the
exact commands to run on WSL2 and on the production EC2 host to continue.

Last updated: 2026-08-31, mid-session. **Nothing described as "uncommitted" below has been
pushed or deployed yet** — that's the very first thing to do.

---

## 0. Orientation — read `CLAUDE.md` first

This repo has a hard rule: **Claude does not have write permission to most files.**
Permitted write paths are: `CLAUDE.md` itself, the memory directory, `info/.notes/`, and
`exercises/` (`.json`/`.xml`/`.java` only). Everything else (`.cs`, `.jsx`, `.js`, `.tsx`,
`.css`, `.html`) requires Claude to write a **prompt** into `info/.notes/` for the user's
local LLM to apply. Check `CLAUDE.md` in the repo root for the exact current wording before
assuming anything has changed.

---

## 1. What this whole engagement is

Neuralascent (`neuralascent.top`) is a personal editorial learning platform: React frontend
(`app/`), C# ASP.NET Core API (`api/`), PostgreSQL. The Java LLD course content pipeline is:
Scaler class material (PDFs/HackMD, already extracted into
`info/.notes/scaler-raw-notes/`) → Claude authors real content/MCQs/exercises grounded in
that material → either a local-LLM prompt (for restricted files) or direct edit (for
`exercises/`) → local verification → commit with `[deploy]` in the message → CI builds and
deploys → DB reseed picks up the new content.

**Critical gotcha, easy to forget**: the deploy workflow (`.github/workflows/deploy-api.yml`)
only runs its job if the commit message contains `[deploy]`, or if triggered manually via
`gh workflow run deploy-api.yml`. A plain push does nothing. This has already caused one
silent multi-commit gap once this session — check every commit message before assuming a
push shipped anything.

---

## 2. Current git state (as of this writing)

```
git log origin/main..HEAD --oneline:
  76f9bfe updated more exercises     <- strategy-stock-trading, strategy-pricing
  0e853fe updated tests              <- MCQ migration, Lesson 18/19/20 content,
                                         15 exercise dirs (adapter-translation through
                                         abstract-factory-document-processing)

Both commits are LOCAL ONLY — not yet pushed to origin/main, and NEITHER has [deploy]
in the message, so pushing them as-is will NOT trigger a production deploy.

Uncommitted working-tree changes: only this file (SESSION-HANDOFF-STATUS.md).
```

Run `git status --short`, `git log --oneline -6`, and
`git log origin/main..HEAD --oneline` immediately to confirm this hasn't changed since
this file was written. If the picture doesn't match, trust the live commands over this
snapshot.

**Nothing has been deployed since `1542598` (the Module 4 self-heal fix)** — that's still
the production HEAD. Everything since then (17 exercises, the MCQ migration, Lesson 18-20
content) is sitting in local commits, unpushed, undeployed.

### To ship all of it in one shot

```bash
git push origin main
# then, since neither local commit has [deploy], trigger manually:
gh workflow run deploy-api.yml
gh run watch
```

Or, cleaner for history: before pushing, amend/reword so the top commit carries `[deploy]`
(only safe if these commits haven't been pushed anywhere yet, which they haven't):
```bash
git commit --amend -m "[deploy] updated more exercises"
git push origin main
gh run watch
```

---

## 3. Verified and ready to ship — do this first

Both of the following were verified correct (counts matched spec exactly, no leftover text,
files balanced) before this file was written — see full detail in section 5 if you need to
re-verify from scratch (e.g. a new LLM claims to have redone something).

### 3a. MCQ migration (95 questions, `lessonInteractions.js`)
- Ported all flat "Self-Check" text blocks from 13 lessons into the interactive
  `practiceQuestions` UI format already used by Lessons 1–3.
- Counts confirmed exact: lessons 4/5/6/7/8/9/10/11/12/13 = 4/3/3/5/5/5/5/5/5/4;
  `14-solid` = 11; `16-structural` = 12; `17-behavioural` = 28. Total 95.
- Zero duplicate ids, code blocks correctly extracted into `codeBlock` fields, no leftover
  `"Self-Check (From Class Material)"` string anywhere in the `.cs` file.
- Source prompt: `info/.notes/migrate-mcqs-to-interactive-ui-prompt.md` (already applied).

### 3b. Lesson 18/19/20 content (`JavaVerticalSeedData.cs`)
- Real content added for `18-how-to-approach-design`, `19-machine-coding-tictactoe`,
  `20-machine-coding-parking-lot`, grounded in real Scaler source material (6-step design
  framework, TicTacToe's 3 undo approaches + O(N³)→O(1) win-check optimization, Parking
  Lot's 9-class design + the deliberately-unresolved concurrency gap).
- No `## Self-Check` sections added (correctly — no verbatim MCQ material exists for these
  topics, only conceptual summaries).
- Lessons 21/22/23 (BookMyShow/Splitwise/Contest) deliberately **not** touched — no source
  material exists for them yet (see section 6).
- Source prompt: `info/.notes/lesson-18-19-20-machine-coding-prompt.md` (already applied).

### Commands to ship both of the above

```bash
# from the repo root, in your primary working clone
git add -A
git commit -m "[deploy] Migrate MCQs to interactive UI; add Lessons 18-20 content; add 14 more exercises"
git push origin main
```

Then verify locally on **WSL2** before trusting production:

```bash
cd ~/raghu-website/scaler-education-journey   # or wherever your WSL2 clone lives
git pull origin main
chmod +x scripts/*.sh   # only needed if git checked out without exec bits again
bash scripts/local-stack.sh
```

`local-stack.sh` rebuilds the API/app images (picks up both `.cs` and `.js` changes) and
reseeds the DB (removes the old flat MCQ text from `ContentBody`, since that reseed step is
idempotent and additive — it will NOT touch the newly-empty Self-Check sections
retroactively removed, they're just gone from the source now, which is what we want).

**Verify in the browser** at `http://localhost`:
- Lessons 4–13, 14, 16, 17 should show the polished interactive "PRACTICE — N QUESTIONS"
  widget (radio buttons, reveal feedback) instead of flat text.
- Lessons 18, 19, 20 should show real content instead of the old bare "Key Topics" stub.

**Then trigger production deploy** (the commit above already has `[deploy]`, so a normal
push triggers it — but if you're re-running this from a squashed/rebased history without
that tag, use the manual trigger instead):

```bash
gh run watch   # or: gh workflow run deploy-api.yml && gh run watch
```

No manual DB cleanup needed for this particular deploy — unlike the earlier Module 4 bug,
this content change doesn't require the `cleanup-redundant-expanded-modules.sql` script.
That script is a **separate, already-resolved** issue — see section 7 if you need its
history, but it should already be applied to production from earlier in this session.

---

## 4. Exercise wiring — 17 of ~65 done

Exercises are wired directly into `exercises/java/java-lld/**/exercise.json` — **no local
LLM needed**, Claude writes these files directly (`exercises/` is a permitted write path).
No DB seeding needed either — the app auto-discovers `exercise.json` files from the
filesystem at API startup.

### Done and structurally verified (pom.xml + solution/starter/tests + exercise.json, all four present, learner/fixture split matches each exercise's actual test contract)

| Exercise dir | Lesson | Pattern |
|---|---|---|
| `design-patterns/adapter-translation` | 16 | Adapter (verified 5/5 tests passing via manual `mvn test`) |
| `design-patterns/adapter-insurance` | 16 | Adapter |
| `design-patterns/adapter-social-media` | 16 | Adapter |
| `design-patterns/facade-image` | 16 | Facade |
| `design-patterns/facade-data` | 16 | Facade |
| `design-patterns/facade-booking` | 16 | Facade |
| `design-patterns/flyweight-chess-user` | 16 | Flyweight |
| `design-patterns/flyweight-graphics` | 16 | Flyweight |
| `design-patterns/decorator-image` | 16 | Decorator |
| `design-patterns/decorator-api` | 16 | Decorator |
| `design-patterns/decorator-file-storage` | 16 | Decorator |
| `design-patterns/factory-document` | 15 | Simple Factory |
| `design-patterns/abstract-factory-notifications` | 15 | Abstract Factory |
| `design-patterns/abstract-factory-audio` | 15 | Abstract Factory |
| `design-patterns/abstract-factory-document-processing` | 15 | Abstract Factory |
| `design-patterns/strategy-stock-trading` | 17 | Strategy |
| `design-patterns/strategy-pricing` | 17 | Strategy |

**This completes 100% of Lesson 16, 100% of Lesson 15, and 2 of 6 Strategy/Observer
exercises for Lesson 17.** All 17 are committed locally (see section 2) but not yet pushed.

### In progress — stopped mid-read, not yet built

**`Strategy_Streami` (Strategy: video streaming quality adjustment)** — source and test
fully read (see below), but no files written yet for this one. Pick this up next.

- Location: `<scratchpad>/exercises-batch3/1773391194_f8a7d2a6fcf483d5/Strategy_Streami-solution/`
- No Reflections needed beyond what's already standard; test uses `org.reflections` +
  `@ExtendWith(MockitoExtension.class)` (no actual mocking calls, but the annotation still
  needs `mockito-core` + `mockito-junit-jupiter` on the classpath — same as
  `strategy-stock-trading`).
- **Lombok to strip**: `Video.java` has `@Getter @Setter` on all fields (`videoUrl`,
  `videoQuality`, `codec`, `bitrate`) plus an explicit 2-arg constructor
  `Video(String videoUrl, VideoQuality videoQuality)` — replace with plain getters/setters,
  keep the explicit constructor as-is.
- **Fixtures** (non-editable): `Video.java`, `VideoCodec.java` (enum: H264/H265/VP9),
  `VideoQuality.java` (enum: LOW/MEDIUM/HIGH), `QualityAdjustmentStrategy.java` (interface:
  `supportsType()`, `adjust(Video) -> Video`).
- **Learner-editable** (4 classes): `VideoStreamingManager` (private `Video` field + private
  `QualityAdjustmentStrategy` field, 2-arg constructor, `streamVideo()` delegates to
  `qualityAdjustmentStrategy.adjust(video)`), `LowVideoAdjustmentStrategy` (sets codec H264,
  bitrate 500), `MediumVideoAdjustmentStrategy` (sets codec H265, bitrate 1000),
  `HighVideoAdjustmentStrategy` (sets codec VP9, bitrate 2000).
- Target `lessonSlug`: `17-behavioural-patterns-uml`.
- Suggested exercise dir name: `strategy-video-streaming` (matches the existing
  `strategy-stock-trading`/`strategy-pricing` naming convention).

### Then continue with the 3 Observer exercises (not started)

- `<scratchpad>/exercises-batch3/1773391221_ba5246debdca20e7/Task_Observer-solution/`
- `<scratchpad>/exercises-batch3/1773391225_03c7a8319fd5c150/Weather_Observer-solution/`
- `<scratchpad>/exercises-batch3/1773391231_9f553c4f9e79cc93/Stock_Observer-solution/`

None of these three have been read yet this session — start fresh with the standard
11-step recipe below.

### Established pattern for wiring any remaining exercise (repeat this exactly)

1. Find the original zip's unzipped solution under
   `<scratchpad>/exercises-batch{1,2,3,4}/<zip-folder>/<Name>-solution/`. **Note**: the
   scratchpad is session-scoped temp storage — if it's gone in a new session, the durable
   source is the original zips in `C:\Users\balaj\Downloads\scaler-notes\Exercises\*.zip`
   (or wherever the user's Downloads folder is on the current machine) — re-unzip from
   there.
2. Read every `.java` file in `src/main` and the one test file in `src/test`.
3. Check for Lombok (`grep -l lombok`). **Decision already made this session: strip Lombok,
   replace with plain hand-written constructors/getters.** Do not add Lombok as a
   dependency — this was an explicit user decision (see section 6).
4. Check the test's imports for `org.reflections` and/or `org.mockito` — if present, add
   them as **test-scope only** dependencies in the exercise's `pom.xml` (see any existing
   `pom.xml` in the table above for the exact dependency block/versions to copy:
   `org.reflections:reflections:0.10.2`, `org.mockito:mockito-core:5.5.0`,
   `org.mockito:mockito-junit-jupiter:5.5.0` — only add what the test actually imports).
5. Read the test file line-by-line to determine the *exact* graded contract — which fields/
   methods/constructors are checked by reflection, and what values are asserted. Do not
   guess this from the class names alone; some contracts are subtle (e.g. the Facade
   exercises assert the facade class itself has **zero** raw dependency fields — the
   dependencies must be reached through an internal delegate class).
6. Build `pom.xml` at the exercise root (not inside `solution/`) — copy the minimal template
   from any existing exercise, changing only `artifactId` and the dependency list per step 4.
7. Build `solution/src/main/java/...` — the complete, correct implementation, matching the
   original exactly (once Lombok is stripped per step 3).
8. Build `starter/src/main/java/...` — copy every non-editable fixture file verbatim from
   `solution/`. For editable files, replace method **bodies** with `// TODO` comments
   describing what to do (keep signatures/fields intact) — do not blank the whole class,
   matching the established convention (see `oop-2/rider-entity` for the original precedent,
   or any exercise above for this session's precedent).
9. Build `tests/src/test/java/...` — the official test file, byte-identical to the original
   **except** any Lombok-only helper class inside the test itself (e.g. a `Pair<L,R>` test
   utility) gets the same Lombok-removal treatment as step 3.
10. Build `exercise.json` — copy the shape from any existing one. Fields: `id` (kebab-case,
    prefixed `java-lld-`), `lessonSlug` (must match a real lesson slug — see section 8 for
    the full slug list and topic-to-lesson mapping), `title`, `language: "java"`,
    `difficulty`, `estimatedMinutes`, `runtime` (always
    `{"profile":"java-maven","javaVersion":11,"timeoutSeconds":10}` — copy verbatim),
    `files[]` (one entry per file the learner sees; `editable:false` for fixtures,
    `editable:true` for the ones with TODOs), `testSuite` (`visible:false`, path, className),
    `evidence[]` (one entry per test method, `label` describing what it proves in plain
    English, `testMethod` matching the exact test method name).
11. No compile-check is possible from Claude's own shell (no Maven installed there). Ask the
    user to verify via the manual assembly recipe:
    ```bash
    cd exercises/java/java-lld/<category>/<exercise-name>
    tmp=$(mktemp -d)
    cp pom.xml "$tmp/"
    cp -r solution/src "$tmp/"
    mkdir -p "$tmp/src/test"
    cp -r tests/src/test/java "$tmp/src/test/"
    cd "$tmp"
    mvn test 2>&1 | grep -E "Tests run|BUILD"
    ```
    Expect `Tests run: N, Failures: 0, Errors: 0, Skipped: 0` matching the test file's
    method count. Repeat with `starter/src` instead of `solution/src` — expect failures
    (proves the starter doesn't accidentally already pass).

### Remaining exercise batches — not started

| Batch | Location | Contents | Target lesson(s) |
|---|---|---|---|
| batch3 | `<scratchpad>/exercises-batch3/` (6 files, 2 done) | Strategy ×3 (2 done: Stock Trading, Pricing; 1 remaining: Streaming — in progress, see above), Observer ×3 (not started) | 17 (`17-behavioural-patterns-uml`) |
| batch4 | `<scratchpad>/exercises-batch4/` (9 files) | TicTacToe Undo, TTT Winner Check, Boardgame, Database Factory, Integrate Cloud, Hotel ×4 stages | TicTacToe→19, Boardgame/DB Factory→15, Integrate Cloud→14, Hotel→24 |
| batch1 | `<scratchpad>/exercises-unzipped/` (36 files) | Threads, Point/Counter classes, Singleton, Prototype, Builder, Factory, Generics, Streams, collection sorting, etc. | Spans Lessons 1–13 by topic — read each template's problem statement to decide (user explicitly delegated this mapping decision to Claude) |

If the scratchpad is gone (new session, different machine), the durable source is the
original zips — see step 1 above. The exact zip→topic mapping was worked out by inspecting
each zip's file names and problem statements; there's no saved index file, so this requires
re-inspecting each zip briefly (grep for class names, read the one `.md` reference template
under `info/.notes/scaler-raw-notes/exercise-templates*/` if the exact same file still
exists, since those templates already recorded the topic/mapping decision).

---

## 5. Full verification battery (re-run this if anything is in doubt)

```bash
# Balance + duplicate-id checks on the two content files (adjust paths if repo moved)
node -e '
const fs = require("fs");
const cs = fs.readFileSync("api/Data/JavaVerticalSeedData.cs", "utf8");
const js = fs.readFileSync("app/src/data/lessonInteractions.js", "utf8");
function balance(s){ const o=(s.match(/\{/g)||[]).length,c=(s.match(/\}/g)||[]).length,po=(s.match(/\(/g)||[]).length,pc=(s.match(/\)/g)||[]).length; return {o,c,po,pc}; }
console.log("CS balance:", balance(cs));
console.log("JS balance:", balance(js));
let stripped = cs.replace(/""/g, "");
console.log("CS quote parity:", (stripped.match(/"/g)||[]).length % 2 === 0 ? "EVEN ok" : "ODD SUSPECT");
console.log("CS has leftover Self-Check text:", cs.includes("Self-Check (From Class Material)"));
const mcqIds = [...js.matchAll(/id:\s*'"'"'([a-z0-9-]+-mcq-\d+)'"'"'/g)].map(m=>m[1]);
console.log("Total mcq ids:", mcqIds.length, "(expect 126 = 31 pre-existing + 95 migrated)");
console.log("Duplicate ids:", mcqIds.length - new Set(mcqIds).size);
["18-how-to-approach-design","19-machine-coding-tictactoe","20-machine-coding-parking-lot"].forEach(s=>console.log(s, cs.includes(`"${s}" => @"`) ? "PRESENT" : "MISSING"));
["21-machine-coding-bookmyshow","22-machine-coding-splitwise","23-machine-coding-contest"].forEach(s=>console.log(s, cs.includes(`"${s}" => @"`) ? "UNEXPECTEDLY PRESENT" : "correctly absent"));
'
```

Expect: both balances equal pairs, quote parity EVEN, no leftover Self-Check text, 126 total
mcq ids with 0 duplicates, 18/19/20 present, 21/22/23 absent.

---

## 6. Key decisions made this session (don't re-litigate these)

- **Lombok**: strip it from all exercise source, replace with plain hand-written
  constructors/getters. User's explicit choice over "add Lombok as a dependency" — reasoning:
  keeps every exercise on the same minimal, proven dependency footprint, avoids annotation-
  processor risk in the sandboxed Docker runner.
- **Test-scope dependencies** (`org.reflections`, `org.mockito`): fine to add per-exercise
  when the *official* test file needs them — unlike Lombok, these don't affect main/solution
  code and preserve grading fidelity far better than hand-rewriting official tests.
- **No subagents for exercise wiring**: user explicitly asked whether to spawn Haiku
  subagents for speed; Claude recommended against it (correctness-sensitive task, subtle
  contracts like the "facade must hold zero raw fields" case, subagents wouldn't reduce total
  review burden) and the user agreed to sequential, single-agent wiring.
- **No conceptChecks invented for new lessons**: only port `practiceQuestions` from existing
  real MCQ material; never author new `conceptChecks` entries without real source material.
- **Lessons 21–23 blocked, not filled with generic content**: no source material exists;
  writing something anyway would violate the FROM_MATERIAL sourcing discipline this whole
  project is built on. Wait for the user to provide real Scaler class material for
  BookMyShow/Splitwise/Contest before touching these.
- **`[deploy]` tag discipline**: always include it in the commit message that should trigger
  a production deploy. This was discovered mid-session after 18 commits silently failed to
  deploy production for lack of the tag.

---

## 7. Resolved earlier this session (context only, no action needed unless something regresses)

- **Module 4 "stuck at Badge=Module 10, 0 lessons" bug**: production's `design-principles-
  patterns` module was created by an old `GetExpandedModules()` code path before the
  idempotent Module-4-creation check existed, so the check's `if (module == null)` guard
  never fired on existing (non-fresh) databases. Fixed by making the check self-healing
  (corrects Badge/Title/Description regardless of origin, backfills lessons if the first
  expected lesson slug is missing) — already committed and deployed. If you ever see a
  module stuck with a wrong Badge or missing lessons again, this is the pattern to check for.
- **Two extra redundant modules** (`ai-first-backend-capstone-advanced` "Module 13",
  `production-ai-enabled-system` "Elective"): removed from `GetExpandedModules()`. Any
  already-seeded rows from before the fix still need one-time manual cleanup via
  `info/.notes/cleanup-redundant-expanded-modules.sql` (should already have been run against
  both local and production earlier this session — check `git log` for confirmation it
  actually happened, since the seed code itself never deletes existing rows).
- **`git config core.fileMode`**: if `chmod +x scripts/*.sh` is needed again after a fresh
  `git pull` on WSL2, check `git config core.fileMode` — if `false`, git won't preserve the
  executable bit on checkout even though it's correctly set in the repo.

---

## 8. Reference — lesson slug map (for `exercise.json`'s `lessonSlug` field)

Course slug: `java-spring-lld`. Module slugs and their lesson slugs:

- `oop-foundations`: `01-intro-to-lld`, `02-oop-1-intro-lab`, `03-oop-2-access-modifiers-encapsulation`, `04-oop-3-polymorphism-interfaces`, `05-oop-4-lms-lab`
- `concurrency-multithreading`: `06-concurrency-1-threads`, `07-concurrency-2-executors`, `08-concurrency-3-synchronization`, `09-concurrency-4-semaphores`, `structured-concurrency`
- `advanced-java-collections`: `10-java-adv-1-generics`, `11-java-adv-2-collections-lab`, `12-java-adv-3-lambdas-streams`, `13-java-adv-4-streams-exceptions`
- `design-principles-patterns`: `14-solid-principles`, `15-creational-patterns`, `16-structural-patterns`, `17-behavioural-patterns-uml`
- `applied-machine-coding`: `18-how-to-approach-design`, `19-machine-coding-tictactoe`, `20-machine-coding-parking-lot`, `21-machine-coding-bookmyshow`, `22-machine-coding-splitwise`, `23-machine-coding-contest`, `24-machine-coding-hotel-management`
- `spring-enterprise-architecture`: `14-spring-boot-core`, `15-spring-data-jpa`, `16-spring-rest-api`, `17-machine-coding-capstone` (these reuse numbers 14-17 — a *different* set of lessons from Module 4's; this is why exercise/MCQ ids for Module 4 use slug-qualified prefixes like `lesson-14-solid-mcq-01`, not bare `lesson-14-mcq-01`, to avoid future collision)

---

## 9. If you're a fresh LLM session reading this cold

Do these in order:
1. `git status --short` and `git log --oneline -10` — confirm section 2's snapshot is still
   accurate; if not, re-derive current state from these commands rather than trusting section 2.
2. If the two content files are still uncommitted, run the verification battery in section 5
   before committing — don't assume a prior session's verification still applies if the
   files show unexpected diffs.
3. Read `CLAUDE.md` in the repo root — confirm the write-permission rules haven't changed.
4. Ask the user which of section 3 (ship verified work), section 4 (continue exercise
   wiring), or something new is the priority for this session.
