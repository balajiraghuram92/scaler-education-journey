# Why a plain LLM isn't enough

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

LLM, the brain Tools and actions Data, retrieval, memory Protocols (MCP, A2A) Safety and risk The agent itself

Section 1: Your first AI agent

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 1 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/your-first-agent-main.zip)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### Your first AI agent

Section 1. We start with a model that can only *talk*, and end with an agent that can *think, use tools and act*. Then you build one on Amazon Bedrock in about ten lines of Python.

Folder `section-01-your-first-agent` Notebook `01_hello_agent.ipynb` Scripts `hello_agent.py` `hello_langgraph_agent.py` Model: Claude Sonnet 4.6 on Amazon Bedrock

{{diagram:1}}

*The journey in this section. Each step adds one ability. Steps 1 to 4 make the model know more. Step 5 is different in kind: the model starts doing things.*

## 1.0 Why a plain LLM isn't enough

Large language models are brilliant, but on their own they are stuck inside what they learned during training. This section is about the two ways we break them out, without retraining the model.

A **large language model (LLM)** such as Claude learns by reading a huge amount of text, once, during **training**. After that its knowledge is frozen. That creates four practical problems for anyone building a real product.

{{diagram:2}}

*The four walls around a plain LLM, and the two doors out. RAG fixes the first three walls by feeding the model fresh, private information. Agents fix the fourth by letting the model use tools to act.*

> **Think of it like this:**
> Picture the class topper who has read every book in the library, and is then locked in an exam hall. No phone, no newspaper, no access to your company's files. Ask about last night's IPL match and they can only guess. Ask them to book you a Tatkal ticket on IRCTC and the best they can do is explain *how* you would book it.
>
> RAG is slipping the right pages under the door. An agent is giving them a phone, a laptop and permission to make calls on your behalf.

#### Two fixes that don't need retraining

You could **fine-tune** or retrain the model on new data, but that is slow, costly, and goes stale again the moment your data changes. Two lighter approaches solve most problems instead:

> **Retrieval Augmented Generation (RAG):**
> Before the model answers, fetch the most relevant pieces of *your* data and put them in the prompt. The model now answers from facts it can see. **It knows more.**

> **AI agents:**
> Give the model a goal, a set of tools, and a loop in which it can reason, call a tool, look at the result and decide what to do next. **It can do things.**

#### From "knowledge retriever" to "actor"

Many teams first build a RAG chatbot that answers questions about their own data. It works, and then users immediately ask for more:

- "Don't just tell me the leave policy. Apply leave for Friday."
- "Find a free slot with the design team and book the meeting."
- "Update the ticket and tell the customer it's fixed."

Moving from a passive system that *retrieves knowledge* to an active one that *takes action* is exactly where most developers get stuck. This section gives you the blueprint for that move. Keep two questions in mind as you read:

1. What is the actual difference between a chatbot and an agent?
2. How do we go beyond clever prompts to systems that carry out tasks *reliably*?

The usual path looks like the journey at the top of this page: a basic LLM, then single prompts, then chatbots, then chatbots grounded with RAG, and finally agents that reason, use tools and act.

#### What you'll learn here

1. What RAG is and how it works
2. What agents are and what they can do
3. The AWS agentic stack
4. How systems grow from one LLM to many agents
5. Agent protocols: MCP and A2A
6. The Strands Agents SDK
7. Building your own "Hello World" agent

> **Already built agents before?:**
> If you have shipped agents with LangGraph or CrewAI, parts 1.1 to 1.7 will feel like a refresher. Skim them for the shared vocabulary we use in every later section, then jump to the lab in 1.8.

## 1.1 RAG: an open book for the model

Retrieval Augmented Generation (RAG) lets a model answer from information it was never trained on, by finding the right text and handing it over just before the model answers.

RAG combines an LLM with an information retrieval system. The name tells you the three moves, in order:

1. R Retrieve Search an external **knowledge base** (a database, an API, or a library of documents) for information related to the user's question.
2. A Augment Add that information (the *context*) to the original question, building one detailed **prompt**.
3. G Generate The LLM reads the prompt and writes an answer that is factual and relevant, because the facts are right there in front of it.

