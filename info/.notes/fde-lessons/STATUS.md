# FDE Vertical Content — Status Tracker

**Read this file first, before doing anything else, when resuming this project in a new
session.** It tells you exactly what's done, what's pending, and the exact next step — no need
to re-verify from scratch or re-derive scope.

Last updated: 2026-08-31, after commit `50b8c0a` (Phase 14 applied — Module 6 complete, 11/11).

**Phases 16, 17, 18, and 19 have been AUTHORED (content + prompt files written, verified) but
NOT YET APPLIED to the app.** Together they cover ALL remaining core curriculum content —
Module 7's back half and the entirety of Module 8 (the final module). Once these four are
applied and committed, the ~104-lesson core FDE curriculum is 100% complete.

**Phase 20 has also been AUTHORED (content + prompt files written, verified) but NOT YET
APPLIED.** It is the first phase of the first elective module (`elective-containerization-orchestration`,
lessons 1-6 of 17: Docker Introduction, Docker Images and Containers, Building Your Own Docker
Image, Images and Containers Deep Dive, Docker Volumes, Docker Networking Deep Dive). Its prompt's
prerequisite check assumes Phases 16-19 are already applied (104 core cases / 122 keys in place)
before it is applied — apply Phases 16-19 first if not already done, then Phase 20. See
`phase-20-elective-containerization-orchestration-content.md` / `-prompt.md`. 51 MCQs total across
the 6 lessons, all verified programmatically (exactly 4 options each, answer-key/index/marked-option
consistent). Every lesson's chapter body includes at least one real Dockerfile/CLI code example, per
the user's explicit requirement for this hands-on elective batch. Module remains incomplete after
this phase — lessons 7-17 are Phases 21 and 22.

**Phase 21 is also AUTHORED, not yet applied.** Lessons 7-12 of 17 (Hardening the Docker
Environment (DevSecOps), Industry-Standard Container Hardening Demo, Introduction to
Orchestration, Kubernetes Architecture, Kubernetes Pod Deep Dive, ReplicaSets/Deployments/
Sidecars). Its prompt's prerequisite check assumes Phase 20 already applied (110 cases / 128
keys). 53 MCQs total, all verified (4-option, answer-key consistency). Every lesson has a real
code example (hardened Dockerfile, CI security-gate workflow, `kubectl describe pod` diagnostic
transcript, full Pod spec with init container + sidecar, Deployment manifest + rollout
transcript). Module remains incomplete — lessons 13-17 are Phase 22, not yet authored.
See `phase-21-elective-containerization-orchestration-content.md` / `-prompt.md`.

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
instead of 4 (a stray extra distractor line), and `CORRECT_ANSWER_KEY`/`CORRECT_ANSWER_INDEX`
mismatching the option actually marked `[x]`. Every authoring agent since Phase 8 (option count)
and Phase 13 (answer-key consistency) is instructed to self-verify both programmatically before
finishing — always spot-check anyway when verifying a newly applied commit.

---

## Progress: what's actually applied in the app right now (committed)

Verify current reality anytime with:
```
cd /home/rbalaji/scaler-education-journey
git log --oneline -3
sed -n '/GetAuthoredFdeLessonContent/,/^    };/p' api/Data/FdeCurriculumSeedData.cs | grep -oP '"\K[0-9]{2}-[a-z0-9-]+(?=")' | wc -l
```
As of the latest working tree: **104 authored lesson cases** are in `GetAuthoredFdeLessonContent`,
and `app/src/data/lessonInteractions.js` has 18 `java-spring-lld` + 104 `fde-curriculum` keys =
122 total.

| # | Module | Slug | Lessons | Status |
|---|---|---|---|---|
| — | Prerequisite: Agentic AI Core | `agentic-ai-core` | 11/11 | ✅ Done (Phases 1-2) |
| 1 | FDE Foundations | `fde-foundations` | 12/12 | ✅ Done (Phases 3-4) |
| 2 | Backend Engineering, Observability & Data Systems | `backend-observability-data` | 15/15 | ✅ Done (Phases 5-7) |
| 3 | Full-Stack FDE | `full-stack-ai-frontends` | 5/5 | ✅ Done (Phase 8) |
| 4 | Cloud, DevOps, Kubernetes & Infrastructure | `cloud-devops-infrastructure` | 12/12 | ✅ Done (Phases 9-10) |
| 5 | Enterprise Communication, Consulting & LLM Engineering | `enterprise-consulting-llm` | 12/12 | ✅ Done (Phases 11-12) |
| 6 | Agentic Systems & Enterprise Integrations | `agentic-systems-integrations` | 11/11 | ✅ Done (Phases 13-14) |
| 7 | Application Engineering, Security & Reliability | `application-security-reliability` | 12/12 | ✅ Done (Phases 15-16 — MODULE COMPLETE) |
| 8 | System Design, Capstone & Hiring Readiness | `system-design-capstone` | 14/14 | ✅ Done (Phases 17-19 — MODULE COMPLETE) |
| — | Elective: Containerization/K8s | `elective-containerization-orchestration` | 0/17 | ❌ Not started (out of scope unless user asks) |
| — | Elective: AWS Multi-Region | `elective-aws-multi-region-cloud-deep-dive` | 0/31 | ❌ Not started (out of scope unless user asks) |

