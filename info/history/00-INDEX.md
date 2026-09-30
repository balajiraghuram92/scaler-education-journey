# 00 — INDEX: `info/history/` (consolidated project history)

**Purpose.** On 2026-09-30 the ~370 Markdown files under `info/` (dozens of session handoffs, executed Local-LLM prompts, superseded plans, three copies of the same HLDs and a 5.8 MB
concatenation of everything) were consolidated into the **8 files below + this index (9 files total)** so a future LLM can read the whole project history in a few passes.
Nothing in `info/` affects the running app (see `CLAUDE.md`). The merged originals were **deleted from the working tree; git keeps them**.

**Recover any original:** `git show 9e6d03f:<original path>` (commit `9e6d03f`, 2026-09-22, is the last commit before this consolidation), or
`git log --diff-filter=D --name-only -- info | head` to find when it was removed, then `git show <commit>^:<path>`.

## Reading order for a fresh LLM session
1. `01-…` (what/why/rules/timeline) → 2. the file for your task (`07-…` for anything under `ai-agent/`, tutor, RAG, Langfuse, pgvector) → 3. `04-…` before touching deploy/DB.
Always confirm current state with `git status`/`git log`; handoff snapshots drift.

## The files
| File | Contents |
|---|---|
| `01-project-overview-timeline-and-decisions.md` | Project overview, tracks/status, working rules, master timeline, decisions index |
| `02-java-lld-fde-curriculum-and-content-pipeline.md` | Java LLD + FDE curriculum, content pipeline & seeding gotchas, exercise engine, lesson-prompt history, FDE deployment investigation |
| `03-website-redesign-and-platform-migration.md` | Warm-Editorial redesign, redesign data migration (evidence/ledger/runbook), AWS platform-migration plan, exercise-design docs, old-site baseline |
| `04-deployment-infra-and-ops.md` | EC2/Docker/CI/SSM/secrets, WSL2/Podman environment facts, pgvector prod migration, session handoffs |
| `05-localization-lab-on-hold.md` | Localization Lab (ON HOLD): decisions, built state, UI specs, pending Python AI service, market playbook, Unity dossier, Model Economics Matrix notes |
| `06-chatbot-auth-and-ai-integration-history.md` | Scope rule, auth/TOTP/$2-day Llama chat build, AI-Infusion course review, chatbot HLD drafts, AI-platform TODO tracker + Muse appendix |
| `07-ai-learning-agent.md` | AI Learning Agent (PRIMARY): decisions, architecture, verified implementation status vs tracker, reviewer findings, condensed tracker, gotchas |
| `08-python-migration-and-study-plans.md` | Backend migration presented as Python migration; migration/interview plans; curriculum-modernization, FDE syllabus, Azure plan, FDE self-study, project labs |

**Related conventions used inside the files:** `(07 §5.3)` = file 07, section 5.3. "Local LLM" = the user's Gemini/3.8 Flash/Qwen coding model. "Tracker" = `ai-learning-agent-BUILD-TRACKER`.

## Terminology changes made during consolidation (2026-09-30, user directive)
- **"Java migration" → "Python migration".** Wherever the old docs described migrating the backend to Java 21 / Spring Boot 3 / Spring AI (`api-java`, "Java-first rebuild", "Java/Spring migration", "Java reimplementation blueprint"),
  the consolidated docs present the target as **Python (FastAPI + Pydantic v2 + Pydantic AI + LangGraph)** — the AI Learning Agent stack (`08-…` §A, provenance box in §A.0).
  The **Java LLD curriculum** (course content about Java, Java exercises, Java runners) is unchanged.
- Java-migration references found **outside `info/`** were *not* edited; they are listed in `08-…` §A.10 and in the PR description.

## Merge map — which original went where (deleted originals; recover via git)

### → `01-project-overview-timeline-and-decisions.md` (1 files)
- `info/.notes/neuralascent-work-status.md`

