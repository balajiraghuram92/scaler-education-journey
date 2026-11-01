# Context management and memory optimisation

## 3.7 Context management and memory optimisation

Remembering everything is easy. Choosing what to put in front of the model, right now, is the real skill.

Effective agent memory stands on three pillars: **context management**, **retrieval strategies** and **memory optimisation**. Context management means deciding what stays in the model's immediate context window (its working memory) and what is offloaded to external storage.

Like a busy executive, an agent can get overwhelmed. Dump 1,000 pages into its context window and it suffers from **context rot**: it becomes less focused, misses details and makes mistakes. So the principle is simple: **treat context as a finite, precious resource**. Smarter models need less hand-holding, but they still do their best work in a curated, **high-signal** environment.

> **Think of it like this:**
> An exam where you're allowed one A4 cheat sheet. Photocopy the whole textbook onto it in tiny print and you'll never find the formula you need. Write only the ten formulas this paper actually tests, and you're fast and accurate. The context window is that one sheet.

The process of choosing what goes into the window is called **context engineering**:

{{diagram:1}}

*Big pool, small window. From a large pool of possible inputs, the agent curates only the most relevant pieces into the limited context window. The model answers or calls a tool; results are stored, summarised or reused later.*

Effective agents succeed not by knowing everything, but by selecting the right context at the right time. For developers, optimising the window rests on three design pillars:

##### System prompts

Strike a balance: specific enough to guide the agent reliably, not so rigid that the system becomes **brittle**.

##### Tools

**Token**-efficient, self-contained, and minimally overlapping, so the agent can choose between them without confusion.

##### Examples (few-shot)

A small set of diverse, representative **few-shot** examples, not a long laundry list of edge cases.

Try it

##### Curate the context window

**Items that can go into the window** (tokens; the first six are relevant to the task):

| Item | Tokens | Relevant to the task |
| --- | --- | --- |
| System prompt (role and rules) | 400 | Yes |
| The user's message | 60 | Yes |
| The user's memories from Mem0 (5 facts) | 150 | Yes |
| Tool definition: websearch | 250 | Yes |
| Tool definition: mem0_memory | 350 | Yes |
| 2 diverse example answers | 600 | Yes |
| 40 edge-case examples | 7,000 | No |
| Full chat history from the last 3 months | 9,500 | No |
| Whole Bangalore city guide (PDF) | 5,500 | No |
| Food-safety regulations (PDF) | 8,000 | No |

**Overflow.** That's … tokens over the window: the request fails, or older content gets cut without you choosing what.

**Missing something.** Without the user's memories (it can't personalise), the websearch tool (it can't find live restaurants), the memory tool (it can't save new preferences), the answer will be generic.

**Fits, but noisy.** Only …% of the window is relevant. This is where context rot starts: the key facts are buried.

**Curated and high-signal.** Everything the task needs, very little it doesn't, in … tokens.

Task: **A user asks, "Find me a low-sodium vegetarian restaurant near Indiranagar."** Tick what goes into a 16,000-token window.

Window used: 0 / 16,000 tokens

Signal: 0% of the window is relevant

#### When a task won't fit in one window

Some jobs are too big for a single context window, for example migrating a large codebase. Four techniques help:

{{diagram:2}}

*Four ways to work beyond one window. Slide it, squeeze it, write things down outside it, or split the work so no single window has to hold everything.*

1. 1 Sliding window The most common, basic form: keep only a fixed window of the most recent tokens or messages. If the window holds 10 messages, message 11 deletes message 1, message 12 deletes message 2, and so on. The active memory slides forward, always keeping the N most recent interactions.
2. 2 Compaction Summarise the conversation so far and restart with a fresh context window holding only the critical decisions and the recent state.
3. 3 Structured note-taking The agent writes to a persistent external file (such as `NOTES.md`, or a memory tool) to track progress across sessions.
4. 4 Sub-agent architectures A lead agent coordinates several specialised sub-agents. Each does the heavy lifting in its own context and returns only a concise summary. You'll build multi-agent systems in the next section.

> **Compaction vs note-taking:**
> Compaction summarises the *story* of the conversation. Note-taking tracks the *state* of the project: "I've completed step 4, step 5 is pending, and the variable name is X."

