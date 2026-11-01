# Lab: your Hello World agent

## 1.8 Lab: your Hello World agent

Theory done. Now you set up your environment, check your AWS access, and build your first agent, adding a tool, a prebuilt tool and a system prompt one step at a time.

Everything for this lab is in the `section-01-your-first-agent` folder of the course code, plus two helpers in `setup/`.

| File | What it does |
| --- | --- |
| `01_hello_agent.ipynb` | **Start here.** Model choice, a one-line agent, your own tool, a prebuilt tool, a system prompt |
| `hello_agent.py` | The smallest possible Strands agent, as a script |
| `hello_langgraph_agent.py` | The same idea built with LangChain and LangGraph: a ReAct agent with one tool |
| `requirements.txt` | The Python libraries this section needs |
| `setup/check_setup.py` | Pre-flight check: are your AWS credentials, Region and model access working? |
| `setup/iam-policy-course.json` | An IAM policy that covers every lab in the course (sandbox accounts only) |

#### What you need

1. 1 Python 3.10 or newer 3.11 or 3.12 is recommended. Check with `python3 --version`.
2. 2 An AWS account Use a sandbox or learning account, never a production one. Work in Region **us-east-1** (N. Virginia), where every AgentCore feature used in the course is available.
3. 3 Tools on your machine AWS CLI v2, Git, and Jupyter (JupyterLab or VS Code with the Jupyter extension). Windows users: run shell scripts from WSL or Git Bash.
4. 4 Access to the models on Amazon Bedrock Bedrock's serverless models are now enabled by default; there's no model-access page to click through any more. One exception: **Anthropic models need a one-time "first time use" form** per AWS account (or once for the whole organisation). If your first Claude call says `AccessDeniedException`, open the Bedrock console, pick a Claude model, and submit the form. The first-ever use of a model also needs AWS Marketplace subscribe permissions and a valid payment method on the account.
5. 5 IAM permissions Permissions attached to your user, role or SSO permission set. Details just below.
6. 6 A development environment Either your own laptop with VS Code, Kiro, Cursor or JupyterLab (Option A), or Amazon SageMaker Studio with a JupyterLab space (Option B).

##### The models used in this course

| Model | ID used in the code | Used for |
| --- | --- | --- |
| Claude Sonnet 4.6 (default) | `global.anthropic.claude-sonnet-4-6` | Strong reasoning and tool use; the default brain |
| Claude Haiku 4.5 | `global.anthropic.claude-haiku-4-5-20251001-v1:0` | Faster and cheaper: memory, evaluation judge, Lambda |
| Titan Text Embeddings v2 | `amazon.titan-embed-text-v2:0` | Embeddings for agent memory (Section 3) |

The `global.` prefix is a **cross-Region inference profile**: Bedrock routes each request to whichever AWS Region can serve it best, and it works from any supported source Region, including India. To switch the model everywhere without touching code, set an environment variable:

```pseudo title="terminal"
SET BEDROCK_MODEL_ID = global.anthropic.claude-haiku-4-5-20251001-v1:0   // this terminal session only; the scripts read it
```

```bash reveal title="terminal"
export BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0
```

{{diagram:1}}

*One agent call, end to end. If anything fails, it's almost always the red box (credentials or permissions) or the Region. That's exactly what `check_setup.py` tests first.*

##### IAM permissions

**IAM** decides what your user or role may do. At a minimum, this section needs permission to call Bedrock models. Later sections need more:

- `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`: call models, with and without streaming (needed now)
- `sagemaker:InvokeEndpoint`: only if you call models hosted on SageMaker AI
- `s3:GetObject` and `s3:PutObject`: read and write data and artefacts
- `bedrock-agentcore:*`: needed for AgentCore in Sections 3, 6 and 7

In a sandbox account, an administrator user is simplest. Otherwise attach `setup/iam-policy-course.json`, which covers every lab in the course. It is deliberately broad, because labs create roles, gateways and Lambda functions, so treat it as sandbox-only.

> **Think of it like this:**
> IAM is your **office access card**. Credentials prove who you are at the gate; the policy decides which doors your card opens. `bedrock:InvokeModel` is the door to the model room. No door, no answer, however correct your code is.

