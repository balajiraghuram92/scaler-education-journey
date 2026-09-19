# Session Handoff — Working Style, Phase 0 Close-out, Phase 1 Kickoff
# (2026-09-12 → 2026-09-15)

> **Read this first in a brand-new Claude Code (or any other assistant)
> session on this repo**, alongside
> [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md)
> (the full project context doc). This file captures how the user wants an
> assistant to *operate* on this project — which isn't derivable from the
> code — plus what actually got done and discussed across this session, so a
> new session can continue without the user re-explaining any of it.
>
> **Note on Claude's memory:** some of what's below (the teaching-style
> preferences especially) also lives in Claude Code's own persistent memory
> feature — but that memory is local to one machine, keyed to this exact
> project path, and does **not** travel via `git push`/`git pull`. This file
> is the durable, git-tracked copy of the same information, so it survives a
> machine switch or a different tool (GPT, a different Claude session)
> reading this repo's `info/.notes/` folder.

**Last updated:** 2026-09-15

---

## 1. How the user wants an assistant to operate on this project (read this before doing anything else)

This is a standing, repeat-until-told-otherwise operating mode for the AI
Learning Agent / AI Tutor project — not a one-off preference for a single
conversation.

### 1.1 Scope of "hand-written by the user" — broader than it first sounds

`CLAUDE.md` already says Claude has no direct write access to source files
in this repo. On top of that, for the **AI Learning Agent specifically**,
the user has explicitly widened the "I write this myself" rule to cover
**all AI-Tutor-supporting work, not just the Python `ai-agent/` code** —
this includes infra that exists to support it, e.g. the `docker-compose.yml`
pgvector image swap and the `scripts/deploy-single-ec2.sh` production
deploy script. (Originally scoped narrower — Python-only — then explicitly
corrected by the user mid-session; see the exchange in this conversation
around "why the prompt now?" if the reasoning needs re-deriving.)

**What this means concretely for an assistant:** for anything under this
umbrella, do not draft a copy-paste-ready prompt, diff, or scaffold — not
even framed as "just a doc, you still write the code." Instead: explain the
relevant concept, point at exactly what needs to change and why (file, line,
the shape of the fix), and let the user write/apply it themselves. Review
after they've done it. This still leaves room for direct operational
commands during live troubleshooting/incident response (e.g. diagnostic
`psql`/`docker`/`pg_dump` commands during the pgvector migration — see
§2 below) — the hand-written rule is about *building* the AI Tutor and its
supporting infra, not about refusing to help debug a live production issue.

The **unchanged** part: this stricter rule is specific to AI-Tutor-adjacent
work. Everywhere else in this repo (Localization Lab, the existing
TOTP/Llama chat system, general site work), the normal `CLAUDE.md` workflow
applies — Claude drafts a copy-paste-ready prompt for the user's Local
LLM/Gemini to execute.

### 1.2 Teaching split — Python syntax vs. backend/AI concepts

Explicitly established this session, and important to get right:

- **Python coding mechanics** (syntax, decorators, async/await, type hints,
  packaging, FastAPI's specific API surface, etc.) — the user has
  C++/C#/Java experience and does **not** want these taught. They'll pick
  this up on the fly while coding. Don't front-load a tutorial, don't
  explain a Python idiom unless asked.
- **Backend and AI-engineering *concepts/terminology*** — the user
  explicitly wants these taught **from scratch, in real depth, assuming
  zero prior knowledge** — not a one-line gloss. This covers things like:
  what a web framework/reverse proxy/vector database/RAG pipeline stage/
  JWT/dependency injection/LangGraph node-edge-state model/Docker
  image-vs-volume actually is and why it exists. **Reason given
  explicitly:** this is interview preparation (target: Jan 2027 AI
  Engineering roles), and concepts half-understood now will be needed cold
  months later — a real, from-basics explanation the first time a concept
  comes up is worth the time even though the user could technically infer
  some of it from context.
- **Pacing:** introduce a concept only when it's actually about to matter
  to the current step (not one giant syllabus dump up front), but give it a
  genuine full explanation *at that point*, not a one-liner assuming prior
  knowledge.
- **If Claude hits an issue, ambiguity, or an undocumented decision while
  explaining or reviewing: ask the user, don't guess or fabricate.** (This
  came up explicitly around the CrewAI-vs-LangGraph question — see §4.)

