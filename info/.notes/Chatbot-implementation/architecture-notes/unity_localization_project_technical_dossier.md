# Unity Localization / Translation Solution — Technical Project Dossier

> **Purpose:** This document reconstructs the Unity Localization work described in the conversation into a detailed, technically oriented project record suitable for interview preparation, resume/project documentation, and historical context.
>
> **Important accuracy rule:** This dossier intentionally distinguishes between:
> - **Confirmed by firsthand recollection or direct professional evidence**
> - **Strong architectural reconstruction from the described system**
> - **Items that are plausible but not directly verified**
>
> It does **not** claim that the public product name "Unity Translate" has been independently proven. The strongest direct public corroboration currently available is a LinkedIn recommendation from Unity Staff Software Engineer Karl Jones describing the work as the **"Unity Localization solution."**

---

## 1. Executive Summary

### 1.1 Engagement context

The work described here was performed while employed by **Rythmos** (subsequently acquired by **Coforge**) as part of an outsourced engineering engagement supporting **Unity Technologies**.

The engineer was **not a Unity employee**. The working model was effectively:

```text
Rythmos / Coforge
        |
        | outsourced engineering engagement
        v
Unity Technologies
        |
        +-----------------------------+
        |                             |
        v                             v
Unity Engineering / Core            Enterprise Services (ES)
teams                               |
                                    +--------------------------+
                                    |                          |
                                    v                          v
                               Localization               Shared services /
                               and other ES                backend/platform
                               workloads
```

The engineer's primary organizational home for the work described here was the **Enterprise Services (ES)** team. ES functioned as a bridge between Unity's:

- core/editor engineering teams,
- shared backend/platform/infrastructure teams,
- enterprise/customer-facing organizations,
- regional Unity teams,
- and production/customer issue streams.

### 1.2 Primary area

The major focus within ES was **Unity Localization**.

The work was not limited to a simple UI feature or a standalone translation script. The described scope covered:

- localization tooling/workflows,
- automated translation,
- backend/service integration,
- translation-provider integration,
- localization data handling,
- cost/credit estimation,
- feature work,
- bug fixing,
- testing,
- documentation,
- production/customer support,
- and coordination across Unity core and backend systems.

The engineer also supported issues in other products/services that shared common ES/backend infrastructure, particularly:

- Version Control (VCS),
- Asset Store,
- Analytics,
- Backporting Service,
- and Unity Editor-facing functionality.

These should not necessarily be represented as five unrelated projects. The described architecture suggests substantial reuse of common services/workflows and ES ownership boundaries.

---

# 2. What the Project Was

## 2.1 High-level problem

Unity's enterprise customers needed localized application/game content while maintaining a controlled, build-oriented deployment model.

The system supported automated translation/localization within the Unity development workflow.

A simplified conceptual flow was:

```text
Unity project / source strings
        |
        v
Unity Editor localization tooling
        |
        v
Localization service / backend
        |
        +--> legacy translation flow
        |
        +--> machine translation provider(s)
        |
        +--> later AI/LLM translation provider(s)
        |
        v
translated localization data
        |
        v
review / approval / project workflow
        |
        v
Unity build
        |
        v
serialized localization data
        |
        v
deployed enterprise application/game/device
```

The key architectural characteristic was **build-time localization rather than unrestricted runtime cloud synchronization**.

---

# 3. Enterprise Customer Model and Why the Architecture Was Different

The customer base described for this work differed materially from a typical live-service consumer game studio.

Relevant customer categories included:

- game/arcade machine manufacturers,
- automotive / automotive HUD vendors,
- industrial customers,
- embedded/closed-environment customers,
- specialized hardware manufacturers,
- and other enterprise customers with controlled release processes.

These customers may have:

- strict certification requirements,
- limited or controlled connectivity,
- offline or intermittently connected runtime environments,
- immutable production binaries,
- safety/quality constraints,
- long deployment lifecycles,
- and a requirement that the localized content tested for a build be exactly what ships.

Because of this, a runtime model such as:

```text
deployed game
    |
    v
cloud TMS / localization service
    |
    v
download new translations dynamically
```

was not the default model for the described enterprise workflow.

Instead, the workflow emphasized:

```text
translation / approval
        |
        v
Unity Editor / build pipeline
        |
        v
serialized localization assets/data
        |
        v
released binary
```

Once the product left the Unity Editor/build pipeline, the localization content was expected to remain tied to the build unless a new release was intentionally produced.

---

# 4. Comparison With Gridly-Style Localization

A useful conceptual comparison is a modern localization CMS/TMS such as Gridly.

## 4.1 Typical cloud/TMS model

A generalized Gridly-like model:

```text
Unity project
    |
    +--> push strings
    +--> push screenshots/context
              |
              v
          TMS/CMS
              |
      translators / reviewers
              |
      translation memory
              |
       machine translation
              |
              v
         approved data
              |
              +--> pull into Unity build
              |
              +--> potentially fetch at runtime
```

The relevant feature is that some systems permit **runtime retrieval of translation changes**, enabling content to change after the original build.

## 4.2 Described Unity ES model

The described enterprise-oriented Unity system was more tightly integrated with the editor/build workflow:

```text
Unity Editor
    |
    v
Localization data
    |
    v
Unity ES localization/translation services
    |
    +--> translation provider
    +--> automated translation
    +--> AI translation
    +--> cost/credits
    |
    v
translated/approved strings
    |
    v
serialized localization assets
    |
    v
build
    |
    v
enterprise runtime
```

The important difference is:

> **Translation changes were integrated into the product/build lifecycle rather than treating production runtime as a continuously synchronized cloud client.**

This distinction is particularly important for embedded, industrial, automotive, arcade, or otherwise controlled enterprise deployments.

