# The AWS agentic stack

## The AWS agentic stack

AWS offers three layers for building agents. Always know which layer you are standing on.

{{diagram:1}}

*Diagram 8 — The AWS agentic stack and where Strands sits within it*

**Amazon Bedrock** is the key one for today: it is a managed service that hosts foundation models (Claude, Nova, and more) behind a single API. You enabled model access in Section 0 — that is what makes these models callable from your code.

Section 7

## The Strands SDK and the agentic loop

Put simply: **Strands has three core components — model, tools, and prompt** — plus an agentic feedback loop.

{{diagram:2}}

*Diagram 9 — The Strands agentic loop: agent asks model, model reasons and selects tools, agent executes, results feed back*

The loop in plain terms: the agent asks the model; the model reasons, responds, and selects tools; the agent executes those tools; results feed back into the agent, which may re-invoke the model. **This continues until the agent determines the prompt has been fully addressed** — then it compiles everything and returns the result.

> **The sentence that makes agents click:**
> "A chatbot answers once. An agent keeps going until the job is done." The loop *is* the difference. Everything else is detail.

Section 8 · Hands-on

## Building a "Hello World" agent

> **How to run every example in this guide:**
> Run everything **from the project root** (the folder containing `config.py`) — not from inside `shivank1/`. The scripts import shared settings from `config.py`, so running from a subfolder gives `ModuleNotFoundError: No module named 'config'`.

#### 8.1 · The simplest possible agent — Strands + Nova Lite

```pseudo title="shivank1/01_hello_world_agent.py"
CREATE model = a Bedrock model using NOVA_LITE   // Amazon's cheapest model, fine for a first run
CREATE agent = Agent with that model
SET response = agent("Hello! Tell me a fun fact about AI agents.")
PRINT response
```

> **Imported:**
> - `Agent` from `strands`: the agent object that wraps the model and is called like a function.
> - `BedrockModel` from `strands.models.bedrock`: the model object that talks to a model on Amazon Bedrock.
> - `NOVA_LITE` from `config`, the project's own `config.py`: the model id of Amazon Nova Lite, shared by all the scripts.

```python reveal title="shivank1/01_hello_world_agent.py"
from strands import Agent
from strands.models.bedrock import BedrockModel
from config import NOVA_LITE

# Nova Lite: Amazon's cheapest model — ideal for a first run.
model = BedrockModel(model_id=NOVA_LITE)

agent = Agent(model=model)

response = agent("Hello! Tell me a fun fact about AI agents.")
print(response)
```

▶ Run it

```text
python shivank1/01_hello_world_agent.py
```

**Four lines is a whole agent.** Read each one: choose a model, wrap it in an `Agent`, call the agent like a function, print the answer. There are no tools here yet, so the loop runs exactly once — this is the "before" picture for Module 2.

#### 8.2 · Same idea in LangGraph, with a tool

Strands is not the only framework. This version uses LangGraph and adds a small tool, so you can watch the loop actually loop.

```pseudo title="shivank1/02_hello_world_langgraph.py"
DEFINE greet(name) as a tool   // the docstring tells the model when to use it
    RETURN "Hello, " + name + "! Welcome to the world of AI agents."

CREATE llm = a chat model for MODEL_ID, served through Bedrock
CREATE agent = a ReAct agent with llm and the greet tool   // the loop: model, tool, model
SET response = the agent's run on "Please greet Alice and Bob."
FOR EACH message in response
    PRINT the message type and text   // one line per step, so you can see the loop
```

> **Imported:**
> - `init_chat_model` from `langchain.chat_models`: builds the chat model object for Bedrock.
> - `tool` from `langchain.tools`: the decorator that turns `greet` into a tool.
> - `create_react_agent` from `langgraph.prebuilt`: builds the agent that loops between the model and its tools.
> - `MODEL_ID` from `config`, the project's own `config.py`: the model id used for the chat model.

```python reveal title="shivank1/02_hello_world_langgraph.py"
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from config import MODEL_ID

# Define a simple tool
@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to the world of AI agents."

# Initialize the LLM via Bedrock
llm = init_chat_model(
    MODEL_ID,
    model_provider="bedrock_converse",
)

# Create a ReAct agent with the tool
agent = create_react_agent(model=llm, tools=[greet])

# Run the agent
response = agent.invoke(
    {"messages": [{"role": "user", "content": "Please greet Alice and Bob."}]}
)

# Print every step so you can see the loop
for message in response["messages"]:
    print(f"{message.type}: {message.text}")
```

