# Neuralascent Lesson Authoring — Master Reference Guide (Updated)

**Purpose:** Paste this at the start of each new chat session before providing lesson-specific material. This ensures consistent Tier-1 quality and efficient Local LLM parsing without re-explaining the platform.

**Last updated:** 2026-08-28
**Version:** 2.2 (Added architecture diagram inclusion criteria and React UI data guidance)

---

## 1. Platform Context (The Quick Version)

- **Site:** Neuralascent (`https://neuralascent.top`) — personal editorial learning platform for Java/Spring backend + applied AI
- **Owner:** Raghuram Balaji (balajiraghuram92@gmail.com)
- **Visual identity:** Warm editorial (serif headings, restrained sage/teal, hairline rules) — **not** a SaaS dashboard
- **Content model:** Pathway → Course → Module → Lesson ("Chapter")
- **Active pathways:**
  - Java Low-Level Design & Spring Architecture (`java-spring-lld`)
  - Forward Deployed Engineer (FDE) (`fde`)
- **Target learner:** Intermediate programmer (knows general programming, not this specific mechanism)
- **Voice:** Second person, present tense, direct — explain to a capable colleague

---

## 2. The Two Quality Tiers (Gap You're Closing)

### Tier 1 — Hand-authored, Published (Modules 1–4, 17 lessons)
Dense, grounded, referenced. Two paragraphs of Concepts Covered with real mechanism. Concrete named scenario. 5-step Practice Loop tied to that scenario. Real Evidence paragraph. Code blocks. Often diagrams and resources. **This is your target.**

**Example:** Lesson 4 — OOP-3: Polymorphism & Interfaces (live at `neuralascent.top/chapters/java-spring-lld`)

### Tier 2 — Machine-templated, Draft (Modules 5+, ~165 lessons)
Thin, generic, no code/diagrams/resources. One short paragraph per section. Coherent English, but not teaching depth. **Your job:** turn these into Tier-1 depth using real source material.

---

## 3. The Exact Markdown Structure (Do Not Deviate)

Every lesson body must follow this order exactly, with these exact section names:

```markdown
# {Lesson Title}

## Concepts Covered
{TWO dense paragraphs.
- Paragraph 1: Explain the actual mechanism, not a definition.
- Paragraph 2: Why it matters, design choices, trade-offs, consequences.
Use precise, load-bearing terminology. Reference real class/method/interface names in backticks.
Say WHY a design choice matters, not just WHAT it is.
NO bullet lists here — this is explanatory prose.
A short, correct, idiomatic Java/Spring/SQL fenced code block is welcome between or after the paragraphs
when it is more precise than another sentence — use it only for real, compiling-quality code.}

## Practical Backend Scenario
{ONE paragraph. A SINGLE, SPECIFIC, NAMED backend or AI-system scenario.
Name the service, the classes/interfaces involved, the concrete business behavior.
NOT "imagine a system that..." — commit to one example and follow it through.
One concrete moment: one entity, one business rule, one wrong outcome if the design is bad.
Reuse the same example in Practice Loop where natural.}

## Practice Loop
1. {imperative step — something the learner actually DOES}
2. {imperative step}
3. {imperative step}
4. {imperative step}
5. {imperative step}
{Exactly 5 steps, each a concrete action tied to the scenario above.
Ordered: step 1 is design/setup, final step is review/refactor/verification.
NOT generic ("practice the concept") — specific to THIS scenario.
Step 3 is ideally a diagnostic or measurement step that makes the problem visceral,
not a conceptual reflection (e.g., "count every line that touches this field" rather than "identify the scaling problem").}

## Evidence of Understanding
{ONE paragraph, written as testable capability.
Format: "You can explain X, demonstrate Y, and show that Z."
Describe what a correct test suite or a correct design review would confirm.
NOT a restatement of Concepts Covered.}

## Suggested Extension
{ONE to TWO sentences. A genuine stretch task naming a SPECIFIC addition.
Example: "Add a new implementation subclass to handle a new payment method."
NOT "explore further" filler.}
```

**Final line (outside the chapter body):**
```
Reference: {single most authoritative source — book+chapter+section, official docs page, or "own knowledge"}
```

This must be exactly one line. Do not write a bulleted list of multiple sources.

---

## 4. Non-Negotiable Quality Rules

### Rule 1: Ground Every Technical Claim
- If source material is provided, base the chapter on it and cite it.
- If no source exists, use only well-established, verifiable facts — never invent a class name, method signature, config key, library behavior, or version detail you are not confident about.
- **When in doubt, omit it rather than guess.**

### Rule 2: No Generic Filler
**Banned phrases (and their pattern):**
- "in today's fast-paced world"
- "it is important to note that"
- "this powerful feature"
- "at its core, X is..."

