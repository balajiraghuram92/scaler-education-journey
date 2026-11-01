# The revision at a glance

**Future with Shivank** Part 00 · Revision

Colour code used in every diagram

LLM, the brain Tools and actions Prompts, data, results You and your setup The agent itself

Part 00: AWS Revision

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Revision:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Scaler AWS AI Bootcamp, the revision session before Lesson 1

#### Part 00 AWS Revision

Before we build agents on AWS, we revise the two warm-up sections: how a LangChain *chain* turns a prompt into an answer, and how an *agent* adds tools, real web search and structured results on top. Every idea here comes back in Lesson 1.

Folder `day1/section1` chains Folder `day1/section2` agents Models: OpenAI `gpt-5.6-sol` · Ollama `gemma3:270m` Search: Tavily

{{diagram:1}}

*Eight small scripts, one idea at a time. Each script changes exactly one thing compared with the one before it, so you can open two side by side and see the difference. A helper, `agent_trace_printer.py`, prints every agent run in Part B.*

## 0.0 The revision at a glance

Part A is about talking to a model reliably. Part B is about letting the model decide to *do* something, by calling a tool, and then reading what it did.

> **Part A: LangChain foundations:**
> Keep API keys in a `.env` file. Build a chain from a **PromptTemplate** and a **chat model**. Swap the paid cloud model for a free local one. Look inside the **AIMessage** that comes back.

> **Part B: your first agent:**
> Turn a Python function into a **tool**, build an **agent** with `create_agent`, give it real web search through Tavily, and make it return a validated object instead of a paragraph.

> **Why "AWS Revision" when the code uses OpenAI?:**
> This is the revision session that opens the AWS bootcamp. The scripts run on OpenAI and Ollama so that anyone can try them without an AWS account. The ideas are the same ones you'll use on Amazon Bedrock in Lesson 1: a prompt, a model, tools, and a loop that runs until the model stops asking for tools. The recap maps each one to its Lesson 1 equivalent.

#### Set up once

Each section folder is its own small project. **uv** reads the project file, creates a **virtual environment** and installs the exact locked versions, so everyone in the class runs the same code.

```pseudo title="terminal, in each section folder"
RUN uv sync                      // create .venv and install the locked versions
RUN cp .env.example .env         // copy the template, then paste your keys into .env
```

```bash reveal title="terminal, in each section folder"
uv sync                      # create .venv, install locked versions
cp .env.example .env         # then paste your keys into .env
```

| Script | What it shows | Needs |
| --- | --- | --- |
| A · 01_hello_world_env_setup.py | Loading keys from `.env` safely, printing a masked key | nothing, or `OPENAI_API_KEY` |
| A · 02_summary_chain_openai.py | Your first chain: `PromptTemplate \| ChatOpenAI` | `OPENAI_API_KEY` |
| A · 03_summary_chain_ollama.py | The same chain on a local model | Ollama + `gemma3:270m` |
| A · 04_inspect_the_response_object.py | Every useful field of the returned `AIMessage` | `OPENAI_API_KEY` or `--local` |
| B · 01_agent_with_placeholder_tool.py | The agent loop with a fake `search` tool | `OPENAI_API_KEY` |
| B · 02_agent_with_tavily_sdk_tool.py | Your own `search` tool calling the Tavily SDK | + `TAVILY_API_KEY` |
| B · 03_agent_with_builtin_tavily_tool.py | The vendor's ready-made `TavilySearch` tool | + `TAVILY_API_KEY` |
| B · 04_agent_with_structured_output.py | `response_format=AgentAnswer` returns a Pydantic object | + `TAVILY_API_KEY` |

Run any script with `uv run python <file>.py`. For the local model you also need **Ollama** installed and running, plus the tiny model downloaded once with `ollama pull gemma3:270m` (about 300 MB). A free Tavily key (1,000 credits a month) comes from app.tavily.com.

## 0.1 Keep keys out of your code

Before talking to any model you need two boring but critical things: Python runs your project, and your secret **API keys** are loaded from a file, never typed into code.

A **.env file** is a plain text file of `KEY=value` lines. It's listed in `.gitignore`, so it never reaches GitHub. Every SDK (OpenAI, LangSmith, Tavily) looks for its key in an **environment variable** with a fixed name, such as `OPENAI_API_KEY`. `load_dotenv()` copies each line of `.env` into the environment, and the SDKs find their keys on their own.