| Strategy | Implementation | Best for |
| --- | --- | --- |
| Structured note-taking | Writes facts to a file | Complex, multi-hour tasks (coding, research) |
| Sliding window | Deletes the oldest data | Short-term, fast chats |
| Summarisation | Compaction | Staying coherent over long horizons |
| Graph-based | Structured metadata and indexing | Providing high-signal identifiers |
| Agentic RAG | **Just-in-time** context | **Progressive disclosure** through tools |

A sophisticated agent often uses **both**: a sliding window (or compaction) keeps the immediate conversation fluid and fast, while structured notes make sure critical facts, like a bug it found an hour ago, aren't accidentally pushed out by the sliding window.

#### Memory optimisation

The context window is a hard limit on how much text a model can process at once. Memory optimisation makes sure the agent gets the most valuable information without overflowing that window or running up huge costs. Done well, it makes an agent behave less like a forgetful goldfish and more like a thoughtful long-term companion, balancing **what to keep, what to summarise and what to forget**. Some strategies, like sliding window and compaction, serve both context management and memory optimisation.

{{diagram:3}}

*What reaches the model under each strategy. Green blocks are messages the model actually sees; faded ones are gone; purple is a summary; blue are past messages retrieved from a store because they match the current question.*

1. 1 Sequential (keep it all) Every message is fed back to the LLM. Simple, but quickly hits token limits and increases cost.
2. 2 Sliding window Only the last N messages are kept. Fast and relevant, but forgets crucial details from earlier in the chat.
3. 3 Summarisation / compaction Periodically condense history into a short summary. Preserves the gist over long periods, but can lose specific minor details.
4. 4 Retrieval-based (RAG) History lives in an external store such as a vector database. The agent searches it and retrieves only the past facts relevant to the current question. That's exactly what Mem0 did in the lab.

Try it

##### Same chat, five memory strategies

A 12-message chat with a food-delivery agent. In message 2 the user said **"I'm allergic to peanuts."** Now, in message 13, they ask **"Suggest a dessert for tonight."** What does the model get to see?

**The chat (12 messages):**

- U: I want to order dinner tonight.
- U: I'm allergic to peanuts.
- A: Noted. Any cuisine preference?
- U: Something South Indian.
- A: Found 6 restaurants near you.
- U: Only ones under ₹500, please.
- A: Here are 3 options.
- U: Book the dosa place.
- A: Ordered: masala dosa ×2.
- U: Add a filter coffee.
- A: Added. Arriving at 8:10 pm.
- U: Thanks!
- U: Suggest a dessert for tonight.

**Sequential**

- All 12 messages, every turn.
- Context: ≈ 12 messages, growing every turn
- ✓ knows about the peanut allergy
- ✓ knows the ₹500 budget
- **Agent:** “Try payasam made without nuts, under ₹150.”

Correct, but every turn re-sends the whole history. In a long chat this hits the token limit and the cost keeps climbing.

**Sliding window**

- Only messages 9–12.
- Context: 4 messages, fixed
- ✗ knows about the peanut allergy
- ✗ knows the ₹500 budget
- **Agent:** “How about peanut chikki? It's a classic.”

Fast and cheap, but the allergy in message 2 slid out of the window. A dangerous answer.

**Summary**

- A summary of 1–8, plus 9–12.
- Context: summary + 4 messages. Summary: user ordering South Indian dinner tonight; allergic to peanuts; ordered masala dosa ×2 and filter coffee, arriving 8:10 pm.
- ✓ knows about the peanut allergy
- ✗ knows the ₹500 budget
- **Agent:** “Try a nut-free payasam from the same restaurant.”

Safe: the summary kept the allergy. But the minor detail “under ₹500” didn't survive the summary.

**Retrieval (RAG)**

- Only the 2 past messages most similar to “dessert tonight”.
- Context: 2 retrieved messages
- ✓ knows about the peanut allergy
- ✓ knows the ₹500 budget
- **Agent:** “A nut-free payasam under ₹150 would work.”

Precise and cheap. But without recent messages it doesn't know an order is already on its way at 8:10, so it can't offer to add the dessert to it.

**Hybrid**

- Retrieved 2 and 6, plus the last 4.
- Context: 2 retrieved + 4 recent
- ✓ knows about the peanut allergy
- ✓ knows the ₹500 budget
- **Agent:** “Shall I add a nut-free payasam (₹120) to your order arriving at 8:10?”

The production pattern: the window keeps the flow, retrieval brings back the critical older facts.

What the model sees

Result

##### Advanced approaches

Many agents start with these simple techniques, but advanced applications need more. Memory must do more than store old conversations: it must organise information, reduce redundancy, surface what matters most, and scale across long-running interactions. That has led to more sophisticated designs:

