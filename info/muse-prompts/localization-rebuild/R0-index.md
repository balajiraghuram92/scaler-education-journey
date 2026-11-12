# Track R — Localization Lab rebuild: order and status

Moves the Localization Lab from the credits-and-marketplace design to the model in `info/localization-design/specs/localization-lab-tier-usage-model-DRAFT.md`: contracted vendor teams, capacity tiers, unlimited client volume, and provider usage metered on the operations side.

Muse builds each step from its prompt; Claude runs the build, tests and a real-database check after each, as in the other tracks. One step at a time within a row.

## Steps

| Step | What | Lands in | Prompt | Waits for |
|---|---|---|---|---|
| R1 | Usage events, rates, metering service, one event per provider call, operations endpoints | `api/`, `tests/` | `R1-usage-metering-backend.md` | nothing |
| R2 | Operations usage page | `app/` | written after R1 is reviewed (it needs R1's final response shapes) | R1 |
| R3 | Controls: monthly budget with an alert, kill switch, in-flight rule | `api/`, `tests/`, `app/` | to write | R1, and question 1 |
| R4 | Service agreement, tiers as team capacity, vendor teams with aliases | `api/`, `tests/` | to write | questions 2 and 3 |
| R5 | Jobs assigned by agreement replace bidding; marketplace, bids and credits removed or parked | `api/`, `tests/`, `app/` | to write | R4, and question 2 |
| R6 | Azure Translator behind `ITranslationProvider` | `api/`, `tests/` | to write | question 5; real calls need the owner's keys and go-ahead |
| R7 | Score scale and who sees scores | `api/`, `app/`, `localization-ai/` | to write | question 4 |
| R8 | `localization-ai` returns the operation, model version and cache-hit flag on every response | `localization-ai/` | to write | R1 |
| R9 | Bring `api-python/` back in line with the .NET API | `api-python/` | to write | after R1-R7 have stopped changing the .NET side |

R1 is safe under any answer to the open questions: it only adds records and an operations view. Nothing is removed until R5.

R2 and R8 can run at the same time as each other once R1 is reviewed; they touch different folders.

## Open questions (from the draft, section 9)

These decide what R3 to R7 build. Numbers refer to the draft.

1. "Unlimited" for the client with metering and alerts for operations, or a real cap that stops work?
2. Does the bidding marketplace go away entirely, or stay as a separate demo mode?
3. Tier names and team sizes.
4. Score scale: keep QPS 0 to 100 with auto-routing, or switch to 1 to 5, vendor-only?
5. Which models and translation provider the lab names; is Google Translate removed or kept as a fallback?
6. Is "operations" the existing admin role? (R1 assumes yes.)

## How to run a step

```
Read info/muse-prompts/localization-rebuild/R1-usage-metering-backend.md and carry out everything below its first "---" line, exactly as written. Do not run commands. Do not commit.
```

Then tell Claude "R1 done" with Muse's report.