**Test:** If a sentence would still be true with the lesson's topic swapped for a different topic, rewrite or delete it. Every sentence must be specific to THIS concept.

### Rule 3: No Bullet-List Concepts
`Concepts Covered` is prose, not a glossary. Do not write "- **Term**: definition." Instead, write connected paragraphs that explain relationships and consequences, like a textbook.

### Rule 4: One Concrete Scenario, Followed Through
Reuse the same named example across "Practical Backend Scenario" and "Practice Loop" where natural. Do not introduce a new unrelated example in each section. The scenario must name a specific moment — one entity, one business rule, one wrong outcome. Not a system requirements document.

### Rule 5: Code When Code Helps
A short, correct, idiomatic Java/Spring/SQL fenced code block is welcome and often better than another paragraph — but **only real, compiling-quality code, never pseudocode.** A before/after code pair showing the difference between two approaches (e.g., procedural vs. OOP) is often the most precise way to illustrate the lesson's central claim.

### Rule 6: Match the Established Voice
- Second person ("you"), present tense, direct.
- Assume an intermediate learner who already knows general programming but not this specific mechanism.
- No em-dash-heavy marketing cadence; write like an engineer explaining something to a capable colleague.

### Rule 7: Respect Prior Lessons
If earlier lessons in the same module are given as context, do not re-explain their concepts — build on them by name.

### Rule 8: Minimum Depth
Target word counts depend on lesson difficulty and scope:

- **Foundational / conceptual lessons** (intro lessons, orientation, paradigm overviews): **500–800 words**
- **Advanced mechanism lessons** (SOLID principles, design patterns, concurrency, threading, generics): **1200–1500 words**

Advanced lessons covering SOLID principles, design patterns (Creational, Structural, Behavioral), concurrency, and threading genuinely need more space to show multiple code examples and trade-offs. Senior engineers reading these will skim-abandon content padded to length, so the higher cap is not a license to pad — it is space for additional code blocks and concrete trade-off discussion that shorter lessons do not need.

`Concepts Covered` should run noticeably longer than one short paragraph — aim for the density of the worked example below. Go deeper on mechanism, trade-offs, and concrete scenario instead of padding.

---

## 5. The Worked Example (Quality Bar Reference)

This is Lesson 4, live on the site. Read it as a calibration for density, not as a template to copy:

```markdown
# Lesson 4 — OOP-3: Polymorphism & Interfaces

## Concepts Covered
Polymorphism lets application code depend on a stable contract while different implementations provide behavior. An interface expresses a capability; an abstract class is useful when related implementations share protected mechanics or invariant checks. Dynamic dispatch selects the overriding implementation at runtime, which makes a collection of interface values useful without a chain of type checks.

Design interfaces around a consumer need. A `PaymentAuthorizer` should expose authorization behavior, not every detail of a gateway SDK. Keep interfaces small enough to fake in a unit test, and use default methods only for behavior that is genuinely safe for every implementation. Substitution means an implementation must honor the timing, error, nullability, and side-effect promises of the contract, not merely compile against it.

## Practical Backend Scenario
An order service supports card, wallet, and bank-transfer payments. It depends on `PaymentAuthorizer`, while `CardAuthorizer`, `WalletAuthorizer`, and `BankTransferAuthorizer` implement the contract. A registry selects the implementation by payment method. The service handles a declined authorization uniformly, while each adapter translates provider-specific responses at its own boundary.

## Practice Loop
1. Define a minimal interface from the use case rather than from a concrete SDK.
2. Write three implementations (card, wallet, bank transfer), each with its own error handling.
3. Create a registry that returns the right implementation by payment method.
4. Write an integration test that verifies the order service handles all three payment methods and a declined authorization correctly.
5. Refactor to ensure each implementation keeps provider-specific logic at its own boundary; the order service should not need to know which provider is in use.

## Evidence of Understanding
You can explain the difference between an interface (a contract for one capability) and an abstract class (shared mechanics among related implementations), and you can design an interface that is small enough to fake and large enough to be useful. You can demonstrate how dynamic dispatch works by writing code that iterates over a collection of interface values, and you can show that a test suite can verify behavior without knowing concrete types.

## Suggested Extension
Add a caching layer (`CachedAuthorizer`) that wraps any `PaymentAuthorizer` and caches recent authorization results by card fingerprint. Verify that a test can swap in your cache without modifying the order service.
```

---

## 6. What Success Looks Like (Self-Review Checklist)

Before passing a chapter to human review, check:

