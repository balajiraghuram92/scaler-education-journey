# FDE Vertical Content — Status Tracker

**Read this file first, before doing anything else, when resuming this project in a new
session.** It tells you exactly what's done, what's pending, and the exact next step — no need
to re-verify from scratch or re-derive scope.

Last updated: 2026-08-31, after commit `19a8f9a` (Phase 10 + Phase 11 applied and verified).
**Phases 12, 13, and 15 have been APPLIED by the local LLM (in one combined pass) and VERIFIED
by Claude — 79 total cases, 793/793 MCQ blocks have exactly 4 options, no duplicate slugs, node
--check passes, verbatim content spot-check passed — but are still UNCOMMITTED in the working
tree as of this update.** Commit them (`git status` shows `api/Data/FdeCurriculumSeedData.cs`,
`app/src/data/lessonInteractions.js`, `task_tracker.md` modified) before starting further work.
Phase 14 (Module 6, lessons 7-11) is deliberately not yet authored — skipped so Phase 13 and a
future Phase 14 wouldn't be authored concurrently by two agents against the same module.

---

## How this project works (read once)

Per `/CLAUDE.md`, Claude cannot edit `api/` or `app/` files directly — only `info/.notes/` and
`exercises/`. The workflow per phase is:

1. Claude authors two files in `info/.notes/fde-lessons/`: `phase-N-<module-slug>-content.md`
   (the actual lesson content + MCQs, in the structured format defined in
   `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md`) and
   `phase-N-<module-slug>-prompt.md` (a copy-paste-ready prompt telling a local LLM exactly how
   to wire that content into `api/Data/FdeCurriculumSeedData.cs`'s `GetAuthoredFdeLessonContent`
   switch and `app/src/data/lessonInteractions.js`).
2. The user pastes the prompt file into their local LLM, which edits the actual app files and
   commits.
3. Claude verifies the resulting commit (diff is additive-only, content matches the source `.md`
   verbatim, no fabrication, correct case counts, no duplicate slugs, `lessonInteractions.js`
   has exactly 4 options per MCQ, `node --check` passes).
4. Move to the next phase.

**Known recurring defect to always check for:** MCQ `OPTIONS` blocks drifting to 5 entries
instead of 4 (a stray extra distractor line). This happened repeatedly across early phases
(1-7) and was fixed in the source `.md` files, and every phase since Phase 8 explicitly warns
authoring agents about it. Always verify option counts programmatically when checking a new
commit — see the verification snippet at the bottom of this file.

---

## Progress: what's actually applied in the app right now

Verify current reality anytime with:
```
cd /home/rbalaji/scaler-education-journey
git log --oneline -3
sed -n '/GetAuthoredFdeLessonContent/,/^    };/p' api/Data/FdeCurriculumSeedData.cs | grep -oP '"\K[0-9]{2}-[a-z0-9-]+(?=")' | wc -l
```
As of commit `19a8f9a`: **61 authored lesson cases** are live in
`GetAuthoredFdeLessonContent`, and `app/src/data/lessonInteractions.js` has 22 `java-spring-lld`
+ 61 `fde-curriculum` keys = 83 total.

| # | Module | Slug | Lessons | Status |
|---|---|---|---|---|
| — | Prerequisite: Agentic AI Core | `agentic-ai-core` | 11/11 | ✅ Done (Phases 1-2) |
| 1 | FDE Foundations | `fde-foundations` | 12/12 | ✅ Done (Phases 3-4) |
| 2 | Backend Engineering, Observability & Data Systems | `backend-observability-data` | 15/15 | ✅ Done (Phases 5-7) |
| 3 | Full-Stack FDE | `full-stack-ai-frontends` | 5/5 | ✅ Done (Phase 8) |
| 4 | Cloud, DevOps, Kubernetes & Infrastructure | `cloud-devops-infrastructure` | 12/12 | ✅ Done (Phases 9-10) |
| 5 | Enterprise Communication, Consulting & LLM Engineering | `enterprise-consulting-llm` | 6/12 | 🟡 Half done (Phase 11 = lessons 1-6) |
| 6 | Agentic Systems & Enterprise Integrations | `agentic-systems-integrations` | 0/11 | ❌ Not started |
| 7 | Application Engineering, Security & Reliability | `application-security-reliability` | 0/12 | ❌ Not started |
| 8 | System Design, Capstone & Hiring Readiness | `system-design-capstone` | 0/14 | ❌ Not started |
| — | Elective: Containerization/K8s | `elective-containerization-orchestration` | 0/17 | ❌ Not started (out of scope unless user asks) |
| — | Elective: AWS Multi-Region | `elective-aws-multi-region-cloud-deep-dive` | 0/31 | ❌ Not started (out of scope unless user asks) |

**Total: 61 of ~104 core lessons done (≈59%). 43 core lessons remain (≈7-8 more phases). Plus
48 elective lessons if those get put in scope later (≈8 more phases).**

---

## Also fixed (unrelated one-off bug)

Commit `de02ef0` fixed a pre-existing bug in the **Java LLD vertical** (not FDE) —
`java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces` had a concept check with
banned `initialSelectedOption`/`initialSubmitted` fields making it render pre-answered. Fixed,
verified zero remaining instances. That lesson still only has 1 concept check where the
convention is 2 — flagged, not fixed (would need new authored content, out of scope of the bugfix).