▶ Run it

```text
python shivank1/02_hello_world_langgraph.py
```

> **Expected output — and the moment it clicks:**
> You will see five lines: `human:` the request · `ai:` (empty) · `tool:` Hello, Alice! · `tool:` Hello, Bob! · `ai:` a summary. **Stop and unpack this.** The empty `ai:` line is the model *choosing to use a tool instead of answering*. That is the agentic loop from Diagram 9, visible in your terminal.

> **Note on models — already handled for you:**
> Older tutorials pin `anthropic.claude-3-5-haiku-20241022-v1:0`, which AWS has since retired. **These files already use the current model** via `config.py`, so there is nothing to patch. If a model is retired in future, run `python 01_list_models.py`, pick a live one, and change the single line in `config.py` — every example picks it up.

---

Module 2 · shivank2

Section 9

## LLM, agent, and tools — who does what

The division of labour — the cleanest mental model here:

- **The LLM is the brain** — it understands requests, reasons about what needs doing, and decides which tools to use.
- **Tools are the hands and senses** — they perform actions and gather information from the outside world.
- **The agent is the coordinator** — it manages the conversation between the LLM and the tools.

{{diagram:3}}

*Diagram 10 — LLM, Agent, and Tools*

#### Types of tools

{{diagram:4}}

*Diagram 11 — Types of tools an agent can use*

Section 10 · Hands-on

## From function to tool

This is the most important idea in this module. Start with an ordinary Python function that checks whether a server is up:

```pseudo title="plain python — the agent cannot use this"
DEFINE check_server_status(server_url):
    TRY
        SET response = an HTTP GET of server_url, waiting at most 5 seconds
        RETURN "Server is up. Status code: " + the response status code
    ON ERROR (any requests exception)
        RETURN "Server is down or unreachable"

SET status = check_server_status("https://staging.myapp.com")
PRINT status   // e.g. "Server is up. Status code: 200"
```

> **Imported:**
> - `requests` third-party package, installed with pip: sends the HTTP GET request and provides the exception that is caught.

```python reveal title="plain python — the agent cannot use this"
import requests

def check_server_status(server_url):
    """Check if a server is responding."""
    try:
        response = requests.get(server_url, timeout=5)
        return f"Server is up. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "Server is down or unreachable"

# You use it like this:
status = check_server_status("https://staging.myapp.com")
print(status)
# "Server is up. Status code: 200"
```

Ask the agent *"Is the staging server running?"* and it replies that it has no ability to check server status. **The agent cannot magically discover your function.** That is the gap.

The bridge is **function calling** (also called tool use). Add three things:

| Add this | Why |
| --- | --- |
| `@tool` decorator | Tells Strands to make this function available to agents |
| Type hints | Tell the agent what data types to expect |
| A proper docstring | Describes what it does, so the agent knows *when* to use it |

```pseudo title="shivank2/01_function_to_tool.py"
DEFINE check_server_status(server_url: text) -> text as a tool   // 1. the @tool decorator, 2. the type hints, 3. the docstring
    // docstring: what the tool does, its server_url argument and what it returns
    TRY
        SET response = an HTTP GET of server_url, waiting at most 5 seconds
        RETURN "Server is up. Status code: " + the response status code
    ON ERROR (any requests exception)
        RETURN "Server is down or unreachable"
```

> **Imported:**
> - `Agent` from `strands`: imported here for the next snippet; not used in this block.
> - `tool` from `strands`: the decorator that makes the function available to an agent.
> - `requests` third-party package, installed with pip: sends the HTTP GET request and provides the exception that is caught.

```python reveal title="shivank2/01_function_to_tool.py"
from strands import Agent, tool
import requests

@tool                                              # 1. decorator
def check_server_status(server_url: str) -> str:      # 2. type hints
    """Check if a server is responding by making an HTTP request.

    Args:
        server_url: The URL of the server to check

    Returns:
        A message indicating whether the server is up or down
    """                                           # 3. docstring
    try:
        response = requests.get(server_url, timeout=5)
        return f"Server is up. Status code: {response.status_code}"
    except requests.exceptions.RequestException:
        return "Server is down or unreachable"
```

```pseudo title="give it to the agent"
CREATE agent = Agent with the check_server_status tool
SET response = agent("Is the staging server running? Check https://httpbin.org/get")
```

```python reveal title="give it to the agent"
agent = Agent(tools=[check_server_status])
response = agent("Is the staging server running? Check https://httpbin.org/get")
```

▶ Run it

