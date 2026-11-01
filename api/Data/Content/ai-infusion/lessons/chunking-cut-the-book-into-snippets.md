# Chunking: cut the book into snippets

## 17 Chunking: cut the book into snippets

Before we embed anything, we have to cut it up. You can't embed a 200-page PDF as one vector — meaning gets averaged away to mush. So we split it into *chunks*. **How** you chunk decides how good your RAG actually is. Engineers underestimate this; the best ones obsess over it.

> **🍕:**
> **The pizza-slice analogy**
>
> One whole pizza is hard to share — too big. Cut it into 100 confetti-sized bits and nobody can taste anything. **Slice sizes matter.** Chunks are pizza slices: too big and you lose precision (the relevant bit is buried), too small and you lose context (each crumb is meaningless).

#### The 4 chunking strategies worth knowing

📏**Fixed size**

Every N characters or tokens — done. Brain-dead simple, fast, your default. *Downside:* chops mid-sentence, mid-table, mid-thought.

Best for: prototypes, blog posts

🔁**Recursive**

Try to split on paragraphs first; if too big, split on sentences; if still too big, on words. Smart fallback ladder. The default in LangChain.

Best for: most real apps

🧠**Semantic**

Embed every sentence; group consecutive sentences that "talk about the same thing". Chunks follow meaning, not size.

Best for: long flowing prose

📑**Structure-aware**

Use the document's own structure — markdown headings, code blocks, HTML sections. Each section becomes a chunk.

Best for: docs, code, wikis

#### Watch all 4 strategies — same text, four different cuts

Same source passage, four ways to chop it. Switch tabs and watch **where the cuts land** and **how chunks change shape**. The differences *are* the lesson — pure text won't make this click; the picture will.

Live sim 4 chunking strategies · same source

click tabs · compare cuts side by side

📄 Source · a tiny markdown doc with 3 topics

```text

```

# Bengaluru Overview

## Tech Industry
Bengaluru is known as India's Silicon Valley. Tech parks like Electronic City and Whitefield host thousands of tech companies. Major firms include Infosys, Wipro, and TCS.

## Climate
The city sits at 920 meters altitude. This gives it pleasantly cool weather year-round. Average temperatures rarely exceed 30 degrees.

## Food
Bengaluru's food scene is legendary. South Indian classics like masala dosa and idli thrive here. Filter coffee shops dot every street corner.

📏

**Fixed** blind char-count

🔁

**Recursive** respect boundaries

🧠

**Semantic** group by topic

📑

**Structure** follow headers

**Try this sequence in class:** start on *Fixed* at size 80 → count the 🪓 mid-word cuts → flip to *Recursive* at the same size → they're all gone → flip to *Semantic* → notice three chunks emerge that align perfectly with the three topics → flip to *Structure* → see how the markdown `##` headers do the work for free.

**What to notice · Fixed**

> **Cuts land at character N — no respect for words, sentences, or paragraphs.** Chunks marked 🪓 were split *mid-word*; context gets fragmented. Cheap to write (one for-loop), but bad for retrieval. Prototypes only.

**What to notice · Recursive**

> **Same character budget, far cleaner cuts.** Splits at paragraph breaks first, then sentences, then words. Almost nothing fragments mid-thought. This is LangChain's `RecursiveCharacterTextSplitter` — the safe default for ~90% of RAG apps.

**What to notice · Semantic**

> **Chunks shaped by meaning, not size.** All *tech* sentences join into one chunk; all *climate* another; all *food* a third. Sizes vary wildly — that's the feature. Best when topic shifts matter more than uniform length. Slower (embed every sentence first).

**What to notice · Structure**

> **Each `##` section becomes its own chunk — header attached to its content.** Markdown, HTML, and code already have natural structure — use it. Unbeatable for docs, wikis, source code: the author already told you how to split.

**Controls**

- **Fixed and Recursive:** Chunk size (characters) · try 80 to see the difference
- **Semantic:** No size knob. Sentences are tagged by topic (tech · climate · food) and adjacent same-topic sentences are merged. Meaning sets the boundaries.
- **Structure:** No size knob. Splits on Markdown headers (`##`). Document structure sets the boundaries.

the recall vs precision tradeoff · keep this in mind

**Big chunks** → high recall (the answer is probably *in* there), but low precision (lots of fluff around it). **Small chunks** → high precision (the chunk is exactly the answer), but low recall (the relevant bit might be split across two chunks and you only pulled one). Most teams sweep chunk size as their first RAG tuning knob.

#### One line of real code

