# LLMs through a finance lens

Future with Shivank *· AI Agents in Finance*

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Project 1 of 2:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Future with Shivank · Hands-on track

#### AI Agents in Finance Section 1 & Section 2 — the finance-first, code-first edition

You already know how agents, tools, memory and multi-agent systems work from our **AI Agents on AWS** module. So this page skips all of that and adds only two new things: **the finance knowledge** you need to build agents a bank would actually use, and **the code**, explained line by line in plain English.

🏦 **Your role for this module:** you have just joined the AI team at **Future with Shivank Bank** (a made-up bank). Analysts, fund managers and advisors keep walking up to your desk with requests. Every lab on this page builds one thing they asked for.

Lab 1A **Earnings-call summariser** Turns a long call transcript into a clean JSON card for fund managers.

Lab 1C **Live price agent** Answers "What is NVIDIA trading at?" with real data, not a guess.

Lab 2A **Ratio retriever** Pulls Apple's profitability, valuation and liquidity ratios from a data API.

Lab 2B + 2C **Rebalancing assistant** Remembers the chat (working memory), then learns across sessions (episodic memory).

Lab 2E **Verified news agent** Reuters only, last two days, every item with a link, checked by a second agent.

Lab 2F **Buy / Hold / Sell pipeline** Three agents pass JSON like a relay baton to produce an investment memo.

How to read the coloured boxes:

🧠 Analogy💰 Finance corner⚠️ Watch out⏭️ Already covered💡 Tip🧪 Simulation (click it!)

#### Setup Before you start (3 minutes)

| Key | Needed for | Cost |
| --- | --- | --- |
| `OPENAI_API_KEY` | Every lab | A few cents for everything on this page |
| `FINANCIAL_MODELING_PREP_API_KEY` | Ratio labs (2A, 2F) | Free plan is enough |
| `GOOGLE_API_KEY` | Gemini comparison in Lab 1A (optional) | Free tier available |
| `HF_TOKEN` + a GPU | Llama comparison in Lab 1A (optional) | Free token; request access to Llama 3.1 8B Instruct on its Hugging Face page first |

```bash title="Terminal · install once"
pip install openai openai-agents google-genai yfinance financetoolkit chromadb llama-index transformers torch
```

```python title="Python · load your keys (top of every lab)"
import os
# Put keys in environment variables (or Colab secrets) — never paste them into code you share
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
FINANCIAL_MODELING_PREP_API_KEY = os.environ["FINANCIAL_MODELING_PREP_API_KEY"]
```

> **Note:**
> 💡 Why do some lines start with `await`?
>
> Agents wait on the internet (the LLM, a price API). The SDK lets Python *wait without freezing* — that is what `async`/`await` means. In **Jupyter or Colab** you can type `await Runner.run(...)` directly in a cell. In a normal **.py file**, either use `Runner.run_sync(...)` (no await needed) or wrap your code like this:

```python title="Python · running async code from a .py file"
import asyncio
from agents import Agent, Runner

async def main():
    result = await Runner.run(my_agent, "Hello")   # 'await' is allowed inside an 'async def'
    print(result.final_output)

asyncio.run(main())                                 # starts the async world and runs main()
```

> **⚠️ Two habits that save you an hour:**
> - **One fresh notebook (or kernel restart) per lab.** Several labs reuse names like `get_company_fundamentals`; an old version left in memory silently gets used.
> - **Your output will differ from the samples here.** LLM answers vary run to run, and prices, ratios and news are live.

---

Section 1

## LLMs through a finance lens

Same building blocks you already know — but a bank asks different questions of them: *Is this number fresh? Where does client data go? Can a fund manager's dashboard read this output without breaking?* This section answers those, with three small labs.

⏭️ Already covered — we won't repeat

What an LLM or a Transformer is · how RAG retrieves, augments and generates · what makes a system "agentic" · how tool calling works · "start with the simplest thing that works" before reaching for agents. If any of these feel rusty, revisit the AWS module. Below, we only keep the **finance angle** and the **code**.

#### 1.1 Finance words you'll meet in the labs

The labs read earnings calls and stock data. Ten words unlock almost all of it:

**Ticker** A stock's short code. `AAPL` = Apple, `NVDA` = NVIDIA.

