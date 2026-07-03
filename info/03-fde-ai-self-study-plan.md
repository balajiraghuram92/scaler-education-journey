# FDE-Lite Self-Study Plan + Local-AI Workflow + Master Calendar
### Learn the Forward Deployed Engineer material now, mapped to the Scaler syllabus — Raghuram Balaji
*Prepared 02 Jul 2026. Companions: `01-project-labs-rebuild-guide.md`, `02-azure-certification-plan-2026.md`*

---

## 1. Strategy (three rules that keep this feasible)

1. **The Coforge interview ≠ the full FDE syllabus.** ~80% of what an AI-Architect panel will probe lives in Scaler's Module 5 (LLM Engineering: RAG, prompting, guardrails, evals, cost/routing) and Module 6 (Agentic Systems: tool calling, agent patterns, MCP, HITL, enterprise integration), plus the document-processing slice of Module 7. Python tooling, React deep-dives, AWS/K8s, dbt/Airflow = low priority for *this* opening. Your Azure cert prep replaces the entire cloud module (map mentally: S3→Blob, SQS→Service Bus, Lambda→Functions, EKS→AKS, IAM→Entra ID).
2. **Learn concepts anywhere; implement in C#/.NET.** After each concept, redo it with Azure OpenAI + `Microsoft.Extensions.AI` / Semantic Kernel / Microsoft Agent Framework — the interview is .NET-shaped. Gem for you: Microsoft's free GitHub course **"Generative AI for Beginners .NET"**.
3. **The labs are the curriculum.** Every video earns its slot only if it changes something in Lab A or Lab B within a week.

## 2. Module-by-module resource map (Scaler FDE → what to actually watch/read)

| Scaler FDE module | Priority | Resources (channel — title, or exact search keywords) |
|---|---|---|
| Foundations (Python, pytest, Pydantic, AI dev tools) | Low–Med | Corey Schafer — Python OOP / decorators / generators playlists; ArjanCodes — Pydantic + software design; search "Claude Code tutorial", "Cursor tutorial". Python on-ramp = 1 week, read-fluency only (also serves AI-103/AI-200). |
| Backend, Observability & Data (FastAPI, auth, pgvector, Kafka) | Med (vector part **High**) | freeCodeCamp — "Python API Development with FastAPI" (skim; you know REST); OktaDev — "OAuth 2.0 and OpenID Connect in Plain English"; James Briggs — vector DBs/embeddings; search "pgvector tutorial" then do the Azure twins (Azure AI Search, Cosmos DB vector). Kafka: Confluent "Kafka 101" only if curious. Skip Airflow/dbt. |
| Full-Stack (TS/React/Next/Vercel AI SDK) | Low | Covered by your Scaler fullstack videos — see triage in §3. |
| Cloud, DevOps & K8s | Med — **do it on Azure via cert prep** | TechWorld with Nana — "Docker Tutorial for Beginners" (~3 h) and "Kubernetes Tutorial for Beginners" (~4 h); her Terraform course if IaC comes up. Everything AWS-specific → your AI-200/AZ-104 study is the Azure version. |
| **LLM Engineering** (fundamentals, prompting, RAG, evals, guardrails, cost) | **HIGHEST** | Karpathy — "Intro to Large Language Models" (1 h) then "Deep Dive into LLMs like ChatGPT" (~3.5 h); 3Blue1Brown — the GPT/attention chapters. DeepLearning.AI (free, learn.deeplearning.ai): "ChatGPT Prompt Engineering for Developers", "Building and Evaluating Advanced RAG", "Evaluating and Debugging Generative AI", "Red Teaming LLM Applications". LangChain YouTube — "RAG From Scratch" series. Hamel Husain — essay "Your AI Product Needs Evals" (read twice). **OWASP Top 10 for LLM Applications** (read the PDF — panels love prompt-injection questions). Search "RAGAS tutorial". Cost/routing: browse the "AI Engineer" conference channel. |
| **Agentic Systems & Integrations** (tools, patterns, MCP, multi-agent, HITL) | **HIGHEST** | Read first: Anthropic — "Building Effective Agents" (workflows-vs-agents canon) and OpenAI — "A Practical Guide to Building Agents" (PDF). Courses: Microsoft GitHub — "AI Agents for Beginners"; Hugging Face — "AI Agents Course" (free + certificate); LangChain Academy — "Introduction to LangGraph". MCP: DeepLearning.AI — "MCP: Build Rich-Context AI Apps with Anthropic"; Microsoft GitHub — "MCP for Beginners". .NET implementation: Microsoft Learn on **Semantic Kernel** + **Microsoft Agent Framework**. Debugging/eval: search "LangSmith tracing tutorial", "Arize Phoenix LLM tracing". |
| App Eng., Security & Doc Processing | Med–High | Microsoft Learn — **Azure AI Document Intelligence** + **Content Understanding** (double-counts for AI-103); **Microsoft Presidio** for PII (enterprise talking point); skim SOC2/GDPR concepts. Skip Postgres RLS/multi-tenancy for now. |
| System Design & AI Architectures | Med–High | ByteByteGo (YouTube) refreshers; Chip Huyen — book **"AI Engineering"** (closest single text to FDE+GenAI syllabus) or her free posts "Building a Generative AI Platform" and "Agents". Rehearse aloud: "design a RAG system at scale", "design a ticket-triage automation platform". |