```text
python shivank2/01_function_to_tool.py
```

> **The one thing to take away from this section:**
> **The docstring is not a comment — it is the user manual the model reads.** The model decides whether to call your tool based on that description alone. Vague docstring, unreliable agent. Deliberately break one: change the docstring to `"Does a thing."` and watch the agent stop calling it. That single experiment will teach you more than any amount of reading.

In short: *this pattern works for any function. Add `@tool`, give it to your Agent, and the agent can now execute it.*

Section 11 · Hands-on

## Your first tool-enabled agent — the tip calculator

A practical, self-contained example from Module 2. Nothing external to configure.

```pseudo title="shivank2/01_function_to_tool.py"
DEFINE calculate_tip(bill_amount, tip_percentage, num_people = 1) as a tool
    SET tip = bill_amount * (tip_percentage / 100)
    SET total = bill_amount + tip
    SET per_person = total / num_people
    RETURN bill, tip, total and per_person   // tip, total and per_person rounded to 2 decimals

CREATE agent = Agent with the calculate_tip tool
SET response = agent("The bill is $85. What's a 20% tip, and how much does each person pay if we're splitting it 4 ways?")
PRINT the text of the response message
```

> **Imported:**
> - `Agent` from `strands`: the agent that is given the tip tool.
> - `tool` from `strands`: the decorator that turns `calculate_tip` into a tool.

```python reveal title="shivank2/01_function_to_tool.py"
from strands import Agent, tool

@tool
def calculate_tip(bill_amount: float, tip_percentage: float, num_people: int = 1) -> dict:
    """Calculate tip and split the bill among people.

    Args:
        bill_amount: Total bill amount in dollars
        tip_percentage: Tip percentage (e.g., 15, 18, 20)
        num_people: Number of people splitting the bill (default: 1)
    """
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    per_person = total / num_people

    return {
        "bill": bill_amount,
        "tip": round(tip, 2),
        "total": round(total, 2),
        "per_person": round(per_person, 2)
    }

agent = Agent(tools=[calculate_tip])

response = agent("The bill is $85. What's a 20% tip, and how much does each person pay if we're splitting it 4 ways?")
print(response.message['content'][0]['text'])
```

Then show that the agent understands *intent*, not keywords — all three of these work without any extra code:

```pseudo title="shivank2/02_tip_calculator.py"
CALL agent("What's a 15% tip on $42?")
CALL agent("Bill is $120, we want to tip 18%, split between 3 people")
CALL agent("Calculate tip for $67.50 at 20%")   // three different phrasings, same tool
```

```python reveal title="shivank2/02_tip_calculator.py"
agent("What's a 15% tip on $42?")
agent("Bill is $120, we want to tip 18%, split between 3 people")
agent("Calculate tip for $67.50 at 20%")
```

▶ Run it

```text
python shivank2/02_tip_calculator.py
```

> **Contrast worth drawing:**
> In traditional chatbot development you'd write regex patterns and intent classifiers to handle those three phrasings, and separately extract the numbers. Here you wrote one function with a clear description and the model did the intent recognition *and* the parameter extraction. That is the leap.

Section 12

## When one tool isn't enough

The scenario: you ask a sales assistant to *"pull last quarter's sales data and email a summary to the team."* That is not one task — it is three: query the database, analyse the numbers, send an email.

```pseudo title="shivank2/03_multi_tool_sales.py"
DEFINE get_sales_data(quarter) as a tool
    RETURN revenue 1250000, deals 47 and the quarter   // sample numbers, not a real database

DEFINE analyze_sales(revenue, deals, quarter) as a tool
    SET avg_deal = revenue / deals
    RETURN "Q" + quarter + ": " + revenue + " revenue, " + deals + " deals, " + avg_deal + " avg deal size"

DEFINE send_email(to, subject, body) as a tool
    RETURN "Email sent to " + to   // no real email is sent

CREATE agent = Agent with get_sales_data, analyze_sales and send_email
SET response = agent("Pull last quarter's sales data and email a summary to the team")   // the agent decides the order
```

> **Imported:**
> - `Agent` from `strands`: the agent that is given the three tools.
> - `tool` from `strands`: the decorator that turns each function into a tool.