1. **FABRICATION:** Are all specific API names, method signatures, config keys, version numbers grounded in the source material or your confident knowledge? Any suspect claim quoted?
2. **GENERIC FILLER:** Zero sentences that would still make sense with a different topic. Quote any that fail.
3. **STRUCTURE:** Five headers present, in order, exactly as named. No extra sections.
4. **SCENARIO CONSISTENCY:** Same named scenario across "Practical Backend Scenario" and "Practice Loop"? Is it one concrete moment, not a system spec?
5. **DEPTH:** `Concepts Covered` reads as two dense explanatory paragraphs (mechanism + consequences), not bullets or one thin paragraph?
6. **CODE BLOCK:** Is there at least one real, compiling-quality code block in the chapter body where a concrete illustration would be clearer than prose? A before/after pair for the lesson's central concept is ideal.
7. **PRACTICE LOOP:** All 5 steps are concrete actions specific to THIS scenario, or do any read generic ("practice the concept", "review your code")? Step 3 in particular should be a diagnostic or measurement exercise, not a conceptual reflection.
8. **REFERENCE:** Is the final Reference line a single source? Not a bulleted list?
9. **SOURCE_TYPE:** Do all MCQ blocks and all Exercise blocks carry a `SOURCE_TYPE` field (FROM_MATERIAL or LLM_GENERATED)?
10. **WORD COUNT:** Foundational lessons target 500–800 words; advanced mechanism lessons target 1200–1500 words. Does this lesson meet its target tier?
11. **ARCHITECTURE DIAGRAM:** If you are recommending an architecture diagram for `lessonInteractions.js`, does it pass the inclusion test? (See §8.) A linear flow diagram that just restates the Practical Backend Scenario prose fails — cut it.

**Verdict:** PASS (ready for human review) or REVISE (list exactly what must change).

---

## 7. Local LLM Parsing Efficiency

### File Organization (4 Distinct Sections)

Structure your lesson file in this order:

```
1. METADATA_BLOCK (YAML)
   ↓ Lines 1-22
   ↓ Database fields (pathway, module, difficulty, etc.)
   ↓ Destination: Lesson metadata table

2. CHAPTER_BODY (Core Teaching Content)
   ↓ Between markers: <!-- CHAPTER_BODY_START --> to <!-- CHAPTER_BODY_END -->
   ↓ Contains: # Title + 6 sections (Concepts Covered → Suggested Extension)
   ↓ Destination: Lesson.ContentBody (extracted verbatim, no modification)

3. SUPPLEMENTARY_CONTENT (MCQs, Exercises, Resources)
   ↓ Each section has explicit markers (MCQ_SECTION, EXERCISES_SECTION, etc.)
   ↓ Contains: Structured blocks for Questions, Exercises, Resources
   ↓ Destination: Separate database tables (questions, exercises, resources)

4. MANIFEST (Inventory & Validation)
   ↓ External references table
   ↓ Validation checklist
   ↓ Confirms all zips, URLs, resources exist
```

### Metadata Block Format (YAML)

Include these fields for database mapping:

```yaml
lesson_id: [pathway]-[module]-[order]-[slug]
lesson_title: "Lesson N — [Full Title]"
lesson_order: [number]

pathway_id: java-spring-lld  # or fde
pathway_name: "Java Low-Level Design & Spring Architecture"

module_id: [module-slug]
module_name: "[Full Module Name]"
module_order: [number]

difficulty: Easy | Intermediate | Medium-Hard | Hard
estimated_minutes: [45]
content_status: Published | Draft | Outline

learning_outcomes:
  - "Outcome 1"
  - "Outcome 2"

created_date: "2026-08-28"
last_updated: "2026-08-28"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true | false
  mcq_count: [number]
  has_coding_exercises: true | false
  exercise_count: [number]
  has_further_reading: true | false
  resource_count: [number]
```

### Section Boundaries (Use HTML Markers)

Clear boundaries prevent ambiguity:

```html
<!-- CHAPTER_BODY_START -->
# Lesson Title
## Concepts Covered
[content]
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions
[MCQ blocks here]
<!-- MCQ_SECTION_END -->

<!-- EXERCISES_SECTION_START -->
## Coding Exercises
[Exercise blocks here]
<!-- EXERCISES_SECTION_END -->

<!-- FURTHER_READING_SECTION_START -->
## Further Reading & Resources
[Resource blocks here]
<!-- FURTHER_READING_SECTION_END -->
```

### Content Source Tracking (SOURCE_TYPE) — NEW in v2.1

Every MCQ block and every Exercise block must carry a `SOURCE_TYPE` field immediately after the block's ID and title fields:

```markdown
**SOURCE_TYPE:** FROM_MATERIAL | LLM_GENERATED
```

**FROM_MATERIAL** — derived directly from any source file provided by the human (lecture notes, pre-read, post-read, assignment files, additional MCQ lists, etc.). The content was explicitly present in, or directly transcribed from, a provided source.