**One-big-video verdict:** no single 65–100 h course maps to FDE — the mega-courses skip guardrails, evals, MCP, and enterprise integration (exactly what your JD stresses). If you want one paid package: Ed Donner's "LLM Engineering" (Udemy) is the usual pick. Better combo (~50–60 focused hours): Karpathy (5 h) → Microsoft's free "for Beginners" repos: GenAI / AI Agents / MCP (+ the .NET GenAI variant) → 4–5 DeepLearning.AI short courses → your two labs as proof.

**Must-read shortlist (interview-dense, ~6 h total):** Anthropic "Building Effective Agents" · OpenAI "A Practical Guide to Building Agents" · OWASP LLM Top 10 · Hamel Husain "Your AI Product Needs Evals" · Chip Huyen's two free posts.

## 3. Scaler Fullstack videos — triage (goal: basic knowledge, ≤3–4 h/week)

- **Watch properly (1.25–1.5×):** *React and Frontend Product Architecture Fundamentals* (components, props/state, hooks, the IMDB labs — refresh, since your localization platform used React); elective *Foundations of AI-Assisted Full-Stack Development* (prompting for UI/logic/APIs, reviewing AI-generated code — it's how you'll build anyway); the single session *AI Feature Integration Lab: LLM APIs, Structured Responses and Backend Orchestration* (your JD in miniature; port the patterns to .NET).
- **Skim selectively:** JS runtime sessions on the event loop, promises, async/await — only where rusty.
- **Skip for now:** polyfills/machine-coding modules, Kanban machine coding, Redux deep dives, Next.js deep dive, HTML/CSS foundations — that's frontend-*role* interview prep, not your target.
- **Application rule:** each watched module must show up in the Lab B React review dashboard within the same week.

## 4. Local-AI workflow on the ProArt PX13 (Ryzen AI Max+ 395, 128 GB)

Your machine runs 70B-class dense and ~100B-class MoE models locally at interactive speeds — use it as the default dev backend.

