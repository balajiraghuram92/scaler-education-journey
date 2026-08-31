# FDE Phase 12 — Module 5: Enterprise Communication, Consulting & LLM Engineering (Lessons 7-12 of 12, module complete)

Six lessons, authored content + MCQs, ready for local-LLM ingestion via
`phase-12-enterprise-consulting-llm-prompt.md` in this same directory.

Course: `fde-curriculum` · Module: `enterprise-consulting-llm` ("5. Enterprise Communication, Consulting & LLM Engineering")

This is the second half of a 12-lesson module. Phase 11 covered lessons 1-6 (customer discovery,
scoping, stakeholder communication, demo storytelling, LLM fundamentals for production, and
prompt engineering for production systems). This phase covers lessons 7-12 — RAG Architecture,
RAG over Customer Documents & Hybrid Search, RAG Evaluation/RAGAS, LLM Safety/Guardrails,
Cost/Latency/Model Routing, and a capstone Assessment — and **completes Module 5**.

These six lessons deliberately build one level up from prerequisite-module content already
taught in `phase-1-agentic-ai-core-content.md`'s "RAG (Retrieval-Augmented Generation)" and
"Advanced Prompting & AI Safety Basics" lessons, and from that same phase's "GenAI World & LLM
Landscape" model-tier-routing example. None of the RAG pipeline mechanism, chunking basics,
RAGAS metric definitions, or prompt-injection mechanics are re-explained here — this phase is
production/customer-deployment specifics on top of that foundation. Lessons 5 and 6 in Phase
11 explicitly forward-referenced two topics this phase resolves: lesson 6 ("Prompt Engineering
for Production Systems") named "a later lesson in this same module, on cost, latency, and model
routing" — resolved by lesson 11 here — and its red-teaming discipline (on top of the mechanistic
injection-defense lesson) is extended into an ongoing guardrail pipeline by lesson 10 here.

---

# LESSON 7

```yaml
lesson_id: fde-enterprise-consulting-llm-07-rag-architecture-ingestion-and-retrieval
lesson_title: "RAG Architecture: Ingestion & Retrieval"
lesson_order: 7

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Design an ingestion pipeline that handles a real customer's messy document set (mixed formats, scanned PDFs, permission metadata) rather than a clean text corpus."
  - "Build incremental re-ingestion that keeps an index in sync with a live document source without a full reindex on every change."
  - "Attach access-control metadata to chunks at ingestion time so retrieval can enforce it later, rather than retrofitting permissions after the fact."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# RAG Architecture: Ingestion & Retrieval

## Concepts Covered

The RAG lesson from the prerequisite module covered chunking trade-offs and the ingestion/retrieval/generation pipeline against a clean, already-text source. A real customer's document set is rarely clean text: it is a mix of PDFs (some digitally native, some scanned images with no text layer), Word and PowerPoint exports, Confluence or SharePoint pages with embedded tables and images, and CSVs someone attached to an email three years ago. The first architectural decision an FDE makes is not chunking strategy — it is parsing strategy per format, because a chunker only ever sees what the parser handed it, and a parser that silently drops a table or garbles a scanned page produces chunks that look fine and retrieve badly. A scanned PDF needs OCR before it has any text to chunk at all, and OCR quality on real customer scans (a faxed policy document, a photographed whiteboard) varies enough that a production pipeline needs a confidence signal from the OCR step and a way to flag low-confidence pages for human review rather than silently ingesting garbled text as if it were clean. Tables are their own problem: a naive parser flattens a table into a single run of text that loses row/column structure, destroying exactly the information a query about "the Q3 number for the EMEA region" needs; a table-aware parser that preserves structure (even as a simple markdown table embedded in the chunk) keeps that information retrievable.

The second reality the prerequisite lesson didn't need to cover is that a customer's document set is not static. A policy wiki gets edited weekly; a product doc gets a new revision; an old FAQ gets deleted because it's wrong. A pipeline that only supports a full reindex — re-parsing, re-chunking, and re-embedding every document from scratch — becomes operationally unusable at any real document count, because a full reindex is slow, expensive (every re-embedding call is billed), and creates a window where the index reflects neither the old nor the new state cleanly. Incremental re-ingestion tracks a per-document change signal (a source system's last-modified timestamp, a content hash, or a webhook from the source system itself) and only re-parses, re-chunks, and re-embeds the documents that actually changed, deleting the stale chunks for a removed or superseded document rather than leaving orphaned vectors that can still be retrieved and cited long after the source was deleted. Getting this wrong in a specific, damaging way is common: a customer edits a policy to fix a compliance error, the FDE's pipeline never re-syncs that one document, and the RAG system keeps confidently citing the now-wrong version indefinitely, which is a worse outcome than having no RAG system at all, because it looks authoritative while being stale.

The third reality is access control, and it has to be designed at ingestion time, not bolted on at query time. A customer's document set is rarely uniformly readable by everyone who will query it — HR policy documents an employee shouldn't see, a legal hold on certain contracts, a finance folder scoped to a specific team. If ingestion doesn't capture which documents (and ideally which chunks, since a single document can mix restricted and unrestricted sections) each requesting user or role is entitled to see, retrieval has no metadata to filter on later, and the only fallback is either over-restricting (excluding documents from the index entirely, which breaks retrieval for people who should see them) or under-restricting (returning a chunk from a document the querying user was never authorized to read). The correct design attaches access-control metadata — source system permissions, an ACL list, or a role tag — to every chunk during ingestion, sourced from the same permission system the original document lived in, so that retrieval-time filtering (covered in the next lesson) has something real to filter against.

## Practical Backend Scenario

An FDE builds RAG ingestion for a manufacturing customer's internal knowledge base: a mix of PDF work-instruction documents (many are scanned images of printed pages from an older system), a Confluence space for engineering standards, and an HR SharePoint site with policy documents restricted to the HR team. The pipeline runs OCR on scanned PDFs, flags any page under an 85% OCR-confidence threshold into a review queue rather than ingesting it silently, preserves table structure from the engineering-standards pages (which contain torque specification tables critical to the content), and tags every chunk from the HR SharePoint site with a `role:hr` access tag pulled directly from SharePoint's own permission API at ingestion time — not inferred or hardcoded. A nightly incremental job checks each source's last-modified timestamp against the index's stored value per document, re-ingesting only what changed; when a torque spec is corrected mid-quarter, the corrected document's chunks replace the old ones within a day rather than the RAG system citing the superseded value for months until the next full reindex.

## Practice Loop

1. Take 3-4 source documents in different formats (a scanned image with no text layer, a document containing at least one table, and a plain text or markdown file) and build format-specific parsing for each, noting exactly what a naive single parser would lose from the scanned document and the table.
2. Add an OCR confidence check to the scanned-document path and route anything below a threshold you choose into a separate "needs review" output instead of silently ingesting it.
3. Measure what actually changes in the index by editing one source document, re-running only your incremental sync, and diffing the chunk set before and after — this diagnostic step confirms your sync only touched the changed document's chunks, not the entire index.
4. Delete a source document entirely and confirm your pipeline removes its chunks from the index rather than leaving them orphaned and retrievable.
5. Add an access-control tag to a subset of your test documents (a simple role string is enough) at ingestion time, sourced from a field on the document itself rather than hardcoded per document, and verify every chunk from a tagged document carries the tag through to the index.

## Evidence of Understanding

You can design format-specific parsing for a customer's actual mixed document set, including a confidence-gated path for OCR on scanned content and structure-preserving handling for tables. You can build incremental re-ingestion that re-syncs only changed or deleted documents using a change signal from the source system, rather than requiring a full reindex, and you can explain the operational and correctness cost of a pipeline that only supports full reindexes. You can explain why access-control metadata has to be captured at ingestion time from the document's actual source-system permissions, and why retrofitting it at query time doesn't work without that metadata already present on each chunk.

## Suggested Extension

Add a per-source ingestion health dashboard that reports, per document, its last successful sync timestamp, its OCR confidence (if applicable), and its access-control tag — and use it to answer, for any given chunk retrieved by the system, "when was this last verified against its source, and who is allowed to see it."
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why parsing strategy comes before chunking strategy
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say the first architectural decision for a real customer document set is parsing strategy per format, not chunking strategy?

**OPTIONS:**
- [ ] A: Chunking strategy is irrelevant once documents are ingested
- [x] B: A chunker only ever sees what the parser produced, so a parser that silently drops a table or garbles a scanned page produces chunks that look fine but retrieve badly, regardless of how good the chunking strategy is
- [ ] C: Parsing and chunking always happen in the same step and cannot be separated
- [ ] D: Chunking strategy only matters for plain text files

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The chunker operates on whatever text the parser extracted; if the parser lost information (a flattened table, a garbled scan), no chunking strategy downstream can recover it, which is why parsing quality per format is the earlier, higher-leverage decision.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [parsing, chunking, ingestion-pipeline]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** OCR confidence gating
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does a production ingestion pipeline need a confidence signal from its OCR step, rather than always ingesting whatever text OCR produced?

**OPTIONS:**
- [ ] A: OCR always fails completely or succeeds completely, so a confidence signal is unnecessary
- [x] B: OCR quality on real customer scans varies, and silently ingesting low-confidence, garbled text produces chunks that appear normal but embed and retrieve incorrectly, so low-confidence pages should be flagged for review instead
- [ ] C: Confidence signals are only useful for detecting duplicate documents
- [ ] D: OCR confidence has no relationship to retrieval quality

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Garbled OCR text still gets embedded and indexed like any other chunk, but its content is wrong, which is a silent failure mode; a confidence threshold routes suspect pages to human review instead of ingesting them as if they were clean.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [OCR, confidence-gating, review-queue]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why table flattening breaks retrieval
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A naive parser flattens a table into one run of plain text. Why does this specifically damage a query asking for "the Q3 number for the EMEA region"?

**OPTIONS:**
- [ ] A: Flattened tables cannot be embedded by any embedding model
- [x] B: Flattening destroys the row/column structure that connects "Q3" and "EMEA" to their specific intersecting value, so the information the query needs is no longer recoverable from the chunk
- [ ] C: This only affects keyword search, not vector search
- [ ] D: Flattened tables are always split into a separate chunk automatically

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
A table's meaning depends on which row and column a value belongs to; collapsing that structure into undifferentiated text loses exactly the relationship a structured query depends on, which is why table-aware parsing (e.g. preserving markdown table structure) matters.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [table-parsing, structure-preservation]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why full reindexing doesn't scale operationally
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a pipeline that only supports a full reindex becomes operationally unusable at real document counts?

**OPTIONS:**
- [ ] A: Vector databases have a hard limit on the total number of reindex operations they can ever perform
- [x] B: A full reindex re-parses, re-chunks, and re-embeds every document from scratch every time, which is slow, costs a billed embedding call per document regardless of whether it changed, and creates a window reflecting neither the old nor new state cleanly
- [ ] C: Full reindexing is only a problem for documents under 1,000 words
- [ ] D: Incremental and full reindexing produce identical index states, so the distinction doesn't matter operationally

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The cost is compounding: every document, changed or not, gets re-embedded on every full reindex, which is wasteful at scale and creates an inconsistent window during the rebuild — the exact problems incremental re-ingestion is designed to avoid.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [full-reindex, incremental-ingestion, operational-cost]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** The specific damage of stale citations
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson describe a RAG system confidently citing a superseded, uncorrected document version as worse than having no RAG system at all?

**OPTIONS:**
- [ ] A: A missing RAG system always produces more accurate answers than any RAG system
- [x] B: The stale citation looks authoritative and confident while being factually wrong, which is more damaging than an obvious absence of an answer, since the user has no signal to distrust it
- [ ] C: Stale citations only occur when the embedding model itself is outdated
- [ ] D: This problem cannot occur if chunking is done correctly

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The specific harm is epistemic: a wrong answer delivered with the same confident tone as a correct one gives the user no reason to question it, whereas no system at all at least doesn't create false confidence in stale information.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [stale-index, incremental-sync, trust]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why access control must be captured at ingestion
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist access-control metadata be attached to chunks at ingestion time rather than filtered in afterward at query time?

**OPTIONS:**
- [ ] A: Access control can always be enforced equally well regardless of when it's implemented
- [x] B: Retrieval-time filtering needs metadata to filter on; if ingestion never captured which documents or chunks a user is entitled to see, there is nothing for a later filtering step to check against
- [ ] C: Query-time filtering is technically impossible in any vector database
- [ ] D: Ingestion-time tagging removes the need for any retrieval-time enforcement at all

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Retrieval-time enforcement (the next lesson's topic) is only as good as the metadata it can filter on; without ingestion-time capture of real source-system permissions, the choice narrows to over-restricting or under-restricting, both of which are worse than correct filtering.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [access-control, ingestion-metadata]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Sourcing access-control tags correctly
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the manufacturing customer scenario, why does the pipeline pull the `role:hr` tag directly from SharePoint's own permission API rather than hardcoding it per document?

**OPTIONS:**
- [ ] A: SharePoint's permission API is required by law for all RAG systems
- [x] B: A hardcoded tag drifts out of sync the moment the source system's actual permissions change, while pulling from the real permission system keeps the tag accurate to the document's true current access rules
- [ ] C: Hardcoding tags is technically impossible in a production ingestion pipeline
- [ ] D: The tag only needs to be accurate at the moment of the very first ingestion

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Sourcing the tag from the actual permission system, rather than a hardcoded guess, means it stays correct as the source system's real access rules change over time, avoiding silent drift between the index's metadata and the truth.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [access-control, permission-sourcing]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What a change signal enables
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What role does a per-document change signal (a last-modified timestamp, content hash, or webhook) play in the ingestion pipeline described in this lesson?

**OPTIONS:**
- [ ] A: It determines which embedding model to use for a given document
- [x] B: It lets incremental re-ingestion identify exactly which documents actually changed, so only those are re-parsed, re-chunked, and re-embedded instead of the entire corpus
- [ ] C: It is only used to generate the access-control tag
- [ ] D: It replaces the need for OCR confidence checking

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The change signal is the mechanism that makes incremental sync possible at all — without a reliable way to detect which documents changed, the pipeline has no basis for skipping unchanged documents during a sync.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [change-signal, incremental-sync]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Handling document deletion in the index
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A source document is deleted from the customer's system entirely. What should a correctly designed incremental ingestion pipeline do?

**OPTIONS:**
- [ ] A: Leave the document's existing chunks in the index indefinitely, since deletion is rare
- [x] B: Detect the deletion and remove the document's chunks from the index, so they cannot still be retrieved and cited after the source no longer exists
- [ ] C: Mark the document's chunks as low-priority but keep them retrievable
- [ ] D: Wait until the next scheduled full reindex to remove the chunks

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
An orphaned chunk from a deleted source is a direct analog to the stale-citation problem — it can still surface in retrieval and be presented as current, so deletion needs to propagate into the index promptly, not wait for a full reindex cycle.

**LESSON_CONNECTION:** Practice Loop, Step 4
**KEYWORDS:** [document-deletion, orphaned-chunks]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 8

```yaml
lesson_id: fde-enterprise-consulting-llm-08-rag-over-customer-documents-and-hybrid-search
lesson_title: "RAG over Customer Documents & Hybrid Search"
lesson_order: 8

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Enforce document-level and chunk-level access control at query time using the metadata captured during ingestion, without leaking a restricted chunk into a response."
  - "Stand up hybrid search in a real customer's infrastructure (a combined dense-vector and sparse-keyword index) and tune the merge between the two result sets."
  - "Rewrite a query for a customer's specific internal jargon and abbreviations before retrieval, rather than relying on the base embedding model to handle domain vocabulary unaided."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# RAG over Customer Documents & Hybrid Search