##### Laptop or SageMaker Studio?

| Requirement | Option A: your laptop | Option B: SageMaker Studio |
| --- | --- | --- |
| AWS credentials | `aws configure`, AWS SSO, or environment variables | Automatic, from the Studio execution role |
| IAM permissions | Attach to your IAM user, role or SSO permission set | Attach to the execution role |
| Bedrock model access | On by default; submit the Anthropic first-time use form once | Same |
| Python packages | `pip install` into a virtual environment | `%pip install` inside the notebook |
| Compute | Your own machine | A JupyterLab space, `ml.m5.large` or bigger, at least 20 GB storage |

#### Set up your environment

##### Option A: your laptop (VS Code, Kiro, Cursor or JupyterLab)

1. 1 Connect to your AWS account With access keys use `aws configure`. With IAM Identity Center (the AWS access portal), use SSO and export the profile name so every tool picks it up.
2. 2 Create a virtual environment A **virtual environment** keeps this course's libraries separate from everything else on your machine.
3. 3 Set the Region and run the check Point everything at us-east-1, then run the pre-flight script.

```pseudo title="terminal: 1. credentials"
RUN aws configure   // enter your access key, secret key and Region (us-east-1)
// or, with IAM Identity Center (SSO):
RUN aws configure sso
RUN aws sso login --profile my-profile
SET AWS_PROFILE = my-profile   // every tool then picks up this profile
```

```bash reveal title="terminal: 1. credentials"
aws configure                 # access key, secret, region = us-east-1
# or, with IAM Identity Center:
aws configure sso && aws sso login --profile my-profile && export AWS_PROFILE=my-profile
```

```pseudo title="terminal: 2 and 3. environment and check"
RUN cd future-with-shivank-agentic-ai-on-aws
RUN python3 -m venv .venv   // create a virtual environment for the course libraries
RUN source .venv/bin/activate   // on Windows: .venv\Scripts\activate
RUN pip install --upgrade pip boto3
SET AWS_REGION = us-east-1
SET AWS_DEFAULT_REGION = us-east-1
RUN python setup/check_setup.py   // the pre-flight check
```

```bash reveal title="terminal: 2 and 3. environment and check"
cd future-with-shivank-agentic-ai-on-aws
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip boto3

export AWS_REGION=us-east-1
export AWS_DEFAULT_REGION=us-east-1

python setup/check_setup.py
```

You should see a ✅ for both models. Something like this:

```text title="expected output (your values will differ)"
Python  : 3.12.4
Account : 123456789012
Caller  : arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_CourseAdmin_1a2b3c/learner
Region  : us-east-1
✅ global.anthropic.claude-sonnet-4-6: ready
✅ global.anthropic.claude-haiku-4-5-20251001-v1:0: ready

If both models replied, you're ready for Section 1.
```

```pseudo title="setup/check_setup.py"
SET REGION = environment variable AWS_REGION, or AWS_DEFAULT_REGION, or "us-east-1"
SET MODELS = your default model (BEDROCK_MODEL_ID) and Claude Haiku 4.5
PRINT the Python version
IF Python is older than 3.10 THEN PRINT a warning
TRY
    CALL STS get_caller_identity   // asks AWS who you are
    PRINT the account and the caller ARN
ON ERROR
    STOP with "AWS credentials not working" and the error
PRINT REGION
CREATE runtime = Bedrock runtime client in REGION
FOR EACH model_id IN MODELS:
    TRY
        ASK model_id "Reply with the single word: ready"   // one tiny Converse call, capped at 10 tokens
        PRINT model_id and the reply
    ON ERROR
        PRINT model_id and the error
PRINT "If both models replied, you're ready for Section 1."
```

> **Imported:**
> - `os` Python standard library: reads the Region and the default model ID from environment variables.
> - `sys` Python standard library: reports the Python version and stops the script with a message if AWS credentials fail.
> - `boto3` package boto3, the AWS SDK for Python: creates the AWS clients that check your identity and call Bedrock.