- **Serve:** LM Studio (easiest on this hardware; Vulkan llama.cpp runtime; enable the OpenAI-compatible server on `:1234`). Ollama works too. In AMD software/BIOS, raise the iGPU's Variable Graphics Memory allocation so big models fit (check current ProArt/Adrenalin guidance).
- **Model picks** (check for newer quants when you install): **gpt-oss-120b** — default "smart" model (reasoning, ticket generation QA); **gpt-oss-20b** or **Qwen3-30B-A3B** — fast MoE for high-volume work (string classification, structured JSON); **Qwen3-Coder-30B** — bug-roulette pair programming. Test **tool/function calling** early per model — quality varies, and knowing which handle it well is itself interview knowledge.
- **Speech:** whisper.cpp / faster-whisper for offline support-call transcription → feeds Lab A's ticket generator. Fully offline = your original iCube "kept in-house for data sensitivity" argument, restated for 2026.
- **Vision:** ONNX Runtime + **DirectML** uses the Radeon iGPU for the Lab A segmentation model. The XDNA NPU is optional garnish — don't burn evenings on NPU plumbing; iGPU + big memory is the star.
- **Evals for free:** run the Lab B eval suite (back-translation, placeholder diff, glossary adherence) across thousands of strings at zero cost; promote only winning prompts to the cloud model. Sentence for the panel: "I ran evals thousands of times locally before spending a rupee on cloud tokens."
- **Hybrid routing demo:** Lab B's ModelRouter — PII/bulk → local, ambiguous/creative → cloud, with eval scores justifying the split. That is FDE "Cost, Latency & Model Routing" + the JD's secure-integration concern, in running code.
- **Also try one evening:** **Foundry Local** (Microsoft's local runtime) — "Foundry Local on my laptop, Azure AI Foundry in the cloud" is native AI-103 vocabulary (verify current AMD acceleration support).
- **Discipline:** ~80% local dev / 20% Azure hardening. The exams test *Azure services*, and the Sept–Oct Azure deployment (Azure OpenAI + App Insights) is non-negotiable — that's the resume line and demo link.

## 5. Master calendar — 02 Jul → 31 Oct 2026 (all threads merged)

| Wk | Dates | Certification | Labs | FDE / videos / reading |
|---|---|---|---|---|
| 1 | Jul 6 | Azure account; Foundry hands-on; Python on-ramp | Lab A wknd 1 (compose, EF Core, WMS API, RobotSim) | Karpathy "Intro to LLMs" |
| 2 | Jul 13 | Python cont.; optional AI-901 sit | Lab A wknd 2 (SignalR chat + P2P call on LAN) | Karpathy "Deep Dive"; Scaler React begins (≤4 h/wk from here) |
| 3 | Jul 20 | Start AI-103 Learn path | Lab A wknd 3 (coturn, TURN creds, frames stub) | 3Blue1Brown GPT chapters; DL.AI Prompt Engineering |
| 4 | Jul 27 | AI-103 path | Lab A wknd 4 (local-LLM tickets, MailHog escalation, anomaly alert) | Anthropic "Building Effective Agents" |
| 5 | Aug 3 | AI-103 path + study-guide checklist | Faults A1–A2 → RCA journal | MS "AI Agents for Beginners" pt 1 |
| 6 | Aug 10 | AI-103 path | Faults A3–A4 | MS "AI Agents for Beginners" pt 2 |
| 7 | Aug 17 | Sandbox; Practice Assessment if released | Faults A5–A6 | OpenAI agents guide; DL.AI MCP course |
| 8 | Aug 24 | AI-103 review week | Faults A7–A8; Lab A demo script | LangChain "RAG From Scratch" (selective) |
| 9 | Aug 31–Sep 6 | **AI-103 EXAM** | Faults A9–A10 (light week) | Hamel Husain evals essay |
| 10 | Sep 7 | **Checkpoint:** AI-200 GA? → else AZ-104. Start chosen path | Lab B core: schema, state machine, outbox | Scaler AI-Assisted Full-Stack elective |
| 11 | Sep 14 | AI-200/AZ-104 path | Lab B: React dashboard + SignalR + Unity script | Semantic Kernel / Agent Framework on MS Learn |
| 12 | Sep 21 | Path cont. | Lab B AI layer: PreTranslator + PlaceholderValidator + Classifier | OWASP LLM Top 10 |
| 13 | Sep 28 | Path cont. | Lab B: eval pipeline + ModelRouter; Faults B1–B3 | DL.AI "Red Teaming LLM Applications" |
| 14 | Oct 5 | Hands-on = deploy | **Deploy Lab A to Azure** (Container Apps + Azure SignalR + Azure OpenAI + App Insights) | Chip Huyen posts; ByteByteGo refreshers |
| 15 | Oct 12 | Practice assessments / review | Faults B4–B7; hybrid-routing demo polish | Mock interviews ×2 (JD + RCA entries) |
| 16 | Oct 19 | **AI-200 or AZ-104 EXAM** | Faults B8–B10 | Rehearse "design ticket-triage platform" aloud |
| 17 | Oct 26 | Buffer / retake margin | Demo dry-runs of both labs | Resume update: certs in, ATS-note skills → Core Skills; story-bank rehearsal |

**Weekly constants:** 2 faults → 2 RCA entries · one 20-min AI mock interview · ≤4 h Scaler fullstack · everything AI runs local-first on the 395.

## 6. The interview narrative (memorize the arc, not a script)

"I've spent seven years doing root-cause analysis on the runtime under Unity — the *operational excellence* half of this role is my day job. In 2018 I built ML-based automation before it was fashionable: a video pipeline feeding a CNN for defect detection inside a supply-chain automation platform. This year I rebuilt my two most relevant systems with the 2026 AI layer — structured LLM ticket triage with guardrails, an eval pipeline, human-in-the-loop review, and hybrid local/cloud model routing — deployed on Azure, and certified on Microsoft's new AI-apps-and-agents track."

Every sentence above is backed by a repo, a journal entry, or a certificate produced by this plan.
