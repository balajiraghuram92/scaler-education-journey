# Lab: LangGraph + AgentCore Memory

## 3.9 Lab: LangGraph + AgentCore Memory

A parent wants a math helper to practise sums with their child. We'll build a LangGraph agent that does multi-step calculations and remembers the conversation, with its memory stored in AgentCore.

Unlike a one-off question and answer, this agent uses AgentCore Memory's **checkpointing** to keep a running context. It can build on earlier calculations and remember the flow of the conversation across turns, even if your notebook restarts.

> **Think of it like this:**
> A video game with cloud saves. Every time you finish a level, the game saves to the cloud (a **checkpoint**). Switch off the console, pick up a different one, sign in, and you continue from the exact same spot. Different save slots (sessions) never mix. The `AgentCoreMemorySaver` is the cloud-save button for a LangGraph agent.

{{diagram:1}}

*Orchestration and persistence, separated. LangGraph runs the reasoning and tools; `AgentCoreMemorySaver` bridges to AgentCore Memory, where state and checkpoints are stored durably. That split is what makes the agent multi-session and production-grade.*

##### How the integration works

1. 1 AgentCore Memory is LangGraph's checkpointer backend A LangGraph **checkpointer** decides where graph state is saved. Here, it's AgentCore Memory.
2. 2 State is saved and loaded at every step, automatically You don't write save or load code. Each node that runs produces a new checkpoint.
3. 3 Many sessions and actors at once Each `thread_id` is its own session, and each `actor_id` its own identity, so many users and conversations can share one memory resource without mixing.

#### Run the notebook: `02-langgraph-agentcore-memory/math_agent_with_checkpointing.ipynb`

```pseudo title="cell 1"
RUN %pip install -q -r requirements.txt   // install the packages, quietly, into this kernel
```

```python reveal title="cell 1"
%pip install -q -r requirements.txt
```

This folder has its own `requirements.txt`: `langchain`, `langchain-aws`, `langgraph`, `langgraph-checkpoint-aws` (which provides `AgentCoreMemorySaver`) and `bedrock-agentcore` (which provides `MemoryClient`). If pip upgraded anything, restart the kernel before continuing.

```pseudo title="cell 2: imports"
SET MODEL_ID = BEDROCK_MODEL_ID from the environment, or "global.anthropic.claude-haiku-4-5-20251001-v1:0"
SET REGION = AWS_REGION, else AWS_DEFAULT_REGION, else "us-east-1"
PRINT "Model: " + MODEL_ID + " | Region: " + REGION
```

> **Imported:**
> - `os` Python standard library: reads the model and region settings from environment variables.
> - `MemoryClient` from `bedrock_agentcore.memory`, package bedrock-agentcore: the client for the AgentCore Memory API, used to create and delete the memory resource.
> - `create_agent` from `langchain.agents`: builds a ready-made tool-calling agent as a LangGraph graph.
> - `init_chat_model` from `langchain.chat_models`: loads the Claude model from Amazon Bedrock as a chat model.
> - `tool` from `langchain.tools`: turns a Python function into a tool the model can call.
> - `AgentCoreMemorySaver` from `langgraph_checkpoint_aws`, package langgraph-checkpoint-aws: the checkpointer that saves agent state to AgentCore Memory.

```python reveal title="cell 2: imports"
import os

from bedrock_agentcore.memory import MemoryClient
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph_checkpoint_aws import AgentCoreMemorySaver

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
print(f"Model: {MODEL_ID} | Region: {REGION}")
```

The model is Claude Haiku 4.5: fast and inexpensive, plenty for tool-driven arithmetic.

##### Create (or reuse) the AgentCore Memory resource

```pseudo title="cell 3"
SET client = MemoryClient for REGION
SET memory = client.create_or_get_memory named "MathLanggraphAgent"   // create it, or reuse it if it already exists
SET memory_id = the "id" field of memory
PRINT "Memory ID:", memory_id, and the status
```

```python reveal title="cell 3"
client = MemoryClient(region_name=REGION)
memory = client.create_or_get_memory(
    name="MathLanggraphAgent",
    description="Short-term memory for the LangGraph math agent",
)
memory_id = memory["id"]
print("Memory ID:", memory_id, "| status:", memory.get("status"))
```