```python reveal title="setup/check_setup.py"
"""Quick pre-flight check: AWS credentials, region, and Bedrock model access.

Run:  python setup/check_setup.py
"""

import os
import sys

import boto3

REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
MODELS = [
    os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6"),
    "global.anthropic.claude-haiku-4-5-20251001-v1:0",
]

print(f"Python  : {sys.version.split()[0]}")
if sys.version_info < (3, 10):
    print("  ❌ Python 3.10+ is required (3.11 or 3.12 recommended)")

try:
    ident = boto3.client("sts", region_name=REGION).get_caller_identity()
    print(f"Account : {ident['Account']}")
    print(f"Caller  : {ident['Arn']}")
except Exception as e:
    sys.exit(f"❌ AWS credentials not working: {e}")

print(f"Region  : {REGION}")

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

print("\nIf both models replied, you're ready for Section 1.")
```

1. **REGION = os.getenv(…)** Read the Region from the environment, falling back to us-east-1.
2. **MODELS = […]** The two models every lab relies on: your chosen default and Haiku.
3. **sys.version_info** Fail early if Python is too old.
4. **get_caller_identity()** Asks AWS **STS** "who am I?". If this fails, your credentials are the problem, not your code.
5. **runtime.converse(…)** A real, tiny model call capped at 10 tokens. If this fails but STS worked, the problem is permissions, the Region, or model access.

##### Option B: Amazon SageMaker Studio

In Studio, credentials come from the execution role automatically, so there's no `aws configure`. Attach the permissions above to that execution role.

1. 1 Open your domain In the SageMaker AI console, choose **Domains** in the navigation pane, then open your domain.
2. 2 Go to Studio In the navigation pane, under **Applications and IDEs**, choose **Studio**.
3. 3 Launch Studio for your user On the **User profiles** tab, find your user profile, then choose **Launch** and **Studio**.

{{diagram:2}}

*Launching SageMaker Studio from your user profile (simplified). The console layout changes from time to time, but the path stays the same: Domains, your domain, User profiles, Launch, Studio.*

1. 4 Create and run a JupyterLab space In Studio, open **JupyterLab**, create a space, choose an `ml.m5.large` instance (or bigger) with at least 20 GB of storage, choose **Run space**, then **Open JupyterLab**.

{{diagram:3}}

*A running JupyterLab space (simplified). Pick the instance type before you run the space; you can stop it any time to stop paying for it.*

1. 5 Bring in the course code Upload the course code with JupyterLab's upload button (or clone it if you have it in a Git repository). Open a terminal (File, New, Terminal). If you uploaded a zip, unzip it, then go into the Section 1 folder.
2. 6 Install and restart Open `01_hello_agent.ipynb` and run the first cell to install the libraries. Then **restart the kernel** (Kernel, Restart) so Python picks up what you just installed.

```pseudo title="JupyterLab terminal"
RUN unzip future-with-shivank-agentic-ai-on-aws.zip   // unpacks the course code
RUN cd future-with-shivank-agentic-ai-on-aws/section-01-your-first-agent   // go into the Section 1 folder
```

```bash reveal title="JupyterLab terminal"
unzip future-with-shivank-agentic-ai-on-aws.zip
cd future-with-shivank-agentic-ai-on-aws/section-01-your-first-agent
```

> **New word: kernel:**
> The **kernel** is the Python process running behind a notebook. Libraries installed while it's running aren't always visible to it, so after installing you restart it to start fresh.

#### Build it, step by step

Open `01_hello_agent.ipynb` (in JupyterLab or VS Code) and run each cell in order. The notebook is organised as Steps 1 to 6; here is every code cell, with what it does and why.

##### Step 1. Install the dependencies

```pseudo title="01_hello_agent.ipynb, Step 1"
RUN %pip install -q -r requirements.txt   // install the libraries listed in requirements.txt, quietly
```

```python reveal title="01_hello_agent.ipynb, Step 1"
%pip install -q -r requirements.txt
```

```pseudo title="requirements.txt"
// version ranges: new enough for the code, below the next major version
LOAD strands-agents from 1.60.0, below 2.0.0
LOAD strands-agents-tools from 0.8.9, below 0.9.0
LOAD langchain from 1.4.0, langchain-aws from 1.8.0 and langgraph from 1.2.0, each below 2.0.0   // only for the LangGraph script
LOAD boto3 from 1.40.0
```

