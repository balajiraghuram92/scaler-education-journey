# How an agent is built on AWS

## 1.4 How an agent is built on AWS

Before we zoom into frameworks, here is the whole build in one picture: where you write code, what the code talks to, and how it reaches users.

{{diagram:1}}

*The blueprint for every agent in this course. Your app sits in the middle. It thinks by calling a model, acts by calling tools, and talks to people through a UI.*

1. 1 Write it in an IDE A developer builds and configures the agentic app in an **IDE** such as Visual Studio Code, Amazon SageMaker Studio, or an agentic IDE such as Kiro.
2. 2 Use a framework The app uses a **framework** such as LangChain or the Strands Agents SDK to define the agent's logic, orchestrate its workflow, and connect it to models and tools.
3. 3 Call a model, the brain An agent needs a reasoning engine to understand requests and decide what to do next, so the running app makes **API** calls to model providers: Amazon Bedrock, or models hosted on Amazon SageMaker AI.
4. 4 Reach tools, memory and other agents At the same time, the app talks to tools, APIs, memory systems and other agents, over **STDIO** or **HTTP(S)**, to fetch information, perform actions or collaborate.
5. 5 Show the result The output reaches the end user through a client application or user interface, where they interact with the agent.

> **STDIO vs HTTP(S), in one line each:**
> **STDIO** is talking to a colleague sitting next to you: the tool runs on the same machine, and the two programs pass messages through standard input and output. **HTTP(S)** is phoning another office: the tool runs somewhere else and you reach it over the network.

#### The same blueprint, inside our first script

Here is `hello_agent.py` from the Section 1 folder. Even ten lines touch steps 2, 3 and 5. Step 4 (tools) arrives in the notebook you run in the lab.

```pseudo title="section-01-your-first-agent/hello_agent.py (trimmed)"
SET MODEL_ID = environment variable BEDROCK_MODEL_ID, or "global.anthropic.claude-sonnet-4-6" if it is not set
SET REGION = environment variable AWS_REGION, or AWS_DEFAULT_REGION, or "us-east-1"
CREATE model = BedrockModel for MODEL_ID in REGION
CREATE agent = Agent that uses model
SET response = the agent's answer to "Hello! Tell me a fun fact about AI agents."
PRINT response
```

> **Imported:**
> - `os` Python standard library: reads settings such as the model ID and Region from environment variables.
> - `Agent` from `strands`, package strands-agents: the agent that combines the model with its tools and prompt.
> - `BedrockModel` from `strands.models.bedrock`, package strands-agents: the model adapter that sends each call to Amazon Bedrock.

```python reveal title="section-01-your-first-agent/hello_agent.py (trimmed)"
import os

from strands import Agent
from strands.models.bedrock import BedrockModel

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
agent = Agent(model=model)

response = agent("Hello! Tell me a fun fact about AI agents.")
print(response)
```

1. **from strands import Agent** Step 2: the framework (Strands Agents) supplies the agent logic.
2. **BedrockModel(…)** Step 3: the brain. Every call to the agent becomes an API call to Amazon Bedrock in your Region.
3. **Agent(model=model)** Step 2 again: model plus (later) tools plus (optionally) a system prompt make an agent.
4. **print(response)** Step 5: here the "UI" is just your terminal. In Section 6 it becomes a web app.

Now that you have seen how AWS supports the practical side of building agents, let's zoom out and look at how these systems grow up over time.

## 1.5 From one LLM to a team of agents

Agentic intelligence doesn't appear all at once. It grows in stages, from a single model answering questions to many agents working together. Each stage adds power, and adds risk.

{{diagram:2}}

*Six stages of agentic systems. Read the red arrow first: as systems get more capable, testing them, securing them, putting guardrails around them and being able to see what they are doing all become harder, and more important. Tap any stage to explore it.*

Explore

##### Stage 1: LLM

What's new at this stage

Example

Where you meet it in this course

How much can go wrong

**Stage 1: LLM**

- **What's new at this stage:** Talk to a model directly. One question, one answer, no tools and no outside data.
- **Example:** Ask Claude on Amazon Bedrock to summarise an article.
- **Where you meet it in this course:** `setup/check_setup.py` calls the model directly with `converse()`.
- **How much can go wrong:** Low. The main risk is a wrong or made-up answer.

**Stage 2: LLM + RAG**

- **What's new at this stage:** Retrieval adds your own, up-to-date documents to every prompt.
- **Example:** An HR chatbot that answers from the policy handbook.
- **Where you meet it in this course:** The RAG ideas in this section; retrieval-based memory in Section 3.
- **How much can go wrong:** Wrong chunks give wrong answers, and retrieval can leak documents a user shouldn't see.

**Stage 3: Augmented LLM**

- **What's new at this stage:** The model can call tools and use memory, not only read.
- **Example:** Look up the live weather, or draft an email and actually send it.
- **Where you meet it in this course:** `01_hello_agent.ipynb` steps 4 and 5: `current_time` and `calculator`.
- **How much can go wrong:** Tools change things in the real world, so a bad decision now has side effects.

