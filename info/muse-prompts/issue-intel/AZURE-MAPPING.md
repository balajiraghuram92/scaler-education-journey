# Bug-fix agent (`issue-intel/`) on Azure managed AI services

Written 11 Nov 2026. A reference for adding Azure services to the bug-fix agent project, and for explaining the design in an interview.

Service dates and status come from `C:\Users\balaj\Documents\claude-queries\azure-ai-services-timeline-2023-2026.md`. Where that file marks something as conflicting, second-hand or from memory, this file repeats the warning. Anything about API shapes that is marked **check** is from my own knowledge and was not verified against Microsoft's documentation today; read the Learn page before building on it.

---

## 1. The idea in one paragraph

The project already hides every outside dependency behind a small interface: one `ModelGateway` for all model calls, adapters for the tracker, chat and code host, one `Sandbox` for running builds, one settings file. So Azure does not need a rewrite. Each managed service is a **second implementation of an interface that already exists**, selected by a setting. The local fake stays the default, so tests still run offline with no Azure account and no cost.

This changes one hard rule in `BUILD-SPEC.md` ("No real external services"). The new rule would be: *no real external service is used unless an Azure profile is switched on in settings; every test runs with the profile off.*

## 2. What to add, and where it plugs in

Ordered by value for effort. "Seam" is the existing file where the new implementation goes.

| # | Part of the project | Azure service | Seam (existing code) | What actually changes |
|---|---|---|---|---|
| 1 | Chat and embedding calls | **Azure OpenAI in Microsoft Foundry** | `app/gateway/adapters.py` (`OpenAICompatAdapter`), `app/settings.py` (`openai_base_url`, `openai_api_key`, model names) | Probably settings only: point the base URL at the resource's OpenAI-compatible `/openai/v1` endpoint and use deployment names as model names. **Check** that the endpoint accepts `Authorization: Bearer <key>`; older Azure endpoints want an `api-key` header and an `api-version` query parameter, which would need a small adapter subclass. |
| 2 | Claude for `fix_plan`, `fix_patch`, `final_check` | **Claude in Microsoft Foundry** | `app/gateway/adapters.py`, new adapter class beside the two existing ones; `app/gateway/routing.py` | A new adapter implementing the same `ModelAdapter` protocol (`complete`, `embed`). Claude uses Anthropic's Messages API shape, not the OpenAI one, so settings alone are not enough. Routing then sends chosen task types to it. This is the cleanest demonstration of "change models on evidence": two providers behind one gateway, compared by the G4 scorecards. |
| 3 | Database, vectors, row-level security | **Azure Database for PostgreSQL Flexible Server** with pgvector | `app/settings.py` (`database_url`), `alembic/` | Connection string only. pgvector and row-level security work the same. Enable the `vector` extension in the server's allowed-extensions setting before running migrations. |
| 4 | Untrusted text from tickets and chat | **Azure AI Content Safety: Prompt Shields** | `app/pipeline/stage_fns.py` (before S7 synthesis) and `app/agents/tools.py` (evidence pack) | A new check that sends ticket and chat text as "documents" and records whether an injection attempt was flagged. It is a **second line**; the existing rule (text goes in delimited data blocks and can never choose a tool or filter) stays the first. Add its result to the safety eval. |
| 5 | Token limits, cost metrics, failover | **API Management AI gateway** | None in code. `openai_base_url` points at API Management instead of at the model resource. | Policies do per-consumer token limits, token metrics, load balancing across deployments and semantic caching. `ModelGateway` keeps what API Management cannot know: task type → model routing, per-run budgets, the scorecards. Explain the split as: *API Management governs consumers, the gateway governs tasks.* |
| 6 | Running `dotnet build` and `dotnet test` for the fix agent | **Azure Container Apps dynamic sessions** (custom container) | `app/agents/sandbox.py` (`run_cmd`, `create_sandbox`, `remove_sandbox`) | A second `Sandbox` implementation. Today the sandbox is a git worktree in a local directory, which isolates files but not the process. A session pool with a custom image containing the .NET SDK gives real isolation with no network. This closes the weakest point of the local design. |
| 7 | Bulk work at ingest (`outcome_classify`, embeddings) | **Azure OpenAI Global Batch** | `app/gateway/cache.py` (`enqueue_batch`, `execute_batch_job`), `app/gateway/gateway.py` (`complete_batch`) | The batch path already exists as a local job queue. A real implementation uploads a JSONL file, polls the batch job and reads results. About half the price, with a 24-hour target. |
| 8 | Hosting the API, worker and MCP server | **Azure Container Apps** (api, worker as a job or second app) | `Dockerfile`, `docker-compose.yml` | Deployment only. The MCP server becomes a remote endpoint that other agents can call. |
| 9 | Secrets and service identity | **Key Vault** and **managed identity** (Microsoft Entra) | `app/settings.py` | Replace keys in environment variables with identity-based access to the model resource and the database. |
| 10 | Traces and cost dashboards | **Application Insights** through OpenTelemetry (Foundry tracing reads the same data) | `app/gateway/gateway.py` (`_log`), `app/pipeline/manager.py` | Emit a span per stage and per model call in addition to the existing `model_calls` rows. |

### Optional, and worth knowing rather than building