## Concepts Covered

The previous lesson tagged chunks with access-control metadata at ingestion time; this lesson is where that metadata actually gets enforced. Retrieval-time access control is a pre-filter, not a post-filter: the correct pattern narrows the candidate set to only chunks the requesting user is authorized to see before similarity ranking runs, using the requesting user's role or identity passed into the retrieval call alongside the query itself. A vector database that supports metadata filtering (most production ones do — a `WHERE`-style clause alongside the similarity search) applies this filter as part of the same query, not as a separate step afterward. Filtering after ranking is the mistake to specifically avoid: if the system first retrieves its top-k chunks by similarity and only then discards the ones the user isn't authorized to see, a query can return fewer than k relevant results (or none) whenever the truly best matches happen to be restricted, silently degrading the answer's quality for no reason visible to the user — and worse, if the discard step is implemented anywhere downstream of the model actually seeing the chunk (for instance, filtering only what's shown in a citation UI while the restricted chunk was already in the prompt), the access-control boundary is not actually enforced at all, since the model already read the restricted content.

Hybrid search, introduced conceptually in the prerequisite RAG lesson as combining dense vector similarity with sparse keyword matching, becomes a real infrastructure decision once it has to run against a specific customer's stack. The two common production shapes are a single system that supports both natively (OpenSearch or Elasticsearch with a dense-vector field alongside its native BM25 text search, or Postgres with `pgvector` alongside its built-in `tsvector` full-text search) and two separate systems queried in parallel with results merged in application code. The native-combination approach is operationally simpler — one system, one index to keep in sync — and is the default choice unless the customer's existing infrastructure already has a strong preference (a customer already running Elasticsearch for other search needs is a real reason to extend it rather than stand up a second vector store). Merging the two result sets is its own tuning problem: reciprocal rank fusion (combining each result set's rank position, not its raw score, into a single blended ranking) is the common default because dense-similarity scores and BM25 scores live on different, non-comparable scales, and naively averaging raw scores from two different scoring systems produces a merge that's dominated by whichever system happens to produce larger numbers, not whichever system found the more relevant result.

Query rewriting is the third production lever, and it matters more in a real customer deployment than in a general-purpose RAG system because customer documents are full of internal jargon, product codenames, and abbreviations the base embedding model was never trained to associate with their meaning. A query like "what's our current PTO carryover policy for L4s" only retrieves correctly if the index and the query both use the same vocabulary for "L4" (an internal leveling term) — if the source documents spell it out as "Level 4 Individual Contributor" and the query uses only the abbreviation, dense similarity alone may miss the connection entirely even though hybrid search's keyword component would also miss it for the same reason (the exact string doesn't appear in either form in both places). A query-rewriting step — expanding known abbreviations, normalizing product codenames to their documented names, or using a cheap LLM call to reformulate the query using the customer's own glossary before it hits the retrieval layer — closes this gap, and building a small glossary of the customer's actual internal terms during discovery (the same discovery-call skill from earlier in this module) is what makes the rewriting step's mappings accurate rather than guessed.

## Practical Backend Scenario

The manufacturing customer's RAG system from the previous lesson serves both engineering staff and HR staff through the same chat interface. An engineer asks "what's the torque spec for the M12 assembly, and what's HR's policy on remote inspection travel?" — a compound query touching both an engineering-standards document (unrestricted) and an HR travel policy document (`role:hr`-tagged, and this user is not in HR). The retrieval layer applies the user's role as a pre-filter before similarity ranking runs, so the HR-restricted chunk is excluded from the candidate set entirely — the model never sees it, and the response correctly answers the torque question while stating the travel-policy question needs to go through HR, rather than fabricating an answer from a chunk it should never have retrieved. Separately, the engineering-standards documents refer to "M12" fasteners throughout, but a batch of newer test queries use the plant floor's spoken shorthand "twelve-mil," which the base embedding model doesn't reliably associate with "M12" — a query-rewriting step that expands "twelve-mil" to "M12" using a small glossary built during the original discovery conversations with the plant's engineering lead fixes retrieval for this term without touching the underlying documents or embedding model.

## Practice Loop

1. Take the tagged chunks from the previous lesson's practice loop and implement a retrieval query that applies the access-control tag as a pre-filter (narrowing the candidate set before ranking), not a post-filter (discarding after ranking) — write a test that proves a restricted chunk never appears in results for an unauthorized user, even when it would otherwise be the top match.
2. Stand up a hybrid search query against your indexed chunks combining dense similarity and keyword/BM25 matching, using whichever native-combination or dual-system approach matches what you have access to.
3. Construct one query where dense-only retrieval and hybrid retrieval return different top results, and measure which one is actually more relevant — this diagnostic step shows concretely what hybrid search is buying you over dense-only for at least one real query.
4. Build a small glossary of 5-10 domain-specific terms or abbreviations for your test documents and write a query-rewriting step that expands them before retrieval; construct one query using only the shorthand form and confirm retrieval improves after rewriting versus before.
5. Combine steps 1 and 4 into a single retrieval call — access-control pre-filtering plus query rewriting plus hybrid search — and verify all three behave correctly together on one compound test query that touches both a restricted and an unrestricted document.

## Evidence of Understanding

You can implement retrieval-time access control as a pre-filter applied before similarity ranking, and explain precisely why filtering after ranking (or filtering only at the UI/citation layer) fails to actually enforce the access boundary. You can stand up hybrid search against a real infrastructure choice (a natively-combined system or a dual-system merge), and explain why reciprocal rank fusion is the standard default merge strategy over naively averaging raw scores from two non-comparable scoring systems. You can build and apply a query-rewriting step using a customer-specific glossary, and explain why a customer's internal jargon is a retrieval failure mode that neither dense similarity nor keyword matching alone reliably solves.

## Suggested Extension

Extend the access-control pre-filter to chunk-level rather than document-level granularity — a single document that mixes a restricted section (e.g. a salary table) with unrestricted general content — and design how the ingestion pipeline from the previous lesson would need to tag chunks differently within the same source document to make chunk-level filtering possible.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Pre-filter vs. post-filter access control
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson insist access control be applied as a pre-filter (narrowing candidates before similarity ranking) rather than a post-filter (discarding restricted results after ranking)?

