# Why agents need memory

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

LLM, the brain Short-term memory, tools Long-term memory, storage Orchestration, extraction Privacy, limits, problems The agent itself

Section 3: Agents that remember

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 3 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Agents-that-remember-main.zip)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### Agents that remember

Section 3. Your agent can think and act. Now it learns to remember: what was just said, who it's talking to, and what it learned last week. You'll build a personal assistant with Mem0 and a LangGraph agent whose memory lives in Amazon Bedrock AgentCore.

Folder `section-03-agent-memory` Notebooks `01_personalized_memory_mem0` `02-langgraph-agentcore-memory/math_agent_with_checkpointing` Models: Claude Sonnet 4.6, Claude Haiku 4.5, Titan Text Embeddings v2

{{diagram:1}}

*The journey in this section. We start with the idea of memory, build it ourselves with Mem0, then hand the hard parts to a managed service.*

## 3.0 Why agents need memory

In Section 2 your agent learned to reason and act with tools. But a tool-using agent that can't remember earlier conversations, your preferences or what it did last time still starts every chat from zero.

Without memory, every interaction feels transactional. With memory, an agent can recall what you asked a minute ago, keep important facts across sessions, adapt to your preferences, and stay on track in long-running work. Memory is what turns a reactive assistant into a dependable collaborator.

This is the natural next step after tools: **tools let an agent act; memory lets it learn from history and keep context.** Together they're the foundation of agents that feel coherent, useful and increasingly personal.

> **Think of it like this:**
> Your neighbourhood kirana uncle versus a vending machine. The vending machine serves everyone the same way, every time. The kirana uncle remembers you buy toned milk, asks if your mother's knee is better, and keeps your usual brand aside. Same transaction, completely different experience. Memory is the difference.

#### What you'll learn here

1. What agent memory is, and why it matters
2. Types of memory: short-term (working) and long-term
3. Implementing memory with AWS services
4. Building a personalised agent with Strands, Mem0, Amazon Bedrock and web search
5. Context management and memory optimisation
6. Amazon Bedrock AgentCore Memory: short-term and long-term
7. Hands-on: a math agent with AgentCore Memory and LangGraph

#### Before you start

1. 1 A working Strands setup from Sections 1 and 2 Virtual environment, AWS credentials, and `check_setup.py` passing.
2. 2 Basic Python functions and classes
3. 3 AWS permissions Notebook 1 calls Bedrock only (Claude for the agent, Claude Haiku and Titan embeddings for Mem0). Notebook 2 also needs AgentCore Memory: `bedrock-agentcore:CreateMemory`, `GetMemory`, `ListMemories`, `DeleteMemory`, `CreateEvent`, `ListEvents`, `GetEvent`, `DeleteEvent`. The course policy `setup/iam-policy-course.json` covers them.
4. 4 REST and JSON (helpful, not required)
5. 5 An IDE VS Code, JupyterLab or Kiro, whichever you used in Section 1.

| Notebook | What it covers | Where on this page |
| --- | --- | --- |
| `01_personalized_memory_mem0.ipynb` | Long-term, per-user memory with Mem0. Each agent's memory tool is bound to one user in code, so users stay isolated even against prompt injection. Plus an admin "super-agent" with an explicit cross-user tool. | 3.6 |
| `02-langgraph-agentcore-memory/math_agent_with_checkpointing.ipynb` | Short-term (session) memory for a LangGraph agent, using Amazon Bedrock AgentCore Memory as the checkpointer | 3.9 |

```pseudo title="terminal"
// Notebook 1
RUN pip install -r requirements.txt
// Notebook 2
RUN pip install -r 02-langgraph-agentcore-memory/requirements.txt
```

```bash reveal title="terminal"
# Notebook 1
pip install -r requirements.txt

# Notebook 2
pip install -r 02-langgraph-agentcore-memory/requirements.txt
```

> **What each notebook leaves behind:**
> Notebook 1 stores memories **locally** (a FAISS index on disk) and uses Bedrock for embeddings (Titan v2) and fact extraction (Claude Haiku 4.5): nothing to clean up in AWS. Notebook 2 creates an AgentCore Memory resource and **deletes it in its last cell**.

## 3.1 What is agent memory?

**Agent memory** is an agent's ability to keep past information so it can maintain context and make better decisions.