```txt reveal title="requirements.txt"
# Section 1 — Your First AI Agent
strands-agents>=1.60.0,<2.0.0
strands-agents-tools>=0.8.9,<0.9.0
langchain>=1.4.0,<2.0.0
langchain-aws>=1.8.0,<2.0.0
langgraph>=1.2.0,<2.0.0
boto3>=1.40.0
```

1. **strands-agents** The Strands Agents SDK: `Agent`, `tool`, `BedrockModel`.
2. **strands-agents-tools** Ready-made tools, such as `calculator`.
3. **langchain, langchain-aws, langgraph** Only for the LangGraph comparison script.
4. **boto3** The AWS SDK for Python; Strands uses it under the hood to call Bedrock.
5. **>=1.60.0,<2.0.0** Version ranges: new enough for our code, but not a future major version that might break it.

##### Step 2. Choose the model

Every example in the course reads the model from one variable. Change it here, or set `BEDROCK_MODEL_ID`, to try a different model: `global.anthropic.claude-sonnet-4-6` (default, strong reasoning and tool use) or `global.anthropic.claude-haiku-4-5-20251001-v1:0` (faster and cheaper).

```pseudo title="01_hello_agent.ipynb, Step 2"
SET MODEL_ID = environment variable BEDROCK_MODEL_ID, or "global.anthropic.claude-sonnet-4-6"
SET REGION = environment variable AWS_REGION, or AWS_DEFAULT_REGION, or "us-east-1"
SET AWS_REGION = REGION, but only if AWS_REGION is not already set   // so the AWS SDK uses the same Region
PRINT the model and the Region
```

> **Imported:**
> - `os` Python standard library: reads the model ID and Region from environment variables, and sets AWS_REGION if it is missing.

```python reveal title="01_hello_agent.ipynb, Step 2"
import os

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

print(f"Model : {MODEL_ID}")
print(f"Region: {REGION}")
```

> **Think of it like this:**
> `os.getenv("NAME", default)` is a settings knob that lives *outside* the code: "use the value of this environment variable if someone set it, otherwise use the default". That's how one notebook runs on Sonnet for you and Haiku for a classmate, with no edits.

##### Step 3. Create your first agent

```pseudo title="01_hello_agent.ipynb, Step 3"
CREATE model = BedrockModel for MODEL_ID in REGION
CREATE agent = Agent that uses model   // an agent = a model + (optional) tools + (optional) system prompt
SET response = the agent's answer to "Explain Amazon Bedrock AgentCore in three sentences."
```

> **Imported:**
> - `Agent` from `strands`, package strands-agents: the agent that combines the model with its tools and prompt.
> - `BedrockModel` from `strands.models.bedrock`, package strands-agents: the model adapter that sends each call to Amazon Bedrock.

```python reveal title="01_hello_agent.ipynb, Step 3"
from strands import Agent
from strands.models.bedrock import BedrockModel

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)

# An agent = a model + (optional) tools + (optional) system prompt
agent = Agent(model=model)

response = agent("Explain Amazon Bedrock AgentCore in three sentences.")
```

{{diagram:4}}

*The whole recipe. Steps 4, 5 and 6 below each fill in one of the optional slots.*

The agent **streams** its answer as it generates it, so you see words appear live. The returned `response` object holds the full result: the final text, the token usage, and the stop reason.

```pseudo title="01_hello_agent.ipynb, Step 3, next cell"
PRINT the stop reason of response   // end_turn: the model finished without asking for a tool
PRINT the token usage of response   // what you are billed for: input plus output tokens
```

```python reveal title="01_hello_agent.ipynb, Step 3, next cell"
print("Stop reason:", response.stop_reason)
print("Tokens used:", response.metrics.accumulated_usage)
```

```text title="example output (numbers will differ)"
Stop reason: end_turn
Tokens used: {'inputTokens': 21, 'outputTokens': 112, 'totalTokens': 133}
```

`end_turn` means the model finished without asking for a tool, so the loop ran exactly once. **Tokens** are what you pay for: input tokens (what you sent) plus output tokens (what it wrote).

