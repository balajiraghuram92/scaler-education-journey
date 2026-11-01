# Setup Guide

Help · setup and how the lessons work

#### Set up once, then *build*

Every step I followed to get a laptop ready for the lessons: WSL and Python, the models, one requirements.txt, API keys and a one-command setup check. Also how every lesson page is laid out.

**Machine** Windows + WSL2 (Ubuntu 24.04) **Language** Python 3.12 **Lessons** [AI-Infusion](/chapter/ai-infusion/ai-infusion-start-here/course-overview) · [AWS AI Bootcamp](/chapter/aws-agentic-ai-bootcamp/bootcamp-overview/bootcamp-overview)

The method

## How every lesson is taught

The pages follow the same rhythm, so you always know where you are:

1. **Recap.** “What you can already do”: the earlier lessons this one stands on.
2. **Flight plan.** The steps ahead, in order, before any detail.
3. **Feel it first.** The idea in plain language and a diagram, often an analogy, before code.
4. **Build in small steps.** One file at a time, each with a decoder that explains it line by line.
5. **Prove it.** A command after each step with the output you should see.
6. **Try it.** An in-page demo you can poke without installing anything.
7. **Check yourself and ship.** Self-check questions, milestones, and a LinkedIn post.

How to study them

Read a lesson once end to end. Then rebuild its project yourself, step by step, running every “prove it” command before moving on. Copying the finished code teaches you far less than getting each step to pass on its own. When you're stuck, the self-check at the end usually names the idea you missed.

Setup overview

## What you need, at a glance

Python

3.123.10 minimum; Lesson 5 images use 3.12

Machine

WSL2Ubuntu 24.04 on Windows

Environment

1 venvone `requirements.txt` for all lessons

API keys

1–4start with Groq (free tier) or OpenAI

Lesson 5

DockerDocker Desktop, WSL2 backend

Lesson 6

AWSaccount, CLI v2, Bedrock access

You don't need everything on day one. Lessons 1–2 need Python, a key and the core packages. Add the rest as you reach the lessons that use them; the lesson-by-lesson table below says exactly when.

Models

## Which model does what

Three kinds of model appear across the lessons. Most confusion goes away once you know which kind you're looking at.

| Kind | What it does | Runs where |
| --- | --- | --- |
| **LLM (chat model)** | Reads text and writes text. Answers, summaries, tool calls, rulings. | Through an API, billed per token |
| **Embedding model** | Turns text into a list of numbers, so similar meanings land close together. Powers RAG search. | Locally (free) or through an API |
| **Cross-encoder** | Reads a question and a passage *together* and scores how relevant the passage is. Used to rerank search results. | Locally (free) |

#### LLM providers

| Provider | Model id | Key in `.env` | Used in |
| --- | --- | --- | --- |
| **OpenAI** | `gpt-4o-mini` embeddings: `text-embedding-3-small` | `OPENAI_API_KEY` | Lessons 1–5 |
| **Groq** | `openai/gpt-oss-20b` `llama-3.3-70b-versatile` (Lesson 1) has since been deprecated | `GROQ_API_KEY` | Lessons 1, 7–10 · free tier |
| **Anthropic Claude** | `claude-opus-5-5` also `claude-sonnet-5-5`, `claude-haiku-5-5` | `ANTHROPIC_API_KEY` | Optional swap in any lesson; Lesson 6 uses Claude through Bedrock |
| **DeepInfra** | `deepseek-ai/DeepSeek-V4-Flash` OpenAI-compatible base URL `https://api.deepinfra.com/v1/openai` | `DEEPINFRA_API_KEY` | Optional low-cost swap in any lesson |
| **AWS Bedrock** | Amazon Nova Lite; `us.anthropic.claude-haiku-4-5-20251001-v1:0` | `aws configure` | Lesson 6, region `us-east-1` |

Model ids change, so check before you run