Picture a chat with a travel agent. You ask, *"What are good places to visit in Bangalore?"* It replies, *"Lalbagh Botanical Garden is a favourite."* You follow up: *"What's the best time to visit it?"* The agent knows "it" means Lalbagh and answers, *"Early morning, and during the Republic Day or Independence Day flower shows."* That small "it" only works because the agent remembered the previous turn.

Try it

##### The same follow-up, with and without memory

**Without memory**

- **You:** What are good places to visit in Bangalore?
- **Agent:** “Lalbagh Botanical Garden is a favourite.”
- **You:** What's the best time to visit it?
- **Agent:** “Could you tell me which place you mean by ‘it’? I don't have the earlier part of our conversation.”

**With memory**

- **You:** What are good places to visit in Bangalore?
- **Agent:** “Lalbagh Botanical Garden is a favourite.”
- **You:** What's the best time to visit it?
- **Memory:** Previous turn: we were talking about Lalbagh Botanical Garden.
- **Agent:** “Lalbagh is best early in the morning, and during the Republic Day or Independence Day flower shows.”

{{diagram:2}}

*Stateless vs memory-enabled. On the left, each new conversation is a stranger. On the right, the agent writes what's useful during one conversation and reads it back in the next.*

On the left the agent is **stateless**: a request comes in, a response goes out, and a new conversation remembers nothing. On the right the agent is connected to a memory layer. It **writes** useful information during interactions and **reads** it back later, so when you return it can use your past preferences and history.

| Feature | Agents without memory | Agents with memory |
| --- | --- | --- |
| Context | Reset every time a session ends | Carried forward across sessions |
| Personalisation | Low; generic responses | High; tailored to the user's history |
| Efficiency | User must repeat information | Agent remembers and builds on past information |
| User experience | Feels like talking to a stranger every time | Feels like a continuous relationship with an assistant |

#### Why memory matters

1. 1 Contextual intelligence Not just storing data, but understanding the why and how behind a request. By spotting patterns in how you work, the agent answers in a way that fits your situation and sees the bigger picture of your project instead of treating each prompt as isolated.
2. 2 User preferences The agent builds a profile of how you like to work: a professional tone, a certain format, constraints you mentioned before. You don't have to repeat "always keep it under 100 words" in every new chat.
3. 3 Knowledge retention Persistent memory that grows over time. Instead of staying static, the agent becomes a better problem-solver the more you use it, remembering complex problems you solved together and using them next time.

## 3.2 Types of agent memory

Memory isn't one thing. An agent needs a scratchpad for the conversation in front of it, and a longer-lasting store for what it should still know next week.

Language models on their own are largely **stateless**: they only know the current prompt and whatever fits in their **context window**. Agents need ways to keep and use information over time. A helpful way to think about this comes from cognitive architectures such as **CoALA**, which organise an agent around reasoning, action and memory. The key idea for us: an agent may need **short-term memory** for the current interaction, **long-term memory** for stable knowledge across sessions, and **episodic memory** to recall past experiences.

{{diagram:3}}

*Short-term and long-term, and three kinds of long-term. Everything the agent experiences is processed into memory, and everything in memory exists to be retrieved when the agent needs to decide or respond.*

#### Short-term memory, or working memory

This is the agent's scratchpad: whatever it's focusing on right now. It's why a chatbot can feel like a natural conversation partner. Instead of treating each message as brand new, it keeps track of the current session, so its answers follow what's already been said. Without it, the agent would forget your question the moment you asked a follow-up.

Technically it's handled by the context window or a **rolling buffer**: a fixed amount of space. As the conversation grows, the oldest information is pushed out to make room for the new.

The catch: short-term memory keeps *one* interaction smooth but saves nothing once the session ends. On its own, it can't learn about you or remember your preferences over time.

> **Think of it like this:**
> A whiteboard in a meeting room. Perfect while the meeting is on; everyone can see what was just said. Run out of space and you wipe the oldest corner. When the meeting ends, the cleaner wipes the whole board.

Try it

##### Shrink the window and watch the agent forget

**Conversation (10 messages, oldest first):**

- **You:** Plan a weekend trip to Mysuru for me.
- **Agent:** Sure. Which dates?
- **You:** The 14th and 15th of next month.
- **Agent:** Noted: 14th and 15th.
- **You:** I prefer trains over buses.
- **Agent:** The Shatabdi from Bangalore takes about 2 hours.
- **You:** Find a hotel near the palace.
- **Agent:** Here are three hotels within 1 km.
- **You:** Book the second one.
- **Agent:** Done. Booked for two nights.

