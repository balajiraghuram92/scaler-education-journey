# The problem, explained with one trip

Trip Buddy *· Scaler AWS AI Bootcamp · Week 2 · Project 1*

> **Lesson resources · Scaler AWS AI Bootcamp · Week 2 · Project 1 of 1:**
> - [</> Browse the code](https://github.com/balajiraghuram92/Scaler-AI-Infusion-Bootcamp/tree/main/excersices/Lab-project/Trip-Buddy)
> - [⬇ Download all](/downloads/ai-engineering/trip-buddy.zip)

Scaler AWS AI Bootcamp · Week 2 · Project 1

#### Trip Buddy A trip planner for a group of friends that looks things up, remembers travel tips and does the maths with real tools

Every friend group has "the Goa plan" that never happens. This time we plan it properly. In ten small scripts and one MCP server you build an AI trip planner: a **database** of places and stays, a **travel notebook** searched by meaning, an **LLM** that gives advice, **RAG** so the advice uses the notebook, and **tools** so every rupee is calculated by Python instead of guessed. Then you chat with it in your browser, and on Slack or WhatsApp.

🧳 **The group chat, Friday night.** *"Manali in July? 3 of us, 4 nights, ₹20,000 each. Will it fit? Is July even a good time?"* Everyone has an opinion, nobody has the numbers. Trip Buddy has to answer both questions: **what does it cost each of us**, exactly, and **what should we watch out for**.

**10 + 1** small scripts, plus an MCP server

**3** tools the agent can call

**10** destinations, 13 travel tips

**₹0** to run scripts 01–03 (no API key)

How to read the coloured boxes:

🧠 Analogy🧳 Trip corner⚠️ Watch out⏭️ Already covered💡 Tip🧪 Simulation

⏭️ What carries over from Week 1

Chains (`prompt | llm`), the `.env` file, `@tool` with a docstring, and the agent loop that runs until the model stops asking for tools: all of it is in [Part 00](/chapter/aws-agentic-ai-bootcamp/w1-part-00-aws-revision/the-revision-at-a-glance) and [Lesson 2](/chapter/aws-agentic-ai-bootcamp/w1-lesson-2-giving-agents-tools/from-talking-to-doing). This page spends its time on what is **new**: storing data in SQLite, embeddings and a vector database, RAG, and writing the tool loop by hand.

---

Start here · the problem statement

## The problem, explained with one trip

##### The situation

The friends need one number each: *how much do I pay?* The rules are simple, and they are the same rules the tools use later:

rooms needed = people ÷ 2, rounded UP # one room fits 2 people stay share = rooms × room price × nights ÷ people food and fun = daily spend × nights cost per person = travel + stay share + food and fun

##### A tiny example: two trips

| Trip | Friends | Nights | Room / night | Travel / person | Daily spend | Cost per person |
| --- | --- | --- | --- | --- | --- | --- |
| **Goa** · Beach | 4 | 3 | ₹3,000 | ₹2,800 | ₹1,500 | **₹11,800** |
| **Manali** · Hills | 3 | 4 | ₹2,500 | ₹9,000 | ₹1,300 | **₹20,866.67** |

🧪 Try it

##### The trip calculator: the same maths as the tools in script 06

Friends 3

Nights 4

Room price / night (₹) 2500

Travel / person (₹) 9000

Daily spend / person (₹) 1300

Budget / person (₹) 20000

Show the LLM's slip: forget to round rooms up

**The maths takes four lines of Python.** The hard part is everything around it:

1. **Where do the prices come from?** Someone has to keep the places, stays and room prices in one place: a database.
2. **What should we watch out for?** "Manali in July" sounds fine until you remember the monsoon. That knowledge lives in a friend's travel notebook, not in the numbers.
3. **Can we just ask an LLM?** It gives friendly advice, but it does the arithmetic in its head, and it may not know the notebook's tips.
4. **So what do we build?** An LLM that *reads the notebook first* (RAG) and *calls Python for every number* (tools).

> **⚠️ The trap:**
> 3 friends need **2 rooms**, not 1.5. An LLM doing the maths in its head often divides 3 by 2 and carries on. That makes Manali look like **₹19,200**, inside the ₹20,000 budget, when the real cost is **₹20,866.67**, over it. Press "Show the LLM's slip" above to see it. That one rounding step is why script 06 exists.

> **If you press "Show the LLM's slip" on the Manali numbers:**
>
> Rooms = 3 ÷ 2 = 1.5 **(not rounded up!)** · stay = 1.5 × ₹2,500 × 4 ÷ 3 · total = ₹9,000 + ₹5,000 + ₹5,200 = ₹19,200 → Fits, with ₹800 to spare.
>
> The correct answer is **₹20,866.67**: the slip turned an over-budget trip into one that looks affordable.

📋 **Problem statement for learners.** A group of friends wants to plan a trip. Given a small database of places and stays and a notebook of travel tips, build an AI trip planner that answers questions like *"Can 3 friends do Manali for 4 nights with ₹20,000 each?"* with the **exact cost per person**, worked out by tools, and **advice grounded in the travel tips** (season, packing, booking early), retrieved by meaning.

---

Understand it

## What we are building, and what you need

#### T1 What we are building: one idea per file

Each script adds exactly one idea to the one before it. Open two of them side by side and the difference is the lesson.

| Script | New idea | The question it answers | Needs |
| --- | --- | --- | --- |
| `trip_01_sqlite_basics.py` | SQLite: two tables, a JOIN, a lookup | Where do we keep places, stays and prices? | nothing |
| `trip_02_embeddings_basics.py` | Embeddings and cosine similarity | How do we find a tip that *means* the same thing? | a free model (~90 MB, once) |
| `trip_03_chromadb_retrieval.py` | A vector database with labels | How do we search many tips, and only one shelf? | nothing |
| `trip_04_llm_chain.py` | `prompt \| llm \| parser` | Can an LLM work out the cost per person? | `OPENAI_API_KEY` |
| `trip_05_rag_chain.py` | Retrieve → augment → generate | Does the advice improve when it reads the notebook? | `OPENAI_API_KEY` |
| `trip_06_tool_calling.py` | Tools and a hand-written agent loop | Can we get exact numbers every time? | `OPENAI_API_KEY` |
| `trip_07_multi_chain.py` | A 3-table database and two chained LLM steps | Can one chain explain the numbers and the next decide GO or NOT YET? | `OPENAI_API_KEY` |
| `trip_08_full_agent.py` | Everything together: ReAct agent + Gradio chat | Can friends just ask, in a chat window? | `OPENAI_API_KEY`, `gradio` |
| `trip_mcp_server.py` | The database and tools as an MCP server: tools, resources, prompts | Can any AI app use Trip Buddy's data? | `mcp` 1.x |
| `trip_09_mcp_client_demo.py` | The MCP protocol by hand: handshake, discovery, calls | What actually travels between client and server? | `mcp` 1.x, no key |
| `trip_10_mcp_agent.py` | The script 08 agent, with tools from the MCP server | Can the agent use tools it doesn't own? | `OPENAI_API_KEY`, `mcp` 1.x |

> **Note:**
> 💡 Why not just a Python script?
>
> For the cost alone, a Python function is enough: that's the calculator above. The AI earns its place where a script can't go: **understanding** a messy question ("3 of us, Manali, 4 nights, 20k each?"), **finding** the right tip by meaning, **choosing** which tool to call with which numbers, and **explaining** the answer to the group. The design rule from Week 1 holds: *code computes, the LLM reasons and explains.*

#### T2 The architecture: a planner, a notebook and a calculator

{{diagram:1}}

*Two kinds of help for one LLM. ① RAG brings in knowledge it wasn't trained on (the notebook). ②③ Tools bring in exactness it can't do in its head (the maths). Scripts 05 and 06 each add one of them; script 08 joins them into one agent.*

> **🧠 The friend who plans every trip:**
> Every group has one: they keep a **notebook of tips** (the vector database), a **spreadsheet of prices** (SQLite) and a **calculator** on the table (the tools). When you ask "Manali in July?", they flip to the hills page first, then work out the cost on the calculator, then tell you. Trip Buddy does the same three moves in the same order.

#### T3 What you need

| You need | Why | Used in |
| --- | --- | --- |
| **Python 3.11+** and **uv** | The scripts use `dict \| None` type hints and run with `uv run` | all |
| **An OpenAI API key** | The planner LLM, read from `.env` | 04 · 05 · 06 |
| **~90 MB of disk** | The free embedding model, downloaded on the first run | 02 · 03 · 05 · 08 · 10 |
| **No AWS account** | This project runs on OpenAI and a local model, so anyone can try it | none |

| Library | What it does here | Scripts |
| --- | --- | --- |
| `sqlite3` | The database, built into Python | 01 |
| `sentence-transformers`, `numpy` | Turns text into 384 numbers; compares them | 02 |
| `chromadb` | Vector database: text + embedding + labels | 03 · 05 |
| `langchain-huggingface` | The same embedding model, in LangChain's shape | 03 · 05 |
| `langchain-core`, `langchain-openai` | Prompts, chains, messages, tools and `ChatOpenAI` | 04 · 05 · 06 |
| `python-dotenv` | Loads `OPENAI_API_KEY` from `.env` | 04 – 08 · 10 |
| `gradio` | The chat window in your browser | 08 · 10 |
| `mcp` **below 2.0** | FastMCP server and the MCP client (brings `pydantic`) | server · 09 · 10 |

```pseudo title="terminal, one-time setup in the project folder"
RUN uv init trip-buddy   // a new project with its own pyproject.toml
RUN uv add the nine libraries above   // mcp must be below 2.0   // creates .venv and locks the versions
CREATE .env with OPENAI_API_KEY = your key   // never commit this file
RUN uv run trip_01_sqlite_basics.py   // then 02, 03 ... 06, in order
```

```bash reveal title="Bash · one-time setup (macOS / Linux / WSL)"
uv init trip-buddy && cd trip-buddy
# copy the Trip Buddy .py files (GitHub or trip-buddy.zip) into this folder, then:
uv add chromadb sentence-transformers numpy langchain-huggingface langchain-core langchain-openai python-dotenv gradio "mcp<2"
cp .env.example .env        # then paste your OPENAI_API_KEY into .env
uv run trip_01_sqlite_basics.py
```

trip-buddy/ ├── .env # YOUR key, never committed ├── trip_01_sqlite_basics.py # places + stays in SQLite ├── trip_02_embeddings_basics.py # sentences → 384 numbers ├── trip_03_chromadb_retrieval.py # the travel notebook, with shelves ├── trip_04_llm_chain.py # the planner, maths in its head ├── trip_05_rag_chain.py # the planner reads the notebook first ├── trip_06_tool_calling.py # the planner uses a calculator ├── trip_07_multi_chain.py # compute → explain → decide ├── trip_08_full_agent.py # the full agent + Gradio chat ├── trip_mcp_server.py # the database + tools as an MCP server ├── trip_09_mcp_client_demo.py # the MCP protocol, by hand ├── trip_10_mcp_agent.py # the agent, tools over MCP ├── slack_bot.py # optional, T15 └── whatsapp_bot.py # optional, T15

**Text · .env.example**

```text
# Copy this file to .env (same folder) and paste your key. Never commit .env.
OPENAI_API_KEY=sk-...

# Optional: any chat model your key can use (default gpt-6-luna)
# OPENAI_MODEL=gpt-4.1-mini   # older non-reasoning model: drop reasoning_effort, use temperature=0
```

> **💡 Get the code:**
> All ten scripts and the MCP server are on GitHub: [Scaler-AI-Infusion-Bootcamp / excersices / Lab-project / Trip-Buddy](https://github.com/balajiraghuram92/Scaler-AI-Infusion-Bootcamp/tree/main/excersices/Lab-project/Trip-Buddy). Read them there one by one, or [download them all as a zip](/downloads/ai-engineering/trip-buddy.zip) and copy them into your `trip-buddy/` folder.

> **⚠️ Pin mcp below 2.0:**
> The MCP files use the 1.x API (`from mcp.server.fastmcp import FastMCP`). In `mcp` 2.x, FastMCP was renamed and other APIs changed, so a plain `uv add mcp` fails with *No module named 'mcp.server.fastmcp'*. Install `"mcp<2"`; the output on this page comes from `mcp` 1.30.

⏭️ Same models, different provider

Like Part 00, this project runs on OpenAI so anyone can try it without an AWS account. The ideas map one to one onto what you used in Week 1: `ChatOpenAI` becomes `BedrockModel`, LangChain's `@tool` becomes Strands' `@tool`, and the hand-written loop in script 06 is what Strands' `Agent` runs for you. Stretch goal S1 asks you to port it.

---

Build it
