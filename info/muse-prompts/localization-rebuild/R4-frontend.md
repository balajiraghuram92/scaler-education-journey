# R4 — Localization Lab rebuild: React app

The whole frontend change for track R, in one step. **It can run at the same time as the backend steps (R1-R3) and R5**: it touches only `app/`, and it is built against the contract, not against the running API.

Authority for every route, field name and fixed string: `info/muse-prompts/localization-rebuild/CONTRACT.md`. Do not edit the contract. If a screen needs a field the contract does not have, stop that item and say so in the report; do not invent a field.

Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository (React + Vite in `app/`, tests with Vitest). For this task you may edit files under `app/`.

Work only in `app/`. Do not touch `api/`, `tests/`, `api-python/`, `localization-ai/`, compose files or `.env*`. One agent, no workflow fan-out. Do not run commands. Do not commit. Do not create or switch branches. Add no npm dependency: charts are plain SVG or CSS.

Do the tasks in order. After each task, append what you did to `info/muse-prompts/localization-rebuild/PROGRESS-frontend.md` (create it) under "R4" before starting the next.

## What changes for the user

- The **Marketplace** tab becomes **Jobs**: one row per locale with the assigned vendor team (by alias), progress, and state. No bids, no prices, no credits.
- The **Strings** page is the client's view: it no longer shows scores, the raw machine draft or review flags.
- The **vendor portal** shows the jobs assigned to the selected team, under the client's alias, with scores from 1 to 5.
- A new **Operations** page (admin only) shows provider usage, caps, the AI switch, rates, teams and agreements.

## Read these first, in full

- `info/muse-prompts/localization-rebuild/CONTRACT.md`
- `app/src/api/client.js` (the `localization` and `vendorPortal` blocks, about lines 354-392, and the `admin` block)
- `app/src/App.jsx` (Localization routes, about lines 138-190; the admin route at about line 57 for `ProtectedRoute requireAdmin`)
- Every file in `app/src/pages/Localization/` and `app/src/pages/Localization/Vendor/`
- `app/src/components/common/StateViews.jsx`, `app/src/utils/timeAgo.js`
- One existing test for style, for example `app/src/__tests__/components/PracticeQuestions.test.jsx`

Match the existing code style: function components, inline style objects as in the Localization pages, the same colour values, `lucide-react` icons, `LoadingState` / `ErrorState` / `EmptyState`, errors shown from `err.message`.

## Task 1 — API client (`app/src/api/client.js`)

In `api.localization`:

- Remove `getMarketplaceOverview`, `postToMarketplace`, `getBids`, `awardBid`, `approveSubmission`, `sendBackForRevision`.
- Add `getJobs(slug)`, `createJob(slug, locale)`, `approveJob(jobId)`, `sendBackJob(jobId)`, `getAgreement(slug)` (CONTRACT 2.4, 2.5).

In `api.vendorPortal`:

- Remove `getOpenJobs`, `submitBid`, `getAwardedJobs`.
- Add `getJobs(vendorId)` (CONTRACT section 3). Keep `getRoster`, `getJobStrings`, `updateJobString`, `submitJob`.

New block `api.localizationOps` (CONTRACT section 4): `getUsage({ project, month })`, `getUsageEvents({ project, limit })`, `getRates()`, `addRate(body)`, `getControls(slug)`, `updateControls(slug, body)`, `getTeams()`, `getAgreement(slug)`, `saveAgreement(slug, body)`. Build query strings with `URLSearchParams` and leave out parameters that are not set.

`updateControls` must be able to send an explicit `null` limit (remove the cap) and to leave a field out (unchanged). Pass the body object through as given; do not strip nulls.

## Task 2 — Workflow page (`LocalizationWorkflow.jsx`)

- `ALL_ACTIONS` becomes the eight strings in CONTRACT section 1, in that order.
- The run handler already shows failed and partial runs (red and amber). Extend the outcome reading: an outcome containing `skipped:` is a warning (amber) with the outcome text, even when nothing failed.
- A 409 from a run (AI switched off, or cap reached) is shown as a warning with the server's `detail`, not as a generic error. `err.status` and `err.problemDetails` are available on `ApiError`.
- Show the project's tier as a small badge beside the page title when `project.tier` is set, and "AI off" in amber when `project.aiEnabled` is false.

## Task 3 — Jobs page replaces Marketplace

- Rename `LocalizationMarketplace.jsx` to `LocalizationJobs.jsx` and rewrite it. Delete `LocalizationBidReview.jsx`.
- `LocalizationShell.jsx`: the fourth tab becomes `{ id: 'jobs', label: 'Jobs', path: '/lab-projects/localization/jobs' }`.
- `App.jsx`: route `/lab-projects/localization/jobs`; remove the two marketplace routes and their imports. Add a redirect from `/lab-projects/localization/marketplace` to the new path so old links work.

