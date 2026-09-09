# Session Summary — Phase 0 Deploy Debugging (2026-09-09 → 2026-09-10)

> **Read this first in a new chat about the AI Learning Agent / AI tutor
> infra.** This supersedes
> [SESSION-2026-09-08-phase0-infra-and-deploy.md](SESSION-2026-09-08-phase0-infra-and-deploy.md)
> as the most recent record — that file covers how Phase 0's code/DNS/TLS
> got built; this one covers what happened trying to actually *run* it in
> production, ending with **one confirmed unresolved item** at the bottom.
> Written to stand alone — no other conversation context assumed.

**Session span:** 2026-09-09 evening → 2026-09-10
**Scope:** debugging the first real production runs of the Phase 0
pipeline built in the prior session — CI test/lint failures, a real React
bug, and a repo-visibility bug in the deploy script fetch.

---

## ⚠️ Still open as of this writing — fix this first

**Confirmed root cause of the current blocker** (log captured live during
this session, from the `c617bc8` run): the pipeline got much further than
before — all four images (`api`, `app`, `ai-agent`, `runner`) pulled
successfully on EC2, the pre-migration Postgres backup uploaded to S3 —
then died running the API's `--migrate` step:
```
Unhandled exception. System.InvalidOperationException: Production configuration error: Auth:JwtSigningKey must be set.
   at Program.<Main>$(String[] args) in /src/api/Program.cs:line 150
```

**Cause:** `scripts/bootstrap-single-ec2.sh` only fetches the app config
from SSM Parameter Store `if [ ! -f /etc/studytracker/api.env ]` — i.e. it
silently reuses whatever's already on disk instead of refreshing it. A
stale copy already sits on the EC2 host (Postgres creds in it clearly work,
since the backup step succeeded), but it's missing (or has a mismatched
key name for) `Auth__JwtSigningKey`. **This isn't just a `.NET` migration
problem** — `start_ai_agent()` reads the exact same file for the exact same
key via a hard-fail `env_value Auth__JwtSigningKey` lookup, so even once
migrations are unblocked, the deploy would fail again at that step for the
identical reason unless this is fixed first.

