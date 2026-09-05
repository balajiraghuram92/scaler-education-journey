# Localization Lab — Architecture Plan

> Portfolio "product-inside-a-product" for Neuralascent, built for a job interview
> (target: end of January 2027). Rebuilds the architecture described in the user's
> Unity Enterprise Services Localization dossier (`~/Downloads/unity_localization_project_technical_dossier.md`),
> using Phrase's real product taxonomy as the base blueprint, with Smartling-style
> AI routing and the Unity build-locked delivery model integrated on top.
>
> Workflow: Claude never writes code for this feature (per CLAUDE.md). Claude researches,
> designs, and produces copy-paste-ready prompts. Gemini produces concept/design images.
> Gemini 3.8 Flash writes all actual backend (`api/`) and frontend (`app/`) code.

## Where it lives

- Route: `/lab-projects/localization` (and sub-routes), embedded inside the existing
  Neuralascent app — not a separate deployment.
- Entry point already stubbed: [app/src/pages/LabProjects.jsx](../../app/src/pages/LabProjects.jsx)
  has a dev-fixture card literally named "Lab B — Unity Localization & Asset Delivery
  Platform" (lines 24-31) — the new page links out from that card.
- Backend conventions to match: minimal-API endpoints in `api/Endpoints/*.cs`
  (see `ExerciseEndpoints.cs`), flat models in `api/Models/*.cs`, services in
  `api/Services/*.cs`, EF Core + Npgsql via `StudyTrackerContext`.
- Frontend conventions to match: pages in `app/src/pages/`, API calls via the
  `api.*` namespace in `app/src/api/client.js`, inline styles using the existing
  CSS custom properties (`--color-sage #2C5E55`, `--color-parchment-card #FFFFFF`,
  `--color-ink #1F2937`, `--color-ink-muted #6B7280`, `--color-border-subtle #E2DDD5`,
  `--font-serif "Newsreader"`).
- Reuse candidate: `api/Services/LlamaApiClient.cs` (from the chatbot integration) —
  the LLM provider adapter pattern for Phase 3 should follow its shape rather than
  inventing a new one.

## Locked architecture decisions (all confirmed with the user)

1. **Delivery model: Build-Locked only.** No continuous/CDN runtime-sync mode.
   Mirrors the dossier's actual differentiator — Unity's enterprise customers
   (automotive HUD, industrial embedded, arcade cabinet) need "what shipped is what
   was tested," not silent post-release drift. Nothing is "live" until a **Build
   Snapshot** is cut: `{ sourceRevision, localizationRevision, config } → immutable
   manifest export`.
2. **AI vertical: full Quality Technologies stack**, modeled on Phrase's actual
   product, not a bare API wrapper:
   - **MT Optimize** — a distinct post-edit LLM pass: takes raw MT/AI output +
     project glossary + style guide + context, polishes it. Glossary-grounding
     lives HERE as its own pipeline stage, not baked into the first translate call.
   - **QPS (Quality Performance Score, 0-100)** — a second, independent LLM call
     that scores an existing translation against MQM-style dimensions (accuracy,
     fluency, terminology, tone). This is an LLM-as-judge pattern, architecturally
     separate from generation.
   - **Auto-Routing** — a per-project configurable QPS threshold; below it, a
     segment routes to a human "Needs Review" queue; above it, auto-advances to
     Approved. (This is the same pattern Smartling calls confidence-based routing.)