**Earnings call** A quarterly call where a company's leaders explain results to investors. The *transcript* is the text of that call.

**Revenue** All the money from sales. Also called the "top line".

**Net income** Profit left after every cost, interest and tax. The "bottom line".

**EPS** Earnings Per Share = net income ÷ number of shares. "How much profit each share earned."

**Guidance** Management's own forecast: "we expect revenue to grow mid-single digits next quarter."

**YoY** Year-over-year: compared with the same quarter last year.

**Fiscal quarter** The company's own accounting quarter. Apple's year ends in September, so its "Q3" is April–June.

**Sentiment** Is this news good, bad or neutral for the stock?

**Portfolio manager (PM)** The person deciding what a fund buys and sells. Wants short, decision-ready summaries.

> **🧠 Analogy — the quarterly report-card meeting:**
> An earnings call is a company's parent–teacher meeting. **Revenue** is all the fees the school collected, **net income** is what is left after paying every bill, **EPS** is that leftover split per family, and **guidance** is the teacher saying "here's what we expect next term". Investors listen for surprises.

#### 1.2 Picking the right model for a finance job

In a bank, model choice comes down to two questions:

1. **How much thinking does the task need?** *Non-reasoning* models answer straight away — fast and cheap. *Reasoning* models think in hidden steps first — slower, pricier, more careful. Many APIs let you set a *reasoning effort* (none → high).
2. **How sensitive is the data?** *Closed* models (GPT, Claude, Gemini) are the most capable, but your prompt travels to the provider. *Open-weights* models (Llama, Mistral, Gemma, GPT-OSS) can run on the bank's own servers, so client data never leaves — but you need GPUs and a team to run them.

{{diagram:1}}

*A rule of thumb for Future with Shivank Bank: first ask "where may this data go?", then "how hard is the thinking?". Example: short intraday trade summaries → fast model; a multi-quarter financial analysis → reasoning model.*

> **🧠 Analogy — cashier vs auditor:**
> A non-reasoning model is the bank cashier: counts notes fast, all day. A reasoning model is the auditor: slow, checks every step, costs more per hour. You don't send the auditor to count notes, and you don't let the cashier sign off the annual accounts.

#### 1.3 Finance-specialised models, tools and datasets

Finance has its own family of models. Know what each one *is* — especially which ones only classify and which ones can write.

| Name | Kind | What it's good at |
| --- | --- | --- |
| **FinBERT** | Open · *classifier* | Labels a financial sentence as positive / negative / neutral. It cannot write a summary. |
| **FinGPT** | Open framework + models | Fine-tuned on news, social media, filings and announcements — sentiment, robo-advice, quant ideas. |
| **InvestLM** | Open · instruction-tuned | Investment Q&A; trained on CFA-exam questions, SEC filings and quant-finance discussions. |
| **FinLlama** | Open · Llama-based | Question answering over filings and reports. |
| **FinMA** | Open (PIXIU project) | Sentiment, headline classification, named-entity recognition, Q&A. |
| **SEC-BERT** | Open · BERT family | Reading SEC filings and pulling out key entities. |
| **BloombergGPT** | Closed · in-house | Trained on a huge private financial corpus; Q&A, classification, summarisation. |
| **Assistants inside finance platforms** | Closed · products | Claude for Financial Services, ChatGPT inside Excel with financial-data connectors, LSEG Workspace AI, FactSet Mercury, Thomson Reuters CoCounsel, AlphaSense search — LLMs wired into the data analysts already use. |

This landscape changes every few months — treat the list as a snapshot and check leaderboards for the current state.

**Datasets = the exam papers.** When someone says "our model understands finance", ask *"on which benchmark?"* These four come up most often:

| Dataset | What it tests |
| --- | --- |
| **Financial PhraseBank** | Sentiment of single news sentences (positive / negative / neutral) |
| **FinQA** | Number crunching over real financial statements, with expert step-by-step solutions |
| **ECTSum** | Short bullet-point summaries of earnings-call transcripts |
| **FiQA** | Opinion-style Q&A and sentiment about specific aspects of a company |

🧪 Try it · 6 lines

##### See a classifier in action (runs on a laptop CPU)