---

## 2. Phase 0 → Phase 1 transition: what actually happened this session

**Full blow-by-blow record, including several real mistakes worth not
repeating, lives in a separate file — read it before touching the
production database again:**
**[SESSION-2026-09-13-pgvector-migration.md](SESSION-2026-09-13-pgvector-migration.md)**

Short version: production Postgres was successfully migrated from
`postgres:16-alpine` to `pgvector/pgvector:pg16` (confirmed genuine arm64
build), data verified intact via a properly-validated backup, `vector`
extension enabled. Along the way: a bash unbound-variable typo in
`scripts/deploy-single-ec2.sh`, a wrong assumed database name
(`studytracker` vs. the real `StudyTrackerDB`), a `docker exec -t`
binary-corruption gotcha that silently invalidated two "backups," and an SSH
`Connection timed out` traced to (most likely) a stale Security Group source
IP or a changed EC2 public IP — **this last one was never explicitly
confirmed fixed in this conversation; if SSH access is still flaky, that's
the place to pick the thread back up (compare current public IP via
`curl -s https://checkip.amazonaws.com` against the EC2 instance's Security
Group inbound rule for port 22, and confirm the instance's current public
IPv4 address hasn't changed).**

**One open item flagged and intentionally left as a user decision, not yet
resolved:** the `vector` extension was enabled via a one-off manual `psql`
command, not captured in any EF Core migration or init script. Also already
recorded in [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md)'s
Phase 1.2 section.

**Also already updated this session** (both reflect current reality, no
further action needed unless the plan changes again):
- [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) —
  Phase 0 marked done, the JWT-trust-bridge milestone dated, and a new
  "sequencing decision" section added: build/validate the embedding +
  reranking pipeline against **Deepinfra's cloud API only first**
  (`BAAI/bge-m3` + `bge-reranker-v2-m3`), defer all Mac Studio/SSH-tunnel/
  local-inference work until that's proven end-to-end. Hard constraint tied
  to this: whatever cloud model is used now must be the *same weights* the
  Mac Studio serves locally later, or a full corpus re-embed is needed —
  this is why `BAAI/bge-m3`/`bge-reranker-v2-m3` specifically (both
  Deepinfra-hosted and self-hostable on Apple Silicon via MPS), not a
  different cloud-only model.
- [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md)'s
  file index — links to the pgvector migration session file.

---

## 3. Where things stand right now / immediate next steps

Per the tracker, Phase 1 ("The Substrate") has formally started. In
dependency order:

1. **1.1 Project scaffold** — add Pydantic AI, a minimal one-node LangGraph
   graph, Langfuse tracing, and LLM/embedding provider env config to
   `ai-agent/` (currently just the JWT-validation skeleton in `main.py`).
   Not yet started as of this writing.
2. **Deepinfra account + API key** — needed before 1.1's config can be
   real. Where the key should live (a new SSM parameter feeding
   `ai-agent`'s env, same pattern as `JWT_SIGNING_KEY`) was discussed but
   not yet set up.
3. **1.2 Content ingestion pipeline** — depends on 1.1 existing; this is the
   first "real" RAG work (chunking, embedding, writing to
   `knowledge_chunk`-style rows in the now-pgvector-enabled `StudyTrackerDB`).
4. **1.3 retrieval → 1.4 Tutor Agent → 1.5 eval harness → 1.6 frontend**,
   each depending on the previous, per the tracker.

**Model-provider credentials still needed, beyond Deepinfra**, per the
locked provider cascade in the SESSION-HANDOFF: Meta Muse API key, AWS
Bedrock IAM access (for Amazon Nova Micro — note this is IAM-based auth, not
a simple API key, and needs a policy/role decision), a Google AI Studio key
for Gemini free-tier eval judging, and a Langfuse key pair (plus a decision
on self-hosted vs. Langfuse Cloud). None of these are provisioned yet as of
this session.

---

## 4. Open, unresolved thread: LangGraph vs. LangChain vs. CrewAI — documentation gap

This session worked through, in detail, *why* this project's design
specifically needs LangGraph's low-level graph/state/cycle/human-in-the-loop
primitives rather than LangChain's linear-chain abstraction or CrewAI's
higher-level role-based multi-agent abstraction — grounded in concrete
features already committed to in `ai-learning-agent-ARCHITECTURE.md` (the
six-agent router fan-out in §3.3, the retrieval-sufficiency retry loop and
validation/repair loop from the original chatbot HLD, the persisted
progressive-hint-disclosure state machine, and the Admin Agent's
human-in-the-loop pause requirement).

**Important, explicitly flagged during that discussion: `CrewAI` is not
mentioned anywhere in this repo's actual architecture docs.** The
LangGraph-vs-CrewAI reasoning given was Claude's own constructed argument
for *why* LangGraph would still win on this project's specific requirements
if asked in an interview — it is **not** a decision this project's notes
ever actually recorded being made. Claude explicitly said so rather than
presenting it as settled history, per the "ask/flag rather than fabricate"
rule in §1.2.

> **RESOLVED 2026-09-18.** Written up as
> [ADR-001-orchestration-framework-choice.md](ADR-001-orchestration-framework-choice.md),
> with the "newly-reasoned, not retroactively-discovered" caveat kept at the top
> of that file. Recorded as decision 9 in `ai-learning-agent-ARCHITECTURE.md`
> §13. A new session does not need to re-ask the question below.

**Still open, not yet decided:** Claude offered to add this CrewAI-vs-LangGraph
reasoning into `ai-learning-agent-ARCHITECTURE.md` as a real documented
decision (with the honest caveat that it's newly-reasoned, not
retroactively-discovered). **The user had not answered this offer when this
summary was written.** If a new session picks this up, the open question to
ask the user is simply: *do you want that reasoning written into the
architecture doc now, and if so, does the reasoning as given actually match
your own thinking, or does anything need adjusting first?*

---

## 5. File index for a cold-start session

| File | What it's for |
|---|---|
| **This file** | Working-style rules + this session's summary — read first alongside the two below |
| [ai-learning-agent-SESSION-HANDOFF.md](ai-learning-agent-SESSION-HANDOFF.md) | Full project context, who the user is, all locked architecture decisions |
| [ai-learning-agent-BUILD-TRACKER.md](ai-learning-agent-BUILD-TRACKER.md) | Phase-by-phase checklist — current source of truth for what's done vs. pending |
| [ai-learning-agent-ARCHITECTURE.md](ai-learning-agent-ARCHITECTURE.md) | Full technical spec (agent roster, RAG pipeline detail, orchestration diagram) |
| [SESSION-2026-09-13-pgvector-migration.md](SESSION-2026-09-13-pgvector-migration.md) | The pgvector production migration — mistakes made, verified current state, one open item (extension not in migrations yet) |
| [SESSION-2026-09-10-phase0-deploy-debugging.md](SESSION-2026-09-10-phase0-deploy-debugging.md) | Earlier Phase 0 deploy debugging (JWT signing key / SSM issue, now resolved) |
| `CLAUDE.md` (repo root) | Repo-wide rules: no direct source edits outside `info/.notes/`/`exercises/`, prompt-workflow for non-AI-Tutor changes, AI-vertical vs AI-integration scope boundary |