```python reveal title="shivank2/03_multi_tool_sales.py"
from strands import Agent, tool

@tool
def get_sales_data(quarter: str) -> dict:
    """Retrieve sales data for a specific quarter."""
    return {"revenue": 1250000, "deals": 47, "quarter": quarter}

@tool
def analyze_sales(revenue: int, deals: int, quarter: str) -> str:
    """Calculate key metrics from sales data."""
    avg_deal = revenue / deals
    return f"Q{quarter}: ${revenue:,} revenue, {deals} deals, ${avg_deal:,.0f} avg deal size"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email message."""
    return f"Email sent to {to}"

agent = Agent(tools=[get_sales_data, analyze_sales, send_email])

response = agent("Pull last quarter's sales data and email a summary to the team")
```

{{diagram:5}}

*Diagram 12 — One request, three tools: the agent works out which to call and in what order*

You never told the agent the sequence. It recognised it needed data first, then analysis, then delivery — and chained them. That is planning.

▶ Run it

```text
python shivank2/03_multi_tool_sales.py
```

> **Rule of thumb:**
> Build focused, single-purpose tools. Avoid the temptation to create one mega-tool that does everything: it becomes harder to maintain, harder for the agent to reason about, and impossible to reuse elsewhere. Small tools recombine — the same `analyze_sales` works with data from any source.

Section 13 · Hands-on

## Pre-built community tools

You don't have to write everything. `strands_tools` ships ready-made tools — import and go.

#### 13.1 · Calculator

```pseudo title="shivank2/05_prebuilt_tools.py"
CREATE agent = Agent with the calculator tool and the system prompt "You are a helpful math assistant."
ASK agent "What's 42 raised to the power of 9?"
ASK agent "Solve the equation x^2 + 5x + 6 = 0"
ASK agent "What's the derivative of sin(x) * cos(x)?"
```

> **Imported:**
> - `Agent` from `strands`: the agent that gets the tool and the system prompt.
> - `calculator` from `strands_tools`: a ready-made maths tool, so you do not write one.

```python reveal title="shivank2/05_prebuilt_tools.py"
from strands import Agent
from strands_tools import calculator

agent = Agent(
    tools=[calculator],
    system_prompt="You are a helpful math assistant."
)

agent("What's 42 raised to the power of 9?")
agent("Solve the equation x^2 + 5x + 6 = 0")
agent("What's the derivative of sin(x) * cos(x)?")
```

Note this also introduces the **system prompt** — standing instructions that shape the agent's behaviour across every request.

▶ Run it

```text
python shivank2/05_prebuilt_tools.py
```

#### 13.2 · Combining several pre-built tools

Fetch data from the web, do maths on it, and write a file — one request, three tools.

```pseudo title="shivank2/06_multi_prebuilt_tools.py"
CREATE agent = Agent with http_request, calculator and file_write, plus the system prompt "You help with data analysis tasks."
SET the environment variable BYPASS_TOOL_CONSENT = "true"   // turns off the approval prompts for these tools
ASK agent to
    fetch stock data from the Yahoo Finance chart API for AAPL (interval 1d, range 5d)
    extract the latest closing prices
    calculate the average price over the period
    save the results to stock_summary.txt
```

> **Imported:**
> - `os` Python standard library: sets the `BYPASS_TOOL_CONSENT` environment variable.
> - `Agent` from `strands`: the agent that is given the three tools.
> - `http_request` from `strands_tools`: a ready-made tool that fetches data from a URL.
> - `calculator` from `strands_tools`: a ready-made tool that does the maths.
> - `file_write` from `strands_tools`: a ready-made tool that writes a file.

```python reveal title="shivank2/06_multi_prebuilt_tools.py"
import os
from strands import Agent
from strands_tools import http_request, calculator, file_write

agent = Agent(
    tools=[http_request, calculator, file_write],
    system_prompt="You help with data analysis tasks."
)

os.environ["BYPASS_TOOL_CONSENT"] = "true"

agent("""
Fetch stock data from https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=5d,
extract the latest closing prices,
calculate the average price over the period,
and save the results to stock_summary.txt
""")
```

▶ Run it

```text
python shivank2/06_multi_prebuilt_tools.py
```

> **Explain BYPASS_TOOL_CONSENT before running it:**
> Some tools are sensitive — they write files or touch cloud resources — so Strands **pauses and asks permission** before running them. Setting `BYPASS_TOOL_CONSENT="true"` turns that prompt off so the cell runs unattended. Teach it as a real safety feature: in production you often *want* a human approving actions. If a cell seems to hang with `[*]`, it is waiting for your `y` at a hidden prompt.

Section 14 · Hands-on

## AWS integration with use_aws

One tool, many services. `use_aws` translates plain English into AWS API calls.