**LLM_GENERATED** — added by the LLM based on lesson topics and its own knowledge; not traceable to a specific source file provided by the human. These require independent human review for accuracy and lesson fit.

**Why this matters:**
- It lets the reviewer spot-check only LLM-generated content, not re-verify what already came from authoritative source files.
- It surfaces which questions were independently introduced so they can be updated if the lesson content changes.
- It creates an audit trail: after review, FROM_MATERIAL items can be auto-approved; LLM_GENERATED items are flagged for sign-off.

**Practical rules:**
- Q1–Q6 are typically direct transcriptions from an assignment or MCQ file → `FROM_MATERIAL`
- LLM-added questions to fill gaps or cover deeper nuances → `LLM_GENERATED`
- When the human provides a list of additional MCQs in their source material, those are `FROM_MATERIAL` regardless of where they appear in the numbered sequence
- All exercises designed by the LLM (not described in any source file) → `LLM_GENERATED`
- If you are unsure whether content came from source material, mark it `LLM_GENERATED` — conservative labelling is safer for review

**Example MCQ block header:**
```markdown
### QUESTION_BLOCK_START: Q7

**QUESTION_ID:** Q7
**QUESTION_TITLE:** Java Access Modifiers and Encapsulation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** FROM_MATERIAL
```

**Example Exercise block header:**
```markdown
### EXERCISE_BLOCK_START: EX1

**EXERCISE_ID:** EX1
**EXERCISE_TITLE:** Refactor Procedural to OOP — Trip State Management
**DIFFICULTY:** Intermediate
**BLOOM_LEVEL:** Application
**ESTIMATED_TIME_MINUTES:** 30
**SOURCE_TYPE:** LLM_GENERATED
```

### Structured MCQ Format

Each MCQ is a self-contained block:

```markdown
### QUESTION_BLOCK_START: Q1

**QUESTION_ID:** Q1
**QUESTION_TITLE:** [Short Title]
**DIFFICULTY:** Easy | Medium | Hard
**BLOOM_LEVEL:** Knowledge | Understanding | Application | Analysis | Synthesis | Evaluation
**SOURCE_TYPE:** FROM_MATERIAL | LLM_GENERATED

**QUESTION_TEXT:**
[Full question with context]

**OPTIONS:**
- [ ] A: [Option A]
- [x] B: [Option B — CORRECT]
- [ ] C: [Option C]
- [ ] D: [Option D]

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
[Why B is correct, why others are wrong]

**LESSON_CONNECTION:** [Specific section reference: "Concepts Covered, Paragraph 2" or "Practice Loop, Step 3"]

**KEYWORDS:** [tag1, tag2, tag3]

### QUESTION_BLOCK_END: Q1
```

**Why structured format:**
- `QUESTION_ID` → Primary key (Q1–QN)
- `CORRECT_ANSWER_KEY` → Auto-grading
- `BLOOM_LEVEL` → Assessment categorization
- `SOURCE_TYPE` → Content review routing
- `KEYWORDS` → Search/tagging
- Block markers → No parsing overlap

### Structured Exercise Format

Each exercise is a self-contained block:

```markdown
### EXERCISE_BLOCK_START: EX1

**EXERCISE_ID:** EX1
**EXERCISE_TITLE:** [Title]
**DIFFICULTY:** Intermediate | Advanced
**BLOOM_LEVEL:** Application | Synthesis | Evaluation
**ESTIMATED_TIME_MINUTES:** [30]
**SOURCE_TYPE:** FROM_MATERIAL | LLM_GENERATED

**SKILLS_TESTED:**
- Skill 1
- Skill 2

**SCENARIO:** [Business context]

**STARTER_CODE_STRUCTURE:**
```
exercises/exercise-01-slug/
├── pom.xml
├── README.md
└── src/
```

**IMPLEMENTATION_REQUIREMENTS:**
1. [Requirement 1]
2. [Requirement 2]

**IMPLEMENTATION_CHECKLIST:**
- [ ] Task A
- [ ] Task B

**TEST_EXPECTATIONS:**
- ✓ Test 1
- ✓ Test 2

**DELIVERABLES:**
- File 1
- File 2

**WHY_THIS_MATTERS:**
[For senior learners: explain the production context and why this skill matters at scale]

**LEARNING_CONNECTION:** [Lesson section reference]

**EXTERNAL_RESOURCE:** exercises-lesson-NN-exN-slug.zip

### EXERCISE_BLOCK_END: EX1
```

**Why structured format:**
- `EXERCISE_ID` → Primary key (EX1, EX2, ...)
- `SOURCE_TYPE` → Content review routing
- `EXTERNAL_RESOURCE` → Direct zip linking
- `ESTIMATED_TIME_MINUTES` → Scheduling/UX
- `SKILLS_TESTED` → Competency mapping
- `WHY_THIS_MATTERS` → Production context for senior learners
- Block markers → No parsing overlap