```python title="Python · finbert_sentiment.py"
from transformers import pipeline

# FinBERT is a classifier: sentence in → label out. It cannot write text.
finbert = pipeline("text-classification", model="ProsusAI/finbert")

headlines = [
    "Apple reports record-breaking revenue in Q4 despite market slowdown",
    "Tesla stock falls after earnings miss expectations",
]
for h in headlines:
    print(h, "→", finbert(h)[0])     # e.g. {'label': 'positive', 'score': 0.93}
```

Notice the speed: no prompt, no JSON — just a label and a confidence score. That is why a specialised small model often beats a giant chat model for one narrow, high-volume job.

#### 1.4 Lab 1A · Earnings-call summariser that returns JSON

**The request:** "Every quarter I read twenty earnings calls. Give me each one as the same fixed card — company, quarter, revenue, EPS, guidance, highlights, risks, outlook — so it can drop straight into our dashboard."

We'll send the same request to three models: GPT-4.1-mini (closed), Gemini 2.5 Flash (closed) and Llama 3.1 8B (open). The transcript is a made-up Apple call stored in a variable called `transcript_apple_earnings_call`.

##### Step 1 — Write the two prompts

```python title="Python · lab_1a_earnings_json.py · step 1"
from openai import OpenAI
import json, os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# WHO the model is + WHAT SHAPE the answer must have
system_prompt = """You are a finance analyst. Produce a concise, decision-useful summary of an
earnings call for portfolio managers. Return strict JSON with keys:
company, quarter, revenue, eps, guidance, highlights[], risks[], outlook."""

# The actual job + the data. The f"..." drops the transcript text into the {...} slot.
user_prompt = f"""Summarize the following earnings call transcript:
{transcript_apple_earnings_call}"""
```

1. `system_prompt` is the job description: the role ("finance analyst"), the audience ("portfolio managers") and the **output contract** — the exact keys. `highlights[]` is a hint that this key should hold a list.
2. `user_prompt` is the task for this one call. The `f` in front of the quotes makes it an *f-string*: whatever is inside `{ }` gets replaced by that variable's value — here, the whole transcript.

##### Step 2 — Call the model and unpack the answer

```python title="Python · lab_1a_earnings_json.py · step 2"
response = client.responses.create(
    model="gpt-4.1-mini",                                    # cheap + fast: fine for summarising
    input=[{"role": "system", "content": system_prompt},
           {"role": "user",   "content": user_prompt}],
    text={"format": {"type": "json_object"}},                # JSON mode: the reply must be valid JSON
)

raw_text = response.output[0].content[0].text                # dig the text out of the response box
summary  = json.loads(raw_text)                              # JSON text  →  Python dictionary
print(json.dumps(summary, indent=2))                         # dictionary →  pretty, indented text
```

{{diagram:2}}

*`response.output[0].content[0].text` reads like opening a tiffin box: the box → its first compartment → the list inside → the first item → the text. Shortcut: `response.output_text` gives you the same text and is safer with reasoning models, where `output[0]` may be a reasoning item instead of the message.*

1. `text={"format": {"type": "json_object"}}` switches on **JSON mode**: the model must return valid JSON. Always mention "JSON" in your prompt when you use it — the API expects that.
2. `json.loads(raw_text)` turns the JSON *text* into a Python *dictionary*, so you can write `summary["eps"]`.
3. `json.dumps(summary, indent=2)` goes the other way, only to print it nicely indented.

##### Same prompts, two other models

```python title="Python · Gemini 2.5 Flash (free tier)"
from google import genai

gclient = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])   # separate name, so we don't overwrite 'client'
resp_genai = gclient.models.generate_content(
    model="gemini-2.5-flash",
    contents=system_prompt + "\n\n" + user_prompt,             # here: both prompts glued into one text
    config={"response_mime_type": "application/json"},         # Gemini's version of JSON mode
)
print(resp_genai.text)
```

```python title="Python · Llama 3.1 8B Instruct (open weights · needs a GPU, e.g. Colab T4)"
import torch, transformers

pipe = transformers.pipeline(
    "text-generation",
    model="meta-llama/Llama-3.1-8B-Instruct",       # downloaded to YOUR machine — nothing leaves it
    model_kwargs={"torch_dtype": torch.float16},     # half-precision numbers → fits on a 16 GB GPU
    device_map="auto",                               # place it on the GPU automatically
)
messages = [{"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}]
outputs = pipe(messages, max_new_tokens=1024)
print(outputs[0]["generated_text"][-1]["content"])  # see the note below
```