> **Think of it like this:**
> RAG turns a closed-book exam into an **open-book exam**. Before you answer, a helpful librarian runs to the shelves, brings back the three most relevant pages and places them on your desk. You still write the answer yourself, but now you are reading from the page instead of guessing from memory.

#### A worked example

Suppose a user asks: *"Who won the 2024 Nobel Prize in Physics?"* A model whose training ended before October 2024 simply cannot know. Here is how RAG handles it.

{{diagram:3}}

*Retrieve, augment, generate. The retrieval step finds the fact; the augment step glues it to the question; the model only has to read and phrase the answer. Swap the news database for your HR policies and the same three steps answer "how many leave days do I get?".*

Try it

##### Same question, with and without retrieval

What reaches the model

What the model says

**If you pick "Plain LLM", the model says:** "I don't have reliable information about the 2024 Nobel Prize in Physics. My training data may end before it was announced."

Honest at best. At worst, a confident wrong guess.

**If you pick "LLM with RAG", the prompt reads:**

```text
Context:
The Nobel Prize in Physics 2024 was awarded to
John J. Hopfield and Geoffrey Hinton "for
foundational discoveries and inventions that
enable machine learning with artificial neural
networks."

Question:
Who won the 2024 Nobel Prize in Physics?
```

**If you pick "LLM with RAG", the model says:** "John J. Hopfield and Geoffrey Hinton won the 2024 Nobel Prize in Physics, for foundational discoveries that enable machine learning with artificial neural networks."

Correct, because the fact was in the prompt.

#### The full RAG pipeline

The three moves above hide some important engineering. A complete RAG system has two halves: work you do **once** to prepare your documents, and work that happens **every time** someone asks a question.

{{diagram:4}}

*Seven steps, two phases. Steps 1 to 4 build a searchable "memory" of your documents. Steps 5 to 7 use it for each question. The dashed border on step 6 means it is optional.*

##### Step 1. Loading (ingesting) the data

Load the documents you want people to ask about: PDFs, wiki pages, web pages, support tickets, rows from a database. This step is called **ingestion**. Garbage in, garbage out: if a document is outdated here, every answer built on it will be outdated too.

##### Step 2. Chunking

Split each document into smaller pieces of text, called **chunks**. Two reasons:

- **The model can only read so much at once.** Every LLM has a **context window**, a maximum amount of text it can take in one go. You cannot paste a 2,000-page manual into one prompt.
- **Long inputs bury details.** Models tend to pay most attention to the start and end of a long input and skim the middle. This is called the **lost-in-the-middle effect**. In a long story, the model might miss a character who appears halfway through. Small, focused chunks avoid that.

{{diagram:5}}

*Lost in the middle. A fact buried in the middle of a huge block is the one most likely to be missed. Chunking means each piece is short, so there is barely a "middle" to get lost in.*

> **Think of it like this:**
> Chunking is turning a thick textbook into a stack of **revision flashcards**. Before an exam you don't reread the whole book; you pull out the three cards that matter for this question.

Try it

##### Change the chunk size

Words per chunk = 25 25

Too small and a chunk loses meaning ("…carry forward to the next…"). Too big and you are back to one long block. Most teams start around a few hundred words, often with a little overlap between neighbouring chunks, and tune from there.

##### Step 3. Embedding

Each chunk is turned into an **embedding**: a long list of numbers (a **vector**) that captures what the text *means*. An *embedding model* does this. On AWS a common choice is Amazon Titan Text Embeddings v2, the same model we use for agent memory in Section 3 (`amazon.titan-embed-text-v2:0`).

The magic property: texts with similar meaning get vectors that sit **close together**, even if they share no words. "How many days off do I get?" lands near "Every employee gets 24 days of paid leave".

{{diagram:6}}

*From words to coordinates. The values shown are illustrative. What matters is that similar meanings produce nearby vectors, so "searching by meaning" becomes "finding the nearest points".*

> **Think of it like this:**
> An embedding is a **GPS coordinate for meaning**. Koramangala and HSR Layout have different names but nearby coordinates. In the same way, "salary credited late" and "payroll delay" are different words with nearby vectors.

Try it

##### See meaning as distance

Real embeddings have around a thousand dimensions. We have squashed some sentences down to two so you can see them. Pick a question and watch where it lands and which neighbours it pulls in.

