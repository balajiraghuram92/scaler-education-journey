# Prompt for Local LLM — FDE Phase 27: Elective "Storage, Networking & Reliability for FDEs", Lessons 8-14 of 14

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-27-elective-storage-networking-reliability-content.md` in full,
and report back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do
not paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies
and MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match
what this prompt describes, STOP and report the discrepancy instead of substituting your own
content.

**This is the FINAL phase of the entire FDE content project.** After this phase is applied, the
full ~104-lesson core curriculum (Prerequisite + Modules 1-8) AND all three elective modules
(Containerization/K8s — 17 lessons, AWS Multi-Region Cloud Deep Dive — 17 lessons, Storage,
Networking & Reliability for FDEs — 14 lessons) are complete: **152 total authored lessons**.
There is no Phase 28. Treat this application as closing out the project, not as "one more phase
in a series."

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **145 existing cases** before `_ => null`. This phase is applied after Phase
26 (`elective-storage-networking-reliability` lessons 1-7 of 14) has already been applied on top
of the full 104-core + 17-Containerization/K8s + 17-AWS-Multi-Region baseline: 104 + 17 + 17 + 7 =
145.

**If the case count is anything other than 145, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains. In particular:
- If the count is 138 (104 + 17 + 17), Phase 26 has not been applied yet — stop and say so.
- If the count is 121 or 127 or 133, one of the AWS Multi-Region elective's own phases (23, 24,
  25) has not been applied yet — stop and say so.
- If the count is anywhere below 121, one of the earlier elective or core-curriculum phases has
  not been applied yet — stop and say so.

Also confirm `app/src/data/lessonInteractions.js` has **163 existing keys** before proceeding: 18
`java-spring-lld/...` + 145 `fde-curriculum/...` (104 core + 17 Containerization/K8s + 17 AWS
Multi-Region + 7 from Phase 26). If this count doesn't match, STOP and report the exact count you
find.

This phase has a content dependency on Phase 26 only in the sense that both phases populate the
same module (`elective-storage-networking-reliability`) — lessons 1-7 from Phase 26 and lessons
8-14 from this phase together complete the module at 14/14. This phase does not reference or
require any specific content from Phase 26's lessons; it only requires that phase's case/key
counts to already be landed before this one is applied.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-27-elective-storage-networking-reliability-content.md`

This file contains 7 lessons — **lessons 8-14 of 14**, completing the "Storage, Networking &
Reliability for FDEs" elective module (`elective-storage-networking-reliability`). This is the
**last phase of the third and final elective module**, and consequently the last phase of the
entire FDE offering. Do not add placeholder content for any other lesson — this phase is scoped
to exactly these 7.

Each of the 7 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s. None of this phase's MCQ blocks carry a `**CODE_BLOCK:**`
field — every fenced code/config sample in this phase lives inside the chapter body itself (cache
headers, CDN CLI, Route 53 JSON, HikariCP/resilience4j YAML, retry-with-jitter Java, token-bucket
Python, Nginx `limit_req` config, a CAP/PACELC trade-off table), not attached to individual
questions. Several questions quote a short snippet of that chapter-body code directly inline in
`QUESTION_TEXT` (fenced) — treat those as part of the question text, not as a separate
`CODE_BLOCK` field, and copy them exactly as written.

The 7 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 8 | Edge Caching, CDNs, and Latency Reduction | `08-edge-caching-cdns-and-latency-reduction` | 9 |
| 9 | Microservices Performance: Latency, Throughput, and Concurrency | `09-microservices-performance-latency-throughput-and-concurrency` | 8 |
| 10 | Designing for High Availability: Multi-Region Active-Active | `10-designing-for-high-availability-multi-region-active-active` | 9 |
| 11 | Fault Tolerance Engineering: Circuit Breakers, Retries, and Backoff | `11-fault-tolerance-engineering-circuit-breakers-retries-and-backoff` | 9 |
| 12 | Graceful Degradation | `12-graceful-degradation` | 8 |
| 13 | Rate Limiting, Throttling, and Shedding | `13-rate-limiting-throttling-and-shedding` | 9 |
| 14 | Data Consistency Trade-offs: CAP and PACELC | `14-data-consistency-trade-offs-cap-and-pacelc` | 9 |

Total MCQs across all 7 lessons: **61**.

Module slug for all 7: `elective-storage-networking-reliability` (this module already exists as a
`SupplementalModuleDefinition` — Phase 26 added lessons 1-7; this phase adds lessons 8-14,
completing it at 14/14).

Double-check each slug against `Slugify(lessonDefinition.Title)` yourself before using it:
lowercase, `&`→` and `, `+`→` plus `, everything else non-alphanumeric (including colons, commas,
and internal hyphens like the one in "Trade-offs") collapsed to `-`, trimmed, multiple `-`
collapsed to one. In particular, verify `14-data-consistency-trade-offs-cap-and-pacelc` yourself
against the literal title "Data Consistency Trade-offs: CAP and PACELC" — the colon after
"Trade-offs" and the internal hyphen inside "Trade-offs" both collapse into the surrounding
single hyphens, they do not produce a double hyphen or a separate segment.

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 145 existing cases
followed by `_ => null`. Add 7 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 145 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's `<!-- CHAPTER_BODY_START -->` / `<!-- CHAPTER_BODY_END -->`
  markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

