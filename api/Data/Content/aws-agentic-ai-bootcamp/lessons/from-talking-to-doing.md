# From talking to doing

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

LLM, the brain Tools and actions Data, AWS services, memory MCP and integrations Safety, limits, problems The agent itself

Section 2: Giving agents tools

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 2 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/giving-agents-tools-main.zip)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### Giving agents tools

Section 2. Your first agent could only talk. Here it gets hands: Python functions it can call, a ready-made toolbox, plain-English access to S3, DynamoDB and Lambda, and patterns for tools that stay fast in production.

Folder `section-02-agent-tools` Notebooks `01_building_tools` `02_prebuilt_and_aws_tools` `03_advanced_tool_patterns` Model: Claude Sonnet 4.6 on Amazon Bedrock

{{diagram:1}}

*The journey in this section. Each step reuses the one before it. By step 6 you know the three ways to write a tool, and when to reach for each.*

## 2.0 From talking to doing

In Section 1 you built an agent that understands requests and writes clever answers. But it couldn't check the weather, read a file, query a database, or change anything in the real world.

That limit hurts the moment you try to build something practical. Picture an AI assistant for your team that discusses project requirements brilliantly, yet can't check whether the deployment pipeline is running, read the latest error logs, or update a ticket. Or a customer-service agent that understands tricky questions perfectly, but can't look up an order, process a refund or book an appointment.

{{diagram:2}}

*Without tools, even the best model is a very expensive chatbot. Everything in red needs the agent to reach outside itself: an API, a database, a file. That reach is what a tool gives it.*

> **Think of it like this:**
> A brilliant new hire on day one, before IT has given them any logins. They can discuss your product for hours, but they can't open Jira, can't read the dashboards, can't send a single email. Tools are those logins.

In this section we fix that by giving the agent **tools**: the ability to interact with real systems, fetch live data and do meaningful work beyond writing text. We start by turning plain Python functions into tools, then use ready-made tools that save days of work, then build custom tools for problems only your business has. By the end, your agents won't just talk about solutions; they'll carry them out.

#### What you'll learn here

1. Why agents need tools
2. Building your first tool-enabled agent
3. Using prebuilt tools from the Strands ecosystem, including AWS access
4. Building custom tools, and the class-based and async patterns for when simple tools aren't enough
5. A quick start with Strands Agent Builder

#### Before you start

1. 1 A working Strands setup from Section 1 Your virtual environment, AWS credentials and `python setup/check_setup.py` showing ✅ for both models.
2. 2 Basic Python Functions, return values, dictionaries and simple classes. We explain the new bits (decorators, type hints, async) as we go.
3. 3 AWS permissions for notebook 2 Besides Bedrock, notebook 2 creates and deletes a small **S3** bucket, a **DynamoDB** table, a **Lambda** function and its **IAM** role. An admin user in a sandbox account, or `setup/iam-policy-course.json`, covers all of it.
4. 4 A little **REST** and JSON (helpful, not required) Knowing that an **API** is "send a request to a URL, get **JSON** back" makes the web and AWS examples easier to follow.

| Notebook | What it covers | Where on this page |
| --- | --- | --- |
| `01_building_tools.ipynb` | Function to tool with `@tool`, a tip calculator, a multi-tool sales assistant, a custom inventory checker | 2.1, 2.2, 2.4 |
| `02_prebuilt_and_aws_tools.ipynb` | Prebuilt tools (`calculator`, `http_request`, `file_write`) and `use_aws` against S3, DynamoDB and Lambda | 2.3 |
| `03_advanced_tool_patterns.ipynb` | The database-connection problem and class-based tools; async tools that run in parallel | 2.5 |

```pseudo title="terminal"
RUN cd section-02-agent-tools                 // go to this section's folder
RUN pip install -r requirements.txt           // install the course libraries
RUN jupyter lab                               // open the notebooks in the browser
```

```bash reveal title="terminal"
cd section-02-agent-tools
pip install -r requirements.txt
jupyter lab
```

Every notebook opens with the same two cells: install the libraries, then choose the model once and keep it in a variable called `model`.

```pseudo title="every notebook, setup cell"
IMPORT os and BedrockModel
SET MODEL_ID = environment variable BEDROCK_MODEL_ID, or "global.anthropic.claude-sonnet-4-6" if it is not set
SET REGION = environment variable AWS_REGION, else AWS_DEFAULT_REGION, else "us-east-1"
SET AWS_REGION in the environment to REGION, unless it is already set
CREATE model = BedrockModel(MODEL_ID, REGION)   // every lab reuses this one model
PRINT which model and region are in use
```