**OPTIONS:**
- [ ] A: Pre-filtering and post-filtering always produce identical result sets, so the choice is only a performance concern
- [x] B: A post-filter can silently return fewer than the intended number of results (or none) whenever the best matches happen to be restricted, and if any downstream step already exposed the restricted chunk to the model before discarding it, the access boundary was never actually enforced
- [ ] C: Post-filtering is faster than pre-filtering in every vector database implementation
- [ ] D: Pre-filtering is only possible when using keyword search, not vector search

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Pre-filtering narrows the authorized candidate set before ranking, so the top-k results are drawn only from what the user can see; post-filtering risks both degraded results and, if the model already saw the restricted content before discard, a genuine access-control failure rather than a display-layer inconvenience.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [access-control, pre-filter, post-filter]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why filtering at the citation UI doesn't enforce the boundary
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A system retrieves a restricted chunk, includes it in the prompt sent to the model, but only hides it from the citation list shown to the unauthorized user in the UI. Why does the lesson say this does not actually enforce access control?

**OPTIONS:**
- [ ] A: Citation UIs are always displayed to every user regardless of permissions
- [x] B: The model already read the restricted chunk's content when generating its answer, so the restricted information can leak into the response text itself even if the citation UI hides the source — the boundary was never enforced upstream
- [ ] C: This approach is equivalent in effect to a correctly implemented pre-filter
- [ ] D: Hiding a citation always prevents the underlying information from influencing the answer

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Enforcement has to happen before the model sees the content, not after, at display time — once a restricted chunk is in the prompt, the model can reflect its content in the answer regardless of what the citation UI later chooses to show or hide.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [access-control, enforcement-point]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Native combination vs. dual-system hybrid search
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, when should an FDE prefer a dual-system hybrid search approach (two separate systems merged in application code) over a single system with native dense-plus-keyword support?

**OPTIONS:**
- [ ] A: Always — dual-system approaches are strictly superior in every deployment
- [x] B: When the customer's existing infrastructure already has a strong preference, such as an existing investment in a search system that can be extended, rather than defaulting to a second, separate vector store
- [ ] C: Never — dual-system hybrid search is never a valid production choice
- [ ] D: Only when the customer's document set is smaller than 100 documents

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson frames native combination as operationally simpler and the default, with the customer's existing infrastructure being the concrete reason to deviate — for example, extending an already-running Elasticsearch deployment rather than adding an entirely separate system.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [hybrid-search-infrastructure, native-combination]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why reciprocal rank fusion over averaging raw scores
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend reciprocal rank fusion (combining rank position) over naively averaging the raw similarity and BM25 scores when merging hybrid search results?

**OPTIONS:**
- [ ] A: Rank position is always a more accurate signal of relevance than a similarity score in isolation
- [x] B: Dense-similarity scores and BM25 scores live on different, non-comparable scales, so averaging raw scores produces a merge dominated by whichever scoring system happens to produce larger numbers rather than whichever result is actually more relevant
- [ ] C: Reciprocal rank fusion eliminates the need for any access-control filtering
- [ ] D: BM25 scores and vector similarity scores are always on an identical numeric scale

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Because the two scoring systems aren't on a comparable scale, blending by rank position rather than raw value avoids letting one system's arbitrary numeric range silently dominate the merged ranking.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [reciprocal-rank-fusion, result-merging]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why jargon defeats both dense and keyword search
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
A query uses the abbreviation "L4," but source documents spell out "Level 4 Individual Contributor" and never use "L4." Why does the lesson say hybrid search alone does not reliably fix this?

**OPTIONS:**
- [ ] A: Hybrid search only functions correctly on numeric queries
- [x] B: Neither the dense embedding nor the keyword/BM25 component can match "L4" against "Level 4 Individual Contributor" without an explicit mapping, since the exact term doesn't appear in both forms in both places — the gap is a vocabulary mismatch, not a retrieval-method limitation
- [ ] C: BM25 always outperforms dense retrieval on abbreviations by default
- [ ] D: This problem only occurs with single-word queries

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Hybrid search combines two retrieval methods, but both still depend on some form of lexical or semantic overlap between query and document; an undocumented internal abbreviation defeats both unless something (query rewriting) bridges the vocabulary gap first.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [query-rewriting, jargon, vocabulary-mismatch]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Where a customer glossary comes from
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The lesson connects building an accurate query-rewriting glossary back to a skill from earlier in this module. Which skill, and why does it matter for the glossary's accuracy?

**OPTIONS:**
- [ ] A: Demo storytelling skills, because the glossary is presented to the customer as part of the final demo
- [x] B: Discovery-call skills — the glossary's term mappings need to be accurate to the customer's real internal vocabulary, and that vocabulary surfaces through the same structured discovery conversations used to gather requirements, not through guessing
- [ ] C: Status-update writing skills, because the glossary is documented in a weekly status email
- [ ] D: Risk register skills, because each glossary term is treated as a named risk

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
An accurate glossary depends on correctly capturing how the customer's own staff actually talk about their work — exactly the kind of vocabulary that surfaces during a well-run discovery conversation, not something an FDE can accurately guess from outside.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [query-rewriting, discovery, glossary]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the compound query in the scenario answered correctly
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, the engineer's compound question about torque spec and HR travel policy was answered correctly for one part and appropriately declined for the other. What specifically made this possible?

**OPTIONS:**
- [ ] A: The model was trained specifically on this customer's HR policies
- [x] B: The access-control pre-filter excluded the HR-restricted chunk from the candidate set before the model ever saw it, so the model could only draw on the unrestricted engineering chunk for its answer
- [ ] C: The query-rewriting step detected the question was compound and split it automatically
- [ ] D: Hybrid search naturally excludes any HR-related content from all queries

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Because the pre-filter removed the HR chunk from the candidate set before ranking, the model had no restricted content in its context at all, which is why it could answer the engineering part correctly and correctly decline the HR part rather than fabricating from content it never received.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [access-control, compound-query]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Fixing "twelve-mil" without touching source documents
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, plant-floor staff use "twelve-mil" as shorthand for "M12," which the embedding model doesn't reliably associate with the documented term. What fixes this without re-writing the source documents or the embedding model?

**OPTIONS:**
- [ ] A: Re-embedding every document with a larger embedding model
- [x] B: A query-rewriting step that expands "twelve-mil" to "M12" using a glossary built from real plant-floor vocabulary, applied before the query reaches retrieval
- [ ] C: Switching from hybrid search to dense-only search
- [ ] D: Increasing the number of chunks retrieved per query

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Query rewriting closes the vocabulary gap at query time, which is cheaper and more targeted than re-embedding an entire document set, and it fixes the specific term mismatch rather than a general retrieval-quality lever like model size or chunk count.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [query-rewriting, glossary]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Chunk-level vs. document-level access control
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why might document-level access-control tagging be insufficient for a single document that mixes a restricted section (e.g. a salary table) with unrestricted general content?