##### Memory-augmented transformers

Dedicated memory tokens or scratchpad spaces inside the model to retain key information.

##### Hierarchical memory

Layers organised by immediacy and importance, like a desk, a filing cabinet and an archive.

##### Compression and consolidation

Reduce raw text into embeddings, summaries or clusters of related memories.

##### Graph-based memory networks

Connect memories through entities and relationships, not just a timeline (remember the Neptune example).

##### Strategic forgetting

Remove low-value information on purpose while preserving the most useful knowledge.

| If you're building… | Start with |
| --- | --- |
| A simple chat app | Sliding window |
| A fact-heavy app | Retrieval-based (RAG) memory |
| A complex, long-running app | Hierarchical or graph-based memory |
| A production system | A hybrid: a sliding window for the immediate flow, plus retrieval for long-term facts |

Next, Amazon Bedrock AgentCore Memory gives you managed versions of these ideas, such as automatic extraction and consolidation, and retrieval, without building them yourself.

## 3.8 Amazon Bedrock AgentCore Memory

Mem0 showed you the idea. AgentCore Memory is the managed, production version: short-term and long-term memory, automatic extraction, isolation by user and session, all behind an AWS API.

**Amazon Bedrock AgentCore** is a modular set of capabilities to build, deploy and operate production-grade agents that are secure, scalable, and work with any framework and any model. Your agent can be written with Strands, LangGraph or anything else; AgentCore provides native resources around it:

{{diagram:4}}

*AgentCore is a toolbox, not a framework. You pick the pieces you need. Here we use Memory; the course comes back for Runtime, Gateway and Identity in Section 6, and Policy, Observability and Evaluations in Section 7.*

AgentCore Memory lets agents retain knowledge and learn continuously. Built-in or custom *strategies* automatically extract and store key kinds of memory from every interaction, so agents stay context-aware across sessions. It has four main features:

##### Core infrastructure

Production-ready from day one: secure, managed APIs; **namespaces** to organise or isolate memories; **time-to-live** settings so temporary data expires; and observability for monitoring usage and debugging.

##### Memory management

How information is stored over time: short-term memory for the current interaction, long-term memory for persistent knowledge, **consolidation** to reduce duplication, and **checkpointing** to save progress in multi-step tasks.

##### Memory extraction

Decides what the agent should remember. Built-in or custom strategies capture useful details such as preferences, generate session summaries, and work in the background with no extra code from you.

##### Memory retrieval

Finds the right information when needed: semantic search by meaning rather than exact words, plus filtering by time, category or other conditions.

#### How it's built

Mem0 was a great way to see persistent memory in action: easy to plug in, and clear about how preferences get stored and retrieved. Production systems need more structure: short-term context, long-term knowledge, extraction and user isolation, handled systematically, securely and at scale. AgentCore Memory provides that as a managed architecture for **stateful** agents:

> **Think of it like this:**
> A hospital stay. While you're on the ward, nurses write everything on the bedside chart: every reading, every dose (**short-term memory, raw events**). When you're discharged, a records officer reads that chart and writes a one-page discharge summary with only what matters (**extraction**). That summary goes into your permanent file, indexed so any doctor can find it later (**long-term memory**). Next visit, the doctor reads the summary, not the whole chart.

{{diagram:5}}

*A loop with a filter in it. Everything goes into short-term memory; only what the extraction module judges worth keeping becomes a long-term memory record.*

1. 1 Raw events go to short-term memory During an interaction the agent produces raw events: user messages, tool calls, intermediate actions, system responses. They're written to short-term memory, the agent's temporary working area, which keeps continuity within the active session, like human working memory.
2. 2 The extraction module decides what's worth keeping Instead of copying everything into permanent storage, it reviews the raw events and picks out meaningful signals (preferences, goals, important facts, summaries of what happened) and turns them into structured memory records. This keeps long-term memory from filling up with low-value detail.
3. 3 Records are stored in long-term memory Long-term memory is a vector store, so the agent can later retrieve memories by meaning and relevance, not exact keywords. Over time this becomes a growing body of knowledge that improves personalisation and keeps decisions consistent across sessions.

This tackles one of the biggest challenges in agentic AI: **state management**. Without memory, every interaction is independent. With this design, the agent captures fine-grained activity as events, keeps recent interactions in short-term memory, and its runtime behaviour stays in line with what it has stored.