### → `02-java-lld-fde-curriculum-and-content-pipeline.md` (35 files)
- `info/.notes/URGENT-fix-broken-csharp-quote-escaping-prompt.md`
- `info/.notes/exercise-runner-docker-socket-permission-fix-prompt.md`
- `info/.notes/exercise-sandbox-spring-boot-extension-prompt.md`
- `info/.notes/exercise-workspace-missing-nonEditable-files-fix-prompt.md`
- `info/.notes/fix-idempotent-module4-seeding-prompt.md`
- `info/.notes/fix-java-lld-preanswered-concept-check-prompt.md`
- `info/.notes/fix-lesson-exercise-association-test-prompt.md`
- `info/.notes/fix-stale-backfill-reconciliation-test-prompt.md`
- `info/.notes/lesson-14-15-content-and-hotel-lesson-prompt.md`
- `info/.notes/lesson-16-structural-patterns-prompt.md`
- `info/.notes/lesson-17-behavioural-patterns-uml-prompt.md`
- `info/.notes/lesson-17-uml-enrichment-prompt.md`
- `info/.notes/lesson-18-19-20-machine-coding-prompt.md`
- `info/.notes/lesson-3-exercise-directory-prompt.md`
- `info/.notes/lesson-3-llm-ingestion-prompt.md`
- `info/.notes/lesson-4-13-content-regrounding-prompt.md`
- `info/.notes/lesson-5-13-content-expansion-additions.md`
- `info/.notes/lesson-9-10-13-duplicate-mcq-fix.md`
- `info/.notes/lesson-content-hierarchy-and-status-fix-prompt.md`
- `info/.notes/lesson-grid-redesign-prompt.md`
- `info/.notes/machine-coding-module-restructure-and-enrichment-prompt.md`
- `info/.notes/mcq-coverage-gap-fix-prompt.md`
- `info/.notes/mcq-distractor-quality-fix-prompt.md`
- `info/.notes/mcq-dynamic-architecture-migration-prompt.md`
- `info/.notes/migrate-mcqs-to-interactive-ui-prompt.md`
- `info/.notes/module-restructure-prompt.md`
- `info/.notes/multi-exercise-per-lesson-and-nav-cleanup-prompt.md`
- `info/.notes/parking-lot-exercises-wiring-prompt.md`
- `info/.notes/parking-lot-mcq-upgrade-prompt.md`
- `info/.notes/remove-domain-tags-from-hero-prompt.md`
- `info/.notes/remove-redundant-expanded-modules-prompt.md`
- `info/.notes/simplify-nav-to-chapters-only-prompt.md`
- `info/.notes/exercise-knowledge/PILOT-database-factory.md`
- `info/.notes/fde-lessons/2026-09-01-ec2-fde-deployment-investigation.md`
- `info/local-llm-content-pipeline/01-content-population-workflow.md`

### → `03-website-redesign-and-platform-migration.md` (30 files)
- `info/images-newdesign/v2-references/neuralascent-redesign-prompts-v2.md`
- `info/images-newdesign/v2-references/neuralascent-redesign-prompts.md`
- `info/website-assignments-reference/1.neuralascent-java-lld-interactive-learning-blueprint.md`
- `info/website-assignments-reference/2.neuralascent_java_exercises_architecture_handoff.md`
- `info/website-assignments-reference/neuralascent-interactive-java-exercise-architecture-and-java-reimplementation-blueprint.md`
- `info/website-reference/chat-handoff-2026-08-23.md`
- `info/website-reference/future-platform-migration-plan.md`
- `info/website-reference/local-llm-migration-prompts.md`
- `info/website-reference/migration-evidence/final-audit-report.md`
- `info/website-reference/migration-evidence/final-stabilization-defect-ledger.md`
- `info/website-reference/migration-evidence/phase-0-inventory-template.md`
- `info/website-reference/migration-evidence/phase-1-runtime-hardening.md`
- `info/website-reference/migration-evidence/phase-2-bridge-schema.md`
- `info/website-reference/migration-evidence/phase-3a-java-pilot.md`
- `info/website-reference/migration-evidence/phase-3b-backfill.md`
- `info/website-reference/migration-evidence/phase-4-api-services.md`
- `info/website-reference/migration-evidence/phase-4b-importer.md`
- `info/website-reference/migration-evidence/phase-5a-frontend-foundation.md`
- `info/website-reference/migration-evidence/phase-5b-webpages.md`
- `info/website-reference/migration-evidence/phase-6-deployment-runbook.md`
- `info/website-reference/migration-evidence/phase-7-bake-review.md`
- `info/website-reference/migration-evidence/stabilization-defect-ledger.md`
- `info/website-reference/migration-execution-tracker.md`
- `info/website-reference/proposals/bake-review-and-cleanup-proposal.md`
- `info/website-reference/redesign-data-migration-plan.md`
- `info/website-reference/runbooks/production-deployment-runbook.md`
- `info/website-reference/technical-migration-architecture.md`
- `info/website-reference/website-comparison-baseline.md`
- `info/study-tracker-webpage-redesign.md`
- `info/local-llm-content-pipeline/00-project-knowledge-map.md`

