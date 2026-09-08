# Session Summary — Phase 0 Infra Build (2026-09-08)

> **Read this first in a new chat about the AI Learning Agent / AI tutor
> infra.** This is a condensed, stand-alone record of one working session:
> what was decided, what was built, what broke and got fixed, and exactly
> what's left. Written so a fresh Claude session needs no other context to
> pick up from here.

**Session date:** 2026-09-08
**Scope of this session:** Phase 0 (infra & routing scaffold) of the AI
Learning Agent project — see
[ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md) §2.4
and [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)
for the full spec this session executed against.

---

## ⚠️ Read this before anything else: two parallel planning tracks exist

While reviewing files touched by a commit mid-session, I found **a second,
separate planning track** already in `info/.notes/` that overlaps with —
and may conflict with — the work in this session:

- `ai-copilot-session-summary-for-opus5.md`
- `copilot-week1-2-design-overview.md`
- `copilot-week1-2-fastapi-foundation-prompt.md`
- referencing `Chatbot-implementation/architecture-notes/neuralascent-chatbot-hld-python-LangChain.md`

That track describes a **26-week AI-transition plan**, a different HLD
("naive RAG baseline, hand-coded by user, no auth/no reranking for weeks
1-2"), and appears to have been produced in conversation with a different
assistant/session ("Opus 5" / "AI Copilot"). It is **not the same document**
as this session's authoritative
[ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md) (the
Pydantic AI + LangGraph + FastAPI, 6-agent-roster, Muse/Nova/Gemini-cascade
plan this session built Phase 0 for).

**This was not reconciled during this session — the user has not yet said
which plan is authoritative going forward, or whether they're meant to
merge.** Do not assume either supersedes the other. Ask the user directly
before writing anything that assumes one plan's architecture over the
other's. The `ai-agent/` FastAPI skeleton and deploy plumbing built in this
session are real and committed regardless of how that's resolved — they're
infra, not architecture-locked to either plan — but Phase 1's actual content
(RAG design, ingestion pipeline shape, etc.) should not proceed until this
is cleared up.

---

## What this session actually built

**Goal:** stand up `tutor.neuralascent.top` as a working, authenticated,
empty FastAPI service reachable through the existing Nginx/EC2 setup, with
zero disruption to the live `.NET`/React site — Phase 0 of the build
tracker.

### Decisions made this session (carried over from a prior session on
another machine, then refined here)

1. **Frontend/backend for the new tutor UI:** fresh TypeScript frontend +
   Python FastAPI backend — **no reuse** of the existing `app/` React/JSX or
   the `.NET` API for the new tutor UI. (Not yet built — Phase 1 concern.)
2. **Embedding + reranking:** local-first on a **Mac Studio M1 Max, 32GB**,
   reached via SSH tunnel, UPS-backed always-on — with **manual toggle, no
   automatic fallback**. Global admin-panel toggle
   (`embedding_backend`/`reranker_backend`: local | api) plus a per-account
   `force_api_backend` override so interview demos never depend on the home
   Mac/WiFi. Models: `BAAI/bge-m3` (embedding) + `bge-reranker-v2-m3`
   (reranking), mirrored on **Deepinfra** as the same-weights API fallback.
   **Not yet built** — the Mac-side service, the tunnel, and the admin
   toggle are all still open (see Outstanding, below).
3. **Routing/cutover plan:** `neuralascent.top` keeps serving `.NET`
   unchanged through Phase 0–2; a new subdomain (`tutor.neuralascent.top`)
   carries the new stack in the meantime; a later Nginx flip (Phase 3) moves
   the whole domain over once the new stack has feature + auth parity.
4. **Auth is not duplicated** — the new FastAPI service validates the
   *existing* `.NET`-issued JWT (HS256, issuer `neuralascent`, audience
   `neuralascent-app`, cookie `na_auth`) rather than building a second login
   system.

### What got built and verified this session

| Piece | File(s) | Status |
|---|---|---|
| `ai-agent` FastAPI skeleton | `ai-agent/main.py`, `ai-agent/Dockerfile`, `ai-agent/requirements.txt` | ✅ Built, committed. `/health` (open) + `/me` (JWT-protected, echoes decoded claims) |
| New Nginx routing | `app/default.conf.template` | ✅ Committed — adds `tutor.${DOMAIN_NAME}` server blocks (HTTP redirect + HTTPS proxy to `ai-agent:8000`), existing blocks untouched |
| Local-dev compose wiring | `docker-compose.yml` | ✅ Committed — `ai-agent` service on `backend-net`, no public port, `app` now depends on it |
| CI image build | `.github/workflows/deploy-api.yml` | ✅ Committed (commit `f2db042`) — builds/pushes `ai-agent` image, extends the platform-verification loop, passes `AI_AGENT_IMAGE`/`AI_AGENT_REF` into the SSM deploy command |
| Production deploy script | `scripts/deploy-single-ec2.sh` | ✅ Committed (commit `c3742f6`) — `start_ai_agent()`, digest/platform verification, rollback handling, health check, all mirroring the existing `api`/`app` pattern |
| DNS | GoDaddy, `tutor` A record | ✅ Done — `tutor.neuralascent.top` resolves to the same IP as the root domain |
| TLS | EC2, manual `certbot --expand` | ✅ Done — certificate SAN now covers `neuralascent.top` **and** `tutor.neuralascent.top` (verified via `openssl s_client`), expires 2026-12-07 |
| **Actual deploy run** | — | ❌ **Not done yet.** Code is on `main`; no pipeline run has actually built/pushed the `ai-agent` image or started it on EC2. `tutor.neuralascent.top` currently still serves whatever the *old* Nginx config on the box has (the React SPA index, not FastAPI) |

