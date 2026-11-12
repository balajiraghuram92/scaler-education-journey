# Track R — API contract after the rebuild

This file is the single source of truth for every step of track R. The backend steps (R1-R3) implement it, the frontend step (R4) consumes it, the AI-service step (R5) implements section 7, and the port step (R6) mirrors it. **No step may change this file.** If something here cannot be built as written, stop that item and say so in the report; the reviewer changes the contract and tells every track.

JSON is camelCase. Timestamps are UTC, ISO 8601. `decimal` values are JSON numbers. Errors use the problem shape the Localization endpoints already return (`type`, `title`, `status`, `detail`, `instance`, `traceId`).

Decisions this contract encodes (owner, 12 Nov 2026):

- **Not a marketplace.** Jobs go to the vendor team named in the project's service agreement. No bids, no prices, no credits.
- **Tiers are team capacity**, not quality: `Silver` 3 linguists per team, `Gold` 6, `Platinum` 10.
- **Hard cap.** Each project has a monthly cap on machine-translation characters and on model tokens. At the cap, no new provider call is made; a call already in flight finishes.
- **Scores are 1 to 5 and vendor-only.** Client-facing responses carry no score, no raw machine draft and no review flag.
- **Azure only.** Azure Translator replaces Google Translate.
- **Aliases both ways.** A client response never contains a vendor's real name; a vendor response never contains a project's real name or slug. Only operations responses contain both.

Three audiences:

| Audience | Path prefix | Signed in? |
|---|---|---|
| Client (project owner) | `/api/localization/projects…`, `/api/localization/jobs…`, `/api/localization/provider-health…` | as today (API key only) |
| Vendor team | `/api/localization/vendor…` | as today (API key only) |
| Operations | `/api/localization/ops…` | signed-in user with `Role == "Admin"` and `Status == "Approved"`; otherwise 403 |

## 1. Fixed strings

```
Workflow actions (exact):
  "Mark Translated"
  "Send to Review"
  "Approve"
  "Auto-Translate via Azure Translator"     (was "Auto-Translate via Google MT")
  "Create Translation Jobs"                 (was "Post to Marketplace")
  "Run MT Optimize"
  "Score Quality"                           (was "Score QPS")
  "Auto-Route"

Job status:     "NotCreated" | "Assigned" | "InProgress" | "SubmittedForReview" | "NeedsRevision" | "Approved"
Tier:           "Silver" | "Gold" | "Platinum"
Usage meter:    "machine-translation" | "llm-optimize" | "llm-score"
Usage operation:"mt-draft" | "mt-optimize" | "qps-score"
Unit kind:      "char" | "input-token" | "output-token"
Cap kind:       "machine-translation" (characters) | "llm" (input + output tokens of both llm meters)
Provider health names: "AzureTranslator" (was "GoogleMT"), "LlmAzureGpt" (unchanged)
```

Job lifecycle:

```
NotCreated --create--> Assigned --first vendor edit--> InProgress --vendor submit--> SubmittedForReview
SubmittedForReview --client approve--> Approved
SubmittedForReview --client send back--> NeedsRevision --first vendor edit--> InProgress
```

## 2. Client endpoints

Unchanged in path and behaviour unless listed: projects, strings, workflow (list, add, update, reorder, run, delete), snapshots, provider health.

### 2.1 Project

`GET /api/localization/projects`, `GET /api/localization/projects/{slug}`:

```json
{ "id": 1, "slug": "auroraline-hud-v3", "name": "Auroraline Automotive — HUD Strings",
  "sourceLocale": "en-US", "createdAt": "…", "tier": "Gold", "aiEnabled": true,
  "locales": [ { "id": 1, "localeCode": "de-DE", "displayName": "German (Germany)" } ] }
```

`tier` is null when the project has no agreement.

### 2.2 Strings (client view)

`GET /api/localization/projects/{slug}/strings?locale=`, and the response of `PUT …/strings/{stringId}/translations/{localeCode}`:

```json
{ "stringId": 1, "key": "hud.speed", "sourceText": "…", "localeCode": "de-DE",
  "targetText": "…", "stage": "Translated", "translationSource": "AI", "updatedAt": "…" }
```

Removed from this view: `qpsScore`, `needsReview`, `rawMtText`, `rawMtQpsScore`.

### 2.3 Workflow run

`POST /api/localization/projects/{slug}/workflow/steps/{stepId}/run` returns the step as today. New outcomes and errors:

| Situation | Result |
|---|---|
| AI switched off for the project, action is one of the four provider actions | 409, title "AI assistance is switched off", detail names the project |
| Cap already reached before the first call | 409, title "Monthly usage cap reached", detail: cap kind, used, limit |
| Cap reached part-way | 200; `lastRunOutcome` ends with `, {n} skipped: monthly {cap kind} cap reached ({used} of {limit})` |
| "Create Translation Jobs" | 200; `lastRunOutcome` = `"{created} jobs created, {skipped} skipped"`; a locale with no assigned team counts as skipped |