{{diagram:7}}

**If you pick "Will rain stop the match?":** Notice this question sits *between* the weather and cricket groups, so it pulls neighbours from both. Meaning isn't one topic.

##### Step 4. Storage in a vector database

Each chunk is saved together with its vector in a **vector database** (or vector store). These systems are built for one job: given a vector, quickly find the stored vectors closest to it. That is called **similarity search**. Common options:

| Option | What it is | A good fit when |
| --- | --- | --- |
| Amazon OpenSearch Service | Managed search and analytics service on AWS with vector search | You want a managed AWS service that scales to large collections |
| Pinecone | Fully managed, hosted vector database | You want a dedicated vector service with nothing to operate |
| FAISS | Open-source similarity-search library that runs inside your app | Experiments, notebooks and smaller, in-memory indexes |
| Chroma | Lightweight open-source vector database | Quick local development and prototypes |
| PostgreSQL + pgvector | An extension that adds vector columns to Postgres | You already run Postgres (for example Amazon RDS or Aurora) |

There is no single best choice. It depends on how much data you have, how fast answers must be, and what your architecture already uses.

> **Think of it like this:**
> A normal library shelves books alphabetically. A vector database is a library that shelves books **by meaning**: walk to the "monsoon" aisle and you find books on rain, flooding and umbrellas side by side, whatever their titles.

##### Step 5. Retrieval

When a user asks a question, the system embeds the *question* with the same embedding model, then asks the vector database for the closest chunks. It returns the **top k** results, where *k* is simply how many you want: the top 3, top 5 or top 10. These chunks become the supporting context for the model.

##### Step 6. Filtering and reranking (optional)

Similarity search is fast but rough. **Reranking** takes the retrieved chunks and scores them again with a more careful (and slower) model, and filtering drops chunks that are irrelevant or not allowed (old versions, another department's data). Both improve answer quality, but they add cost, latency and moving parts, so they are optional.

> **Think of it like this:**
> Hiring at scale: a quick resume screen shortlists 50 candidates (retrieval), then a proper interview picks the best 3 (reranking). You only pay for interviews when the quick screen isn't good enough.

##### Step 7. Answer generation

The best chunks are passed to the language model together with the original question. The model writes a clear, relevant answer based on that retrieved information, ideally pointing to which chunk each fact came from.

Try it

##### Run the whole RAG pipeline on a tiny employee handbook

Or type your own question e.g. Can I work from home on Fridays?

Top k = 2 2

on Rerank the retrieved chunks

Retrieve: every chunk, ranked by similarity to the question

Augment: the prompt sent to the model

Generate: the answer

This playground scores chunks by shared words, a toy stand-in for embeddings. Real embedding models match meaning, so they would also connect "days off" with "paid leave".

**The handbook the playground searches:**

- [1] Leave policy: Every full-time employee gets 24 days of paid leave per year. Up to 8 unused days carry forward to the next year.
- [2] Sick leave: Employees get 12 days of sick leave each year. A doctor's note is needed for more than 2 days in a row.
- [3] Work from home: Employees can work from home up to 2 days a week with their manager's approval.
- [4] Travel policy: Book flights at least 14 days before travel. Economy class is required for flights under 6 hours.
- [5] Travel allowance: On work trips, the daily meal allowance is Rs 1,500 in metro cities and Rs 1,000 elsewhere.
- [6] Laptops: New joiners receive a laptop on day one. Report a lost or damaged laptop to IT within 24 hours.
- [7] Parental leave: Birthing parents get 26 weeks of paid leave. Other parents get 4 weeks of paid leave.
- [8] Holidays: The office is closed on 12 public holidays a year. The list is shared every December.

**When a preset's answer chunk is missed:** "I couldn't find that in the handbook." The chunk that holds the answer wasn't retrieved. Raise k, or turn reranking off and on to see what changes.

**Typed question, nothing relevant:** Nothing in the handbook matches well. A good RAG app answers "I couldn't find that" instead of guessing.

**Typed question, chunks retrieved:** In a real system this prompt now goes to the LLM, which would answer mainly from the top-ranked chunk.

> **Where this goes next:**
> Hold on to RAG. In the next part you will see that agents often use RAG as *one of their tools*, calling it only when they need facts.