---

# 5. Organizational Architecture

## 5.1 Enterprise Services as a bridge layer

The described ES organization sat between multiple technical ownership areas.

A useful conceptual representation is:

```text
                         +----------------------+
                         | Unity Core / Editor  |
                         | C++ / C# engineering |
                         +----------+-----------+
                                    |
                                    | editor/runtime integration
                                    v
                         +----------------------+
                         | Enterprise Services  |
                         | (ES)                 |
                         +----------+-----------+
                                    |
                   +----------------+----------------+
                   |                                 |
                   v                                 v
          Shared backend/platform           Enterprise workflows
          and infrastructure                / customer support
                   |
                   v
       localization / VCS / Asset Store /
       Analytics / related services
```

ES therefore did not necessarily "own" every code path.

Instead, engineers often had to understand enough of:

- the Unity Editor,
- C++/C# core behavior,
- backend services,
- APIs,
- authentication/IAM,
- customer flows,
- and infrastructure

to diagnose issues crossing organizational boundaries.

## 5.2 Core engineering relationship

The Unity Editor core is heavily based on C++ and C#.

Different senior/core engineering owners were responsible for core technologies or subsystems, for example:

- core Unity/editor C++/C#,
- internal C# systems,
- Version Control,
- Perforce integration,
- and other deeply integrated editor functionality.

The ES team could nevertheless be involved whenever the issue crossed into:

- Asset Store behavior inside the Editor,
- localization tooling inside the Editor,
- Version Control integration,
- backend communication,
- authentication/authorization,
- customer workflows,
- or shared platform services.

Thus a task involving the Asset Store, VCS, Localization or Analytics did not automatically imply four independently designed platforms.

---

# 6. Shared Backend / Platform Model

The described architecture indicates that Unity products such as:

- Asset Store,
- Analytics,
- Version Control,
- Localization

could share substantial backend infrastructure and workflow patterns, with the user-facing experience differing based on the product and IAM-controlled access.

A conceptual model is:

```text
                     Identity / IAM
                           |
                           v
                 +---------------------+
                 | Shared ES Backend   |
                 | / Platform Services |
                 +----------+----------+
                            |
       +--------------------+---------------------+
       |                    |                     |
       v                    v                     v
 Asset Store           VCS / SCM            Localization
 frontend              frontend             frontend
       |                    |                     |
       +--------------------+---------------------+
                            |
                          APIs
                            |
                            v
                  shared platform services
```

Therefore, a defect could be experienced in different product surfaces while ultimately being caused by:

- the same service,
- shared authentication,
- common API patterns,
- common workflow orchestration,
- shared persistence,
- common deployment infrastructure,
- or common platform behavior.

This is an important explanation for why the engineer's LinkedIn history can appear to show several projects while the actual engineering work was performed within a common ES/platform context.

---

# 7. Regional Collaboration: Japan and China

## 7.1 Japan

The engineer recalls working extensively with the **Japan Unity team / stakeholders**, particularly around localization.

The Japan-facing work is consistent with the broader concept of Unity having regional localization operations and technical localization workflows.

## 7.2 China

The engineer also worked with the **China Unity organization/team**.

A significant historical architectural/organizational change occurred when the Unity China organization became more separate from the global organization.

The recalled outcome was that:

- China initially participated in systems/workflows related to the global architecture,
- later the China organization changed or replaced portions of its backend/infrastructure,
- therefore the implementation visible to China later could diverge from the original global implementation.

This is relevant to historical reconstruction: **a system that existed during the original Rythmos engagement may no longer look the same today because regional infrastructure evolved.**

> **Accuracy note:** The exact internal technical migration path, service names, dates, and repository boundaries are not independently verified in this dossier.

---

# 8. Project Phases

The following phases reconstruct the evolution described during the conversation.

---

## Phase 0 — Existing Localization Foundation

### Objective

Provide the base Unity localization workflow and infrastructure used by enterprise projects.

### Existing components

The environment included a Unity-side localization system conceptually involving:

- localized string tables/data,
- target locales,
- editor workflows,
- translated assets/strings,
- backend/service integration,
- and a controlled build pipeline.

### Engineer involvement

The engineer worked within ES to:

- understand the existing workflow,
- diagnose issues,
- implement changes,
- fix defects,
- test behavior,
- document functionality,
- and support enterprise users.

---

# 9. Phase 1 — Automated Translation Using Google Translate / Machine Translation

## 9.1 Objective

Automate a translation workflow so that developers/customer teams did not have to manually translate every string.

The conceptual architecture was:

```text
Unity source strings
       |
       v
localization request
       |
       v
translation backend
       |
       v
Google Translate / MT provider
       |
       v
translated strings
       |
       v
localization data
       |
       v
Unity Editor / build workflow
```

## 9.2 Why a backend was necessary

A robust translation implementation requires more than calling an API from the editor.

A service layer can centralize:

- provider authentication,
- API credentials,
- request validation,
- payload normalization,
- batching,
- language mapping,
- retries,
- error handling,
- logging,
- quota/rate handling,
- billing/credit tracking,
- and response normalization.

This allows Unity editor tooling to remain relatively provider-agnostic.

## 9.3 Likely abstraction boundary

A clean architecture would look like:

```text
Unity Editor
    |
    v
Localization Translation API
    |
    v
Translation Orchestrator
    |
    +--> Provider Adapter: Google
    |
    +--> Provider Adapter: Legacy / Other
    |
    +--> Provider Adapter: AI / LLM
    |
    v
Normalized Translation Result
```

This architecture allows the provider to change without rewriting the whole editor integration.

