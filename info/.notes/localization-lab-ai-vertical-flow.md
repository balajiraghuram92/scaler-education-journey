# Localization Lab — AI Vertical Flow (locked 2026-09-05)

> Companion to [localization-lab-plan.md](localization-lab-plan.md). Covers the
> UI-level decisions for Phase 3 (AI Vertical): Provider Health, QPS display,
> Auto-Routing's Needs Review state, Simulate Outage, and the tenant
> switcher/live-fallback toggle. The underlying AI logic (prompt construction,
> response parsing, routing decision) is out of scope here — that's the
> hand-written boundary already locked in the main plan. This document is UI
> surface only.

---

## 1. Provider Health panel

**Location (confirmed): slide-out panel from a top-nav icon**, not a
dedicated tab. A small status icon sits in the top nav (colored dot: sage
green = healthy, amber = degraded, red = down) — clicking it opens a
right-anchored drawer (same dimmed-overlay pattern as the string/snapshot
drawers) showing:

```
ProviderHealthSnapshot
  provider              "Google MT" | "LLM (Azure GPT)"
  p50LatencyMs
  p99LatencyMs
  errorRatePercent
  circuitState          Closed (healthy) | Open (tripped) | Half-Open (recovering)
```

One block per provider, stacked vertically in the panel. Available from every
screen (it's a nav-level icon, not route-scoped), reusing the drawer
interaction pattern rather than inventing a new one.

### 1.1 Simulate Provider Outage
A single icon-only button at the bottom of the Provider Health panel, per
provider: "Simulate Outage" — toggles that provider's `circuitState` to `Open`
on demand, for live interview demos rather than hoping for a real failure.
Toggling it back ("Resolve" / "Stop Simulating") is the same button in its
alternate state.

---

## 2. QPS score display

**Confirmed: a new "QPS" column in the main Strings table, and repeated in the
row-detail drawer.**

- Strings table: new column between TARGET and STAGE (or after STAGE — TBD at
  image-prompt time), showing a 0–100 number, colored sage if at/above the
  project's configured threshold, amber if below.
- Drawer: same QPS number repeated near the top, next to the stage indicator.
- This column only appears for AI-translated strings (Phase 3 active) — rows
  translated via the Marketplace (Phase 2.5) or manual entry (Phase 1) show
  an em-dash "—" in this column, since QPS is specifically the AI-as-judge
  score, not a universal quality metric applied to all translation sources.

---

## 3. Auto-Routing "Needs Review" state

**Confirmed: replaces the 4-dot track with a distinct flagged state, not a 5th
dot.**

When QPS is below the project's threshold, the row's stage indicator swaps
from the 4-dot track to a single amber flag/exclamation icon + "Needs Review"
text label (same position/size as the dot-track + label it replaces). This is
deliberately visually distinct — signaling "this one needs a human decision,
not just progression to the next mechanical stage" — rather than extending the
dot-track to 5 stages, which would create an inconsistency between
AI-routed rows (5 dots) and marketplace/manual rows (4 dots).

### 3.1 Filtering
The Strings table gets one quick-filter control (a small filter chip/toggle
near the table header, not yet visually designed) — "Show: Needs Review only"
— since this is the queue an interview demo would want to jump straight to.

---

## 4. Tenant switcher + live/fallback toggle

**Confirmed: added globally now, in the top nav, even before Phase 3 is
built.** Both controls sit in the top nav on every screen from here forward —
Strings, Workflow, Snapshots, Marketplace all need this in their nav bar, even
though the underlying tenant-switching/fallback logic doesn't exist until
Phase 3 wires it up.

```
Top nav (left to right): logo/wordmark → [Provider Health icon] → tenant
switcher dropdown → live/fallback toggle → user avatar
```

- **Tenant switcher**: dropdown showing current tenant, e.g. "Auroraline
  Automotive ▾" — switching tenants changes which project's data is shown.
  (Seeded demo tenants: Auroraline Automotive, Ferrix Industrial Systems,
  Pinnacle Arcade Co., plus 2 generic SaaS/mobile tenants, per the main plan.)
- **Live/fallback toggle**: a small two-state switch, e.g. "● Live" (sage) vs
  "○ Fallback" (muted grey) — reflects whether the app is currently serving
  real provider data or seeded demo-tenant fallback data. Before Phase 3 is
  built, this always shows "Live" and does nothing when clicked; it's present
  for visual/layout consistency, not functional yet.

**Consequence:** every reference image generated so far (Strings/drawer,
Marketplace tab + drawer + bid review, and the vendor-portal images) needs
this nav update to stay consistent going forward. See
[localization-lab-workflow-snapshots-flow.md](localization-lab-workflow-snapshots-flow.md)
§3 for the explicit callout on the Strings image specifically. The
owner-side Marketplace images need the same nav update; the vendor-portal
images do NOT (vendors don't get a tenant switcher or Provider Health icon —
that's owner/internal tooling).

---

## Status

All four Phase 3 UI-surface decisions locked (2026-09-05). No mockups
generated yet. Recommend: since the nav-bar change (tenant switcher +
live/fallback toggle + Provider Health icon) touches every owner-side screen,
the cleanest path is to (1) finalize one single "nav bar" reference crop
showing the new right-hand nav cluster, then (2) regenerate/patch the owner
screens against it, rather than re-deriving the nav bar independently in six
separate prompts and risking six slightly different versions of it.