Providers retire models regularly. Groq deprecated the Llama model from Lesson 1 while the course was running, which is why Lessons 7–10 use `openai/gpt-oss-20b`. DeepInfra's catalog also has a dated `DeepSeek-V4-Flash-0731` variant. If a call fails with “model not found”, look up the current id on the provider's models page and change it in **one** place: `providers.py` below, or the lesson's config file.

#### Embedding models

| Model | Dims | Notes |
| --- | --- | --- |
| `all-MiniLM-L6-v2` | 384 | Local, free, fast, about 90 MB. The default in Lessons 3–4. |
| `BAAI/bge-large-en-v1.5` | 1024 | Local, slower, usually more accurate. The upgrade path mentioned in Lessons 3–4. |
| `text-embedding-3-small` | 1536 | OpenAI API, paid per token. Used by the containerised RAG bot in Lesson 5. |

#### Cross-encoder (reranker)

| Model | Notes |
| --- | --- |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | Local and free, through `sentence-transformers`. Rescores the top results from vector search (Lessons 3–4). |

Both local models download from Hugging Face the first time you use them and are cached in `~/.cache/huggingface`, so the first run is slow and later runs are instant.

Requirements lesson by lesson

## What each lesson needs

| Lesson | Python packages | Models & keys | Other tools |
| --- | --- | --- | --- |
| 1 | `openai` `gradio` `requests` `beautifulsoup4` `python-dotenv` | `gpt-4o-mini` or a Groq model · OpenAI or Groq key | — |
| 2 | + `langchain` `langchain-openai` | `gpt-4o-mini` · OpenAI key | — |
| 3–4 | + `langchain-chroma` `langchain-huggingface` `langchain-community` `sentence-transformers` `pypdf` | `gpt-4o-mini`, MiniLM embeddings, ms-marco cross-encoder · OpenAI key | ~1 GB disk for PyTorch and models |
| 5 | `fastapi` `uvicorn` `scikit-learn` `pandas` `chromadb` `openai` (pinned inside each image) | `gpt-4o-mini`, `text-embedding-3-small` · OpenAI key | Docker Desktop + Compose, `redis:7-alpine` |
| 6 | `strands-agents` `strands-agents-tools` `boto3` `langgraph` `langchain-aws` | Bedrock: Nova Lite, Claude Haiku 4.5 · AWS keys | AWS account, CLI v2, Bedrock model access |
| 7 | `groq` `gradio` `python-dotenv` | `openai/gpt-oss-20b` · Groq key | — |
| 8 | `langchain-groq` `langchain-core` `gradio` | `openai/gpt-oss-20b` · Groq key | — |
| 9–10 | `groq` `gradio` (SQLite is built into Python) | `openai/gpt-oss-20b` · Groq key | — |

Windows + WSL

## Set up WSL, step by step

WSL2 runs a real Ubuntu Linux inside Windows. The lessons' commands (`source .venv/bin/activate`, `./setup.sh`, Docker) then work exactly as written, with no Windows-specific variants.

#### 1 · Install WSL2 and Ubuntu (Windows, once)

```pseudo title="windows.ps1"
// Windows PowerShell as administrator, once per machine
RUN wsl --install -d Ubuntu-24.04     // install WSL2 and Ubuntu 24.04, then restart when asked
RUN wsl --update                      // get the latest WSL kernel
RUN wsl -l -v                         // check that Ubuntu-24.04 shows VERSION 2
```

```python reveal title="windows.ps1 · Windows PowerShell as administrator"
# Windows PowerShell, "Run as administrator" - once per machine
wsl --install -d Ubuntu-24.04     # installs WSL2 + Ubuntu 24.04 (ships Python 3.12); restart when asked
wsl --update                      # latest WSL kernel
wsl -l -v                         # Ubuntu-24.04 must show VERSION 2
```

After the restart, open “Ubuntu 24.04” from the Start menu and create a Linux username and password. Everything from here on runs **inside Ubuntu**.

#### 2 · Python, a venv and every package (Ubuntu, once)