### Structured Resource Format

Each resource is a self-contained block:

```markdown
### RESOURCE_BLOCK_START: RESOURCE_1

**RESOURCE_ID:** RESOURCE_1
**RESOURCE_TYPE:** BookChapter | Documentation | HackMd | PDF | Reference
**RESOURCE_TITLE:** [Title]
**AUTHOR:** [Author]
**SOURCE:** [Citation or URL]

**READING_LEVEL:** Beginner | Intermediate | Advanced | Reference
**TIME_ESTIMATE_MINUTES:** [30]

**RELEVANCE:** [Why this relates to the lesson]

**KEY_CONCEPTS:**
- Concept 1
- Concept 2

**RELATIONSHIP_TO_LESSON:** [Links to specific section]

### RESOURCE_BLOCK_END: RESOURCE_1
```

### External References Manifest

At the end, include a table and validation checklist:

```markdown
## External References & Downloadable Resources

| Reference ID | Type | Filename | Purpose | Status |
|---|---|---|---|---|
| ZIP_EX1 | Exercise Starter | exercises-lesson-01-ex01-slug.zip | Description | Required |
| ZIP_EX2 | Exercise Starter | exercises-lesson-01-ex02-slug.zip | Description | Required |

**VALIDATION_CHECKLIST:**
- [ ] ZIP_EX1 exists and contains starter code
- [ ] ZIP_EX2 exists and contains starter code
- [ ] Both pom.xml reference Java 11+ and JUnit 5
- [ ] Both include README.md with problem statements
- [ ] Both include test suites in src/test/java/
- [ ] All URLs in resources are accessible
```

### Local LLM Extraction Workflow

LLM follows this systematic workflow:

```
1. Parse YAML metadata block
   → Populate lesson.pathway_id, lesson.module_id, lesson.difficulty
   → Verify counts match actual content

2. Extract CHAPTER_BODY (between markers)
   → Validate 6-section structure (Concepts → Evidence → Extension)
   → Insert entire block to Lesson.ContentBody (no modification)

3. Extract MCQs (between MCQ markers)
   → For each QUESTION_BLOCK:
     - Read QUESTION_ID, CORRECT_ANSWER_KEY, OPTIONS
     - Read SOURCE_TYPE (route to auto-approve or human review queue)
     - Create Question record with auto-grading enabled
     - Store EXPLANATION, KEYWORDS for UI

4. Extract Exercises (between EXERCISES markers)
   → For each EXERCISE_BLOCK:
     - Read EXERCISE_ID, SKILLS_TESTED
     - Read SOURCE_TYPE (route to auto-approve or human review queue)
     - Read EXTERNAL_RESOURCE (zip filename)
     - Create Exercise record and link zip

5. Extract Resources (between RESOURCE markers)
   → For each RESOURCE_BLOCK:
     - Read RESOURCE_ID, RESOURCE_TYPE
     - Read RELATIONSHIP_TO_LESSON
     - Create LessonResource record (optional)

6. Validate all external references exist

7. Update Lesson.ContentStatus = "Published"
```

---

## 8. Optional Additions (When Warranted)

### LessonResource (Further Reading)
If the lesson genuinely benefits, add external resources following the Structured Resource Format above.

### LessonCodeComparison (Before/After)
A labeled code pair showing improvement:
```json
{
  "before": "// raw procedural code",
  "after": "// refactored OOP code",
  "explanation": "Why after is better"
}
```

### LessonDiagram (Inline SVG or Spec)
Render a concept visually if the lesson genuinely benefits. See §8a for detailed inclusion criteria — most lessons do not need a diagram.

### Problem (Static Problem Card)
A lighter-weight exercise distinct from coding exercises.

### Concept-Check MCQ
Only if the concept has genuine common misconceptions or 3–4 plausible-looking wrong answers. Mark SOURCE_TYPE appropriately.

### Coding Exercise Package
Only if the lesson teaches a mechanic small enough to verify with JUnit tests in a few files. Use Maven project structure with starter code, hidden tests, and solution reference. Include a `WHY_THIS_MATTERS` field for senior learners.

---

## 8a. React UI Data — lessonInteractions.js

Each lesson in `app/src/data/lessonInteractions.js` can carry three optional UI data objects: concept checks, an architecture diagram, and practice questions. This section governs when to include each one and what good looks like.

The key for each entry is `{pathway-id}/{module-slug}/{lesson-slug}`:
```js
'java-spring-lld/oop-foundations/01-intro-to-lld': {
  conceptChecks: [...],
  architecture: {...},      // optional — see inclusion criteria below
  practiceQuestions: [...]
}
```