> **Reconstruction note:** The exact class names, endpoint names, database schema, deployment platform, and provider-adapter interfaces are not preserved in the current conversation and should not be invented during an interview.

---

# 10. Phase 2 — Translation Credits / Cost Estimation

## 10.1 Objective

Integrate translation usage with Unity's existing **credit system**.

The described requirement was that translation should not be an uncontrolled backend call. The customer needed visibility into cost/usage.

A generalized flow:

```text
Translation request
       |
       v
calculate billable units
       |
       +--> characters / words / tokens / provider units
       |
       v
credit estimator
       |
       v
estimated cost / credits
       |
       +--> customer confirmation/workflow
       |
       v
translation provider
       |
       v
actual usage
       |
       v
credit accounting
```

## 10.2 Why this is significant

This turns machine translation from a simple API integration into a **commercially controlled service**.

Relevant engineering concerns include:

- request sizing,
- pricing model,
- currency/credit conversion,
- estimation vs actual billing,
- provider-specific pricing,
- failure behavior,
- partial requests,
- retries and duplicate billing,
- auditability,
- and user-visible cost estimation.

## 10.3 Example conceptual API

```http
POST /translation/estimate

{
  "sourceLanguage": "en",
  "targetLanguages": ["ja", "zh-CN", "de"],
  "textCount": 1250,
  "characterCount": 42000,
  "provider": "google"
}
```

Conceptual response:

```json
{
  "estimatedCredits": 123.45,
  "provider": "google",
  "sourceLanguage": "en",
  "targetLanguages": ["ja", "zh-CN", "de"]
}
```

The exact payload above is illustrative only.

---

# 11. Phase 3 — Translation Workflow Integration

The translation capability became useful only when integrated into the full localization workflow.

A mature workflow can be represented as:

```text
source strings
    |
    v
validate
    |
    v
identify untranslated/changed entries
    |
    v
calculate translation size
    |
    v
estimate credits
    |
    v
request translation
    |
    v
provider processing
    |
    v
normalize result
    |
    v
store translation
    |
    v
mark state/status
    |
    v
editor consumes result
    |
    v
build
```

Important state transitions might conceptually include:

```text
NEW
  |
  v
QUEUED
  |
  v
TRANSLATING
  |
  +--> FAILED
  |
  v
TRANSLATED
  |
  v
REVIEWED
  |
  v
APPROVED
  |
  v
READY_FOR_BUILD
  |
  v
BUILT
```

Again, these state names are conceptual unless they can be verified from retained project artifacts.

---

# 12. Phase 4 — AI / LLM Translation

## 12.1 Evolution

The described system later evolved beyond traditional machine translation.

The remembered trajectory included:

```text
Legacy translation
        |
        v
Google Translate / conventional MT
        |
        v
AI-based translation
        |
        +--> hosted GPT models
        +--> additional models/providers
        +--> modern AI translation workflows
```

Azure-hosted GPT models were part of the described AI phase.

## 12.2 Why adding AI was more than changing an HTTP endpoint

An LLM-based translation path introduces additional engineering requirements:

- prompt/template management,
- language constraints,
- contextual translation,
- terminology handling,
- structured responses,
- token limits,
- batching,
- truncation protection,
- retries,
- model selection,
- model-specific pricing,
- safety/quality controls,
- deterministic formatting,
- caching,
- observability,
- and fallback behavior.

A generalized abstraction is:

```text
TranslationRequest
    |
    +-- sourceLanguage
    +-- targetLanguage
    +-- sourceText
    +-- context
    +-- glossary/terminology
    +-- provider
    +-- model
    |
    v
Translation Orchestrator
    |
    +---------------------------+
    |                           |
    v                           v
Traditional MT             LLM Provider
    |                           |
    v                           v
Provider Adapter            Prompt Builder
                                |
                                v
                          Model Invocation
                                |
                                v
                          Response Parser
                                |
                                v
                        Translation Result
```

---

# 13. AI Translation Cost Integration

The credit system had to evolve with AI pricing.

Traditional MT and LLMs have different cost models.

A generalized calculation can look like:

```text
estimated_cost =
    provider_base_cost
    + input_units * input_rate
    + output_units * output_rate
    + optional processing overhead
```

For an LLM, "units" can be token-based.

For a conventional MT provider, pricing may be character-based.

Therefore a provider abstraction is useful:

```text
ProviderPricingStrategy
       |
       +--> CharacterBasedPricing
       |
       +--> TokenBasedPricing
       |
       +--> RequestBasedPricing
       |
       +--> HybridPricing
```

The existing Unity credit system could then expose a unified user experience:

```text
Provider-specific billing
          |
          v
internal credit conversion
          |
          v
customer-facing estimate
```

This is one of the technically meaningful parts of the project because it combines:

- API integration,
- billing,
- backend architecture,
- editor workflow,
- and AI infrastructure.

---

# 14. Phase 5 — Multi-Provider Translation Architecture

A mature translation system benefits from provider abstraction.

Conceptually:

```text
                     +----------------+
                     | Translation    |
                     | Request        |
                     +-------+--------+
                             |
                             v
                    +-------------------+
                    | Orchestrator      |
                    +---------+---------+
                              |
            +-----------------+------------------+
            |                 |                  |
            v                 v                  v
        Google MT          Azure GPT        Other AI/MT
            |                 |                  |
            +-----------------+------------------+
                              |
                              v
                    Normalized Translation
                              |
                              v
                        Localization DB
```

Benefits:

- provider independence,
- easier migration,
- consistent error handling,
- consistent billing,
- common logging,
- common authentication,
- common client API,
- easier testing.

---

# 15. Localization Data Lifecycle

The complete data lifecycle can be described as follows.

## 15.1 Source extraction

Source language strings originate from the Unity project.