**Window of 7 or more messages:** **Remembers.** “You said the 14th and 15th of next month.”

**Window of 6 messages or fewer:** **Forgot.** “I'm not sure which dates you mentioned. Could you tell me again?” The message with the dates has slid out of the window.

Messages the window can hold = 10 10

The conversation so far

Next message from the user

**User:** "Remind me, which dates did I say?"

Agent's answer

#### Long-term memory

Long-term memory takes the agent beyond a single conversation. It can remember your history, understand complex facts and build expertise from everything it has learned. Two capabilities make that possible:

- **Permanent storage.** Unlike short-term memory, it doesn't reset. It's built on databases or **vector embeddings**, which also capture how pieces of information relate, and it can hold huge amounts of history.
- **Personalisation and history.** A support agent with long-term memory remembers you had a specific problem three months ago. Instead of asking the same basic questions again, it tailors its answer to your history: faster, more personal, more helpful.

The CoALA framework splits long-term memory into three types:

{{diagram:4}}

*Experienced, done, known. Episodic memory captures what the agent has lived through, procedural memory how it does things, semantic memory what it knows.*

##### Episodic memory

**Episodic memory** lets an agent look back at its own history, like a person remembering a specific meeting or conversation rather than general facts. With it, the agent can do *case-based reasoning*: facing a new problem, it recalls a similar past situation, checks whether what it did then worked, and makes a better decision now. To do that, it keeps a structured log of each episode:

{{diagram:5}}

*An episode is a mini case study. Next time someone reports a double charge, the agent can recall this episode and what worked.*

For example, an AI financial advisor with episodic memory remembers your specific investment choices over several years. It doesn't just know the stock market in general; it knows *your* history, and recommends accordingly.

##### Semantic memory

**Semantic memory** is the agent's internal library of structured facts: definitions, formulas, rules. In simple terms, episodic memory lets an agent remember a specific conversation with you; semantic memory lets it know what the words in that conversation mean. Agents implement it with knowledge bases, symbolic AI or vector embeddings, which organise large amounts of data so the right fact can be found almost instantly. It's essential wherever domain expertise matters:

- **Medical tools:** recalling symptoms and drug interactions
- **Business systems:** company-wide policies and data
- **Legal assistants:** searching thousands of past cases and precedents to give fact-based answers

Semantic memory gives an agent a stable base of world knowledge, so it reasons from facts and rules instead of guessing from patterns.

##### Procedural memory

**Procedural memory** is the agent's ability to *do*: skills, workflows and action patterns such as how to use a tool, a reasoning strategy, or a step-by-step routine. It persists across sessions and improves with experience. Think of learning to ride a bike: at first you think about every step (balance, pedal, steer); later you just ride.

> **In one line:**
> Semantic memory is *what the agent knows*, episodic memory is *what it has experienced*, and procedural memory is *how it gets things done*.

Try it

##### Which kind of memory is this?

0 of 8 sorted

**Options:** Episodic · Semantic · Procedural · Short-term

1. Last Tuesday a customer said her order arrived damaged; the agent refunded her and she was happy with the outcome. **Answer: Episodic.** A specific past event with an action and an outcome: an episode.
2. Mumbai is the capital of Maharashtra. **Answer: Semantic.** A general fact that's true regardless of any conversation: semantic.
3. To file an expense claim: upload the bill, choose a cost centre, then submit for approval. **Answer: Procedural.** A routine for getting something done: procedural.
4. Two messages ago the user said “make it shorter”. **Answer: Short-term.** Only matters inside this conversation: short-term, working memory.
5. Last quarter the agent suggested index funds to this client, and the portfolio grew 8%. **Answer: Episodic.** A past decision and its result for a specific person: episodic, the basis of case-based reasoning.
6. Our refund policy allows returns within 30 days. **Answer: Semantic.** A stable business rule: semantic memory, the agent's internal library.
7. Always call the search tool before answering questions about prices. **Answer: Procedural.** A learned way of working with tools: procedural.
8. Earlier in this chat the user picked the 7 pm show. **Answer: Short-term.** Part of the current session's context: short-term.

You can tell experienced, known, how-to and right-now apart.

Feedback after each answer: **Yes.** when it is right, or **Not quite.** The correct answer is **Episodic.** (the answer for that item), followed by its explanation.