### → `04-deployment-infra-and-ops.md` (5 files)
- `info/.notes/SESSION-HANDOFF-STATUS.md`
- `info/.notes/SESSION-HANDOFF-2026-09-22.md`
- `info/.notes/SESSION-2026-09-08-phase0-infra-and-deploy.md`
- `info/.notes/SESSION-2026-09-10-phase0-deploy-debugging.md`
- `info/.notes/SESSION-2026-09-13-pgvector-migration.md`

### → `05-localization-lab-on-hold.md` (10 files)
- `info/.notes/localization-lab-ARCHITECTURE-AND-WORKFLOW.md`
- `info/.notes/localization-lab-BUILD-PROMPT.md`
- `info/.notes/localization-lab-STATUS-TRACKER.md`
- `info/.notes/localization-lab-ai-vertical-flow.md`
- `info/.notes/localization-lab-marketplace-flow.md`
- `info/.notes/localization-lab-plan.md`
- `info/.notes/localization-lab-workflow-snapshots-flow.md`
- `info/localization-design/compass_artifact_wf-1a9bddba-6b12-572f-bac0-fff4c685ba4c_text_markdown.md`
- `info/localization-design/project-a-ext-model-economics-matrix.md`
- `info/localization-design/unity_localization_project_technical_dossier.md`

### → `06-chatbot-auth-and-ai-integration-history.md` (9 files)
- `info/.notes/SESSION-2026-09-AI-chatbot-planning-and-auth-build.md`
- `info/.notes/Chatbot-implementation/references/neuralascent-auth-and-chat-gemini-prompts.md`
- `info/.notes/Chatbot-implementation/references/combined_all_documentation.md`
- `info/.notes/Chatbot-implementation/references/neuralascent_ai_platform_todo_tracker.md`
- `info/.notes/Chatbot-implementation/references/neuralascent-chatbot-hld.md`
- `info/.notes/Chatbot-implementation/references/neuralascent-chatbot-hld-python.md`
- `info/.notes/Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-JAVA-LANGCHAIN.md`
- `info/.notes/Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-dotnet-Semantic-Kernal.md`
- `info/.notes/Chatbot-implementation/architecture-notes/unity_localization_project_technical_dossier.md`

### → `07-ai-learning-agent.md` (11 files)
- `info/.notes/ADR-001-orchestration-framework-choice.md`
- `info/.notes/ai-learning-agent-ARCHITECTURE.md`
- `info/.notes/ai-learning-agent-BUILD-TRACKER.md`
- `info/.notes/ai-learning-agent-SESSION-HANDOFF.md`
- `info/.notes/SESSION-2026-09-15-teaching-style-and-phase1-kickoff.md`
- `info/.notes/SESSION-2026-09-19-langgraph-scaffold-and-adr.md`
- `info/.notes/SESSION-2026-09-20-langfuse-integration-and-docker-compose.md`
- `info/.notes/SESSION-2026-09-21-ingestion-pipeline-phase-a-and-provider-decisions.md`
- `info/.notes/ai-copilot-session-summary-for-opus5.md`
- `info/.notes/copilot-week1-2-design-overview.md`
- `info/.notes/copilot-week1-2-fastapi-foundation-prompt.md`