```text
source code / localization assets
              |
              v
        source string set
```

## 15.2 Change detection

Only new or changed strings need translation.

```text
current source
     |
     v
compare with prior version
     |
     +--> unchanged
     |
     +--> new
     |
     +--> modified
     |
     v
translation candidate set
```

## 15.3 Translation

Candidates are sent through the configured translation provider.

## 15.4 Persistence

The translated data is stored in the localization/backend workflow.

## 15.5 Review/approval

Enterprise workflows may require review before inclusion in a release.

## 15.6 Build integration

Approved strings become part of the build's serialized localization content.

---

# 16. Editor vs Runtime Boundary

This is one of the most important architectural details.

## 16.1 Editor-time responsibilities

The Unity Editor side handled concepts such as:

- localization setup,
- locale selection,
- string-table interaction,
- translation initiation,
- translation import,
- status visibility,
- cost estimation,
- and preparation of build assets.

## 16.2 Backend responsibilities

The backend was responsible for:

- service API exposure,
- authentication/authorization,
- translation provider access,
- orchestration,
- persistence,
- billing/credits,
- status tracking,
- operational logging,
- and infrastructure concerns.

## 16.3 Runtime responsibilities

The shipped runtime primarily consumed the finalized, serialized localization data.

Conceptually:

```text
EDITOR
  |
  +--> translate
  +--> review
  +--> approve
  +--> serialize
  |
  v
BUILD
  |
  v
RUNTIME
  |
  +--> load localization assets
  +--> resolve locale
  +--> display localized strings
```

This is different from a runtime cloud synchronization system.

---

# 17. Security and IAM Considerations

Because several Unity products shared platform infrastructure, IAM was important.

The described environment used different user-facing experiences controlled by identity/access management.

A conceptual model:

```text
User
  |
  v
Identity / Authentication
  |
  v
Authorization / IAM
  |
  +--> Asset Store capabilities
  +--> VCS capabilities
  +--> Analytics capabilities
  +--> Localization capabilities
  |
  v
shared backend APIs
```

A localization request would therefore need to consider:

- authenticated identity,
- authorization,
- tenant/customer boundaries,
- project ownership,
- permitted locales,
- translation permissions,
- and access to billing/credits.

---

# 18. API / Service Design Considerations

The backend translation service can be conceptualized around several API operations.

## 18.1 Translation estimate

```http
POST /translation/estimate
```

Purpose:

- estimate usage,
- show credit cost,
- validate request.

## 18.2 Translation request

```http
POST /translation/jobs
```

Purpose:

- create translation job,
- validate input,
- associate it with customer/project/user.

## 18.3 Job status

```http
GET /translation/jobs/{id}
```

Purpose:

- monitor asynchronous translation state.

## 18.4 Result retrieval

```http
GET /translation/jobs/{id}/result
```

Purpose:

- retrieve normalized translations.

## 18.5 Provider abstraction

Backend internally maps:

```text
job.provider
      |
      +--> Google
      +--> Azure/OpenAI-hosted GPT
      +--> future provider
```

Exact routes are illustrative and should not be presented as retained historical endpoint names.

---

# 19. Synchronous vs Asynchronous Processing

Machine translation can become expensive and slow when a customer submits thousands of strings.

A scalable design is therefore:

```text
Editor
  |
  | submit
  v
API
  |
  | create job
  v
Queue
  |
  v
Worker
  |
  +--> provider API
  |
  v
Persist result
  |
  v
job = COMPLETE
```

This supports:

- retries,
- batching,
- provider throttling,
- long-running jobs,
- progress tracking,
- failure isolation.

A synchronous implementation might be acceptable for small requests, but an asynchronous job model is generally more scalable.

> **Reconstruction note:** The exact historical processing model (queue technology, worker implementation, orchestration mechanism) is not verified by the conversation and must not be invented.

---

# 20. Reliability and Failure Handling

Translation services depend on external providers, so failures can originate outside Unity.

Important failure classes include:

### Authentication failure

```text
Unity backend -> provider
                 |
                 +--> invalid credential
```

### Rate limiting

```text
provider -> HTTP 429 / quota exceeded
```

### Timeout

```text
provider -> no response
```

### Partial batch failure

```text
1000 strings requested
  |
  +--> 950 succeeded
  +--> 50 failed
```

### malformed provider response

The backend needs validation before writing translation results.

### Duplicate requests

Retries can accidentally trigger duplicate charges unless idempotency is considered.

A robust job may therefore use:

```text
client request ID
       |
       v
idempotency key
       |
       v
translation job
```

---

# 21. Testing Strategy

The engineer explicitly received recognition for **features, bug fixes, tests and documentation** from Unity Staff Software Engineer Karl Jones.

A translation platform would require multiple testing layers.

## 21.1 Unit testing

Targets:

- translation request validation,
- language-code mapping,
- provider adapters,
- pricing calculations,
- credit conversion,
- serialization/deserialization,
- retry logic.

## 21.2 Integration testing

Targets:

```text
Editor
  |
  v
Localization API
  |
  v
Translation service
  |
  v
Provider adapter
```

## 21.3 Failure-path testing

Examples:

- provider unavailable,
- timeout,
- invalid locale,
- unsupported language pair,
- quota exceeded,
- empty source string,
- malformed response,
- duplicate submission.

## 21.4 Regression testing

Especially important because localization services can affect:

- Unity Editor behavior,
- build output,
- customer workflows,
- and shared platform infrastructure.

---

# 22. Documentation Responsibilities

The Karl Jones recommendation specifically mentions:

- features,
- bug fixes,
- tests,
- and **documentation**.

Relevant documentation categories would include:

- user workflow,
- setup/configuration,
- translation process,
- provider behavior,
- error handling,
- API contracts,
- troubleshooting,
- release notes,
- known limitations,
- and support procedures.

Documentation was therefore part of the engineering lifecycle rather than an afterthought.

---

# 23. Production / Customer Support Engineering

The work should not be represented as only greenfield coding.

The ES environment included substantial:

- debugging,
- production support,
- technical investigation,
- bug reproduction,
- root-cause analysis,
- cross-team escalation,
- and customer issue resolution.

This aligns directly with Les Plumridge's recommendation describing Raghuram as a core member of the **outsourced Sustained Engineering team** who conducted detailed technical investigations, resolved complex bugs, delivered bug fixes and quality-of-life improvements, and supported top-tier customers.

This is important because it demonstrates experience with **production-grade systems**, not only development environments.

---

# 24. Debugging Difficult Issues

Sustained Engineering work often involves bugs that cannot be reproduced with a minimal local setup.

A typical investigation pattern:

```text
customer report
     |
     v
collect logs / configuration
     |
     v
identify affected subsystem
     |
     v
compare working vs failing environments
     |
     v
trace backend/editor interaction
     |
     v
root-cause hypothesis
     |
     v
instrument / patch / reproduce
     |
     v
fix
     |
     v
regression tests
     |
     v
release / backport
```

Sébastien Rombauts' recommendation provides independent corroboration of this style of work in Unity Editor Version Control:

- difficult longstanding issue,
- unable to reproduce locally,
- customer-specific repository,
- deep technical investigation,
- eventual resolution.

Although that recommendation is specifically about VCS, it provides strong evidence of the broader ES/Sustained Engineering engineering style.

---

# 25. Version Control Relationship to Localization / Shared Infrastructure

VCS is not being claimed here as a localization feature.

The reason it appeared alongside Localization in the engineer's work history is architectural/organizational:

- VCS could share common ES/platform infrastructure,
- the Editor may surface backend-connected features,
- IAM and service layers are shared,
- ES engineering supported cross-cutting issues,
- and a defect in a common service can affect multiple product experiences.

Therefore:

```text
Localization
VCS
Asset Store
Analytics
```

should not automatically be interpreted as four independent codebases owned exclusively by the engineer.

The broader description is:

> **Cross-product Enterprise Services engineering over shared Unity platform/backend infrastructure.**

---

# 26. Unity Editor Integration

The Unity Editor itself is a major integration boundary.

A typical localization interaction may be:

```text
Unity Editor
   |
   +--> user selects source/target locale
   |
   +--> user initiates translation
   |
   v
client-side API layer
   |
   v
Unity backend
   |
   v
translation service
   |
   v
result
   |
   v
Editor imports/updates localization data
```

Because the Editor is core Unity software, responsibility can cross:

- ES,
- Core Editor,
- C# internal systems,
- backend,
- and platform infrastructure teams.

This explains why an ES engineer can work with core engineers such as those responsible for C++/C# or VCS without personally being a member of the core engine organization.

---

# 27. Source Control and Localization

Localization data itself must be compatible with source control and build reproducibility.

Important concerns include:

- deterministic localization files,
- merge conflicts,
- locale additions/removals,
- table changes,
- generated data,
- imported translations,
- file versioning,
- and build reproducibility.

A localized build should be reproducible from a known source revision:

```text
Git/Perforce revision
        +
localization data revision
        +
build configuration
        |
        v
deterministic build
```

This makes Version Control relevant to localization even when VCS isn't itself a translation system.

---

# 28. Build Reproducibility

For enterprise deployments, the localized output should correspond to a known build state.

A useful conceptual model:

```text
Source Revision = R12345
Localization Revision = L67890
Translation Provider = X
Translation Version/State = Approved
Build Configuration = Production-JP

                     |
                     v

                Release Build
```

This allows an organization to identify exactly which localized content entered a release.

---

# 29. Why Runtime Dynamic Updates Were Not the Default

The described customer model creates strong constraints.

Examples:

### Automotive

A vehicle/HUD system may require software validation before deployment.

### Industrial

An industrial system may operate in controlled networks.

### Arcade/game machine

A manufacturer may produce a fixed appliance rather than a continuously updated cloud-connected client.

Therefore:

```text
cloud changed translation
        |
        X
```

is not equivalent to:

```text
approved translation
      |
      v
validated build
      |
      v
deployed product
```

The latter is safer and more predictable in controlled environments.

---

# 30. Localization Solution vs Public Unity Localization Package

This distinction is essential when discussing the project.

## 30.1 Public Localization Package

The public Unity Localization package is a developer-facing Unity package providing localization functionality within Unity projects.

## 30.2 Described Unity Localization Solution

The work described here includes broader infrastructure and enterprise workflows around localization:

- translation services,
- backend integration,
- automated translation,
- provider integration,
- AI translation,
- credit/cost estimation,
- enterprise support,
- and regional workflows.

Therefore it would be misleading to summarize the entire project as:

> "I only worked on the Unity Localization Package."

A more accurate description is:

> **Worked on Unity's broader Localization solution and associated Enterprise Services/backend workflows, including automated translation and translation-service integration.**

---

# 31. Why "Unity Translate" May Be Hard to Find Today

Several explanations are plausible:

1. The name may have been an internal/project name rather than a public product name.
2. The service may have been renamed.
3. The service may have been retired.
4. The architecture may have moved toward external TMS providers.
5. The service may have been reorganized across Unity organizations.
6. China-specific infrastructure may have diverged.
7. Internal engineering systems frequently have little public documentation.

Therefore the absence of a current public page does **not** prove the internal system did not exist.

---

# 32. Evidence From Unity / Professional References