```pseudo title="chunk.py"
CREATE splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)   // about 800 characters per chunk, adjacent chunks share 100
SET chunks = splitter.split_text(your_long_document)
PRINT the number of chunks
```

> **Imported:**
> - `RecursiveCharacterTextSplitter` from `langchain_text_splitters`, package langchain-text-splitters: cuts long text into pieces, preferring paragraph and sentence breaks.

```python reveal title="chunk.py"
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,        # aim for ~800 chars per chunk
    chunk_overlap=100,     # adjacent chunks share 100 chars (context glue)
)

chunks = splitter.split_text(your_long_document)
print(len(chunks))    # → e.g. 47 chunks ready to embed
```

> **💡:**
> **Why `chunk_overlap`?**
>
> If your question's answer sits exactly at a chunk boundary, you'd miss it. Overlap (50–100 chars) makes sure every sentence appears in at least one chunk fully. Cheap insurance.

Block 18 · ~10 min

## 18 Vector databases: a search engine for meaning

You have thousands of embeddings. For every question, you need the top-k nearest ones — *fast*. That's what a vector database does, and that's **all** it does.

> **🗂️:**
> **One-line definition**
>
> A vector database is a *search engine* where instead of "find documents containing this word", the query is "find vectors closest to *this* vector". Same idea as Google, swapped engine.

#### The three names you'll hear all the time

🟢

**Chroma**

Open-source, runs in-process (no server!), one `pip install`. Perfect for prototypes & up to ~10M vectors. **What we'll use today.**

🔵

**Pinecone**

Fully managed SaaS. Zero ops, scales to billions, but paid. The boring-and-reliable choice for production.

🟣

**Qdrant**

Open-source *and* production-grade. Self-host or use their cloud. Great middle ground when you outgrow Chroma.

