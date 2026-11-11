# L2 — Localization Lab: owner app corrections (React)

Run this after L1 has been reviewed and merged. Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository. The React app is in `app/` (Vite, plain JSX, inline `style={{}}` objects, `lucide-react` icons, no CSS framework). The repo's `CLAUDE.md` is addressed to a different assistant; for this task you are authorised to edit the files listed under "Files you may change" and nothing else.

## Background

The Localization Lab owner app lives at `/lab-projects/localization`. An audit against the original design spec found the deviations listed below. Fix them without changing any API route or adding any dependency.

## Read these first, in full

- `app/src/pages/Localization/LocalizationShell.jsx`
- `app/src/pages/Localization/LocalizationStrings.jsx`
- `app/src/pages/Localization/LocalizationWorkflow.jsx`
- `app/src/pages/Localization/LocalizationSnapshots.jsx`
- `app/src/pages/Localization/LocalizationMarketplace.jsx`
- `app/src/pages/Localization/LocalizationBidReview.jsx`
- `app/src/components/Localization/ProviderHealthPanel.jsx`
- the `localization` section of `app/src/api/client.js`
- `app/src/components/common/StateViews.jsx`

## Files you may change

- the six page files and the panel listed above
- new files under `app/src/pages/Localization/` or `app/src/components/Localization/`

## Changes

### 1. One source of truth for the selected project

Today every page hard-codes `useState('auroraline-hud-v3')`, the Bid Review page hard-codes the same slug in an API call, and the shell's header hard-codes the project name, "English (en-US)" and "5 Locales". The project dropdown in the shell changes nothing.

- Create `app/src/pages/Localization/useLocalizationProject.js`: a hook that reads the selected slug from the `project` URL query parameter (falling back to the first project returned by `api.localization.getProjects()`), loads that project with `api.localization.getProject(slug)`, and returns `{ slug, project, projects, loading, error, selectProject }`. `selectProject(slug)` updates the query parameter and keeps any other query parameters.
- The shell and all five pages use this hook. Remove every hard-coded slug.
- The shell's header shows the loaded project's `name`, its `sourceLocale`, and the real number of locales. Tab links and the Bid Review back link keep the `project` query parameter.
- Selecting another project in the dropdown must make the current page reload its data for that project.

### 2. Strings page — locales come from the project

`LocalizationStrings.jsx` lines 17–23 hard-code five locales in state and never update them. Use the locales from the loaded project. The default selected locale is the `locale` query parameter if present, otherwise the project's first locale.

### 3. Strings page — the drawer repeats the stage indicator and the QPS score

The table shows a four-dot track plus a one-word label, or an amber flag plus "Needs Review" when `needsReview` is true. The drawer (lines 511–519) shows only the stage as text.

- Extract the indicator into `app/src/components/Localization/StageIndicator.jsx` and use it in both the table and the drawer, so they cannot drift apart.
- In the drawer, next to the indicator, show the QPS score when the row has one, coloured with the same rule as the table (`>= 70` sage, otherwise `#A6772C`).

### 4. Strings page — review toolbar

When the page is opened from the Marketplace with `?locale=…&jobId=…` it shows an Approve / Send Back toolbar.

- Make both buttons icon-only with a `title` tooltip ("Approve Submission", "Send Back for Revision"). Remove the text labels.
- Show the toolbar only when that job's current status is `SubmittedForReview`. Read the status from `api.localization.getMarketplaceOverview(slug)`.
- After either action succeeds, hide the toolbar and remove `jobId` from the URL.
- A failed action is currently rendered inside the green success banner. Render failures in the same red style the drawer's `saveError` uses.

### 5. Shell — nav cluster

- The Provider Health control must be a small circular icon-only button: just the coloured dot, with the status in the `title` tooltip. Remove the `Activity` icon and the "Provider Health" text.
- Dot colour: red if any provider's circuit is `Open`, amber `#A6772C` if any is `HalfOpen`, otherwise sage. Keep the existing 30-second refresh.
- Keep the "Live" indicator and the "Vendor Portal" link as they are.

### 6. Workflow page

- Last-run line (lines 319–327): render `Last ran {relative time} — {lastRunOutcome}`, for example `Last ran 2h ago — 12 strings affected`. Search `app/src` for an existing relative-time helper and reuse it; if none exists, add a small local function (minutes, hours, days).
- The Run button and the Add Step control must be icon-only with a `title` tooltip. Remove their text labels.
- After L1, the API returns 400 for an unknown action and 409/501 for some runs. Make sure every non-2xx response shows the server's `detail` text in the existing per-step notice.

### 7. Marketplace page and Bid Review page

- `LocalizationMarketplace.jsx` line 46 uses `alert()`. Replace it with an inline error message inside the drawer; the server's 409 `detail` text must be visible to the user.
- Status text colours, per the spec: sage and bold for `Open` and `Approved`, muted grey for `Not Posted`, plain ink for everything else. `SubmittedForReview` is currently amber; make it plain ink.
- `LocalizationBidReview.jsx` line 110 falls back to invented numbers (`6` strings, `1240` words, `180`–`240`). Remove the fallbacks; show the loading state until the real job data is available, and an `ErrorState` if the job is not found in the overview.
- On the Bid Review page, show the award button only while the job status is `Open`.

### 8. Tables follow the "ruled table" spec

On Strings, Snapshots, Marketplace and Bid Review, the table wrapper has `borderRadius: '8px'` and the header row has a tinted background. The spec is a ruled table: 1px row dividers, no rounded card, no header tint, no shadow. Remove the radius and the tint; keep the row dividers.

### 9. Housekeeping

Remove unused imports in the files you touch (for example `AlertTriangle`, `CheckCircle` in `LocalizationStrings.jsx`).

## Do not

- Do not edit `app/src/api/client.js`, `app/src/App.jsx`, anything under `app/src/pages/Localization/Vendor/`, or anything under `api/`.
- Do not add a dependency, a CSS file, or a state library.
- Do not change colours, fonts or spacing beyond what the items above require. Keep the `var(--token, #fallback)` pattern for every colour.
- Do not build a "Needs Review only" filter, a QPS threshold setting, or anything not listed here.

## Finish

Run `npm run lint` and `npm run build` inside `app/`. Then report: the list of files changed, the command output, and anything in this prompt that did not match what you found in the code (report it; do not guess around it).