The script version, `hello_agent.py`, is the same thing outside a notebook:

```pseudo title="section-01-your-first-agent/hello_agent.py"
SET MODEL_ID and REGION from environment variables, with defaults
CREATE model = BedrockModel for MODEL_ID in REGION
CREATE agent = Agent that uses model
SET response = the agent's answer to "Hello! Tell me a fun fact about AI agents."   // streams to the terminal as it is written
PRINT an empty line, then a line of 60 dashes
PRINT response   // the same answer again, as the final result
```

> **Imported:**
> - `os` Python standard library: reads settings such as the model ID and Region from environment variables.
> - `Agent` from `strands`, package strands-agents: the agent that combines the model with its tools and prompt.
> - `BedrockModel` from `strands.models.bedrock`, package strands-agents: the model adapter that sends each call to Amazon Bedrock.

```python reveal title="section-01-your-first-agent/hello_agent.py"
"""Section 1: Hello World agent with the Strands Agents SDK on Amazon Bedrock.

Run:
    python hello_agent.py
"""

import os

from strands import Agent
from strands.models.bedrock import BedrockModel

# One place to choose the model. Override without editing code:
#   export BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
agent = Agent(model=model)

response = agent("Hello! Tell me a fun fact about AI agents.")
print()
print("-" * 60)
print(response)
```

> **Why you see the answer twice:**
> Run `python hello_agent.py` and the answer appears, then a line of dashes, then the same answer again. The first copy is Strands streaming the text live as the model writes it. The second is `print(response)` printing the final result object. The dashes are there so you can tell them apart.

##### Step 4. Give the agent a tool

A tool is just a Python function with three things: the `@tool` **decorator**, **type hints** so the model knows what arguments to send, and a **docstring** so the model knows *when* to use it.

```pseudo title="01_hello_agent.ipynb, Step 4"
DEFINE current_time(timezone, default "Asia/Kolkata")   // @tool: the agent may call this function
    RETURN the current date and time in that timezone, as readable text
CREATE agent = Agent with model and the tool current_time
ASK agent "What time is it right now in Bangalore and in New York?"
```

> **Imported:**
> - `datetime` from `datetime`, Python standard library: gets the current date and time.
> - `ZoneInfo` from `zoneinfo`, Python standard library: turns a timezone name such as Asia/Kolkata into a timezone.
> - `tool` from `strands`, package strands-agents: the decorator that registers the function as a tool the agent can call.

```python reveal title="01_hello_agent.ipynb, Step 4"
from datetime import datetime
from zoneinfo import ZoneInfo

from strands import tool

@tool
def current_time(timezone: str = "Asia/Kolkata") -> str:
    """Get the current date and time in a given IANA timezone.

    Args:
        timezone: IANA timezone name, for example "Asia/Kolkata" or "America/New_York".
    """
    return datetime.now(ZoneInfo(timezone)).strftime("%A, %d %B %Y %I:%M %p %Z")

agent = Agent(model=model, tools=[current_time])
agent("What time is it right now in Bangalore and in New York?")
```

How each part of the function is used

1. @ @tool Registers the function as a tool the agent can offer to the model.
2. : timezone: str = "Asia/Kolkata" Becomes the input schema: one text argument, optional, with a default.
3. " The docstring Becomes the description. The model reads it to decide whether this tool fits the question.

Roughly what the model is shown

```pseudo
DEFINE the tool description that the model is shown:
    SET name = "current_time"
    SET description = the docstring: "Get the current date and time in a given IANA timezone."
    SET inputSchema = one text argument, timezone, described as an IANA timezone name
    SET required = none, so the argument is optional
```

View code

{ "name": "current_time", "description": "Get the current date and time in a given IANA timezone.", "inputSchema": {"json": { "type": "object", "properties": { "timezone": { "type": "string", "description": "IANA timezone name, for example \"Asia/Kolkata\" or \"America/New_York\"." } }, "required": [] }} }

> **Think of it like this:**
> The docstring is the **description on a restaurant menu**. The waiter (the model) can't taste the food in the kitchen (your code); it recommends a dish only from what the menu says. Vague menu, wrong dish. That's why good docstrings matter so much in Section 2.