> **🎯:**
> **Picking one (don't overthink)**
>
> Prototyping or under 1M chunks? **Chroma**. Want zero ops & have a budget? **Pinecone**. Need to self-host at scale? **Qdrant** or **Weaviate**. The good news: LangChain wraps all of them with the same interface, so swapping later is a one-line change.

#### What it actually does — three operations

a vector DB is just these three calls

1

`db.add(documents, embeddings)` — store chunks and their vectors. (Indexing.)

2

`db.query(query_vector, k=3)` — return the 3 chunks whose vectors are closest. (Retrieval.)

3

`db.delete(ids)` — remove chunks when a doc is deleted. That's it. Three calls.

🏭 Industry spotlight · how it stays fast

##### HNSW — the trick behind every vector DB

Searching billions of vectors naively means computing billions of distances per query. **HNSW** (Hierarchical Navigable Small World — a 2018 algorithm) builds a "ladder" graph so each query takes only ~log(N) hops. Result: sub-10ms lookups on 100M vectors. You'll never write this yourself — every vector DB ships it built-in.

Chroma · HNSW Pinecone · proprietary Qdrant · HNSW FAISS · IVF + HNSW

Block 19 · ~20 min · all four pieces, working together

## 19 Build a real RAG in 30 lines

We've talked about every piece. Now we wire them up. This is the whole pattern — every RAG system you'll see in production is just a fancier version of *this*.

#### Step 1 — Index your documents (once)

```pseudo title="index.py"
SET docs = a list of 4 sample sentences about returns, shipping, corporate orders and office hours
CREATE splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
SET chunks = splitter.create_documents(docs)   // wraps each piece of text as a document
CREATE embedder = HuggingFaceEmbeddings("all-MiniLM-L6-v2")   // free, runs on your machine
CREATE db = Chroma.from_documents(chunks, embedder, save to "./chroma_db")   // embeds every chunk, then stores it on disk
PRINT "Indexed " + number of chunks + " chunks"
```

> **Imported:**
> - `RecursiveCharacterTextSplitter` from `langchain_text_splitters`, package langchain-text-splitters: cuts the documents into chunks of about 500 characters.
> - `HuggingFaceEmbeddings` from `langchain_huggingface`, package langchain-huggingface: wraps a free embedding model that runs locally.
> - `Chroma` from `langchain_chroma`, package langchain-chroma: a vector database that stores the chunks and their vectors in a folder.

```python reveal title="index.py"
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# ① load your documents (any text — for now, hardcoded)
docs = [
    "Our return policy allows refunds within 30 days of purchase.",
    "Shipping is free for orders above ₹999 across India.",
    "For corporate orders above 50 units, contact sales@example.com.",
    "Our office is in Indiranagar, Bangalore. Open Mon-Fri 10am-7pm.",
]

# ② split into chunks (small docs here, but production = thousands of pages)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.create_documents(docs)

# ③ pick an embedding model (free, runs locally, no API key)
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ④ build the vector store from chunks + embeddings (saves to disk)
db = Chroma.from_documents(chunks, embedder, persist_directory="./chroma_db")

print(f"Indexed {len(chunks)} chunks 🎉")
```

#### Step 2 — Ask a question (every time)

```pseudo title="rag.py"
LOAD the .env file into the environment   // load_dotenv()
CREATE embedder = HuggingFaceEmbeddings("all-MiniLM-L6-v2")   // the same model used for indexing
CREATE db = Chroma opened from "./chroma_db", using embedder
CREATE model = ChatOpenAI("gpt-4o-mini", temperature 0)   // low randomness, steadier answers
CREATE prompt = a template with {context} and {question} slots, saying to answer ONLY from the context
DEFINE rag_answer(question):
    SET chunks = db.similarity_search(question, k=3)   // the 3 nearest chunks
    SET context = the text of each chunk, joined with blank lines
    SET chain = prompt | model
    RETURN the text of chain.invoke(context, question)
PRINT rag_answer("How long do I have to return something?")
```

> **Imported:**
> - `HuggingFaceEmbeddings` from `langchain_huggingface`, package langchain-huggingface: the free local embedding model, the same one used when indexing.
> - `Chroma` from `langchain_chroma`, package langchain-chroma: opens the vector store saved in the chroma_db folder.
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the chat model that writes the final answer.
> - `ChatPromptTemplate` from `langchain_core.prompts`, package langchain-core: builds a prompt with named slots that get filled in.
> - `load_dotenv` from `dotenv`, package python-dotenv: copies the .env file into the environment.

```python reveal title="rag.py"
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

# ⑤ open the same vector store we built in step 1
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db       = Chroma(persist_directory="./chroma_db", embedding_function=embedder)
model    = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ⑥ the prompt: instructions + chunks + question
prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below. If the context doesn't contain
the answer, say "I don't know." Be concise and quote facts directly.

Context:
{context}

Question: {question}
""")

def rag_answer(question):
    chunks = db.similarity_search(question, k=3)         # ⑦ retrieve top 3
    context = "\n\n".join(c.page_content for c in chunks)
    chain = prompt | model                                # ⑧ same chain trick as Class 2
    return chain.invoke({"context": context, "question": question}).content

print(rag_answer("How long do I have to return something?"))
# → "30 days from the purchase date."  ✅ from your data, not a guess
```

🔍 decoder — the 8 numbered steps

①

Your data. In real life this is PDFs, web pages, Notion exports — anything you can turn into text.

②

Chunk it. Block 17 in action. `chunk_size=500` is a sane default.

③

Pick an embedder. We're using a free local one — swap to `OpenAIEmbeddings()` for a paid, slightly better version.

④

`Chroma.from_documents` embeds every chunk and stores both the text and the vector. Done once per dataset.

⑤

Reopen the same database. The embeddings are already on disk — no re-encoding.

⑥

The magic prompt template. Notice `"ONLY the context below"` — this single line is the most important hallucination-fighter in RAG.

⑦

`similarity_search` = embed the question, find the 3 nearest chunks, return them. The librarian.

⑧

Same LangChain pipe (`prompt | model`) you used in Class 2. **RAG didn't replace your previous knowledge — it slotted right in.**

#### Watch it run — step-by-step pipeline

Press *Next* to see exactly what happens inside `rag_answer("How long do I have to return something?")`. Each step is a card; this is the whole RAG flow on one screen:

- **1 · USER QUESTION:** `"How long do I have to return something?"`
- **2 · EMBED THE QUESTION:** Turn the question into a 384-number vector via `model.encode(question)`. We can't show 384 numbers, but think of it as the question's "coordinates".
- **3 · SEARCH THE VECTOR DB:** `db.similarity_search(query, k=3)` → finds the 3 nearest chunks: refunds within 30 days... · shipping is free above ₹999 · corporate orders contact sales@
- **4 · STUFF INTO THE PROMPT:** The retrieved chunks become `{context}` in our prompt template. Question goes into `{question}`. One single string is sent to the LLM.
- **5 · LLM ANSWERS FROM CONTEXT:** GPT-4o-mini reads the prompt and replies: *"You can return items within 30 days of purchase."* ✅ Pulled from the chunk, not from memory.

✓ RAG complete · same loop runs every question.

Live sim RAG, step by step

press ▶ five times

🎯

**Take a moment — this *is* the canonical pattern**

That's it. Every RAG system in the world — from a hobby project to Perplexity — is a variant of these 8 lines. From here we're just making it *better*: smarter retrieval, smarter prompts, multiple passes. The core never changes.

Block 20 · ~15 min · 80% of RAG quality lives here

## 20 Make it better: rerank + hybrid search

A vanilla RAG works. A *good* RAG works **well**. The two tricks that close that gap — and that every senior engineer asks about — are *reranking* and *hybrid search*. Both are easy to add.

#### Problem 1: the top-5 from vector search isn't the *best* 5

Embedding similarity is fast, but it sometimes ranks shallow word-matches above deep semantic matches. So we use a **two-stage retrieval** — a fast first pass to narrow down, then a slow accurate pass to pick the real winners.

> **📄:**
> **Imagine hiring for one open role — with 1,000 applicants**
>
> You can't interview 1,000 people (it would take a year). You also can't pick someone by gut feel from a stack of resumes (you'd hire badly). So you do **two passes**: a fast *resume scan* to shortlist 25, then a real *30-minute interview* with each of those 25. **Bi-encoder and cross-encoder are exactly these two passes.**

📋**Bi-encoder** like a resume scan

Reads the query and the document **separately**, turns each into a vector, then compares the two vectors with cosine similarity. The encoder *never sees them together* — it judges each "card" alone.

- ⚡ **Fast** — sub-10ms over millions of docs
- 💾 **Pre-computable** — encode all your docs once, store forever, only encode the query at runtime
- 📉 **Shallow** — misses subtle relevance because the model never compares them side-by-side

→ use it to grab top 50–100 candidates

🎙️**Cross-encoder** like a 30-min interview

Feeds the query **and** the document into one transformer *together*, lets the model attend to both at once, then outputs a single relevance score. The model can compare them token by token, weigh trade-offs, spot nuance.

- 🎯 **Way more accurate** — sees query↔doc word interactions directly
- 🐢 **Slow** — full transformer run per (query, doc) pair
- ❌ **Not pre-computable** — each score is pair-specific, you can't cache anything

→ use it to rerank those 50 → top 3

1,000,000

all your chunks

📋 bi-encoder

➜

~10 ms

50

candidates

🎙️ cross-encoder

➜

~200 ms

3

to the LLM

*Funnel total: ~210ms — fast enough for live chat, accurate enough to beat raw vector search by miles.*

remember this — the two-stage pattern is universal

**Stage 1 (bi-encoder):** grab top 50-100 candidates from the vector DB. Fast.

**Stage 2 (cross-encoder):** re-score those candidates with a smarter model. Slow per item, but you're only re-scoring 50, not 50 million. Keep the top 3-5 for the LLM.

#### See reranking flip the order

Same query, same candidates. *Left*: what cosine similarity returned. *Right*: what a cross-encoder reranker returns. Press the button and watch the real answer rise:

Live sim Reranker · before vs after

query: "how do I return a defective product?"

Press *Run* to see the cross-encoder rerank.

**Stage 1 · before rerank**

1. Our shipping is fast and reliable for all returns. — 0.78
2. Refund policy: items can be returned within 30 days. — 0.74
3. Return shipping labels are emailed after request. — 0.71
4. For damaged or defective items, replacements are sent free of cost. — 0.69
5. Our return desk is at the warehouse in Pune. — 0.66

**Stage 2 · after cross-encoder rerank**

1. For damaged or defective items, replacements are sent free of cost. — 0.94
2. Refund policy: items can be returned within 30 days. — 0.88
3. Return shipping labels are emailed after request. — 0.81
4. Our return desk is at the warehouse in Pune. — 0.62
5. Our shipping is fast and reliable for all returns. — 0.45

stage 1 · vector search (top 5)

➜

stage 2 · cross-encoder rerank

Notice doc #3 — it never says the word "return" but it's clearly the most relevant. Pure vector search ranks it #4; cross-encoder lifts it to #1. *That* is why we rerank.

The code to add reranking is laughably short:

```pseudo title="rerank.py"
CREATE reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")   // free and fast
DEFINE retrieve_with_rerank(question, top_k = 3):
    SET candidates = db.similarity_search(question, k=25)   // 25 cheap candidates from the vector store
    SET pairs = one (question, chunk text) pair for each candidate
    SET scores = reranker.predict(pairs)   // one relevance score per pair
    RETURN the top_k candidates, sorted by score from highest to lowest
```

> **Imported:**
> - `CrossEncoder` from `sentence_transformers`, package sentence-transformers: a model that reads the query and a document together and gives one score. It is accurate but slow.

```python reveal title="rerank.py"
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")   # free, fast

def retrieve_with_rerank(question, top_k=3):
    candidates = db.similarity_search(question, k=25)        # grab 25 cheap candidates
    pairs = [(question, c.page_content) for c in candidates]
    scores = reranker.predict(pairs)                          # cross-encoder scores each pair
    return [c for _, c in sorted(zip(scores, candidates), reverse=True)[:top_k]]
```

#### Problem 2: sometimes you need the *exact word*

Pure semantic search ignores keywords. Ask "what's the price of **SKU-4429**?" and the embedding doesn't care about that specific code — it just sees "price" and "product". For codes, names, IDs, dates — **keyword search beats semantic** hands down. The fix isn't to pick one or the other. It's to use *both*, with very different strengths.

> **📚:**
> **Two librarians, very different superpowers**
>
> Remember our librarian from Block 15? She has **two assistants** who search the stacks completely differently. One is a literalist who lives for exact words. The other is a philosopher who lives for meaning. Send your query to the right one and you get great results. **Send your query to *both* — and let them merge their rankings — and you get magic.** That's hybrid search.

🔤**Librarian A · BM25** the literalist

Obsessed with **exact words**. Type *"SKU-4429"* or *"Article 21"* and she'll find every single doc containing those exact characters. But ask for *"running shoes"* and she'll skip the doc titled *"marathon footwear"* — different words, even though same meaning.

- ✅ **Brilliant at** product codes, SKUs, model numbers, version strings
- ✅ **Brilliant at** proper nouns, dates, legal references, technical jargon
- ❌ **Blind to** synonyms, paraphrase, intent — words are just characters to her

→ catches what vector misses

🧠**Librarian B · Vector** the philosopher

Obsessed with **meaning**. Ask for *"running shoes"* and she surfaces *"marathon footwear"*, *"jogging trainers"*, even *"sneakers for athletes"*. But ask for *"SKU-4429"* and she shrugs — random letters and numbers are just noise to her.

- ✅ **Brilliant at** natural-language questions, "what's this about?"
- ✅ **Brilliant at** fuzzy queries, paraphrase, multilingual matching
- ❌ **Blind to** exact codes, IDs, technical strings — drowns them in averages

→ catches what BM25 misses

#### Hybrid = both librarians on the case

Send the same query to *both* librarians at the same time. Each ranks the docs by their own logic. You then **merge their two ranked lists into one** using a tiny formula called **Reciprocal Rank Fusion (RRF)**:

⚡

**Reciprocal Rank Fusion in one line**

For each doc, final score = `1 / (60 + rank in BM25) + 1 / (60 + rank in Vector)`. Docs that *both* librarians ranked highly bubble to the top. Docs only one of them liked still get a fair shot. No tuning, no thresholds, no magic numbers (well, 60 — but it almost never matters). *That's it.* Used by almost every production RAG system in the wild.

> **🤝:**
> **Why this works so well in practice**
>
> Real user queries are *messy* — mostly natural language, but sprinkled with technical terms, product codes, names, or jargon the embedding model has never seen. Hybrid covers both halves of every messy query automatically: the natural-language part goes to Vector, the technical-term part goes to BM25, and RRF stitches the answers together. **You're not picking sides — you're using each tool for what it's actually good at.**

#### See it on a real query — *"I want running shoes"*

Same query, three rankings. Watch how Librarian A and Librarian B return different top picks — and how Hybrid merges them. Press the button to see who wins:

Live sim BM25 vs Vector vs Hybrid

same query, three rankings

press ▶ Compare

**Document set**

1. Adidas Ultraboost sneakers · Marathon running shoes
2. Nike Air Zoom Pegasus trainers
3. Puma casual footwear for everyday wear
4. Asics Gel-Kayano stability trainers
5. Reebok CrossFit gym shoes
6. Woodland leather trekking boots
7. Bata kids school shoes

##### 🔤 BM25 keyword

Counts word overlap. Loves "shoes" appearing literally.

##### 🧠 Vector semantic

Understands "running" means jogging — even if the word "shoes" isn't there.

##### ⚡ Hybrid blended

Reciprocal rank fusion — gives the best of both. Default for production.

🏭 Industry spotlight · this is what the leaderboard chases

##### Every "+10% retrieval quality" paper is one of these tricks

Reranking + hybrid search are the two single biggest quality wins in RAG. Add them and you go from "demo works" to "production works". Almost every benchmark in the MTEB leaderboard uses some combination. You now know the playbook.

BM25 + Vector Cross-encoder rerank Reciprocal rank fusion Cohere Rerank API

Block 21 · ~20 min · 🏁 THE BUILD