```pseudo title="ubuntu_setup.sh"
// Inside Ubuntu (WSL), once
RUN sudo apt update, then sudo apt upgrade -y        // refresh the package lists, then upgrade
RUN sudo apt install -y python3, python3-venv, python3-pip, python-is-python3, build-essential, git, curl, unzip
RUN python --version                                 // expect Python 3.12.x
RUN git config --global core.autocrlf input          // keep Linux line endings in repos

// Work in the Linux file system, not /mnt/c: file access there is much faster
RUN mkdir -p ~/ai-infusion, then cd into it
// put requirements.txt, .env.example, providers.py and check_setup.py in that folder

// One virtual environment for all lessons
RUN python -m venv .venv
RUN source .venv/bin/activate                        // run this in every new terminal
RUN pip install --upgrade pip

// CPU-only PyTorch first, which skips the multi-GB CUDA download
RUN pip install torch from the CPU-only wheel index
RUN pip install -r requirements.txt

// Keys
RUN cp .env.example .env, then open .env in nano and fill in the keys you use
APPEND .env, .venv/ and __pycache__/ to .gitignore   // keep real keys and the venv out of git
RUN python check_setup.py                            // add --models to test embeddings and the cross-encoder
```

```python reveal title="ubuntu_setup.sh · Ubuntu terminal"
# Inside Ubuntu (WSL) - once
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip python-is-python3 build-essential git curl unzip
python --version                          # expect Python 3.12.x
git config --global core.autocrlf input   # keep Linux line endings in repos

# Work in the Linux filesystem, not /mnt/c - file access there is far faster
mkdir -p ~/ai-infusion && cd ~/ai-infusion
# put requirements.txt, .env.example, providers.py and check_setup.py here

# One virtual environment for all lessons
python -m venv .venv
source .venv/bin/activate                 # run this in every new terminal
pip install --upgrade pip

# CPU-only PyTorch first (skips a multi-GB CUDA download), then everything else
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Keys
cp .env.example .env && nano .env
printf ".env\n.venv/\n__pycache__/\n" >> .gitignore

python check_setup.py                     # add --models to test embeddings + cross-encoder
```

1 **`python-is-python3`** Ubuntu only installs `python3`. This package makes plain `python` work too, so commands from the lessons run unchanged.

2 **Stay out of `/mnt/c`** Your Windows drive is visible at `/mnt/c`, but file access across the boundary is many times slower, which hurts `pip install` and git especially. Keep projects in `~/`. VS Code and Windows Explorer can still open them (`\\wsl$\Ubuntu-24.04\home\<you>`).

3 **CPU-only PyTorch before the rest** `sentence-transformers` depends on PyTorch, and the default wheel bundles several GB of GPU (CUDA) libraries. Installing the CPU build first means pip reuses it. The lessons' models are small, so a CPU is plenty.

4 **`source .venv/bin/activate` in every new terminal** If you see `ModuleNotFoundError` for a package you installed, this is almost always the reason. The prompt shows `(.venv)` when it's active.

#### 3 · Editor: VS Code with the WSL extension

Install VS Code on Windows and add the **WSL** extension (by Microsoft). Then, from the Ubuntu terminal inside a project folder, run `code .`. VS Code opens connected to Linux, and its terminal, Python interpreter and debugger all run in WSL. Pick `.venv/bin/python` as the interpreter when it asks.

#### 4 · Docker Desktop (Lesson 5)

Install Docker Desktop for Windows. In *Settings → General*, keep “Use the WSL 2 based engine” on, and in *Settings → Resources → WSL integration*, enable **Ubuntu-24.04**. Check from Ubuntu with `docker run hello-world`. Don't also install Docker inside Ubuntu with apt; Docker Desktop provides the `docker` command there.

#### 5 · AWS CLI (Lesson 6)

```pseudo title="aws_cli.sh"
// Lesson 6 only, inside Ubuntu (WSL)
RUN curl to download the AWS CLI v2 zip, saved as awscliv2.zip
RUN unzip awscliv2.zip, then sudo ./aws/install      // install the CLI from the unzipped folder
DELETE the aws folder and awscliv2.zip               // tidy up the installer files
RUN aws --version                                    // check that the CLI is installed
RUN aws configure                                    // enter your access keys and a region (us-east-1 for Lesson 6)
RUN aws sts get-caller-identity                      // print your account id when the keys work
```

