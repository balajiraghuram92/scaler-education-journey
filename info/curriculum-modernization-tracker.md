# Curriculum Modernization Tracker

## Purpose

Bring the Java Low-Level Design and Forward Deployed Engineer (FDE) curricula into one canonical Chapters experience while preserving the existing legacy tracker, completion history, and source lineage.

The curriculum conversion supplied in `pasted-text.txt` is a planning reference. Lesson text written in this phase must be original instructional material, with external technical claims grounded in primary documentation where appropriate.

## Product Decisions

- `Chapters` is the curriculum library and the only top-level entry point for learning pathways.
- Active pathways initially are **Java Low-Level Design & Spring Architecture** and **Forward Deployed Engineer (FDE)**.
- FDE remains a career-oriented pathway. Shared subjects must also be available through focused pathways later, rather than forcing users to find them inside FDE.
- Planned pathways are catalog records with `ComingSoon` status, not fake active courses. They do not display progress or lesson counts.
- Existing FDE legacy tasks remain the source of completion history until each task is safely linked to one canonical lesson.
- No legacy vertical, task, or completion state is deleted in this programme.

## Planned Pathway Catalog

| Status | Pathway | Scope |
| --- | --- | --- |
| Active | Java Low-Level Design & Spring Architecture | Java OOP, concurrency, JVM, collections and Spring architecture |
| Active | Forward Deployed Engineer (FDE) | Customer delivery, applied AI, application engineering, cloud and enterprise systems |
| Coming soon | Data Structures & Algorithms | Problem-solving patterns and core algorithms |
| Coming soon | SQL & Data Foundations | Relational data modelling, SQL and query performance |
| Coming soon | High-Level Design & Distributed Systems | Scalable architecture and distributed systems trade-offs |
| Coming soon | Frontend Engineering with React | TypeScript, React, Next.js and frontend quality |
| Coming soon | Data Engineering | Pipelines, warehouses, orchestration and data quality |
| Coming soon | Machine Learning & Deep Learning | ML theory, model evaluation, neural networks and CNNs |
| Coming soon | AWS Cloud Engineering | AWS foundations, security, networking and managed services |
| Coming soon | DevOps & Platform Engineering | Docker, Kubernetes, CI/CD, GitOps and infrastructure as code |

## Shared-Content Rule

One canonical lesson can appear in more than one pathway. Completion is recorded once for that lesson and reflected in every pathway that includes it. A pathway-specific application, assessment, or capstone remains its own lesson.

Examples:

- Docker fundamentals belongs to DevOps & Platform Engineering and is included in FDE.
- AWS IAM and VPC fundamentals belongs to AWS Cloud Engineering and is included in FDE.
- A customer deployment exercise remains an FDE-specific lesson.

## Phase Status

### Phase 1 — Inventory and design

- [x] Confirm active and planned pathway catalog.
- [x] Identify Java as canonical-course data and FDE as legacy-task data.
- [x] Confirm no deletion and no progress double-counting policy.
- [x] Inspect every FDE legacy task and its source module in `FdeSeedData.cs`.
- [x] Record canonical FDE module and lesson generation rules without choosing legacy ownership.

### Phase 2 — Chapters experience

- [x] Redesign Chapters as a warm editorial curriculum library.
- [x] Render active pathways from the learning-path API.
- [x] Render planned pathways as disabled, descriptive catalog cards.
- [x] Add responsive interaction and keyboard-safe visual states.
- [x] Update the reading room to render each lesson's stored chapter body rather than a fixed Java concurrency manuscript.

### Phase 3 — Canonical FDE migration

- [x] Implement additive FDE canonical course, module, and lesson seed source.
- [x] Implement verified-only FDE and Java task-to-content reconciliation rules.
- [ ] Run a dry reconciliation report before any apply operation.
- [ ] Verify the migration is idempotent and leaves legacy data intact.

### Phase 4 — Original lesson content