---

### Concept Checks (max 2 per lesson)

Concept checks are gated interaction points — they stop the learner mid-page to verify understanding before they continue. **Maximum 2 per lesson.** They appear after the `Concepts Covered` section in the chapter reader.

**What makes a good concept check:**
- Tests a single, non-trivial point that is easy to get wrong
- Has 3–4 plausible wrong answers that reflect real misconceptions (not obviously silly distractors)
- The correct answer explains *why*, not just *what*
- Should NOT test a fact the learner just read verbatim — test application or recognition of a pattern

**Data shape:**
```js
{
  id: 'lesson-N-concept-check-01',
  eyebrow: 'CONCEPT CHECK 01 — TOPIC NAME',
  question: '...',
  options: [
    { id: 'a', label: 'A', text: '...' },
    { id: 'b', label: 'B', text: '...' },
    { id: 'c', label: 'C', text: '...' },
    { id: 'd', label: 'D', text: '...' }
  ],
  correctOptionId: 'b',
  explanation: '...',           // shown on correct answer
  incorrectExplanation: '...',  // shown on wrong answer — diagnostic, not a re-statement
  hint: '...'                   // shown on demand after wrong answer — one sentence
}
```

**DO NOT hardcode `initialSelectedOption` or `initialSubmitted` — these cause the question to appear pre-answered on load.**

---

### Architecture Diagram — Inclusion Criteria

The architecture diagram renders as an annotated flow chart after the `Practical Backend Scenario` section. **It is optional and most lessons should not include one.**

**Include a diagram only if ALL of these are true:**
1. The flow is genuinely non-obvious from prose alone (multi-actor async flow, decorator chain, strategy switching at runtime, event-driven pattern)
2. The diagram shows something the Practical Backend Scenario prose does NOT already cover
3. The diagram would give a 7-8 year developer a faster mental model than reading another paragraph

**Do NOT include a diagram if:**
- It is a linear request → controller → entity → output flow that is already described in the scenario text
- It just repeats what the code block already shows
- It is the only visual on the page for its own sake

**Best pattern for OOP / procedural-vs-OOP lessons:**
Do NOT use a linear flow. Use a **before/after contrast** — two separate node groups on one diagram, left showing procedural data mutation (multiple services reaching into the struct directly), right showing OOP (all services calling through the entity method). This earns the diagram's space and makes the lesson's central claim visible at a glance.

**Data shape (when included):**
```js
architecture: {
  id: 'lesson-N-{concept-slug}',
  eyebrow: 'PRACTICAL BACKEND SCENARIO — {SCENARIO NAME IN CAPS}',
  boundaryLabel: 'BOUNDARY LABEL',
  boundaryText: 'One sentence explaining what the boundary enforces.',
  nodes: [
    { id: 'input',    label: 'Entry Point',             kind: 'input'    },
    { id: 'service',  label: 'ServiceName',             kind: 'service'  },
    { id: 'boundary', label: 'Entity.method()',         kind: 'boundary', highlighted: true },
    { id: 'adapter',  label: 'DownstreamService',       kind: 'adapter'  },
    { id: 'output',   label: 'Result State',            kind: 'output'   }
  ]
}
```

Node `kind` values: `input`, `service`, `boundary`, `adapter`, `output`.
Only one node should be `highlighted: true` — the enforcement point (entity method or interface contract).

**If the lesson does not meet the inclusion criteria, omit the `architecture` key entirely from the entry.**

---

### Practice Questions (all lesson MCQs go here)

All MCQs from the lesson file's MCQ section go into `practiceQuestions` as structured objects. They render at the bottom of the chapter page after the concept checks and exercise. There is **no DB-backed `Question` model** — MCQs live entirely in this frontend data file.

**Data shape:**
```js
practiceQuestions: [
  {
    id: 'lesson-N-mcq-01',       // lesson-N-mcq-01 through lesson-N-mcq-NN
    question: '...',
    options: [
      { id: 'a', label: 'A', text: '...' },
      { id: 'b', label: 'B', text: '...' },
      { id: 'c', label: 'C', text: '...' },
      { id: 'd', label: 'D', text: '...' }
    ],
    correctOptionId: 'b',
    explanation: '...'           // shown after selection — no retry, no hint
  }
]
```

SOURCE_TYPE is a JS comment only — do not add it as a data field.

---

## 9. How to Use This Document (Workflow)

**In a new chat session, before providing lesson-specific material:**

1. **Paste this entire file as context** (or reference it: "Use the updated Master Ref guide v2.1")

2. **Then provide, in one message:**
   - Lesson title
   - Module name & order
   - Pathway (java-spring-lld or fde)
   - Difficulty & EstimatedMinutes
   - Learning outcomes (optional)
   - **The source material itself** (paste, describe, or link)