---

## Next step

**Phases 12, 13, and 15 are authored and waiting to be applied, in that order.** Each phase's
content + prompt files are ready in `info/.notes/fde-lessons/` (see File index below). Hand each
prompt to the local LLM **in this exact order — 12, then 13, then 15** — because each phase's
prompt states an exact prerequisite case/key count that assumes the prior phases in this batch
were already applied:

| Phase | Module | Lessons | Cases before → after | Keys before → after |
|---|---|---|---|---|
| 12 | 5 `enterprise-consulting-llm` | 7-12 (completes module, 12/12) | 61 → 67 | 83 → 89 |
| 13 | 6 `agentic-systems-integrations` | 1-6 of 11 (first half) | 67 → 73 | 89 → 95 |
| 15 | 7 `application-security-reliability` | 1-6 of 12 (first half) | 73 → 79 | 95 → 101 |

**Phase 14 (Module 6, lessons 7-11 — API Integration Patterns, Integration Failure Modes, Messy
Customer Data & Entity Resolution, Build: CRM-to-AI Support Copilot, Assessments) is
deliberately not yet authored** — skipped this batch specifically to avoid two agents authoring
the same module concurrently. It's the natural next authoring task after this batch is applied
and verified, and would complete Module 6 (11/11).

After Phase 14, remaining work: Module 7 lessons 7-12 (a "Phase 16"), then Module 8 "System
Design, Capstone & Hiring Readiness" (14 lessons, ~2-3 phases) — the final core module.

**Overlap-avoidance notes already baked into what was authored (for reference, not action):**
Phase 12's lessons 7-9 (RAG Architecture, RAG over Customer Docs, RAG Evaluation/RAGAS) were
written one level up from the Prerequisite module's RAG lesson (`agentic-ai-core`, slug
`05-rag-retrieval-augmented-generation`) — production/customer-deployment specifics rather than
re-teaching the RAG mechanism. Lesson 10 (Safety/Guardrails) goes one level up from
`03-advanced-prompting-and-ai-safety-basics`. Lesson 11 (Cost/Latency/Routing) extends the
prerequisite module's model-tier-routing example and resolves Phase 11 lesson 6's forward
reference. Phase 13's lessons 1-5 were written one level up from the Prerequisite module's agent/
multi-agent/debugging lessons into enterprise production territory (tool-contract versioning,
production hardening, failure taxonomies, MCP governance, supervisor/HITL patterns); lesson 6
introduces enterprise integration topology as new territory, scaffolding toward the module's
later CRM-to-AI Support Copilot capstone. Phase 15's lesson 2 builds on Module 3's React/TS
fundamentals rather than re-teaching them; lesson 3's Celery half builds on Module 2's existing
Celery/idempotency coverage, going one level up into RLS + multi-tenant background-job design.

---

## Verification snippet (run after any new phase is applied)

```bash
cd /home/rbalaji/scaler-education-journey
git log --oneline -3
git show --stat <sha>   # confirm additive-only diff to .cs/.js, lessonExerciseAssociations.js untouched
sed -n '/GetAuthoredFdeLessonContent/,/^    };/p' api/Data/FdeCurriculumSeedData.cs \
  | grep -oP '"\K[0-9]{2}-[a-z0-9-]+(?=")' | sort | uniq -d   # expect empty (no duplicate slugs)
node --check app/src/data/lessonInteractions.js
node -e "
const fs = require('fs');
const content = fs.readFileSync('app/src/data/lessonInteractions.js', 'utf8');
const re = /options:\s*\[([\s\S]*?)\]\s*,\s*correctOptionId/g;
let m, bad = 0, total = 0;
while ((m = re.exec(content)) !== null) {
  const count = (m[1].match(/\{\s*id:/g) || []).length;
  total++;
  if (count !== 4) { bad++; console.log('Found', count, 'options at index', m.index); }
}
console.log('Total option blocks:', total, 'Non-4-option:', bad);
"
```

Then spot-check 2-3 distinctive sentence fragments (10+ words) from the new `.md` source file's
`## Concepts Covered` sections against `api/Data/FdeCurriculumSeedData.cs` with `grep -c` to
confirm the local LLM copied verbatim rather than rewriting (this happened once, in Phase 3 —
always check for it, don't assume it won't recur).

---

## File index

All phase files live in `info/.notes/fde-lessons/`:
- `phase-0-authored-content-switch-prompt.md` — infra-only, adds the `GetAuthoredFdeLessonContent` switch mechanism
- `phase-1-agentic-ai-core-content.md` / `-prompt.md` through `phase-11-enterprise-consulting-llm-content.md` / `-prompt.md` — all applied
- `phase-12-enterprise-consulting-llm-content.md` / `-prompt.md` — authored, not yet applied
- `phase-13-agentic-systems-integrations-content.md` / `-prompt.md` — authored, not yet applied
- `phase-15-application-security-reliability-content.md` / `-prompt.md` — authored, not yet applied (Phase 14 intentionally skipped this batch — see Next step)
- This file (`STATUS.md`) — always check here first in a new session