| Service | How it relates | Advice |
|---|---|---|
| **Foundry Agent Service** (GA May 2025) | Could expose this project's MCP tools to a managed agent, so the investigation is reachable from Copilot-style clients. | Good small demo: register the MCP server as a tool. Do not move the pipeline or the fix loop into it (see section 3). |
| **Hosted agents** in Foundry Agent Service | Would run the hand-written fix agent as a container behind a managed endpoint. | Status is disputed in the timeline (preview vs GA). Describe as "a hosting option", do not depend on it. |
| **Microsoft Entra Agent ID** | The pipeline already runs under a "service identity with full SE access". Agent ID is the managed form of that idea: the agent has its own identity, separate from any user. | Preview in May 2025; GA date not found. Mention as the production answer to "who is the agent acting as?". |
| **Azure AI Search** (hybrid, semantic ranker, agentic retrieval) | An alternative to pgvector plus PostgreSQL full-text search in `app/search/`. | Keep PostgreSQL. See section 3. Building a second retriever just to compare recall@k in the G1 eval is a fair experiment, with the permission caveat stated. |
| **Microsoft Agent Framework 1.0** (GA 3 Apr 2026) | A framework for the kind of loop this project writes by hand. | Do not adopt it here. The spec's "no agent framework" choice is deliberate and is a strength when explaining the system. |
| **Groundedness detection** (Content Safety) | Overlaps S8's citation check. | Still preview per the timeline. The project's own check is stricter (every claim must cite an evidence id that exists). |
| **Foundry evaluations** | Overlaps `evals/`. | Keep the project's own harness; its ground truth comes from the generator, which no hosted evaluator can know. |

## 3. What should not move, and why

These are the parts that make the project worth showing. Replacing them with a managed service would make it weaker.

- **Row-level security in PostgreSQL.** The permission model is that the database itself refuses to return rows the viewer may not see. Azure AI Search does security trimming with filters that the application adds to each query, which is the weaker "remember to filter" model the spec set out to avoid. If AI Search is ever used, it must be a recall experiment over data everyone may see, or the leakage test must be re-run against it.
- **The fixed eight-stage pipeline and the bounded fix loop.** They are plain functions so every step can be read and traced, a failed stage stops the run, and nothing is skipped silently. A managed agent runtime decides its own steps.
- **Human approval for every write and merge.** No service changes this.
- **The eval harness and generated ground truth.**
- **`ModelGateway` as the only caller of models.** API Management sits in front of the provider, not in place of the gateway.

## 4. Suggested order of work

Each step is useful alone and leaves the project working.

1. **Models first (rows 1 and 2).** Gives real numbers for the G1–G4 evals in place of fake-adapter numbers. Needs: one Foundry resource, one small and one large chat deployment, one embedding deployment, and the embedding dimension setting changed from 64 to the real model's size (which means a migration for the vector column and re-embedding the corpus).
2. **Database (row 3).** Proves the row-level security design on the managed service.
3. **Prompt Shields (row 4).** Small, and adds a measurable line to the safety eval.
4. **Sandbox (row 6).** The largest piece of new code and the best security story.
5. **API Management (row 5), Batch (row 7), hosting and identity (rows 8–9), tracing (row 10).** Production plumbing; do as many as are useful to talk about.

For Muse, each numbered step is one prompt in the style of the correction prompts: one agent, the seam file named, the interface it must implement, the setting that selects it, a fake-backed test, and no change to default behaviour.

## 5. Costs and risks to decide before starting

- **Money.** Model calls and API Management are billed. The eval runners make many calls; run them on a small slice of the corpus first and keep the per-run budget in `app/gateway/budgets.py` switched on. API Management's token-limit and content-safety policies are not available on the Consumption tier (per the timeline, second-hand).
- **Data.** The corpus is synthetic, so nothing sensitive leaves the machine. Keep it that way.
- **Embedding dimension.** Changing the model changes the vector size. The column size, the index and every stored embedding change together.
- **Tests stay offline.** Every Azure implementation needs a test that runs against a fake transport; live calls belong in an opt-in eval run, not in `pytest`.
- **MCP library version.** The project is currently held at the older `mcp<2` because `app/mcp_server/server.py` was written for the 1.x interface. Port it before exposing the server remotely.

## 6. Saying it accurately

Three different claims; keep them apart.

| Claim | True when |
|---|---|
| "Built on …" | The implementation exists in the repo, selected by a setting, and you have run it against the real service. |
| "Designed so that … plugs in at …" | The seam exists (it does, for every row in section 2) but the Azure implementation has not been written or run. |
| "The managed equivalent is …" | You are mapping a concept, for example the service identity to Entra Agent ID. |

Date checks from the timeline that apply here:

- Foundry Agent Service: GA May 2025, with MCP support. Safe to cite from then.
- Claude in Foundry: only the 4.5-era models (Sonnet 4.5, Opus 4.1, Haiku 4.5) are confirmed, in preview from November 2025. Any later Claude model name on Foundry needs its own source.
- Global Batch: GA 23 October 2024; earlier use was preview.
- Container Apps dynamic sessions: preview May 2024, GA November 2024.
- Prompt Shields: preview March 2024, GA later (date not in the timeline).
- Entra Agent ID and hosted agents: GA dates not established. Say "preview" unless you have a source.
- Agent Framework: preview October 2025, 1.0 on 3 April 2026.

## 7. Things to verify on Microsoft Learn before building

- The exact base URL and authentication header for the OpenAI-compatible endpoint of a Foundry resource, and whether an `api-version` is still required.
- The endpoint and request shape for Claude models deployed in Foundry.
- Whether dynamic sessions custom containers can run with egress fully disabled, and their limits on run time and disk (a `dotnet build` needs both).
- The Prompt Shields request format for documents and its size limit per call.
- Which API Management tiers support the AI gateway policies you want.
- Current status of hosted agents, Entra Agent ID and groundedness detection.