The strongest direct professional evidence described in this conversation is:

## 32.1 Karl Jones — Unity Staff Software Engineer

Karl's LinkedIn recommendation states that he worked with Raghuram on the:

> **"Unity Localization solution"**

and says Raghuram:

- was pivotal to development of the system,
- helped meet a key release date,
- supported subsequent updates,
- developed features,
- fixed bugs,
- created tests,
- and contributed documentation.

This is the strongest direct public evidence connecting the engineer to the Unity Localization solution.

## 32.2 Les Plumridge — Unity / Sustained Engineering leadership

Les's recommendation describes Raghuram as a core member of the:

> **"outsourced Sustained Engineering team"**

and highlights:

- detailed technical investigation,
- complex bug resolution,
- bug fixes,
- quality-of-life improvements,
- top-tier customer support,
- mentoring,
- and operational reliability.

This corroborates the Rythmos-to-Unity outsourced-engineering relationship and the production nature of the work.

## 32.3 John Dickinson — Unity Engineering Manager

John's recommendation identifies work on the:

> **"Unity Backporting Service team"**

and confirms work with:

- C++,
- C#,
- Unity,
- bug fixing of live product versions,
- reliability,
- and high-quality engineering.

## 32.4 Sébastien Rombauts — Unity Senior Software Engineer

Sébastien's recommendation identifies work on difficult issues in Unity Editor's:

> **Version Control module**

including an issue that could not be reproduced locally and required dealing with a complex end-user repository.

Together, these references show a multi-year engineering relationship across Unity systems while remaining consistent with an outsourced Rythmos/Unity model.

---

# 33. Historical Unity Localization Career Evidence

Public Unity hiring material also establishes that Unity has maintained a technical localization discipline.

## 33.1 Senior Localization Engineer — Bengaluru

A Unity posting for **Senior Localization Engineer** in Bengaluru describes participation in the **Global Localization Team** and technical work involving:

- localization automation frameworks,
- localization workflows across different technology stacks/architectures,
- source-control automation,
- complex automation pipelines,
- Translation Memories,
- Term Bases,
- Machine Translation engines,
- TMS integrations,
- APIs/connectors,
- client-side and web applications,
- Python/JavaScript,
- and GenAI-driven translation workflows.

This demonstrates that Unity treats localization as a software/engineering discipline, not solely as manual translation.

## 33.2 Global Localization / Technical Project Manager

A Unity posting for a Technical Project Manager in San Francisco described responsibilities around:

> **"Global Localization production services and workflows"**

including terminology, translation management systems, coordination, and localization operations.

This is useful evidence that Unity has used the language of **localization services and workflows**, not simply "localization package."

## 33.3 Localization — APAC / Seoul

A later Unity localization role focused on APAC and referenced:

- Asia-Pacific internal stakeholders,
- Seoul and Tokyo localization personnel,
- localization engineers,
- machine-translation workflows,
- automation tools,
- and regional localization operations.

This is relevant to the recollection of collaboration with Japan and other Asia-region Unity teams.

---

# 34. Recommended Interview Description

A technically defensible description is:

> I was employed by Rythmos and worked as part of an outsourced engineering engagement supporting Unity Technologies. My main organization was Enterprise Services (ES), which acted as a bridge between Unity's core/editor teams, backend/platform engineering and enterprise customers.
>
> My primary focus was Unity's Localization solution. I worked on the engineering side of automated localization, including backend/service integration, translation workflows, machine translation, later AI/LLM-based translation, and integration with Unity's credit system for translation cost estimation. I also handled feature development, debugging, testing, documentation and production/customer issues.
>
> I worked with Unity teams in multiple regions, including Japan and at times China. I also supported issues in other Unity products that shared common ES/backend infrastructure, which is why my work history can appear across Localization, VCS, Asset Store, Analytics and other services even though the underlying engineering organization and shared platform were closely related.

---

# 35. Resume-Oriented Version

A concise high-signal version:

> **Rythmos / Coforge — Client: Unity Technologies**
>
> Worked within Unity's outsourced Enterprise Services engineering organization, bridging Unity Editor/core systems, shared backend/platform services and enterprise customers. Contributed extensively to Unity's Localization solution, developing and maintaining automated translation workflows, backend integrations, machine-translation and later AI/LLM translation capabilities, translation credit/cost estimation, tests and production fixes. Supported cross-product issues across shared ES infrastructure including Localization, Version Control, Asset Store and Analytics.

---

# 36. More Technical Resume Version

> **Unity Localization / Enterprise Services**
>
> - Developed and maintained localization/translation workflows integrated with Unity Editor and backend platform services.
> - Implemented automated translation integrations with machine-translation providers and later AI/LLM-based translation services.
> - Extended Unity's credit/billing workflow to estimate translation usage and cost across provider-specific pricing models.
> - Built and maintained backend/service integration, request validation, translation orchestration, result processing and failure handling.
> - Delivered features, production bug fixes, regression tests and technical documentation.
> - Investigated cross-system issues spanning Unity Editor, shared ES backend infrastructure, IAM-controlled services and enterprise workflows.
> - Collaborated with Unity engineering and regional teams including Japan and China.
> - Supported shared platform issues impacting Localization, Version Control, Asset Store and Analytics workflows.

---

# 37. Interview Story Structure

When asked:

**"Tell me about your Unity localization project."**

Use this progression:

### 1. Context

"I was at Rythmos, not a Unity employee, and was part of an outsourced engineering engagement supporting Unity."

### 2. Organization

"My main organization was Enterprise Services, which sat between Unity core/editor teams, backend/platform teams and enterprise customers."

### 3. Problem

