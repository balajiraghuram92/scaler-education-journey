# Prompt for Local LLM — FDE Phase 12: Enterprise Communication, Consulting & LLM Engineering (Module 5), Lessons 7-12 of 12 (module complete)

Paste everything below this line into the local LLM as-is. All lesson content and MCQs were
already authored by hand in a companion file — you are NOT being asked to write new prose or
invent examples, only to wire the already-approved content into the correct files.

**Before doing anything else: confirm you can actually read
`info/.notes/fde-lessons/phase-12-enterprise-consulting-llm-content.md` in full, and report back
what lessons and MCQ counts you see in it, before proceeding to Section 2.** Do not paraphrase,
rewrite, or invent content of your own for any lesson — copy the chapter bodies and MCQs from
that file verbatim. If you cannot read the file, or if what you find doesn't match what this
prompt describes, STOP and report the discrepancy instead of substituting your own content.

---

## 0. Prerequisite check

Confirm `api/Data/FdeCurriculumSeedData.cs` already has a `GetAuthoredFdeLessonContent(string
slug)` method with **61 existing cases** (11 `agentic-ai-core` + 12 `fde-foundations` + 15
`backend-observability-data` + 5 `full-stack-ai-frontends` + 12 `cloud-devops-infrastructure` + 6
`enterprise-consulting-llm` lessons 1-6, covering Phases 1-11) before `_ => null`. If those 61
cases aren't there — in particular, if `enterprise-consulting-llm` does not yet have 6 cases
(lessons 1-6) — STOP. Phase 11 must be applied first; do not proceed with this phase until it
has been.

---

## 1. Source file to read in full

`info/.notes/fde-lessons/phase-12-enterprise-consulting-llm-content.md`

This file contains 6 lessons, the second half of Module 5 ("5. Enterprise Communication,
Consulting & LLM Engineering"), lessons 7-12 of 12 — **this phase completes the module.** Phase
11 already covered lessons 1-6 (customer discovery, technical scoping, stakeholder communication,
demo storytelling, LLM fundamentals for production, and prompt engineering for production
systems); this phase does not touch or re-wire those.

Each of the 6 lessons has a YAML metadata block, a `<!-- CHAPTER_BODY_START -->` … `<!--
CHAPTER_BODY_END -->` block, and a `<!-- MCQ_SECTION_START -->` … `<!-- MCQ_SECTION_END -->` block
with structured `QUESTION_BLOCK`s.

The 6 lessons, in order, with their exact database slugs and MCQ counts:

| # | Lesson title | Lesson slug (use exactly) | MCQ count |
|---|---|---|---|
| 7 | RAG Architecture: Ingestion & Retrieval | `07-rag-architecture-ingestion-and-retrieval` | 9 |
| 8 | RAG over Customer Documents & Hybrid Search | `08-rag-over-customer-documents-and-hybrid-search` | 9 |
| 9 | RAG Evaluation & Iteration (RAGAS) | `09-rag-evaluation-and-iteration-ragas` | 9 |
| 10 | LLM Safety, Guardrails & Security | `10-llm-safety-guardrails-and-security` | 9 |
| 11 | Cost, Latency & Model Routing | `11-cost-latency-and-model-routing` | 9 |
| 12 | Assessment: Discovery Call + RAG PoC Build | `12-assessment-discovery-call-plus-rag-poc-build` | 8 |

Module slug for all 6: `enterprise-consulting-llm` (same module Phase 11 started; this phase
adds its final 6 lessons and completes it — 12/12).

---

## 2. Update `api/Data/FdeCurriculumSeedData.cs`

Find `GetAuthoredFdeLessonContent(string slug)`. It currently ends with the 61 existing cases
followed by `_ => null`. Add 6 new cases, one per lesson slug in the table above, **immediately
before** `_ => null` (after the existing 61 cases — do not reorder or touch those).

Same CHAPTER_BODY rules as previous phases:
- Copy the text between each lesson's markers verbatim, excluding the markers themselves.
- Escape every literal double-quote by doubling it: `"` → `""`.
- Backticks need no escaping.
- The string must end with a newline before the closing `"`.

Do NOT change any other part of the file, and do NOT modify or re-order any of the 61 existing
cases already in place.

---

## 3. Update `app/src/data/lessonInteractions.js`

Add 6 new keys to the `lessonInteractions` object, one per lesson:

```
'fde-curriculum/enterprise-consulting-llm/{lesson-slug}'
```

e.g. `'fde-curriculum/enterprise-consulting-llm/07-rag-architecture-ingestion-and-retrieval'`

Do NOT touch any existing key — 22 `java-spring-lld/...` + 11 `fde-curriculum/agentic-ai-core/...`
+ 12 `fde-curriculum/fde-foundations/...` + 15 `fde-curriculum/backend-observability-data/...` + 5
`fde-curriculum/full-stack-ai-frontends/...` + 12 `fde-curriculum/cloud-devops-infrastructure/...`
+ 6 `fde-curriculum/enterprise-consulting-llm/...` (lessons 1-6) = **83 total existing keys**
(from Phases 1-11) already present. After this phase, the file should have 89 total keys (83 + 6
new).

Follow the exact same conventions as previous phases:

### 3a. conceptChecks (exactly 2 per lesson)
Same selection priority as before — pick the two most non-trivial, misconception-prone points from
each lesson. `id` pattern:
`lesson-fde-enterprise-consulting-llm-{lesson-number:00}-concept-check-{01|02}` (lesson-number is
07-12 for this phase). Map source `CORRECT_ANSWER_KEY` (A/B/C/D) to lowercase `correctOptionId`.
Never add `initialSelectedOption` or `initialSubmitted`.

### 3b. architecture (optional — apply the inclusion test)
Apply the three-part inclusion test from the Master Reference Guide (§8a) to all 6 lessons.

Lessons 7, 9, and 10 (ingestion pipeline design, an ongoing RAGAS evaluation practice, and a
two-layer guardrail pipeline) are each candidates worth checking closely, but each is fully
covered by its Practical Backend Scenario prose as a description, not a genuinely non-obvious
multi-actor async flow, decorator chain, or runtime-branching pattern that prose alone
under-serves — omit `architecture` for all three.

Lesson 8's access-control-pre-filter-plus-hybrid-search retrieval path is the strongest
candidate in this phase: a query passing through role-based pre-filtering, parallel dense and
keyword retrieval, and reciprocal-rank-fusion merging is a genuine multi-step branching flow.
Still default to omitting it unless you judge, independently, that this specific flow gives a
7-8 year developer a faster mental model than the existing prose — if in doubt, omit.

Lesson 11's routing-gateway-plus-caching architecture (a request passing through budget check,
tier selection, prompt-cache lookup, semantic-cache lookup, and model call) is also a candidate
worth a second look for the same reason — a genuine multi-branch flow — but again default to
omitting unless it clearly earns its space beyond what the scenario prose already covers.

