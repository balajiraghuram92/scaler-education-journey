# Azure Certification Plan — July → October 2026
### For the Coforge AI Architect (internal) opening — Raghuram Balaji
*Facts verified via web research on 02 Jul 2026. Microsoft is mid-overhaul — re-check the official exam page the week you book.*

---

## 1. The 2026 overhaul (why old blog advice is now wrong)

Microsoft is retiring ~12 role-based certifications between June and September 2026 — its largest credential restructuring since role-based certs began — and replacing them with AI-centric exams.

| Old (retiring/retired) | Status | Replacement |
|---|---|---|
| **AI-102** Azure AI Engineer Associate | **Retired 30 Jun 2026** | **AI-103** — Azure AI Apps and Agents Developer Associate (GA 19 Jun 2026) |
| **AZ-204** Azure Developer Associate | **Retires 31 Jul 2026** | **AI-200** — Azure AI Cloud Developer Associate |
| AI-900 (exam) | Replaced Mar 2026 | AI-901 (Azure AI Fundamentals — certification name unchanged, doesn't expire) |
| DP-100 Data Scientist | Retiring 2026 | AI-300 — MLOps Engineer Associate |
| AZ-500 Security Engineer | Retiring 2026 | SC-500 — Cloud and AI Security Engineer |
| AZ-104 Administrator / AZ-305 Architect | **Not retiring** | — |

Rules that matter to you:
- Retired certs stay on your transcript but **cannot be renewed** after retirement, and there is **no automatic migration** to the replacement. → Do **not** sprint for AZ-204 before 31 Jul; it would be a wasting asset.
- Do **not** buy AI-102/AZ-204 courses — content no longer matches the live exams.
- Associate exams have **no prerequisites** (recommended experience only). The one real prerequisite trap: **Azure Solutions Architect Expert** — you may sit AZ-305 anytime, but the *certification* is only awarded once you also hold an **active AZ-104**. So AZ-305 is your **2027** goal (fits the "Architect" title), not an October option.

---

## 2. Recommendation

### Set A — maximum JD alignment (my pick)
| Order | Exam | Target date |
|---|---|---|
| 1 | **AI-103 — Azure AI Apps and Agents Developer Associate** | **~15–25 Sep 2026** |
| 2 | **AI-200 — Azure AI Cloud Developer Associate** | **~25–31 Oct 2026** *(checkpoint below)* |

### Set B — safe/classic (choose if you want zero new-exam risk)
| Order | Exam | Target date |
|---|---|---|
| 1 | **AZ-104 — Azure Administrator Associate** (mature prep ecosystem; the AZ-305 prerequisite) | Sep 2026 |
| 2 | **AI-103** | Oct 2026 |

**Week-10 checkpoint (early Sep):** if AI-200 is still in beta or practice materials remain thin → swap slot 2 to **AZ-104**, push AI-200 to November. Either way, AI-103 is non-negotiable — it *is* "the AI one Microsoft just introduced," and it reads like your target JD.

Optional extras: **AI-901** fundamentals as a gentle 4–5 day first-exam warm-up in July (skippable at 11+ yrs; fundamentals never expire). **GH-300 GitHub Copilot** cert matches the JD's "GHCP" line — cheap add-on; verify current availability before booking (not re-checked against the 2026 changes).

---

## 3. Exam fact sheets

### AI-103 — Developing AI Apps and Agents on Azure
- **Cert:** Microsoft Certified: Azure AI Apps and Agents Developer Associate. GA since 19 Jun 2026.
- **Logistics:** USD 165 list (India pricing differs — check at scheduling; watch Microsoft Learn for voucher offers), ~120 min, ~40–60 questions, pass 700/1000, Pearson VUE (online-proctored or test centre), English-only at launch, free annual renewal via Microsoft Learn assessment. Retake possible 24 h after a first fail.
- **Shape:** built around **Microsoft Foundry** (not the old service-by-service AI-102 style). Scenario-driven; some code items lean on the **Python** Foundry SDK.
- **Domain weights:** Implement generative AI & agentic solutions **30–35%** · Plan & manage an Azure AI solution **25–30%** · Computer vision / Text analysis / Information extraction **10–15% each**.
- **Skills that mirror your JD:** RAG in an application; tool-augmented flows and multistep reasoning; safety filters, guardrails, content moderation; evaluating for fabrications/relevance/quality; managed identity & keyless credentials; Content Understanding for document/field extraction (= "NLP for document processing, emails, ticket analysis").
- **Prep:** Microsoft Learn course **AI-103T00** + the official **study guide as a checklist**; the **exam sandbox** for question mechanics; official **Practice Assessment** when it ships (typically ~8 weeks post-GA — check); hands-on = your Lab A/B AI layers redone with Foundry + Azure OpenAI.
- Links: certification page `learn.microsoft.com/credentials/certifications/azure-ai-apps-and-agents-developer-associate/` · study guide `learn.microsoft.com/credentials/certifications/resources/study-guides/ai-103`

### AI-200 — Developing AI Cloud Solutions on Azure
- **Cert:** Microsoft Certified: Azure AI Cloud Developer Associate — the AZ-204 successor (~60% of AZ-204 carries forward, reweighted for AI workloads).
- **Content pillars:** containers (ACR, App Service, Container Apps) · **vector search** across Cosmos DB / pgvector / Managed Redis · messaging (Service Bus, Event Grid) · **managed identity everywhere** (connection-string answers are usually wrong answers) · observability & diagnosis. Study guide lists **Python** as the language.
- **Caveats:** recently in **beta** (delayed scoring, sparse third-party material). Verify GA status on Microsoft Learn before booking; Practice Assessment likely late. This is exactly why the Week-10 checkpoint exists.
- **Prep:** Microsoft Learn path **AI-200T00**; hands-on = deploy Lab A to Container Apps, add a vector-search feature, wire managed identity to SQL/Key Vault.

### AZ-104 — Azure Administrator Associate (fallback / Set B)
- Stable, not retiring; richest prep ecosystem of any Azure exam: Microsoft Learn path + **John Savill's Technical Training** (YouTube) AZ-104 study cram + official Practice Assessment.
- Strategic value: it is the **prerequisite for Azure Solutions Architect Expert** — pass AZ-104 now, AZ-305 in 2027, and the Expert badge lands exactly when you're settling into an "AI Architect" role.

---

## 4. Timeline (integrates with the labs — full merged calendar lives in file 03)

| Window | Certification thread |
|---|---|
| Jul (wks 1–2) | Azure account + Foundry hands-on (deploy a model, build a toy agent, try Content Understanding). **Python read-fluency on-ramp** — it's absent from your resume and both new exams lean on it; with C/C++/C# it's a fast week. Optional AI-901 sit. |
| Jul–Aug (wks 3–8) | AI-103: Learn path AI-103T00 → study-guide checklist → sandbox → practice assessment if released. Lab A AI layer doubles as lab time. |
| **Mid-Sep (wk 9)** | **AI-103 exam.** |
| Sep–Oct (wks 10–15) | AI-200 path (or AZ-104 after the Week-10 checkpoint). Deploy Lab A to Azure (Container Apps + Azure SignalR + Azure OpenAI + App Insights) — hands-on prep, resume line, and demo link in one move. |
| **Late Oct (wk 16)** | **AI-200 or AZ-104 exam.** |

## 5. Pre-booking checklist (new-exam era discipline)
1. Open the official exam page on Microsoft Learn → confirm **GA vs beta**, language availability, and current skills-measured date.
2. Diff the study guide against your checklist — new exams get revised within months of launch.
3. Confirm the Practice Assessment exists; if not, rely on Learn module knowledge checks + sandbox.
4. Register with a **personal MSA** (not the Coforge work account) so the transcript survives any org change.
5. Book online-proctored only if your room/network passes the system test; otherwise a Pearson VUE centre in Bengaluru.
