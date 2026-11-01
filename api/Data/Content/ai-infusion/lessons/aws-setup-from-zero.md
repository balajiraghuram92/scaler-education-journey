# AWS setup from zero

> **Lesson resources · Lesson 6 · AI agents on AWS:**
> - [Watch the Class 6 recording](https://www.scaler.com/meetings/i/ai-infused-learning-6/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Class-6-AI-infusion.zip)

Future with Shivank · AI Agents on AWS

#### From LLM to a *working agent*

A hands-on masterclass for anyone who already knows LLMs and agents at a basic level. Every concept in plain language, every diagram, and a runnable command after each idea — plus AWS setup from scratch and a capstone project.

Level · **Beginner-friendly** Framework · **AWS Strands SDK** Model host · **Amazon Bedrock** Region · **us-east-1**

Section 0 · Setup

## AWS setup from zero

Everything in both modules runs on your own laptop and calls AI models hosted on AWS. So there are exactly two things to arrange: **credentials** (so your laptop can talk to AWS) and **model access** (so AWS lets you use the models). Nothing else.

> **What this costs:**
> Running code locally is free. You only pay per model call, priced per token — the examples in this entire masterclass cost a fraction of a cent in total. Nothing keeps running in the background, so there is nothing to switch off afterwards.

#### 0.1 · Create an access key (browser, once)

Signed in to the AWS console as an admin:

1. Top search bar → type **IAM** → open it.
2. Left menu → **Users** → click your username.
3. Open the **Security credentials** tab.
4. Scroll to **Access keys** → **Create access key**.
5. Use case → **Command Line Interface (CLI)** → tick the box → **Next** → **Create access key**.
6. Copy the **Access key ID** and **Secret access key** now — the secret is shown only once.

> **Treat the secret like a password:**
> Never paste it into chat, screenshots, or a Git repo. `aws configure` stores it locally in `~/.aws/credentials`, which is where it belongs.

#### 0.2 · Connect your laptop

```pseudo title="terminal"
RUN aws configure
    ASK for the Access Key ID          // paste the key id
    ASK for the Secret Access Key      // paste the secret; it is stored in ~/.aws/credentials
    ASK for the default region         // type us-east-1
    ASK for the output format          // press Enter to leave it blank
```

```python reveal title="terminal"
aws configure
# AWS Access Key ID     → paste the key id
# AWS Secret Access Key → paste the secret
# Default region name   → us-east-1
# Default output format → (press Enter, leave blank)
```

Check it worked:

```pseudo title="terminal"
RUN aws sts get-caller-identity   // prints your Account, UserId and Arn if the credentials work
```

```python reveal title="terminal"
aws sts get-caller-identity
```

Success prints your `Account`, `UserId`, and `Arn`. If you get `InvalidClientTokenId`, the key is wrong or deactivated — create a fresh one and run `aws configure` again.

#### 0.3 · Enable the models in Bedrock

Models are switched off by default. In the console:

1. Top-right region selector → **US East (N. Virginia) · us-east-1**.
2. Search **Bedrock** → open it → left menu → **Model access**.
3. **Modify model access** → tick the models below → submit.

| Model | Used for |
| --- | --- |
| Amazon Nova Lite | Module 1 Hello World (cheap, fast) |
| Claude Haiku 4.5 | Module 1 LangGraph example, Module 2 tools |
| Claude Sonnet 4.5 | Heavier reasoning; useful later |

Verify from the terminal which Anthropic models are live in your account:

```pseudo title="terminal"
RUN aws bedrock list-foundation-models --region us-east-1   // ask Bedrock which models exist
SET names = each modelId that contains 'anthropic.claude'   // the --query filter
PRINT names as a table
```

```python reveal title="terminal"
aws bedrock list-foundation-models --region us-east-1 \
  --query "modelSummaries[?contains(modelId,'anthropic.claude')].modelId" \
  --output table
```

> **The single most common error you will hit:**
> The repo pins older model IDs that AWS has since retired. You will see `ResourceNotFoundException … model version has reached the end of its life` or `… marked by provider as Legacy`. **The fix is always the same:** list the live models with the command above, pick one, prefix it with `us.`, and swap it into the code. Treat this as a skill worth learning, not as a bug.

#### 0.4 · The project folder

All the code for both modules ships with this guide, already fixed and ready to run. Unzip it anywhere and open the folder in VS Code — **you can rename the folder to whatever you like**, nothing depends on its name.

```text title="what's inside"
.
├── GUIDE.html            # this file
├── README.md             # how to run everything
├── config.py             # model IDs — change once, applies everywhere
├── requirements.txt
├── setup.sh / setup.bat
├── 00_check_setup.py     # run this FIRST
├── 01_list_models.py     # use when a model is retired
├── shivank1/             # 2 examples
├── shivank2/             # 9 examples
└── shivank3/             # capstone project
```

#### 0.5 · Install the packages

```pseudo title="terminal · from the project folder"
RUN ./setup.sh   // macOS / Linux: install the packages the project needs
RUN setup.bat    // Windows: the same job
```

```python reveal title="terminal · from the project folder"
# macOS / Linux
./setup.sh

# Windows
setup.bat
```

Or do it manually if you prefer:

```pseudo title="terminal · manual install"
RUN python3 --version           // must be 3.10 or higher
RUN python3 -m venv .venv       // create an isolated environment in .venv
RUN source .venv/bin/activate   // turn it on (Windows: .venv\Scripts\activate)
RUN pip install --upgrade pip
RUN pip install -r requirements.txt   // install the packages the project lists
```

```python reveal title="terminal · manual install"
python3 --version          # must be 3.10 or higher
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> **If you're in conda (your prompt shows `(base)`):**
> The venv keeps this project isolated from your conda environment. After activating you should see `(.venv)` at the front of your prompt. In VS Code, also pick the interpreter: ⌘⇧P → *Python: Select Interpreter* → choose the `.venv` one.

#### 0.6 · Run the readiness check

This is the single most useful command in the whole project. It verifies Python, packages, credentials, region, Bedrock access, **and makes a real model call** — so if it passes, every example will run.

```pseudo title="00_check_setup.py"
RUN source .venv/bin/activate   // turn on the project's virtual environment
SET AWS_DEFAULT_REGION = us-east-1   // tells the AWS tools which region to use
RUN python 00_check_setup.py   // checks Python, packages and credentials, then makes one real model call
```

```python reveal
source .venv/bin/activate
export AWS_DEFAULT_REGION=us-east-1
python 00_check_setup.py
```

▶ Run it

> **What success looks like:**
> Six `[ OK ]` lines ending with *"All checks passed."* If anything fails it prints the exact fix — enable model access, paste fresh credentials, or swap a retired model. Run this before you touch anything else. If it passes, every example in this guide will work.

> **Do this before anything else:**
> Give Section 0 a proper 15 minutes before you write any agent code. Setup failures are the number-one reason people abandon hands-on AI work. Do not move past this section until `get-caller-identity` returns your account details.

---

Module 1 · shivank1

Section 1

## Why agents exist at all

Start here, because it frames everything else. A standard LLM has two hard limits:

- **Knowledge cutoff** — it only knows what it was trained on. Ask about yesterday's news and it cannot help.
- **No access to your world** — it cannot read your company database, check today's weather, or send an email.

There are two ways to fix this without retraining the model:

| Approach | What it adds | The model becomes… |
| --- | --- | --- |
| **RAG** | Relevant context fetched from your data | A better-informed *knowledge retriever* |
| **Agents** | The ability to reason and *use tools* | An *actor* that gets things done |

Here is the framing that matters: many teams build a RAG system, then find users want the AI to **actually do the work** — book the meeting, update the record, run the workflow. Moving from passive retriever to active agent is exactly where people get stuck. That is what these two modules fix.

Section 2

## RAG and how it works

RAG combines an LLM with a search system in three steps:

1. **Retrieve** — search an external knowledge base for information relevant to the question.
2. **Augment** — glue that retrieved context onto the original question to form a richer prompt.
3. **Generate** — the LLM answers using the supplied context.

{{diagram:1}}

*Diagram 1 — How Retrieval Augmented Generation works*

For example: *"Who won the 2024 Nobel Prize in Physics?"* The system queries a real-time news database, finds the fact, adds it to the prompt, and the LLM produces an accurate answer — despite that fact being past its training cutoff.

#### The full RAG pipeline

The next diagram expands this into the seven stages of building a real RAG system.

{{diagram:2}}

*Diagram 2 — The RAG pipeline, from raw documents to a final answer*

#### The stages, in plain language

- **Load** — bring in the documents you want to query.
- **Chunk** — split them into small pieces. Two reasons: models have a limited context window, and it avoids the *lost-in-the-middle* effect where details buried in a long passage get overlooked.
- **Embed** — convert each chunk into a vector, a numerical representation of its meaning (using an embedding model such as Amazon Titan).
- **Store** — keep chunks plus vectors in a vector database that supports similarity search. Common examples: Amazon OpenSearch Service, Pinecone, FAISS, Chroma, PostgreSQL with pgvector.
- **Retrieve** — turn the user's question into a vector too, and pull the *top-k* most similar chunks (k = 3, 5, 10…).
- **Filter & rerank** — optionally re-sort for quality. Improves results but adds cost and complexity.
- **Generate** — hand the retrieved chunks plus the original question to the LLM, which writes the final answer.

> **Analogy that lands:**
> RAG is an **open-book exam**. The model hasn't memorised the textbook, but you let it flip to the three most relevant pages before answering. Chunking is deciding how big each page is; embedding is the index at the back that tells you which pages to flip to.

Section 3

## What is an agent?

The word *agent* just means something that performs a task on your behalf. A working definition: **AI agents are autonomous software systems that use AI to reason, plan, and carry out tasks** for humans or other systems. They make decisions, adapt to new information, and act without needing explicit instructions for every step.

What makes them powerful is **iterative thinking** — they evaluate results, adjust, and keep working toward a goal. And they often use RAG *as one part* of that workflow.

{{diagram:3}}

*Diagram 3 — An AI agent as a travel planner, using agentic RAG*

Follow this example closely. The agent takes *"What should I pack for New York summer?"* and it does **not** just look one thing up. It:

1. Uses RAG to retrieve historical weather data
2. Checks a real-time forecast via an API
3. Analyses user preferences (pack light, but avoid being cold)
4. Synthesises all of it into a personalised recommendation

That final synthesis — combining three different sources into a judgement — is the decision-making that separates an agent from simple retrieval.

> **The one-line distinction to drill:**
> **RAG answers questions. Agents accomplish goals.** RAG gives the model better information; an agent gives it the ability to act, check the result, and try again.

Section 4

## From LLMs to multi-agent systems

Think of this as a progression. Each step adds one capability. This is the fastest way to orient yourself if you "sort of know" agents already.

{{diagram:4}}

*Diagram 4 — Progression from basic LLM capabilities to multi-agent systems*

The one line to hold on to: **each level adds exactly one thing.** Memory, then grounding, then action, then teamwork. If you can name what each level adds, you understand the shape of the entire field.

Section 5

## Agent protocols — MCP and A2A

Once agents need to reach the outside world and each other, you need standard ways to connect. Two protocols matter, and they are constantly confused with each other, so compare them side by side.

#### MCP — Model Context Protocol

MCP connects an agent to **tools and data**. A server exposes capabilities; a client (your agent) discovers and calls them. Think of it as **USB for AI tools** — plug in a new server, gain new abilities, without changing your agent's code.

{{diagram:5}}

*Diagram 5 — MCP workflow: the client discovers a server's capabilities, then calls them*

#### A2A — Agent to Agent

A2A connects an agent to **other agents**. Each agent publishes an *agent card* (a small profile: name, skills, how to talk to it), and other agents read that card and send it messages.

{{diagram:6}}

*Diagram 6 — How A2A works: an orchestrator discovers and messages independent agents*

|  | MCP | A2A |
| --- | --- | --- |
| Connects an agent to… | Tools, data, prompts | Other agents |
| The other side is… | A server exposing capabilities | A peer agent with its own brain |
| Discovery via | Listing tools/resources/prompts | The agent card |
| Analogy | USB port for abilities | Colleagues phoning each other |

Diagram 7 — MCP vs A2A, side by side

> **Scope note:**
> Module 1 only *introduces* these protocols — building MCP servers and A2A agents is a much larger topic on its own. Learn the vocabulary here so it is familiar later, then move on. Resist the urge to go and build an MCP server today; finish the agent fundamentals first.

Section 6