1. a `MemoryClient(region_name=REGION)` A client for the AgentCore Memory API in your region.
2. b `create_or_get_memory(...)` Creates the memory resource named `MathLanggraphAgent` the first time and waits until it's **ACTIVE**. Run the notebook again and it simply reuses the existing one. No extraction strategies are passed, because this lab only needs short-term memory.
3. c `memory_id` The resource's unique ID. Everything else in the notebook refers to the memory by this ID.

{{diagram:2}}

*Your memory resource in the console. A schematic of the AgentCore Memory list after cell 3. The ID ends in a random suffix; the status starts as Creating and becomes Active, which is what `create_or_get_memory` waits for.*

##### Configure the checkpointer and the model

```pseudo title="cell 4"
SET checkpointer = AgentCoreMemorySaver for memory_id in REGION   // saves agent state in AgentCore Memory
SET llm = a chat model for MODEL_ID, called through the Bedrock Converse API in REGION
```

```python reveal title="cell 4"
checkpointer = AgentCoreMemorySaver(memory_id, region_name=REGION)
llm = init_chat_model(MODEL_ID, model_provider="bedrock_converse", region_name=REGION)
```

1. a `AgentCoreMemorySaver(memory_id, ...)` A checkpointer that stores the agent's state in this AgentCore Memory resource: conversation progress, intermediate state and checkpoints, so the agent can resume instead of starting from scratch.
2. b `init_chat_model(..., model_provider="bedrock_converse")` Loads the model from Amazon Bedrock through the **Converse API** in your region, as a LangChain chat model.

##### Math tools

```pseudo title="cell 5"
DEFINE add(a, b) as a tool:           // the docstring tells the model what the tool does
    RETURN a + b
DEFINE multiply(a, b) as a tool:
    RETURN a * b
SET tools = [add, multiply]
```

```python reveal title="cell 5"
@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b

tools = [add, multiply]
```

LangChain's `@tool` works like Strands' `@tool` from Section 2: the function name, type hints and docstring become the tool's description for the model.

##### Build the agent with the AgentCore Memory checkpointer

```pseudo title="cell 6"
CREATE graph = an agent with:
    model = llm
    tools = tools
    system prompt = "You are a helpful assistant. Use the tools for every calculation."
    checkpointer = checkpointer      // saves the agent's state after every step
// the last line draws the graph in the notebook
```

```python reveal title="cell 6"
graph = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant. Use the tools for every calculation.",
    checkpointer=checkpointer,
)
graph
```

`create_agent` builds a ready-made tool-calling agent as a LangGraph graph. Passing `checkpointer=checkpointer` is the single line that gives it memory. The system prompt insists on tools for every calculation, because LLMs are unreliable at big-number arithmetic. Putting `graph` on the last line makes the notebook draw it:

{{diagram:3}}

*The graph `create_agent` builds. A request enters at `__start__`, the model node either finishes or routes to the tools node, and tool results flow back to the model. Dashed edges are conditional. The checkpointer saves the state behind the scenes.*

##### Run it

At run time, LangGraph takes a **config** with values that belong to this call, such as user and session IDs. The AgentCore checkpointer needs two of them:

| LangGraph config key | Becomes in AgentCore | Meaning |
| --- | --- | --- |
| `thread_id` | `session_id` | One conversation thread |
| `actor_id` | `actor_id` | The user, agent, or any other identity the memory belongs to |

```pseudo title="cell 7"
SET config = thread_id "session-1" (the session), and actor_id "react-agent-1" (the identity)
SET inputs = one user message: "What is 1337 times 515321? Then add 412 and return the value to me."
FOR EACH chunk the graph streams for inputs and config:   // "updates" mode: one chunk per finished step
    PRINT chunk
```