3. **The output you get:**
   - Complete lesson file (Lesson_N_Title_vN.md)
   - Structured with metadata, chapter body, MCQs, exercises, resources
   - All MCQs and exercises tagged with SOURCE_TYPE
   - Following all parsing efficiency guidelines
   - Ready for Local LLM extraction

4. **You run the self-review checklist** (§6) locally or in a fresh turn.

5. **Only if it passes, move to Local LLM ingestion** and then seeding into production database.

---

## 10. Critical Context — Platform Details

### Database Model
- `Lesson.ContentBody` — the Markdown chapter (extracted from CHAPTER_BODY markers)
- `Lesson.ContentStatus` — `Outline | Draft | Published`
- `Lesson.Difficulty`, `Lesson.EstimatedMinutes` — shown as metadata badges
- `Question` — MCQ records (auto-grading enabled)
- `Exercise` — Coding exercises (links to starter zips)
- `LessonResource` — Further reading & external resources (optional)

### Tech Stack
- Frontend: React 19 + Vite
- API: ASP.NET Core 8 (.NET)
- Database: PostgreSQL 16
- Deployment: Docker/Docker Compose, GitHub Actions, AWS EC2 (ARM64)
- Hosting: `neuralascent.top`

### Key Files (for reference only)
- `api/Data/JavaVerticalSeedData.cs` — Java pathway seed + content
- `api/Data/FdeCurriculumSeedData.cs` — FDE seed
- `app/src/pages/ChapterReader.jsx` — lesson reader component

---

## 11. The Seeding Write-Once Gotcha

When inserting a chapter into the codebase:

For Tier-2 (Draft) lessons already in the database, editing the seed file and redeploying does **not** automatically update the live row — the system only writes when the row is missing or status is `Outline`.

**Solution:** Use a `BackfillExpandedLessonContent(db, courseId)` method that runs on every startup:
```csharp
private static bool NeedsExpandedEnrichment(Lesson lesson)
{
    return lesson.ContentStatus == "Draft"
        && lesson.ContentBody.Length < 1200; // Tier-1 bodies run well past this
}
```

This mirrors the existing `BackfillLessonContent` pattern and is idempotent and safe.

---

## Quick Reference — At a Glance

| Item | Details |
|---|---|
| **Target Quality** | Tier-1: two dense Concepts paragraphs, concrete scenario, 5-step Practice Loop, Evidence paragraph, code blocks. Foundational: 500–800 words; Advanced: 1200–1500 words. |
| **Structure** | # Title, ## Concepts Covered, ## Practical Backend Scenario, ## Practice Loop (1–5 steps), ## Evidence of Understanding, ## Suggested Extension |
| **Tone** | Second person, present tense, direct. Explain to a capable colleague. No marketing cadence. |
| **Voice** | Intermediate programmer assumption: knows general programming, not this specific mechanism. |
| **Scenario** | One named example, reused across Practical Scenario and Practice Loop. One concrete moment: one entity, one business rule, one wrong outcome. Not a system spec. |
| **Practice Loop** | Exactly 5 steps, concrete actions specific to THIS scenario. Step 1: setup; Step 3: diagnostic/measurement (visceral, not conceptual); Step 5: review/refactor. |
| **Evidence** | Testable capability: "You can explain X, demonstrate Y, show that Z." |
| **Extension** | One to two sentences. Name a specific addition (new class, constraint, behavior). Not filler. |
| **Code Blocks** | Real, compiling-quality Java/Spring/SQL. Never pseudocode. A before/after pair for the lesson's central claim is ideal. |
| **Reference** | Single line. One authoritative source. Not a bulleted list. |
| **Minimum Length** | Foundational lessons: 500–800 words target. Advanced mechanism lessons: 1200–1500 words target. |
| **No Bullet Lists in Concepts** | Prose only. Connected paragraphs explaining mechanism + consequences. |
| **No Generic Filler** | Every sentence specific to THIS concept. Delete if swapping topics makes it still true. |
| **SOURCE_TYPE** | Required on every MCQ block and every Exercise block. `FROM_MATERIAL` (from provided sources) or `LLM_GENERATED` (added by LLM). Enables targeted human review of independently introduced content. |
| **MCQ Format** | Structured blocks with QUESTION_ID, CORRECT_ANSWER_KEY, BLOOM_LEVEL, SOURCE_TYPE, KEYWORDS for auto-grading, categorization, and review routing. |
| **Exercise Format** | Structured blocks with EXERCISE_ID, SOURCE_TYPE, EXTERNAL_RESOURCE (zip), SKILLS_TESTED, WHY_THIS_MATTERS for competency mapping and senior context. |
| **Section Markers** | HTML comments (<!-- SECTION_START --> to <!-- SECTION_END -->) for programmatic extraction. |
| **Metadata** | YAML with database field names; supplementary_content flags enable validation. |
| **Architecture Diagram** | Optional. Include ONLY if the flow is non-obvious from prose. Best pattern for OOP lessons: before/after contrast (procedural vs. OOP), not a linear request→entity→output flow. Most lessons: omit entirely. (See §8a.) |
| **Concept Checks** | Max 2 per lesson. Test application or misconception, not verbatim recall. Never hardcode `initialSelectedOption` or `initialSubmitted`. (See §8a.) |
| **Practice Questions** | All lesson MCQs go here as `practiceQuestions[]` in lessonInteractions.js — no DB `Question` model exists. SOURCE_TYPE is a JS comment only. (See §8a.) |