The page:

- Header line from `getAgreement`: tier, members per team, valid dates. When the project has no agreement (404), show an `EmptyState` saying the project has no service agreement and that operations assigns one.
- A table, one row per locale from `getJobs`: locale, vendor team alias, team size, strings, words, a progress bar from `completedPercent`, status, and one action:
  - `NotCreated` with a team: "Create job" → `createJob`.
  - `NotCreated` without a team: no button; text "No team assigned".
  - `SubmittedForReview`: "Approve" and "Send back".
  - otherwise no action.
- A 409 from any action is shown inline on that row with the server's `detail`.
- No price, bid or credit appears anywhere. Search `app/src` for "Credit", "bid", "Bid", "marketplace" and "Marketplace" after the change; only the redirect route may remain.

## Task 4 — Strings page (`LocalizationStrings.jsx`)

Remove everything that reads `qpsScore`, `rawMtQpsScore`, `rawMtText` or `needsReview`: the score column, the score badges in the detail panel, the raw-draft comparison and any filter on them. The response no longer has these fields (CONTRACT 2.2). Leave the rest of the page as it is. The review-action banner that mentions credits loses that wording.

## Task 5 — Vendor portal

- `VendorOpenJobs.jsx` becomes `VendorJobs.jsx`: the team picker reads `alias` from the roster (no rating); below it, the team's jobs from `vendorPortal.getJobs(vendorId)` with client alias, locale, counts, progress and status; a row links to the job page. Delete `BidSubmissionModal.jsx`. Update `useSelectedVendor.js`, `VendorPortalShell.jsx` and the route import in `App.jsx`.
- `VendorMyJob.jsx`: rows are vendor string rows (CONTRACT section 3). Show `score` as a 1 to 5 badge and `rawMtScore` beside the raw draft. Group the list by score in this order: not scored, 1-2, 3, 4, 5, with a count per group and a filter to show one group. The header shows the client alias, never a project name. The first-edit and submit behaviour is unchanged.
- Colours for the score badge: 1-2 red, 3 amber, 4-5 green, not scored grey, using the colour values already in these files.

## Task 6 — Operations page

New `app/src/pages/Localization/LocalizationOps.jsx`, route `/lab-projects/localization/ops`, wrapped as the admin route is: `<Layout><ProtectedRoute requireAdmin>…</ProtectedRoute></Layout>`. Add a link to it in `LocalizationShell.jsx` that is rendered only for an admin user; read how `ProtectedRoute` learns the role and use the same source.

Sections, each loading independently with its own loading and error state:

1. **Month and project selectors** (project list from `api.localization.getProjects()`, plus "All projects"; month as `yyyy-MM`, default the current UTC month).
2. **Caps** (only when a project is selected): one bar per cap kind, used against the limit, with the numbers; "No cap" when the limit is null; amber from 80 %, red at 100 %.
3. **Controls** (only when a project is selected): the AI switch and the two limits, saved with `updateControls`. An empty limit field means remove the cap and is sent as `null`; an untouched field is not sent.
4. **Usage this month**: a table per meter (calls, failed, cache hits, units, units out, cost) and the same per operation and per locale; a daily bar chart per meter drawn in SVG. When `ratesMissing` is not empty, an amber note: "No price set for: …; cost shown as 0 for these."
5. **Rates**: the list, and a form to add one (meter and unit kind as selects from the fixed strings, price per million, optional valid-from).
6. **Teams**: alias, real name, languages.
7. **Agreement** (only when a project is selected): tier select, valid-from, and a team select per project locale; saved with `saveAgreement`. Server 400s are shown beside the form.
8. **Recent events**: the newest 100 for the selection.

A 403 from any call shows one message for the whole page: "Operations access requires an administrator account."

Numbers: thousands separators for units; cost with 4 decimals.

## Task 7 — tests

Vitest, in `app/src/__tests__/`, mocking `api` as the existing component tests do:

1. Jobs page: a `NotCreated` row with a team shows "Create job"; without a team shows "No team assigned"; a `SubmittedForReview` row shows both review buttons; a 409 on create shows the server detail on that row.
2. Vendor job page: rows are grouped by score with the right counts; a row with `score: null` is in "not scored".
3. Workflow page: an outcome containing `skipped:` renders the warning style; a 409 run renders the server detail.
4. Operations page: caps bars show used and limit; clearing a limit field sends `null`; an untouched field is absent from the request body; a 403 shows the access message.
5. API client: `getUsage` builds the query string and omits unset parameters.

Do not edit existing tests unless a removed function forces it; list each edit.

## Finish

End with a short report: each task done or not done, every file created, changed, renamed or deleted, the result of the search in Task 3, any contract field you needed and did not have, and anything that could not be done as written. Never say a test or lint passes; you have not run it.