1. `outputs[0]` — the pipeline returns one result per input; we sent one conversation, so take the first.
2. `["generated_text"]` — this holds the *whole chat*: your system message, your user message, and the model's new reply at the end.
3. `[-1]["content"]` — `-1` means "last item", i.e. the model's reply; `["content"]` is its text.

##### What came back — and the finance lesson hiding in it

| Key | GPT-4.1-mini | Gemini 2.5 Flash | Llama 3.1 8B |
| --- | --- | --- | --- |
| `revenue` | `98700000000` a number | `"$98.7B (+6% YoY)"` text, with growth mixed in | `"$98.7 billion"` text |
| `eps` | `1.72` | `"$1.72 (+9% YoY)"` | `"$1.72"` |
| `guidance` | object with 3 fields | one sentence | object with 3 fields |
| `highlights` | Product-by-product detail: iPhone, Mac, iPad, Services record, margin, cash returned to shareholders | Key growth drivers grouped together | Short, high-level facts, little analysis |

💰 Finance corner — "valid JSON" is not the same as "usable JSON"

All three replies are valid JSON, yet the fund manager's dashboard runs `summary["revenue"] > 90e9`. It works for GPT and **crashes** for the other two, because their revenue is text. In finance, numbers must arrive as numbers, in a known unit. Fix it in the prompt — name every key, its type and its unit:

```python title="Python · a stricter output contract"
system_prompt = """You are a finance analyst writing for portfolio managers.
Return strict JSON with exactly these keys and types:
  company: string
  quarter: string, like "FY2025 Q3"
  revenue_usd: number in US dollars, no symbols or words (98700000000, not "$98.7B")
  revenue_growth_yoy_pct: number (6 means +6%)
  eps_usd: number
  guidance: string
  highlights: list of strings
  risks: list of strings
  outlook: one of "positive", "neutral", "negative"
"""
```

Even stricter: hand the API a full JSON Schema ("structured outputs"), so the model cannot return the wrong type at all. And notice the depth difference: the small 8B model listed facts, the bigger models explained *why* — size still matters for analysis.

#### 1.5 Prompting, finance style

You know the techniques; here is what they look like on a trading desk.

| Technique | Finance example | Use when |
| --- | --- | --- |
| **Zero-shot** | "Classify the sentiment of this headline as positive, negative or neutral: *Apple reports record-breaking revenue in Q4 despite market slowdown*" → **Positive** | The task is common and simple |
| **Few-shot** | Show three labelled headlines first (see below), then ask for a new one | You want a house style or tricky labels |
| **Chain-of-thought** | Give a worked example of a profit-margin calculation, then a new company | The answer needs arithmetic or several steps |
| **Zero-shot CoT** | Add one sentence at the end: "Let's think step by step." | Multi-step, but you have no worked examples |

Task: Classify the sentiment of a headline as Positive, Negative, or Neutral. Headline: Tesla stock falls after earnings miss expectations → Negative Headline: Amazon maintains steady growth amid economic slowdown → Neutral Headline: Apple reports record-breaking revenue in Q4 despite market slowdown → Positive Now classify: Nvidia shares surge after strong AI chip demand drives record quarterly revenue Sentiment: ▢

One example = one-shot, n examples = n-shot.

💰 Finance corner — net profit margin

**Net profit margin = net income ÷ revenue.** Out of every ₹100 of sales, how many rupees are profit? Profit going up is not enough — if sales went up even faster, the business is actually getting *less* efficient. The margin tells you which.

🧪 Simulation

##### Run the chain-of-thought yourself

This is exactly the 3-step reasoning the CoT prompt teaches the model. Change the numbers (in $ millions) and watch each step.

Year 1 revenue

2000

Year 1 net income

200

Year 2 revenue

2400

Year 2 net income

260

**Step 1 · Calculate both margins**

**Step 2 · Compare**

**Step 3 · Conclude**

- **Improving:** The company keeps more of each dollar of sales.
- **Declining:** The company keeps less of each dollar of sales.
- **Flat:** Profitability is unchanged.

> **Check:** Revenue must be above zero — a margin divides by revenue.

