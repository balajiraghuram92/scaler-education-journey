# Localization Lab — Vendor Marketplace Flow (locked 2026-09-05)

> Companion to [localization-lab-plan.md](localization-lab-plan.md). This document
> covers ONLY the vendor/freelancer marketplace addition — the human-translation
> track that runs parallel to the AI/MT pipeline. It reconstructs the "developers
> post work, translators apply with a bid" model from the real Unity ES project
> (see the dossier's Phase 1/9 commercialization discussion), scaled to a
> buildable portfolio feature.
>
> Nothing in this document is built yet. This is the pre-mockup flow spec —
> every entity, state, and screen the mockups and build prompt must cover, so
> Gemini isn't asked to guess anything when we get to images/code.

---

## 1. Why this exists

The AI/MT pipeline (Phases 2-3 of the main plan) answers "how do we translate
fast and cheap." The marketplace answers the other half of the real project:
**enterprise customers sometimes need a human translator for a language the AI
pipeline doesn't cover well, or for quality-critical content** — and Unity's
real workflow let outside translators bid on that work per-language, the same
way a freelance platform works, rather than assigning a single fixed vendor.

This is a **second, independent interview centerpiece** alongside the AI
vertical — it demonstrates marketplace/bidding-system design, not just API
integration.

---

## 2. Core entities

```
Vendor
  id
  name                 e.g. "Maria Fischer"
  languages[]          e.g. ["de-DE", "fr-FR"]  — declared, seeded, not verified
  rating                e.g. 4.9  (seeded, static — no live review system in scope)
  avatarInitials

MarketplaceJob
  id
  projectId
  locale                e.g. "de-DE"  — ONE locale per job, always
  stringCount           count of strings in this locale still New/untranslated at post time
  wordCount             derived from those strings' source text
  suggestedPriceLow     computed from wordCount × a per-word credit rate
  suggestedPriceHigh    computed the same way, upper band
  status                Draft | Open | Awarded | InProgress | SubmittedForReview
                         | Approved | NeedsRevision | Closed
  awardedVendorId       null until Awarded
  postedAt / awardedAt / submittedAt / approvedAt

Bid
  id
  jobId
  vendorId
  proposedPrice          vendor's number — expected inside or near the suggested band
  note                   short free-text pitch, e.g. "Native DE, automotive UI experience"
  status                 Pending | Awarded | Declined | Withdrawn
  submittedAt

LedgerEntry (extends the existing AI/MT credit ledger from Phase 2 — NOT a new ledger)
  id
  projectId
  source                 "AI" | "Marketplace"   ← the field that makes cost-comparison possible
  amount
  relatedJobId           null for AI entries, set for Marketplace entries
  createdAt
```

**Key modeling decision:** a `MarketplaceJob` is always scoped to exactly one
`(projectId, locale)` pair. A project needing DE, JA, and ZH-CN translated
posts **three separate jobs**. A vendor who only knows DE never sees the JA or
ZH-CN jobs — the Open Jobs board is pre-filtered by the vendor's declared
`languages[]`.

---

## 3. Job lifecycle (state machine)

```
                    owner clicks "Post to Marketplace"
                    (Orchestrator action, per project+locale)
                              |
                              v
   Draft ─────────────────► Open ──────► Awarded ──────► InProgress
  (not yet posted,      (visible to      (owner picked   (vendor editing
   computed but          matching-       one bid, rest    Target strings
   not visible to        language        auto-Declined)   in vendor portal)
   vendors)              vendors,
                         accepting                              |
                         bids)                                  v
                                                        SubmittedForReview
                                                     (vendor clicks "Submit
                                                      for Review" once all
                                                      rows in the job are
                                                      Target-filled)
                                                                  |
                                                    owner reviews in the same
                                                    Strings table, filtered to
                                                    this job's rows
                                                                  |
                                        +-------------------------+------------------------+
                                        |                                                   |
                                        v                                                   v
                                    Approved                                        NeedsRevision
                              (LedgerEntry created,                          (sent back to InProgress,
                               source=Marketplace,                            vendor keeps editing —
                               strings advance to                             no new bidding round)
                               Approved stage same as
                               AI-translated strings) ------------> Closed
```

**Bid sub-lifecycle within an Open job:**
```
Pending ──► Awarded      (one bid, chosen by owner)
Pending ──► Declined     (all other bids on the same job, automatically, at award time)
Pending ──► Withdrawn    (vendor pulls their own bid before award — optional, low priority)
```

Once a job leaves `Open`, no new bids are accepted — the bid list is frozen at
whatever existed at award time.

---

## 4. Screens required — Owner side

These live inside the existing Neuralascent app, as a **4th tab** added to the
already-locked tab bar: `Strings | Workflow | Snapshots | Marketplace`
(underline style, matching the locked visual spec).

### 4a. Marketplace tab — locale overview
One row per locale configured on the project (not per string). Ruled table,
same visual language as the Strings table:

| Column | Content |
|---|---|
| Locale | e.g. "de-DE" |
| Strings remaining | count still New at last check |
| Status | Not Posted / Open (bidding) / Awarded to \<vendor\> / In Progress / Submitted for Review / Approved |
| Suggested band | e.g. "180–240 credits" (only shown once posted) |
| Action | icon button: "Post to Marketplace" (if Not Posted) → opens 4b; "View Bids" (if Open) → opens 4c; "Review Submission" (if Submitted for Review) → opens 4d |

### 4b. Post-to-Marketplace panel (drawer or modal — reuse the locked
dimmed-overlay drawer pattern)
- Locale name (heading)
- Read-only computed fields: string count, word count, suggested price band
  (low–high)
