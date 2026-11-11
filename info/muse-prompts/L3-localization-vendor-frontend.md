# L3 — Localization Lab: vendor portal corrections (React)

Run this after L1 and L2 have been reviewed and merged. Paste everything below this line into Muse Code, opened at the repository root.

---

You are working in the `scaler-education-journey` repository. The React app is in `app/` (Vite, plain JSX, inline `style={{}}` objects, `lucide-react` icons). The repo's `CLAUDE.md` is addressed to a different assistant; for this task you are authorised to edit the files listed under "Files you may change" and nothing else.

## Background

The vendor portal at `/lab-projects/localization/vendor` is a separate, deliberately limited shell: a translator picks who they are from a seeded roster (there is no login), sees open jobs in their languages, bids, and works only on jobs awarded to them. The design rule is "locked scope": a vendor must never see or edit anything outside their own awarded job.

The server now enforces the job lifecycle (it returns 403 for a bid in a language the vendor does not have, and 409 for actions in the wrong job state). The portal has to respect and display that.

## Read these first, in full

- `app/src/pages/Localization/Vendor/VendorPortalShell.jsx`
- `app/src/pages/Localization/Vendor/VendorOpenJobs.jsx`
- `app/src/pages/Localization/Vendor/VendorMyJob.jsx`
- `app/src/pages/Localization/Vendor/BidSubmissionModal.jsx`
- the `vendorPortal` section of `app/src/api/client.js`

## Files you may change

- the four files above
- new files under `app/src/pages/Localization/Vendor/`

## Changes

### 1. The selected vendor must survive navigation

`VendorOpenJobs.jsx` and `VendorMyJob.jsx` each hold their own `selectedVendorId` in `useState(null)`, and the shell resets it to the first roster vendor on every page load. So a user who picks "Kenji Sato" on Open Jobs and opens a job lands on My Job as "Maria Fischer".

- Create `app/src/pages/Localization/Vendor/useSelectedVendor.js`: a hook that loads the roster once with `api.vendorPortal.getRoster()`, keeps the selected vendor id in `sessionStorage`, defaults to the first roster vendor only when nothing valid is stored, and returns `{ roster, vendor, selectVendor, loading, error }`.
- Both pages and the shell use this hook. `VendorOpenJobs.jsx` line 26 fetches the roster a second time; remove that duplicate fetch.

### 2. My Job — enforce "only my awarded job"

`VendorMyJob.jsx` loads the strings of whatever job id is in the URL, for any vendor.

- Before loading strings, load `api.vendorPortal.getAwardedJobs(vendor.id)` and look for the job id from the URL. If it is not there, render an `EmptyState` saying the job is not assigned to the selected vendor, and do not call `getJobStrings`.
- Take the locale from that job. Remove the hard-coded `useState('de-DE')` on line 15; the `TARGET (xx)` column header and the page heading must use the job's locale.
- When the selected vendor changes while on this page, re-run the check.

### 3. My Job — read-only once submitted

- When the job status is `SubmittedForReview`, `Approved` or `Closed`, hide the pencil edit buttons and the "Submit for Review" button, and show one line of text stating the status.
- When the status is `NeedsRevision`, show one line of text saying the owner sent the job back for revision; editing and re-submitting stay enabled.
- If the server answers 409 to an edit or a submit, show its `detail` text inline. Do not use `alert()`.

### 4. Open Jobs and the bid modal

- If the server rejects a bid (403 language mismatch, 409 job no longer open, 409 duplicate bid, 400 invalid price), show its `detail` text inside the modal and keep the modal open.
- After a successful bid, mark that job's card as "Bid submitted" and disable its button for the rest of the session, so the user cannot trigger the duplicate-bid error by accident.
- The price input must reject zero and negative values before the request is sent.

### 5. Housekeeping

Remove unused imports and unused state in the files you touch.

## Do not

- Do not add the Provider Health icon, the project switcher or the live indicator to the vendor portal. Their absence is intentional.
- Do not add a Stage column to the My Job table. Its absence is intentional.
- Do not edit `app/src/api/client.js`, `app/src/App.jsx`, the owner pages, or anything under `api/`.
- Do not add a dependency or a CSS file. Keep the `var(--token, #fallback)` pattern for every colour.

## Finish

Run `npm run lint` and `npm run build` inside `app/`. Then report: the list of files changed, the command output, and anything in this prompt that did not match what you found in the code (report it; do not guess around it).
