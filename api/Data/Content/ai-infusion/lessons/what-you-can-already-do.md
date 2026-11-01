# What you can already do

> **Lesson resources · Lessons 3–4 · RAG: give your AI a library:**
> - [Watch the Class 3 recording](https://www.scaler.com/meetings/i/ai-infused-learning-3/archive)
> - [Watch the Class 4 recording](https://www.scaler.com/academy/mentee-dashboard/class/558449)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Class-3-4-AI-infusion.zip)

AI **Engineering** · Class 3

Class 3 · RAG · Talk to your own documents

#### Stop letting your AI *guess*. Give it a library.

Class 2: your agent could *act* — but it still didn't know **your** data. Today you fix that. You'll build a system that reads your PDFs, finds the right passage for any question, and answers from **real text** — not vibes. It's called **RAG**, and it's how every "chat with your docs" app on the planet actually works. 👉

📚 Embeddings, intuition first ✂️ Chunking, demystified 🗂️ Vector databases 🎯 Reranking + hybrid search 📄 Chat-with-your-PDF, shipped

**Scaler Academy** — every diagram below is interactive. Drag, click, type along.

🧭 vector space, live demo

{{diagram:1}}

similar meaning ⟶ nearby points · that's the entire trick

30-second recap · classes 1 + 2

## ↺ What you can already do

Call any LLM (OpenAI, Groq, Ollama) Snap a LangChain chain together Pass chat history with placeholders Build an agent that picks tools

> **🤔:**
> **But your agent has two real problems**
>
> **1) It doesn't know *your* stuff** — your company's docs, your PDFs, last week's release notes. **2) When it doesn't know, it makes things up** (hallucinates) confidently. Today's class is the single biggest fix in AI engineering. Same agent loop — but now it can look things up in a library *you* built.

> **🎙️:**
> **Speaker note · landing the bridge**
>
> If the shop-assistant agent felt fuzzy last class, this class is the cleanup. Say it plainly: "Last week the model *chose* a tool. Today the tool is its own library — and the magic moves from *which tool* to *how do we find the right page?*." That's RAG, in one sentence.

Plan for today

## ⏱ Our Class 3 flight plan

Two clean halves: **understand the four pieces of RAG** (embeddings → chunking → vector DB → retrieval) and then **build a real "chat with your PDF" app**. Every concept gets a simulator.

0:00

**Recap + Why RAG?**

The 4 problems RAG solves — knowledge cutoff, private data, hallucinations, citations

0:10

**The RAG mental model in 1 picture**

Librarian analogy + the 5-box pipeline

0:20

**Embeddings — words become coordinates**

The "aha" moment: *king − man + woman ≈ queen*. Live similarity meter.

0:45

**Chunking — cut the book into snippets**

Strategies + chunk-size simulator

1:00

**Vector databases — search engine for meaning**

Chroma · Pinecone · Qdrant — which one when

1:10

**Build the 30-line RAG (live code)**

Load → chunk → embed → store → retrieve → answer

1:30

**Make it better — reranking + hybrid search**

Bi-encoder ✕ cross-encoder · BM25 ✕ vector

1:45

**Project: Chat with Your PDF**

Gradio chat UI + your own doc + public link

2:05

**Ship it to LinkedIn**

Caption template + post — today 🎉

2:15

**Peek ahead — Agentic RAG**

Where this leads next class

Block 14 · ~10 min · the hook

## 14 Why does RAG exist?

An LLM is a brilliant intern who finished training a year ago and was never allowed inside your office. RAG fixes both — fresh data, *and* your private data — by handing the intern a relevant page **at question-time**.

🗓️**Knowledge cutoff**

The model's training ended months ago. It doesn't know yesterday's RBI rate cut or last week's Budget numbers.

✓ RAG: fetch today's article

🔒**Private / internal data**

It has never seen your HR policy, your contracts, your product wiki, or your customer tickets — and you can't paste them all into one prompt.

✓ RAG: search your docs

🌀**Hallucinations**

When unsure, the model invents confident-sounding answers. Bad in customer support, dangerous in legal, fatal in healthcare.

✓ RAG: ground in real text

🔗**No citations**

Ask "where did you get that?" and a raw LLM has nothing. Real products need *"see source: page 14"*.

✓ RAG: return the source chunk

🤯

**The 1-line definition**

**RAG = Retrieval-Augmented Generation.** Before the model answers, *you* retrieve the most relevant snippets from your own data and stuff them into the prompt. The model then answers *from* those snippets. No retraining. No fine-tuning. Just open-book exam instead of closed-book.

🏭 Industry spotlight · where you've seen this already

##### Almost every "AI feature" you've used is RAG underneath

Notion AI answering from your workspace, Glean searching your company's apps, Perplexity citing sources, Intercom's Fin support bot, ChatGPT's "search the web", Cursor finding code in your repo, even the new "ask about this PDF" button in your browser — same pattern, every time. Master this, and you can clone any of them.

Notion AI Glean Perplexity Intercom Fin Cursor ChatGPT Search

> **💡:**
> **Quick reality-check (mention in class)**
>
> People sometimes ask: "Why not just fine-tune the model on our data?" Three reasons it's usually wrong: **(1)** expensive and slow to redo every time data changes, **(2)** still can't cite sources, **(3)** still hallucinates. RAG is faster, cheaper, traceable, and almost always the right first move.

Block 15 · ~10 min · the picture

## 15 RAG in one simple picture

Forget the buzzwords. The whole pipeline is just **a smart librarian** sitting between your question and the model.

> **📚:**
> **The library analogy that explains everything**
>
> Imagine you ask your friend a question about a 800-page book they've never read. Bad idea — they'll guess. Smart move? **You find the 3 most relevant pages, hand them over, and *then* ask.** They read the pages and answer confidently with the real text. That's RAG. The "librarian" who finds those 3 pages is the only new thing we're building today.

#### The 5-box pipeline (memorise this)

❓

**Question** user types it

➜

🔎

**Search** find relevant chunks

➜

📋

**Stuff** add chunks to prompt

➜

🧠

**LLM** answer using them

➜

💬

**Answer**+ source citation

Boxes 1, 4, 5 you already know from Class 1. Boxes 2 + 3 are the entire job of today's class.

Two phases · don't confuse them

**Phase 1 — Indexing (offline, once):** read your docs → break into chunks → turn each chunk into numbers (embedding) → store in a vector database. Slow, but you only do it when documents change.

**Phase 2 — Querying (online, every question):** turn the question into numbers → find nearest chunks in the database → paste them into the prompt → LLM answers. Milliseconds per query.

✨

**The unlock that surprises everyone**

You are *not* retraining the model. The model stays exactly the same as Class 1's `gpt-4o-mini`. We're only changing **what goes into the prompt**. RAG is, at its core, very fancy *prompt engineering* — automated.

Block 16 · ~25 min · the "aha" of the whole class

## 16 Embeddings: words become coordinates

Before we can "search by meaning", we need a way to **turn meaning into numbers**. That's an *embedding*. And once you see what it does, every confusing thing about RAG suddenly makes sense.

definition · keep this in your head

An **embedding** is a list of numbers (a *vector*) that captures the meaning of a piece of text. Similar meanings ⟶ similar numbers ⟶ nearby points in space. Different meanings ⟶ far apart.

#### Imagine a 2D world first — height & weight

Forget AI for a second. If I plot people by *height vs weight*, people of similar build end up close together on the chart. Same idea, scaled up. Real embeddings have **384, 768 or even 3072 dimensions** — way more than we can draw — but the principle is identical: *similar ⟶ close, different ⟶ far.*

> **📊:**
> **"Why so many dimensions?"**
>
> Because meaning is rich. Two words can be similar in many ways at once — *topic, tone, formality, language, sentiment*. Each dimension captures a different axis of similarity. 768 isn't arbitrary; it's just enough to separate millions of distinct ideas.

#### The *aha*: embedding math actually works

This is the demo that turned a generation of engineers into believers. Trained on enough text, vectors carry real relationships you can do arithmetic on. Pick a side and watch:

king − man + woman ≈ queen

king − man + woman

paris − france + india

delhi − india + japan

walking − walk + run

Click a different equation. Each is a *real result* from GloVe / Word2Vec embeddings — no tricks. The model never saw any rule like "queen is the female king" — that pattern just *emerges* from the geometry of meaning.

🤯

**Why this is the foundation of everything today**

If *woman* and *queen* can be found by simple arithmetic, then "find the chunk most similar to my question" is also just arithmetic — fast, scalable, and runs on commodity hardware. Every RAG system uses exactly this idea. **Search by meaning = nearest point in vector space.**

#### See it in 2D — same idea, drawable

A real-world plot of word vectors squished from 768 dimensions down to 2 for visualization. Click pairs and notice the *direction* connecting them is the same:

Live sim Vector space mini-map

click the pairs · watch the arrows align

{{diagram:2}}

👑 king ↔ queen / man ↔ woman

🏛️ paris ↔ france / delhi ↔ india

🍎 banana ↔ grape (close) vs aeroplane (far)

*"capital-of"* is encoded as the **direction** from country → capital. Same arrow length, same angle, anywhere on the map. That direction *is* the relationship.

#### The score we use: *cosine similarity*

Two vectors close together = the *angle* between them is small. The cosine of that angle is our score. It ranges from **-1 (opposite) to +1 (identical)**. Practically: **above 0.7 means "very similar"**, below 0.3 means "barely related". No math needed to use it — just remember: *bigger number = more similar*.

> **📐:**
> **The clock-hands intuition**
>
> Two clock hands pointing at the same time ⟶ angle = 0 ⟶ cosine = 1 ⟶ perfectly similar. Pointing at 12 and 6 ⟶ angle = 180° ⟶ cosine = −1 ⟶ opposites. We don't care how *long* the hands are, only the angle. That's why text length doesn't break the score.

#### Try it — the similarity meter

Type any two sentences. The meter shows the cosine similarity our system would compute (this in-browser simulation uses a small built-in semantic table, so results feel realistic for common topics).

Live sim Cosine similarity meter

try opposites, synonyms, totally unrelated pairs

Sentence A

Sentence B

0.00

cosine similarity

Type or click a preset to score.

**What the meter says:**

- 🟢 Near-synonyms — same meaning, different words.
- 🟢 Strongly related — same topic.
- 🟡 Loosely related — shares some concepts.
- 🟠 Distantly related — barely overlapping.
- 🔴 Unrelated — totally different vector neighbourhoods.

#### How do we actually get an embedding? One function call.

You don't have to train anything — somebody else already did. Open-source models from Hugging Face (`sentence-transformers`) or APIs from OpenAI / Cohere give you embeddings in one line:

```pseudo title="embeddings.py"
CREATE model = SentenceTransformer("all-MiniLM-L6-v2")   // free and fast, gives 384 numbers per text
SET vec = model.encode("A cat is sleeping on the couch")   // the embedding: a list of 384 numbers
PRINT the shape of vec
PRINT the first 5 numbers of vec

SET v1 = model.encode("A cat is sleeping on the couch")
SET v2 = model.encode("A kitten is napping on the sofa")
SET similarity = dot(v1, v2) / (norm(v1) * norm(v2))   // cosine similarity
PRINT similarity
```

> **Imported:**
> - `SentenceTransformer` from `sentence_transformers`, package sentence-transformers: loads a pre-trained embedding model by name.
> - `dot` from `numpy`: multiplies two vectors pair by pair and adds the results.
> - `norm` from `numpy.linalg`: returns the length of a vector.

```python reveal title="embeddings.py"
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # ① free, fast, 384 dims

vec = model.encode("A cat is sleeping on the couch")  # ② that's an embedding!
print(vec.shape)         # → (384,)  — 384 numbers
print(vec[:5])          # → [-0.05, 0.12, 0.41, -0.08, 0.22] (something like that)

# to compare two pieces of text → encode both → take cosine similarity
from numpy import dot
from numpy.linalg import norm

v1 = model.encode("A cat is sleeping on the couch")
v2 = model.encode("A kitten is napping on the sofa")
similarity = dot(v1, v2) / (norm(v1) * norm(v2))   # cosine
print(similarity)       # → 0.87 (very similar 🎉)
```

🔍 decoder

①

**all-MiniLM-L6-v2** is a tiny but excellent open-source embedding model — runs on your laptop, no API key needed. For production, look at `BAAI/bge-large-en-v1.5` (best English) or OpenAI's `text-embedding-3-small` (paid, very good multilingual).

②

`.encode("text")` returns the vector. That's the whole API surface — one call, 384 numbers back. Now your text is searchable by meaning.

> **🎙️:**
> **Speaker note · how to pitch this section**
>
> This is the "physics" of RAG. Don't rush. Spend a full 5 minutes letting them play with the meter and the king-queen equation. Once they internalize *"similar meaning = nearby vector"*, everything else in this class is bookkeeping.

📍

**Vectors = coordinates**

Every chunk of text gets a point in space.

📐

**Cosine similarity**

Score from −1 to +1. Bigger = closer.

🪄

**Math you can do**

king − man + woman ≈ queen. Really.

⚡

**One function call**

`.encode(text)` — that's it.

Block 17 · ~15 min · the unglamorous part that decides everything