#### Short-term memory: actors, sessions and events

Short-term memory preserves the immediate conversation, tracks active interactions, and keeps different users and sessions apart. It's organised around three concepts that answer three questions: **who** is interacting, **what** happened, and **which conversation** it belongs to.

{{diagram:6}}

*Who, what, which conversation. The actor scopes the memory to an identity, events record what happened, the session groups them, and two-way sync lets the agent write and read back.*

1. 1 Actor: whose memory is it? Every event belongs to an **actor**: a specific user, or a user–agent combination. This keeps one user's conversation out of another's context, preventing cross-contamination.
2. 2 Events, grouped into a session During the interaction the agent creates **events**: chat messages, or other data as JSON blobs. A **session** represents one conversation or interaction period, so several messages are treated as one ongoing exchange.
3. 3 Synced into short-term memory Short-term memory holds three things: **chat messages** (the conversation history), **session state** (temporary variables, workflow progress) and **checkpoints** (snapshots that let a conversation be resumed). The two-way "sync" arrows mean the agent writes new information in and reads stored context back, so it can continue smoothly, remember what just happened, and recover if interrupted.

> **In one line:**
> **Events** capture what happened, **actors** say who it belongs to, **sessions** say which conversation it was part of, and **short-term memory** holds the active working context that keeps the agent stateful and coherent.

> **You'll see these exact names in Lab 2:**
> The LangGraph checkpointer maps `thread_id` to an AgentCore **session ID** and `actor_id` to an AgentCore **actor ID**. It stores each checkpoint as events in short-term memory.

#### Long-term memory: strategies and namespaces

Short-term memory explains how the agent tracks what's happening *now*. But agents also need to remember facts, preferences and outcomes over much longer periods. AgentCore Memory provides a structured way to extract useful information from ongoing interactions and store it as long-term memory. Two ideas drive it:

- **Memory strategies** decide *what* is worth remembering and how to process it.
- **Namespaces** decide *where* it's filed, so it can be found in the right context later.

Together they move you beyond storing raw conversations to a memory that is selective, structured and searchable.

##### Namespaces

A namespace partitions memory, a bit like folders. You might keep one namespace for user preferences, another for past project details, another for general facts, so the agent never confuses different kinds of information. Their real power is that they let you **zoom in or zoom out**:

{{diagram:7}}

*Paths you can zoom along. A longer path is a narrower scope. For example `/strategy/{strategyId}/actor/{actorId}/session/{sessionId}`. Search at `…/actor/{actorId}` to see everything about one user; add `/session/{sessionId}` to see one conversation; search at `/` to see everything.*

| Level | Holds | Example |
| --- | --- | --- |
| Global `/` | Universal knowledge every agent must follow, regardless of the user | Company-wide compliance rules or security protocols |
| Strategy | Domain expertise, shared across many users but limited to one topic | A medical agent's anatomy facts |
| Actor | User preferences and recurring behaviour, so the agent remembers who you are and how you like to work | "User84 prefers WhatsApp updates" |
| Session | Summaries of specific conversations | Ticket #456, so the agent knows what was said ten minutes ago versus ten months ago |

> **Namespaces are templates:**
> When you configure a strategy you give it a namespace template with placeholders, for example `/users/{actorId}/preferences/` or `/summaries/{actorId}/{sessionId}/`. AgentCore fills in placeholders such as `{actorId}` and `{sessionId}` for each event, so every user's memories land in their own path automatically.

##### Memory strategies

When you create or update an AgentCore Memory, you define one or more strategies. They decide what is retained, how it's structured in namespaces, and how it's processed when events arrive. **If no strategy is configured, no long-term memory is extracted**; you get short-term memory only, which is exactly what Lab 2 uses. There are three types:

##### Built-in

Fully managed extraction for common needs. You pick one and AgentCore does the rest.

##### Built-in with overrides

Limited customisation of a built-in strategy: change its prompt instructions or the Bedrock model it uses, while keeping the managed pipeline and output format.

##### Self-managed

Full control over extraction and memory management. You run your own logic and write the resulting records yourself.

| Built-in strategy | What it keeps | Links back to |
| --- | --- | --- |
| User preference | Preferences, choices and styles ("prefers vegetarian food") | The Mem0 lab |
| Semantic | Facts and knowledge mentioned in conversations | Semantic memory (3.2) |
| Summary | A running summary of each session | Compaction (3.7) |
| Episodic | Interactions as structured episodes (what happened, what was done, how it turned out), plus reflections across episodes | Episodic memory (3.2) |