> **⚠️ Watch out — the 100-example problem:**
> Few-shot is great with 3 examples. With 100 labelled headlines in every prompt, you pay for those tokens on every call, responses slow down, and you may exceed the context window. That is the moment to consider fine-tuning or retrieval instead.

#### 1.6 Fine-tuning in finance — why it's rarely the first move

A fine-tuning dataset is just many rows of "here is the input, here is the answer I want". For headline sentiment, one training row looks like this:

```json title="JSONL · one training example per line"
{"messages": [{"role": "system", "content": "You are a senior financial analyst."}, {"role": "user", "content": "Quarterly operating profit rose to EUR 13.1 mn from EUR 8.7 mn a year earlier."}, {"role": "assistant", "content": "positive"}]}
```

Cheaper variants such as **PEFT / LoRA** train a small add-on instead of the whole model. Still, in finance fine-tuning hits four walls:

1. **Markets move weekly.** New regulations, rates and earnings make a fine-tuned model stale within weeks — and you must retrain to update it.
2. **Client data is confidential.** Uploading transaction records to a vendor's fine-tuning sandbox may break compliance rules.
3. **Decisions need live signals.** Credit risk or portfolio rebalancing depends on today's prices and macro data — far too fast to retrain for.
4. **Most bank data is messy.** PDFs, emails and memos must be hand-converted into clean input/answer pairs first.

| What you need | Best fit |
| --- | --- |
| A stable *style* or narrow task (e.g. label headlines our way) | Fine-tuning (or a small specialised model) |
| Fresh facts — prices, news, today's numbers | A tool that calls a data API |
| Answers from the bank's private documents | RAG over those documents |
| Several steps, decisions, checks | An agent (with tools + memory) |

#### 1.7 Lab 1B · Prove the knowledge cutoff with NVIDIA

A two-line experiment you can show in class. Ask a model with a known training cutoff (GPT-4.1: June 2024) for "the latest" news:

```python title="Python · lab_1b_knowledge_cutoff.py"
response = client.responses.create(
    model="gpt-4.1",
    input="Give me the latest news about NVIDIA.",
)
print(response.output_text)
```

Here are some of the latest news highlights about NVIDIA as of June 2024: 1. NVIDIA Surpasses $3 Trillion Market Cap … 2. NVIDIA Unveils Next-Gen Rubin GPUs …

💰 Finance corner

A real event — but from the model's training window, served as "latest". Here this model was honest and stamped the date; others won't, and will confidently invent a "recent" headline. In finance, **stale is wrong**: a trader acting on last year's news loses money. Newer models have later cutoffs, but the gap never closes — so any "now" question must go through a tool.

#### 1.8 Lab 1C · "What's NVIDIA trading at?" — without and with an agent

##### Without an agent

```python title="Python · lab_1c_price.py · plain LLM call"
response = client.responses.create(model="gpt-4.1", input="What is the last price of NVIDIA.")
print(response.output_text)
```

As of my latest update in June 2024, I do not have real-time data access. To find the most recent price of NVIDIA (NVDA), please check Yahoo Finance, Google Finance or NASDAQ…

Polite, honest, useless to a trader. Now we give it a tool.

##### Step 1 — The tool: a normal Python function plus one decorator

```python title="Python · lab_1c_price.py · step 1 (pip install openai-agents yfinance)"
from agents import Agent, Runner, function_tool
import yfinance as yf

@function_tool                                    # turns this function into a tool the LLM can call
def get_latest_stock_price(symbol: str) -> dict:
    """Fetch the current stock price for the given symbol."""   # the LLM reads this to decide when to use it
    ticker = yf.Ticker(symbol)                    # a handle for one stock, e.g. "NVDA"
    hist = ticker.history(period="1d")            # a table of the last trading day
    latest_close = hist["Close"].iloc[-1]         # column "Close", last row  → latest price
    latest_date = hist.index[-1]                  # label of that last row    → its date
    return {"price": float(latest_close), "date": str(latest_date.date())}
```