```python reveal title="cell 7"
config = {
    "configurable": {
        "thread_id": "session-1",  # REQUIRED: maps to AgentCore session_id
        "actor_id": "react-agent-1",  # REQUIRED: maps to AgentCore actor_id
    }
}

inputs = {"messages": [{"role": "user", "content": "What is 1337 times 515321? Then add 412 and return the value to me."}]}

for chunk in graph.stream(inputs, stream_mode="updates", config=config):
    print(chunk)
```

`stream_mode="updates"` prints one chunk each time a node finishes, keyed by the node's name, so you watch the agent think, call a tool, get a result, and continue:

```text title="outputillustrative, shortened with …"
{'model': {'messages': [AIMessage(content=[{'type': 'text', 'text': "I'll calculate 1337 × 515321, then add 412 to the result."}, {'type': 'tool_use', 'name': 'multiply', 'input': {'a': 1337, 'b': 515321}, …}], …, tool_calls=[{'name': 'multiply', 'args': {'a': 1337, 'b': 515321}, …}], usage_metadata={'input_tokens': 665, 'output_tokens': 92, …})]}}
{'tools': {'messages': [ToolMessage(content='688984177', name='multiply', …)]}}
{'model': {'messages': [AIMessage(content=[… 'name': 'add', 'input': {'a': 688984177, 'b': 412} …])]}}
{'tools': {'messages': [ToolMessage(content='688984589', name='add', …)]}}
{'model': {'messages': [AIMessage(content='The answer is **688,984,589**. …')]}}
```

Read it as a story: the model plans and calls `multiply`; the tool returns 688,984,177; the model calls `add` with that result and 412; the tool returns 688,984,589; the model answers. Every one of those steps was saved as a checkpoint.

##### Inspect the saved state

```pseudo title="cell 8"
FOR EACH message in the latest saved state for config:
    PRINT the message type (human, ai or tool), a colon, and the message text
    PRINT a line of 40 equals signs
```

```python reveal title="cell 8"
for message in graph.get_state(config).values.get("messages"):
    print(f"{message.type}: {message.text}")
    print("=" * 40)
```

`graph.get_state(config)` loads the latest checkpoint for this actor and session from AgentCore Memory. `message.type` is `human`, `ai` or `tool`; `message.text` is its plain text.

```text title="outputillustrative"
human: What is 1337 times 515321? Then add 412 and return the value to me.
========================================
ai: I'll calculate 1337 × 515321, then add 412 to the result.
========================================
tool: 688984177
========================================
ai: Now I'll add 412 to that result.
========================================
tool: 688984589
========================================
ai: The answer is **688,984,589**.

To break it down:
- 1337 × 515,321 = 688,984,177
- 688,984,177 + 412 = **688,984,589**
========================================
```

##### Checkpoint history

```pseudo title="cell 9"
FOR EACH checkpoint in the saved history for config:   // newest first
    PRINT "Checkpoint", its checkpoint_id, and the number of messages in its state
```

```python reveal title="cell 9"
for checkpoint in graph.get_state_history(config):
    print(
        f"Checkpoint {checkpoint.config['configurable']['checkpoint_id']} "
        f"— messages in state: {len(checkpoint.values.get('messages', []))}"
    )
```

```text title="outputillustrative IDs"
Checkpoint 1f0b2e7a-91c4-6d3e-8005-… — messages in state: 6
Checkpoint 1f0b2e7a-6a12-6f08-8004-… — messages in state: 5
Checkpoint 1f0b2e79-f3d0-6b7a-8003-… — messages in state: 4
Checkpoint 1f0b2e79-c855-61e2-8002-… — messages in state: 3
Checkpoint 1f0b2e79-5e0b-6c94-8001-… — messages in state: 2
Checkpoint 1f0b2e79-3a7f-6a10-8000-… — messages in state: 1
Checkpoint 1f0b2e79-3a6c-6e55-bfff-… — messages in state: 0
```

Most recent first. Each node run added a message and a checkpoint, so you can see the whole run as a series of snapshots, like save points in a game. LangGraph can even resume or "time-travel" from any of them.

##### Memory persistence: continue the same session

```pseudo title="cell 10"
SET inputs = one user message: "What were the first calculations I asked you to do?"
// the same config as cell 7, so the same session-1 and its saved history
FOR EACH chunk the graph streams for inputs and config:
    PRINT chunk
```