> **Mix and match:**
> A single memory resource can use built-in and custom strategies at the same time.

##### The memory extraction module

This module turns raw short-term events into useful long-term memory. Based on the selected strategy, it runs **asynchronously**: it extracts important details, merges them with existing knowledge, and indexes the results for semantic search.

{{diagram:8}}

*Extract, consolidate, index. Consolidation looks up similar memories first, so a new fact either becomes a new record, updates an old one, or is skipped as redundant.*

1. 0 Capture, then wait for the trigger Raw events are captured continuously in short-term memory. Instead of storing everything immediately, the extraction module runs in the background when the strategy's trigger fires: after a batch of new messages, or after a short pause in the conversation. New long-term records typically appear within tens of seconds, so don't expect them the instant a message is sent.
2. 1 Extraction Identifies and pulls meaningful information out of the raw interaction stream.
3. 2 Consolidation Merges it with existing knowledge. The module retrieves similar memories and then **adds** new information, **updates** an existing entry, or **skips** it if it's not meaningful or is redundant. An outdated memory isn't silently overwritten; it's marked invalid. The summary strategy has only a consolidation step, because a session summary is already structured content.
4. 3 Embedding and indexing The consolidated memory is converted to embeddings and indexed in long-term vector storage, ready for semantic search.

The result: memory formation that is structured, not duplicated, and efficient, balancing real-time capture with durable, searchable long-term memory.

##### Bringing it all together

Strategies say what kind of knowledge to keep, the extraction module turns raw events into structured records, and namespaces file those records in the right scope. Follow one support conversation from start to finish:

{{diagram:9}}

*Captured raw, kept summarised, found by meaning. The conversation lands in short-term memory as raw events; a strategy and the extraction module turn it into a summary filed under a namespace; later, a semantic search retrieves that summary for the agent.*

Try it

##### Watch short-term events become long-term memory

You are **User84** in session `OrderSupportSess`. The memory has two built-in strategies: summary and user preference.

**Button 1 · Report a problem**

- **User84:** Hi, I'm having trouble with my order #12345
- **Assistant:** Let me look up your order.
- **Tool:** lookup_order(order_id="12345")

Three raw events written to **short-term memory**. Nothing in long-term memory yet: extraction runs in the background, not instantly.

**Button 2 · State a preference**

- **User84:** Please send updates on WhatsApp, not email.
- **Assistant:** Sure, WhatsApp it is.

Two more events. The `userPreference` strategy will care about this one.

**Button 3 · Change your mind**

- **User84:** Actually, email updates are fine now.
- **Assistant:** Got it, I'll use email.

A changed preference. Run extraction to see consolidation **update** instead of adding a duplicate.

**Run extraction**

- **1 Extraction.** Reading the new events and pulling out meaningful signals: “User84 had an issue with order #12345. The assistant looked up the order details to help resolve it.”, “Prefers order updates on WhatsApp, not email”.
- **2 Consolidation.** Retrieved similar existing memories and decided: ADD summary, ADD preference, UPDATE preference (the WhatsApp one is marked INVALID), or NO-OP (summary already up to date). If nothing is worth keeping: skip, nothing new.
- **3 Embedding and indexing.** Turning the records into vectors and indexing them in long-term storage.
- Done. New long-term records are filed under their **namespaces**. In the real service this background work typically takes tens of seconds.

Namespaces used: `/summaries/User84/OrderSupportSess/` and `/users/User84/preferences/`. Records: “Prefers order updates on WhatsApp, not email”, then “Prefers order updates by email”, which marks the earlier one INVALID.

**Ask: "What happened with my order?"**

- **Semantic search in long-term memory** for “What happened with my order issue?” → best match in `/summaries/User84/OrderSupportSess/`: “User84 had an issue with order #12345. The assistant looked up the order details to help resolve it.” The agent answers from this summary, even in a brand-new session.
- Or, if extraction has not run: no matching records. Long-term memory is empty until extraction has run, so the agent would have to ask again.

States shown: (no events yet), (no long-term records yet), and "No new events since the last extraction. Send a message first." Start with button 1.

You are **User84** in session `OrderSupportSess`. The memory has two built-in strategies: summary and user preference.

Ask: "What happened with my order?"

1 Extraction 2 Consolidation 3 Embedding and indexing

Short-term memory (events)

Long-term memory (records by namespace)

Start with button 1.