### → `08-python-migration-and-study-plans.md` (14 files)
- `info/01-project-labs-rebuild-guide.md`
- `info/02-azure-certification-plan-2026.md`
- `info/03-fde-ai-self-study-plan.md`
- `info/04-fde-curriculum-tracker.md`
- `info/curriculum-modernization-tracker.md`
- `info/java_aws_migration_tracker.md`
- `info/.notes/Chatbot-implementation/java-migration/Stage-1/neuralascent_java_first_rebuild_and_migration_roadmap.md`
- `info/.notes/Chatbot-implementation/java-migration/references/85_DAY_LOCKED_IN_PLAN.md`
- `info/.notes/Chatbot-implementation/java-migration/references/AGGRESSIVE_30_DAY_PLAN.md`
- `info/.notes/Chatbot-implementation/java-migration/references/CLARITY_YOUR_REAL_SCOPE.md`
- `info/.notes/Chatbot-implementation/java-migration/references/INTERVIEW_PREP_ROADMAP_85DAYS.md`
- `info/.notes/Chatbot-implementation/java-migration/references/START_TOMORROW_CHECKLIST.md`
- `info/.notes/Chatbot-implementation/java-migration/references/neuralascent-ai-platform-todo-tracker-merged.md`
- `info/.notes/Chatbot-implementation/java-migration/references/neuralascent-java-migration-learning-plan.md`

### Deleted as duplicates / noise (content preserved elsewhere or byte-identical)
- `info/.notes/Chatbot-implementation/references/neuralascent-auth-and-chat-gemini-prompts.md.orig` (same prompt package with unresolved stash-conflict markers; §2 of file 06 keeps the unique review text).
- Within the lists above: `combined_all_documentation.md` (5.8 MB concatenation of every doc), the byte-identical HLD copies (`references/neuralascent-chatbot-hld.md` = Java HLD, `references/…hld-python.md`, `architecture-notes/…dotnet-Semantic-Kernal.md`),
  the unmerged `neuralascent_ai_platform_todo_tracker.md` (verified: zero lines that the merged tracker lacks), and the duplicate `unity_localization_project_technical_dossier.md`.

## Deliberately NOT merged or deleted (left exactly as they were)
- **Lesson source material (never touched):** `info/.notes/scaler-raw-notes/**`, `info/.notes/input-notes/**`, `info/.notes/final-notes/**`, `info/.notes/scaler-dump/**` (zips/images) — the user did not confirm whether raw notes should be folded in; default = leave. Also `info/AI-helper/**` (transcripts + class zips), `info/downloaded-*`, all PNG/PDF/ZIP/image assets, `info/images-newdesign/*.png`, `info/localization-design/images/`.
- **Authored FDE lesson source + its status tracker:** `info/.notes/fde-lessons/**` (27 phase `-content.md` files ≈ 3 MB of lesson text, 27 `-prompt.md`, `phase-0-…-switch-prompt.md`, and `STATUS.md`, the index for them). Summarised in `02-…`; left in place as authored source.
- **Living templates / referenced files:**
  - `info/.notes/Neuralascent_Master_Reference_Guide_Updated.md` — cited by `CLAUDE.md`; the authoring contract (summarised in `02-…` §3).
  - `info/.notes/Neuralascent_Local_LLM_Ingestion_Prompt.md` — the paste-ready ingestion template that pairs with the guide.
  - `info/local-llm-content-pipeline/02-local-llm-prompts.md` — master system prompt, per-chapter template, MCQ/exercise prompts, self-review rubric (its header links to the deleted `00`/`01` were repointed to `info/history/`).
  - `info/.notes/Chatbot-implementation/references/neuralascent-chatbot-hld-dotnet.md` — cited by `CLAUDE.md`.
  - `info/.notes/Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-python-LangChain.md` — the one full-detail Python HLD kept (see file 06 §4).
- **Non-Markdown tools in `info/.notes/`:** `cleanup-redundant-expanded-modules.sql`, `verify-new-exercises.sh`.
- `info/.raghu-personal/README.md` (personal drop-folder readme).
- Everything outside `info/` (code, exercises, `CLAUDE.md`, `.agents/**`, `task_tracker.md`, `docs/**`, `parse_tasks.py`, …).

## Caveats
- `parse_tasks.py` (repo root) opens `info/04-fde-curriculum-tracker.md`, now deleted; the checklist is in `08-…` §B.2 and in git. The script is a one-off generator whose output (`FdeSeedData.cs`) already exists.
- Links inside the *kept* files that point at deleted siblings (e.g. `Master Reference Guide` mentions of companion docs) now resolve to this history; consult the merge map.
- Dates: prompt files were bulk-imported into git on 2026-09-05; the dates in file 02's table are content dates where known.
- This history reports **verified** state where it could be checked against source (notably `ai-agent/`, `App.jsx`, deploy scripts); items that could not be verified are marked as such.