```pseudo title=".env (placeholders, never commit the real file)"
SET OPENAI_API_KEY to your OpenAI key, which starts with sk-
SET OPENAI_MODEL to gpt-5.6-sol   // optional, this is the default
SET TAVILY_API_KEY to your Tavily key   // only for the search scripts in section 2
// optional tracing: sends every call to LangSmith
SET LANGSMITH_TRACING to true
SET LANGSMITH_API_KEY to your LangSmith key
SET LANGSMITH_PROJECT to the name of your project
```

```bash reveal title=".env (placeholders, never commit the real file)"
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.6-sol          # optional, this is the default
TAVILY_API_KEY=tvly-...           # section 2 only
# optional tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=section-01-langchain-foundations
```

```pseudo title="01_hello_world_env_setup.py"
LOAD every KEY=value line from .env into the environment

DEFINE describe_secret(name):
    SET value = environment variable called name
    IF value is empty THEN
        RETURN "name is missing, copy .env.example to .env"
    RETURN "name loaded" + first 8 characters + total length   // never the full key

PRINT describe_secret("OPENAI_API_KEY")
```

> **Imported:**
> - `os` Python standard library: gives access to environment variables through `os.environ`.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.

```python reveal title="01_hello_world_env_setup.py (core)"
import os
from dotenv import load_dotenv

load_dotenv()

def describe_secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        return f"{name} is missing ❌  → copy .env.example to .env"
    return f"{name} loaded ✅  (starts with {value[:8]!r}, {len(value)} characters)"

print(describe_secret("OPENAI_API_KEY"))
```

1. **load_dotenv()** Reads `.env` from this folder (or a parent) into `os.environ`. A variable already exported in your terminal wins over the file.
2. **os.environ.get(name)** Returns the value, or `None` if it isn't set, so a missing key gives a friendly message instead of a crash.
3. **value[:8]** Shows only the first 8 characters, such as `'sk-proj-'`. That tells you the key *type* but is useless to an attacker.
4. **len(value)** A quick sanity check: a truncated paste shows up as the wrong length.

```text title="expected output"
Hello from Future with Shivank — AI Harness!
OPENAI_API_KEY loaded ✅  (starts with 'sk-proj-', 164 characters)
LANGSMITH_TRACING = (not set) → tracing is optional, see Script 02
```

> **Never print a full key:**
> Terminal output ends up in screenshots, screen recordings and logs. Print a masked prefix like this script does, and if a key ever leaks, revoke it and make a new one.

## 0.2 Your first chain

Three building blocks appear in every later script: a prompt template, a chat model, and the pipe `|` that joins them into a chain.

{{diagram:2}}

*What `chain.invoke({...})` runs. The template turns your dict into prompt text, the model answers, and you read the answer from `.text`. The dict keys must match the template's placeholders.*

#### The prompt is a template with an output contract

Every script summarises the same short biography (of Dr A. P. J. Abdul Kalam) from `sample_data.py`, so cloud and local models can be compared on identical input. The template has one **placeholder**, `{information}`, and a numbered list that tells the model exactly which three parts to return.

```pseudo title="02_summary_chain_openai.py, the template"
SET PROFILE_TEMPLATE to this text   // the numbered list is the output contract
    "Here is a short biography:", then a new line holding {information}
    "Using only this text, give me:", then three numbered parts
        1. A one-line headline about this person
        2. A three-bullet summary a 12-year-old would understand
        3. One question you would ask them in an interview
```

```python reveal title="02_summary_chain_openai.py, the template"
PROFILE_TEMPLATE = """Here is a short biography:
{information}

Using only this text, give me:
1. A one-line headline about this person
2. A three-bullet summary a 12-year-old would understand
3. One question you would ask them in an interview
"""
```

> **Think of it like this:**
> A prompt template is a fill-in-the-blanks form, like a railway reservation slip. The printed parts never change; you only write in the blanks. The numbered list is the "output contract": the wording of the answer changes every run, but its *shape* (headline, three bullets, one question) stays the same.

#### Building and running the chain