> **Imported:**
> - `os` Python standard library: reads and sets environment variables such as `AWS_REGION`.
> - `BedrockModel` from `strands.models.bedrock`: the model client that sends requests to Amazon Bedrock.

```python reveal title="every notebook, setup cell"
import os
from strands.models.bedrock import BedrockModel

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
print(f"Using {MODEL_ID} in {REGION}")
```

> **Always pass the model:**
> Every agent in this section is created with `Agent(model=model, ...)`. If you leave `model` out, Strands falls back to its own built-in default, which can change between versions or may not be enabled in your account. Passing it explicitly keeps every lab on the same, known model.

> **Two things you'll see while running:**
> **Clean-up:** notebook 2 creates real AWS resources. Its last cell deletes them; always run it.
>
> **Deprecation notices:** `strands-agents-tools` 0.8.x prints a **deprecation** warning for a few prebuilt tools (`calculator`, `http_request`, `tavily`, `current_time`). They still work; the course pins `strands-agents-tools<0.9` so they keep working.

## 2.1 Why agents need tools

Suppose you've built an agent to help with your development workflow. It understands git, explains CI/CD and answers project questions. Then you actually use it.

You ask: *"How many open issues do I have in my project repo, and which one has been sitting there the longest?"* It replies: *"I can't access your GitHub account, but you can check by going to your repository's Issues tab and sorting by creation date."*

You already know how to check GitHub. That's why you asked. What you've built is a chatbot that can only answer generically from what it knows. Now give the same agent a GitHub tool and ask again:

1. 1 The agent works out that it needs GitHub's API
2. 2 It calls the GitHub tool `list_issues(repo="myproject", state="open")`
3. 3 Data comes back 23 open issues; issue #47 "Memory leak in data processor" was created 127 days ago.
4. 4 The LLM answers with real facts "You've got 23 open issues. The oldest is #47 about a memory leak in the data processor; it's been open for 127 days. Probably worth tackling that one."

{{diagram:3}}

*Tells you how vs does it for you. Without tools, an agent is an LLM chatbot that explains how you could find the answer. With tools, it finds the answer itself.*

Try it

##### Same question, with and without the GitHub tool

**Agent without tools:**
- **You:** How many open issues do I have in my project repo, and which one has been sitting there the longest?
- **Model:** No tool can reach GitHub, so I can only explain how to look it up.
- **Agent:** “I can't access your GitHub account, but you can check by going to your repository's Issues tab and sorting by creation date.”

**Agent with a GitHub tool:**
- **You:** How many open issues do I have in my project repo, and which one has been sitting there the longest?
- **Model:** I have a GitHub tool. I need open issues for this repo.
- **Tool call:** `list_issues(repo="myproject", state="open")`
- **Result:** 23 open issues. Oldest: #47 “Memory leak in data processor”, created 127 days ago.
- **Agent:** “You've got 23 open issues. The oldest is #47 about a memory leak in the data processor; it's been open for 127 days. Probably worth tackling that one.”

Agent with a GitHub tool

#### What LLMs can't do on their own

LLMs are remarkable at understanding and writing text: essays, explanations, code suggestions. But they have built-in limits, and each one maps to a kind of tool that fixes it.

| Limit | What it means | The kind of tool that fixes it |
| --- | --- | --- |
| Knowledge cutoff | Can't know events or data after its last training update | Search, news, weather and other live-data APIs |
| No real-world interaction | Can't read files, call APIs or execute tasks | File, HTTP, email, database and AWS tools |
| No persistent memory | Forgets past conversations once the session ends | Memory tools and stores (Section 3) |
| No built-in verification | Can't fact-check or confirm its own output is right | Calculators, code execution, lookups against a source of truth |

With tools, agents can query GitHub, read files and databases, check server status and more. A weather API tool fetches your city's weather, a news API tool gets the latest headlines, an email tool sends a message, a file-system tool reads and writes files, and a calculator tool does exact maths. You'll build or use several of these in this section.

#### Brain, coordinator, hands

Here is the relationship between an agent and its tools, in one picture.

{{diagram:4}}

*LLM, agent and tools. The LLM never touches a tool directly. It asks; the agent runs the tool and brings the result back.*

> **Think of it like this:**
> A film shoot. The **director** (the LLM) decides each shot. The **crew** (the tools) work the cameras, lights and sound. The **assistant director** (the agent) runs the set: takes the director's call, gets the crew moving, and reports back what happened.

##### Kinds of tools to think about