"Enterprise customers needed automated localization integrated into their Unity workflow, but many of them were embedded/controlled deployments where runtime cloud synchronization was not appropriate."

### 4. Architecture

"The editor-side tooling communicated with Unity backend services, which orchestrated translation providers and persisted the resulting localized data."

### 5. First generation

"The workflow initially relied on machine translation, including Google Translate."

### 6. Commercialization

"We integrated the flow with Unity's credit system so customers could estimate and account for translation usage."

### 7. AI evolution

"Later the same architecture evolved to support AI/LLM translation, including hosted GPT-based models, which introduced different token, pricing and response-handling requirements."

### 8. Engineering work

"I worked across features, backend integration, bug fixes, tests, documentation and production investigations."

### 9. Enterprise constraints

"The resulting localization data was primarily intended to become part of the validated build rather than being dynamically replaced in production at runtime."

### 10. Cross-team aspect

"Because ES shared infrastructure with other Unity services and the Editor, issues could cross Localization, VCS, Asset Store, Analytics and core/editor components."

---

# 38. What Not to Say Without Evidence

Avoid claiming exact details that are not preserved in the current context.

Do **not** invent:

- specific database technology,
- specific cloud provider,
- exact Kubernetes/ECS/Azure/AWS deployment,
- exact programming language for every backend component,
- exact REST endpoint names,
- exact database tables,
- exact queue technology,
- exact service names,
- exact Git repository names,
- exact translation schema,
- exact number of microservices,
- exact request throughput,
- exact customer count,
- exact translation volume,
- exact dates for every architectural phase.

When asked, describe the architectural responsibility rather than guessing implementation details.

---

# 39. Confirmed vs Reconstructed Knowledge Matrix

| Topic | Confidence | Basis |
|---|---|---|
| Worked for Rythmos, later Coforge | **Confirmed** | Employment history supplied by engineer |
| Worked with Unity as client | **Confirmed** | Multiple Unity professional recommendations |
| Part of outsourced ES/Sustained Engineering environment | **Confirmed** | Les Plumridge recommendation |
| Worked on Unity Localization solution | **Confirmed** | Karl Jones recommendation |
| Feature development | **Confirmed** | Karl Jones recommendation |
| Bug fixes | **Confirmed** | Karl + Les + John recommendations |
| Tests | **Confirmed** | Karl recommendation |
| Documentation | **Confirmed** | Karl recommendation |
| Unity Backporting Service work | **Confirmed** | John recommendation |
| Unity Editor VCS work | **Confirmed** | Sébastien recommendation |
| Japan collaboration | **Firsthand recollection** | Engineer |
| China collaboration | **Firsthand recollection** | Engineer |
| China later diverged in backend/infrastructure | **Firsthand recollection / historical context** | Engineer; exact migration details unverified |
| Localization focused on enterprise customers | **Firsthand recollection** | Engineer |
| Google Translate phase | **Firsthand recollection** | Engineer |
| AI/GPT translation phase | **Firsthand recollection** | Engineer |
| Unity credit integration for translation costs | **Firsthand recollection** | Engineer |
| Build-time rather than unrestricted runtime translation | **Firsthand architectural recollection** | Engineer |
| Shared backend/platform across Asset Store/VCS/Analytics/Localization | **Strong architectural recollection** | Engineer |
| IAM-controlled product experiences | **Strong architectural recollection** | Engineer |
| Exact name "Unity Translate" | **Not independently proven** | Internal name recollection |
| Exact endpoint/database/cloud architecture | **Not currently verified** | No retained artifacts in conversation |

---

# 40. Suggested Technical Architecture Diagram

```text
                         UNITY CUSTOMER / USER
                                  |
                                  v
                      +-------------------------+
                      | Unity Editor / Tooling   |
                      | C# + core editor layer  |
                      +------------+------------+
                                   |
                              authenticated
                                   |
                                   v
                      +-------------------------+
                      | IAM / Authorization     |
                      +------------+------------+
                                   |
                                   v
                      +-------------------------+
                      | ES / Backend API Layer  |
                      +------------+------------+
                                   |
                            +------+------+
                            |             |
                            v             v
                 +----------------+   +----------------+
                 | Localization   |   | Shared ES /    |
                 | Orchestrator   |   | Platform APIs  |
                 +-------+--------+   +--------+-------+
                         |                     |
               +---------+----------+          |
               |         |          |          |
               v         v          v          v
            Google     AI/LLM     Future     Credits /
             MT       Provider    Provider   Billing
               |         |          |
               +---------+----------+
                         |
                         v
                Normalized Translation
                         |
                         v
                Localization Persistence
                         |
                         v
                Review / Approval Workflow
                         |
                         v
                  Unity Build Pipeline
                         |
                         v
              Serialized Localization Data
                         |
                         v
                Enterprise Runtime
```

---

# 41. Alternative Shared Platform View

```text
                        Identity / IAM
                              |
                              v
                    +----------------------+
                    | Shared ES Platform   |
                    +----------+-----------+
                               |
          +--------------------+---------------------+
          |                    |                     |
          v                    v                     v
    Localization           Version Control      Asset Store
          |                    |                     |
          +--------------------+---------------------+
                               |
                               v
                          Shared services
                               |
                               v
                           Infrastructure

                    Analytics also participates
                    in shared service patterns
```

The purpose of this diagram is to explain why one ES engineer can legitimately receive recommendations referring to multiple Unity products without those being unrelated job changes.

---

# 42. Engineering Challenges

The project's engineering complexity came from the intersection of several systems:

```text
Localization
    +
Unity Editor
    +
Backend APIs
    +
External translation providers
    +
AI/LLM providers
    +
Credits/billing
    +
IAM
    +
Source control
    +
Enterprise deployment constraints
    +
Regional operations
    +
Production support
```