Outcome texts for the provider actions keep their current form with the new names: `"{n} strings translated via Azure Translator"`, `"{n} strings optimized"`, `"{n} strings scored"`, each followed by `, {m} failed` when `m > 0`.

### 2.4 Agreement

`GET /api/localization/projects/{slug}/agreement` → 200, or 404 when the project has none:

```json
{ "tier": "Gold", "membersPerTeam": 6, "validFrom": "…", "validTo": null,
  "teams": [ { "localeCode": "de-DE", "vendorTeamAlias": "Vendor Team Larch", "memberCount": 6 } ] }
```

### 2.5 Jobs (replace the marketplace)

`GET /api/localization/projects/{slug}/jobs` → one row per project locale:

```json
{ "id": 12, "projectId": 1, "localeCode": "de-DE", "status": "InProgress",
  "stringCount": 136, "wordCount": 540, "completedPercent": 42,
  "vendorTeamAlias": "Vendor Team Larch", "memberCount": 6,
  "createdAt": "…", "submittedAt": null, "approvedAt": null }
```

For a locale with no job: `id` null, `status` "NotCreated", counts computed live from the strings, `vendorTeamAlias` and `memberCount` from the agreement (null when no team is assigned).

`completedPercent` = strings of the job's locale whose stage is `Translated`, `InReview` or `Approved`, over `stringCount`, rounded down; 0 when `stringCount` is 0.

| Method | Path | Result |
|---|---|---|
| POST | `/api/localization/projects/{slug}/jobs/{localeCode}` | 200 job row. 409 `NO_TEAM_FOR_LOCALE` when the agreement assigns no team to that locale; 409 when a job for that locale exists and is not `Approved` |
| POST | `/api/localization/jobs/{jobId}/approve` | 200 job row; 409 unless status is `SubmittedForReview` |
| POST | `/api/localization/jobs/{jobId}/send-back` | 200 job row; 409 unless status is `SubmittedForReview` |

Removed: every `/api/localization/projects/{slug}/marketplace…` and `/api/localization/marketplace/…` route.

## 3. Vendor endpoints

| Method | Path | Result |
|---|---|---|
| GET | `/api/localization/vendor/roster` | `[ { "id": 1, "alias": "Vendor Team Larch", "languages": "de-DE,fr-FR" } ]` |
| GET | `/api/localization/vendor/{vendorId}/jobs` | jobs assigned to that team, newest first |
| GET | `/api/localization/vendor/jobs/{jobId}/strings` | vendor string rows |
| PUT | `/api/localization/vendor/jobs/{jobId}/strings/{stringId}` | body `{ "targetText": "…" }`; vendor string row; rules as today |
| POST | `/api/localization/vendor/jobs/{jobId}/submit` | vendor job row; rules as today |

Vendor job row (no project name, no slug):

```json
{ "id": 12, "clientAlias": "Client Team Kestrel", "localeCode": "de-DE", "status": "InProgress",
  "stringCount": 136, "wordCount": 540, "completedPercent": 42,
  "createdAt": "…", "submittedAt": null, "approvedAt": null }
```

Vendor string row (scores and the raw draft are visible here and nowhere else):

```json
{ "stringId": 1, "key": "hud.speed", "sourceText": "…", "localeCode": "de-DE",
  "targetText": "…", "stage": "Translated", "translationSource": "AI", "updatedAt": "…",
  "score": 4, "needsReview": false, "rawMtText": "…", "rawMtScore": 3 }
```

`score` and `rawMtScore` are integers 1 to 5, or null when not scored.

Removed: `GET /vendor/{vendorId}/open-jobs`, `POST /vendor/{vendorId}/jobs/{jobId}/bids`, `GET /vendor/{vendorId}/awarded-jobs`.

## 4. Operations endpoints

All under `/api/localization/ops`, admin only (403 otherwise).

### 4.1 Usage

`GET /usage?project={slug}&month={yyyy-MM}` (both optional; month defaults to the current UTC month; malformed month → 400; unknown project → 404):

```json
{ "month": "2026-11", "projectSlug": "auroraline-hud-v3",
  "meters": [ { "meter": "llm-optimize", "calls": 136, "failedCalls": 0, "cacheHits": 0,
                "units": 70000, "unitsOut": 5102, "costUsd": 0.42 } ],
  "byOperation": [ { "meter": "llm-optimize", "operation": "mt-optimize", "calls": 136, "failedCalls": 0,
                     "cacheHits": 0, "units": 70000, "unitsOut": 5102, "costUsd": 0.42 } ],
  "byLocale": [ { "meter": "llm-optimize", "localeCode": "de-DE", "calls": 27, "units": 14000,
                  "unitsOut": 1020, "costUsd": 0.08 } ],
  "byDay": [ { "date": "2026-11-12", "meter": "llm-optimize", "units": 70000, "unitsOut": 5102, "costUsd": 0.42 } ],
  "ratesMissing": [ { "meter": "llm-score", "unitKind": "input-token" } ],
  "caps": [ { "kind": "machine-translation", "monthlyLimit": 2000000, "used": 23895 },
            { "kind": "llm", "monthlyLimit": 5000000, "used": 75102 } ] }
```

