# Localization Lab — capacity tiers with metered AI usage (DRAFT r2)

**Status: draft for the owner to correct. Nothing here is built.**

- r1 (2026-11-12) was written from a chat description only and got the model wrong: it proposed monthly allowances with hard stops.
- r2 (same day) is rewritten after reading the owner's own design notes, which are kept outside this repository. Statements marked **[S]** come from those notes. Statements marked **[A]** are my assumptions. Section 9 lists what still needs a decision.

The notes describe a real platform. This lab is a demo with invented data ("Auroraline"), so this draft takes the *model* from the notes and no names, clients or text.

## 1. The model in the source notes

| Topic | What the notes say |
|---|---|
| Marketplace | **Not a marketplace. [S]** Vendor teams are contracted by the platform and come as part of the service. Clients do not choose vendors, and vendors do not bid. |
| Tiers | Tier (Silver, Gold, and so on) means **team size and capacity**, not quality. **[S]** Same quality bar for every tier. The minimum tier follows the size of the client or project. Team size is set by hand per project or quarter; there is no automatic scale-up. |
| Volume | **Unlimited volume. No quotas or word allowances. No prices shown to clients. [S]** |
| Anonymity | Both directions. **[S]** The client sees a vendor team alias, the vendor sees a client alias. Only operations holds the mapping. |
| Progress | Percent complete against the deadline, with an accept or return loop. **[S]** Not words per day. |
| Machine help | For the vendor only. **[S]** Azure Translator produces a draft; a small model scans each draft, scores it 1 to 5 and may suggest a correction; a larger model re-scores in batch. Clients never see scores. A linguist is always the final authority. |
| Usage tracking | **Operations side only. [S]** Every Translator call is recorded with characters and billed characters; every model call with tokens. An operations page shows usage, errors and batch status, and has a kill switch. |
| Cost control | Rate limits per provider resource, word-count chunks per vendor team, a per-project monthly token budget with an alert. **[S]** Work in flight is never cancelled when a limit is reached; it finishes, records its state, and no new work is picked up. |

So "unlimited" and "tracked" are both true: the client's volume is unlimited by agreement, and the platform meters what that volume costs it in Azure Translator characters and model tokens.

## 2. What this repository has today

| Area | Today | Against section 1 |
|---|---|---|
| Marketplace | Jobs are posted per locale, vendors bid, the owner awards a bid | Wrong model: no bidding, no awarding |
| Unit of account | "Credits" on price bands, bids and a project balance | Wrong model: no prices are shown to clients |
| Tiers | None | Missing |
| Vendor assignment | By winning a bid | Should be by agreement: a contracted team per project and locale |
| Anonymity | Vendor roster shows vendor names and ratings to the owner | Should be aliases both ways |
| Machine translation | Google Translate | Should be Azure Translator |
| Scoring | QPS 0 to 100 with an auto-route threshold | The notes use 1 to 5, grouped by score, vendor-only. See question 4 |
| Usage record | One ledger row per workflow run; cost is $0 because no prices are configured | Should be one row per provider call, with an operations view |
| Limits | None | Should be rate limits, a monthly token budget with an alert, and a kill switch |
| Usage page | None | Missing |

The existing documents that describe the credit and marketplace model would be marked superseded once this draft is agreed: `localization-lab-plan.md`, `localization-lab-marketplace-flow.md`, and Parts B.2 and F.4 of `localization-lab-ARCHITECTURE-AND-WORKFLOW.md`.

## 3. Proposed model for the lab

### 3.1 Service agreement and tiers

```
ServiceAgreement
  ProjectId
  Tier              "Silver" | "Gold" | "Platinum"   (capacity only)
  ValidFrom, ValidTo
  Notes

VendorTeam
  Alias             shown to the client
  (real name kept only for the operations role)

TeamAssignment
  AgreementId, VendorTeamId, LocaleCode, MemberCount
```

- A tier fixes the **team size** assigned to the project. **[A]** Example: Silver 3 linguists, Gold 6, Platinum 10. Numbers are placeholders.
- No allowance, no balance, no price anywhere in the client view.
- Creating a translation job takes the team from the agreement for that locale. A locale with no assigned team is an error the owner sees, not a bid request.

### 3.2 What is metered

| Meter | Unit | Counted at |
|---|---|---|
| `azure-translator` | characters sent, and characters billed (each target locale is billed separately) | every draft request |
| `llm-scan` (small model) | input tokens, output tokens | every per-string scan |
| `llm-score` (large model) | input tokens, output tokens | every scored string, standard or batch |
| `embedding` | tokens | every translation-cache lookup |

Cache hits and translation-memory exact matches make no provider call and are recorded as zero-unit events, so the saving is visible.

### 3.3 Usage events

One immutable row per provider call. This replaces the per-run `LedgerEntry` with `Source = "AI"`.

```
LocalizationUsageEvent
  Id
  ProjectId
  VendorTeamId        (nullable)
  Meter
  Operation           "mt-draft" | "scan" | "score" | "retranslate" | "cache-embed" | "eval-run"
  WorkflowStepRunId   (nullable; groups the calls of one run)
  BatchId             (nullable; for batch scoring)
  LocaleCode
  Units               characters or input tokens
  UnitsBilled         billed characters, or output tokens
  CacheHit            bool
  ModelVersion        deployment and version used
  CostUsd             units x the rate in force at the time
  RateVersion
  OccurredAt
```

