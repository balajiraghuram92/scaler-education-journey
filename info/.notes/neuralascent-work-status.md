# Neuralascent — Work Status & Resume Point

> **SUPERSEDED 2026-09-06** — see
> [SESSION-2026-09-AI-chatbot-planning-and-auth-build.md](SESSION-2026-09-AI-chatbot-planning-and-auth-build.md)
> for the complete, up-to-date record (the auth/TOTP/chat build described below finished,
> survived a regression scare, and is now committed to `main`; Localization Lab — Track 2
> below — is also since completed and committed, in a different chat session). This file is
> kept only as a historical snapshot of mid-build state; read the file above first.

**Last updated:** 2026-09-04. **Purpose:** so a future session (or you) can pick this back up without re-explaining anything. Read this file first before touching any of the auth/TOTP/chat/AI-vertical work again.

**Why paused now:** switching to the Localization project to make full use of Claude's 50%-extra-token offer, active through **Sept 13, 2026**. Track 1 below is functionally complete and just needs the user's own build/smoke-test pass — nothing here is blocking that switch.

---

## The four tracks, and where each one stands

### 1. Neuralascent AI-integration infra (auth + TOTP + AI chat) — DONE, pending your own final verification

Full implementation exists on disk (see `git status` — everything under `api/Endpoints/{Auth,Admin,Chat}Endpoints.cs`, `api/Services/Auth/`, `api/Services/Email/`, `api/Models/{AppUser,MfaChallenge,ChatConversation,ChatMessage}.cs`, `api/Options/*.cs`, and the matching frontend in `app/src/pages/{AuthPage,AdminDashboard}.jsx`, `app/src/context/AuthContext.jsx`, `app/src/components/common/{ProtectedRoute,ChatWidget}.jsx`). `task_tracker.md` Phases 41-43 document it accurately.

- Self-serve email signup → admin-approval-only dashboard (with automated approve/reject emails) → mandatory TOTP (Google Authenticator-compatible, RFC 6238) second factor for every user including the admin → httpOnly-cookie JWT session.
- AI chat: Meta Llama API, lesson-scoped, hard **$2.00/day** budget cap (plus a 500-req/day backstop, plus a character-count fallback if token-usage parsing ever fails) — checked *before* any model call, not just logged after.
- Full code review completed 2026-09-04, across **seven rounds** (see `info/.notes/Chatbot-implementation/references/neuralascent-auth-and-chat-gemini-prompts.md` — this is the canonical record of every prompt, correction, and regression across the whole build — read it if anything here seems to have broken again). The implementation went through a genuine mid-review regression: a botched `git stash`/merge conflict resolution silently reverted every security fix (and briefly made `api/Program.cs` fail to compile) partway through review. That was caught, and a second hardcoded-secret instance was found in the process that the first review pass had missed (`api/Options/JwtOptions.cs`'s `SecretKey` default, which was silently overriding the fix in `JwtTokenService.cs`). **As of the final pass, a full repo-wide sweep (`grep` for the known secret strings and for conflict markers across all of `api/`) came back completely clean** — no known hardcoded secrets, no leftover conflict markers, no known logic bypasses.
- Frontend build verified for real (`npm run build` — clean). Backend was reviewed line-by-line but **not compiler-verified** — no .NET SDK/Docker was available in the reviewing environment, so this has never actually been compiled or run since the auth/TOTP/chat work started.
- **Given the regression history above, do a real verification pass before push, not just a glance:**
  1. Delete the stray `.orig` backup files still sitting in the working tree (`.env.example.orig`, `api/Program.cs.orig`, `api/Services/LlamaApiClient.cs.orig`, `docker-compose.yml.orig`, `task_tracker.md.orig` as of last check) — untracked leftovers from the botched merge, harmless but shouldn't get committed.
  2. `docker compose -f docker-compose.yml -f docker-compose.dev.yml build api app` — first real compiler check this code has ever had.
  3. An actual end-to-end smoke test once it's running: sign up, approve from the admin dashboard, log in, enroll TOTP, send a chat message, confirm the $2 budget cap actually trips.
  4. Only then push.
- A `git stash` (`On main: !!GitHub_Desktop<main>`) may still exist as a safety-net backup from when this implementation briefly vanished from the working tree and was recovered via `git stash apply`. Check `git stash list`; safe to `git stash drop` once the build/smoke-test above passes and you're happy with what's committed.

**Do not re-run the earlier Gemini prompts from scratch** — the implementation is done; only the fix/correction prompts in `neuralascent-auth-and-chat-gemini-prompts.md` are relevant if anything regresses again.

### 2. Unity Localization personal project — ACTIVE, working toward Phase 2 (Google Translate API)

This is the project you're switching focus to now. I have not been assisting with this one in this conversation — the only trace of it in this repo is `info/.notes/Chatbot-implementation/architecture-notes/unity_localization_project_technical_dossier.md` and a `StudyVertical`/`Lab Projects` seed entry ("Rebuild Lab B — Unity Localization Platform") in `api/Data/DbSeeder.cs`. You said you're working through it "till phase two, which is using of Google Translate API to get the text translated." No further detail was given — when you come back to this, you (or a future me) will need to read that dossier file and whatever you've built so far to pick up context; nothing here tracks its internal progress.

### 3. Neuralascent AI vertical (curriculum content) — PAUSED, resumes after Track 2 hits its Phase 2 milestone

This is the Model Economics Matrix / RAG eval-harness project-portfolio content discussed earlier (hosted-vs-self-hosted LLM economics, quantization, cost-per-resolved-query). Per the standing rule (see `CLAUDE.md` and Claude's memory, `neuralascent-ai-vertical-vs-ai-integration.md`): **this content is hand-authored by you only — never a Local-LLM/Gemini content-generation prompt.** Nothing has been produced for it yet in this conversation; the only work done was planning/scoping discussion. Resume this **by hand** once Track 2 reaches its Phase 2 milestone.

### 4. AI features for the Localization project — PLANNED, comes after Track 3

You mentioned that after finishing Track 3, you'll start on the AI-powered side of the Localization project (presumably beyond basic Google Translate API calls — e.g., LLM-assisted translation QA/refinement), also **by hand**. No scoping or design work has happened on this yet — it's just noted as the next thing after Track 3.

---

## Order of return
Track 2 (Localization, Phase 2) → Track 3 (AI vertical content, by hand) → Track 4 (Localization AI features, by hand). Track 1 just needs your build/push, independent of this sequence — do that whenever, it's not blocking anything else.
