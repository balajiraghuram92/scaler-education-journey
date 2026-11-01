# Agent design patterns — finance edition (part 3)

## Agent design patterns — finance edition (part 3)

#### 2.5 Reasoning patterns on a trading desk

The planning variants, mapped to jobs an analyst at Future with Shivank Bank actually does:

| Pattern | In one line | Finance example |
| --- | --- | --- |
| **Plan-then-execute** | Write the full plan, then follow it | Rebalance: fetch allocations → find risk gaps → build the trade list → execute in order (re-plan only if a trade fails) |
| **Plan-and-execute** | Plan a little, act, look, re-plan | Company check: fetch ratios + news → spot a surprise jump in debt → *add* a cash-flow analysis step → continue |
| **Hierarchical** | Big goal → sub-plans → concrete actions | "Cut portfolio volatility" → rebalance equities / shorten bond duration / hedge currency → specific trades and % changes |
| **Planning + ReAct** | Each plan step runs its own think → act → observe loop | Invest or not: statements → ratios (falling margins? fetch more) → news sentiment → verdict |
| **Planning + reflection** | Critique the plan before running it | The review notices "no cash-flow quality check" and adds one before any data is fetched |

💰 Four words from that table

- **Leverage** — how much the company runs on borrowed money. A sudden jump is a red flag.
- **Bond duration** — how sensitive a bond's price is to interest-rate changes. Shorter duration = less swing.
- **Currency hedge** — a contract that protects you if, say, the dollar falls against the rupee.
- **Cash-flow quality** — are reported profits backed by real cash coming in? Profits without cash are a warning sign.

##### Worked example — a plan-then-execute trend detector for Apple

The plan an LLM would write: **(1)** get the last 3 months of daily prices · **(2)** compute the 20-day moving average · **(3)** compare today's average with the one a week ago · **(4)** label it Uptrend or Downtrend.

> **🧠 Analogy — a batter's 20-innings average:**
> One innings can be a fluke. A batter's average over the last 20 innings tells you their real form — and whether that average is rising or falling tells you the trend. A **20-day moving average** does the same for a stock: the average of the last 20 closing prices, recalculated every day.

🧪 Simulation

##### Run the plan on a made-up stock

{{diagram:1}}

**Step 3:** MA20 today = `value`, five trading days ago = `value` → **Step 4:** Uptrend or Downtrend.