**Total applied: 104 of 104 core curriculum lessons (100% COMPLETE). The entire FDE core curriculum is now fully authored, verified, and wired into the application.**

---

## Electives now IN SCOPE (as of this update) — 3 modules, 48 lessons, Phases 20-27

Corrected breakdown (an earlier version of this file had this wrong — only listed 2 electives and
miscounted AWS at 31 lessons; verified directly against `SupplementalModules` in
`api/Data/FdeCurriculumSeedData.cs`):

| Elective | Slug | Lessons | Phases |
|---|---|---|---|
| Containerization and Orchestration | `elective-containerization-orchestration` | 17 | 20 (L1-6), 21 (L7-12), 22 (L13-17, completes) |
| AWS Multi-Region Cloud Deep Dive | `elective-aws-multi-region-cloud-deep-dive` | 17 | 23 (L1-6), 24 (L7-12), 25 (L13-17, completes) |
| Storage, Networking & Reliability for FDEs | `elective-storage-networking-reliability` | 14 | 26 (L1-7), 27 (L8-14, completes) |

**Mechanism confirmed identical to core lessons:** `EnsureSupplementalModules` (line ~341 of
`FdeCurriculumSeedData.cs`) calls `GetAuthoredFdeLessonContent(lessonSlug) ??
BuildSupplementalLessonContent(...)` — the same override switch already governs electives, no
infra change needed. Slug format: `{lessonIndex+1:00}-{Slugify(Title)}`, numbering restarts at
01 per module (same as core). Each elective module already has decent one-paragraph-per-field
skeleton content inline in `SupplementalModuleDefinition`/`Lesson(...)` calls in the C# source —
authoring agents should read that as the outline/starting point, not contradict it, but expand it
into the full chapter-body format with **concrete worked examples baked in** (real Dockerfile/
K8s-YAML/Terraform/AWS-CLI snippets — user explicitly asked for this, since these are hands-on
infra topics more than the conceptual core modules were).

Dispatched 2 subagents at a time (throttled after an earlier 4-parallel dispatch hit the session
rate limit) — see progress notes below as each wave completes.

---

## Also fixed (unrelated one-off bug)

Commit `de02ef0` fixed a pre-existing bug in the **Java LLD vertical** (not FDE) —
`java-spring-lld/oop-foundations/04-oop-3-polymorphism-interfaces` had a concept check with
banned `initialSelectedOption`/`initialSubmitted` fields making it render pre-answered. Fixed,
verified zero remaining instances. That lesson still only has 1 concept check where the
convention is 2 — flagged, not fixed (would need new authored content, out of scope of the bugfix).

---

## Final Ingestion Summary: Phases 16, 17, 18, 19

All four phases have been applied and verified clean (104 cases, 122 keys, 870 total MCQs across all 104 FDE lessons, exactly 4 options per MCQ, no duplicate slugs, node AST syntax check passes).

| Phase | Module | Lessons | Cases before → after | Keys before → after |
|---|---|---|---|---|
| 16 | 7 `application-security-reliability` | 7-12 (completes module, 12/12) | 84 → 90 | 102 → 108 |
| 17 | 8 `system-design-capstone` | 1-5 of 14 | 90 → 95 | 108 → 113 |
| 18 | 8 `system-design-capstone` | 6-10 of 14 | 95 → 100 | 113 → 118 |
| 19 | 8 `system-design-capstone` | 11-14 of 14 (completes module AND the entire core curriculum) | 100 → 104 | 118 → 122 |