```pseudo title="shivank2/07_use_aws.py"
CREATE agent = Agent with the use_aws tool and the system prompt "You are an AWS assistant that helps manage cloud resources."
ASK agent "List all S3 buckets in my account"
```

> **Imported:**
> - `Agent` from `strands`: the agent that gets the tool and the system prompt.
> - `use_aws` from `strands_tools`: a ready-made tool that can call many AWS services.

```python reveal title="shivank2/07_use_aws.py"
from strands import Agent
from strands_tools import use_aws

agent = Agent(
    tools=[use_aws],
    system_prompt="You are an AWS assistant that helps manage cloud resources."
)

agent("List all S3 buckets in my account")
```

The same single tool handles completely different services — Other examples:

```pseudo title="one tool, three services"
// DynamoDB
ASK agent "Look up customer ID 12345 in the DynamoDB customers table and update their email to newemail@example.com"

// Lambda
ASK agent "Invoke the Lambda function 'order-processor' with order ID 67890"
```

```python reveal title="one tool, three services"
# DynamoDB
agent("Look up customer ID 12345 in the DynamoDB customers table and update their email to newemail@example.com")

# Lambda
agent("Invoke the Lambda function 'order-processor' with order ID 67890")
```

> **Before you run this:**
> These examples assume the AWS resources already exist in your account. The S3 bucket, DynamoDB table, and Lambda function referenced must exist for the snippets to work. While you are learning, **stick to the S3 listing example** — it works on any account, even an empty one (an empty list is a valid result, not an error).

Notice what just happened: you described what you wanted in plain English, and the agent figured out the AWS API calls. **You didn't write boto3 code, didn't handle AWS responses, and didn't even specify which operation to use.**

▶ Run it

```text
python shivank2/07_use_aws.py
```

> **Handle with care:**
> `use_aws` can *modify* real resources. Stick to read-only requests ("list", "describe") while you learn, and always work in a sandbox account, never production. This is exactly why the consent prompt exists — read it before you type `y`.

Section 15 · Hands-on

## Building custom tools

When community tools don't fit — an internal API, a proprietary database, something new — you write your own. For example: an online store checking inventory.

```pseudo title="shivank2/04_custom_tool_inventory.py"
DEFINE check_inventory(product_id) as a tool
    SET inventory = {PROD-123: 15, PROD-456: 0, PROD-789: 8}   // stands in for a real database
    SET quantity = inventory[product_id], or 0 if the id is unknown
    IF quantity > 0 THEN
        RETURN "Product " + product_id + " is in stock. We have " + quantity + " units available."
    ELSE
        RETURN "Product " + product_id + " is currently out of stock."

CREATE agent = Agent with the check_inventory tool
ASK agent "Is PROD-123 in stock?"
ASK agent "Do we have PROD-456 available?"
ASK agent "Check inventory for PROD-789"
ASK agent "Can I order PROD-123 right now?"   // four phrasings, same tool
```

> **Imported:**
> - `Agent` from `strands`: the agent that is given the tool.
> - `tool` from `strands`: the decorator that turns `check_inventory` into a tool.

```python reveal title="shivank2/04_custom_tool_inventory.py"
from strands import Agent, tool

@tool
def check_inventory(product_id: str) -> str:
    """Check if a product is in stock.

    Args:
        product_id: The product ID to check (e.g., "PROD-123")
    """
    # This is where you'd query your actual database
    inventory = {
        "PROD-123": 15,
        "PROD-456": 0,
        "PROD-789": 8
    }

    quantity = inventory.get(product_id, 0)

    if quantity > 0:
        return f"Product {product_id} is in stock. We have {quantity} units available."
    else:
        return f"Product {product_id} is currently out of stock."

agent = Agent(tools=[check_inventory])

# All of these work — the agent understands intent, not just keywords
agent("Is PROD-123 in stock?")
agent("Do we have PROD-456 available?")
agent("Check inventory for PROD-789")
agent("Can I order PROD-123 right now?")
```

Note the mock dictionary: in production you'd replace it with real database queries or an API call. The *agent-facing* part — decorator, type hints, docstring — stays identical either way.

▶ Run it

```text
python shivank2/04_custom_tool_inventory.py
```

> **Exercise — pick one of these:**
> Build a tool for a problem you actually care about. Ideas: check the weather in your city (call a weather API) · validate email format · calculate age from birthdate · calculate BMI · calculate shipping costs from weight and distance. *Don't worry if the logic is simple — what matters is seeing how a custom tool fits into the agent workflow.*

Section 16 · Advanced