### Corrections made mid-session (worth knowing before touching this infra again)

- **Production deployment does NOT use `docker-compose.yml`.** That file is
  dev-only (`scripts/local-stack.sh` etc.). Production is GitHub Actions →
  build/push to `ghcr.io` → AWS SSM `RunShellScript` → `curl`s
  `bootstrap-single-ec2.sh` + `deploy-single-ec2.sh` straight from
  `raw.githubusercontent.com` at the commit SHA → plain `docker run`
  commands on the EC2 host. No `git clone` anywhere in that path.
- **`python:3.12-slim` is Debian, not Alpine** — "slim" means a stripped
  Debian, not a different distro. `apt-get` is correct there regardless of
  the EC2 host being Amazon Linux 2023 (RPM-based) — the container image's
  OS is independent of the host OS; the host only needs a compatible
  kernel + container runtime.
- **The `ai-agent` healthcheck needs `curl` installed explicitly** —
  `python:3.12-slim` doesn't ship it. Missing this would have left `ai-agent`
  permanently "unhealthy," which would have blocked `app` from ever starting
  (`depends_on: ai-agent: condition: service_healthy`). Fixed in the
  Dockerfile.
- **TLS is issued via `certbot ... certonly --standalone`**, not
  `certbot --nginx`. The deploy script only runs `certonly` (which is where
  the new SAN needed adding) on a *first-ever* certificate for the domain —
  once a cert already exists, it only ever runs `renew`, which does **not**
  add new SANs. This is why the SAN had to be added with a **one-time manual
  `certbot --expand` command** run directly on the EC2 host — the code fix
  alone would never have fixed an already-existing certificate.
- Two small syntax slips were caught in review before being applied to
  production: a missing `in` in a bash `for image in ...; do` loop, and a
  stray bare newline risk from message word-wrapping. Both fixed.
- Gemini (the "AGY" tool used for these edits) declined to touch
  `.github/workflows/*.yml` on its own — that file was hand-edited by the
  user each time, with Claude reviewing the diff before commit.

---

## Outstanding — what's next

In rough order:

1. **Trigger the actual deploy.** Code is ready; nothing has run yet. Go to
   **GitHub Actions → "Build and Deploy to AWS" → Run workflow** (manual
   `workflow_dispatch`, not a `[deploy]` commit message) so it can be
   watched live for this first run touching new infra.
2. **Verify end-to-end after that deploy:**
   `curl https://tutor.neuralascent.top/health` → `{"status":"ok"}`, and
   `https://tutor.neuralascent.top/me` with a real logged-in session's
   cookie/bearer token → decoded JWT claims (proves the shared-auth design
   actually works, not just that it compiles).
3. **Mac Studio embedding/reranking service** — none of this is built yet:
   the `autossh` reverse tunnel, the `launchd` agent, the local `bge-m3` /
   `bge-reranker-v2-m3` service on the Mac, and the Deepinfra API-key
   fallback. See
   [ai-learning-agent-ARCHITECTURE.md §2.4](ai-learning-agent-ARCHITECTURE.md)
   for the exact tunnel command and restricted-key setup already specified.
4. **Admin-panel toggle + health indicator** — real application code
   touching the existing admin dashboard (`embedding_backend`/
   `reranker_backend` toggle, `force_api_backend` per-account override,
   Mac/tunnel reachability indicator). Not started.
5. **Resolve the two-planning-track question above** before starting Phase
   1's actual content/RAG work.
6. Once Phase 0 is fully done, Phase 1 begins: content ingestion pipeline,
   pgvector setup, single Tutor Agent, golden eval set — see the build
   tracker for the full checklist.

---

## File index (for a cold-start session)

| File | What it's for |
|---|---|
| **This file** | Session log for 2026-09-08's Phase 0 infra work — read first for "what just happened" |
| [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md) | Full project context: who the user is, why this project exists, all locked architecture decisions — read first for "what is this project" |
| [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md) | Full technical spec, including §2.4 (local inference host, SSH tunnel, routing/cutover — the spec this session executed) |
| [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) | Checkbox-level phase tracker — **not yet updated with this session's Phase 0 progress; do that before starting new work** |
| [neuralascent-work-status.md](neuralascent-work-status.md) | Top-level status across all Neuralascent tracks |
| `ai-copilot-session-summary-for-opus5.md`, `copilot-week1-2-*.md` | The **other**, unreconciled planning track — see the warning at the top of this file |
| `CLAUDE.md` (repo root) | Repo-wide rules: no direct source edits outside `info/.notes/`/`exercises/`, prompt-workflow for code changes, AI-vertical vs AI-integration scope boundary |

---

## Immediate action for whoever reads this next

The build tracker's Phase 0 checkboxes are stale (still show most items
unchecked despite the work above being done and committed). Before doing
anything else, update
[ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)'s
Phase 0 section to reflect: Nginx block ✅, JWT middleware ✅, FastAPI
skeleton ✅ (deployed to EC2 still ❌ pending the actual pipeline run), DNS
✅, TLS/SAN ✅. Then raise the two-planning-track question with the user
before going further.