`caps` is present only when `project` is given; `monthlyLimit` is null for an uncapped kind. `unitsOut` is null for the character meter.

`GET /usage/events?project={slug}&limit={n}` (limit 1-500, default 100), newest first:

```json
{ "id": 9, "projectSlug": "auroraline-hud-v3", "workflowStepId": 3, "meter": "llm-score", "operation": "qps-score",
  "localeCode": "de-DE", "units": 531, "unitsOut": 2, "cacheHit": false, "succeeded": false,
  "costUsd": 0.0011, "occurredAt": "…" }
```

### 4.2 Rates

`GET /rates` → `[ { "id": 1, "meter": "llm-score", "unitKind": "input-token", "usdPerMillion": 2.0, "validFrom": "…" } ]`, newest `validFrom` first.

`POST /rates` body `{ "meter", "unitKind", "usdPerMillion", "validFrom"? }` → 201 with the rate. Unknown meter or unit kind, or a negative price → 400. Same meter, unit kind and `validFrom` as an existing row → 409.

### 4.3 Controls

`GET /projects/{slug}/controls`:

```json
{ "projectSlug": "auroraline-hud-v3", "aiEnabled": true,
  "caps": [ { "kind": "machine-translation", "monthlyLimit": 2000000, "used": 23895 },
            { "kind": "llm", "monthlyLimit": 5000000, "used": 75102 } ] }
```

`PUT /projects/{slug}/controls` body, every field optional; a field that is absent is left unchanged, an explicit `null` limit removes the cap:

```json
{ "aiEnabled": false, "machineTranslationMonthlyLimit": 2000000, "llmMonthlyLimit": 5000000 }
```

Returns the same shape as GET. A negative limit → 400.

### 4.4 Teams and agreements

`GET /teams` → `[ { "id": 1, "alias": "Vendor Team Larch", "realName": "Maria Fischer", "languages": "de-DE,fr-FR" } ]`.

`GET /projects/{slug}/agreement` → the client shape from 2.4 plus `"clientAlias"` and, per team, `"vendorTeamId"` and `"vendorTeamRealName"`.

`PUT /projects/{slug}/agreement` body:

```json
{ "tier": "Gold", "validFrom": "…", "validTo": null,
  "teams": [ { "localeCode": "de-DE", "vendorTeamId": 1 } ] }
```

Creates or replaces the agreement. `memberCount` for every team is the tier's capacity. Unknown tier, a locale the project does not have, an unknown team, or a locale listed twice → 400.

## 5. Caps and the kill switch

- "Used" for a cap is the sum over the current UTC calendar month of the project's usage events: `units` for `machine-translation`; `units + unitsOut` for the two llm meters together. Cache hits count 0.
- Before each provider call the service compares used (including the events of this run) with the limit. For machine translation the call's size is known (source characters): the call is skipped if it would pass the limit. For a model call the size is not known in advance: the call is skipped once used is at or over the limit.
- A skipped string is left as it was. The run continues to the end so that the outcome can report the count.
- A project with no cap row is uncapped for that kind.
- `aiEnabled = false` refuses the four provider actions with 409 before any call. "Create Translation Jobs" and the three stage actions are not affected.

## 6. Scores

- Scale 1 to 5. 5 = publishable as is; 4 = minor polish; 3 = needs editing; 2 = poor, rework; 1 = wrong or unusable.
- A translation whose placeholders do not match the source can never score above 2.
- The project's `qpsThreshold` means: a score **below** it needs review. Default 4.
- "Auto-Route" sets `needsReview` from the score and the threshold, as today.

## 7. `localization-ai` service

Paths and request bodies are unchanged. Responses change as follows.

`POST /qps-score`:

```json
{ "score": 4, "flaggedIssues": ["…"], "vetoed": false,
  "inputTokens": 531, "outputTokens": 12, "tokensUsed": 543, "latencyMs": 210, "costUsd": 0.0, "fallback": false,
  "operation": "qps-score", "model": "…", "promptVersion": "qps_judge_v2" }
```

`score` is an integer 1 to 5, or null with `fallback: true` when the judge gave no usable answer. `vetoed` is true when the placeholder rule capped the score at 2.

`POST /translate-and-optimize`: unchanged fields, plus `"operation": "mt-optimize"`, `"model"`, `"promptVersion"`.

`POST /auto-route`: `needsReview` is true when `qpsScore` is null, or `qpsScore < projectThreshold`, or any check is false. Scores outside 1 to 5 → 422.

`POST /comet-score`, `POST /run-eval`, `GET /health`: unchanged, except that eval runs store and report the judge score on the 1 to 5 scale.
