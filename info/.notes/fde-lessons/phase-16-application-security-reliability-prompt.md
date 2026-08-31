# Prompt for Local LLM — FDE Phase 16: Application Engineering, Security & Reliability (Module 7), Lessons 7-12 of 12 (COMPLETES MODULE 7)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-16-application-security-reliability-content.md` in full, and report
back what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not
paraphrase, rewrite, or invent content of your own for any lesson — copy the chapter bodies and
MCQs from that file verbatim. If you cannot read the file, or if what you find doesn't match what
this prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **84 existing cases** before `_ => null`. This phase is applied first in a new
four-phase batch (Phase 16, then Phase 17, 18, 19, covering Module 8). 84 = 61 cases from Phases
1-11 + 6 from Phase 12 + 6 from Phase 13 + 6 from Phase 15 (Module 7 lessons 1-6) + 5 from Phase
14 (Module 6 completion — API Integration Patterns & Connector Design, Integration Failure Modes
& Debugging, Messy Customer Data & Entity Resolution, Build: CRM-to-AI Support Copilot,
Assessments: Agentic System Build & Red-Team, Integration War Room).

**If the case count is anything other than 84, STOP and report the exact count you find instead
of proceeding.** Do not attempt to reconcile a mismatched count on your own judgment, and do not
substitute a different set of existing cases than what the file actually contains.

Also confirm `app/src/data/lessonInteractions.js` has **102 existing keys** before proceeding: 18
`java-spring-lld/...` + 84 `fde-curriculum/...`. If this count doesn't match, STOP and report the
exact count you find.

This phase's dependency is strictly on those two counts (84 cases, 102 keys) being correct — it
has no content dependency on any specific earlier phase's subject matter beyond what's already
baked into those counts.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-16-application-security-reliability-content.md`

This file contains 6 lessons, the **second and final half** of Module 7 ("7. Application
Engineering, Security & Reliability"), lessons 7-12 of 12. Lessons 1-6 were added in Phase 15.
**Applying this phase completes Module 7 at 12/12 lessons, which also completes all of Modules
1-7 in the FDE curriculum — only Module 8 ("System Design, Capstone & Hiring Readiness") remains
outstanding afterward.**

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | Enterprise Security for FDE Systems (PII, SOC2, GDPR) | `07-enterprise-security-for-fde-systems-pii-soc2-gdpr` | 8 |
| 8 | Secrets, Encryption & Deployment Topologies | `08-secrets-encryption-and-deployment-topologies` | 8 |
| 9 | Load Testing, Capacity Planning & Performance (k6) | `09-load-testing-capacity-planning-and-performance-k6` | 8 |
| 10 | Incident Response & Customer-Facing RCA | `10-incident-response-and-customer-facing-rca` | 8 |
| 11 | Enterprise Readiness Checklist & Go-Live | `11-enterprise-readiness-checklist-and-go-live` | 8 |
| 12 | Assessment: Secure Deploy + Incident Simulation | `12-assessment-secure-deploy-plus-incident-simulation` | 8 |

Total MCQs across all 6 lessons: **48**.

These slugs were derived by hand from each lesson's exact title using the repo's existing
`Slugify` function in `api/Data/FdeCurriculumSeedData.cs` (lowercase; `&` → ` and `; `+` → `
plus `; every other non-alphanumeric run collapsed to a single `-`; trimmed of leading/trailing
`-`). If you independently derive a different slug from the titles in `api/Data/FdeSeedData.cs`,
STOP and report the discrepancy rather than picking one silently — do not proceed with a slug
that doesn't match the table above.

Module slug for all 6: `application-security-reliability` (same module as Phase 15 — this phase
adds the second and final half, completing it at 12/12).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 84 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 84 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 84 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/application-security-reliability/{lesson-slug}'
```

e.g. `'fde-curriculum/application-security-reliability/07-enterprise-security-for-fde-systems-pii-soc2-gdpr'`

Do NOT touch any existing key — 18 `java-spring-lld/...` + 84 `fde-curriculum/...` = **102 total
existing keys** already present. After this phase, the file should have **108 total keys** (102 +
6 new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-application-security-reliability-{lesson-number:00}-concept-check-{01|02}`
(lesson-number is 07-12 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase
`correctOptionId`. Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.

**Expected outcome: omit `architecture` for all 6 lessons.** None of them describe a genuinely
non-obvious multi-actor async flow, decorator chain, or runtime-branching pattern beyond what the
scenario prose and any included code block already cover:
- Lesson 7 (Enterprise Security): a data-classification/redaction decision and an erasure
  handler's table-scoped lookup — linear, already clear from prose.
- Lesson 8 (Secrets, Encryption & Deployment Topologies): a cross-account KMS grant and a
  topology decision — the JSON policy snippet already shows the mechanism precisely; a diagram
  would restate it.
- Lesson 9 (Load Testing): a k6 test methodology and a bottleneck-diagnosis narrative — the
  included k6 script code block already shows the concrete mechanism.
- Lesson 10 (Incident Response): a document-writing lesson (postmortem vs. RCA) — no flow to
  diagram.
- Lesson 11 (Enterprise Readiness Checklist): a four-category checklist — a checklist is not an
  architecture flow.
- Lesson 12 (Assessment): an assessment lesson — no diagram, consistent with other assessment
  lessons in this pathway (e.g., Phase 12 lesson 12, Phase 14 lesson 11) which also omit one.

If your own read of any lesson's Concepts Covered or Practical Backend Scenario genuinely clears
the inclusion bar differently, you may include an `architecture` object for that one lesson only,
modeled per §8a's node shape — but the default and expected outcome for this phase is to omit it
for all 6.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-application-security-reliability-{lesson-number:00}-mcq-{01, 02, ...}`. None of this
phase's questions need a `codeBlock` field — omit it, even where the chapter body itself contains
a SQL, JSON, or JS code block (that code lives in the chapter body, not in an MCQ, for every
question in this phase).

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 84 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (102 total from Phases 1-15, including Phase 14)
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
Full method body — all 90 cases now present (84 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 102 existing entries unchanged, plus the 6 new entries for this phase
(108 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: all 6 omitted (no qualifying multi-actor or runtime-branching flow
beyond what the prose and code blocks already cover) — see §3b above for the per-lesson reasoning.

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-enterprise-security-for-fde-systems-pii-soc2-gdpr',
  '08-secrets-encryption-and-deployment-topologies',
  '09-load-testing-capacity-planning-and-performance-k6',
  '10-incident-response-and-customer-facing-rca',
  '11-enterprise-readiness-checklist-and-go-live',
  '12-assessment-secure-deploy-plus-incident-simulation'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 7 ("7. Application Engineering, Security & Reliability") at 12/12 lessons —
lessons 1-6 were completed in Phase 15, and this phase adds lessons 7-12. **All of Modules 1-7 in
the FDE curriculum are now fully authored; only Module 8 ("System Design, Capstone & Hiring
Readiness") remains, to be covered in Phases 17-19.**

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 84 existing cases, before
      `_ => null` (90 total)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/application-security-reliability/...`
      keys; all 102 pre-existing keys unchanged (108 total)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 12 lessons of "7. Application
      Engineering, Security & Reliability" now render real authored content (Module 7 shows
      12/12 complete)
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed every MCQ block that made it into `practiceQuestions` has exactly 4 options — the
      source file has already been checked for this programmatically, but verify none were
      dropped or duplicated during transcription
- [ ] Confirmed no `architecture` key was added for any of the 6 lessons unless a genuine,
      independently-justified exception was found and stated in OUTPUT C