**These 7 lessons' chapter bodies contain fenced code/config blocks** — HTTP `Cache-Control`
headers, an AWS CLI `create-invalidation` command, a CDN cache-policy YAML fragment, a HikariCP
pool-sizing YAML fragment, a Route 53 `change-resource-record-sets` JSON payload, a Python cart-merge
function, a `resilience4j` circuit-breaker/time-limiter/bulkhead YAML block, a Java retry-with-
jittered-backoff snippet, a Java feature-flag/fallback snippet, a Python `TokenBucket` class, an
Nginx `limit_req_zone`/`limit_req` config, a raw `429` HTTP response, and a CAP/PACELC trade-off
Markdown table plus a Python sticky-routing function. Copy them exactly as written, including all
indentation inside the code fences — do not reformat, re-indent, or "clean up" any code sample.
Any double quote inside a code sample (JSON payloads especially) still needs to be doubled per the
rule above — be careful here, the Route 53 JSON payload in Lesson 10 is quote-heavy.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 145 existing
cases already in place. Do NOT modify `SupplementalModules`, `EnsureSupplementalModules`,
`Slugify`, `BuildSupplementalLessonContent`, or any other method.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 7 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/elective-storage-networking-reliability/{lesson-slug}'
```

e.g. `'fde-curriculum/elective-storage-networking-reliability/08-edge-caching-cdns-and-latency-reduction'`

This is the same key pattern as every core and elective module — `EnsureSupplementalModules`
builds the lesson slug the same way core modules do (`{lessonIndex+1:00}-{Slugify(Title)}`).

Do NOT touch any existing key — 18 `java-spring-lld/...` + 145 `fde-curriculum/...` (104 core +
17 Containerization/K8s + 17 AWS Multi-Region + 7 from Phase 26) = **163 total existing keys**
already present. After this phase, the file should have **170 total keys** (163 + 7 new). This
completes `lessonInteractions.js` for the entire FDE offering — no further phases will add keys
to this file.

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Pick the two most non-trivial, misconception-prone points from each lesson. `id` pattern:
`lesson-fde-elective-storage-networking-reliability-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 08-14 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

Strong candidates per lesson (pick your own final two per lesson from the actual chapter text —
these are starting suggestions, not a mandate):
- Lesson 8: the `max-age` vs `s-maxage` distinction; the cross-tenant cache-key root cause.
- Lesson 9: Little's Law pool sizing; tail-amplification compounding across fan-out calls.
- Lesson 10: per-data-path granularity (active-active for cart, single-writer for settlement);
  the routing layer's own RTO contribution (health-check interval + DNS TTL).
- Lesson 11: why `slowCallDurationThreshold` matters for a "slow but 200" degradation; why a
  bulkhead is complementary to, not redundant with, a circuit breaker.
- Lesson 12: why a per-request fallback still pays the timeout cost until wired to the breaker's
  OPEN state; honest labeling ("Popular picks") vs. silent substitution.
- Lesson 13: capacity (burst) vs. refill_rate (sustained) as independently tunable numbers; why a
  global limit fails to isolate tenants from each other.
- Lesson 14: this lesson's explicit differentiation from the core curriculum's CAP/PACELC theory
  lesson; the settlement-vs-cart guarantee choice and its concrete latency cost.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 7 lessons: (1)
the flow must be genuinely non-obvious from prose alone, (2) it must show something the Practical
Backend Scenario prose does not already cover, (3) it must give a 7-8 year developer a faster
mental model than another paragraph would.

Lesson 10 (Designing for High Availability: Multi-Region Active-Active) and Lesson 11 (Fault
Tolerance Engineering: Circuit Breakers, Retries, and Backoff) are the strongest candidates in
this phase — a two-region active-active topology with a per-field routing split (cart
active-active, settlement single-writer) is a genuinely spatial, multi-actor relationship, and a
circuit breaker's CLOSED/OPEN/HALF_OPEN state machine is a state-transition diagram, not a linear
flow, which is exactly the shape this guide's inclusion test favors. Apply the test yourself
against the actual final lesson text — if either clearly passes, include an `architecture` object
(for Lesson 10: the two-region topology with the settlement single-writer path highlighted; for
Lesson 11: the three-state circuit breaker machine with the OPEN state highlighted). For lessons 8,
9, 12, 13, and 14: these are a cache-key/header lesson, a queueing-math lesson, a feature-flag/
fallback lesson, a token-bucket/admission lesson, and a decision-table lesson respectively, each
already anchored by a concrete code/config/table example that makes the mechanism as clear as a
diagram would — omit `architecture` for all five unless your own read finds a genuine exception.
If in doubt on any lesson, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-elective-storage-networking-reliability-{lesson-number:00}-mcq-{01, 02, ...}`.

**`codeBlock` field:** Several MCQs in this phase's source file quote a short fenced code/config
snippet directly inside `QUESTION_TEXT` (e.g. Lesson 9's Little's Law questions quoting the
HikariCP YAML, Lesson 11's questions quoting the `resilience4j` config or the backoff computation,
Lesson 13's questions quoting the `TokenBucket`/Nginx/429 snippets, Lesson 14's questions quoting
the trade-off table or the sticky-routing function). For each of these, set the practiceQuestions
entry's `codeBlock` field to that exact snippet (verbatim, preserving indentation) and keep
`question` as pure prose per §8a's rule — locate them by looking for a fenced block inside a
`QUESTION_TEXT` section in the source file. All other MCQs in this phase have no such snippet in
their `QUESTION_TEXT` — omit `codeBlock` for those, including questions that only reference a
short identifier inline (e.g. `s-maxage`, `Retry-After`) in a prose sentence.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 7 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 145 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, `EnsureSupplementalModules`,
  `SupplementalModules`, or any other method/definition in `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (163 total from prior phases)