```pseudo title="02_summary_chain_openai.py (core)"
SET OPENAI_MODEL to the OPENAI_MODEL value from .env, or gpt-5.6-sol if it is not set

DEFINE build_profile_chain(model_name):
    CREATE profile_prompt_template = PromptTemplate with input variable information and PROFILE_TEMPLATE
    CREATE llm = ChatOpenAI with temperature 0 and model_name
    RETURN profile_prompt_template | llm   // the prompt's output feeds the model

SET chain = build_profile_chain(OPENAI_MODEL)
SET response = chain.invoke with information set to PERSON_INFORMATION
PRINT response.text
```

> **Imported:**
> - `PromptTemplate` from `langchain_core.prompts`, package langchain-core: a template with blanks, such as `{information}`.
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the chat model that calls OpenAI.
> - `PERSON_INFORMATION` from `sample_data`, your local `sample_data.py`: the biography the chain summarises.

```python reveal title="02_summary_chain_openai.py (core)"
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from sample_data import PERSON_INFORMATION

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")

def build_profile_chain(model_name: str):
    profile_prompt_template = PromptTemplate(
        input_variables=["information"], template=PROFILE_TEMPLATE
    )
    llm = ChatOpenAI(temperature=0, model=model_name)
    return profile_prompt_template | llm

chain = build_profile_chain(OPENAI_MODEL)
response = chain.invoke(input={"information": PERSON_INFORMATION})
print(response.text)
```

1. **os.getenv("OPENAI_MODEL", ...)** The model name lives in `.env`, so you can switch models without editing code.
2. **input_variables** Lists every `{placeholder}` the template expects.
3. **temperature=0** Asks for the most predictable answer. GPT-5.x reasoning models only allow their default, so LangChain quietly drops it there; it matters for local models.
4. **prompt | llm** The pipe builds a **RunnableSequence**: the output of the left side becomes the input of the right. This style is called **LCEL**.
5. **chain.invoke(...)** Runs the whole chain once and returns an `AIMessage`.
6. **response.text** The answer as one plain string. More on why not `.content` in 0.4.

```text title="sample output (wording changes every run)"
Model: gpt-5.6-sol

1. Headline: From newspaper boy in Rameswaram to India's "Missile Man" and President.

2. Summary for a 12-year-old:
- He was a scientist who helped India build its own rockets and put a satellite into space.
- People called him the "Missile Man of India", and later he became the country's 11th President.
- He loved teaching students and was giving a lecture when he died in 2015.

3. Interview question:
What did selling newspapers as a boy teach you that helped you as a scientist?
```

> **Try this:**
> Replace `PERSON_INFORMATION` in `sample_data.py` with a paragraph about anyone you like, a cricketer or your favourite founder, and run it again. Nothing else changes. That's the point of a template.

## 0.3 Same chain, local model

LangChain gives every chat model the same interface. Moving from a paid cloud model to a free one on your laptop changes exactly one line.

**Ollama** is a free app that downloads **open-weights** models (Gemma, Qwen, Llama and others) and serves them at `http://localhost:11434`. No API key, no cost, and your data never leaves your machine. Pick a model below to see the one line that differs.

##### Swap the model, keep the chain

interactive

The only line that changes

```text title="02_summary_chain_openai.py"

```

**If you pick "Cloud: ChatOpenAI":** **Cloud, paid per token.** Follows the three-part contract: one headline, exactly three bullets, one interview question. `response.content` is a list of blocks, so read `.text`.

**If you pick "Local: ChatOllama":** **Local, free and private.** Comes back fast, but a 270M-parameter model often ignores parts of the instructions: four bullets instead of three, or no interview question. `.content` is already a string; `.text` still works.

Typical result

| Trade-off | Cloud (gpt-5.6-sol) | Local (gemma3:270m) |
| --- | --- | --- |
| Cost | Pay per token | Free |
| Privacy | Text goes to the provider | Never leaves your laptop |
| Setup | An API key | Install Ollama, `ollama pull` the model |
| Quality | Follows the three-part contract | Tiny model: may write four bullets or forget the question |

> **Want better local answers?:**
> 270 million parameters is tiny next to GPT-class models. Pull a bigger one, for example `ollama pull gemma4` (about 10 GB), and set `OLLAMA_MODEL=gemma4` in `.env`. Same code, much better answers.