Lesson 12 is an assessment/rubric lesson with no single technical flow to diagram — omit.

Default to omitting the `architecture` key for all 6 lessons in this phase unless you find a
genuinely non-obvious multi-actor flow this description missed — if in doubt, omit.

### 3c. practiceQuestions (all remaining MCQs)
Same format as prior phases, `id` pattern
`lesson-fde-enterprise-consulting-llm-{lesson-number:00}-mcq-{01, 02, ...}`. None of this phase's
questions need a `codeBlock` field — omit it.

SOURCE_TYPE (`LLM_GENERATED` for all questions this phase) is a review marker only, not a JS data
field — an optional `// LLM_GENERATED` comment per question object is fine.

---

## 4. `app/src/data/lessonExerciseAssociations.js` — do NOT touch

None of these 6 lessons have a coding exercise. Do not add any entry.

---

## 5. Constraints

Do NOT touch:
- Any of the 61 existing cases in `GetAuthoredFdeLessonContent`
- `BuildLessonContent`, `BuildSupplementalLessonContent`, `Slugify`, or any other method in
  `FdeCurriculumSeedData.cs`
- Any existing key in `lessonInteractions.js` (83 total from Phases 1-11)
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
Full method body — all 67 cases now present (61 existing unchanged, 6 new from this phase),
before `_ => null`.

### OUTPUT B: Full updated `app/src/data/lessonInteractions.js`
Print the entire file — all 83 existing entries unchanged, plus the 6 new entries for this phase
(89 total).

### OUTPUT C: Architecture diagram decisions
For each of the 6 lessons, state whether you included or omitted the `architecture` key and the
one-sentence reason. Expected: all 6 omitted (lessons 7, 9, 10, and 12 have no qualifying flow;
lessons 8 and 11 have a genuinely multi-branch candidate flow but should still default to
omission unless independently judged to clearly pass the inclusion test).

### OUTPUT D: Exercise associations
State: "No exercises in this phase — lessonExerciseAssociations.js not changed."

---

## 7. Operational note — database reset required

These 6 lessons likely already exist in the database with thin, machine-templated `ContentBody`.
After applying the code changes and restarting the API, run:

```sql
UPDATE lessons SET content_body = '', content_status = 'Outline'
WHERE slug IN (
  '07-rag-architecture-ingestion-and-retrieval',
  '08-rag-over-customer-documents-and-hybrid-search',
  '09-rag-evaluation-and-iteration-ragas',
  '10-llm-safety-guardrails-and-security',
  '11-cost-latency-and-model-routing',
  '12-assessment-discovery-call-plus-rag-poc-build'
);
```

Then restart the API again:

```
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart api
```

This completes Module 5 ("5. Enterprise Communication, Consulting & LLM Engineering") in full —
all 12 lessons (1-6 from Phase 11, 7-12 from this phase) should now have authored content. No
further phases remain for this module.

---

## 8. Post-ingestion checklist

- [ ] All 6 new cases added to `GetAuthoredFdeLessonContent`, after the 61 existing cases, before
      `_ => null` (67 total)
- [ ] `lessonInteractions.js` has 6 new `fde-curriculum/enterprise-consulting-llm/...` keys; all
      83 pre-existing keys unchanged (89 total)
- [ ] Ran the SQL reset for all 6 slugs, then restarted the API
- [ ] Visited `/chapters/fde-curriculum` and confirmed all 12 lessons of "5. Enterprise
      Communication, Consulting & LLM Engineering" render real authored content — lessons 1-6
      from Phase 11 and lessons 7-12 from this phase — with none left showing
      placeholder/draft content
- [ ] Spot-checked at least 2 of the 6 new lessons: content matches the source file verbatim,
      concept checks not pre-answered on load, practice questions render at the bottom
- [ ] Confirmed at most one or two lessons in this phase ended up with an `architecture` key,
      and only if it genuinely passed the inclusion test — the default expectation is all 6
      omitted