```python reveal title="aws_cli.sh · Ubuntu terminal"
# Lesson 6 only - AWS CLI v2 inside Ubuntu (WSL)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install && rm -rf aws awscliv2.zip
aws --version
aws configure                    # region: us-east-1, as in Lesson 6
aws sts get-caller-identity      # prints your account id when the keys work
```

#### WSL gotchas, solved

| Symptom | Fix |
| --- | --- |
| `pip install` or git is painfully slow | The project is under `/mnt/c`. Move it to `~/`. |
| Gradio says `http://127.0.0.1:7860`; will the browser reach it? | Yes. WSL2 forwards `localhost`, so open that URL in your Windows browser. |
| `/bin/bash^M: bad interpreter` running a `.sh` | Windows line endings. Run `sed -i 's/\r$//' setup.sh`, and set `core.autocrlf input` (step 2) for the future. |
| AWS says “Signature expired” after the laptop slept | WSL's clock drifted. Run `wsl --shutdown` in PowerShell and reopen Ubuntu. |
| Process killed while loading models | WSL ran out of memory. Create `C:\Users\<you>\.wslconfig` with `[wsl2]` and `memory=8GB` on the next line, then `wsl --shutdown`. |
| `docker: command not found` in Ubuntu | Docker Desktop isn't running, or WSL integration is off for Ubuntu-24.04 (step 4). |
| Editing this website's files from WSL | Your Windows repo is at `/mnt/c/Users/balaj/Documents/balajiraghuram.github.io`. It's fine for HTML edits; keep Python projects in `~/`. |

requirements.txt

## One shopping list for all ten lessons

`requirements.txt` is a plain list of packages, one per line, that `pip install -r requirements.txt` installs in one go. It's how a project says “this is what I need to run”. Anyone, including Docker in Lesson 5, can rebuild the same environment from it.

```pseudo title="requirements.txt"
// one package name per line; text after # is a comment; comment out a group you do not need yet
// core, every lesson
FOR EACH of openai, anthropic, python-dotenv, gradio, requests, beautifulsoup4: install it
// LangChain, lessons 2, 3-4 and 8
FOR EACH of langchain, langchain-core, langchain-openai, langchain-groq, langchain-text-splitters: install it
// RAG, lessons 3-4: embeddings, cross-encoder and vector DB (the heaviest group, it pulls in PyTorch)
FOR EACH of langchain-community, langchain-huggingface, langchain-chroma, sentence-transformers, pypdf, numpy: install it
// tool-calling projects, lessons 7 and 9-10
INSTALL groq
// serving, lesson 5
FOR EACH of fastapi, uvicorn, scikit-learn, pandas, joblib, chromadb: install it
// agents on AWS, lesson 6
FOR EACH of boto3, strands-agents, strands-agents-tools, langgraph, langchain-aws: install it
```

```python reveal title="requirements.txt · grouped by lesson"
# AI Infusion - one environment for Lessons 1-10 (Python 3.12 recommended, 3.10 minimum)
# Install:  pip install -r requirements.txt
# Comment out a group you don't need yet. RAG is the heaviest (it pulls in PyTorch).

# --- core: every lesson ---
openai              # OpenAI, plus Groq and DeepInfra through base_url
anthropic           # Claude
python-dotenv       # loads .env into os.environ
gradio              # the web UI in most lessons
requests
beautifulsoup4      # Lesson 1 web scraper

# --- LangChain: Lessons 2, 3-4, 8 ---
langchain
langchain-core
langchain-openai
langchain-groq
langchain-text-splitters

# --- RAG: Lessons 3-4 (embeddings, cross-encoder, vector DB) ---
langchain-community
langchain-huggingface
langchain-chroma
sentence-transformers   # all-MiniLM-L6-v2 embeddings + ms-marco cross-encoder
pypdf
numpy

# --- tool-calling projects: Lessons 7, 9-10 ---
groq

# --- serving: Lesson 5 (each Docker image also pins its own copy) ---
fastapi
uvicorn
scikit-learn
pandas
joblib
chromadb

# --- agents on AWS: Lesson 6 ---
boto3
strands-agents
strands-agents-tools
langgraph
langchain-aws
```