Ask about Bangalore and New York, and the model will request `current_time` twice, once per timezone, read the two results and answer. That's the agent loop from 1.7, with real tools. You can replay it in the loop simulator above.

##### Step 5. Use a prebuilt tool

`strands-agents-tools` ships ready-made tools. Here the agent gets a `calculator` so it doesn't have to do arithmetic "in its head", which LLMs are surprisingly unreliable at.

```pseudo title="01_hello_agent.ipynb, Step 5"
LOAD the prebuilt calculator tool
CREATE agent = Agent with model and the tools calculator and current_time
ASK agent "What is 18% GST on a laptop that costs Rs 84,999? Give me the final price too."
```

> **Imported:**
> - `calculator` from `strands_tools`, package strands-agents-tools: a ready-made tool that does exact arithmetic for the agent.

```python reveal title="01_hello_agent.ipynb, Step 5"
from strands_tools import calculator

agent = Agent(model=model, tools=[calculator, current_time])
agent("What is 18% GST on a laptop that costs Rs 84,999? Give me the final price too.")
```

Expected numbers: GST = 84,999 × 0.18 = **₹15,299.82**, final price = **₹1,00,298.82**. Notice the agent has two tools but uses only the one it needs.

##### Step 6. Shape behaviour with a system prompt

The **system prompt** sets the agent's role, tone and rules for every turn of the conversation.

```pseudo title="01_hello_agent.ipynb, Step 6"
CREATE agent = Agent with model and system_prompt:
    SET system_prompt = a patient tutor for engineers new to AI agents, using one real-world analogy and keeping answers under 120 words
ASK agent "What is the difference between an LLM and an AI agent?"
```

```python reveal title="01_hello_agent.ipynb, Step 6"
agent = Agent(
    model=model,
    system_prompt=(
        "You are a patient tutor for engineers who are new to AI agents. "
        "Explain ideas with one real-world analogy and keep answers under 120 words."
    ),
)
agent("What is the difference between an LLM and an AI agent?")
```

> **Think of it like this:**
> A system prompt is the **briefing a new employee gets on day one**: who you are here, how you talk to customers, what you never do. The user's prompt is each customer's request; the briefing applies to all of them.

Try it

##### Agent builder: switch things on and watch the code change

Model

Tools

System prompt

on Add a system prompt

**Default system prompt in the builder:** You are a patient tutor for engineers who are new to AI agents. Keep answers under 120 words.

```text title="my_agent.py (generated)"

```

> **What you just did:**
> Built an agent in one line, added your own tool and a prebuilt tool, and controlled its behaviour with a system prompt. Next, run the two scripts in the folder to see the same idea as plain Python files, including one built with LangGraph.

#### The same idea in LangGraph

Strands isn't the only way. `hello_langgraph_agent.py` builds the same kind of agent with LangChain's `create_agent`, which runs on the LangGraph runtime and replaces the older `langgraph.prebuilt.create_react_agent`. It builds a **ReAct** agent: reason, act with a tool, observe, repeat. The same loop you met in 1.7, just with different wording.

```pseudo title="section-01-your-first-agent/hello_langgraph_agent.py"
SET MODEL_ID and REGION from environment variables, with defaults
DEFINE greet(name)   // the @tool decorator lets the agent call it
    RETURN "Hello, " + name + "! Welcome to the world of AI agents."
CREATE llm = chat model for MODEL_ID through the Bedrock Converse API, in REGION
CREATE agent = create_agent with llm, the tool greet, and the system prompt "You are a friendly assistant."
SET response = agent.invoke with the message "Please greet Alice and Bob."
FOR EACH message IN response["messages"]:
    PRINT the message type and its text   // user, then ai, tool and the final answer
```

> **Imported:**
> - `os` Python standard library: reads the model ID and Region from environment variables.
> - `create_agent` from `langchain.agents`, package langchain: builds a ReAct-style agent that runs on the LangGraph runtime.
> - `init_chat_model` from `langchain.chat_models`, package langchain: creates the chat model for the Bedrock Converse API.
> - `tool` from `langchain.tools`, package langchain: the decorator that turns `greet` into a tool.