3. **Demo reliability — a real Tier-1 feature, not just a fallback:**
   - Real API calls are the default path (~80% of the time in practice).
   - A **Provider Health panel** tracks P50/P99 latency, error rate, and
     circuit-breaker state per provider (Google MT vs LLM), live.
   - A **"Simulate Provider Outage"** control lets the user trigger the failure
     path on demand during an interview, rather than hoping for a real failure.
   - On real failure (or simulated outage), the app falls back to a **seeded demo
     tenant** rather than a single canned response.
   - **Seeded demo tenants:** one shared `DemoStringPool` (source strings +
     glossary terms), composed differently per tenant so N full datasets don't
     need hand-authoring. Default tenants (fictional names, deliberately echoing
     the dossier's real Unity enterprise customer categories): *Auroraline
     Automotive* (HUD), *Ferrix Industrial Systems* (embedded controls),
     *Pinnacle Arcade Co.* (cabinet), plus 2 more generic SaaS/mobile tenants for
     contrast. A tenant switcher/search sits in the top nav alongside the
     live/fallback toggle.
4. **Sequencing: depth-first.** Finish Tier 1 (below) completely before starting
   Tier 2/3 polish. Nothing gets built shallow-and-wide first.
5. **Orchestrator workflow engine: config-driven, not a visual node canvas.**
   Same Trigger → Action semantic model as Phrase Orchestrator (linear/parallel
   action lists per project), but expressed as a structured settings UI (ordered
   steps, dropdowns, conditions) rather than a drag-and-drop graph editor. A real
   node-canvas UI (e.g. via React Flow) was explicitly rejected as too much
   frontend risk for a depth-first plan — may revisit as a Tier-3 polish pass if
   time allows before January.

## Base blueprint — modeled on Phrase's real product taxonomy

| Our module | Phrase's real equivalent | Reference |
|---|---|---|
| Project/string management | Phrase Strings (key-based, file-derived tags, locale-scoped, branch-aware) | phrase.com/platform/strings |
| Translation/review UI | Phrase TMS CAT Editor | support.phrase.com Strings Connector docs |
| Workflow engine | Phrase Orchestrator (Trigger → Action, linear/parallel) | phrase.com/platform/orchestrator |
| Confidence routing | Phrase QPS + Auto-Routing | phrase.com Quality Technologies blog |
| LQA scoring | Phrase Auto LQA (MQM 2.0-based) | phrase.com/phrase-quality-technologies |
| Glossary-aware post-edit | Phrase MT Optimize | phrase.com/phrase-quality-technologies/auto-lqa |

Full competitive research (Lokalise, Crowdin, Smartling feature comparisons,
enterprise RBAC/audit-log patterns, CI/CD continuous-localization patterns) was
done in-conversation; Phrase was selected as the base after that comparison
specifically because its module taxonomy (Strings / TMS / Orchestrator / Quality
Technologies) maps cleanly onto a buildable phase plan, and because its QPS +
Auto-Routing + MT Optimize split gives a cleaner separation of concerns than a
generic composite would.

## Phase roadmap (final, supersedes the earlier 3-phase draft)

**Phase 1 — Foundation + Workflow Engine + Build Lock** (no external providers yet)
- Strings module: projects, keys, tags, locales, manual translation entry, status
  states (New → Translated → Reviewed → Approved)
- Orchestrator (config-driven): per-project ordered pipeline of Trigger → Action
  steps; Phase 1 actions are manual only (Mark Translated, Send to Review, Approve)
  — built as the extensible backbone so Phase 2/3 add new action types into the
  same engine rather than bolting on separately
- Build Snapshot: "Cut Build Snapshot" terminal action + immutable manifest export
  (mirrors dossier §28's `sourceRev + localizationRev + config → deterministic
  build` model)

**Phase 2 — Automated MT + Credits**
- Google Translate provider wired in as a new Orchestrator action type
  ("Auto-Translate via Google MT")
- Character-based credit/cost estimator (estimate-before-commit, running ledger)
- Provider Health panel scaffolding begins (latency/error tracking for the one
  real external provider now in play)

**Phase 2.5 — Vendor Marketplace** (confirmed 2026-09-05 — second interview
centerpiece, parallel human-translation track alongside AI/MT)
- Full spec: [localization-lab-marketplace-flow.md](localization-lab-marketplace-flow.md)
- Depends only on Phase 1 (Orchestrator action framework) and Phase 2 (credit
  ledger) — does NOT depend on Phase 3's QPS/MT Optimize
- New Orchestrator action type: "Post to Marketplace" (per project+locale)
- Vendor roster (seeded), MarketplaceJob + Bid entities, full job/bid state
  machine (Draft → Open → Awarded → InProgress → SubmittedForReview →
  Approved/NeedsRevision → Closed)
- Owner-side: Marketplace tab (locale overview), Post-to-Marketplace drawer,
  side-by-side bid review list; submission review reuses the existing Strings
  table/drawer filtered by locale
- Vendor-side: separate locked-scope portal (vendor picker, Open Jobs board,
  bid submission form, "My Jobs" workspace scoped to only the awarded job's
  strings — no Orchestrator/Snapshots/other-locale visibility)
- Settlement via the same credit ledger as AI/MT, tagged `source: Marketplace`
  vs `source: AI`, enabling a direct cost-comparison story
- Must be complete (depth-first) before starting Phase 3

**Phase 3 — AI Vertical** (the interview centerpiece)
- LLM provider adapter (reuse `LlamaApiClient.cs` pattern) as another Orchestrator
  action type
- MT Optimize pass (glossary + context-aware post-edit)
- QPS scoring pass (Auto LQA / LLM-as-judge, MQM-style dimensions)
- Auto-Routing (QPS threshold → Needs Review queue)
- Token-based pricing added to the credit engine (character-based vs token-based
  side by side)
- Provider Health panel completed for both providers + Simulate Outage control
- Seeded demo tenants + live/fallback toggle + tenant switcher

**Explicitly deferred / cut:**
- Continuous/CDN runtime delivery mode
- Full visual node-canvas workflow builder (Tier-3 stretch only)
- Real multi-tenant DB partitioning, real SSO/SCIM wiring, pseudo-localization
  tooling, in-context live-preview overlay, real fuzzy-match TM engine — these
  are "convincing surface" items (Tier 3), not to be built for real unless time
  remains after Phase 3 is solid.

## Hand-written AI boundary (Phase 3) — locked

Everything in Phases 1-2 and most of Phase 3 is built via the Gemini 3.8 Flash
prompt workflow. But the actual AI logic in Phase 3 must be **hand-written by
the user**, not Gemini-generated, specifically so it's defensible in a live
interview. The line:

**Hand-write (the user writes these personally):**
1. Prompt construction for all three AI calls — the translation-generation
   prompt, the MT Optimize (glossary-aware post-edit) prompt, and the
   QPS/Auto-LQA scoring prompt (the rubric itself).
2. Response parsing/validation — turning raw LLM text into structured
   `{translatedText, confidence}` / `{score, flaggedIssues[]}`, including
   malformed-output handling.
3. The routing decision logic — comparing QPS score against the per-project
   threshold to decide Approved vs. Needs Review.
4. The provider abstraction interface itself (`ITranslationProvider` /
   `IQualityScorer` shape that Google MT and the LLM both implement).

**Gemini can write everything else**, including all of Phase 1/2, the
Orchestrator's generic step-execution engine, Google Translate integration
(deterministic, no judgment involved), credit math, Provider Health
instrumentation plumbing, seeded demo tenants, all UI, and the thin
endpoint/service wrapper that calls into the hand-written provider interface.

Claude's offer still open: once the user is ready to write the hand-written
slice, Claude can produce a precise interface-contract spec (method
signatures, expected shapes) to code against — spec only, or spec + review
after a first pass — but will not write that code itself.

## UI/UX design — locked visual spec (as of 2026-09-05)

Grounded in the live site's actual tokens (not assumed): page bg `#F8F6F0`,
card `#FFFFFF`, sage accent `#2C5E55`, ink `#1F2937`, muted ink `#6B7280`,
border `#E2DDD5`, serif `Newsreader`. Verified against
[info/images-newdesign/updated_homepage.png](../images-newdesign/updated_homepage.png)
and [Study-tracker.png](../images-newdesign/Study-tracker.png), and real nav
chrome from [Navbar.jsx](../../app/src/components/Navbar.jsx). A known Gemini
failure mode was caught directly in this repo's own reference archive —
[Final-Design.png](../images-newdesign/final-references/Final-Design.png) has
visibly garbled body-text paragraphs — so every image prompt for this feature
carries an explicit "short labels only, no paragraphs" guardrail.

Design converged through two rounds: (1) 10 divergent in-universe metaphor
concepts (Language Atlas, Translation Ledger, Dispatch Log, Locale Shelf,
Compositor's Galley, Reading Room, Editor's Proofing Desk, Glossary Desk,
Correspondence Log, Foreign Rights Dossier — all sharing identical
colors/fonts/nav, varying only metaphor/layout), user ran them through Gemini
and cropped/highlighted the winning elements from four of them; (2) a
confirmed hybrid, then 10 finishing-detail variations (tab style, drawer
style, dot-track style, entry numbers, action-button style) on that locked
hybrid; user reviewed and gave three corrections.

**Final locked spec:**
- **Base structure:** Translation Ledger's ruled table (no cards), numbered
  Workflow Settings rows, "Closing Entries"-style Build Snapshot table.
- **Tab navigation:** Foreign Rights Dossier's `Strings | Workflow |
  Snapshots` tab bar at the top of every screen (maps onto the three routes:
  `/lab-projects/localization/:projectId`, `.../workflow`, `.../snapshots`).
- **Status indicator:** Dispatch Log's 4-dot progress track **replaces** the
  ledger's checkbox/tally marks entirely — one indicator per row, plus the
  current stage's name as a single-word label beneath the track (unlabeled
  dots were tried and rejected — not legible to a first-time viewer).
- **Row detail:** Editor's Proofing Desk's two-column manuscript view, as a
  **row-detail slide-over drawer** (not a separate page) opened by clicking a
  table row. Drawer heading is the string's real **Key** field (monospace),
  NOT the project name — corrected after the first mockup showed the project
  name repeated pointlessly in the drawer. Drawer also repeats the Stage
  dot-track + label so status is visible while editing. Source (read-only) and
  Target (editable) as two stacked boxes with a thin sage divider, "Save &
  Next" button at the bottom.
- **Explicitly dropped:** a margin column of checkmark/circle "proofing marks"
  next to Source/Target — this was a leftover from Proofing Desk's original
  *multi-row* checklist meaning (one tick per string in a list), which didn't
  translate into a *single-string* detail view and rendered as meaningless
  decorative ticks. No such element in the final spec; the Stage indicator
  already covers status.
- **Tab bar style: underline** (not segmented-pill) — plain understated
  underline under the active tab, matching the ledger/editorial no-cards
  aesthetic rather than a rounded-pill SaaS look.
- **Drawer style: dimmed overlay** (not split-view push) — the drawer slides
  over a dimmed table rather than pushing the table aside. Standard modal
  pattern, lower frontend risk, consistent with the earlier call to reject
  the node-canvas Orchestrator builder for the same reason.
- **Action-button style: icon-only** (not text pill) — compact icon buttons
  with tooltips for Save & Next, Approve, Cut Build Snapshot, etc.

All three finishing-detail choices are now locked (confirmed 2026-09-05).

## Deliverables produced so far

- Phase 1 Gemini 3.8 Flash build prompt (Strings CRUD + config-driven
  Orchestrator backbone + Build Snapshot export) — written in full, matching
  api/Endpoints, api/Models, api/Services, StudyTrackerContext conventions.
  **Now superseded on the frontend side**: it predates the tab-bar/dot-track/
  slide-over UI convergence above, so `ProjectDetail.jsx`,
  `WorkflowSettings.jsx`, `BuildSnapshots.jsx` need re-speccing against the
  locked visual spec before being used to build. The backend portion (models,
  endpoints, service logic, migration) is unaffected by the UI convergence and
  still stands as written.
- 20 total Gemini concept-image prompts across two rounds (10 divergent
  metaphors, then 10 finishing-detail variations on the locked hybrid) — all
  given directly in chat, not saved to a file yet.

## Vendor marketplace (added 2026-09-05)

A second parallel track — a freelance-style vendor marketplace, reconstructing
the real "developers post work, translators bid per-language" model from the
Unity ES project — is now specced in full in
[localization-lab-marketplace-flow.md](localization-lab-marketplace-flow.md).
Entities, job/bid state machines, owner-side screens, and a separate
locked-scope vendor portal are all defined there. **Confirmed 2026-09-05**: it now sits as Phase 2.5 in the roadmap below,
after Google MT + Credits and before the AI Vertical. No mockups exist for it
yet — see the flow doc's §8 for the 6 screens still needed.

## Remaining Phase 1 screens + Phase 3 UI surface (added 2026-09-05)

Two more design docs now cover the screens that weren't specced yet:
- [localization-lab-workflow-snapshots-flow.md](localization-lab-workflow-snapshots-flow.md)
  — the Workflow tab (config-driven Orchestrator, up/down reorder, inline
  last-run status per step) and the Snapshots tab (whole-project-only Build
  Snapshot cuts, row-detail drawer with the immutable manifest).
- [localization-lab-ai-vertical-flow.md](localization-lab-ai-vertical-flow.md)
  — Phase 3's UI surface: a Provider Health slide-out panel (with Simulate
  Outage) from a top-nav icon, a QPS column in the Strings table, Auto-Routing's
  "Needs Review" state replacing the dot-track (not a 5th dot), and a tenant
  switcher + live/fallback toggle added to the **global** top nav now, ahead of
  Phase 3 actually being built.

**Important:** the nav-bar addition (tenant switcher, live/fallback toggle,
Provider Health icon) means the already-approved Strings/drawer reference
image is superseded on that one point — every owner-side screen mocked from
here on needs the new nav cluster, and the original Strings image should
eventually be regenerated to match before it's used as a build reference.

## Status

Architecture (backend) fully locked. **Visual design now fully locked** —
hybrid base + three corrections + three finishing-detail choices, all
confirmed. Immediate next steps once a new session picks this up:
1. Generate one final single locked reference image incorporating the full
   spec above (ruled table, underline tabs, labeled dot-track, dimmed-overlay
   drawer with Key heading and no margin ticks, icon-only buttons).
2. Re-write the frontend portion of the Phase 1 build prompt to match the
   locked visual spec (tab bar instead of separate nav links, dot-track
   component, overlay drawer with Key heading, icon-only buttons, no margin
   ticks).
3. User then runs the updated Phase 1 prompt through Gemini 3.8 Flash to
   actually build it, before the Sept 13, 2026 usage-bonus window closes.
4. After Phase 1 is built and smoke-tested, move to Phase 2 (Google
   Translate + credits), then Phase 3 (AI vertical — partly hand-written per
   the boundary above).
