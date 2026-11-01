# Why memory is hard

## 3.3 Why memory is hard

Before building memory into an agent, know the six problems you're signing up for.

{{diagram:1}}

*Six things that make memory hard. Every managed memory service you'll meet, including AgentCore Memory, is essentially a set of answers to these six.*

1. 1 Storage scalability As an agent talks to users and does tasks, the data it generates grows very quickly. Storing millions of high-dimensional embeddings (numeric representations of text) is expensive and heavy. You have to scale the store without it slowing down or costing a fortune.
2. 2 Memory refresh Real life changes. Agents need to update or overwrite old facts with new ones. Deciding what to keep, what to forget, and how to update outdated information without corrupting the rest is a delicate balance.
3. 3 Integration complexity Connecting an LLM to vector databases, external APIs and different memory layers (short-term vs long-term), and making them talk efficiently in real time, is a serious engineering job.
4. 4 Privacy and security Memory often holds personal or proprietary information, which makes it a target. If an agent remembers a card number or health data, that must be encrypted and tightly controlled. There's also **multi-tenancy** risk: one user's memory leaking into another user's answers.
5. 5 Retrieval accuracy Stored memory is useless if the agent can't find the right piece. Searches often return noisy or only loosely related results. Improving **precision and recall** is one of the biggest technical hurdles.
6. 6 Observability It's hard to see why an agent remembered one fact or failed to find another. Without tools to monitor, trace and visualise how memory is used, debugging and improving the agent is very difficult.

## 3.4 An agent loop with memory

Here is how an agent with both short-term and long-term memory handles one request, end to end.

{{diagram:2}}

*Read, think, answer, write. Solid arrows 2 and 3 read memory before thinking; dashed arrows 6 write back afterwards, so the next request starts smarter.*

Step through

##### Follow one request through memory

Pick step 1. The example: a returning user asks a support agent "Has my replacement shipped yet?"

- **Step 1 · Perceive.** A returning user writes: “Has my replacement shipped yet?”
- **Step 2 · Read short-term memory.** This session so far: the user has just logged in; no task is in progress.
- **Step 3 · Query long-term memory.** Found: *preference* “send updates on WhatsApp”; *history* “order #4471 arrived damaged, replacement approved 3 days ago”; *knowledge* “replacements ship within 2 working days”.
- **Step 4 · Reason.** The LLM gets the question plus all of that context, and decides to check the courier status for the replacement of #4471.
- **Step 5 · Act.** It calls the tracking tool and replies: “Yes, your replacement for #4471 shipped yesterday. I'll send updates on WhatsApp.”
- **Step 6 · Save and learn.** It writes back: “replacement for #4471 shipped”, so the next session starts with that already known.

1. 1 Perceive the query From a user (text or voice), a system-triggered API event, or an automated change in the environment.
2. 2 Read short-term (working) memory Recent conversation history, current task progress, and the session's immediate state.
3. 3 Query long-term memory From vector databases or key-value stores: **user preferences** (settings and styles), **historical data** (past decisions and their outcomes), and a **knowledge base** (learned concepts, summaries, previous experiences).
4. 4 Reason Combine the input with retrieved short- and long-term context into one prompt, and let the LLM decide the best course of action.
5. 5 Act Produce a context-aware result: a personalised reply, a detailed plan, or a tool call.
6. 6 Save and learn Store new information (updated goals, success or failure signals, structured insights) back into memory for future tasks.

## 3.5 Memory building blocks on AWS

AWS gives you a service for every kind of memory: fast stores for the conversation in progress, databases for facts, vector search for meaning, cheap storage for raw files, and glue to tie it together.

With services for persistent storage, vector-based retrieval, workflow orchestration and session state, you can design agents that remember what matters, retrieve it when needed and act on it. The diagram below shows a typical memory architecture. At the centre, **Amazon Bedrock** or **Amazon SageMaker AI** provides the LLM, the agent's brain. Around it sit the memory stores and the orchestration layer that make the agent stateful.