```python reveal title="cell 10"
inputs = {"messages": [{"role": "user", "content": "What were the first calculations I asked you to do?"}]}

for chunk in graph.stream(inputs, stream_mode="updates", config=config):
    print(chunk)
```

```text title="outputillustrative, shortened"
{'model': {'messages': [AIMessage(content='The first calculations you asked me to do were:\n\n1. **Multiply** 1337 × 515321\n2. **Add** 412 to the result\n\nThese were part of a single request; the final value was 688,984,589.', …)]}}
```

We only sent the new question. The checkpointer loaded the earlier messages for `session-1` from AgentCore Memory before the model ran, so the agent could answer from stored context.

##### Session isolation: a new session starts empty

```pseudo title="cell 11"
SET config = thread_id "session-2" (a new session), and actor_id "react-agent-1" (the same actor)
SET inputs = one user message: "What values did I ask you to multiply and add?"
FOR EACH chunk the graph streams for inputs and config:
    PRINT chunk
```

```python reveal title="cell 11"
config = {
    "configurable": {
        "thread_id": "session-2",  # new session
        "actor_id": "react-agent-1",  # same actor
    }
}

inputs = {"messages": [{"role": "user", "content": "What values did I ask you to multiply and add?"}]}
for chunk in graph.stream(inputs, stream_mode="updates", config=config):
    print(chunk)
```

```text title="outputillustrative"
{'model': {'messages': [AIMessage(content="I don't have any record of earlier calculations in this conversation. Which numbers would you like me to multiply and add?", …)]}}
```

Same actor, different `thread_id`, so a different AgentCore session, with no checkpoints yet. Short-term memory is scoped to the session. Remembering things *across* sessions is the job of long-term memory strategies, from 3.8.

Try it

##### Sessions, checkpointers and kernel restarts

**Checkpointer options**

- **AgentCoreMemorySaver:** `checkpointer=AgentCoreMemorySaver(memory_id, …)`
- **In-process (InMemorySaver):** `checkpointer=InMemorySaver()`: state lives in this Python process only.
- **No checkpointer:** `create_agent(…)` with no checkpointer.

**Session (`thread_id`):** session-1, session-2. Selecting one logs: Switched to `thread_id="…"`.

**Stored checkpoints**

- **Stored in:** AgentCore Memory (in AWS), or Python process memory (this kernel).
- Nothing is saved. Without a checkpointer every call starts with an empty state.
- `session-1` · actor `react-agent-1`: … messages, … checkpoints ← current

**Ask: 1337 × 515321, then + 412**

- **You:** What is 1337 times 515321? Then add 412.
- **Tools:** multiply(1337, 515321) → 688,984,177 · add(688984177, 412) → 688,984,589
- **Agent:** The answer is 688,984,589.

**Ask: what did I ask first?**

- **You:** What were the first calculations I asked you to do?
- **Agent (loaded):** Loaded … earlier messages from `session-1`: you asked me to multiply 1337 × 515321 and then add 412 (result 688,984,589).
- **Agent (nothing saved):** I don't have any earlier messages. (No checkpointer: nothing was saved.)
- **Agent (no record):** I don't have any record of earlier calculations in `session-1`. (This session has no checkpoints, and the kernel restart wiped in-process memory.)

**Restart the kernel**

- **Kernel:** Restarted. All Python objects are gone; you re-run the cells to rebuild the graph. AgentCore Memory still holds every checkpoint.
- **Kernel (in-process):** Restarted. All Python objects are gone; you re-run the cells to rebuild the graph. In-process checkpoints were lost with the process.
- **Kernel (no checkpointer):** Restarted. All Python objects are gone; you re-run the cells to rebuild the graph. There was nothing to lose.

Ask the calculation in session-1, then ask what you asked first. Then try session-2, a kernel restart, and the other checkpointers.

Checkpointer

Session (`thread_id`)

Ask: 1337 × 515321, then + 412

Ask: what did I ask first?

Stored checkpoints

Conversation

##### Clean up