**OPTIONS:**
- [ ] A: Document-level tagging always correctly protects every section of a mixed document
- [x] B: Tagging the whole document as restricted excludes unrestricted content unnecessarily, while tagging it as unrestricted exposes the restricted section — only chunk-level tagging (applied per section during ingestion) allows the unrestricted parts to remain retrievable while the restricted section stays protected
- [ ] C: Chunk-level tagging is never necessary once hybrid search is in place
- [ ] D: This problem is specific to scanned PDFs and doesn't apply to other formats

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
A single access-control tag applied to an entire mixed document forces an all-or-nothing choice that either over-restricts or under-restricts; chunk-level tagging at ingestion (the previous lesson's mechanism) is what makes fine-grained enforcement possible.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [chunk-level-access-control, granularity]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 9

```yaml
lesson_id: fde-enterprise-consulting-llm-09-rag-evaluation-and-iteration-ragas
lesson_title: "RAG Evaluation & Iteration (RAGAS)"
lesson_order: 9

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Build a real RAGAS-scored eval dataset from a customer's own subject-matter experts rather than from questions an FDE invented alone."
  - "Wire RAGAS scoring into a CI gate that blocks an ingestion or retrieval change from shipping if it regresses any of the four metrics below an agreed threshold."
  - "Run RAGAS as an ongoing production practice against sampled live queries, not a one-time pre-launch check, and route a metric-specific regression to the correct fix."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# RAG Evaluation & Iteration (RAGAS)

## Concepts Covered

The prerequisite RAG lesson taught what RAGAS's four metrics measure and how to attribute a wrong answer to retrieval or generation. This lesson is about running RAGAS as an ongoing operational practice against a real customer deployment, and the first production reality is that a RAGAS score is only as good as the eval dataset it's computed against. An FDE writing test questions alone, without customer input, tends to produce questions that are easier and more evenly distributed across topics than what real users actually ask — real query logs cluster heavily around a handful of high-frequency intents and contain phrasing an FDE would never think to write. A real eval dataset is built with the customer's subject-matter experts: pull a sample of representative questions from actual usage where possible (or, pre-launch, from the SMEs who will use the system daily), have those SMEs write or verify the "gold" expected answer and identify which source chunks should be considered ground-truth-relevant for context precision and recall scoring, and keep the dataset versioned so a later question about "did retrieval get better or worse since last month" has a stable, unchanging yardstick to compare against — a moving eval set makes month-over-month comparison meaningless, because you can't tell if a score change came from the system or from a different set of questions.

The second operational shift is treating RAGAS as a CI gate, not a one-time report generated before launch and then forgotten. Every change that can affect retrieval or generation quality — a chunking strategy tweak, a prompt edit, a reranking model swap, an embedding model upgrade — should run the full eval dataset through RAGAS scoring before merging, with an agreed threshold per metric (not necessarily a single overall pass/fail number) that blocks the change if any metric regresses past it. This mirrors the golden-test-set eval-gate discipline from the prompt-engineering-for-production-systems lesson earlier in this module, applied here to the retrieval and ingestion layers specifically rather than to prompt wording alone — a chunking change that quietly drops context recall from 0.91 to 0.74 is exactly the kind of regression that's invisible without an automated score comparison and easy to miss by eyeballing a handful of example answers, which is why the gate has to be automated and run on every relevant change, not run manually when someone remembers to.

The third operational shift is running RAGAS continuously against sampled production traffic, not just against the static eval dataset. A held-out eval set proves the system worked well on the questions it was tested against at build time; it says nothing about drift after launch — a document set that grows, a customer's vocabulary shifting, or a vendor model update (the same model-versioning reality from the LLM-fundamentals lesson) can degrade real-world performance in ways the static eval set never surfaces because it never changes. Sampling a percentage of live production queries, scoring them with RAGAS on an ongoing basis (using a smaller, automated LLM-as-judge for the sampled scoring, since full human review of every live query doesn't scale), and routing any metric that trends downward back to the correct fix — chunking or hybrid search for a context precision or recall dip, prompt or model-version review for a faithfulness or relevancy dip — turns evaluation from a launch gate into a genuine operating practice, and it is what actually lets an FDE tell a customer, months after handoff, whether the system they're operating is still performing the way it did on day one.

## Practical Backend Scenario

Three months after the manufacturing customer's RAG system launched, the plant's engineering lead reports that answers "feel less reliable" but can't point to a specific wrong answer. The FDE's monthly RAGAS run against the versioned 40-question eval dataset (built originally with the same engineering lead and an HR representative, each verifying gold answers and ground-truth chunks for their own domain) shows context recall has dropped from 0.89 to 0.71 over the quarter, while faithfulness and answer relevancy are unchanged — narrowing the fault to retrieval, not generation, exactly as the RAGAS-attribution skill from the prerequisite lesson would predict. Investigating further, the engineering-standards document set has nearly doubled in size since launch as new equipment documentation was added, and the original chunking configuration, tuned for the smaller initial document set, is now retrieving less precisely against the larger, more topically diverse index — a chunking parameter that needs revisiting isn't a one-time launch decision, it's something document-set growth can silently invalidate. The fix — re-tuning chunk size and re-running the eval dataset to confirm recall recovers — gets validated against the same stable eval set before shipping, so the FDE can tell the customer with actual evidence, not a guess, exactly what degraded and why.

## Practice Loop

1. Working with a domain expert (a colleague, or someone who genuinely knows the source material well, standing in for a customer SME), build a 15-20 question eval dataset from your RAG system's practice loop from lesson 7-8: have them write or verify the expected answer and identify the ground-truth relevant chunks for each question, not just write questions alone.
2. Version this dataset (a simple file with a version tag is enough) and run the full RAGAS scoring against your current system, recording all four metric scores as your baseline.
3. Deliberately make one change likely to affect retrieval quality (a chunk-size change, or adding several new, topically similar documents to your index without re-tuning), then re-run the same versioned eval dataset and compare scores against your baseline — this diagnostic step should surface a measurable score change, showing exactly which metric moved.
4. For whichever metric moved, apply the RAGAS-attribution skill from the prerequisite lesson to identify whether the fix belongs in retrieval (chunking, hybrid search, reranking) or generation (prompt, model version), and make that fix.
5. Re-run the eval dataset a final time to confirm the fix actually recovered the regressed metric without degrading any of the other three, and write a one-paragraph summary of what changed, what metric it affected, and what evidence confirms the fix worked.

## Evidence of Understanding

You can build a RAGAS eval dataset with a domain expert's verified gold answers and ground-truth relevant chunks, and explain why a dataset an FDE writes alone tends to be easier and less representative than real usage. You can wire RAGAS scoring into a CI-style gate with per-metric thresholds that blocks a retrieval- or generation-affecting change from shipping on regression, and explain why this needs automation rather than manual spot-checking. You can run RAGAS continuously against sampled production traffic to detect drift a static pre-launch eval set cannot surface, and route a metric-specific regression to the correct fix using the retrieval-versus-generation attribution skill from the prerequisite RAG lesson.

## Suggested Extension

Design an alerting rule for the continuous production RAGAS practice — a specific threshold and time window (e.g. "context recall drops more than 10 points over any rolling 30-day window") that would page an FDE or open a ticket automatically, rather than relying on a customer noticing and reporting a vague feeling that "answers seem less reliable" months later.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why an FDE-only eval dataset is a risk
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say an eval dataset an FDE writes entirely alone, without customer SME input, tends to be a weaker signal of real-world quality?

**OPTIONS:**
- [ ] A: RAGAS cannot score any dataset the FDE writes without customer sign-off
- [x] B: It tends to be easier and more evenly distributed across topics than real usage, which clusters around high-frequency intents and phrasing an FDE would not think to write
- [ ] C: FDE-written questions are always factually incorrect
- [ ] D: Eval datasets must contain at least 1,000 questions to be valid

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The specific risk is representativeness, not validity — an FDE alone tends to write questions that don't reflect the actual distribution and phrasing of real user queries, which real SME input or real usage logs correct for.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [eval-dataset, SME-involvement]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why the eval dataset needs to be versioned
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a moving (unversioned, frequently-changed) eval dataset makes month-over-month RAGAS score comparison meaningless?

**OPTIONS:**
- [ ] A: RAGAS scores are only valid for exactly 30 days after computation
- [x] B: If the questions being scored change between two measurements, you cannot tell whether a score difference came from a real system change or simply from scoring a different set of questions
- [ ] C: Versioned datasets always produce higher scores than unversioned ones
- [ ] D: RAGAS requires a minimum dataset size that only versioned datasets can guarantee

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
A stable yardstick is what makes a score comparison meaningful — if the eval set itself changes, a score movement could reflect the new question mix rather than any real change in system quality.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [eval-dataset-versioning, comparability]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** RAGAS as a CI gate
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Which changes does the lesson say should trigger a full RAGAS eval-gate run before merging?

**OPTIONS:**
- [ ] A: Only changes to the customer-facing UI, since backend changes cannot affect RAGAS scores
- [x] B: Any change that can affect retrieval or generation quality — chunking strategy, prompt edits, reranking model swaps, or embedding model upgrades
- [ ] C: Only changes explicitly labeled "RAG update" in the commit message
- [ ] D: Changes are never gated; RAGAS is run only once, before initial launch

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names a broad set of change types spanning both retrieval and generation layers as gate triggers — the common thread is anything that could plausibly move a RAGAS metric, not a narrow or manually-flagged subset.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [CI-gate, eval-gate, RAGAS]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Why per-metric thresholds instead of one overall score
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend an agreed threshold per individual RAGAS metric, rather than a single blended overall pass/fail score?

**OPTIONS:**
- [ ] A: RAGAS technically cannot compute a blended overall score under any circumstances
- [x] B: A single blended score can mask a serious regression in one metric (e.g. context recall dropping sharply) if the other three metrics stay strong enough to keep the average acceptable, hiding exactly the kind of stage-specific problem RAGAS is meant to surface
- [ ] C: Per-metric thresholds are only relevant for very large document sets
- [ ] D: A blended score is always identical to the lowest of the four individual metrics

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Per-metric thresholds preserve exactly the diagnostic value that motivated scoring the four metrics separately in the first place — a blended average can hide a real regression in one dimension behind strength in the others.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [per-metric-threshold, blended-score]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why a static eval set can't detect drift
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a held-out, static eval set that proved good scores at launch cannot be relied on to detect drift months later?

**OPTIONS:**
- [ ] A: Static eval sets automatically expire after 90 days
- [x] B: A static eval set never changes, so it cannot reveal degradation caused by a growing document set, shifting customer vocabulary, or a vendor-side model update — all of which affect real production traffic without ever being reflected in the unchanging eval set's scores
- [ ] C: RAGAS cannot be run more than once against the same eval set
- [ ] D: A static eval set always produces a perfect score by definition

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The eval set is fixed, but the production system's real inputs are not — document growth, vocabulary shift, and model updates all change real-world performance in ways a set of unchanging test questions was never positioned to catch.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [production-drift, static-eval-limitation]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why sampled LLM-as-judge scoring, not full human review
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend a smaller, automated LLM-as-judge for continuously scoring sampled production traffic, rather than full human review of every live query?

**OPTIONS:**
- [ ] A: LLM-as-judge scoring is always more accurate than human review
- [x] B: Full human review of every live query does not scale, so an automated judge scoring a representative sample is the practical way to maintain an ongoing signal without reviewing every single production query by hand
- [ ] C: Human review is prohibited by RAGAS's methodology
- [ ] D: Automated judges are required to also perform the ingestion pipeline's OCR confidence checks

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The practical constraint is scale — continuous, ongoing scoring of a meaningful sample of production traffic is only sustainable with automation, since human review of every query is not operationally viable at real volume.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [continuous-evaluation, LLM-as-judge, scale]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Diagnosing the scenario's recall drop
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, context recall dropped from 0.89 to 0.71 while faithfulness and answer relevancy stayed unchanged. What does this specifically tell the FDE about where to look for a fix?

**OPTIONS:**
- [ ] A: The fault is in the generation stage, so the prompt needs revision
- [x] B: The fault is in the retrieval stage, since context recall is a retrieval-stage metric and the unchanged generation-stage metrics (faithfulness, relevancy) rule out a generation-side cause
- [ ] C: The eval dataset itself must be corrupted, since a single metric moving alone is not possible
- [ ] D: The fix must be a full model version upgrade, regardless of what changed in retrieval

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is a direct application of the prerequisite lesson's stage attribution: context recall belongs to retrieval, and its isolated movement (with generation-stage metrics stable) narrows the investigation to retrieval-side causes like chunking or index composition.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [RAGAS-attribution, context-recall]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why document-set growth can silently invalidate chunking
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the manufacturing customer's chunking configuration, which performed well at launch, degrade retrieval quality after the document set nearly doubled?

**OPTIONS:**
- [ ] A: RAGAS scores always decline naturally over time regardless of any system change
- [x] B: A chunking configuration tuned against a smaller, less topically diverse document set can retrieve less precisely once the index grows larger and more varied, since chunking is not a one-time launch decision but a parameter that document-set changes can invalidate over time
- [ ] C: Adding new documents to an index always corrupts existing chunks
- [ ] D: The embedding model automatically degrades as index size increases

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson frames chunking as something that can be silently invalidated by real-world change (document-set growth) rather than a decision made once and forgotten — this is precisely the kind of drift the continuous evaluation practice is designed to catch.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [chunking-drift, document-set-growth]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why alerting matters over waiting for customer reports
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson's Suggested Extension propose an automated alerting rule (e.g. a recall drop past a threshold within a rolling window) rather than relying on a customer to report that "answers feel less reliable"?

**OPTIONS:**
- [ ] A: Customer reports are always more precise than any automated metric
- [x] B: A vague customer report gives no specific signal of what changed or when, while an automated threshold on a tracked metric surfaces the exact regression proactively, before it accumulates into a customer-visible trust problem
- [ ] C: Automated alerting removes the need for a versioned eval dataset
- [ ] D: Customers are contractually prohibited from reporting quality issues directly

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The whole value of continuous RAGAS monitoring is catching a specific, measurable regression before it becomes a vague, hard-to-diagnose customer complaint — an alerting rule operationalizes that early-detection goal.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [alerting, proactive-monitoring]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 10

```yaml
lesson_id: fde-enterprise-consulting-llm-10-llm-safety-guardrails-and-security
lesson_title: "LLM Safety, Guardrails & Security"
lesson_order: 10

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Design a layered guardrail pipeline (pre-call and post-call classifiers) for a customer deployment, distinct from the per-prompt red-teaming practice covered earlier in this module."
  - "Choose between a managed content-moderation or PII-detection service and a self-hosted guardrail classifier based on a customer's latency, cost, and data-residency constraints."
  - "Design an incident-response process and audit log for a guardrail violation that a customer's compliance or security team can actually operate after handoff."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# LLM Safety, Guardrails & Security

## Concepts Covered

The prompt-engineering lesson earlier in this module established red-teaming as a per-prompt practice: writing adversarial test cases targeting one specific prompt's attack surface and gating merges on them passing. That practice catches injection attempts you thought to test for, at the moment a prompt changes. A production customer deployment needs a second, independent layer that runs continuously against live traffic, catching what red-teaming didn't anticipate and what changes in customer usage surface over time — this is what a guardrail pipeline is for, and it operates at a different point in the request lifecycle than red-teaming's build-time testing. A guardrail pipeline has two natural points of insertion: pre-call guardrails inspect the incoming user input before it reaches the model at all (detecting an injection attempt, a request for content clearly outside the feature's intended scope, or input containing PII that shouldn't be sent to a third-party model API in the first place), and post-call guardrails inspect the model's output before it reaches the user or executes a tool call (catching a harmful, off-policy, or PII-leaking response the pre-call layer didn't block, or validating that a tool-call's parameters match policy before execution — directly extending the deterministic output-validation layer from the advanced-prompting-and-safety lesson). Neither layer alone is sufficient: pre-call guardrails can't catch a response that goes wrong for reasons unrelated to the input (a model hallucinating a policy that doesn't exist), and post-call guardrails alone let a clearly malicious input reach the model before catching only its output.