**Stage 4: Agentic workflow**

- **What's new at this stage:** The model plans several steps, picks a tool for each, and combines the results.
- **Example:** Check flights, compare prices, ask your preference, book the ticket.
- **Where you meet it in this course:** Section 2 (tool-heavy agents) and Section 4 (graph pattern).
- **How much can go wrong:** Mistakes compound across steps; you need tracing to see which step went wrong.

**Stage 5: Autonomous agent**

- **What's new at this stage:** The agent pursues long-term goals with little human input and its own feedback loop.
- **Example:** A market-watching agent that trades within strict risk limits.
- **Where you meet it in this course:** Long-running agents on AgentCore Runtime (Section 6), with policy and guardrails (Section 7).
- **How much can go wrong:** No human approves each action, so hard limits, policies and a kill switch are essential.

**Stage 6: Multi-agent collaboration**

- **What's new at this stage:** Several specialised agents communicate and coordinate towards a shared goal.
- **Example:** Researcher, writer and editor agents producing one report.
- **Where you meet it in this course:** Section 4 (supervisor, swarm, graph) and Section 5 (A2A travel agents).
- **How much can go wrong:** Interactions are hard to predict; evaluation and observability across agents become critical.

> **Why the red arrow grows:**
> A bicycle needs a bell. A scooter needs a helmet and brakes. A car needs seatbelts, airbags and a dashboard. A fleet of buses needs all that plus a control room and traffic rules. More power, more ways to fail, so more safety and more visibility. Agents are the same; that's what Section 7 is about.

#### Stage 1. LLM

Using a foundation LLM directly: prompt it to write text, answer questions, summarise, translate. The interaction is usually a single turn or a simple conversation, with no tools and no multi-step decisions.

On AWS you have two ways to use a foundation model: **models on Amazon Bedrock**, which is **model as a service**, or **models hosted on Amazon SageMaker AI**, which is **platform as a service**. (Remember the Uber vs leased car analogy.)

*Example:* asking Anthropic's Claude on Amazon Bedrock a question and getting a direct answer.

{{diagram:3}}

*Stage 1 is a straight line. No lookups, no tools, no memory beyond the current conversation.*

> **In our code: setup/check_setup.py:**
> The setup checker is a pure stage-1 call. It sends one message straight to the model through Bedrock's Converse API, with no agent and no tools:

```pseudo title="setup/check_setup.py (excerpt)"
CREATE runtime = Bedrock runtime client in REGION
FOR EACH model_id IN MODELS:
    TRY
        ASK model_id "Reply with the single word: ready"   // one tiny Converse call, no agent and no tools
        SET text = the reply text, trimmed
        PRINT model_id and text
    ON ERROR
        PRINT model_id and the error
```

```python reveal title="setup/check_setup.py (excerpt)"
runtime = boto3.client("bedrock-runtime", region_name=REGION)
for model_id in MODELS:
    try:
        r = runtime.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": "Reply with the single word: ready"}]}],
            inferenceConfig={"maxTokens": 10},
        )
        text = r["output"]["message"]["content"][0]["text"].strip()
        print(f"✅ {model_id}: {text}")
    except Exception as e:
        print(f"❌ {model_id}: {e}")
```

#### Stage 2. LLM + RAG

Here the LLM is **grounded** in external knowledge through RAG. Instead of relying only on what it learned in training, the system first retrieves relevant information from enterprise documents, knowledge bases or databases, and passes it to the model as context. Answers become more accurate, more current and more specific to your domain.

*Example:* a chatbot that answers employees' questions using your internal HR policy documents.

##### Traditional RAG vs agentic RAG

You'll hear both terms. The difference is **who decides** when and how to retrieve.

**Traditional RAG** follows the same fixed path every time: *user question → retrieve documents → send context to the LLM → generate answer*. Ask "What is our company's leave policy?" and it fetches HR policy chunks and answers.

**Agentic RAG** treats retrieval as *one tool among many* inside an agent: *question → agent reasons → maybe call the RAG tool → maybe call other tools → answer or act*. The agent can decide when to retrieve, refine a search, use several sources, combine retrieval with APIs, and act on what it finds. The agent is the decision-maker; RAG is one capability it uses when needed.

{{diagram:4}}

*Fixed pipe vs decision-maker. Traditional RAG always retrieves, even when retrieval can't help. Agentic RAG picks the right source for each question, and can loop until it has what it needs.*

Try it

##### Send the same question to both systems

Traditional RAG

Agentic RAG

**Question 1: "What is our leave policy?"**

Traditional RAG:

- **Act:** Retrieve: top chunks from the HR handbook (leave policy, sick leave).
- **Act:** Add them to the prompt and call the LLM.
- **Answer:** "24 paid leave days a year; up to 8 carry forward." ✓

Agentic RAG:

- **Reason:** Reason: this is a policy question, so the handbook has it.
- **Act:** Call the RAG tool: search the HR handbook for 'leave policy'.
- **Observe:** Got the leave policy chunk.
- **Answer:** "24 paid leave days a year; up to 8 carry forward." ✓

**Question 2: "Should I carry an umbrella to office today?"**

Traditional RAG:

- **Act:** Retrieve: closest handbook chunk is 'Work from home…' (nothing about weather).
- **Act:** Add it to the prompt and call the LLM.
- **Result:** "The handbook doesn't mention umbrellas." ✗ Retrieval can't help with live data.

Agentic RAG:

- **Reason:** Reason: this needs today's weather, not the handbook. Skip RAG.
- **Act:** Call the weather API for Bangalore.
- **Observe:** 80% chance of rain after 4 pm.
- **Answer:** "Yes, take one. Rain is likely after 4 pm." ✓

**Question 3: "What's 18% GST on Rs 84,999, and can I claim it on a work trip?"**

Traditional RAG:

- **Act:** Retrieve: 'Travel allowance' chunk (meals only).
- **Act:** Add it to the prompt; the LLM must also do the maths in its head.
- **Result:** "GST is roughly Rs 15,300; claims are unclear." ✗ Approximate maths, half an answer.

Agentic RAG:

- **Reason:** Reason: two parts. Maths needs the calculator; the claim needs the handbook.
- **Act:** Call calculator: 84999 * 0.18
- **Observe:** 15299.82
- **Act:** Call the RAG tool: travel expense rules.
- **Observe:** Travel allowance covers meals only.
- **Answer:** "GST is Rs 15,299.82 (total Rs 1,00,298.82). It's not claimable: the travel allowance covers meals only." ✓

#### Stage 3. Augmented LLM

Now the LLM is connected to external tools and data sources. This is the shift from a passive LLM to an active one.

{{diagram:5}}

*Three pillars around the brain. Retrieval tells the LLM where to find information, tools let it act, and memory lets it keep track of what has happened so far.*

The LLM is still the central brain, but on its own it is limited by its training cutoff and cannot touch the world. The augmented LLM adds three pillars. An effective agent knows **where to find** information (retrieval), **how to use it to act** (tools), and **how to keep track of progress** (memory). Understanding how these three talk to the LLM is the key to building reliable workflows on AWS.

*Example:* an LLM that searches the internet for live information before answering, or one that writes an email and then calls an email API to send it.

> **In our code: 01_hello_agent.ipynb, steps 4 and 5:**
> When you give the agent the `current_time` tool and the prebuilt `calculator`, you have built an augmented LLM. The model can now get the real time and do exact arithmetic instead of guessing.

#### Stage 4. Agentic workflow, and stage 5. Autonomous agent

**Agentic workflow.** The LLM is no longer just answering; it becomes an agent that plans, reasons and executes a *sequence* of steps towards a goal. It breaks a complex task into sub-tasks, decides which tool each needs, runs them, and combines the results. Planning, memory and reflection usually come along.

*Example:* an agent booking a flight first checks availability through a flight API, compares prices, asks you about your preferences, and finally calls a booking API to complete the reservation.

**Autonomous agent.** A more advanced form of the agentic workflow, with more independence and persistence. It learns from its environment, adapts its plans and pursues long-term objectives *without constant human input*, using feedback loops and self-correction.

{{diagram:6}}

*The key visual difference: one has an end, the other doesn't. An agentic workflow is a task with a finish line. An autonomous agent is a loop that keeps watching, acting and learning, which is exactly why it needs the strongest guardrails.*

*Example of an autonomous agent:* one that continuously monitors market trends, researches new investment opportunities, and executes trades on its own based on predefined strategies and risk limits.

> **Agentic workflow:**
> A wedding planner with a checklist: venue, caterer, decorator, done. When the wedding is over, the job ends.

> **Autonomous agent:**
> A self-driving car: it never stops perceiving the road, deciding, steering and correcting until the trip ends, and learns from every drive.

> **Autonomy needs limits:**
> An agent that trades money without asking anyone must have hard limits: maximum trade size, allowed instruments, a kill switch, and a full log of every decision. This is the red arrow from the stage diagram, made real.

#### Stage 6. Multi-agent collaboration

The most complex stage: several autonomous agents working together towards a shared goal. Each has a specialised role, its own knowledge or tools, and they communicate and coordinate to solve problems too big for one agent. It mimics how a human team works.

{{diagram:7}}

*A newsroom made of agents. Each agent is good at one thing, and the messages between them (violet) are where the coordination happens. Those messages are what agent protocols, coming next, standardise.*

> **Where we build these:**
> Agentic workflows, autonomous agents and multi-agent teams get full hands-on treatment in Section 4 (supervisor-worker, agent as a tool, graph and swarm patterns) and Section 5 (MCP and A2A).

Now that you understand how agents evolve and grow more complex, let's look at how they talk to tools and to each other.