---

## Changelog

### v2.2 (2026-08-28) — Current

**What's New:**

- ✅ **Section §8a — React UI Data (lessonInteractions.js):** New dedicated section covering all three UI data objects (concept checks, architecture diagram, practice questions) with data shapes, inclusion criteria, and anti-patterns. This replaces guessing what goes where in the frontend data file.
- ✅ **Architecture diagram — inclusion criteria:** Explicit pass/fail test for whether a lesson earns a diagram. Key rule: a linear request→entity→output flow that repeats the Practical Backend Scenario prose does NOT pass. Best pattern for OOP lessons: before/after contrast (procedural vs. OOP), not a linear flow.
- ✅ **Concept checks — `initialSelectedOption`/`initialSubmitted` anti-pattern:** Explicitly banned. These cause questions to appear pre-answered on page load.
- ✅ **Practice questions — no DB Question model:** Clarified that all MCQs go into `practiceQuestions[]` in lessonInteractions.js. There is no DB-backed Question model; SOURCE_TYPE is a JS comment only, not a data field.
- ✅ **Self-review checklist §6:** Added item 11 for architecture diagram inclusion decision.
- ✅ **Quick Reference table:** Added rows for Architecture Diagram, Concept Checks, and Practice Questions.
- ✅ **CLAUDE.md (repo root):** Updated to allow Claude to read and write `info/.notes/` files directly (meta/reference docs with no effect on the running app).
- ✅ **Word count tiers (v2.1 carryover):** Foundational 500–800; Advanced mechanism 1200–1500.

### v2.1 (2026-08-28)

**What's New:**

- ✅ **Section 7 — Content Source Tracking (SOURCE_TYPE):** New convention for marking all MCQ and Exercise blocks with `FROM_MATERIAL` or `LLM_GENERATED`. Enables targeted human review of independently introduced content; FROM_MATERIAL items from provided sources can be auto-approved.
- ✅ **Rule 5 (Code Blocks):** Explicitly calls out before/after code pairs as the ideal way to illustrate the lesson's central claim.
- ✅ **Rule 4 (Scenario):** Strengthened to require "one concrete moment — one entity, one business rule, one wrong outcome" rather than a system requirements paragraph.
- ✅ **Practice Loop guidance:** Clarified that Step 3 should be a diagnostic or measurement exercise (e.g., "count every line that touches this field"), not a conceptual reflection ("identify the scaling problem").
- ✅ **Reference line:** Clarified must be exactly one line, not a bulleted list of multiple sources.
- ✅ **Self-Review Checklist (§6):** Added items for SOURCE_TYPE, code block presence, Reference format, and scenario concreteness.
- ✅ **Exercise format:** Added `WHY_THIS_MATTERS` field for senior learner context.
- ✅ **Quick Reference table:** Added SOURCE_TYPE row.

### v2.0 (2026-08-28)

**What's New in v2.0:**

- ✅ **Section 7 (Local LLM Parsing Efficiency):** Added comprehensive guide for structured formats, markers, and extraction workflow
- ✅ **Structured MCQ Format:** Consistent block format with QUESTION_ID, BLOOM_LEVEL, KEYWORDS for auto-grading
- ✅ **Structured Exercise Format:** Consistent block format with EXERCISE_ID, EXTERNAL_RESOURCE, SKILLS_TESTED
- ✅ **Structured Resource Format:** Consistent block format for further reading materials
- ✅ **Section Boundary Markers:** HTML comments for programmatic extraction (no parsing ambiguity)
- ✅ **Metadata Block:** YAML with explicit database field names and supplementary_content flags
- ✅ **External References Manifest:** Table + validation checklist for all zips and URLs
- ✅ **Local LLM Workflow:** Documented 7-step extraction workflow for systematic processing
- ✅ **Lesson 1 Example:** Lesson 1 v2 demonstrates all new patterns in practice

---

**You are now ready. In your next chat: paste this, then provide the lesson details + source material.**