The build-versus-buy decision for guardrail tooling is a real architectural choice with customer-specific trade-offs, not a default. Managed content-moderation and PII-detection APIs (from major cloud providers or dedicated vendors) are fast to integrate, maintained and updated by the vendor as new attack patterns emerge, and usually the right default — but every request routed through a managed service adds a network hop (a latency cost that compounds at the volume this module's cost-and-latency lesson quantifies) and, more importantly for many enterprise customers, means customer data leaves the customer's own infrastructure boundary to reach a third-party classifier, which can directly violate a data-residency or compliance constraint surfaced during the original discovery call. A self-hosted guardrail — a smaller, purpose-built classifier model or a deterministic rule-and-regex layer running inside the customer's own infrastructure — avoids that data-boundary problem entirely and can be faster, at the cost of the FDE's team now owning its maintenance and its accuracy against new attack patterns. The right choice is the same discovery-driven judgment call the module's early lessons taught for any technical decision: read back the customer's actual data-residency and compliance constraints from the discovery brief, and let those constraints — not a default preference for either approach — decide.

The final production reality is that a guardrail catching something is not the end of the story; it needs to become an operable incident, not a silent block. A guardrail violation — a blocked injection attempt, a PII leak caught and redacted, a policy-violating output suppressed — should generate a structured, timestamped audit log entry (what was blocked, which layer caught it, the anonymized or redacted input/output, the policy rule that triggered) that flows into the same observability stack the LLM-fundamentals lesson established for ordinary operational monitoring, not a separate system nobody watches. This is what actually lets a customer's own security or compliance team operate the guardrail layer after handoff — the FDE-role "enable" step applied specifically to safety tooling — because a guardrail that silently blocks requests with no visible trail gives the customer's team nothing to investigate, audit for a compliance review, or use to tune the guardrail's own false-positive rate over time.

## Practical Backend Scenario

A healthcare-adjacent customer's support-ticket triage agent (the same tool-using-agent shape from the advanced-prompting-and-safety lesson's `issue_refund` example, here handling patient-scheduling requests instead) needs a guardrail layer beyond that lesson's mechanistic defenses and beyond this module's per-prompt red-teaming, because the customer's compliance team requires an auditable record of every blocked attempt for their own regulatory reporting. The FDE designs a pre-call guardrail that screens incoming ticket text for PII patterns (a patient ID or date-of-birth pattern appearing somewhere it shouldn't) before the ticket ever reaches the model API, and a post-call guardrail that validates the agent's proposed scheduling action against a deterministic policy check before it executes — extending, not replacing, the output-validation layer already built. Because the customer's compliance constraint (surfaced during the original discovery call) prohibits any patient data leaving their own infrastructure boundary, the FDE chooses a self-hosted regex-and-small-classifier pre-call layer over a managed PII-detection API, accepting the added maintenance burden in exchange for meeting the data-residency requirement. Every guardrail trigger — pre-call or post-call — writes a structured log entry into the customer's existing SIEM system rather than a separate tool only the FDE's team can see, so the compliance team can pull a monthly report of every blocked attempt without asking the FDE to run a query for them.

## Practice Loop

1. Design a pre-call guardrail check for one specific risk relevant to your practice-loop agent from an earlier lesson in this module (a PII pattern, an out-of-scope request category, or a known injection phrase) and write a test input that should trigger it.
2. Design a post-call guardrail check that validates a tool call's parameters against a deterministic policy before execution, extending (not duplicating) any output-validation logic you built in the advanced-prompting-and-safety lesson's practice loop.
3. For your two guardrail checks, write down which one would need to change first if the customer's traffic pattern shifted to include a new kind of request you hadn't anticipated — this diagnostic step distinguishes checks that generalize from checks tightly coupled to one specific attack pattern.
4. Make the build-versus-buy decision explicit: write one sentence for each guardrail check stating whether you'd use a managed service or a self-hosted classifier, and name the specific customer constraint (data residency, latency budget, or maintenance capacity) driving that choice.
5. Design the structured audit log entry your guardrail pipeline would write on a trigger (timestamp, layer, redacted input/output, policy rule) and specify which existing observability or compliance system it should flow into, rather than a standalone log only you can see.

## Evidence of Understanding

You can design a two-layer guardrail pipeline (pre-call input screening, post-call output and tool-call validation) and explain how it differs in purpose and timing from the per-prompt red-teaming practice covered earlier in this module. You can make and justify a build-versus-buy decision between a managed moderation/PII service and a self-hosted classifier using a customer's actual data-residency, latency, and maintenance constraints rather than a default preference. You can design a structured, auditable incident record for a guardrail trigger that flows into a customer's own observability or compliance tooling, and explain why a silent block is not sufficient for a customer's security team to operate the system after handoff.

## Suggested Extension

Design a monthly false-positive review process for the pre-call PII guardrail from the practice loop — a way for the customer's compliance team to sample and review a portion of triggered blocks, flag any that were incorrectly triggered, and feed that feedback back into tuning the guardrail's threshold, closing the loop between the audit log and the guardrail's own accuracy over time.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** How a guardrail pipeline differs from red-teaming
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does a production guardrail pipeline differ in purpose and timing from the per-prompt red-teaming practice covered earlier in this module?

**OPTIONS:**
- [ ] A: A guardrail pipeline replaces red-teaming entirely, making the earlier practice unnecessary
- [x] B: Red-teaming is a build-time test against attacks the FDE anticipated for one specific prompt; a guardrail pipeline runs continuously against live traffic, catching attacks the red-team set didn't anticipate and shifts in real usage over time
- [ ] C: Guardrail pipelines only run once, at deployment time, identical to red-teaming's timing
- [ ] D: Red-teaming and guardrail pipelines both operate exclusively on model output, never on input

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Red-teaming is a build-time, prompt-specific gate; a guardrail pipeline is a continuously running production layer, which is why the two are complementary rather than redundant — one catches what you anticipated, the other catches what you didn't.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [guardrail-pipeline, red-teaming, build-vs-runtime]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Why neither guardrail layer alone is sufficient
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say pre-call and post-call guardrails are both needed, rather than either one alone being sufficient?

**OPTIONS:**
- [ ] A: Pre-call and post-call guardrails always catch exactly the same set of problems, so using both is only redundancy for safety margin
- [x] B: Pre-call guardrails can't catch a response that goes wrong for reasons unrelated to the input (e.g. a hallucinated policy), and post-call guardrails alone let a clearly malicious input reach the model before anything is checked
- [ ] C: Post-call guardrails are always sufficient on their own, and pre-call guardrails exist only for legacy compatibility
- [ ] D: Pre-call guardrails are sufficient on their own once red-teaming has been done for a prompt

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The two layers catch different failure classes — input-side risks a pre-call check can screen for, and output-side risks (including ones with no problematic input at all) only a post-call check can catch — so both are needed to cover the full risk surface.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [pre-call-guardrail, post-call-guardrail]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** How post-call guardrails extend prior output validation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How does this lesson's post-call tool-call validation relate to the deterministic output-validation layer from the advanced-prompting-and-safety lesson?

**OPTIONS:**
- [ ] A: It replaces the earlier output-validation layer entirely, making it obsolete
- [x] B: It directly extends that same deterministic validation layer — checking a tool call's parameters against policy before execution — now framed as one component of a broader, continuously-running guardrail pipeline rather than a single standalone check
- [ ] C: It applies only to text responses and has no relationship to tool-call validation
- [ ] D: It is unrelated to the earlier lesson's output-validation concept

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly frames post-call guardrails as extending, not duplicating or replacing, the earlier deterministic output-validation mechanism — placing that same check inside a broader, continuously operating pipeline.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [output-validation, post-call-guardrail]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** The real cost of a managed guardrail service
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Beyond added latency, what is the more significant concern the lesson names for routing guardrail checks through a managed third-party content-moderation or PII-detection API?

**OPTIONS:**
- [ ] A: Managed services are always less accurate than self-hosted classifiers
- [x] B: Customer data leaves the customer's own infrastructure boundary to reach the third-party classifier, which can directly violate a data-residency or compliance constraint surfaced during discovery
- [ ] C: Managed services cannot be integrated with any existing observability stack
- [ ] D: Managed services require the customer to migrate their entire infrastructure to the vendor's cloud

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
For many enterprise customers, the data-boundary crossing itself — not just latency — is the disqualifying concern, since it can conflict with a compliance or data-residency constraint already captured during discovery.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [managed-service, data-residency, build-vs-buy]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** What should decide the build-versus-buy choice
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what should actually determine whether an FDE chooses a managed guardrail service or a self-hosted classifier for a given customer?

**OPTIONS:**
- [ ] A: A fixed company-wide default that applies identically to every customer engagement
- [x] B: The customer's actual data-residency, latency, and maintenance-capacity constraints as surfaced during discovery, not a default preference for either approach
- [ ] C: Whichever option the FDE personally has more experience implementing
- [ ] D: Whichever option is cheaper per API call in isolation, regardless of other constraints

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson explicitly frames this as the same discovery-driven judgment call taught earlier in the module — real customer constraints, not a default preference, should decide.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [build-vs-buy, discovery-driven-decision]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why a silent guardrail block is insufficient
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a guardrail that silently blocks a violating request, with no visible trail, fails to actually "enable" a customer's team to operate the safety layer after handoff?

**OPTIONS:**
- [ ] A: Silent blocking is always technically impossible to implement correctly
- [x] B: With no structured, auditable record of what was blocked, why, and by which layer, the customer's own security or compliance team has nothing to investigate, report on for a compliance review, or use to tune the guardrail's false-positive rate
- [ ] C: Silent guardrails always have a 100% false-positive rate by design
- [ ] D: Guardrail triggers are legally required to be shown to the end user in real time

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The enable step requires giving the customer's own team something operable — a structured audit trail is what turns a guardrail from a black box the FDE understood into a system the customer's team can genuinely investigate and maintain.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [audit-log, enable, incident-response]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why the healthcare customer chose a self-hosted layer
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, why did the FDE choose a self-hosted regex-and-classifier pre-call layer over a managed PII-detection API, despite the added maintenance burden?