**Not yet fixed as of end of session** — this needs manual action on the
EC2 host/SSM Parameter Store (not a code change):
1. `sudo docker inspect studytracker-api --format '{{range .Config.Env}}{{println .}}{{end}}' | grep Auth__JwtSigningKey` — get the key the *currently live* container already trusts (auth works on the live site today, so this must be a valid value — reuse it, don't rotate it, or every existing session gets invalidated).
2. `sudo grep -c '^Auth__JwtSigningKey=' /etc/studytracker/api.env` — confirm it's actually missing locally.
3. `aws ssm get-parameter --name /neuralascent/prod/api-env --with-decryption --query Parameter.Value --output text | grep -c '^Auth__JwtSigningKey='` — check whether SSM (the real source of truth) has it.
4. If SSM has it but the local file doesn't: `sudo rm /etc/studytracker/api.env` so the next run re-fetches fresh. If SSM is also missing it: add it there first (preserving every other existing line), using the value from step 1, then also remove the stale local file.
5. Re-trigger via `workflow_dispatch` — do not run the deploy script by hand on the box, so the rollback trap and health checks stay in effect.

Separately (not urgent): `tutor.neuralascent.top` was still serving the OLD
config at last check this session (`/health` → plain "healthy" text, not
FastAPI JSON; `/me` → the SPA's `index.html`, not JWT claims; `Server:
nginx`, no `uvicorn`) — expected, since no run has succeeded all the way
through yet. Re-check with the same curl commands once the above is fixed
and a full green run completes.

Also worth a non-urgent follow-up once unblocked: the `[ ! -f ... ]` guard
in `bootstrap-single-ec2.sh` means any *future* addition to the SSM
parameter will silently never reach the box until someone thinks to delete
the stale file by hand — consider changing it to always fetch fresh rather
than cache.

---

## What this session found and fixed, in the order it happened

### 1. `.NET` test-compile errors (blocking "Verify API")
Two pre-existing bugs in the test project, never caught before because this
CI job's `if:` condition (`workflow_dispatch` or `[deploy]` in the commit
message) meant it had essentially never run to completion before this
session's work:

- **Namespace collision**: the API project has its own namespace literally
  named `StudyTracker.Api.Options`, which shadowed
  `Microsoft.Extensions.Options.Options` (the static `.Create()` factory)
  wherever both were `using`-imported in test files. Fixed by fully
  qualifying `Microsoft.Extensions.Options.Options.Create(...)` at both call
  sites (`TotpSecretProtectorTests.cs`, `AuthAndUserManagementTests.cs`).
- **Stale constructor call**: `TotpSecretProtector`'s constructor gained an
  `IHostEnvironment env` parameter at some point, but its test still called
  it with one argument. Fixed by adding a minimal inline
  `FakeHostEnvironment : IHostEnvironment` test double (no new NuGet
  packages) and passing it in.
- Committed as `3c94db3` (`[deploy] fix test-compile errors and
  cross-platform crypto exception assertion`).

### 2. Cross-platform crypto exception assertion (same commit)
`Decrypt_TamperedPayload_ThrowsCryptographicException` used
`Assert.Throws<CryptographicException>`, which requires an **exact** type
match. On macOS (Apple CryptoKit interop, confirmed via the stack trace's
`Interop.AppleCrypto.AesGcmDecrypt`), AES-GCM tag mismatches throw
`AuthenticationTagMismatchException` — a valid subclass, but not an exact
match, so the strict assertion failed there while presumably passing on
Linux CI runners. Fixed by switching to `Assert.ThrowsAny<CryptographicException>`
(the file already used this exact pattern elsewhere, for
`ArgumentException`). Not a production bug — `catch (CryptographicException)`
anywhere in real code still catches the subclass fine.

**Verified locally after the fix:** 134 passed, 1 skipped (Docker exercise
integration test — expected skip locally), 0 failed.

### 3. Real React Rules-of-Hooks crash (blocking "Verify frontend" lint)
`app/src/pages/Localization/Vendor/BidSubmissionModal.jsx` had an early
`if (!isOpen || !job) return null;` **before** four `useState` calls. Its
parent (`VendorOpenJobs.jsx`) renders this component unconditionally and
only toggles `isOpen`/`job` props — it never unmounts it — so this was a
genuine "Rendered more hooks than during the previous render" runtime crash
on every modal open, not just a lint nicety.

Fix required three parts, not just reordering:
1. Moved all four `useState` calls (and a new `useEffect`) above the
   conditional return, so hooks are always called in the same order.
2. Guarded `defaultPrice` against a `null` `job` (`job ? Math.round(...) : 0`)
   — needed because the component's very first mount happens with `job`
   still null, before any job is selected.
3. Added a `useEffect` keyed on `job?.id` to reset `proposedPrice`/`note`/
   `error` each time a *different* job opens — needed because, since the
   component never unmounts, `useState`'s initializer only ever runs once,
   so without this the form would silently carry stale values from
   whichever job was open previously.
4. Dropped an unused `CheckCircle` import, flagged separately by lint.

Committed as `86b1fe7` (`fix builder failures on git actions`).

**Verified locally after the fix:** `npm run lint` exit 0 (0 errors, ~50
pre-existing unrelated unused-import/variable warnings remain, non-blocking),
`npm run test` 5 files / 34 tests passed, `npm run build` succeeded.

### 4. Private-repo curl-fetch 404 (blocking the actual EC2 deploy step)
With the two `.NET`/frontend fixes in and CI's build steps all green
(confirmed: the `ai-agent` image itself built and pushed successfully —
its digest is visible in the failed run's own SSM command parameters), the
**"Deploy immutable release to EC2" step failed**:
```
curl: (22) The requested URL returned error: 404
```
fetching `bootstrap-single-ec2.sh` from `raw.githubusercontent.com` with
**no authentication**. Root cause, confirmed directly:
```
raw.githubusercontent.com/.../<sha>/scripts/bootstrap-single-ec2.sh → 404 (unauthenticated)
api.github.com/repos/balajiraghuram92/scaler-education-journey        → 404 (unauthenticated)
```
GitHub returns `404` (not `401`/`403`) for a private repo's contents when
unauthenticated, to avoid leaking the repo's existence. **This repo is
private**, and this SSM-command curl fetch was never authenticated — a
pre-existing bug in `deploy-api.yml`, unrelated to anything built in the
prior Phase 0 session, that simply never got exercised until a run finally
reached this far.

**Fix**: added a `GITHUB_TOKEN`-authenticated header to both `curl` calls
(the job already had `permissions: contents: read`, so `secrets.GITHUB_TOKEN`
had the access needed — it just wasn't being used):
```
"curl -fsSL -H \"Authorization: token ${{ secrets.GITHUB_TOKEN }}\" $SCRIPT_BASE/scripts/bootstrap-single-ec2.sh -o /tmp/bootstrap-single-ec2.sh",
"curl -fsSL -H \"Authorization: token ${{ secrets.GITHUB_TOKEN }}\" $SCRIPT_BASE/scripts/deploy-single-ec2.sh -o /tmp/deploy-single-ec2.sh",
```
Committed as `c617bc8` (`[deploy]  fixed docker deploy image`) — confirmed
on disk to match exactly. This was a hand-edit to `.github/workflows/*`
(the "Gemini"/local-LLM tool used for other edits this whole project
declines to touch workflow files directly, so these have consistently been
manual edits reviewed by Claude before commit, same pattern as before).

---

## Current confirmed state (as of end of session)

| Item | Status |
|---|---|
| `.NET` test suite | ✅ 134/135 passing (1 expected skip), verified locally |
| Frontend lint/test/build | ✅ all three clear locally |
| `ai-agent` Docker image | ✅ confirmed built and pushed to `ghcr.io` (digest seen in a run's own params) |
| GitHub Actions build steps (api/app/ai-agent/runner + platform verify) | ✅ all passed in the run that hit the 404 |
| EC2 deploy step | ❌ failed on that run (private-repo 404); fix pushed as `c617bc8` but **not yet confirmed working** |
| `tutor.neuralascent.top` live behavior | ❌ still the OLD config — plain-text `/health`, SPA HTML on `/me`, `nginx` server header, no `uvicorn` anywhere |

**This session did not get to see a fully green run.** The very last thing
done was pushing the `GITHUB_TOKEN` auth fix and confirming (via direct
`curl`) that the live site hasn't changed yet.

---

## Immediate next step for a new session

1. **Fix the stale `/etc/studytracker/api.env` / SSM `Auth__JwtSigningKey`
   issue described above** — this is confirmed, diagnosed, and just needs
   the manual EC2/SSM steps carried out (see the ⚠️ section above for the
   exact commands). This is the actual current blocker, not a mystery to
   re-investigate.
2. Re-trigger via `workflow_dispatch` and read the full log again — the
   404 (private-repo curl auth) is confirmed fixed, and the JWT-key issue
   should be too if step 1 was done correctly. Don't assume anything else
   is clean — read the whole log.
3. Once it succeeds: verify with curl (`/health` → `{"status":"ok"}`, `/me`
   without a cookie → `401` JSON, `/me` with a real `na_auth` cookie →
   decoded JWT claims, `curl -I` → `Server: uvicorn`).
4. Once fully green, this closes out Phase 0's "actual deploy" checkbox in
   [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)
   — update it (it currently still says "pending" for this).
5. The two-planning-track question flagged in the prior session's summary
   (`ai-copilot-session-summary-for-opus5.md` / `copilot-week1-2-*.md` vs.
   `ai-learning-agent-ARCHITECTURE.md`) was **not raised or resolved this
   session either** — still outstanding, still worth asking the user
   directly before any Phase 1 content work begins.
6. Mac Studio SSH tunnel + local embedding/reranking service, and the
   admin-panel backend toggle — both still entirely unbuilt, per the prior
   session's summary. Nothing changed on these this session.

---

## Incidental finding (not acted on, informational only)

`git status` at various points this session showed `api/obj/*` build
artifacts as tracked-and-modified, despite `.gitignore` correctly listing
`/api/bin` and `/api/obj`. These were tracked before the ignore rule
existed (gitignore doesn't retroactively untrack files). Recommended
cleanup, not done: `git rm -r --cached api/obj api/bin` in its own commit.
Not blocking anything — just noisy local diffs after every local build.

---

## File index (for a cold-start session)

| File | What it's for |
|---|---|
| **This file** | This session's debugging log — read first for "what's currently broken/pending" |
| [SESSION-2026-09-08-phase0-infra-and-deploy.md](SESSION-2026-09-08-phase0-infra-and-deploy.md) | Prior session — how Phase 0's code, DNS, and TLS got built in the first place |
| [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md) | Full project context — who the user is, why this project exists, all locked architecture decisions |
| [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md) | Full technical spec, including §2.4 (local inference host, SSH tunnel, routing/cutover) |
| [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) | Checkbox-level phase tracker — **not yet updated with this session's findings; do that once the deploy is confirmed green or still broken** |
| `ai-copilot-session-summary-for-opus5.md`, `copilot-week1-2-*.md` | The **other**, still-unreconciled planning track — see warning in the prior session's summary |
| `CLAUDE.md` (repo root) | Repo-wide rules: no direct source edits outside `info/.notes/`/`exercises/`, prompt-workflow for code changes, AI-vertical vs AI-integration scope boundary |