```pseudo title="cell 12"
Delete the memory resource memory_id with delete_memory_and_wait   // wait up to 300 seconds, checking every 10
PRINT "Deleted memory", memory_id
```

```python reveal title="cell 12"
client.delete_memory_and_wait(memory_id=memory_id, max_wait=300, poll_interval=10)
print("Deleted memory", memory_id)
```

> **Always run the cleanup cell:**
> This deletes the `MathLanggraphAgent` memory resource and waits (up to 300 seconds, checking every 10) until it's gone, so nothing is left behind in your account.

**What you just did:** created an AgentCore Memory resource, used `AgentCoreMemorySaver` as the LangGraph checkpointer, saw state persist across turns in the same session, and saw a new session start with a clean slate. You now have a stateful agent with production-grade persistence and multi-step reasoning.

## 3.10 Recap and self-check

Your agents no longer start every conversation from zero.

We started with why memory matters, then split it into short-term memory (the current conversation) and long-term memory (episodic, semantic and procedural). You saw the six challenges memory brings, followed one request through an agent loop that reads and writes memory, and mapped each kind of memory to AWS services. You built a personalised Strands agent with Mem0 that keeps every user's memory isolated in code. You learned to treat context as a precious resource, with sliding windows, compaction, notes, sub-agents and retrieval. Finally you met AgentCore Memory, with its actors, sessions, events, strategies and namespaces, and gave a LangGraph agent persistent, session-scoped memory with a single checkpointer.

#### You should now be able to explain

| Idea | In one line |
| --- | --- |
| Agent memory | Keeping past information so the agent keeps context and makes better decisions |
| Short-term vs long-term | A rolling scratchpad for this conversation vs a durable store across sessions |
| Episodic, semantic, procedural | What it experienced, what it knows, how it does things |
| Memory loop | Read short-term and long-term memory, reason, act, then write back what was learned |
| Memory on AWS | DynamoDB, Redis or AgentCore for now; Aurora, DynamoDB or Neptune for facts; OpenSearch, pgvector, Pinecone or Knowledge Bases for meaning; S3 for raw files |
| User isolation | Bind the memory tool to one user in code; prompts are guidance, not a security boundary |
| Context engineering | Curate a small, high-signal window from a big pool of possible context |
| Compaction vs notes | Compaction summarises the story; notes track the state of the work |
| AgentCore Memory | Raw events in short-term memory; strategies extract, consolidate and index records into namespaced long-term memory |
| Checkpointer | Saves LangGraph state after every step; `thread_id` → session, `actor_id` → actor |

#### When something goes wrong

| What you see | What it usually means and how to fix it |
| --- | --- |
| `ValidationException` mentioning `temperature` and `topP` when the agent stores a memory | The Mem0 shim cell didn't run (or ran before a kernel restart). Run the shim cell again, then recreate the agents. |
| `AccessDeniedException` from Bedrock | Model access or region. Check the model ID and that your role can invoke it in your region. |
| `AccessDenied` on `bedrock-agentcore:CreateMemory`, `CreateEvent` or `ListEvents` | Your role lacks AgentCore Memory permissions. Attach `setup/iam-policy-course.json`. |
| Memory is not yet active | `create_or_get_memory` waits for ACTIVE; if you created it another way, wait a minute and retry. |
| The agent "forgets" between sessions in Lab 2 | Expected: short-term memory is per `thread_id`. Reuse the same `thread_id`, or add a long-term strategy. |
| Mona's memories come back empty after re-running the notebook | The setup cell deletes the local FAISS index and `.mem0_course` on purpose, so each run starts clean. |
| `ModuleNotFoundError` or old behaviour after installing | Restart the kernel after `%pip install`, then run the cells from the top. |

> **Did you clean up?:**
> Lab 2's last cell deletes the `MathLanggraphAgent` AgentCore Memory resource; make sure it ran. Lab 1 stores everything locally (FAISS index and `.mem0_course`), so there is nothing to delete in AWS.

#### Self-check

Ten quick questions. Pick an answer to see why it's right or wrong.

Score: 0 of 10 answered

**1. Without memory, what happens when a user returns for a new conversation?**

