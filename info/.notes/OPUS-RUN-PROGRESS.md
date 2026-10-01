# OPUS Run Progress

Branch: `claude/opus-3-stage-d88sa1` (never push `main`; no deploys; no EC2/AWS/SSM; no secrets; never change `content_status`; no DB writes).
Prompt: `info/.notes/opus-cloud-prompt-3-stage-audit-and-ai-agent-hardening.md`

## Status
| Stage | Status |
|---|---|
| 1 Audit | **Complete** (2026-10-01) |
| 2 Chapter updates | Not started — waits for owner "go Stage 2" and approval of report §A items |
| 3 `ai-agent/` hardening | Not started — waits for owner "go Stage 3" and approval of report §B items |

## Stage 1
- Files changed: `info/.notes/OPUS-AUDIT-REPORT.md` (new), `info/.notes/OPUS-RUN-PROGRESS.md` (new). Nothing else.
- Method: 5 parallel Sonnet 5.5 sub-agents (machine-coding inventory, seeded lessons, ai-agent code, deploy/CI, info/ tree); orchestrator re-verified high-severity ai-agent and deploy claims in the code. **Nothing was executed**; runtime behaviour is inferred from code. The orchestrator was Sonnet 5.5, not Opus 5.5.
- Headline findings: (d) `DATABASE_URL` never produced by the deploy path (Critical for prod); unauthenticated `/echo` and `/agent_test` publicly proxied; fresh-DB migration deadlock; rollback deletes crash logs; no Python tests/CI. All defects (a)–(h) confirmed.
- Content headline: Java L2/L3 seed bodies are empty; Splitwise exercises exist but are unwired; BookMyShow has no exercise; MCQ correct answer is the longest option in 94 % of questions; 58 templated lessons thin and effectively locked.
- Decisions made: none beyond audit scope. Locked decisions (bge-m3, LangGraph, Pydantic AI, Langfuse, Muse/Nova/Gemini, HNSW, hybrid retrieval) respected and not re-opened.

## What remains
- Owner answers to report §D (esp. 1, 4, 5, 6).
- Stage 2 and Stage 3 work lists are in report §C.

## Exact next action
Owner reviews and merges the Stage 1 PR, answers §D, then says "go Stage 2" or "go Stage 3" (naming the §A/§B items approved). A fresh session starts from this file, reads the report, and begins with §C item 1 of the named stage.

## EC2 follow-up steps (placeholder, filled in during Stage 3; owner runs later)
To be written in Stage 3. Expected topics: confirm SSM env has `DATABASE_URL` (or `DATABASE_*`), `MUSE_AI_API_KEY`, `LANGFUSE_*`; confirm prod DB image is pgvector; run `migrate.py` once; check `schema_migrations`/`content_chunks`.
