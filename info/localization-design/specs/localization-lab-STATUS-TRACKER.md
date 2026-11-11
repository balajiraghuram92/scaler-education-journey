# Localization Lab — Status Tracker

> Single source of truth for "what's built, what's pending, what changed."
> Update this file whenever a phase/bug/decision changes state — don't let
> it drift out of sync with reality the way the earlier design docs did with
> the running code.

Last updated: 2026-09-05

---

## 0. Architecture pivot (2026-09-05) — READ THIS FIRST

**The hand-written AI boundary (MT Optimize, QPS Scoring, Auto-Routing) will
be implemented in Python + FastAPI, not C#**, because this is being built as
an AI-engineering portfolio piece for AI-role job applications — a Python/
FastAPI AI service is the more relevant skill demonstration than C# stubs.

This means:
- The existing C# stub classes (`MtOptimizeService`, `QpsScoringService`,
  `AutoRoutingService` in `api/Services/Localization/`) stay as placeholders
  that throw `NotImplementedException` — **they will NOT be filled in**.
  Instead, a new **Python FastAPI microservice** will own this logic, and the
  .NET `WorkflowService` will be updated to call out to it over HTTP instead
  of calling the local C# stubs.
- Full proposed architecture, endpoint contracts, and the suggestion/accept/
  reject/human-review UX flow are specified in
  [localization-lab-ARCHITECTURE-AND-WORKFLOW.md](localization-lab-ARCHITECTURE-AND-WORKFLOW.md).
- **Nothing has been implemented yet for this pivot** — it's design-only per
  the user's explicit request ("do not do it now, I want to be part of it").
  The user will hand-write the FastAPI service themselves, with Claude
  available to produce an interface-contract spec to code against on request.
- **LLM provider decided (2026-09-05): self-hosted open-weight model on the
  user's own GPU, served via vLLM** — not a commercial API (ruled out
  AWS Bedrock, Azure OpenAI, Claude/OpenAI direct). See architecture doc
  Part F.5 for the serving architecture and model-selection considerations.
- **`GoogleTranslateProviderService` stays in .NET, unchanged** — real
  Google Cloud Translation Basic/NMT call, kept as the deliberate "Legacy
  MT" baseline stage for a before/after quality comparison against the
  self-hosted LLM stage (Part F.6) — not moved into Python, not faked.

---

## 1. Done and verified (all confirmed live, not just code-reviewed)

### Backend (C# / ASP.NET Core / EF Core / Postgres) — `api/`
- [x] Full data model: 12 entities under `api/Models/Localization/` (projects,
  locales, strings, translations, workflow steps, snapshots, vendors,
  marketplace jobs/bids, ledger entries, provider health)
- [x] EF Core migration applied (`20260905120000_AddLocalizationLab`)
- [x] All 16 services under `api/Services/Localization/`
- [x] All 4 endpoint groups under `api/Endpoints/Localization/`
  (Localization, Marketplace, VendorPortal, ProviderHealth)
- [x] `GoogleTranslateProviderService` — real Google Cloud Translation API
  integration with dev-mode mock fallback (`[MOCK-XX] ...`), implements
  `ITranslationProvider`
- [x] Credit ledger + price-band estimation (`CreditLedgerService`), fixed to
  never produce a degenerate zero-width band
- [x] Seed data: 1 project (`auroraline-hud-v3`), 5 target locales, **~47
  strings** (~964 words — expanded from the original 6-string/15-word demo
  set specifically so Marketplace price bands are grounded in real content),
  3 workflow steps, 3 build snapshots, 5 vendors, marketplace jobs/bids
  across all 5 locale states (Awarded/Open/Not Posted/Submitted/Approved),
  2 provider health rows
- [x] Workflow step update endpoint (`PUT .../workflow/steps/{stepId}`) —
  Trigger/Action dropdowns now persist changes, not just Add/Reorder/Delete/Run
- [x] Hand-written AI boundary stubs (`MtOptimizeService`, `QpsScoringService`,
  `AutoRoutingService`) throw `NotImplementedException` with clear messages,
  and the Workflow run endpoint surfaces this as a real HTTP 501 — **verified
  live**, including after editing a step's action via the new update endpoint

### Frontend (React) — `app/`
- [x] Owner app: Strings tab (table + row drawer, QPS column, dot-track /
  Needs-Review flag), Workflow tab (add/reorder/delete/run/update steps),
  Snapshots tab (cut + read-only manifest drawer), Marketplace tab (locale
  overview + post-to-marketplace + bid review + award)
- [x] Vendor portal (separate shell, no owner nav): Open Jobs board, bid
  submission modal, My Jobs locked-scope workspace
- [x] Provider Health slide-out panel + working Simulate Outage / Resolve
  toggle
