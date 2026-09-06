### PROJECT A-EXT — The Model Economics Matrix (hosted vs self-hosted, measured)

> **Placement:** insert in Part 2, immediately after Project A's "Build difficulty" line and before "PROJECT B — Automated Lesson Quality Auditing & Gap Detection".

**Why this extension exists:** You own a Ryzen AI Max+ 395 with 128GB unified memory. That is an unusual hardware profile — enormous capacity at roughly 256 GB/s bandwidth — and it makes you able to do something almost no transition candidate can: load and compare 70B–120B class models at 4-bit against *your own* golden set and report the quality delta. Combined with India-specific data-residency pressure (DPDP Rules notified November 2025 with phased enforcement running through November 2026 and May 2027; RBI requiring payment system data stored in India with any overseas processing returned within 24 hours), this converts the eval harness from a retrieval-quality tool into a **procurement-grade decision tool** — which is what enterprises and services firms actually need and rarely get.

**What it adds to the harness:** Project A's config matrix varies the *retrieval* axis (chunk size × strategy × embedding model × reranker × top-k). This extension adds the **generation and serving axis** on top: model family × parameter count × quantization × hosting mode. Same golden set, same metric runners, one more dimension.

---

#### Architecture

- **Local inference lane:** llama.cpp / Ollama on the Strix Halo box for the capacity-bound comparisons (Qwen-72B, Llama 3.3 70B, GPT-OSS-class 120B at Q4_K_M and Q8). ROCm support on gfx1151 is workable but not first-class — expect Vulkan/llama.cpp to be the reliable path, and budget time for toolchain friction.
- **Hosted lane:** the same prompts through your existing raw-SDK client (a GPT-4-class model, a Claude-class model, plus a small cheap model as the cascade floor).
- **Rented-GPU lane (the gap-closer):** a few hours on an L40S or A100 via E2E Networks, Yotta, or AWS `ap-south-2` (Hyderabad) running vLLM, purely to generate real concurrency numbers. This is the one thing the laptop structurally cannot teach you.
- **Cost model:** a written-down break-even spreadsheet — API cost per 1M tokens vs GPU-hour cost ÷ realistic utilisation, with assumptions exposed rather than buried in a conclusion.

---

#### Hard problems, and why they're hard

- **Capacity ≠ throughput.** 128GB lets you *load* a 70B model; it tells you nothing about what happens at 20 concurrent users. Continuous batching, PagedAttention, KV cache memory pressure, and the throughput-vs-p95-latency curve only appear under real concurrency. Articulating that distinction — and having gone and measured it on rented hardware rather than hand-waving — is the senior signal.
- **Quantization quality loss is task-specific.** Vendors advertise things like INT4 at 4× smaller footprint and 2× faster inference with under 1% accuracy degradation. Nobody believes vendor numbers. Measuring degradation *on your own stratified golden set, per query class*, is the whole point.
- **Sizing vocabulary.** You'll be asked to reason in the market's terms: a quantized 70B serving a small team on 2× A100 80GB or 4× L40S; a 120B at scale needing 4–8× A100/H100. Know how those numbers are derived, not just what they are.
- **The compliance argument is subtler than it looks.** None of DPDP, the RBI directions, HIPAA or NABH actually *mandates* on-premise deployment — each permits properly contracted third-party processing. What on-prem changes is how much of your compliance position depends on somebody else honouring theirs. Framing self-hosting as compliance-surface *reduction* rather than a legal requirement is a strong-hire answer; parroting "DPDP requires on-prem" is a weak one.

---

#### Failure modes and how to detect them

| Failure mode | Detection |
|---|---|
| Quantized model degrades only on one query class (usually multi-hop synthesis) while the aggregate looks fine | Report metrics **stratified by query class**, never as a single mean |
| Local latency looks great single-user, collapses under load | Only visible in the rented-GPU lane — which is why that lane isn't optional |
| Break-even model quietly assumes 100% GPU utilisation | State utilisation as an explicit variable; show the curve, not a point estimate |
| Judge-model contamination (hosted model judging a self-hosted model's output → self-preference bias) | Name the bias, and spot-check against the human-labelled calibration set from Project B |

---

#### Measurement plan

- **Baseline:** hosted GPT-4-class API, no cascade, no cache.
- **Interventions, measured one at a time:**
  1. Small-model cascade with confidence-based escalation
  2. Semantic caching
  3. Self-hosted 70B at Q4
  4. Self-hosted ~30B at Q4
  5. 8B as the floor
- **Metrics:** faithfulness, context precision, answer relevancy (reusing Project A's runners); TTFT and p95 total latency; **cost per resolved query** — not cost per call; and break-even query volume.
- **On the rule of thumb:** the market line is that self-hosting turns cheaper somewhere above ~1M tokens/day. That's somebody else's number. The value is producing your own curve with your own assumptions.
- **Deliverable:** one table plus a short honest write-up answering two questions — at what volume does local win, and which query classes does it lose on.

**Target interview sentence:**

> "On my 100-question stratified golden set, Qwen-72B at Q4_K_M held faithfulness within 4 points of a GPT-4-class API but lost 11 points specifically on cross-lesson synthesis. Cost per resolved query crossed over at roughly N queries/day on a single L40S at 60% utilisation. So my recommendation for a residency-constrained BFSI client would be a cascade — local model for the 80% of single-hop queries, hosted escalation for synthesis — not a wholesale migration."

---

#### Interview clusters this answers

- Cost governance and model cascading — the competency Indian employers rate highly and juniors never have
- Quantization literacy with real, self-generated numbers
- Serving/inference stack: vLLM, continuous batching, KV cache, throughput vs latency
- Data residency and sovereign deployment for BFSI and government accounts
- Evaluation under a second axis (generation/serving, not just retrieval)
- **"When *not* to self-host"** — the judgement question underneath all of the above

---

#### Scope guards

- Reuse the existing golden set. Do **not** author a second one.
- Cap the matrix at ~5 model configs. The point is the method, not exhaustive coverage.
- One rented-GPU session, not an ongoing cluster.
- No fine-tuning.
- Do not build a serving product. A CLI, a results table, and a written analysis is the deliverable.

---

#### Stacking and honest assessment

**Eval-harness stacking:** This is the clearest demonstration of why the harness comes first. The same runners that measured chunking now measure model economics at zero marginal authoring cost — which is itself the argument for building evaluation infrastructure before anything else.

**Build difficulty:** Low-medium *given hardware you already own*, which is precisely why it's high-leverage for you specifically. The real costs are ROCm/toolchain friction on Strix Halo and the discipline to write the cost model honestly rather than reverse-engineering it toward a conclusion you already like.

**Risk to watch:** this is genuinely fun and will happily eat the time Projects B and C need. Timebox it.