**Lesson breakdown for Module 8 (`system-design-capstone`, new module, 14 lessons total):**
1. Distributed Systems Fundamentals (CAP, PACELC, Raft, Saga) — Phase 17
2. System Design: RAG System at Scale — Phase 17
3. System Design: Agentic Platform at Scale — Phase 17
4. System Design: Multi-Tenant SaaS Platform — Phase 17
5. System Design: Enterprise Integration Hub — Phase 17
6. System Design Interview Framework & Practice — Phase 18
7. Capstone Sprint 1: Discovery & Solution Design — Phase 18
8. Capstone Sprint 2: Core Build & Integration Layer — Phase 18
9. Capstone Sprint 3: Harden, Secure & Observe — Phase 18
10. Capstone Sprint 4: Red-Team, Eval & Fix — Phase 18
11. Capstone Demo Day: Client Panel Presentation — Phase 19
12. Interview Readiness & Career Launch — Phase 19
13. FDE Mock Engagement: Full Simulation — Phase 19
14. Graduation Review: Portfolio Defense & Next Steps — Phase 19

Phase 18's lessons 7-10 (the four Capstone Sprints) are ONE continuous narrative authored by a
single agent for continuity: fictional client **Meridian Risk Partners** (a mid-market P&C
insurance MGA) engaging an FDE to build **SubmissionIQ**, an AI-assisted broker-submission
intake/underwriting-assist platform — key names Sandra Voss (VP Underwriting, economic buyer),
Derek Nomura (Head of Underwriting Ops, champion); broker portal **BrokerLink**; policy admin
system **Atlas**; a second tenant **Coastal Underwriters** onboards mid-arc to drive the
multi-tenant hardening story in Sprint 3. Sprint 1 = discovery/PRD-lite/risk-register, Sprint 2 =
grounded extraction + RAG + orchestrator-worker MCP/connector build, Sprint 3 = RLS hardening +
guardrails + observability, Sprint 4 = RAGAS eval gate + red-team + integration-failure diagnosis
+ reconciliation against Sprint 1's risk register. Phase 19's lesson 11 (Demo Day) was
deliberately written with a generic "the capstone system you built" framing rather than assuming
Meridian Risk Partners by name, since it was authored in parallel without access to Phase 18's
invented scenario — this is fine as written, no follow-up needed.

**Overlap-avoidance notes already baked into what was authored (for reference, not action):**
Phase 16's lessons 7-12 continue the Meridian Legal Ops/ClauseReview scenario from Phase 15 and
go one level up from Module 4's secrets/observability basics into enterprise-specific concerns
(cross-account BYOK, k6 load-testing methodology, customer-facing RCA). Phase 17's 5 lessons are
explicit system-design-interview-style syntheses (requirements → capacity estimate → high-level
design → trade-off deep-dive → failure modes) applying RAG/agentic/multi-tenant/integration
content already taught in Phases 1-2, 12-15 at scale, deliberately not re-explaining those
mechanisms' basics. Phase 18's lesson 6 (Interview Framework) references Phase 17's 5 lessons by
slug as worked examples. Phase 19 avoids re-teaching demo storytelling (Phase 11 lesson 4),
red-team/eval methodology (Phase 12/14), and system-design-interview technique (Phase 18 lesson
6) in its own lessons 11-13.

**After this batch, the entire ~104-lesson core FDE curriculum is complete.** The only remaining
optional work is the two elective modules (Containerization/K8s, 17 lessons; AWS Multi-Region
deep-dive, 31 lessons) — out of scope unless the user asks to bring them in scope.

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
- `phase-1-agentic-ai-core-content.md` / `-prompt.md` through `phase-14-agentic-systems-integrations-content.md` / `-prompt.md` — all applied and committed (through commit `50b8c0a`)
- `phase-15-application-security-reliability-content.md` / `-prompt.md` — applied and committed
- `phase-16-application-security-reliability-content.md` / `-prompt.md` — authored, not yet applied (Module 7 lessons 7-12, completes the module)
- `phase-17-system-design-capstone-content.md` / `-prompt.md` — authored, not yet applied (Module 8 lessons 1-5)
- `phase-18-system-design-capstone-content.md` / `-prompt.md` — authored, not yet applied (Module 8 lessons 6-10)
- `phase-19-system-design-capstone-content.md` / `-prompt.md` — authored, not yet applied (Module 8 lessons 11-14, completes the module AND the entire core curriculum)
- `phase-20-elective-containerization-orchestration-content.md` / `-prompt.md` — authored, not yet
  applied (Elective module `elective-containerization-orchestration`, lessons 1-6 of 17 — first
  elective phase; module not yet complete)
- This file (`STATUS.md`) — always check here first in a new session