- [x] Nav-bar duplication bug fixed (LocalizationShell no longer repeats the
  global `<Layout>` nav's logo/avatar)
- [x] Status-label formatting bug fixed (`SubmittedForReview` →
  "Submitted for Review", etc.) in both owner and vendor views
- [x] Routing wired into `App.jsx`, entry link fixed in `LabProjects.jsx`

### Infra
- [x] `docker-compose.yml` YAML syntax bug fixed (unquoted colon in TOTP key message)
- [x] Full stack verified running end-to-end in WSL2 (migrate → seed → all
  tabs clicked through with real API calls, not just static review)

### End-to-end functional verification log (2026-09-05)
- [x] Strings: edit a translation via the row drawer → saves via real API
- [x] Workflow: ran "Approve" step live (12→2 strings affected on re-run),
  edited an existing step's Action to "Score QPS" via the new update
  endpoint, ran it, got a real 501 with the hand-written-boundary message
  rendered as a UI banner
- [x] Snapshots: matches seed data exactly, drawer shows full manifest
- [x] Marketplace: posted zh-CN live (created a real job with computed
  47 strings / 964 words / 140–185 credit band), awarded Kenji Sato's bid
  on ja-JP ("Job successfully awarded to Kenji Sato!")
- [x] Provider Health: Simulate Outage flipped Google MT to Circuit: Open /
  87.5% error rate, Resolve brought it back to "All Providers Operational"

---

## 2. Known, accepted gaps (not blocking, documented on purpose)

- Vendor "My Jobs" inline edit is a lighter-weight interaction than the
  owner's full row drawer (per original build prompt — intentional, not a bug)
- Vendor rating changes over time, bid withdrawal — explicitly out of scope
  (per the locked marketplace flow design)
- No per-project configurable QPS threshold UI — hard-coded `>= 70` display
  logic only
- Continuous/CDN delivery mode, visual node-canvas Orchestrator builder, real
  vendor auth/signup, real multi-tenant DB partitioning — all explicitly out
  of scope per the locked architecture (see `localization-lab-plan.md` §11)

---

## 3. Pending — the actual remaining work

### 3.1 Python FastAPI AI service (hand-written by the user)
- [ ] Design finalized in [localization-lab-ARCHITECTURE-AND-WORKFLOW.md](localization-lab-ARCHITECTURE-AND-WORKFLOW.md)
      Part F — **read this before starting**
- **Decided:** self-hosted open-weight model on the user's own GPU, served
  via **vLLM** (OpenAI-compatible endpoint), called by FastAPI — a 3-process
  architecture (.NET → FastAPI → vLLM), not a commercial LLM API
- **Decided:** `GoogleTranslateProviderService` stays in .NET as Stage 1
  ("Legacy MT") — real Google Cloud Translation Basic/NMT call, effectively
  free at this project's content scale, kept as-is rather than faked
- [ ] Model selection/testing across the 5 target locales (candidates:
      Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3 —
      ja-JP/zh-CN quality needs real evaluation, not a default pick)
- [ ] vLLM serving setup (quantization choice per actual GPU VRAM)
- [ ] Scaffold the FastAPI service (not started)
- [ ] **New DB field**: `LocalizationTranslation.RawMtText` (nullable) — holds
      Stage-1 Legacy MT output separately from `TargetText`, so the
      before/after comparison has something real to diff against (needs a
      small EF Core migration — not yet added)
- [ ] Prompt construction for MT Optimize (glossary-aware post-edit pass,
      reads `RawMtText` → writes `TargetText`) — **hand-written**
- [ ] Prompt construction + rubric for QPS scoring (LLM-as-judge) — **hand-written**
- [ ] Response parsing/validation for both LLM calls — **hand-written**
- [ ] Auto-Routing decision logic (QPS vs. threshold → Approved/Needs Review) — **hand-written**
- [ ] .NET `WorkflowService` updated to call the FastAPI service via HTTP for
      the three Phase-3 actions, replacing the local stub calls
- [ ] Frontend: "Legacy MT" read-only comparison box in the Strings drawer
      (shown only when `RawMtText` is non-null) — small, not yet built
- [ ] Integration test: full pipeline (Legacy MT → MT Optimize → QPS
      Score → Auto-Route → Approved or Needs Review) working end-to-end,
      with the before/after QPS delta visible as the demo's core artifact

### 3.2 Frontend follow-ups once the AI service is real
- [ ] Verify the QPS column and Needs-Review flag actually populate from real
      scores instead of only seed data
- [ ] "Show: Needs Review only" quick filter on the Strings table (designed,
      not yet built — see `localization-lab-ai-vertical-flow.md` §3.1)
- [ ] Tie Needs-Review strings into the Marketplace flow as the "send to
      human review" destination (see architecture doc — this is the "separate
      list sent to human review" loop the user asked about)

### 3.3 Final coherence pass
- [ ] Once the AI service is real, walk the full demo narrative end-to-end:
      AI-translate → QPS score → Auto-Route, compared against a
      Marketplace-translated locale, with Provider Health/Simulate Outage as
      the reliability story — confirm it reads as one coherent system for an
      interview, not disconnected features

---

## 4. File index

| File | Purpose |
|---|---|
| `localization-lab-plan.md` | Original architecture + phase roadmap (Phases 1-3) |
| `localization-lab-marketplace-flow.md` | Phase 2.5 vendor marketplace full spec |
| `localization-lab-workflow-snapshots-flow.md` | Workflow tab + Snapshots tab UI spec |
| `localization-lab-ai-vertical-flow.md` | Phase 3 UI surface spec (Provider Health, QPS, Needs Review, nav) |
| `localization-lab-BUILD-PROMPT.md` | The single-shot Gemini 3.8 Flash build prompt that produced the current implementation |
| `localization-lab-ARCHITECTURE-AND-WORKFLOW.md` | **New** — full system architecture + Google Translate integration status + proposed suggest/accept/reject/human-review flow + Python FastAPI service design |
| `localization-lab-STATUS-TRACKER.md` | This file |