**OPTIONS:**
- [ ] A: Self-hosted layers are always faster than managed APIs regardless of infrastructure
- [x] B: The customer's compliance constraint, surfaced during discovery, prohibited any patient data leaving their infrastructure boundary — a managed API would violate that constraint by design
- [ ] C: Managed PII-detection APIs do not exist for healthcare-adjacent use cases
- [ ] D: The FDE's team had no prior experience with managed APIs

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is a direct application of the discovery-driven build-versus-buy principle: the customer's actual data-residency constraint, not a general preference, made the self-hosted option the only compliant choice.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [self-hosted-guardrail, data-residency, discovery-constraint]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Why the audit log went into the customer's existing SIEM
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why did the FDE write every guardrail trigger into the customer's existing SIEM system rather than a separate log only the FDE's own team could see?

**OPTIONS:**
- [ ] A: SIEM systems are the only tool capable of storing timestamped log entries
- [x] B: So the compliance team can pull a monthly report of every blocked attempt themselves, without depending on the FDE to run a query for them — the same enable-after-handoff principle applied to the guardrail layer specifically
- [ ] C: A separate log system would have been technically incompatible with the guardrail classifier
- [ ] D: SIEM systems automatically fix false-positive guardrail triggers without human review

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Routing the audit trail into a system the customer's own team already uses is what makes the guardrail layer genuinely operable by them after handoff, rather than a capability that quietly depends on the FDE staying involved.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [audit-log, SIEM, handoff]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Purpose of a false-positive review process
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the Suggested Extension's monthly false-positive review process close the loop on?

**OPTIONS:**
- [ ] A: It closes the loop between red-teaming and the golden test set from the prompt-engineering lesson
- [x] B: It closes the loop between the audit log's recorded triggers and the guardrail's own accuracy, letting the customer's compliance team's review feed back into tuning the guardrail's threshold over time
- [ ] C: It replaces the need for any structured audit logging going forward
- [ ] D: It determines whether to switch from a self-hosted to a managed guardrail service

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Without a feedback loop, an audit log is just a record; the review process is what turns that record into an input for actually improving the guardrail's accuracy over time, owned by the customer's own team.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [false-positive-review, feedback-loop, guardrail-tuning]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 11

```yaml
lesson_id: fde-enterprise-consulting-llm-11-cost-latency-and-model-routing
lesson_title: "Cost, Latency & Model Routing"
lesson_order: 11

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 75
content_status: Draft

learning_outcomes:
  - "Extend a basic complexity-based model-routing function into production routing infrastructure with caching, batching, and per-customer cost budgets."
  - "Choose between prompt caching and semantic caching for a given workload, and explain what class of repeated cost each one actually eliminates."
  - "Build a cost-and-latency observability view that lets an FDE and a customer jointly see where request volume is spending money and time, and use it to justify a routing or caching change with real numbers."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 9
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Cost, Latency & Model Routing

## Concepts Covered

The GenAI-World-and-LLM-Landscape lesson from the prerequisite module built a basic routing function: classify a question's complexity, send it to the smallest model tier that reliably clears the accuracy bar, and calculate the resulting cost savings at volume. That function is the right starting mental model but not yet production infrastructure — this lesson is about the layer that sits around it once real customer traffic and real reliability requirements are in play. The first addition is a routing gateway: rather than each feature's code independently deciding which model tier to call, a shared routing layer (a thin proxy service, or a library every feature imports) centralizes the tier-selection logic, the fallback-on-low-confidence escalation from the prerequisite lesson's practice loop, and per-customer usage tracking in one place — so a tier-selection improvement (a better complexity classifier, a new fallback rule) benefits every feature that routes through it, instead of needing to be re-implemented separately in each one. A gateway is also where per-customer cost budgets and quotas belong: a customer contracted for a specific monthly spend needs the routing layer to track cumulative cost against that budget and apply a policy (route to cheaper tiers only, alert, or hard-stop) as the budget is approached, which is an entirely different concern from the individual routing decision on any single request and doesn't belong scattered across feature code.

The second production lever, absent from the prerequisite lesson's basic function, is caching — and the two common forms eliminate genuinely different classes of repeated cost, which is why choosing the right one for a workload matters. Prompt caching (a provider-level feature that lets a long, unchanging prefix of a prompt — system instructions, few-shot examples, a large retrieved document — be cached server-side so a repeated call reusing that prefix is billed and latency-charged at a fraction of the full prompt cost) eliminates the cost of re-processing the same static content on every call; it is the direct production answer to the prompt-length cost concern the prompt-engineering-for-production-systems lesson flagged but deferred to this lesson, since a long but cacheable system prompt is far cheaper at volume than its raw token count suggests. Semantic caching (storing a past query's full response, indexed by the query's embedding, so a new query similar enough to a previous one returns the cached response instead of a new model call entirely) eliminates the cost of the model call altogether for near-duplicate queries — a distinct win, real for the high-frequency, low-variance question types the routing function already identified as candidates for the smallest model tier, since these are exactly the queries most likely to repeat close to verbatim across different users. Prompt caching helps every call that shares a long static prefix regardless of whether the query itself repeats; semantic caching only helps when the query itself is a near-repeat — conflating the two, or assuming one subsumes the other, misses real savings available from the one not chosen.

The third lever is a latency budget distinct from cost, because the fastest and cheapest tier are not always the same choice once a feature's actual UX requirement is factored in. A synchronous, user-facing chat response has a real latency budget (a user waiting more than a couple of seconds for the first token measurably degrades the experience), which argues for streaming the response token-by-token rather than waiting for the full completion, and can argue for a faster, slightly more expensive tier over the cheapest one if the cheapest tier's added latency crosses the UX threshold — a case where the pure cost-minimizing routing decision from the prerequisite lesson's practice loop is the wrong one once latency is weighed in explicitly. A background batch job (nightly report summarization, a large-scale reclassification run) has no such real-time constraint and can route to the cheapest tier and use batch-processing APIs (where providers offer a discounted rate in exchange for asynchronous, non-real-time processing) without any UX cost at all. Building the cost-and-latency observability that makes both of these decisions visible — per-route request volume, cost, p50/p95 latency, and cache hit rate, ideally broken out per customer — is what turns "we should route more traffic to the cheaper tier" from a hunch into a decision an FDE can justify to a customer with real numbers, the same evidence-based discipline the demo-storytelling lesson taught for presenting a solution's value.

## Practical Backend Scenario

The support-copilot from the prerequisite lesson's scenario has grown past its original single-customer prototype into a shared feature serving twelve customers, each with a different contracted monthly LLM spend. The FDE builds a routing gateway that all twelve customers' traffic passes through: it applies the original complexity-based tier selection, tracks cumulative spend per customer against their contracted budget (alerting the account team at 80% of budget, capping to the cheapest tier only past 95%), and applies prompt caching on the system instructions and retrieved-policy-document prefix shared across every call for a given customer, cutting the billed cost of that shared prefix by most of its raw token cost on every call after the first. Investigating the observability dashboard the gateway also produces, the FDE notices one customer's traffic is dominated by a small set of near-identical questions ("what's the WFH policy," asked by dozens of different employees in slightly different phrasing) — a strong semantic-caching candidate distinct from the prompt caching already in place, since these are different callers asking functionally the same question rather than one caller reusing a shared prefix. Adding semantic caching for that customer's traffic, tuned to a similarity threshold conservative enough to avoid returning a cached answer for a genuinely different question, cuts that customer's model-call volume noticeably further, and the dashboard's before-and-after cost and cache-hit-rate numbers are what the FDE uses to explain the improvement to the account team in concrete terms rather than a general claim that "caching helped."

## Practice Loop

1. Extend the basic routing function from the prerequisite lesson's practice loop into a shared gateway function that any feature could call, adding a per-customer running cost total and a simple budget-threshold policy (e.g. route to the cheapest tier only once a customer's tracked spend crosses a limit you set).
2. Identify one long, unchanging portion of your routed calls' prompts (system instructions, a retrieved document) and calculate what fraction of each call's total prompt tokens it represents — this is your prompt-caching candidate, and this diagnostic step quantifies how much of your current cost that fraction represents before you implement caching for it.
3. Separately, identify or construct a set of near-duplicate queries (different phrasing, same underlying question) your routed feature might realistically receive, and design a semantic-caching check (embedding similarity above a threshold returns a cached response) distinct from the prompt-caching mechanism in step 2.
4. For one synchronous, user-facing call in your routed feature, measure or estimate the latency difference between your cheapest tier and a faster tier, and decide — with the latency numbers in hand, not a guess — whether the UX cost of the cheapest tier's latency justifies routing to the faster, more expensive tier instead.
5. Build a minimal observability view (even a simple log summary is enough) showing, per route, request volume, total cost, and cache hit rate, and use it to identify one concrete opportunity (a routing change, a caching addition) you would recommend and could justify with the numbers your view produced.

## Evidence of Understanding

You can extend a basic per-request routing decision into shared gateway infrastructure with centralized tier selection, fallback escalation, and per-customer cost budgets. You can distinguish prompt caching from semantic caching by the specific class of repeated cost each eliminates, and choose correctly between them for a given workload rather than treating them as interchangeable. You can weigh latency against cost explicitly for a synchronous, user-facing call versus a background batch job, and justify a routing or caching recommendation using real cost-and-latency observability numbers rather than a general claim that a change "should help."

## Suggested Extension

Add a p95 latency alert to the gateway's observability view that fires when a specific route's tail latency crosses a threshold you define, and design what the gateway's automatic response should be — a temporary reroute to a faster tier, a circuit breaker to a cached or degraded fallback, or a page to the FDE — connecting this lesson's latency budget concept to the reliability and fallback-design discipline from the LLM-fundamentals-for-production lesson.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** What a routing gateway centralizes
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson recommend a shared routing gateway rather than letting each feature independently implement its own tier-selection logic?

**OPTIONS:**
- [ ] A: Individual features cannot technically call more than one model tier without a gateway
- [x] B: A shared gateway means a tier-selection improvement (a better classifier, a new fallback rule) benefits every feature routing through it at once, instead of needing separate re-implementation in each feature's own code
- [ ] C: Gateways eliminate the need for any per-customer cost tracking
- [ ] D: Routing gateways are required by every LLM provider's terms of service

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Centralizing routing logic means an improvement made once propagates to every feature using the gateway, rather than needing to be duplicated across each feature's independent implementation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [routing-gateway, centralization]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** Where per-customer budgets belong
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say per-customer cost budgets and quota policy belong in the routing gateway rather than scattered across individual feature code?

**OPTIONS:**
- [ ] A: Feature code is technically incapable of tracking cumulative cost
- [x] B: Tracking cumulative spend against a contracted budget and applying a policy as it's approached is a distinct, cross-cutting concern from any single routing decision, and centralizing it avoids duplicating (and inconsistently implementing) that logic in every feature
- [ ] C: Budgets only matter for customers on the cheapest model tier
- [ ] D: Gateways cannot apply any policy other than a hard stop

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Budget tracking spans every request a customer makes across every feature, which is exactly the kind of cross-cutting concern that belongs in shared infrastructure rather than duplicated, and potentially inconsistently implemented, in each feature separately.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [cost-budget, gateway, cross-cutting-concern]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** What prompt caching specifically eliminates
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What specific class of repeated cost does prompt caching eliminate, according to the lesson?

**OPTIONS:**
- [ ] A: The cost of a genuinely new, never-before-seen query
- [x] B: The cost of re-processing the same static, unchanging prefix of a prompt (system instructions, a large retrieved document) on every call that reuses it, regardless of whether the query itself repeats
- [ ] C: The cost of running the model's output through a post-call guardrail
- [ ] D: The cost of ingesting new documents into a RAG index

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Prompt caching targets the static prefix specifically — it helps on every call sharing that prefix regardless of what the variable part of the query is, which is a different mechanism from caching based on query similarity.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [prompt-caching, static-prefix]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** What semantic caching specifically eliminates
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say conflating prompt caching and semantic caching, or assuming one subsumes the other, causes real savings to be missed?

**OPTIONS:**
- [ ] A: Prompt caching and semantic caching are actually the same mechanism under different names
- [x] B: They eliminate genuinely different classes of repeated cost — prompt caching helps any call sharing a long static prefix regardless of query repetition, while semantic caching only helps when the query itself is a near-repeat — so relying on only one misses savings the other would have captured
- [ ] C: Semantic caching always produces a strict superset of prompt caching's savings
- [ ] D: Using both caching mechanisms together is technically impossible in the same system

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The two mechanisms target different sources of repeated cost — a shared static prefix versus a repeated whole-query pattern — so a workload can have savings available from one that the other would never touch, which is why distinguishing them matters.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [prompt-caching, semantic-caching, cache-type-selection]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** How prompt caching resolves the earlier lesson's deferred trade-off
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The prompt-engineering-for-production-systems lesson flagged prompt length as a cost concern but deferred the full trade-off to this lesson. How does prompt caching change that earlier lesson's cost calculus?

**OPTIONS:**
- [ ] A: It means prompt length no longer has any cost implications at all
- [x] B: A long but cacheable system prompt (a static prefix reused across calls) is billed at a fraction of its raw token cost after the first call, so its true production cost is much lower than its raw token count alone would suggest — without eliminating the value of trimming genuinely unnecessary content
- [ ] C: It means every prompt should be made as long as possible to maximize caching benefit
- [ ] D: It replaces the need for a golden test set when evaluating a prompt change

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Prompt caching doesn't make prompt length irrelevant — favoring the shortest prompt that clears the golden set's bar is still sound — but it changes the actual cost of a long, genuinely necessary static prefix, which is the specific resolution this lesson provides to the earlier lesson's deferred trade-off.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [prompt-caching, prompt-length-cost, cross-lesson-link]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** Why the fastest tier isn't always the cheapest choice
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson say a pure cost-minimizing routing decision can be the wrong choice for a synchronous, user-facing chat call, even when it correctly identifies the cheapest tier that clears the accuracy bar?

**OPTIONS:**
- [ ] A: Cost-minimizing routing decisions are always correct regardless of the use case
- [x] B: A real-time UX has a genuine latency budget, and if the cheapest tier's added latency crosses that threshold, a faster but more expensive tier can be the right choice once latency is weighed in explicitly, not just cost and accuracy
- [ ] C: Latency is never a real consideration for any user-facing feature
- [ ] D: The cheapest tier is always the fastest tier by definition

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
Cost and latency are separate constraints; a routing decision optimized purely for cost can violate a real UX latency requirement, which is why the lesson treats latency budget as its own explicit lever alongside cost and accuracy.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [latency-budget, routing-tradeoff]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** Why batch jobs can route differently than chat calls
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why can a nightly batch summarization job route to the cheapest available tier and use discounted batch-processing APIs, in a way a synchronous chat feature cannot?

**OPTIONS:**
- [ ] A: Batch jobs are always exempt from accuracy requirements
- [x] B: A batch job has no real-time UX constraint, so there is no latency cost to weigh against the cost savings — unlike a synchronous chat call where a user is actively waiting
- [ ] C: Batch-processing APIs are only compatible with the largest, most expensive model tier
- [ ] D: Chat features are technically incapable of using discounted APIs of any kind

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The absence of a real-time constraint is exactly what frees a background job to optimize purely for cost — the latency trade-off that matters for a synchronous chat call simply doesn't apply.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [batch-processing, latency-constraint]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** Distinguishing the scenario's two caching wins
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, the FDE applies prompt caching to the shared system-instructions-and-policy-document prefix, and separately adds semantic caching for one customer's near-identical questions. Why are these treated as two distinct additions rather than one mechanism?

**OPTIONS:**
- [ ] A: They are actually the same caching mechanism, described twice for emphasis
- [x] B: Prompt caching addresses the shared static prefix reused across every call for a customer, while semantic caching addresses different callers asking functionally the same question in different words — two distinct sources of repeated cost that neither mechanism alone would fully capture
- [ ] C: Semantic caching was only added because prompt caching failed to reduce any cost
- [ ] D: Prompt caching only applies to batch jobs, never to the support-copilot's live traffic

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The scenario deliberately illustrates both caching types working on different parts of the same feature's cost profile — the shared prefix and the repeated-question pattern are genuinely separate sources of redundant cost.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [prompt-caching, semantic-caching, scenario-application]
### QUESTION_BLOCK_END: Q8

### QUESTION_BLOCK_START: Q9
**QUESTION_ID:** Q9
**QUESTION_TITLE:** Why observability numbers mattered for the account team conversation
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson connect the gateway's before-and-after cost and cache-hit-rate numbers to the demo-storytelling lesson's evidence-based discipline?

**OPTIONS:**
- [ ] A: Cost numbers are only useful for internal engineering review, never for a customer-facing conversation
- [x] B: Concrete before-and-after numbers let the FDE justify the caching improvement to the account team the same way a demo ties evidence directly to a customer's success metric, rather than making a vague, unsubstantiated claim that "caching helped"
- [ ] C: The account team requires a live product demo before accepting any cost claim
- [ ] D: Observability dashboards replace the need for a written status update

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This connects back to the module's earlier communication discipline: a claim backed by real measured numbers is checkable and persuasive in exactly the way the demo-storytelling lesson taught, versus an unsubstantiated general claim.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [observability, evidence-based-communication]
### QUESTION_BLOCK_END: Q9
<!-- MCQ_SECTION_END -->

---

# LESSON 12

```yaml
lesson_id: fde-enterprise-consulting-llm-12-assessment-discovery-call-plus-rag-poc-build
lesson_title: "Assessment: Discovery Call + RAG PoC Build"
lesson_order: 12