When you design an agent, ask what it needs to *find*, *do*, *compute*, *connect to*, and any special media it handles. These five families cover almost everything.

{{diagram:5}}

*Five families of tools. A real agent usually mixes several: a support agent might retrieve (order lookup), compute (refund maths) and act (issue the refund).*

#### From function to tool

Before building agents, let's turn one ordinary Python function into something an agent can use. Say you already have a function that checks whether your staging server is up:

```pseudo title="01_building_tools.ipynb: a plain function"
DEFINE check_server_status_plain(server_url)
    TRY
        CALL requests.get(server_url), waiting at most 5 seconds   // a slow server cannot hang the program
        RETURN "Server is up. Status code: " + the status code
    ON ERROR (any request failure: down, unreachable, timed out)
        RETURN "Server is down or unreachable"

PRINT check_server_status_plain(the test URL)
```

> **Imported:**
> - `requests` third-party package: sends the HTTP GET request and returns the server's reply.

```python reveal title="01_building_tools.ipynb: a plain function"
import requests

def check_server_status_plain(server_url):
    """Check if a server is responding."""
    try:
        response = requests.get(server_url, timeout=5)
        return f"Server is up. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "Server is down or unreachable"

print(check_server_status_plain("https://httpbin.org/get"))
```

It works when *you* call it. But ask an agent "Is the staging server running?" and it replies something like: *"I don't have the ability to check server status. You can use curl or ping."* The agent can't magically discover a function sitting in some Python file.

The fix is called **function calling**, also known as **tool use**. To make the function available, add three things: the `@tool` **decorator** (tells Strands to offer it to agents), **type hints** (tell the agent what data to send) and a clear **docstring** (tells it what the function does, so it knows when to use it).

```pseudo title="01_building_tools.ipynb: the same function as a tool"
DEFINE check_server_status(server_url) RETURNS text
    // @tool: the agent can see this function and call it
    // the docstring tells the agent when to use it
    TRY
        CALL requests.get(server_url), waiting at most 5 seconds
        RETURN "Server is up. Status code: " + the status code
    ON ERROR (any request failure)
        RETURN "Server is down or unreachable"
```

> **Imported:**
> - `Agent` from `strands`: the class that runs the model and its tools together.
> - `tool` from `strands`: the decorator that registers a function as a tool.

```python reveal title="01_building_tools.ipynb: the same function as a tool"
from strands import Agent, tool

@tool  # Decorator
def check_server_status(server_url: str) -> str:  # Type hints
    """Check if a server is responding by making an HTTP request.

    Args:
        server_url: The URL of the server to check

    Returns:
        A message indicating whether the server is up or down
    """
    try:
        response = requests.get(server_url, timeout=5)
        return f"Server is up. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "Server is down or unreachable"
```

{{diagram:6}}

*Three ingredients, three jobs. The decorator makes it a tool, the type hints say what to send, the docstring says when to use it. The function body is private: the model only ever sees the spec and the result.*

Inside, the function makes an HTTP GET request to the URL with a 5-second **timeout**. If the server answers, it returns the **status code** (200 means success). If anything fails (server down, network error, timeout), it catches the **exception** and returns a friendly message instead of crashing. Now hand it to an agent:

```pseudo title="01_building_tools.ipynb"
CREATE agent = Agent(model, tools = [check_server_status])
ASK agent: "Is the staging server running? Check the staging URL"
SAVE the answer in response
```

```python reveal title="01_building_tools.ipynb"
agent = Agent(model=model, tools=[check_server_status])
response = agent("Is the staging server running? Check https://httpbin.org/get")
```

The agent now calls `check_server_status` with the right URL and answers from the real result. This pattern works for any function: add `@tool`, give it to the agent, and the agent can run it.

Try it

##### Remove an ingredient and see what the model loses

on @tool decorator

on Type hints

on Docstring

```text title="your function"

```

Roughly what the model is shown

What that means

- **Without @tool:** **Invisible.** The agent can't discover the function. Ask "Is the staging server running?" and you get: "I don't have the ability to check server status. You can use curl or ping."
- **Without type hints:** **Guessing the format.** The model knows it should send `server_url` but not what type it is. Fine for one string; risky for numbers, dates or lists.
- **Without a docstring:** **Guessing the purpose.** The model only has the name to go on. "check_server_status" is a decent hint, but a name like `run_check` would leave it lost, and it doesn't know what the argument means.
- **With all three:** **Ready.** The model knows what the tool does, when to use it and exactly what to send.

#### When one tool isn't enough

Real requests usually need several steps. Imagine a sales assistant and the request: *"Pull last quarter's sales data and email a summary to the team."* That's not one task but three: query the database, analyse the numbers, send an email. So you build three small tools:

```pseudo title="01_building_tools.ipynb: multi-tool sales assistant"
// each function below is marked @tool, so the agent can call it
DEFINE get_sales_data(quarter)
    RETURN a dict with revenue 1250000, deals 47 and the quarter

DEFINE analyze_sales(revenue, deals, quarter)
    SET avg_deal = revenue / deals
    RETURN one summary line: quarter, revenue, deals and average deal size

DEFINE send_email(to, subject, body)
    PRINT the email to, subject and body
    RETURN "Email sent to " + to

CREATE agent = Agent(model, tools = [get_sales_data, analyze_sales, send_email])
ASK agent: "Pull last quarter's sales data and email a summary to team@company.com"
SAVE the answer in response
```

```python reveal title="01_building_tools.ipynb: multi-tool sales assistant"
@tool
def get_sales_data(quarter: str) -> dict:
    """Retrieve sales data for a specific quarter."""
    return {"revenue": 1250000, "deals": 47, "quarter": quarter}

@tool
def analyze_sales(revenue: int, deals: int, quarter: str) -> str:
    """Calculate key metrics from sales data."""
    avg_deal = revenue / deals
    return f"{quarter}: ${revenue:,} revenue, {deals} deals, ${avg_deal:,.0f} avg deal size"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email message."""
    print(f"\n[EMAIL] to={to} | subject={subject}\n{body}\n")
    return f"Email sent to {to}"

agent = Agent(model=model, tools=[get_sales_data, analyze_sales, send_email])
response = agent("Pull last quarter's sales data and email a summary to team@company.com")
```

Each tool does one job. The data tool only fetches data, the analysis tool only crunches numbers, the email tool only sends messages. That makes them reusable: analysing data from another source? Same analysis tool. Emailing something else? Same email tool. And you never wrote "if the user asks for a sales summary, do steps 1, 2, 3". The agent works out which tools to use, in what order, and how to pass data from one to the next.

{{diagram:7}}

*One request, three tool calls, nobody scripted the order. Each tool's output becomes the next tool's input, and the model is the one deciding that wiring at run time. (The quarter value is whatever the model infers "last quarter" means on the day you run it.)*

Step through

##### Watch the sales request unfold

Press "Next step". The matching arrow in the diagram above lights up.

**Steps through the sales request:**
- **Step 1 of 14.** You ask: “Pull last quarter's sales data and email a summary to team@company.com”.
- **Step 2 of 14.** The agent sends your request to the model, together with the specs of all three tools.
- **Step 3 of 14.** The model's first decision: it needs data. stop_reason = tool_use for get_sales_data.
- **Step 4 of 14.** The agent runs get_sales_data(quarter="Q3 2026"). The model worked out which quarter “last quarter” is.
- **Step 5 of 14.** The tool returns {revenue: 1250000, deals: 47, quarter: "Q3 2026"}.
- **Step 6 of 14.** The agent hands that result back to the model.
- **Step 7 of 14.** The model pulls the numbers out of the result and asks for analyze_sales.
- **Step 8 of 14.** The agent runs analyze_sales(revenue=1250000, deals=47, quarter="Q3 2026").
- **Step 9 of 14.** It returns “Q3 2026: $1,250,000 revenue, 47 deals, $26,596 avg deal size”.
- **Step 10 of 14.** Back to the model with the summary.
- **Step 11 of 14.** The model writes the email body and asks for send_email.
- **Step 12 of 14.** The agent runs send_email(to="team@company.com", subject=…, body=…). In the notebook, the tool's print shows an [EMAIL] line.
- **Step 13 of 14.** “Email sent to team@company.com”.
- **Step 14 of 14.** The model replies with stop_reason = end_turn, and the agent tells you it's done. Three tools, and you never wrote the order.

> **Tip: build focused, single-purpose tools:**
> Resist one mega-tool that does everything. It's harder to maintain, harder for the agent to reason about, and impossible to reuse elsewhere. Think of a TV remote with 80 unlabelled buttons versus three clearly named ones: the model, like you, picks correctly when each button does one obvious thing.

##### Two more multi-tool chains

{{diagram:8}}

*Find, compute, act. Both chains follow the same shape: fetch something, work something out, then do something. The words on the arrows are the data the agent passes along.*

This is what makes agents useful. You build focused tools, each doing one thing well. The agent figures out which to use, in what order, and how to pass data between them. You don't write workflows or state machines; you describe what each tool does and the agent handles the rest. Now let's build one end to end.