- `lessonExerciseAssociations.js`
- Any CSS file, any other `.cs` file, any other `.js` file
- The `getLessonInteractions` export at the bottom of `lessonInteractions.js`

Match code style exactly:
- `FdeCurriculumSeedData.cs`: C# verbatim strings, double-quote escaping, 4-space indent
- `lessonInteractions.js`: single quotes, 2-space indent, trailing comma on last property

---

## 6. Output format

Produce, clearly labeled:

### OUTPUT A: The updated `GetAuthoredFdeLessonContent` method
Full method body — all 152 cases now present (145 existing unchanged, 7 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 163 existing entries unchanged, plus the 7 new entries for this phase
(170 total).

### OUTPUT C: Architecture diagram decisions
For each of the 7 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: lessons 8, 9, 12, 13, and 14 omitted; lessons 10 and 11 are
judgment calls — either omitted (default) or included with the topology/state-machine framing
described in §3b above.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required, and this is the final phase

These 7 lessons likely already exist in the database with thin, machine-templated `ContentBody`
(from `BuildSupplementalLessonContent`'s skeleton-expansion, not this phase's authored content).
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '08-edge-caching-cdns-and-latency-reduction',
  '09-microservices-performance-latency-throughput-and-concurrency',
  '10-designing-for-high-availability-multi-region-active-active',
  '11-fault-tolerance-engineering-circuit-breakers-retries-and-backoff',
  '12-graceful-degradation',
  '13-rate-limiting-throttling-and-shedding',
  '14-data-consistency-trade-offs-cap-and-pacelc'
);
```

**Note:** these slugs (`08-...` through `14-...`) are reused across multiple modules by design
(numbering restarts per module). If your `lessons` table has a composite or module-scoped
uniqueness constraint, scope this `UPDATE` by joining to the module
(`elective-storage-networking-reliability`) explicitly instead of relying on `slug` alone — check
the schema before running this if you have any doubt, so you don't accidentally reset lessons in a
different module that happen to share the same slug.

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

**This is the final phase of the entire FDE content project.** After this phase is applied and
verified, the "Storage, Networking & Reliability for FDEs" elective module is complete at 14/14,
and with it, all three elective modules (Containerization/K8s 17/17, AWS Multi-Region Cloud Deep
Dive 17/17, Storage/Networking/Reliability 14/14) plus the full ~104-lesson core curriculum
(Prerequisite + Modules 1-8, all complete) are done — **152 total authored FDE lessons, 170 total
`lessonInteractions.js` keys (18 java-spring-lld + 152 fde-curriculum).** There is no further
phase to plan or apply.

---

## 8. Post-ingestion checklist

- [ ] All 7 new cases added to `GetAuthoredFdeLessonContent`, after the 145 existing cases, before
      `_ => null` (152 total)
- [ ] `lessonInteractions.js` has 7 new
      `fde-curriculum/elective-storage-networking-reliability/...` keys; all 163 pre-existing
      keys unchanged (170 total)
- [ ] Ran the SQL reset for the 7 slugs, scoped to the correct module if the schema requires it,
      then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed the "Storage, Networking & Reliability for
      FDEs" elective module appears with all 14 lessons rendering real authored content (lessons
      1-7 from Phase 26, lessons 8-14 from this phase) — including visible, correctly-formatted
      code/config blocks (Cache-Control headers, resilience4j YAML, the Python TokenBucket class,
      the Nginx config, the CAP/PACELC trade-off table) — and that no lesson in this module still
      shows placeholder/skeleton-expanded content
- [ ] Spot-checked at least 3 of the 7 new lessons: content matches the source file verbatim
      (including fenced code blocks and the Lesson 14 Markdown table), concept checks not
      pre-answered on load, practice questions render at the bottom, and any question with a
      `codeBlock` renders it as a distinct monospace block
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this programmatically (61/61 blocks verified:
      exactly 4 options in A-D order, `correctOptionId` matching the marked option), but verify
      none were dropped or duplicated during transcription
- [ ] Confirmed the full FDE offering now totals 152 lessons across the core curriculum and all
      three electives, and that `elective-storage-networking-reliability` specifically shows
      14/14 lessons with authored content — this is the closing checklist item for the entire
      project, not just this phase