pathway_id: fde-curriculum
pathway_name: "Forward Deployed Engineer (FDE)"

module_id: enterprise-consulting-llm
module_name: "5. Enterprise Communication, Consulting & LLM Engineering"
module_order: 5

difficulty: Medium-Hard
estimated_minutes: 90
content_status: Draft

learning_outcomes:
  - "Run a full discovery call against an unfamiliar mock customer scenario and produce a discovery brief that would pass the confirm-before-building bar from earlier in this module."
  - "Design and build a small RAG proof-of-concept against a provided document set, applying ingestion, hybrid search, and access-control decisions appropriate to the scenario's actual constraints."
  - "Evaluate your own PoC with a real, if small, RAGAS-scored eval set and articulate what production hardening (guardrails, cost/latency routing, observability) it would still need before a real customer deployment."

created_date: "2026-08-31"
last_updated: "2026-08-31"
author: "Raghuram Balaji"

supplementary_content:
  has_mcq_section: true
  mcq_count: 8
  has_coding_exercises: false
  exercise_count: 0
  has_further_reading: false
  resource_count: 0
```

<!-- CHAPTER_BODY_START -->
# Assessment: Discovery Call + RAG PoC Build

## Concepts Covered

This assessment combines the two halves of Module 5 into one end-to-end exercise, because a real FDE engagement never separates the consulting skills from the technical build the way the module's individual lessons had to for teaching purposes. The assessment has two connected parts. Part one is a mock discovery call: working from a short scenario brief (a fictional customer, an industry, a vague initial ask), you run the four-pass structure from the module's first lesson — current-state walkthrough, pain quantification, constraints, and stakeholder mapping — against a role-played customer, then produce a written discovery brief the same way the earlier lessons required, one specific enough that a stakeholder could confirm or correct it before any build work starts. The brief has to name a concrete, measurable success metric, not a vague goal, and it has to surface at least one real constraint (a data-residency requirement, an integration boundary, a compliance rule) that will directly shape what gets built in part two — this is the test of whether discovery was actually done, versus performed as a formality before jumping to a predetermined solution.

Part two is a small RAG proof-of-concept, built against a provided document set and directly answerable from the discovery brief you just wrote: the constraints you surfaced in part one should visibly shape technical decisions in part two, not be forgotten the moment the conversation ends. If the brief surfaced a data-residency constraint, the PoC's retrieval or guardrail design should reflect it, even in simplified form; if the brief surfaced that certain document types shouldn't be visible to certain roles, the PoC's ingestion should tag for it, even if enforcement is a stub. The PoC itself draws on the ingestion, hybrid search, and evaluation skills from lessons 7 through 9 of this module, scaled down to what's buildable in the assessment's time box — a handful of representative documents, a basic hybrid retrieval setup, and a small, hand-verified eval set (10-15 questions is enough) scored against at least the two retrieval-stage RAGAS metrics, context precision and context recall, from the prerequisite RAG lesson.

The assessment's final component is a self-evaluation that is honest about scope, not a claim of completeness. You are asked to explicitly name what your PoC does not yet have that a real customer deployment would require — a guardrail pipeline (lesson 10), cost-aware model routing at volume (lesson 11), incremental re-ingestion for a live document source (lesson 7), or a demo structured around the success metric from your own discovery brief (the demo-storytelling lesson) — and explain, in one or two sentences each, what closing that gap would actually take. This mirrors the honest-status-reporting discipline taught early in the module: a PoC presented as "basically done" when it has no guardrails and no evaluation gate is exactly the overstated-certainty failure mode the stakeholder-communication lesson warned against, and naming the gap explicitly is itself part of what's being assessed, not an admission of an unfinished assignment.

## Practical Backend Scenario

The assessment brief describes a mid-size logistics company (deliberately similar in shape to, but distinct in specifics from, the running example used across this module's earlier lessons) that wants "something like ChatGPT for our internal driver-handbook and safety-policy documents." Running the discovery call surfaces that the real pain is dispatchers spending 10-15 minutes per shift answering the same handful of driver questions by phone, that a workable success metric is "percentage of driver questions answered correctly without escalating to a dispatcher, measured against a 20-question test set drawn from real past calls," and that a real constraint — surfaced only when the stakeholder-mapping pass reaches the safety-compliance officer, not the dispatch manager who initiated the request — is that any safety-policy content involving a currently-open incident investigation must never be surfaced to drivers until the investigation closes. The written discovery brief names this constraint explicitly as a non-goal-adjacent hard requirement, and the PoC built in part two tags safety-policy documents with an "investigation-hold" flag at ingestion, filtered out at retrieval time regardless of how well a chunk would otherwise match a query — a direct, traceable line from one specific fact surfaced during stakeholder mapping to one specific technical decision in the build, which is exactly the connection the assessment is designed to test for.

## Practice Loop

1. Run the discovery call against the assessment's mock scenario using the four-pass structure, and write the discovery brief — problem statement, quantified pain, constraints, and a concrete success metric — to the same bar the module's earlier lessons required.
2. Before touching any code, write one sentence connecting each constraint named in your brief to a specific decision you intend to make in the PoC build — this diagnostic step forces the discovery-to-build connection to be explicit rather than assumed.
3. Build the PoC: ingest the provided document set with at least one access-control or content-restriction tag reflecting a constraint from your brief, and stand up hybrid retrieval against it.
4. Hand-build a 10-15 question eval set with verified gold answers and ground-truth chunks, and score your PoC's context precision and context recall against it, recording the actual numbers rather than an impression of how well it seemed to work.
5. Write the honest self-evaluation section: name at least three specific production gaps (drawing on lessons 7-11 of this module) your PoC does not yet close, and for each, one sentence on what closing it would actually require.

## Evidence of Understanding

You can run a structured, four-pass discovery call against an unfamiliar scenario and produce a discovery brief with a concrete success metric and at least one real, build-shaping constraint. You can build a small RAG PoC where a specific constraint from your own discovery brief visibly shapes a specific technical decision in ingestion or retrieval, rather than treating discovery and build as disconnected phases. You can score your own PoC against a hand-verified eval set using real RAGAS metrics and write an honest, specific self-evaluation naming genuine production gaps, rather than presenting a scoped-down PoC as more complete than it is.

## Suggested Extension

Take the honest self-evaluation from your practice loop's step 5 and turn the single most important named gap into a one-paragraph scoping item — problem, proposed approach, and rough effort estimate — written the way the technical-scoping lesson's options-matrix and risk-register discipline would require, as if you were proposing it as the next phase of this engagement to the customer from your discovery brief.
<!-- CHAPTER_BODY_END -->

<!-- MCQ_SECTION_START -->
## Multiple-Choice Questions

### QUESTION_BLOCK_START: Q1
**QUESTION_ID:** Q1
**QUESTION_TITLE:** Why the assessment combines both halves of the module
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Understanding
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does this assessment combine a mock discovery call with a RAG PoC build into one connected exercise rather than testing each skill set separately?

**OPTIONS:**
- [ ] A: Discovery and technical build skills are unrelated and combining them is only a time-saving measure
- [x] B: A real FDE engagement never separates consulting skills from the technical build — this assessment tests whether a constraint surfaced during discovery actually shapes the resulting build, not just whether each skill can be performed in isolation
- [ ] C: Separate assessments would require twice as much grading effort
- [ ] D: The RAG PoC build does not depend on any information gathered during discovery

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The assessment's design specifically tests the connection between the two halves — a discovery brief's constraints have to visibly influence build decisions — which is the real-world integration point the module's individual lessons couldn't test in isolation.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [assessment-design, discovery-to-build-connection]
### QUESTION_BLOCK_END: Q1

### QUESTION_BLOCK_START: Q2
**QUESTION_ID:** Q2
**QUESTION_TITLE:** What makes a discovery brief pass the assessment bar
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
According to the lesson, what does the discovery brief specifically need to contain to demonstrate discovery was genuinely done, not performed as a formality?

**OPTIONS:**
- [ ] A: A list of every possible feature the PoC could theoretically include
- [x] B: A concrete, measurable success metric and at least one real constraint that will directly shape what gets built in part two
- [ ] C: A guarantee that the PoC will meet the customer's expectations perfectly
- [ ] D: A cost estimate for a full production rollout

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson names these two elements specifically as the test of genuine discovery — a vague goal or a brief with no build-shaping constraint reads as a formality performed on the way to a predetermined solution, not real discovery.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 1
**KEYWORDS:** [discovery-brief, success-metric, constraints]
### QUESTION_BLOCK_END: Q2

### QUESTION_BLOCK_START: Q3
**QUESTION_ID:** Q3
**QUESTION_TITLE:** Why a constraint from discovery must be traceable into the build
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson require the PoC's technical decisions to visibly reflect the constraints surfaced during the discovery call, even in simplified form?

**OPTIONS:**
- [ ] A: A PoC is only graded on whether it retrieves accurate answers, regardless of any discovery-surfaced constraint
- [x] B: If constraints are surfaced during discovery but never actually shape the build, discovery was performed as a formality rather than genuinely informing the engagement — the traceable line from constraint to decision is what proves the connection
- [ ] C: Constraints only need to be reflected in the final written report, not in the PoC itself
- [ ] D: Technical constraints and business constraints are always identical and interchangeable

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The whole point of combining the two assessment parts is to test this connection directly — a constraint that never surfaces in the technical decisions means discovery didn't actually inform anything real.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [constraint-traceability, discovery-to-build]
### QUESTION_BLOCK_END: Q3

### QUESTION_BLOCK_START: Q4
**QUESTION_ID:** Q4
**QUESTION_TITLE:** Which RAGAS metrics the PoC eval set targets
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Knowledge
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
The assessment's small hand-verified eval set is scored against at least which two RAGAS metrics, according to the lesson?

**OPTIONS:**
- [ ] A: Faithfulness and answer relevancy, the two generation-stage metrics
- [x] B: Context precision and context recall, the two retrieval-stage metrics
- [ ] C: A single blended overall score combining all four metrics
- [ ] D: Latency and cost per query, treated as RAGAS metrics

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
The lesson specifically names context precision and context recall — the retrieval-stage metrics from the prerequisite RAG lesson — as the minimum scoring requirement for the scaled-down assessment PoC.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 2
**KEYWORDS:** [RAGAS, context-precision, context-recall]
### QUESTION_BLOCK_END: Q4

### QUESTION_BLOCK_START: Q5
**QUESTION_ID:** Q5
**QUESTION_TITLE:** Why naming production gaps is part of the assessment
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Evaluation
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
Why does the lesson treat the self-evaluation's list of named production gaps as part of what's being assessed, rather than an admission that the assignment is unfinished?

**OPTIONS:**
- [ ] A: Every PoC is expected to be fully production-ready regardless of the assessment's time box
- [x] B: Presenting a scoped-down PoC as more complete than it is repeats the overstated-certainty failure mode the stakeholder-communication lesson warned against; explicitly and specifically naming what's missing demonstrates the honest-status-reporting skill the module built throughout
- [ ] C: Naming gaps is only useful for the grader's convenience and has no connection to any earlier lesson
- [ ] D: A complete self-evaluation should claim the PoC has no remaining gaps

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This ties the assessment directly back to the module's earliest communication lessons — precise, honest status language that distinguishes what's actually done from what isn't is exactly what's being tested here, applied to your own work.

**LESSON_CONNECTION:** Concepts Covered, Paragraph 3
**KEYWORDS:** [honest-self-evaluation, status-reporting]
### QUESTION_BLOCK_END: Q5

### QUESTION_BLOCK_START: Q6
**QUESTION_ID:** Q6
**QUESTION_TITLE:** How the investigation-hold constraint reached the technical build
**DIFFICULTY:** Hard
**BLOOM_LEVEL:** Analysis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
In the scenario, the "investigation-hold" constraint on certain safety-policy documents was surfaced only during the stakeholder-mapping pass, by the safety-compliance officer rather than the dispatch manager who initiated the request. Why does this specifically illustrate the value of the stakeholder-mapping pass?

**OPTIONS:**
- [ ] A: The dispatch manager and safety-compliance officer always have identical requirements in any engagement
- [x] B: The loudest or first stakeholder (the dispatch manager) did not know about or mention this constraint; only by deliberately reconciling accounts across multiple stakeholders, including one not present at the initial request, did the FDE surface a requirement that materially changed the technical build
- [ ] C: Stakeholder mapping is only relevant for pricing and budget discussions
- [ ] D: The investigation-hold constraint would have been discovered regardless of which stakeholders were consulted

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This is a direct illustration of the module's earlier point that a requirement voiced by the loudest stakeholder isn't automatically the requirement that matters most — the safety-compliance officer's constraint would have been missed entirely without deliberately reconciling multiple stakeholders' accounts.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [stakeholder-mapping, hidden-constraint]
### QUESTION_BLOCK_END: Q6

### QUESTION_BLOCK_START: Q7
**QUESTION_ID:** Q7
**QUESTION_TITLE:** How the investigation-hold constraint was implemented technically
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Application
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
How did the PoC in the scenario technically implement the investigation-hold constraint from the discovery brief?

**OPTIONS:**
- [ ] A: By deleting all safety-policy documents from the index entirely
- [x] B: By tagging safety-policy documents with an "investigation-hold" flag at ingestion, filtered out at retrieval time regardless of how well a chunk would otherwise match a query
- [ ] C: By training a custom embedding model specifically for safety-policy content
- [ ] D: By adding a disclaimer to every response mentioning the possibility of an open investigation

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This mirrors the access-control tagging-at-ingestion and pre-filtering-at-retrieval mechanism taught in lessons 7 and 8 of this module, applied here to a compliance-driven content restriction rather than a role-based one.

**LESSON_CONNECTION:** Practical Backend Scenario
**KEYWORDS:** [ingestion-tagging, retrieval-filtering]
### QUESTION_BLOCK_END: Q7

### QUESTION_BLOCK_START: Q8
**QUESTION_ID:** Q8
**QUESTION_TITLE:** What the Suggested Extension asks you to produce
**DIFFICULTY:** Medium
**BLOOM_LEVEL:** Synthesis
**SOURCE_TYPE:** LLM_GENERATED

**QUESTION_TEXT:**
What does the Suggested Extension ask you to do with the most important gap named in your self-evaluation?

**OPTIONS:**
- [ ] A: Immediately build a full production implementation of it before the assessment is considered complete
- [x] B: Turn it into a one-paragraph scoping item — problem, proposed approach, and rough effort estimate — written to the same discipline as the technical-scoping lesson's options-matrix and risk-register work, as if proposing it as the engagement's next phase
- [ ] C: Remove it from the self-evaluation entirely, since naming it once was sufficient
- [ ] D: Escalate it directly to the safety-compliance officer without further scoping

**CORRECT_ANSWER_KEY:** B
**CORRECT_ANSWER_INDEX:** 1

**EXPLANATION:**
This connects the assessment's closing step back to the module's technical-scoping lesson, treating the most important named gap as a real, presentable scoping item rather than leaving it as an unstructured note.

**LESSON_CONNECTION:** Suggested Extension
**KEYWORDS:** [scoping, next-phase-proposal]
### QUESTION_BLOCK_END: Q8
<!-- MCQ_SECTION_END -->