The green line only starts on day 20 — you need 20 prices before the first average exists (that's why `ma20` is empty/NaN for the first 19 rows). Notice how much smoother it is than the grey daily line.

```python title="Python · trend_check.py · the same plan, as plain code"
import yfinance as yf

prices = yf.Ticker("AAPL").history(period="3mo")["Close"]      # step 1: ~63 daily closing prices
ma20 = prices.rolling(window=20).mean()                        # step 2: 20-day moving average
today_ma, week_ago_ma = ma20.iloc[-1], ma20.iloc[-6]           # step 3: today vs 5 trading days earlier
trend = "Uptrend" if today_ma > week_ago_ma else "Downtrend"   # step 4: label it
print(f"MA20 today={today_ma:.2f}, a week ago={week_ago_ma:.2f} → {trend}")
```

> **💡 Not every plan step needs an LLM:**
> Steps 1–4 are pure arithmetic. In a real system, let the LLM *write the plan and explain the result*, and let plain code (or a calculator tool) do the maths — cheaper, faster and never wrong about a sum. Deciding which steps get an LLM and which get code is called **workflow engineering**. `.iloc[-6]` is "6th row from the end" = 5 trading days before today.

##### Lab 2D · ReAct with LlamaIndex: the live price, with visible thinking

Same goal as Lab 1C, different framework. Here you can *watch* the Thought → Action → Observation loop as it streams.

```python title="Python · lab_2d_react_price.py · step 1 (pip install llama-index yfinance)"
from llama_index.core.agent.workflow import ReActAgent, AgentStream
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
import yfinance as yf

def get_latest_price(ticker_symbol: str):
    """Fetch the latest price for the given ticker symbol."""
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period="1d", interval="1m")         # today, one row per MINUTE
    if not data.empty:                                         # did any rows come back?
        latest_row = data.iloc[-1]                             # the most recent minute
        return {
            "ticker": ticker_symbol,
            "datetime": latest_row.name.strftime("%Y-%m-%d %H:%M"),   # .name = this row's label = its timestamp
            "price": float(latest_row["Close"]),
        }
    else:
        return {"error": f"No data found for ticker: {ticker_symbol}"}  # the agent can read this and react

tools = [FunctionTool.from_defaults(get_latest_price)]       # LlamaIndex's way to wrap a function as a tool

agent_prices = ReActAgent(
    llm=OpenAI(model="gpt-4o", api_key=OPENAI_API_KEY),
    tools=tools,
    timeout=120,              # give up after 120 s instead of hanging forever
    verbose=False,
)
```

1. `interval="1m"` asks for minute-by-minute rows instead of one row per day — so the "latest" really is the latest minute.
2. `data.iloc[-1]` is the last *row*. A single row knows its own label through `.name` — and since the rows are labelled by time, `latest_row.name` is the timestamp. (This is the confusing line. `.name` here has nothing to do with the stock's name.)
3. `.strftime("%Y-%m-%d %H:%M")` formats that timestamp as text like `2025-09-12 15:59`.
4. The `else` branch returns an **error message instead of crashing**. A ReAct agent can read "No data found" and try again with a corrected ticker.
5. `FunctionTool.from_defaults(fn)` is LlamaIndex's equivalent of `@function_tool`: it reads the name, docstring and type hints.

```python title="Python · lab_2d_react_price.py · step 2 · run it and stream the thinking"
handler = agent_prices.run("What is the last price of Apple?")   # start the job, get a tracking handle

async for ev in handler.stream_events():       # live updates while the agent works
    if isinstance(ev, AgentStream):            # only the "text chunk" events
        print(ev.delta, end="", flush=True)    # print each new chunk on the same line, immediately

response = await handler                       # wait for the final, complete answer
```

> **🧠 Analogy — food-delivery tracking:**
> `agent_prices.run(...)` places the order and hands you a **tracking link** (`handler`). `stream_events()` is the live map ("rider picked up the order…"). `AgentStream` events are the text updates — other event types (like tool calls) are skipped by the `if`. `ev.delta` is just the newest bit of text. Finally, `await handler` is the food arriving: the complete answer.

Thought: The current language of the user is: English. I need to use a tool to help me answer the question. Action: get_latest_price Action Input: {"ticker_symbol": "AAPL"} Thought: I can answer without using any more tools. I'll use the user's language to answer. Answer: The latest price of Apple (AAPL) is $234.06 as of September 12, 2025, 15:59.

The *Observation* (the tool's result) is fed back silently between the two thoughts. Because every step is written out, you can see exactly where a wrong answer came from — very useful when an auditor asks "why did the system say that?"

|  | Lab 1C · OpenAI Agents SDK | Lab 2D · LlamaIndex |
| --- | --- | --- |
| Make a tool | `@function_tool` above the function | `FunctionTool.from_defaults(fn)` |
| Make the agent | `Agent(name, instructions, model, tools)` | `ReActAgent(llm, tools, timeout)` |
| Run it | `Runner.run_sync(...)` → `.final_output` | `handler = agent.run(...)` → `await handler` |
| See the thinking | Traces / logs | Streamed Thought / Action lines |

##### Self-consistency: let five analysts vote on an earnings surprise

💰 Finance corner — what is an "earnings surprise"?

Before results, analysts publish forecasts; their average EPS forecast is the **consensus**. If the company reports more, that's a *beat*. Here consensus was **1.20** and reported EPS was **1.25**: a beat of (1.25 − 1.20) ÷ 1.20 ≈ **4.2%**. But the market judges the whole picture — revenue growth, margins, guidance, management changes. An EPS beat with falling margins and a departing CEO can be a *neutral* surprise.

Self-consistency asks the model the same chain-of-thought question several times (with some randomness), then takes the **majority vote**. Each path focuses on different evidence:

🧪 Simulation

##### Click a path to flip its conclusion, and watch the vote

- **Path 1** · EPS beat by ~4% → Positive surprise
- **Path 2** · EPS beat and revenue increased → Positive surprise
- **Path 3** · EPS beat but margins declined → Neutral surprise
- **Path 4** · EPS beat and guidance is positive → Positive surprise
- **Path 5** · EPS beat but a leadership change was announced → Neutral surprise

Majority vote → **Positive surprise** (3 of 5 paths). One brittle line of reasoning can't decide alone.

In practice, sample an odd number of paths, or one more to break the tie.

```python title="Python · self_consistency.py · try it yourself"
from collections import Counter
from openai import OpenAI

client = OpenAI()

cot_prompt = """You are a financial analysis agent.
Classify the earnings result as: Positive surprise, Neutral surprise or Negative surprise.
Reason step by step before producing the final classification.

Input:
EPS: 1.25 vs consensus 1.20
Revenue: +4% YoY
Margins: Declining
Guidance: Raised
Management: CEO departure announced

End with exactly one line: FINAL: Positive surprise | Neutral surprise | Negative surprise"""

answers = []
for _ in range(5):                                            # 5 independent reasoning paths
    r = client.responses.create(model="gpt-4.1-mini", input=cot_prompt, temperature=1.0)
    last_line = r.output_text.strip().splitlines()[-1]        # e.g. "FINAL: Positive surprise"
    answers.append(last_line.replace("FINAL:", "").strip())

votes = Counter(answers)                                      # counts each distinct answer
print(votes)                                                  # e.g. Counter({'Positive surprise': 3, 'Neutral surprise': 2})
print("Majority:", votes.most_common(1)[0][0])
```

1. `temperature=1.0` adds randomness, so the five paths reason differently. With temperature 0 you'd get five near-identical answers and the vote would be pointless.
2. Asking for a fixed last line (`FINAL: …`) makes the answer easy to pull out with `.splitlines()[-1]`.
3. `Counter` tallies the answers; `.most_common(1)[0][0]` is "the top answer's text".

Cost note: five paths = five times the tokens. Use it for decisions that matter, not for every headline.

#### 2.6 Lab 2E · Verified news agent (evaluator–optimizer loop)

**The request:** "Give me the latest 5 financial news items for the Eurozone. Reuters only, from the last two days, and a link for every item — I won't trade on anything I can't verify."

💰 Why so strict?

News moves prices within minutes. A hallucinated headline, or a week-old story presented as today's, can trigger a wrong trade. So the bank demands a trusted source, a date window and a link per item — and a second agent that checks all three before anything reaches a trader.

{{diagram:2}}

*The searcher keeps the whole conversation (`input_items`); the evaluator only ever sees the newest summary (`latest_outline`) — fresh eyes, fewer tokens. The loop ends on "successful" or when the retry counter passes the limit.*

🧪 Simulation

##### Step through two rounds of the loop (the map above lights up)

**Start.** Your request becomes the first item in the searcher's chat: `[{"content": msg, "role": "user"}]`. `latest_outline` is still `None`.

**Round 1 · the searcher writes.** It searches Reuters and writes 5 items. `to_input_list()` = your message + its reply. `latest_outline` = just the new summary text.

**Round 1 · the evaluator grades.** The judge sees only `latest_outline`. Its form: score **unsuccessful**, feedback *"Only 2 of the 5 news items fall strictly within the required date window."*

**Round 1 · feedback goes back in.** Two items are appended: a system message `"News Summary: …"` and a user message `"Feedback: … provide an external source link:"`. Counter → 1. Is 1 > 4? No → loop again.

**Round 2 · the searcher rewrites.** This time it sees its own earlier answer *and* the judge's complaint. It replaces the out-of-window stories and adds a date and link for each item.

**Round 2 · pass → stop.** Score **successful** — *"The news summary rigorously fulfills the specified requirements."* → `break` → `print(latest_outline)`.

* Web-search call items are also added to `input_items`; we leave them out of the count to keep it simple.

Get the flow first; the code for every box follows right after.

##### Step 1 — Dates, so the window is always "the last two days"

```python title="Python · lab_2e_news_loop.py · step 1 (pip install openai-agents)"
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Literal
from agents import Agent, Runner, WebSearchTool, ItemHelpers, TResponseInputItem

today_date   = datetime.now().strftime("%Y-%m-%d")                         # e.g. "2026-10-22"
two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")   # e.g. "2026-10-20"
```

> **⚠️ Classroom gotcha:**
> These dates are baked into the agents' instructions with f-strings at the moment you run the cell. Leave the notebook open overnight and the "last two days" window is stale — re-run this cell and the agent definitions.

##### Step 2 — The searcher

```python title="Python · lab_2e_news_loop.py · step 2"
INSTRUCTIONS_NEWS_SEARCH = (
    "You are a research news assistant specialized in Finance or any news that can have an impact "
    "on the financial health of a given company or a region. "
    "You search the web for a given region to collect the most important and recent news. "
    "Produce a concise summary of the results with citations. The summary must be "
    "2-3 paragraphs and less than 300 words. Capture the main points. Write succinctly. "
    f"Get only the latest news between 2 days ago {two_days_ago} and today {today_date}. "
    "Use only this resource: https://www.reuters.com/. "
    "For each item you are providing, specify the date on which the article was published. "
    "For each item you are providing, specify the complete external link to the article. "
    "This is important. Otherwise, don't give me a summary, if you don't provide a date and an external link. "
    "If you don't give a source link, it means that you are hallucinating. "
)

web_news_searcher = Agent(
    name="web_news_searcher",
    instructions=INSTRUCTIONS_NEWS_SEARCH,
    tools=[WebSearchTool()],          # OpenAI's hosted web search — no code of your own needed
)
```

Three finance constraints are encoded right in the instructions: **one trusted source**, **a date window**, and **a date + link per item**. Python joins adjacent strings in brackets into one long string, which is why it's written as many short lines.

##### Step 3 — The evaluator and its "form"

```python title="Python · lab_2e_news_loop.py · step 3"
@dataclass
class EvaluationFeedback:
    feedback: str                                    # free text: why it passed or failed
    score: Literal["successful", "unsuccessful"]     # exactly one of these two words — nothing else

news_evaluator = Agent(
    name="news_evaluator",
    instructions=(
        "You will be given a financial news summary in a given region (Euro, US, Asia) and you are "
        "asked to evaluate the completeness of external source links. "
        "Check whether the news summary is supported by external article links from https://www.reuters.com/. "
        f"Check whether the news summary was published between 2 days ago {two_days_ago} and today {today_date}. "
        "For each item of news, the date of the news must be explicitly provided. "
        "Check whether the news summary corresponds to the region or regions requested by the user. "
        "If the user requested 'n' news items, each item must be supported by an external source link, "
        "so you need to ensure that there are 'n' source links. "
        "External links are required for the user to verify the accuracy of the news. "
    ),
    output_type=EvaluationFeedback,                  # forces the answer into the form above
)
```

> **🧠 Analogy — a form with tick-boxes:**
> Without `output_type`, the judge could reply "mostly fine, one link looks odd" and your `if` statement wouldn't know what to do. The dataclass is a printed form: one comment box (`feedback`) and one tick-box with exactly two options (`score`). `Literal[...]` means "only these exact values". Now `result.score == "successful"` is always a clean yes/no.

##### Step 4 — The loop (with comments on every line)

```python title="Python · lab_2e_news_loop.py · step 4"
msg = input("User's request:")    # e.g. "Provide the latest 5 news in the Eurozone and specify the source for each one."
input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]   # the searcher's running chat
latest_outline: str | None = None   # will hold the newest news summary
max_iteration = 4                   # retry limit
nbr_iterations = 0                  # retries so far

while True:
    # 1) The searcher writes (or rewrites) the summary, seeing the whole chat so far
    news_searcher_result = await Runner.run(web_news_searcher, input_items)
    input_items = news_searcher_result.to_input_list()                       # old chat + the new reply
    latest_outline = ItemHelpers.text_message_outputs(news_searcher_result.new_items)  # just the new text

    # 2) The evaluator grades ONLY the newest summary
    news_evaluator_result = await Runner.run(news_evaluator, latest_outline)
    result: EvaluationFeedback = news_evaluator_result.final_output         # the filled-in form

    # 3) Passed? Stop.
    if result.score == "successful":
        print("Links check is good ==> stopping the iteration.")
        break

    # 4) Failed: add the summary and the judge's feedback to the chat, then go round again
    input_items.append({"content": f"News Summary: {latest_outline}", "role": "system"})
    input_items.append({"content": f"Feedback: {result.feedback}\n for each item in the news summary, "
                                   "provide an external source link:", "role": "user"})
    nbr_iterations += 1
    if nbr_iterations > max_iteration:
        print("Reached max_iteration ==> stopping the iteration.")
        break

print(latest_outline)
```

| Variable | What it is | Changes how? |
| --- | --- | --- |
| `input_items` | The searcher's whole conversation | Grows every round (reply + summary + feedback) |
| `.to_input_list()` | "Everything so far, ready to feed back in" | Old input + this run's new items |
| `.new_items` | Only what this run produced | Fresh each round |
| `latest_outline` | Plain text of the newest summary | Replaced each round |
| `result` | The judge's form: `.score` + `.feedback` | Replaced each round |
| `nbr_iterations` | Retry counter | +1 after each failure |

> **Note:**
> 💡 How many searches can actually happen?
>
> The check is `nbr_iterations > max_iteration`, so with `max_iteration = 4` the searcher can run **5 times**: the first try plus 4 retries. Change it to `>=` if you want 4 runs in total. Either way, a limit is essential — a loop between two LLMs with no limit can burn money forever.

##### Guardrails, finance edition

| Guardrail | Checks… | Finance example |
| --- | --- | --- |
| **Input** | The request, before the agent starts | A fundamental-analysis agent is asked for "Tesla's 5-year price chart" → stop early instead of wasting tokens on a wrong-scope answer |
| **Output** | The answer, before the user sees it | Block any reply that contains another client's name or account details |
| **Tool** | The arguments the LLM wants to pass to a tool | Ticker must look like a ticker and must not be on the bank's restricted list before calling the data API |
| **Task** | An intermediate result, before the next step uses it | In Lab 2F, check that the retrieval JSON really contains numbers before the analysis agent runs |

Framework support differs: the OpenAI Agents SDK has input/output guardrails, Google ADK has tool guardrails, CrewAI has task guardrails.