> **Think of it like this:**
> A busy clinic. The doctor (the LLM) does the thinking. The notepad on the desk holds what the patient said five minutes ago (**short-term**). The patient-records system holds date of birth, allergies and past visits as neat fields (**structured**). The medical library lets the doctor look up "conditions like this one" by meaning, not exact words (**semantic**). The basement archive keeps every original scan and report (**durable**). And the receptionist decides which of these to pull for each visit (**orchestration**).

{{diagram:3}}

*One brain, several kinds of memory. The LLM sits in the middle; each memory store answers a different question ("what was just said?", "what are the facts?", "what is this similar to?"), and the orchestration layer decides which to ask.*

Step through

##### Trace one question through the AWS memory stack

Pick step 1. The example: an HR assistant is asked "Who on my team knows Python and worked on Project X? Use the shortlist rules we agreed."

- **Step 1.** The HR manager asks: “Who on my team knows Python and worked on Project X? Use the shortlist rules we agreed.”
- **Step 2.** The **orchestration** layer (say, a Strands agent or a LangGraph graph) takes over and decides which memories it needs.
- **Step 3.** **Short-term memory** (DynamoDB, Redis or AgentCore Memory): earlier in this session they said “my team” means the Bangalore data team.
- **Step 4.** **Semantic memory** (OpenSearch, pgvector, Pinecone or Knowledge Bases): it finds the meeting notes where the “shortlist rules” were agreed, even though they're titled “selection criteria”.
- **Step 5.** **Structured memory** (here Neptune): a graph query finds who WORKED_ON Project X and KNOWS Python.
- **Step 6.** Everything is packed into one prompt for the **LLM** on Bedrock or SageMaker AI.
- **Step 7.** The LLM answers with a shortlist that follows the agreed rules, and the user gets an informed, accurate response.

1. 1 The user asks a question
2. 2 The orchestration layer triggers
3. 3 It checks short-term memory for recent context
4. 4 It queries semantic memory (RAG) for relevant documents
5. 5 It may query structured memory for specific user facts
6. 6 All of this is fed to the agent's LLM
7. 7 The LLM generates an informed, context-accurate response

#### Each component, one at a time

##### The agent's LLM

It receives inputs, reasons through problems, and decides which memory to access or what action to take. On AWS this is typically a model accessed through **Amazon Bedrock** (Claude, Amazon Titan or Nova, Meta Llama and others), or an open-weight model such as Llama hosted on **Amazon SageMaker AI**. In this section's labs, the agent uses Claude Sonnet 4.6 (Notebook 1) and Claude Haiku 4.5 (Notebook 2) through Bedrock.

##### Short-term memory (context)

Stores the immediate history of the current interaction, for example the last 10 messages of a chat, so the agent knows what was just discussed and doesn't repeat itself. On AWS:

- **Amazon DynamoDB:** a fast **NoSQL** database for session state and recent chat transcripts.
- **Redis** (Amazon ElastiCache or Amazon MemoryDB): an **in-memory** store for ultra-low-latency access to "hot" session data.
- **Amazon Bedrock AgentCore Memory:** a managed, **serverless** memory service that keeps track of the ongoing conversation for you. You'll use it in the second lab.

##### Structured long-term memory

Factual, relational data in traditional formats. If an agent needs a customer's recent order or a company's inventory, it looks here.

- **Amazon Aurora:** a high-performance **relational (SQL)** database for complex, structured relationships.
- **Amazon DynamoDB:** for massive-scale metadata or historical records that don't need complex joins.
- **Amazon Neptune:** a **graph database**, for when the agent must understand relationships between entities. For example: *"Which employees have worked on Project X and also know Python?"*

{{diagram:4}}

*Graph databases follow relationships. The answer is whoever is linked to both nodes. A relational database can do this with joins; a graph database makes it the natural question to ask.*

##### Semantic long-term memory (the RAG layer)

Stores general knowledge, facts and concepts. It's arguably the most important layer for modern AI, and it powers **retrieval-augmented generation (RAG)**, where relevant passages are searched for and handed to the model with the question. Data is stored as **vectors** (lists of numbers that represent meaning), so the agent finds information by concept rather than exact keywords. Options on AWS:

- **Amazon OpenSearch Service:** a search suite with vector-database capabilities to find relevant document chunks.
- PostgreSQL with **pgvector** (for example on Amazon Aurora or Amazon RDS): a standard database with an extension that stores and searches embeddings.
- **Pinecone:** a specialised third-party vector database built for high-speed semantic search.
- **Amazon Bedrock Knowledge Bases:** a fully managed, serverless option for semantic memory inside Bedrock.

##### Durable storage

The **data lake** where the original, raw source files live before they're processed or indexed into the other memory types. **Amazon S3** is the foundation here: raw PDFs, text files, logs and images that the agent may need to reference or re-process later.

##### Memory orchestration

The logic layer, the connective tissue. It decides when to look in short-term memory and when to query semantic long-term memory.

- **AWS Lambda:** serverless code that runs specific tasks, for example "fetch this user's profile from Aurora".
- **AWS Step Functions:** a workflow orchestrator that stitches multiple tasks into a sequence.
- **Strands Agents SDK:** the agent framework you've used since Section 1. It manages the conversation, tools and memory hooks so you write less plumbing.
- **LangGraph:** a framework for building stateful, multi-step agents as a *graph*. It extends the LangChain ecosystem: instead of a simple linear chain, you design workflows as nodes and edges.

{{diagram:5}}

*Nodes and edges. Each node is one step (call the LLM, execute a tool, retrieve memory, apply business logic). Edges control the flow, including loops, conditional branches and retries. You'll build exactly this loop in the second lab.*

That structure makes LangGraph well suited to complex, multi-turn agents that need planning, reflection or structured decisions. On AWS it can call models on Bedrock or SageMaker AI, keep its state in DynamoDB, Redis or AgentCore Memory, and be deployed on AWS Lambda, containers (Amazon ECS or Amazon EKS), or Amazon Bedrock AgentCore Runtime.

#### Putting it together

| Memory type | What it holds | Typical AWS choices |
| --- | --- | --- |
| Short-term memory | What is happening now | Redis (ElastiCache, MemoryDB), DynamoDB, AgentCore Memory |
| Long-term structured memory | Organised facts | Aurora, DynamoDB, Neptune |
| Long-term semantic memory | Meaning-based recall | OpenSearch, pgvector, Pinecone, Bedrock Knowledge Bases |
| Durable storage | Raw, persistent data | Amazon S3 |
| Orchestration | The glue that connects everything | Strands Agents SDK, LangGraph, Lambda, Step Functions |

> **Where this section's labs sit on that map:**
> **Lab 1** uses Strands as orchestration, Bedrock as the LLM, and Mem0 as long-term semantic memory, stored in a local **FAISS** index while you learn (OpenSearch in production). **Lab 2** uses LangGraph as orchestration and AgentCore Memory as short-term memory.

Try it

##### Pick the right store for each need

0 of 6 answered

**Options:** Short-term · Structured · Semantic · Durable

1. The last 10 messages of the current chat, read on every single turn. **Answer: Short-term.** Hot session data: Redis (in-memory, the fastest), DynamoDB or AgentCore Memory.
2. A customer's order status and delivery address. **Answer: Structured.** Structured facts in rows and fields: Aurora or DynamoDB.
3. Policy paragraphs about “getting money back”, even when they say “refund”. **Answer: Semantic.** Search by meaning, not keywords: a vector store such as OpenSearch, pgvector or Bedrock Knowledge Bases.
4. The original scanned contracts, kept so they can be re-processed later. **Answer: Durable.** Raw files belong in the data lake: Amazon S3.
5. Which engineers worked on Project X and also know Python? **Answer: Structured.** Relationships between entities: structured memory, ideally a graph database such as Neptune.
6. Progress of an agent halfway through a five-step booking. **Answer: Short-term.** Session state for the task in progress: short-term memory.

You can match memory needs to AWS stores.