#### How to work with it

| You want to… | Do this |
| --- | --- |
| Install everything | `pip install -r requirements.txt` (venv active) |
| Install only what you need now | Put `#` in front of the groups for later lessons, then install |
| Add a package | Add a line, then run `pip install -r requirements.txt` again; installed ones are skipped |
| Freeze exact versions that work | `pip freeze > requirements.lock.txt`, and install from that file to reproduce your setup exactly |
| Build a Docker image (Lesson 5) | Each service gets its own small requirements file with **pinned** versions (`fastapi==0.115.6`), copied before the code so the install layer caches |
| Start a lesson's own project | Use the requirements file shipped with that project when it has one (Lesson 6's repo includes one). |

Unpinned here, pinned in production

This file leaves versions open so you get current releases, which suits learning. A real deployment pins every version (`==`), so the build you tested is the build that ships. That's the dependency-hell lesson from Lesson 5.

Keys & providers

## One .env, one switch, one check

#### 1 · Keys live in `.env`, never in code

```pseudo title=".env.example"
// copy this file to .env, then fill in only the keys you use
// .env must be in .gitignore, so real keys are never committed
SET OPENAI_API_KEY = (empty until you add a key)
SET ANTHROPIC_API_KEY = (empty until you add a key)
SET GROQ_API_KEY = (empty until you add a key)
SET DEEPINFRA_API_KEY = (empty until you add a key)
// Lesson 6 uses aws configure instead, which stores keys in ~/.aws/credentials
```

```python reveal title=".env.example · copy to .env"
# Copy to .env  (cp .env.example .env)  and fill in only the keys you use.
# .env must be listed in .gitignore - never commit real keys.
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
DEEPINFRA_API_KEY=
# Lesson 6 (AWS) uses `aws configure`, which stores keys in ~/.aws/credentials instead.
```

Get keys from each provider's console: [Groq](https://console.groq.com/keys) (free tier, the easiest start), [OpenAI](https://platform.openai.com/api-keys), [Claude](https://platform.claude.com/), and [DeepInfra](https://deepinfra.com/). `load_dotenv()` reads the file at the start of each script, as in every lesson since Lesson 1.

#### 2 · Switch providers by changing one word

Lesson 1 showed that the OpenAI SDK talks to Groq if you change `base_url`. DeepInfra works the same way. Claude uses Anthropic's own SDK. This helper puts all four behind one function:

```pseudo title="providers.py"
LOAD every KEY=value line from .env into the environment   // runs when this file is imported
CREATE OPENAI_COMPATIBLE: one entry per provider
    openai: key OPENAI_API_KEY, no base URL (the default), model gpt-4o-mini
    groq: key GROQ_API_KEY, Groq's base URL, model openai/gpt-oss-20b
    deepinfra: key DEEPINFRA_API_KEY, DeepInfra's base URL, model deepseek-ai/DeepSeek-V4-Flash
SET CLAUDE_MODEL = claude-opus-5-5

DEFINE ask(provider, prompt):
    IF provider is claude THEN
        IMPORT anthropic
        CREATE client = anthropic.Anthropic()   // reads ANTHROPIC_API_KEY by itself
        CALL client.beta.messages.create with CLAUDE_MODEL, max_tokens 1024, the server-side fallback beta, fallbacks set to default, and the prompt   // fallbacks retries on another model if this one declines
        IF response.stop_reason is refusal THEN
            RETURN "(declined)"
        RETURN the first text block in response.content, or "" if there is none
    SET cfg = OPENAI_COMPATIBLE[provider]
    CREATE client = OpenAI(api_key from the environment variable named in cfg, base_url from cfg)   // raises an error if that variable is not set
    CALL client.chat.completions.create with cfg model, max_tokens 512, and the prompt
    RETURN the message content of the first choice

IF this file is run directly THEN
    PRINT ask("groq", "Explain an embedding in one sentence.")
```