```python reveal title="section-01-your-first-agent/hello_langgraph_agent.py"
"""Section 1: Hello World agent with LangGraph / LangChain on Amazon Bedrock.

`create_agent` (from langchain.agents) is the current way to build a
ReAct-style agent that runs on the LangGraph runtime. It replaces the older
`langgraph.prebuilt.create_react_agent`.

Run:
    python hello_langgraph_agent.py
"""

import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

# A simple tool the agent can call
@tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to the world of AI agents."

# Initialize the LLM via the Bedrock Converse API
llm = init_chat_model(MODEL_ID, model_provider="bedrock_converse", region_name=REGION)

# Create a ReAct agent with the tool
agent = create_agent(model=llm, tools=[greet], system_prompt="You are a friendly assistant.")

# Run the agent
response = agent.invoke({"messages": [{"role": "user", "content": "Please greet Alice and Bob."}]})

# Print every message in the conversation: user -> AI (tool calls) -> tool results -> AI answer
for message in response["messages"]:
    print(f"{message.type}: {message.text}")
```

Because the script prints every message, you can see the loop itself in the output:

```text title="example output (wording will differ)"
human: Please greet Alice and Bob.
ai: I'll greet both Alice and Bob for you!        ← model asks for greet("Alice") and greet("Bob")
tool: Hello, Alice! Welcome to the world of AI agents.
tool: Hello, Bob! Welcome to the world of AI agents.
ai: I've greeted both Alice and Bob! They've been welcomed to the world of AI agents.
```

| Idea | Strands | LangChain / LangGraph |
| --- | --- | --- |
| Model | `BedrockModel(model_id=…)` | `init_chat_model(…, model_provider="bedrock_converse")` |
| Tool | `@tool` from `strands` | `@tool` from `langchain.tools` |
| Agent | `Agent(model, tools, system_prompt)` | `create_agent(model, tools, system_prompt)` |
| Run it | `agent("…")` | `agent.invoke({"messages": […]})` |

#### Strands vs LangChain vs LangGraph: which when?

|  | Strands Agents | LangChain | LangGraph |
| --- | --- | --- | --- |
| Approach | Agent-first SDK: model + tools + prompt | Building blocks: prompts, parsers, loaders, integrations | Stateful graph orchestration |
| Boilerplate | Minimal | Moderate | More setup, more control |
| State | Built in (plus AgentCore Memory or session managers) | Manual | Built in, with checkpointers |
| Best for | Fast, AWS-native agents | RAG pipelines and integrations | Complex flows with loops, branches, human-in-the-loop |

{{diagram:5}}

*A quick decision guide. Graph and swarm patterns are in Section 4, AgentCore Memory in Section 3, AgentCore Runtime in Section 6.*

> **Think of it like this:**
> **Strands is an automatic car**: get in and drive. **LangChain is a box of Lego**: every part you could want, you assemble them. **LangGraph is designing a metro map**: you draw every station and track, so you control exactly where each train can go, including loops and stops where a human gets on.

#### When something goes wrong

| Error | What it usually means and how to fix it |
| --- | --- |
| `AccessDeniedException` calling Bedrock | Check IAM permissions and that `AWS_REGION` is set. For Claude models, make sure the Anthropic first-time use form has been submitted for the account. |
| `ValidationException … model identifier is invalid` or "on-demand throughput isn't supported" | Use an inference-profile ID (with `global.` or `us.`), as in the model table. |
| `ResourceNotFoundException … Legacy model` or end-of-life | That model was retired. Set `BEDROCK_MODEL_ID` to a current model. |
| `ThrottlingException` | Too many requests. Wait a minute and retry; use Haiku for bulk runs. |
| Credentials errors or "token has expired" | Your SSO session ran out. Run `aws sso login --profile my-profile` again. |
| `ModuleNotFoundError` in a notebook | Run the `%pip install -r requirements.txt` cell, then restart the kernel. |

> **Cost and clean-up:**
> This section creates no AWS resources; you only pay per model call, which for these labs is a few cents. There's nothing to clean up. Later sections that create resources end with a clean-up cell or a `cleanup.sh` script; always run it before moving on.
