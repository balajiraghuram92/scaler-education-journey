# Localization Lab — tier-based service with metered usage (DRAFT)

**Status: draft for the owner to correct. Nothing here is built.**
Written 2026-11-12 from the owner's description in chat, not from a source document. Every line marked **ASSUMED** is my guess and needs a yes or a correction. Section 8 lists the questions that change the design.

## 1. What the owner said

- The product is like Phrase: a translation platform with a marketplace side.
- The service is sold by **tier**, not by credits.
- "Unlimited" is not acceptable: usage of **Azure Translator** and **GPT-4.1** must be tracked.
- There was a **usage dashboard**. The earlier build (Gemini) assumed credits and tracked usage through the credit ledger instead.

## 2. What the repository has today

| Area | Today | Problem against section 1 |
|---|---|---|
| Unit of account | "Credits": `LedgerEntry.Amount`, shown on marketplace price bands and bids | Credits are the wrong model; a tier with allowances is wanted |
| Machine translation | `GoogleTranslateProviderService` (Google Translate v2) | Should be Azure Translator |
| LLM stage | `localization-ai` service, OpenAI-compatible client, documented as self-hosted vLLM | Should be GPT-4.1 (Azure OpenAI or Foundry) |
| Usage record | One `LedgerEntry` per workflow run: `Source`, `UnitsConsumed`, `UnitType`, `RealCostUsd` | Per run, not per call; no user or tier; `RealCostUsd` is 0 because no prices are configured |
| Limits | None for localization. (`BudgetGuardService` caps the tutoring chatbot only.) | Nothing stops a project from unlimited use |
| Dashboard | None in the Localization pages | A usage view is wanted |

Design documents that describe the credit model and should be marked superseded once this draft is agreed: `localization-lab-plan.md`, `localization-lab-marketplace-flow.md`, Parts B.2 and F.4 of `localization-lab-ARCHITECTURE-AND-WORKFLOW.md`.

## 3. Proposed model

### 3.1 Tiers

A project (or its owning account, see question 1) is on exactly one tier. A tier is a set of **monthly allowances** and feature switches. **ASSUMED** shape, numbers are placeholders:

| | Starter | Team | Enterprise |
|---|---|---|---|
| Azure Translator characters per month | 500,000 | 5,000,000 | custom |
| GPT-4.1 tokens per month (input + output) | 1,000,000 | 20,000,000 | custom |
| MT Optimize, QPS, Auto-Route | Optimize only | all | all |
| Marketplace (human vendors) | no | yes | yes |
| Locales per project | 3 | 20 | custom |
| When an allowance runs out | hard stop | hard stop or paid overage | paid overage |

Tiers are rows in a table, not constants in code, so they can be changed without a deploy.

### 3.2 What is metered

Two meters only, matching the two paid providers:

| Meter | Unit | Counted at | Source of the number |
|---|---|---|---|
| `azure-translator` | source characters | every translate call | request text length, as Azure bills it |
| `gpt-4.1` | input tokens, output tokens (kept separately) | every chat call: optimize, QPS judge, eval runs | `usage` block of the model response |

Embeddings for the translation cache are a third, small meter (**ASSUMED**: tracked, shown, but not limited).

Cache hits consume no GPT-4.1 tokens, so the cache shows up directly as saved allowance.

### 3.3 Usage events

Every provider call writes one immutable row. This replaces the per-run ledger entry as the source of truth.

```
LocalizationUsageEvent
  Id
  ProjectId
  UserId (nullable: workflow runs triggered by a schedule have none)
  Meter              "azure-translator" | "gpt-4.1" | "embedding"
  Operation          "auto-translate" | "mt-optimize" | "qps-score" | "eval-run" | "cache-embed"
  WorkflowStepRunId  (nullable; groups the calls of one run)
  LocaleCode
  Units              characters, or input tokens
  UnitsOut           output tokens (null for characters)
  CacheHit           bool
  CostUsd            Units x configured rate at the time of the call
  RateVersion        which price row was used
  OccurredAt
```

`CostUsd` is our cost of goods, shown to the owner of the platform, not a price charged to the customer. The customer sees allowance used.

### 3.4 Allowance check

Before a workflow action that calls a provider:

