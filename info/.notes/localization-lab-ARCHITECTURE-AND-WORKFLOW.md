# Localization Lab — Full Architecture & Workflow Reference

> Read-only design/reference document. **Nothing described in Parts E-G (the
> eval harness, semantic cache, glossary grounding, or the Python FastAPI AI
> service) has been implemented.** This exists so you can understand every
> flow end-to-end and defend it in an interview, and so you have a concrete
> spec to hand-write against when you're ready — not as something Claude
> will build.

---

## Part 0 — What this project is actually for

This feature is not a generic app add-on. It is the working implementation
of **"Idea 1: Translation Cost-Governance Gateway with Quality Evaluation"**
from your India AI-role transition playbook — the highest-interview-leverage
localization idea in that document, chosen specifically because it lets you
claim a real production analog (your Rythmos/Unity localization work) with a
measured before/after, built on the exact competency cluster your target
interviews test: **retrieval-adjacent provider orchestration, evaluation
design, cost governance, and a baseline→intervention→delta narrative.**

Concretely, this doc is written so that when it's done you can say a
specific, numbers-backed sentence in an interview — not "I built a
translation app," but something like:

> *"On a 40-case golden set spanning five locales, naive single-provider
> Legacy MT scored 0.61 COMET-Kiwi and 58/100 on my own LLM-judge rubric.
> Adding a self-hosted glossary-aware refinement pass raised that to 0.87
> COMET-Kiwi and 89/100, cut per-string cost by using semantic caching on
> repeated UI strings, and routed only the bottom 12% of cases to human
> review instead of the whole batch."*

Every design choice below is made to make that sentence true and defensible,
not just to make the feature "work." Where the playbook names a specific
tool or metric (COMET-Kiwi, golden eval set, semantic caching, glossary
adherence, cost-per-resolved-query), this doc uses that exact vocabulary
rather than inventing custom equivalents — using the terms the market
actually uses is itself part of the interview signal.

---

## Part A — System architecture, today

```
┌─────────────────────────────┐        ┌──────────────────────────────┐
│  React Owner App             │        │  React Vendor Portal          │
│  (app/src/pages/Localization)│        │  (app/src/pages/Localization/ │
│  Strings / Workflow /        │        │   Vendor)                     │
│  Snapshots / Marketplace     │        │  Open Jobs / Bid / My Jobs    │
└───────────────┬───────────────┘        └───────────────┬────────────────┘
                │  fetch() via app/src/api/client.js (api.localization.*, api.vendorPortal.*)
                │  JSON over HTTP, x-api-key header
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ASP.NET Core Minimal API  (api/, C# / .NET 8)                       │
│  ─────────────────────────────────────────────────────────────────  │
│  Endpoints (api/Endpoints/Localization/*.cs)                         │
│    LocalizationEndpoints · MarketplaceEndpoints ·                    │
│    VendorPortalEndpoints · ProviderHealthEndpoints                   │
│         │  route handlers, DI-injected services, RFC7807 Problem     │
│         │  responses on error                                       │
│         ▼                                                            │
│  Services (api/Services/Localization/*.cs)                           │
│    LocalizationProjectService · LocalizationStringService ·          │
│    WorkflowService · SnapshotService · CreditLedgerService ·         │
│    MarketplaceService · VendorPortalService · ProviderHealthService  │
│    GoogleTranslateProviderService (implements ITranslationProvider)  │
│    MtOptimizeService / QpsScoringService / AutoRoutingService        │
│      → currently STUBS, throw 501 (see Part D/E/F)                   │
│         │  EF Core (DbContext: StudyTrackerContext)                  │
│         ▼                                                            │
│  PostgreSQL 16  (localization_* tables — pgvector available for      │
│                   the semantic cache, see Part E.2)                  │
└─────────────────────────────────────────────────────────────────────┘
                │
                │  outbound HTTPS
                ▼
┌─────────────────────────────┐
│  Google Cloud Translation    │   ← real external API call, wrapped by
│  API (v2, Basic/NMT tier)    │     GoogleTranslateProviderService
└─────────────────────────────┘
```

