# Glossary

## A–Z Glossary

Every underlined word on this page, in one place.

© 2026 Shivank Agrawal, Future with Shivank. Agentic AI on AWS, Section 3. Course code is provided under the MIT License.

AWS service names, tool names and library versions change often. When something here differs from what you see, the current documentation wins.

- **Agent memory** — An agent's ability to keep past information (what was said, who you are, what worked before) so it can keep context and make better decisions.
- **Stateless** — Keeps nothing between requests. Each call starts from zero, like a vending machine that serves everyone the same way.
- **Stateful** — Keeps state between steps or requests, so it can carry on where it left off.
- **Context window** — The maximum amount of text (measured in tokens) a model can read in one go: the prompt, the history, tool results and its answer.
- **Token** — The unit models read and write: a word or piece of a word. Context limits and prices are counted in tokens.
- **CoALA** — Cognitive Architectures for Language Agents: a research framework that describes agents in terms of memory, reasoning and action, and splits long-term memory into episodic, semantic and procedural.
- **Rolling buffer** — A fixed-size list where adding a new item pushes out the oldest one. Short-term memory often works this way.
- **Embedding (vector)** — A list of numbers that captures the meaning of a piece of text. Texts with similar meanings get similar vectors, which makes search by meaning possible.
- **Episodic memory** — Memory of specific past events and experiences, such as a particular conversation, what was done and how it turned out.
- **Semantic memory** — Memory of general facts, definitions and rules that don't depend on any particular event.
- **Procedural memory** — Memory of how to do things: skills, routines and workflows that improve with practice.
- **Multi-tenancy** — One system serving many separate customers (tenants). The risk is one tenant's data showing up for another.
- **Precision and recall** — Precision: how many of the results returned are actually relevant. Recall: how many of the relevant items were found at all.
- **NoSQL database** — A database that doesn't use fixed relational tables, often storing items as key-value pairs or documents. Fast and easy to scale. DynamoDB is one.
- **In-memory store** — A database that keeps data in RAM instead of on disk, so reads and writes take well under a millisecond. Redis is one.
- **Serverless** — You use the service without managing any servers. AWS handles capacity and scaling, and you pay for what you use.
- **Relational (SQL) database** — Stores data in tables of rows and columns linked by keys, queried with SQL. Great for structured facts and joins.
- **Graph database** — Stores things as nodes and the relationships between them as edges, so questions like "who is connected to both X and Y?" are natural to ask.
- **RAG (retrieval-augmented generation)** — Search a knowledge store for passages relevant to the question, then give them to the model with the question so the answer is grounded in real data.
- **pgvector** — An extension for PostgreSQL that adds a vector column type and similarity search, so an ordinary database can store and search embeddings.
- **Data lake** — A central store for raw data in its original format (PDFs, logs, images, text), kept until it's needed. Usually built on Amazon S3.
- **FAISS** — An open-source library for fast similarity search over vectors. Lab 1 uses it as a small vector store saved on your disk.
- **Mem0** — An open-source memory layer for AI agents. It extracts facts from conversations, stores them as searchable memories per user, and retrieves them later.
- **Global inference profile** — A model ID starting with global. that lets Bedrock route your request to whichever AWS Region has capacity, for better availability.
- **Shim** — A small piece of code placed between two components to make them fit together, for example by changing a request before it's sent.
- **Prompt injection** — Text written to trick a model into ignoring its instructions, such as "ignore your rules" or "I give you all permissions".
- **Context rot** — The drop in accuracy when a model's context is stuffed with too much or irrelevant material: it loses focus, misses details and makes mistakes.
- **High-signal** — Information that is directly useful for the task, with little noise around it.
- **Context engineering** — Deliberately choosing what goes into the model's context window (instructions, tools, examples, memories, documents) so it has exactly what it needs.
- **Brittle** — Breaks easily when something slightly unexpected happens. Over-rigid prompts make agents brittle.
- **Few-shot examples** — A handful of worked examples included in the prompt so the model can copy the pattern.
- **Just-in-time context** — Loading information only at the moment it's needed (for example with a search tool) instead of putting everything in the prompt up front.
- **Progressive disclosure** — Revealing information step by step as the agent asks for it, rather than all at once.
- **Amazon Bedrock AgentCore** — A set of managed AWS services for running agents in production: Runtime, Memory, Gateway, Identity, built-in tools, Policy, Observability and Evaluations. Works with any framework and model.
- **Namespace** — A path-like label, such as /users/{actorId}/preferences/, that files long-term memory records so they can be stored, isolated and searched by scope.
- **Time-to-live (TTL)** — An expiry time after which stored data is deleted automatically.
- **Consolidation** — Merging newly extracted information with existing memories: add it, update an older memory, or skip it as redundant.
- **Checkpoint** — A saved snapshot of an agent's state at a point in time, so it can resume from exactly there later.
- **Checkpointer** — The LangGraph component that saves and loads graph state (checkpoints) to a storage backend after every step.
- **Actor** — In AgentCore Memory, the identity a memory belongs to: a user, or a user-and-agent pair.
- **Event** — In AgentCore Memory, one recorded item in a session: a conversational message (role and text) or a blob of JSON.
- **Session** — In AgentCore Memory, one conversation or interaction period that groups related events.
- **Asynchronous** — Runs in the background without making the caller wait. Your agent keeps chatting while extraction happens.
- **Converse API** — Amazon Bedrock's single, consistent API for chatting with any supported model, including tool use.
- **Run config** — A dictionary passed to a LangGraph call with per-call settings. Its configurable section carries IDs like thread_id and actor_id.