## 0.4 What comes back: the AIMessage

So far we printed only the answer text, but `chain.invoke()` returns a rich object. Knowing its fields matters for agents: the same object will carry the model's tool calls in Part B.

| Field | What it holds | Example |
| --- | --- | --- |
| type | Who wrote the message: `"ai"`, vs `"human"`, `"system"`, `"tool"` | `ai` |
| content | The raw content: a string, or a *list* of content blocks | `list` on OpenAI, `str` on Ollama |
| text | The answer as one plain string. Use this. | `1. Headline: From newspaper boy…` |
| tool_calls | Empty for now; filled when the model wants a tool | `[]` |
| usage_metadata | Provider-independent **token** counts, which is what you pay for | `{'input_tokens': 412, 'output_tokens': 386, …}` |
| response_metadata | Provider-specific details: model name, finish reason, timings | `model_name`, or `done_reason` on Ollama |
| id | A unique id for this response | `resp_0a1b2c…` |

```pseudo title="04_inspect_the_response_object.py (core)"
DEFINE make_llm(use_local):
    IF use_local THEN
        CREATE ChatOllama with temperature 0 and model OLLAMA_MODEL
        RETURN the model and OLLAMA_MODEL
    CREATE ChatOpenAI with temperature 0 and model OPENAI_MODEL
    RETURN the model and OPENAI_MODEL

SET use_local to true when "--local" is in the command-line arguments
SET llm, model_name = make_llm(use_local)
SET chain = PromptTemplate.from_template(PROFILE_TEMPLATE) | llm
SET response = chain.invoke with information set to PERSON_INFORMATION

PRINT response.usage_metadata
PRINT the keys of response.response_metadata
PRINT the type name of response.content
```

> **Imported:**
> - `ChatOllama` from `langchain_ollama`, package langchain-ollama, imported only with `--local`: the chat model that talks to your local Ollama app.
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the cloud chat model, used by default.

```python reveal title="04_inspect_the_response_object.py (core)"
def make_llm(use_local: bool):
    if use_local:
        from langchain_ollama import ChatOllama
        return ChatOllama(temperature=0, model=OLLAMA_MODEL), OLLAMA_MODEL
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(temperature=0, model=OPENAI_MODEL), OPENAI_MODEL

use_local = "--local" in sys.argv
llm, model_name = make_llm(use_local)
chain = PromptTemplate.from_template(PROFILE_TEMPLATE) | llm
response = chain.invoke({"information": PERSON_INFORMATION})

print(response.usage_metadata)
print(list(response.response_metadata.keys()))
print(type(response.content).__name__)
```

1. **make_llm()** Returns a cloud or a local model. Both have the same interface, so nothing after this line cares which one it got.
2. **"--local" in sys.argv** Run with `--local` to use Ollama instead of OpenAI.
3. **PromptTemplate.from_template** A shortcut that finds the placeholders for you, instead of listing `input_variables`.
4. **usage_metadata** Input, output and total tokens: your cost per call.
5. **type(response.content)** Prints `list` on newer OpenAI models, which is exactly why every script prints `.text`.

```text title="sample output (numbers and ids differ every run)"
type(response)        : AIMessage
response.type         : ai
response.tool_calls   : []
usage_metadata        : {'input_tokens': 412, 'output_tokens': 386, 'total_tokens': 798, ...}
model_name            : gpt-5.6-sol
content is a          : list  (Responses-API content blocks) — that's why we use .text
```

> **Why .text and not .content?:**
> Newer OpenAI models reply through the **Responses API**, where `.content` can be a list of content blocks rather than a string. `.text` always gives you one plain string, for every provider, so the course uses it everywhere.

#### Tracing with LangSmith, no code changes

Add the three `LANGSMITH_*` lines from 0.1 to `.env` and run any script again. LangChain notices them and sends a **trace** of every call to smith.langchain.com automatically.

1. 1 RunnableSequence The parent trace: one run of your whole chain.
2. 2 PromptTemplate A child step showing the filled-in prompt that was actually sent.
3. 3 ChatOpenAI or ChatOllama The model call, with latency, token count and cost. Compare a cloud and a local run side by side.

In Part B tracing is even more useful: you'll see two model calls with the tool call in between, which is the agent loop made visible.