- No manual price override by the owner — the band is system-computed only,
  vendors are the ones who propose within/near it
- Single icon-button primary action: "Post" (confirms, job → Open)

### 4c. Bid review — side-by-side list
Table, one row per bid on this job (only reachable while job is `Open`):

| Column | Content |
|---|---|
| Vendor | name + star rating, e.g. "Maria Fischer ★4.9" |
| Languages | vendor's full declared list (context — shows they're not a DE-only specialist if relevant) |
| Proposed price | e.g. "210 credits" — visually flagged (subtle color, not a badge) if outside the suggested band |
| Note | vendor's short pitch text |
| Action | icon button: "Award" |

Awarding one bid immediately flips the others to Declined and the job to
`Awarded` — no confirmation modal needed beyond the icon click (low-risk,
reversible only by re-posting a new job, which is an acceptable interview
trade-off to state explicitly, not silently glossed over).

### 4d. Review submission
Reuses the **existing Strings table + row-detail drawer** (already fully
designed), just pre-filtered to `WHERE locale = job.locale`. No new visual
design needed here. One additional action at the top of the filtered view:
icon button "Approve Submission" (→ Approved, creates the LedgerEntry) or
"Send Back for Revision" (→ NeedsRevision).

---

## 5. Screens required — Vendor side (separate portal)

This is a **visually distinct shell** — not the Neuralascent owner app with a
permission filter. Same color tokens/fonts (so it's recognizably the same
product family) but its own simpler nav, reinforcing the locked-scope story in
an interview ("a vendor cannot even see there's an Orchestrator").

Entry point: a vendor picker (since vendors are a seeded roster, not real
auth) — a simple dropdown/switcher at the top: "Viewing as: Maria Fischer (DE,
FR)". No login form, no password field.

### 5a. Open Jobs board
Card-per-job (this is the one place a card style is appropriate — it's a
different product surface than the ledger-style owner app), filtered to jobs
where `job.locale` is in the selected vendor's `languages[]`:
- Project name, locale, word count, suggested price band, "days open" or similar
- Button: "Submit a Bid" → opens 5b

### 5b. Bid submission form
- Read-only job summary (project, locale, word count, suggested band)
- Price input, defaulted to the band midpoint, editable
- Short note textarea (placeholder: "Tell the project owner about your experience with this content")
- Submit button

### 5c. My Jobs — locked-scope workspace
Once awarded, the vendor's version of the Strings table — but:
- **Only** rows where `locale = job.locale AND projectId = job.projectId`
- No Workflow tab, no Snapshots tab, no Orchestrator, no other locales, no
  project settings — literally absent from the nav, not just disabled
- Same row-detail drawer (Source/Target, Key heading, dot-track) as the owner
  app, so the actual translation-editing UX is shared/reused
- One additional top-level action once every row is filled: "Submit for
  Review" (→ job status `SubmittedForReview`)

---

## 6. Open questions / explicitly deferred

- **Suggested price band formula**: exact per-word credit rate not yet fixed —
  reuse whatever per-character/word rate Phase 2's credit estimator lands on;
  don't invent a second pricing formula.
- **Vendor rating changes over time**: out of scope — ratings are static seed
  values, no post-job rating/review flow (would be a Tier-3 stretch item if
  time allows).
- **Bid withdrawal by vendor before award**: nice-to-have, not required for
  the core demo story — build only if Tier 1 of this feature is done early.
- **Multiple simultaneous awarded jobs per vendor**: allowed by the model (a
  vendor's My Jobs list is naturally multi-row), no special handling needed.

---

## 7. Where this sits in the phase roadmap

Depends on:
- The Orchestrator action framework (Phase 1 of the main plan) — "Post to
  Marketplace" is implemented as a new Orchestrator action type, same pattern
  as "Auto-Translate via Google MT."
- The credit ledger (Phase 2 of the main plan) — Marketplace LedgerEntries
  extend the same ledger, not a new one.

Does NOT depend on Phase 3 (AI vertical / QPS / MT Optimize) — the marketplace
is a parallel human-translation track, not a consumer of QPS scores.

**Sequencing: confirmed 2026-09-05.** Built as **Phase 2.5 — Vendor
Marketplace**, slotted after Phase 2 (Google MT + Credits) and before Phase 3
(AI Vertical), since it only needs the Orchestrator and credit ledger, both of
which exist by the end of Phase 2. This keeps the depth-first rule intact
(finish Marketplace completely before starting the AI vertical) while giving
two independent interview centerpieces by the end of the build instead of
one. See the main plan's Phase roadmap for the canonical listing.

---

## 8. Mockups still needed (not yet generated)

None of the marketplace screens have a reference image yet. In build order:
1. Owner: Marketplace tab — locale overview table (§4a)
2. Owner: Post-to-Marketplace drawer (§4b)
3. Owner: Bid review list (§4c) — §4d reuses the existing Strings mockup, no new image needed
4. Vendor: Open Jobs board (§5a)
5. Vendor: Bid submission form (§5b)
6. Vendor: My Jobs locked-scope workspace (§5c) — largely reuses the existing Strings table/drawer visual language, so this may need only a light variant image, not a full new concept

## Status

Flow fully specified and internally consistent, sequencing confirmed as
Phase 2.5 (2026-09-05). Not yet mocked up visually — see §8 for the 6 screens
still needed before the Phase 2.5 build prompt can be written.