1. Sum this month's events for the project's meter.
2. Estimate the run (characters are exact; tokens are estimated from string count and a moving average per string).
3. If the estimate fits: run. If it does not: refuse the whole run with a clear message ("This run needs about 240,000 GPT-4.1 tokens; 85,000 remain this month"), unless the tier allows overage.
4. During the run, stop when the allowance is actually reached; report how many strings were done and how many were left.

No silent partial success: the step outcome states what was skipped and why.

### 3.5 Prices

A small table of provider rates with a validity date, so past events keep the rate they were charged at:

```
ProviderRate: Meter, UnitKind ("char" | "input-token" | "output-token"), UsdPerMillion, ValidFrom
```

The numbers must be taken from the Azure pricing pages when this is built; none are written here on purpose.

## 4. What happens to credits and the marketplace

**ASSUMED:** the marketplace stays (human vendors bid on jobs), but it stops using fictional credits.

- A vendor bid is a price in real currency.
- Approving a job records a marketplace charge for the project; it is not part of the tier allowance.
- `LedgerEntry` with `Source = "Marketplace"` is kept for those charges. `Source = "AI"` entries are replaced by usage events.
- `CreditLedgerService.GetProjectBalanceAsync` and the "Credits" labels in `LocalizationMarketplace.jsx` and `LocalizationBidReview.jsx` are removed or renamed.

If the marketplace is meant to be included in the tier (for example "Team includes 10,000 human-translated words"), that is a third meter and section 3.1 gains a row. See question 3.

## 5. Usage dashboard

One page under the Localization Lab, per project, month selector.

- **Allowance bars:** Azure Translator characters and GPT-4.1 tokens, used against tier allowance, with the projected month-end figure.
- **Usage over time:** daily bars per meter.
- **Breakdown:** by operation (auto-translate, optimize, QPS, eval), by locale, by user.
- **Cache:** hit rate and tokens saved.
- **Cost (platform owner only):** `CostUsd` per meter, cost per string, legacy MT against LLM-enhanced.
- **Recent runs:** each workflow run with its units and outcome, linking to the step.

An account-level view sums the projects if tiers are per account.

## 6. Changes by component

| Component | Change |
|---|---|
| .NET API | `LocalizationTier`, `ProjectTierAssignment`, `LocalizationUsageEvent`, `ProviderRate` entities and migration; `UsageMeteringService` (record, month totals, allowance check); `AzureTranslatorProviderService` behind the existing `ITranslationProvider`; allowance check in `WorkflowService` before the provider actions; usage endpoints |
| localization-ai | Already returns token counts per call. Add the operation name and cache-hit flag to every response so the .NET side can write one event per call. Point the OpenAI-compatible client at the GPT-4.1 deployment (configuration only) |
| React app | Usage dashboard page; tier badge and remaining allowance on the Workflow page; refusal message when a run does not fit; remove "Credits" wording |
| Seed data | Three tiers, the demo project on one of them, a month of synthetic usage so the dashboard is not empty |

Who builds what follows the existing rules: the .NET and React parts are open to Claude; the Python service is the owner's or Muse's.

## 7. Out of scope for a first version

Payment, invoicing, self-service tier change, per-user limits inside a project, rate limiting per minute, and alerts by email.

## 8. Questions for the owner

1. **Who holds the tier?** A project, or an account that owns several projects? (Today there is no account entity for localization; a project-level tier is the smaller change.)
2. **What are the tiers?** Names, allowances, and which features each one unlocks. The table in 3.1 is invented.
3. **Is human translation part of the tier**, or always paid per job on top?
4. **At the limit: stop, or allow overage?** If overage, at what price, and who approves it?
5. **Which deployment of GPT-4.1 and Azure Translator?** Azure OpenAI or Foundry, which region, and are the keys already created? (Real calls cost money and need the owner's go-ahead.)
6. **Does Google Translate stay** as a fallback provider or is it removed?
7. **Who sees cost in dollars?** Only the platform owner, or the customer too?
8. **Should existing ledger rows be migrated** into usage events, or left as history?
9. **Was the earlier usage dashboard** a design you still have (screenshot, Figma, document)? If so, add it under `info/localization-design/images/` and this section follows it instead.
