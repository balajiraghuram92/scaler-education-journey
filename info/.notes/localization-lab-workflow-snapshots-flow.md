# Localization Lab — Workflow & Snapshots Flow (locked 2026-09-05)

> Companion to [localization-lab-plan.md](localization-lab-plan.md). Covers the
> two remaining Phase 1 screens that were never individually specced: the
> Workflow tab (config-driven Orchestrator UI) and the Snapshots tab (Build
> Snapshot ledger). The Strings tab (3rd Phase 1 screen) already has an
> approved reference image and needs no further discussion here — except the
> nav-bar addition noted in §3 below, which affects it retroactively.

---

## 1. Workflow tab

### 1.1 What it edits
A single ordered pipeline per project — a flat list of Trigger → Action steps,
same semantic model as Phrase Orchestrator, expressed as a structured list (no
node canvas, per the earlier locked decision).

```
WorkflowStep
  id
  order              integer, determines execution order
  trigger            e.g. "On Manual Click" (Phase 1), "On String Translated" (later)
  action             Phase 1: Mark Translated | Send to Review | Approve
                     Phase 2+: Auto-Translate via Google MT | Post to Marketplace
                     Phase 3: Run MT Optimize | Score QPS | Auto-Route
  condition          optional, e.g. "QPS < threshold" (Phase 3 only)
  lastRun            { timestamp, outcome, affectedCount } — see 1.3
```

### 1.2 Reordering
Each step row has small **up/down arrow icon buttons** (not a drag handle) —
purely structured-settings interaction, zero drag physics, consistent with
rejecting the visual node-canvas builder for the same risk reason.

### 1.3 Execution history (confirmed: shown inline)
Each step row displays a small muted-grey line beneath its config summary:
`Last ran 2h ago — 12 strings affected`. This means `WorkflowStep` needs a
`lastRun` field and the backend needs to record one execution summary per step
per run (not a full audit log — just the most recent outcome). Keep this
lightweight: no history browsing/timeline UI in scope, just the single latest
line per step.

### 1.4 Screen layout
- Numbered rows (matching the plan's "numbered Workflow Settings rows"),
  ruled-table style consistent with Strings/Snapshots — NOT cards.
- Each row: step number, Trigger dropdown, Action dropdown, optional Condition
  field (Phase 3 only, hidden/absent in Phase 1), up/down reorder icons,
  delete icon, and the `lastRun` summary line beneath.
- An "Add Step" icon-only control at the bottom of the list.
- No separate "Save" button needed if each field commits on change (simplest);
  flag as an open implementation detail for the build prompt, not a design
  question.

---

## 2. Snapshots tab

### 2.1 What a snapshot is
Mirrors dossier §28's `sourceRevision + localizationRevision + config →
deterministic build` model.

```
BuildSnapshot
  id
  createdAt
  sourceRevision         e.g. a project/content revision identifier
  localizationRevision   e.g. a translation-state revision identifier
  config                 workflow/pipeline config at time of cut, read-only
  perLocaleCounts[]       { locale, approvedStringCount } — one entry per locale
                          in the project at cut time
```

### 2.2 Scope of "Cut Build Snapshot" (confirmed)
**Always snapshots every locale in the project** — one icon-only button, no
locale picker. Matches "what shipped is what was tested": a snapshot is a
whole-project checkpoint, not a partial one. If a later interview question
asks about partial/staged releases, the honest answer is "out of scope for
this build — the model treats a release as all-or-nothing per project."

### 2.3 Row detail (confirmed: reuses the locked drawer)
Clicking a snapshot row opens the same dimmed-overlay drawer pattern already
used for string rows: heading = snapshot id/version (monospace, same
convention as the string Key heading), body = read-only manifest block
showing `sourceRevision`, `localizationRevision`, `config` summary, and the
per-locale approved-string counts as a small table-within-drawer. No editable
fields — a snapshot is immutable once cut.

### 2.4 Screen layout
- "Closing Entries"-style ruled table (per the plan), one row per snapshot,
  columns: snapshot id (monospace) | created at | source revision | # locales
  included | total approved strings.
- "Cut Build Snapshot" icon-only button (megaphone-style action icon
  inconsistent — use a distinct icon, e.g. an outlined camera/checkmark-seal
  icon, TBD at image-prompt time) top-right of the table.

---

## 3. Nav-bar consequence (affects the already-approved Strings image)

Per the Phase 3 discussion (see
[localization-lab-ai-vertical-flow.md](localization-lab-ai-vertical-flow.md)),
the tenant switcher + live/fallback toggle were confirmed to be **added
globally now**, not deferred to Phase 3. This means:

**The already-approved Strings/drawer reference image needs a nav-bar
revision** — it currently shows only the logo + avatar, with no tenant
switcher or live/fallback toggle. Every future reference image (Workflow,
Snapshots, and any Strings re-render) must include this in the top nav, and
the original Strings image should be treated as superseded on this one point
even though everything else about it stays locked.

---

## Status

Both screens fully specified (2026-09-05). No mockups generated yet for
either. Recommend generating Workflow and Snapshots reference images together
with a corrected Strings nav-bar (to restore full consistency across all
Phase 1 images) before writing the Phase 1 frontend build prompt.