`CostUsd` is the platform's own cost. It is shown to the operations role only.

### 3.4 Controls (none of them is a client quota)

| Control | Behaviour |
|---|---|
| Rate limit | A token bucket per provider (characters per minute for Translator, tokens per minute for the scan model), shared by all workers |
| Chunking | Scanned strings accumulate into word-count chunks per vendor team (10,000 to 50,000 words, tunable by the team lead); a chunk is sent for batch scoring on an interval |
| Monthly budget | Per project, in tokens and characters. Crossing a threshold raises an **alert** to operations. It does not stop the client's work |
| Kill switch | Global and per project, read at the start of each task. When off, remaining strings go to the linguist without a draft or score |
| In-flight rule | A running call or a submitted batch always finishes and records its state. Only new work is held back |
| Done guard | A string cannot be marked done while its score is still pending, unless scoring was skipped, failed or filtered |

### 3.5 Rates

```
ProviderRate: Meter, UnitKind ("char" | "input-token" | "output-token"), UsdPerMillion, ValidFrom
```

Past events keep the rate they were charged at. The numbers are taken from the Azure pricing pages when this is built; none are written here on purpose.

## 4. What happens to the marketplace and credits

**[A]** Remove the bidding model and keep the screens that still make sense:

| Today | Becomes |
|---|---|
| "Post to Marketplace" workflow action | "Create translation job": assigns the agreed team for each locale |
| Marketplace page (price bands, post per locale) | Jobs page: per locale, the assigned team alias, progress against the deadline, state |
| Bid review page | Removed |
| Vendor portal: open jobs, submit a bid | Vendor portal: jobs assigned to my team |
| Vendor portal: awarded jobs, edit strings, submit | Kept, with drafts and scores shown |
| `CreditLedgerService`, credit balance, "Credits" labels | Removed |
| `LedgerEntry` rows | Left as history; no new rows |

If the bidding flow should stay as a separate demo mode, say so (question 2) and this section shrinks to renaming.

## 5. Operations usage page

A new page, visible to the operations or admin role only.

- **This month:** characters and tokens per meter, with cost, against the project budget and a month-end projection.
- **Over time:** daily usage per meter.
- **Breakdown:** by project, vendor team, locale and operation.
- **Savings:** translation-memory and cache hit rates, units avoided.
- **Health:** provider errors by code, rate-limit hits, batches in progress, expired or failed batches.
- **Controls:** kill switch, budget thresholds.
- **Runs:** each workflow run with its units and outcome.

Client view: projects active, completed and upcoming; per active project the counts approved, in progress and returned; vendor shown by alias; no scores, no usage, no cost. **[S]**

Vendor view: the same projects with client aliases; work grouped by score in the in-progress stage. **[S]**

## 6. Changes by component

| Component | Change |
|---|---|
| .NET API | Agreement, vendor team and assignment entities; usage events and rates; `UsageMeteringService`; `AzureTranslatorProviderService` behind the existing `ITranslationProvider`; job creation from the agreement; removal of bidding endpoints; usage and control endpoints for the operations role; aliasing in every client and vendor response |
| localization-ai | Already returns token counts per call. Add the operation name, model version and cache-hit flag to every response so the .NET side writes one event per call. Point the client at the Azure-hosted models (configuration) |
| React app | Jobs page in place of Marketplace; bid review removed; vendor portal reduced to assigned jobs; operations usage page; "Credits" wording removed |
| Seed data | Three tiers, an agreement and aliased teams for the demo project, a month of synthetic usage |

The .NET and React parts are open to Claude under the current rules. The Python service is the owner's or Muse's.

## 7. What the notes also contain that this draft does not cover

Listed so they are not lost; each is its own piece of work: XLIFF download and upload as a second vendor mode, placeholder masking for Translator, a golden set with a held-out calibration split, a deterministic veto that caps the score when a placeholder rule fails, a retranslation bucket chosen by the team lead, in-editor client review, and content-filter handling.

## 8. Out of scope

Payment and invoicing (there are no client prices), automatic team scaling, and per-user limits.

## 9. Questions for the owner

1. **"Unlimited" versus "tracked".** The notes say unlimited volume with no quotas. In chat you said unlimited is not right and usage must be tracked. This draft reads that as: unlimited for the client, metered and budgeted with alerts on the operations side. Is that right, or do you want a real cap that stops work?
2. **Does the bidding marketplace go away entirely**, or stay as a separate demo mode beside the agreement model?
3. **Tier names and team sizes.** The three tiers and member counts in 3.1 are placeholders.
4. **Score scale.** The lab has QPS 0 to 100 with auto-routing; the notes use 1 to 5 grouped by score and visible to vendors only. Switch the lab to 1 to 5, or keep 0 to 100?
5. **Which models.** The notes describe a small scan model plus a larger batch scorer; you mentioned GPT-4.1. Which deployments should the lab name, and should Google Translate be removed or kept as a fallback?
6. **Who is "operations" in the lab?** The existing admin role, or a new role?
7. **Real provider calls** cost money and need your keys and go-ahead. Until then everything runs on the fake providers, which cannot produce scores.