> **Imported:**
> - `os` Python standard library: gives access to environment variables through `os.environ`.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file into the environment.
> - `OpenAI` from `openai`: the client for OpenAI, and for Groq and DeepInfra through their `base_url`.
> - `anthropic` Anthropic's SDK, package `anthropic`: the Claude client, imported only in the Claude branch.

```python reveal title="providers.py · one function, four providers"
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# One OpenAI-compatible client covers three providers: only the key, base_url and model change.
OPENAI_COMPATIBLE = {
    "openai":    {"key": "OPENAI_API_KEY",    "base_url": None,
                  "model": "gpt-4o-mini"},
    "groq":      {"key": "GROQ_API_KEY",      "base_url": "https://api.groq.com/openai/v1",
                  "model": "openai/gpt-oss-20b"},
    "deepinfra": {"key": "DEEPINFRA_API_KEY", "base_url": "https://api.deepinfra.com/v1/openai",
                  "model": "deepseek-ai/DeepSeek-V4-Flash"},
}
CLAUDE_MODEL = "claude-opus-5-5"

def ask(provider: str, prompt: str) -> str:
    if provider == "claude":
        import anthropic
        client = anthropic.Anthropic()                    # reads ANTHROPIC_API_KEY
        response = client.beta.messages.create(
            model=CLAUDE_MODEL, max_tokens=1024,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",                          # retry on another model if this one declines
            messages=[{"role": "user", "content": prompt}])
        if response.stop_reason == "refusal":
            return "(declined)"
        return next((b.text for b in response.content if b.type == "text"), "")

    cfg = OPENAI_COMPATIBLE[provider]
    client = OpenAI(api_key=os.environ[cfg["key"]], base_url=cfg["base_url"])
    response = client.chat.completions.create(
        model=cfg["model"], max_tokens=512,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    print(ask("groq", "Explain an embedding in one sentence."))
```

1 **Three providers, one client class** OpenAI, Groq and DeepInfra all speak the OpenAI API format. Only the key, base URL and model id differ, so they live in a dictionary.

2 **Claude has its own SDK** `anthropic.Anthropic()` reads `ANTHROPIC_API_KEY` by itself. Its reply is a list of content blocks, so the code picks the text block. `fallbacks="default"` asks the API to retry on another Claude model if the first one declines the request.

3 **Model ids in one place** When a provider retires a model, you change one line here, not every script.

#### 3 · Check the whole setup in one command

```pseudo title="check_setup.py"
LOAD every KEY=value line from .env with load_dotenv()
SET ok = Python is 3.10 or newer
PRINT OK or FAIL, with the Python version   // 3.12 is recommended

FOR EACH group of modules (core, LangChain, RAG, tool-calling, serving, AWS agents):
    SET missing = the modules in the group that cannot be found
    PRINT OK, or MISS with the names in missing

IF the openai module cannot be found THEN
    STOP with "Install the packages first: pip install -r requirements.txt"
IMPORT ask from providers

FOR EACH provider and its key name (openai, groq, deepinfra, claude):
    IF that key is empty in the environment THEN
        PRINT skip, and continue with the next provider
    TRY
        SET reply = ask(provider, "Reply with the single word: ready")
        PRINT OK, then the first 40 characters of reply
    ON ERROR
        PRINT FAIL, the error type and the first line of the message   // usually a wrong key or a retired model id

IF "--models" is in the command-line arguments THEN
    IMPORT CrossEncoder and SentenceTransformer
    CREATE the all-MiniLM-L6-v2 embedding model, encode "hello world", PRINT its shape
    CREATE the ms-marco cross-encoder, score one question and passage, PRINT the score
```

