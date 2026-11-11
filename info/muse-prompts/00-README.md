# Muse prompts — tracks, order and running in parallel

Four tracks, built by Muse Code from the prompts in this folder and reviewed by Claude after each step.

| Track | What | Prompts | Lands in |
|---|---|---|---|
| L | Localization Lab corrections (.NET + React) | `L1-…`, `L2-…`, `L3-…` | `api/…/Localization`, `app/src/pages/Localization` |
| LA | Localization AI service (Python) | `localization-ai/LA1-to-LA4-prompts.md` | new `localization-ai/`, one EF migration, then .NET wiring |
| P | Python port of the .NET API | `python-port/PORT-RULES.md`, `python-port/P0-to-P8-prompts.md` | new `api-python/` |
| G | Issue Intelligence & bug-fix agent (Python) | `issue-intel/BUILD-SPEC.md`, `issue-intel/G0-to-G4-prompts.md` | new `issue-intel/` |

## What can run at the same time

Steps on the same row of a track run one after another. Different tracks, and steps marked ∥, can run at the same time.

```
Track L    L1 ∥ L2 ∥ L3 ───────────────────────────┐
                                                    ├─► LA4 ─┐
Track LA   LA1 ─► LA2 ─► LA3 ──────────────────────┘        │
                                                             ├─► P6
Track P    P0 ─► P1 ─► P2 ─► ( P3 ∥ P4 ∥ P5 ∥ P7 ) ─────────┘ ─► P8
Track G    G0 ─► G1 ─► G2 ─► G3 ─► G4
```

Why these limits:

- **L1, L2, L3** edit different files, so they can run together. L2 and L3 display errors that L1 makes the server return, so test the three together after all are merged.
- **LA4** edits `WorkflowService.cs` (also edited by L1) and `LocalizationStrings.jsx` (also edited by L2). It waits for both.
- **P0, P1, P2** are the foundation every later port phase imports (settings, models, the signed-in user). They cannot be parallel. After P2, phases P3, P4, P5 and P7 fill separate modules; P0 pre-registers every router so none of them touches `main.py`.
- **P6** ports the Localization code, so it waits until that code has stopped changing (after L1–L3, and after LA4 if you want the port to include the AI wiring).
- **G** touches only `issue-intel/` and never waits for anything else, but its own phases build on each other.

A sensible first wave is four sessions: **L1, LA1, P0, G0**. Add L2 and L3 if you are comfortable reviewing six results at once.

Running in parallel does not cost fewer credits; it only saves clock time. It also means a mistake in an early phase is not caught before the next one starts, so keep the review between phases of the same track.

## How to run sessions in parallel

One folder can only be on one branch, so each parallel session needs its own git worktree. From the main checkout:

```bash
git worktree add ../sej-la1 -b muse/la1 main
```

Open Muse Code in that folder and paste the prompt. Repeat with a different folder and branch name per session (`../sej-p0` / `muse/py-p0`, `../sej-g0` / `muse/g0`, and so on). Remove a worktree after its branch is merged:

```bash
git worktree remove ../sej-la1
```

**The prompt files must be committed to `main` before you create worktrees.** A new worktree contains only committed files, and the prompts tell Muse to read `info/muse-prompts/…` and `info/localization-design/specs/…`.

## The review loop

1. Muse reports done. Do not merge.
2. Tell Claude "review LA1" (or whichever step), with Muse's final report.
3. Claude reads the diff, runs the build and tests, and either passes it or writes a correction prompt.
4. Merge after the review passes. Start the next step of that track from the merged `main`.

## Branch names

`muse/loc-backend` (L1), `muse/loc-owner-ui` (L2), `muse/loc-vendor-ui` (L3), `muse/la1` … `muse/la4`, `muse/py-p0` … `muse/py-p8`, `muse/g0` … `muse/g4`.

## If credits run short

Cheap and high-value: L1–L3, P0, P1, LA1, LA2, G0. Expensive: P3, P7, G1, G3. P4 and P5 can be dropped without affecting any other step. G4 can be dropped without affecting G0–G3.