This is significantly broader than a simple "translation API integration."

---

# 43. Key Engineering Competencies Demonstrated

The project demonstrates experience in:

### Backend integration

- API design
- external provider integration
- service orchestration
- authentication
- authorization
- failure handling

### Enterprise engineering

- multi-team coordination
- customer-facing systems
- production support
- controlled release workflows
- operational reliability

### AI engineering

- LLM provider integration
- prompt-driven processing
- model/provider abstraction
- usage/cost tracking

### Software engineering

- feature development
- debugging
- regression testing
- documentation
- source control
- release support

### Platform engineering

- shared infrastructure reasoning
- cross-service troubleshooting
- IAM
- service dependencies

---

# 44. How to Explain the "No Public Page" Problem

A technically safe explanation is:

> The work was performed through Rythmos as an outsourced Unity engineering engagement. The specific localization service was an internal/customer-facing system, not necessarily a separately marketed Unity product. Unity's public careers material does independently document a Global Localization engineering function involving automation frameworks, machine translation engines, TMS integrations, APIs and GenAI workflows. In addition, a Unity Staff Software Engineer publicly recommended me for my work on the "Unity Localization solution."

This avoids the fragile claim:

> "Google search proves Unity Translate existed."

The stronger statement is:

> **"My work is corroborated by Unity employees and by Unity's own localization engineering hiring material."**

---

# 45. Evidence Preservation Recommendations

For interview verification, maintain a private evidence folder containing only material you are legally and contractually allowed to retain.

Recommended categories:

```text
evidence/
├── employment/
│   ├── Rythmos employment documentation
│   └── Coforge transition documentation
│
├── linkedin/
│   ├── Karl-Jones-recommendation.pdf
│   ├── Les-Plumridge-recommendation.pdf
│   ├── John-Dickinson-recommendation.pdf
│   └── Sebastien-Rombauts-recommendation.pdf
│
├── unity-careers/
│   ├── senior-localization-engineer-bengaluru.pdf
│   ├── global-localization-technical-pm.pdf
│   └── localization-apac.pdf
│
└── personal-project-notes/
    ├── localization-architecture.md
    └── interview-notes.md
```

Do **not** retain or disclose proprietary Unity source code, confidential architecture diagrams, credentials, private tickets, customer data or other restricted material merely for interview verification.

---

# 46. Final Technical Summary

The most accurate technical characterization of the work is:

> **A multi-phase enterprise localization engineering initiative implemented within Unity's Enterprise Services ecosystem, integrating Unity Editor workflows with backend localization services, automated machine translation, later AI/LLM translation, translation credit/cost accounting, and controlled build-time localization for enterprise customers.**

The engineer's role was not simply:

```text
"translator"
```

or:

```text
"Unity Localization package developer"
```

It was closer to:

```text
Rythmos outsourced engineering
            |
            v
Unity Enterprise Services
            |
            +--> Localization engineering
            +--> Backend/service integration
            +--> Automated translation
            +--> AI translation
            +--> Credits / cost estimation
            +--> Production support
            +--> Cross-team debugging
            +--> Enterprise customer workflows
            |
            +--> Shared platform issues
                    |
                    +--> VCS
                    +--> Asset Store
                    +--> Analytics
                    +--> Unity Editor/core boundaries
```

The strongest public corroboration is the Unity Staff Software Engineer recommendation explicitly identifying the work as the **Unity Localization solution**, combined with recommendations from Unity engineering/management personnel describing the broader outsourced Sustained Engineering relationship and additional Unity systems.

---

# Appendix A — Safe Interview Terminology

Preferred:

- "Unity Localization solution"
- "Unity's Global Localization engineering ecosystem"
- "Unity Enterprise Services"
- "outsourced engineering engagement supporting Unity"
- "automated translation workflow"
- "machine translation integration"
- "AI/LLM translation integration"
- "translation backend"
- "translation credit/cost estimation"
- "Unity Editor integration"
- "shared ES/backend infrastructure"
- "build-time localization for enterprise deployments"

Avoid unless you have documentary evidence:

- "Unity Translate was an official public Unity product"
- "I was a Unity employee"
- "Unity internally used exactly this database/queue/cloud architecture"
- "I owned all of Unity Localization"
- "I designed Unity's entire localization platform"
- "all Asset Store/VCS/Analytics code was one codebase"

---

# Appendix B — One-Minute Technical Explanation

> I worked for Rythmos on an outsourced engineering engagement with Unity, primarily within Enterprise Services. My main area was the Localization solution. The architecture connected Unity Editor-side localization workflows with backend services that could orchestrate machine translation and later AI/LLM translation providers. We also integrated the workflow with Unity's existing credit infrastructure so translation usage could be estimated and accounted for. My work covered features, backend/service integration, debugging, tests, documentation and production support. The system was particularly relevant to enterprise customers such as embedded, automotive, industrial and arcade-style deployments, where localization typically needed to be finalized as part of a validated build rather than dynamically synchronized from the cloud after release. Because ES shared platform/backend infrastructure with other Unity products, I also supported issues involving VCS, Asset Store and Analytics, often crossing boundaries between Unity Editor core engineering and backend teams.

---

# Appendix C — Important Qualification

This document is a **reconstructed technical record** based on:

1. The engineer's firsthand recollection provided in conversation.
2. Direct LinkedIn recommendations supplied in conversation from Unity employees/leadership.
3. Public Unity localization career material discussed in the conversation.

It is **not** a recovered copy of Unity's confidential architecture documentation.

Where exact technical implementation details were not provided, this dossier intentionally uses **conceptual architecture** rather than fabricating implementation specifics.

That distinction should be preserved during interviews.