> **Imported:**
> - `importlib.util` Python standard library: `find_spec` checks whether a module is installed, without importing it.
> - `os` Python standard library: `os.getenv` reads each key from the environment.
> - `sys` Python standard library: gives the Python version and the command-line arguments.
> - `load_dotenv` from `dotenv`, package python-dotenv: loads `.env` before the checks run.
> - `ask` from `providers`, the helper file above: calls each provider with one short prompt.
> - `CrossEncoder` and `SentenceTransformer` from `sentence_transformers`, package sentence-transformers: the local models, imported only when `--models` is given.

```python reveal title="check_setup.py · python check_setup.py"
import importlib.util
import os
import sys

from dotenv import load_dotenv

load_dotenv()

ok = sys.version_info >= (3, 10)
print(f"{'OK  ' if ok else 'FAIL'} Python {sys.version.split()[0]}{'' if ok else ' - need 3.10+ (3.12 recommended)'}")

GROUPS = {
    "core (all lessons)":              ["openai", "anthropic", "dotenv", "gradio", "requests", "bs4"],
    "LangChain (2, 3-4, 8)":           ["langchain", "langchain_openai", "langchain_groq"],
    "RAG (3-4)":                       ["langchain_huggingface", "langchain_chroma", "sentence_transformers", "pypdf"],
    "tool-calling projects (7, 9-10)": ["groq"],
    "serving (5)":                     ["fastapi", "uvicorn", "sklearn", "pandas"],
    "AWS agents (6)":                  ["boto3", "strands", "strands_tools", "langgraph", "langchain_aws"],
}
for group, modules in GROUPS.items():
    missing = [m for m in modules if importlib.util.find_spec(m) is None]
    print(f"{'OK  ' if not missing else 'MISS'} {group}{': ' + ', '.join(missing) if missing else ''}")

# One tiny call per provider whose key is in .env
if importlib.util.find_spec("openai") is None:
    sys.exit("Install the packages first: pip install -r requirements.txt")
from providers import ask  # noqa: E402

KEYS = {"openai": "OPENAI_API_KEY", "groq": "GROQ_API_KEY",
        "deepinfra": "DEEPINFRA_API_KEY", "claude": "ANTHROPIC_API_KEY"}
for provider, key in KEYS.items():
    if not os.getenv(key):
        print(f"skip {provider:9} (no {key} in .env)")
        continue
    try:
        reply = ask(provider, "Reply with the single word: ready")
        print(f"OK   {provider:9} -> {reply.strip()[:40]}")
    except Exception as e:                       # wrong key, wrong model id, no network...
        print(f"FAIL {provider:9} -> {type(e).__name__}: {str(e).splitlines()[0][:80]}")

# Local models download on first use (~100 MB). Run with --models to test them.
if "--models" in sys.argv:
    from sentence_transformers import CrossEncoder, SentenceTransformer
    vectors = SentenceTransformer("all-MiniLM-L6-v2").encode(["hello world"])
    print(f"OK   embeddings    -> shape {vectors.shape}")
    score = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2").predict([("what is RAG?", "RAG retrieves documents.")])
    print(f"OK   cross-encoder -> score {float(score[0]):.2f}")
```

*$ python check_setup.py (example: only a Groq key set yet)* **OK** Python 3.12.3 **OK** core (all lessons) **OK** LangChain (2, 3-4, 8) **OK** RAG (3-4) **OK** tool-calling projects (7, 9-10) **OK** serving (5) **OK** AWS agents (6) skip openai (no OPENAI_API_KEY in .env) **OK** groq -> ready skip deepinfra (no DEEPINFRA_API_KEY in .env) skip claude (no ANTHROPIC_API_KEY in .env)

A `MISS` line names the exact packages to install. A `FAIL` line shows the provider's error: usually a wrong key, or a model id that has been retired. When everything you need says `OK`, open [Lesson 1](/chapter/ai-infusion/lesson-01-first-ai-app/our-flight-plan).

AI Infusion · notes and builds from the course, Lessons 1–10. Each lesson page links to the next. Model ids and prices change often. The ids on this page were current when it was written, so check each provider's models page if a call fails.