Options: The agent recalls the last session automatically · The agent starts from scratch with no previous context · The model retrains on the old chat · The agent refuses to answer

**Answer: The agent starts from scratch with no previous context.** A stateless agent treats every new conversation as a stranger. Memory is what carries context forward.

**2. Short-term memory is usually implemented as…**

Options: A graph database of entities · An S3 data lake · A fine-tuned model · The context window or a rolling buffer that drops the oldest messages

**Answer: The context window or a rolling buffer that drops the oldest messages.** Short-term memory is the working scratchpad: a fixed amount of space where new messages push out old ones.

**3. “Last month this customer reported a double charge, we refunded it, and they were satisfied.” Which memory type is that?**

Options: Semantic · Procedural · Episodic · Short-term

**Answer: Episodic.** A specific past event with its action and outcome is an episode, the raw material for case-based reasoning.

**4. Which AWS service fits the question “who worked on Project X and also knows Python?” best?**

Options: Amazon Neptune · Amazon S3 · AWS Step Functions · Amazon ElastiCache

**Answer: Amazon Neptune.** It's a question about relationships between entities, which is exactly what a graph database like Neptune is for.

**5. In the Mem0 lab, what actually stops Mona's agent from reading Bunny's memories?**

Options: The system prompt alone · The memory tool is created with user_id="mona_mona" in code and exposes no user_id parameter · Bedrock Guardrails · Bunny's memories are encrypted with a different key

**Answer: The memory tool is created with user_id="mona_mona" in code and exposes no user_id parameter.** The prompt is guidance; the hard boundary is the tool bound to one user in code. There's nothing for a persuasive prompt to change.

**6. What is context rot?**

Options: Old memories expiring because of a TTL · A model forgetting its training data · Embeddings becoming outdated · Accuracy dropping when the window is stuffed with too much or irrelevant material

**Answer: Accuracy dropping when the window is stuffed with too much or irrelevant material.** Too much context buries the important parts. Treat the window as a finite, precious resource.

**7. Compaction vs structured note-taking: which statement is right?**

Options: They're the same thing · Compaction tracks project state; notes summarise the story · Compaction summarises the story of the conversation; notes track the state of the work · Notes are only for sub-agents

**Answer: Compaction summarises the story of the conversation; notes track the state of the work.** “Step 4 done, step 5 pending, variable is X” is a note. A condensed retelling of the chat is compaction.

**8. An AgentCore Memory resource has no strategies configured. What do you get?**

Options: Short-term memory only; nothing is extracted to long-term memory · Long-term memory with default strategies · An error at creation · Only session summaries

**Answer: Short-term memory only; nothing is extracted to long-term memory.** Strategies drive extraction. Without one, you get short-term memory, which is exactly what Lab 2 uses.

**9. During consolidation, a new fact contradicts an older memory. What happens?**

Options: Both are kept as duplicates · The new fact is dropped · The old record is marked invalid and the new fact takes its place · The session is deleted

**Answer: The old record is marked invalid and the new fact takes its place.** Consolidation adds, updates or skips. Outdated memories are marked invalid, so the agent works from the current fact.

**10. In Lab 2 you switch from thread_id "session-1" to "session-2" with the same actor_id. Why can't the agent recall the calculation?**

Options: The memory was deleted · thread_id maps to an AgentCore session, and short-term memory is scoped to the session · actor_id must change too · The model ran out of tokens

**Answer: thread_id maps to an AgentCore session, and short-term memory is scoped to the session.** Checkpoints belong to a session. Cross-session recall is a job for long-term memory strategies.

Final score message (10 of 10 answered): Great work, you're ready for Section 4 when 8 or more are right. Otherwise: Revisit the parts you missed, then try Section 4.

Feedback after each answer: **Correct.** when it is right, or **Not quite.** You picked “…”. The correct answer is **“…”.** followed by the explanation for that question.

> **Up next: Section 4, multi-agent patterns:**
> So far, one agent has done all the work. Next you'll see why one agent isn't always enough and build teams of agents: a supervisor with workers, agents used as tools, graphs that route work through defined steps, and swarms that hand work to each other. Folder: `section-04-multi-agent-patterns`.