1. `@function_tool` is like printing a **menu card** for your function. The SDK reads the name, the docstring (the description) and the type hint `symbol: str` (the input), and shows that card to the LLM.
2. `yf.Ticker(symbol)` opens a handle to one stock. `.history(period="1d")` returns a pandas table (a DataFrame) for the last trading day — see the picture below.
3. `hist["Close"]` picks the Close column; `.iloc[-1]` means "row at position −1", i.e. the last row.
4. `hist.index[-1]` — the *index* is the row labels on the left (dates). The last label is the date of that price.
5. `float(...)` and `str(...date())` turn pandas types into plain Python values, so the result becomes clean text for the LLM.

| index (Date) | Open | High | Low | Close | Volume |
| --- | --- | --- | --- | --- | --- |
| 2025-08-15 | 181.88 | 181.90 | 178.04 | 178.89 | 156,602,200 |

What `hist` looks like (illustrative numbers). Highlighted: `hist.index[-1]` on the left, `hist["Close"].iloc[-1]` on the right. With `period="5d"` you would get five rows, and `[-1]` would still pick the newest.

💰 Finance corner — OHLCV

Every price table has the same five columns. **Open**: first trade of the day. **High / Low**: the day's extremes. **Close**: last trade — during market hours, the latest price so far. **Volume**: how many shares changed hands.

##### Step 2 — The agent, then run it

```python title="Python · lab_1c_price.py · step 2"
stock_price_agent = Agent(
    name="Stock Price Agent",                                          # a label, shows up in logs
    instructions="Fetch Historical prices for a given stock symbol",   # its job description
    model="gpt-4.1",                                                   # the brain
    tools=[get_latest_stock_price],                                    # what it may call
)

output = Runner.run_sync(                                              # run_sync: no 'await' needed
    starting_agent=stock_price_agent,
    input="What is today's date, and what is the current stock price of Nvidia?",
)
print(output.final_output)
```

Today's date for the latest price data is August 15, 2025. The current stock price of Nvidia (NVDA) is $178.89.

> **Note:**
> 💡 Why ask for the date too?
>
> It's a lie detector. If the date matches today's trading day, the answer came from the tool. If it shows a 2024 date, the model answered from memory. Also notice: you typed "Nvidia", but the tool needs a ticker — the LLM filled in `"NVDA"` itself. Choosing tool arguments is part of the LLM's job.

🧪 Simulation

##### Step through the agent loop

{{diagram:3}}

**1 · You ask.** `Runner.run_sync` sends your question to the LLM — together with the tool's "menu card": its name, its description (the docstring) and its input (`symbol: str`).

**What travels on the arrow:**

```
input = "What is today's date, and what is the current stock price of Nvidia?"
```

**2 · The LLM chooses the tool.** The model knows it can't know today's price. Instead of answering, it replies with a tool-call request. Notice it turned "Nvidia" into the ticker `NVDA` on its own.

**What travels on the arrow:**

```
{"tool": "get_latest_stock_price", "arguments": {"symbol": "NVDA"}}
```

**3 · The Runner runs YOUR function.** The LLM never runs code. The SDK calls `get_latest_stock_price("NVDA")` on your machine, and yfinance downloads the last trading day from Yahoo Finance.

**What travels on the arrow:**

```
hist = yf.Ticker("NVDA").history(period="1d")
```

**4 · The facts come back.** Your function picks the last Close and its date, and returns a small dictionary.

**What travels on the arrow:**

```
{"price": 178.89, "date": "2025-08-15"}
```

**5 · The result is injected.** The Runner adds that result to the conversation and calls the LLM again. Now real, fresh numbers are in the model's context.

**What travels on the arrow:**

```
tool result → appended to the conversation → second LLM call
```

**6 · The final answer.** The LLM writes the reply in plain English. That text is `output.final_output`. One loop: think → act → observe → answer.

**What travels on the arrow:**

```
The current stock price of Nvidia (NVDA) is $178.89 (data date: August 15, 2025).
```

💰 Where banks take this next

- **Market intelligence agent** — watches news, economic indicators and central-bank statements, and summarises the likely impact on each sector.
- **Client reporting agent** — pulls each client's portfolio data, calculates performance and writes a quarterly report in that client's style.
- **Earnings-call analyser** — transcribes the call, extracts metrics, scores sentiment with evidence, flags guidance changes.
- **Backtesting agent** — you say "momentum strategy on tech stocks"; it fetches history, tests how that strategy *would have* performed, and charts the results.

---

Section 2