**Tech stack, named precisely (for interview language):**
- Frontend: React 18, client-side routing via `react-router-dom`, no state
  library (local component state + `fetch` via a thin API client wrapper),
  inline styles driven by CSS custom properties (design tokens)
- Backend: ASP.NET Core **Minimal APIs** (not MVC controllers) — route
  groups (`MapGroup`), typed request/response DTOs as C# `record` types,
  dependency-injected scoped services
- ORM: **Entity Framework Core 8** with the Npgsql provider, code-first
  migrations
- Database: **PostgreSQL 16** — already the right substrate for a semantic
  cache via the **pgvector** extension, no new infrastructure needed (the
  same point your playbook makes about Project A's RAG tutor applies here)
- Auth on the API surface: a single shared `x-api-key` header check
  (middleware in `Program.cs`) — not per-user auth; this feature doesn't use
  the site's JWT/user auth system at all, it's a flat API-key-gated surface
- Containerization: Docker Compose, separate `api`, `app` (nginx-served
  static build), and `database` services — the FastAPI AI service (Part F)
  and vLLM model server become two more services in this same compose file

---

## Part B — Data model

### B.1 Existing (built and verified)

```
LocalizationProject 1───* LocalizationLocale
        │
        1───* LocalizationString 1───* LocalizationTranslation (one per locale)
        │
        1───* WorkflowStep
        │
        1───* BuildSnapshot 1───* BuildSnapshotLocaleCount
        │
        1───* MarketplaceJob 1───* MarketplaceBid *───1 Vendor
        │
        1───* LedgerEntry (source: "AI" | "Marketplace")

ProviderHealthSnapshot — standalone, one row per provider (not project-scoped)
```

Key fields worth knowing cold:
- `LocalizationTranslation.Stage`: `"New" → "Translated" → "Reviewed" → "Approved"`
- `LocalizationTranslation.TranslationSource`: `"Manual" | "AI" | "Marketplace"`
- `LocalizationTranslation.QpsScore` (nullable int) and `NeedsReview` (bool) —
  populated only by seed data today; this is what the real pipeline populates
- `MarketplaceJob.Status`: `Draft → Open → Awarded → InProgress → SubmittedForReview → Approved/NeedsRevision → Closed`
- `LedgerEntry.Source = "AI"` is a **valid value with zero real rows** —
  nothing currently writes one (see Part F.4, the cost-governance gap)

### B.2 New entities needed for this design (not yet built)

```
LocalizationTranslation  (extended)
  + RawMtText          (string?, nullable)  — Stage-1 Legacy MT output, kept
                                               separate from TargetText so a
                                               before/after diff is possible
  + RawMtQpsScore       (int?, nullable)     — QPS on the raw MT text, for
                                               the comparison view

GlossaryTerm
  - Id
  - ProjectId (FK)
  - LocaleCode                — which target locale this pair applies to
  - SourceTerm                — e.g. "HUD"
  - TargetTerm                — e.g. approved German rendering
  - Notes (string?)           — usage guidance for the prompt

TranslationCacheEntry           (the semantic cache — pgvector-backed)
  - Id
  - ProjectId (FK)
  - LocaleCode
  - SourceText
  - SourceEmbedding  (pgvector `vector` column)
  - CachedTranslation
  - HitCount           — incremented on every cache hit, itself a metric
  - CreatedAt / LastHitAt

EvalGoldenCase                  (the golden eval set)
  - Id
  - ProjectId (FK)
  - LocaleCode
  - SourceText
  - GoldTranslation             — hand-authored/expert reference
  - Category                    — e.g. "short-label" | "warning-message" |
                                   "idiomatic" | "legal-disclaimer" (mirrors
                                   your playbook's Project A case-tagging)
  - Notes (string?)

EvalRun
  - Id
  - ProjectId (FK)
  - PipelineConfig              — e.g. "legacy-only" | "legacy+optimize" |
                                   "legacy+optimize+cache" |
                                   "legacy+optimize+glossary" — one row per
                                   configuration you measure, so results are
                                   directly comparable across runs
  - RunAt
  - AvgCometKiwi (decimal?)
  - AvgQpsScore (decimal?)
  - GlossaryAdherenceRate (decimal?)
  - PlaceholderPreservationRate (decimal?)
  - CacheHitRate (decimal?)
  - AvgLatencyMs (int?)
  - TotalCostUsd (decimal?)     — real dollar cost for this run, computed
                                   from tokens/characters × known rates

EvalCaseResult                  (per-case detail within a run)
  - Id
  - EvalRunId (FK)
  - EvalGoldenCaseId (FK)
  - ProducedTranslation
  - CometKiwiScore (decimal?)
  - QpsScore (int?)
  - GlossaryAdherenceOk (bool?)
  - PlaceholderPreservedOk (bool?)
  - LatencyMs (int?)

LedgerEntry  (extended)
  + UnitsConsumed (int?)        — characters (Legacy MT) or tokens (LLM stage)
  + UnitType (string?)          — "characters" | "tokens"
  + RealCostUsd (decimal?)      — actual dollar cost, separate from the
                                   existing fictional `Amount` (Marketplace
                                   credits) — see Part F.4 for why these stay
                                   two different units rather than being
                                   forced into one
```

This is a real, non-trivial migration when you build it (7 new/changed
tables), but every field maps directly to something your playbook says gets
tested in interviews — there's no decoration here.

---

## Part C — Complete flow walkthroughs (as built today)

### C.1 Editing a string translation (Strings tab)
1. `LocalizationStrings.jsx` mounts → `api.localization.getStrings(slug, locale)` → `GET /api/localization/projects/{slug}/strings?locale={code}`
2. `LocalizationEndpoints.GetStrings` → `LocalizationStringService.GetStringsAsync` → EF Core query joining `LocalizationString` + `LocalizationTranslation` for that locale (LEFT JOIN semantics: a string with no translation row yet shows `Stage = "New"`)
3. User clicks a row → drawer opens (client-side only, no request) → edits Target text → clicks the save icon
4. `api.localization.updateTranslation(...)` → `PUT .../strings/{stringId}/translations/{localeCode}` → `LocalizationStringService.UpdateTranslationAsync` → upserts the `LocalizationTranslation` row, sets `TranslationSource = "Manual"`, `Stage = "Translated"`

### C.2 Running a Workflow step (Workflow tab)
1. `GET .../workflow` loads all `WorkflowStep` rows ordered by `Order`
2. Clicking a step's Action dropdown → `PUT .../workflow/steps/{stepId}` → `WorkflowService.UpdateStepAsync` persists the new `Action`/`Trigger`/`ConditionExpression`
3. Clicking "Run" → `POST .../workflow/steps/{stepId}/run` → `WorkflowService.RunStepAsync` — a big `switch` on `step.Action`:
   - `"Mark Translated"` / `"Send to Review"` / `"Approve"` — bulk-advance every `LocalizationTranslation` in the project whose `Stage` matches the prior stage
   - `"Auto-Translate via Google MT"` — for every locale, for every string with no/empty target text, calls `ITranslationProvider.TranslateAsync(...)` (currently resolved to `GoogleTranslateProviderService`) and writes the result with `TranslationSource = "AI"`, `Stage = "Translated"`
   - `"Post to Marketplace"` — computes word/string counts, calls `CreditLedgerService.EstimatePriceBandAsync`, creates a `MarketplaceJob`
   - `"Run MT Optimize"` / `"Score QPS"` / `"Auto-Route"` — calls the three stub services, which currently throw → surfaces as **HTTP 501**, rendered by the frontend as an inline banner naming the hand-written boundary

### C.3 Marketplace post → bid → award → approve
1. Owner clicks the megaphone icon on a "Not Posted" locale row → confirm drawer shows a **live-computed** estimate (word count from real `LocalizationString.SourceText`, price band from `CreditLedgerService`)
2. Confirm → `POST .../marketplace/{localeCode}/post` → `MarketplaceService.PostToMarketplaceAsync` creates/updates a `MarketplaceJob` with `Status = "Open"`
3. Vendor portal's Open Jobs board filters jobs by `LocaleCode` against the selected vendor's declared `Languages`, server-side in `VendorPortalService.GetOpenJobsForVendorAsync`
4. Vendor submits a bid → `POST .../vendor/{vendorId}/jobs/{jobId}/bids` → creates a `MarketplaceBid`, `Status = "Pending"`
5. Owner reviews bids side-by-side, clicks Award → `POST .../bids/{bidId}/award` → `MarketplaceService.AwardBidAsync` sets that bid `Awarded`, all siblings `Declined`, job → `Awarded`
6. Vendor works in the locked-scope "My Jobs" workspace (only that job's project+locale strings, enforced server-side — the actual access-control boundary, not just a UI filter), edits target text per string, clicks "Submit for Review" → job → `SubmittedForReview`
7. Owner reviews, clicks "Approve Submission" → `MarketplaceService.ApproveSubmissionAsync` → job → `Approved`, writes a `LedgerEntry` (`Source = "Marketplace"`, `Amount` = the awarded bid's price), bulk-advances translations to `Stage = "Approved"`

### C.4 Build Snapshot cut
`POST .../snapshots` → `SnapshotService.CutSnapshotAsync` → always includes every locale (no partial selection, by design) → generates a `SnapshotIdentifier` like `snap-2026-09-05-a`, counts `Stage == "Approved"` translations per locale into `BuildSnapshotLocaleCount` rows. Immutable — no update/delete endpoint exists on purpose.

### C.5 Provider Health / Simulate Outage
`GET .../provider-health` reads the two `ProviderHealthSnapshot` rows. "Simulate Outage" → `POST .../provider-health/{provider}/simulate-outage` flips `CircuitState` to `"Open"` and bumps `ErrorRatePercent` — a demo control, not real circuit-breaker logic, letting you *demonstrate* the failure path on demand.

---

## Part D — Google Translate integration: current state, precisely

**This already exists and is real** (not a placeholder):

- `api/Services/Localization/GoogleTranslateProviderService.cs` implements
  `ITranslationProvider.TranslateAsync(sourceText, sourceLocale, targetLocale)`
- Calls the real **Google Cloud Translation API v2** REST endpoint with an
  API key from `IOptions<GoogleTranslateOptions>`
- If the key isn't configured: non-Production returns a labeled mock
  (`[MOCK-DE] ...`); Production throws
- Invoked exactly once in the codebase: `WorkflowService.RunStepAsync`'s
  `"Auto-Translate via Google MT"` case
- Does **no** judgment, scoring, glossary-awareness, or context-aware
  polishing — pure deterministic provider integration, which is why it
  stays hand-written-boundary-exempt and stays in .NET (Part F.4)

Today's real flow: `untranslated string → Google Translate API → raw text
stored, Stage = "Translated", TranslationSource = "AI"` — no quality score,
no accept/reject, no routing, and **no cost recorded anywhere** (the ledger
gap — see Part F.4). Parts E-G below are the design to fill all of that.

---

## Part E — The pipeline: eval-harness-first design

Per your playbook's own thesis — *"the measurement-first portfolio... a
baseline→intervention→delta loop"* — the golden eval set and metric runner
are the actual deliverable here, not a side effect of building the pipeline.
Build **E.1 (golden set) and E.4 (metric runner) before** the AI service
itself, so every subsequent piece (MT Optimize, caching, glossary) has
something fixed to measure against from day one, exactly like your Project
A's "the harness is the reusable substrate" pattern.

### E.1 Golden eval set

- **Size**: 30-50 cases to start (your playbook's Project C uses ~50 for
  exactly this reason — enough to be statistically meaningful, small enough
  to hand-author and hand-verify every gold answer yourself)
- **Coverage**: spread across all 5 locales and multiple `Category` tags —
  short UI labels, warning/instructional messages, and at least a few
  longer/idiomatic strings specifically because those are where Legacy MT
  should visibly struggle and the LLM stage should visibly help — the
  contrast *is* the interview story
- **Authorship**: gold translations should be genuinely good — either your
  own competent-enough judgment, or care taken to source them correctly;
  a weak gold set produces a meaningless delta
- Stored as `EvalGoldenCase` rows (Part B.2), reusable across every future
  pipeline change forever — this is a permanent asset, not a one-off script

### E.2 Semantic caching (pgvector)

Named explicitly in your playbook's Idea 1 architecture — avoids
re-translating near-duplicate strings, which matters a lot in a
UI/game-string context (`"Cancel"` appearing 40 times across a project
shouldn't cost 40 translation calls):

- On translate: embed the source text, query `TranslationCacheEntry` via
  pgvector cosine-similarity search against the same `ProjectId`+`LocaleCode`
  scope
- Above a similarity threshold (needs tuning — start conservative, e.g.
  0.95+, since a cache **false hit** silently changes meaning, which your
  playbook explicitly flags as a named failure mode: *"cache poisoning
  meaning drift"*
- On hit: return the cached translation, increment `HitCount`, skip the
  LLM call entirely — this is where the real cost savings and latency
  savings both come from, and `CacheHitRate` becomes one of your `EvalRun`
  metrics
- On miss: translate normally, then write a new `TranslationCacheEntry`

### E.3 Glossary grounding

- `GlossaryTerm` rows define approved source→target term pairs per locale
  (e.g. keep "HUD" untranslated, or enforce a specific automotive-domain
  rendering)
- MT Optimize's prompt includes the relevant glossary terms for that
  locale as explicit constraints
- `GlossaryAdherenceOk` is checked post-hoc per case: did the output
  actually use the approved term? (a deterministic string-match check,
  cheap, matches your playbook's "deterministic checks first, LLM judge
  only on the uncertain tail" cascade philosophy)

### E.4 Metric runner — the actual harness

A repeatable, pytest-style runner (matching your playbook's DeepEval-CI
pattern) that, for a given `PipelineConfig`, runs every `EvalGoldenCase`
through the pipeline and computes:

- **COMET-Kiwi** — reference-free neural MT quality score. This is the
  named, market-recognized metric your playbook calls out specifically
  ("BLEU is dead... the working stack is COMET + LLM-as-judge"). Runs
  locally via the `unbabel-comet` Python package — no external API needed,
  it's a downloadable model, which also means it's free to run repeatedly
- **QPS score** — your existing hand-written LLM-as-judge (unchanged in
  purpose, now paired with COMET-Kiwi instead of standing alone)
- **Glossary adherence rate** — % of cases where required terms appear
- **Placeholder preservation rate** — % of cases where formatting
  tokens/placeholders in the source survive unchanged in the output (a
  named failure mode in your playbook: "LLMs love to mangle `{count}`" —
  worth including even though this demo project's seeded strings don't
  currently use placeholders; add a few golden cases that do, specifically
  to exercise this check)
- **Cache hit rate**, **average latency**, **total cost** — operational
  metrics, not quality metrics, but equally part of the "cost governance"
  story

Each run writes one `EvalRun` row + N `EvalCaseResult` rows. Comparing
`EvalRun` rows across `PipelineConfig` values **is** the baseline→delta
table — no separate analysis tooling needed, it's just a query.

### E.5 The proposed end-to-end pipeline (updated)

```
1. Legacy MT (Google Cloud Translation Basic/NMT — real, exists today)
        │  writes RawMtText, RawMtQpsScore
        ▼
2. Semantic cache check (pgvector) — before calling the LLM stage at all
        │
        ├─ cache hit ──────────────────────────► use cached translation
        │
        └─ cache miss
                ▼
3. MT Optimize (self-hosted LLM, glossary-grounded — hand-written)
        │  writes TargetText; write new TranslationCacheEntry
        ▼
4. QPS Score (self-hosted LLM-as-judge — hand-written) + COMET-Kiwi
   (local model, no LLM call needed)
        │  writes QpsScore
        ▼
5. Auto-Route decision (hand-written)
        │
        ├─ QPS >= threshold ──► Stage stays "Translated", ready for owner review
        └─ QPS < threshold  ──► NeedsReview = true (flag icon, not dot-track)
        ▼
6. Owner reviews Strings tab; flagged rows → "Post to Marketplace" for
   human review (existing Marketplace flow, unchanged — see E.6)
```

### E.6 Design forks carried over (unchanged from prior draft)

- **Marketplace scope for flagged-only review** — still recommend option
  (b): keep marketplace jobs whole-locale, let the vendor see which rows
  are flagged when they open the job, rather than building per-string job
  scoping now. Revisit only if you specifically want to demo posting just
  the low-confidence subset.
- **Manual accept gate** — still optional: QPS-pass can either auto-advance
  `Stage`, or only ever advance on an explicit "Save & Next" click, with
  `NeedsReview` as a pure hint either way. Decide when building the frontend
  piece, not now.

---

## Part F — Python FastAPI AI service: proposed design

**Not implemented. Design only, for you to build.**

### F.1 Why a separate service, and how it talks to .NET

```
.NET WorkflowService  ──HTTP POST──►  FastAPI AI Service  ──►  self-hosted LLM
        │                                    │                 (own GPU, via vLLM)
        │                                    ▼
        │                             COMET-Kiwi (local model,
        │                             no network call)
        │◄─────────────── JSON result ───────────────────────
        ▼
   writes QpsScore / CometKiwiScore / NeedsReview / TargetText / RawMtText
   back to Postgres via the existing EF Core DbContext — .NET still owns
   persistence
```

A **polyglot microservice split** — .NET orchestration/platform layer,
Python AI-inference layer — communicating over a thin internal HTTP
contract. With a self-hosted model this is really a **three-process**
architecture: .NET API → FastAPI (prompt/business logic + COMET-Kiwi
scoring) → vLLM (model serving). Precise language matters in an interview:
"FastAPI serves the model" and "FastAPI calls a model server" are different
claims — you're building the second one.

### F.2 Proposed endpoints (contract only — you write the implementation)

```
POST /translate-and-optimize
  Request:  { rawMtText: str, sourceText: str, targetLocale: str,
              projectSlug: str, glossaryTerms: list[{source: str, target: str}] }
  Response: { optimizedTranslation: str, cacheHit: bool, tokensUsed: int }

POST /qps-score
  Request:  { sourceText: str, targetText: str, targetLocale: str }
  Response: { score: int (0-100), flaggedIssues: list[str] }

POST /comet-score
  Request:  { sourceText: str, targetText: str, targetLocale: str }
  Response: { score: float (0-1) }
  # Note: this one does NOT call the LLM — COMET-Kiwi runs as a local
  # model inference inside the FastAPI process itself (or a small
  # dedicated worker), which matters for the cost story: this metric is
  # free per-call, unlike qps-score

POST /run-eval
  Request:  { projectSlug: str, pipelineConfig: str }
  Response: { evalRunId: int, avgCometKiwi: float, avgQpsScore: float,
              glossaryAdherenceRate: float, placeholderPreservationRate: float,
              cacheHitRate: float, avgLatencyMs: int, totalCostUsd: float }
  # Runs every EvalGoldenCase through the named pipeline config, writes
  # EvalRun + EvalCaseResult rows. This is literally your CI-gate endpoint
  # — could be wired into a GitHub Action later for the "quality gate on
  # every change" story, though that's a stretch goal, not v1.

POST /auto-route
  Request:  { qpsScore: int, projectThreshold: int }
  Response: { needsReview: bool }
```

### F.3 What's hand-written vs. generatable

Given the explicit goal is interview-demonstrable skill, lean further
toward hand-writing than the original C#-era boundary did — almost
everything AI-adjacent here is worth writing yourself:

**Hand-write yourself:**
- Prompt construction for MT Optimize and QPS scoring
- Response parsing/validation (structured output handling, malformed-output recovery)
- The Auto-Routing threshold comparison
- The semantic-cache similarity-threshold logic and embedding pipeline
- The COMET-Kiwi integration and score aggregation into `EvalRun`
- The provider abstraction for calling vLLM's OpenAI-compatible endpoint
- The eval-runner orchestration (`/run-eval`)

**Fine to scaffold with an LLM/Gemini:**
- FastAPI boilerplate (app setup, Pydantic models, routing, Dockerfile, requirements.txt)
- The thin HTTP client on the .NET side

### F.4 Decided

- **LLM provider: self-hosted, open-weight model, on your own GPU**, served
  via **vLLM** — not a commercial API
- `GoogleTranslateProviderService` (Legacy MT) **stays in .NET**, unchanged
- **Cost tracking gets built for real this time**: every `/translate-and-optimize`
  and `/qps-score` call returns token usage; the .NET side computes
  `RealCostUsd` (from a configured $/1K-token rate, even if self-hosted
  inference is "free" in the sense of no per-call billing — you should
  still model an equivalent cost, e.g. amortized GPU cost per token, so the
  ledger is meaningful and comparable to what a commercial API would have
  cost) and writes a `LedgerEntry` with `Source = "AI"` — closing the gap
  flagged earlier where AI usage was completely untracked
- Legacy MT calls also get a `LedgerEntry` (character-based, Google's real
  published rate) — so the ledger finally supports the actual "cost per
  resolved query, Legacy MT vs LLM-Enhanced vs Marketplace" comparison your
  playbook's Idea 1 explicitly wants
- Auth between .NET and Python: shared secret header, matching the existing
  `x-api-key` pattern

### F.5 Self-hosted model — serving architecture

```
┌─────────────────────────┐        ┌───────────────────────────────┐
│  FastAPI AI Service      │  HTTP  │  vLLM OpenAI-compatible server │
│  (hand-written prompts,  │───────►│  (model serving — infra work,  │
│   parsing, routing,      │        │   a distinct skill from prompt │
│   COMET-Kiwi, caching)   │◄───────│   engineering)                  │
└─────────────────────────┘        └───────────────┬─────────────────┘
                                                     ▼
                                          GPU, quantized model weights
```

- **vLLM** exposes an OpenAI-compatible `/v1/chat/completions` endpoint —
  your FastAPI client code looks identical to calling a commercial API,
  even though it's hitting your own GPU; swapping providers later is a
  config change, not a rewrite
- **Model candidates** (need real testing across de-DE/ja-JP/zh-CN/fr-FR/es-ES,
  not a default pick): **Qwen2.5-7B-Instruct** (prioritized — strong on
  zh-CN/ja-JP, two of your five locales), Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3
- **Quantization**: 4-bit (AWQ/GPTQ), exact choice per your GPU's VRAM
- This serving layer is itself a legitimate interview topic — model choice,
  quantization trade-offs, latency — distinct from and complementary to the
  prompt-engineering work above

### F.6 The Legacy-vs-Enhanced comparison — now with real metrics

Updated from the earlier draft to route through the eval harness rather
than being a one-off UI feature:

- `RawMtText` / `RawMtQpsScore` capture Stage 1 before Stage 2 overwrites
  anything (Part B.2)
- The Strings drawer's "Legacy MT" comparison box (not yet built — small,
  well-scoped frontend addition) shows both texts and both QPS scores
  side-by-side for any individual string
- But the **real artifact** is the `EvalRun` comparison across
  `PipelineConfig` values — run `"legacy-only"` and `"legacy+optimize"`
  against the same golden set, and the resulting two `EvalRun` rows *are*
  your interview sentence's numbers, computed and stored, not eyeballed
  from a UI

---

## Part G — Interview narrative checklist

Once built, you should be able to answer each of these with a real number
from an `EvalRun` row, not a description:

- [ ] What was your baseline COMET-Kiwi / QPS score with Legacy MT alone?
- [ ] What did the self-hosted LLM stage move those to?
- [ ] What's your cache hit rate, and what did it save in cost/latency?
- [ ] What's your glossary adherence rate, before and after grounding?
- [ ] What % of cases get flagged Needs Review, and can you name *why*
      (which `Category` tags dominate the flagged set)?
- [ ] What's your cost-per-resolved-query, broken out by Legacy MT vs
      LLM-Enhanced vs Marketplace (human) — the three-way comparison your
      playbook's Idea 1 explicitly wants?
- [ ] Can you name the specific failure mode you found (e.g. "idiomatic
      phrases" scored lowest) and what you'd do next to address it?

This checklist is the actual finish line for this feature — not "the UI
renders correctly," but "every box above has a real number behind it."
