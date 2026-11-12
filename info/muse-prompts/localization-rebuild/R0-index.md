# Track R — Localization Lab rebuild: order and status

Moves the Localization Lab from the credits-and-marketplace design to the owner's model: contracted vendor teams, capacity tiers, hard monthly usage caps, scores from 1 to 5 shown to vendors only, and Azure Translator.

- **Contract:** `CONTRACT.md` — every route, JSON shape and fixed string after the rebuild. All six prompts build to it; none may change it.
- **Design background:** `info/localization-design/specs/localization-lab-tier-usage-model-DRAFT.md`. Where the draft and the contract differ, the contract wins (the owner chose a hard cap; the draft describes alert-only).

Muse builds every step from its prompt. Claude checks afterwards by running the builds, the tests, the migrations against a real database, and the app in a browser.

## Owner decisions (12 Nov 2026)

| Question | Decision |
|---|---|
| When usage gets high | Hard cap per project per month; new provider calls stop at the cap, a call in flight finishes |
| Bidding marketplace | Removed; jobs go to the team named in the service agreement |
| Score scale | 1 to 5, vendor-only |
| Machine-translation provider | Azure Translator only; Google Translate removed |
| Tiers | Silver 3, Gold 6, Platinum 10 linguists per team (placeholder sizes; change them in `ServiceTiers` and the contract together) |
| Operations role | The existing admin role |

## Steps

| Step | What | Folder | Prompt |
|---|---|---|---|
| R1 | Usage events, rates, one event per provider call, operations usage endpoints | `api/`, `tests/` | `R1-usage-metering-backend.md` |
| R2 | Usage caps, AI kill switch, Azure Translator replaces Google | `api/`, `tests/` | `R2-controls-and-azure-translator-backend.md` |
| R3 | Agreements, tiers, team aliases, jobs by assignment, bidding and credits removed, 1 to 5 scores | `api/`, `tests/` | `R3-agreements-jobs-scores-backend.md` |
| R4 | React app: Jobs page, client Strings view, vendor portal, Operations page | `app/` | `R4-frontend.md` |
| R5 | AI service: 1 to 5 judge, placeholder veto, response fields | `localization-ai/` | `R5-ai-service-score-scale.md` |
| R6 | Python port brought back in line with the .NET API | `api-python/` | `R6-python-port-sync.md` |

## Order

One Muse session, one after another: **R1, R2, R3, R4, R5, R6**. Claude checks after all six are finished.

Rules the order must respect, whichever way it is run:

- R1, R2 and R3 edit the same .NET files and must run in that order.
- R6 ports the C# that R1 to R3 produce, so it runs after R3.
- R4 and R5 touch only their own folders and are written against the contract. They can run at any point, including in separate sessions alongside the backend chain:

```
Session A   R1 ─► R2 ─► R3 ─► R6
Session B   R4
Session C   R5
```

Checking only at the end saves waiting, but a mistake in R1 is then built on by R2 and R3. If time allows, tell Claude "R1 done" before starting R2; that one check covers the migration style every later backend step copies.

## Paste lines

```
Read info/muse-prompts/localization-rebuild/R1-usage-metering-backend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

```
Read info/muse-prompts/localization-rebuild/R2-controls-and-azure-translator-backend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

```
Read info/muse-prompts/localization-rebuild/R3-agreements-jobs-scores-backend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

```
Read info/muse-prompts/localization-rebuild/R4-frontend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

```
Read info/muse-prompts/localization-rebuild/R5-ai-service-score-scale.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

```
Read info/muse-prompts/localization-rebuild/R6-python-port-sync.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

## What the rebuild does not cover

From the owner's notes, each its own later piece of work: XLIFF download and upload as a second vendor mode, placeholder masking for the translation provider, a golden set with a held-out calibration split, batch scoring in word-count chunks, a retranslation bucket chosen by the team lead, a done-guard that blocks submit until scoring finishes, in-editor client review, and content-filter handling.

Real provider calls (Azure Translator, the Azure-hosted model) need the owner's keys and go-ahead. Until then the stack runs on mock translation and the fake model, which produces no scores.

## Environment variables the owner must set after R2

`AzureTranslator__Key`, `AzureTranslator__Region`, and optionally `AzureTranslator__Endpoint`, in the compose and `.env` files that Claude and Muse do not edit. The Google Translate key can be removed.

## Follow-up after the R2-R6 review (12 Nov 2026)

Owner decision: jobs include machine output for vendor post-editing (CONTRACT 2.5 and 3 amended).

| Order | Prompt | Scope | Depends on |
|---|---|---|---|
| a | `../corrections/C17-api-python-track-r.md` | api-python fixes found in review | — |
| b | `R7-jobs-include-mt-output.md` | .NET + React | — (can run beside C17) |
| c | `R8-port-jobs-include-mt-output.md` | api-python port of R7 | C17 and R7 |

Paste lines:
- `Read info/muse-prompts/corrections/C17-api-python-track-r.md and do everything below its paste line.`
- `Read info/muse-prompts/localization-rebuild/R7-jobs-include-mt-output.md and do everything below its paste line.`
- `Read info/muse-prompts/localization-rebuild/R8-port-jobs-include-mt-output.md and do everything below its paste line.`