- [x] Create original draft instructional bodies, core concepts, worked scenarios, practice loops, and completion cues for every seeded FDE lesson.
- [x] Add curated primary-source reference trails by curriculum module.
- [ ] Keep incomplete or research-dependent material clearly marked as a draft rather than inventing notes.
- [x] Keep FDE chapter bodies marked as `Draft` until editorial review.
- [x] Add deterministic Java legacy-title mappings to the canonical Java course.
- [x] Review Java course coverage against the supplied curriculum reference and fill confirmed lesson-body gaps with original material.
- [x] Add an idempotent Java backfill that enriches empty or original outline-only lesson bodies without replacing substantive editorial work.

### Phase 5 — Validation

- [ ] Confirm `/chapters` shows Java and FDE as active pathways.
- [ ] Confirm Java and FDE both route through `Chapters` breadcrumbs.
- [ ] Confirm FDE progress matches mapped legacy completions without duplicate counting.
- [ ] Confirm no stale legacy-only route is used by the Home tracker.
- [ ] Run the project verification available in the local environment.

### Phase 6 - Scaler-aligned curriculum expansion

- [x] Cross-check the converted 57-page curriculum reference and the supplied module screenshots against the current Java and FDE seeds.
- [x] Add the three missing FDE elective modules: Containerization and Orchestration, AWS Multi-Region Cloud Deep Dive, and Storage, Networking & Reliability for FDEs.
- [x] Add 48 original FDE elective draft chapters with stable supplemental identities and no invented progress.
- [x] Expand the Java/backend course additively with Databases & SQL, Design Principles & Patterns, Applied Design & Machine Coding, both AI-first backend capstones, Production-Ready AI-Enabled Systems, High-Level Design, and Data Engineering.
- [x] Add 117 original Java/backend draft chapters from the confirmed reference outline: 13 SQL, 10 patterns, 14 machine-coding, 12 primer, 15 advanced capstone, 8 AI-enabled system, 21 HLD, and 24 data-engineering chapters.
- [x] Add seed idempotency coverage for the FDE electives and Java expanded module catalogue.
- [ ] Resolve the one legacy compatibility exception: the current FDE task tracker combines the Agentic System Build & Red-Team assessment with Integration War Room, while the reference presents them as two separately tracked entities. Do not split or delete the legacy task without an approved reconciliation design.

## Implementation Evidence

- **Completed in source:** Chapters catalog redesign, planned-pathway catalog, canonical FDE seed source, FDE reconciliation safety update, Java title mappings, 104 FDE core draft bodies, 48 FDE elective draft bodies, substantive Java lesson-body backfills, and 117 new Java/backend draft chapters.
- **Mapped source coverage:** the FDE seed catalogue contains 104 legacy tasks plus 48 additive elective chapters. The Java tracker contains 22 legacy items; its canonical pathway preserves 17 Java lessons, one Structured Concurrency chapter, five practice problems, and now 117 additive Scaler-aligned Java/backend chapters.
- **Static check:** `git diff --check` completed without whitespace errors on 2026-08-24.
- **Not run:** Database seeding, reconciliation dry-run/apply, application build, tests, and browser verification. The first seed/reconciliation attempt was blocked before the application started because the published API image lacks a compatible manifest for the user's Linux platform; use the local Compose development override for the next attempt.

## Current Constraints and Risks

- The existing `FdeReconciler` intentionally refuses to fabricate canonical FDE entities. The canonical seed/migration must be added before it can verify task links.
- The source conversion was generated by an AI tool, so its structure will be reconciled against the local legacy FDE tasks before becoming canonical data.
- Course notes are a later product phase. This phase establishes high-quality original chapter foundations, not a claim that every lesson has final editorial copy.
- The current model assigns a lesson to one course module. Shared AWS, DevOps, frontend, and data lessons need a future additive membership table before they can be reused across standalone pathways without copying content.
- The current expansion keeps HLD and Data Engineering in the Java/backend course to match the confirmed curriculum sequence. A future course-membership model should promote them to independent pathways while keeping a single completion record.
