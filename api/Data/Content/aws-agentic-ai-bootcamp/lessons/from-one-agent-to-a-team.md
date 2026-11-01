# From one agent to a team

**Future with Shivank** Agentic AI on AWS

Colour code used in every diagram

An agent Coordinator, supervisor, router Specialist, worker, tool Data, results, shared context LLM reasoning, decisions Problems, limits, risk

Section 4: Agents that work together

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Lesson 4 of 6:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Agentic AI on AWS, hands-on labs by Shivank Agrawal

#### Agents that work together

Section 4. One agent with tools goes a long way. When a job is too big, too varied or too slow for one agent, you build a team: a supervisor with workers, agents used as tools, swarms that hand work around, and graphs that route it along fixed paths.

Folder `section-04-multi-agent-patterns` Notebooks `01_supervisor_worker` `02_agent_as_tool` `03_graph_pattern` `04_swarm_pattern` Model: Claude Sonnet 4.6 on Amazon Bedrock

{{diagram:1}}

*The journey in this section. We start with why teams help, build four team shapes in four notebooks, and finish with the most important skill: knowing when you don't need a team at all.*

## 4.0 From one agent to a team

When a software team takes on a hard problem, nobody does everything alone. Architects, developers and testers each do what they're best at. A hospital works the same way, with doctors, nurses, specialists and administrators. The same idea applies to AI agents.

In Sections 1 to 3 you built single agents with tools and memory. For most use cases, one well-equipped agent is enough. But what if the problem is too big or too varied for one agent to handle well?

In this section you move from one agent to several. You'll see why one agent isn't always enough, then build the main ways of coordinating a team: a **supervisor** delegating to workers, agents reused as **tools**, **swarms** that hand work to each other, and **graphs** that route work along fixed paths. Along the way you'll learn when each pattern makes sense, and when it doesn't.

> **Think of it like this:**
> A wedding in India. One person can't book the hall, manage the caterer, handle the decorators, coordinate the mehendi artist and greet 500 guests. So there's a wedding planner (the coordinator) and specialists who each own one job. The planner doesn't cook; the caterer doesn't decorate. Multi-agent systems are built on exactly this division of labour.

#### What you'll learn here

1. When one agent isn't enough
2. What multi-agent patterns are
3. How agents communicate: sequential, parallel and collaborative
4. Common orchestration patterns: supervisor–worker, agent as tool, swarm and graph
5. When multi-agent is not the answer

#### Before you start

1. 1 A working Strands setup from Sections 1 to 3 Virtual environment, AWS credentials with Amazon Bedrock access, and `check_setup.py` passing.
2. 2 Basic Python functions and classes
3. 3 An AWS account with Bedrock permissions Every notebook calls Claude Sonnet 4.6 on Bedrock. Nothing else is created in your account, so there's nothing to clean up.
4. 4 REST APIs and JSON (helpful, not required)
5. 5 An IDE VS Code, JupyterLab or Kiro, whichever you've been using.
6. 6 A free Tavily API key for notebook 1 The news and sentiment agents search the web with Tavily. An Alpha Vantage key is optional; without it, financial data comes from Yahoo Finance, which needs no key.

| Notebook | Pattern | Example | On this page |
| --- | --- | --- | --- |
| `01_supervisor_worker.ipynb` | Supervisor–worker | Market research: news, financial and sentiment workers coordinated by a supervisor | 4.3 |
| `02_agent_as_tool.ipynb` | Agent as tool | Tutoring: a teacher delegates to math, writing and science tutors | 4.4 |
| `03_graph_pattern.ipynb` | Graph | E-commerce orders routed through risk, fraud, inventory, shipping and refund steps | 4.7 |
| `04_swarm_pattern.ipynb` | Swarm | Game level design: four specialists hand work to each other | 4.7 |

```bash title="terminal"
pip install -r requirements.txt
export TAVILY_API_KEY="tvly-..."          # notebook 1 (free key at tavily.com)
export ALPHA_VANTAGE_API_KEY="..."        # optional
jupyter lab
```

> **What's in requirements.txt:**
> `strands-agents` and `strands-agents-tools` (the agents, plus the ready-made Tavily search tool), `yfinance` (free Yahoo Finance data), `alpha_vantage` (optional market data), `pandas` and `boto3`.

## 4.1 When one agent isn't enough

Before the patterns, the why: when should several agents work together instead of one super-agent doing everything?

#### The problem with single agents

Imagine asking one agent to research the latest AI trends, analyse competitors' pricing, write a technical specification, generate the code, review that code for security issues, and build a presentation for executives. That's a lot to ask. These are the warning signs that one agent is carrying too much:

##### Context overload

It tries to track too many different tasks at once and loses focus, the **context rot** you met in Section 3.

##### Jack of all trades, master of none

Results are mediocre across every task instead of excellent and accurate in specific areas.

##### No parallelisation

Everything happens one step after another, even when tasks could run at the same time.

##### Hard to debug

When something goes wrong, it's hard to pinpoint which part of the process failed.

#### The multi-agent solution

Picture a busy restaurant. One person could take orders, cook, serve and wash up, but it would be slow. Instead there's a host, servers, chefs and dishwashers, each focused on what they do best. Together they deliver a smooth experience.

Multi-agent systems work the same way. Instead of one very complex agent, you build several specialised agents that cooperate. Under the hood, a **coordinator** agent receives the request, breaks it into subtasks, and delegates each one to the right specialist. The specialists do their work and report back, and the coordinator stitches the results into one response.

{{diagram:2}}

*One generalist vs a team of specialists. The coordinator breaks the request into subtasks and delegates; each specialist does one job well and reports back.*

##### Benefits of the multi-agent approach

1. 1 Specialisation Each agent becomes an expert in its domain, with a focused prompt and the right tools.
2. 2 Parallel processing Independent tasks run at the same time, saving time.
3. 3 Better debugging You can isolate and fix problems in one specific agent.
4. 4 Scalability Add new agents as the system grows, without rewriting everything.

Try it

##### The same six jobs, one agent vs a team

Total time

Context the busiest agent carries

> **One agent, six hats.** Everything runs one after another, the context fills with research notes, prices, spec, code and slides, and quality drops as it loses focus. If the security review finds a problem, you're searching one huge transcript for the cause.

> **Specialists in parallel where possible.** Research and pricing run together; the deck is built while the code is written. Dependencies still apply (no spec without research, no review without code), so it isn't 6× faster, but each agent stays focused and a failure points to one agent.

## 4.2 What are multi-agent patterns?

A **multi-agent pattern** is a structured way of organising several AI agents to work towards a common goal.

Think of an orchestra: strings, brass, woodwind and percussion each play their part, together, under a conductor. And just as music can be organised in different ways (a small chamber group, a large symphony, a jazz band that improvises), there are different patterns for organising agents. Each solves a particular kind of problem, and choosing the right one makes your system faster and easier to build.

Every multi-agent design answers four questions:

{{diagram:3}}

*Four questions behind every pattern. Orchestration, specialisation, collaboration and coordination. Each pattern in this section is a different set of answers to them.*

| Aspect | The question | Two ends of the spectrum |
| --- | --- | --- |
| Orchestration | How will information flow between agents? | A central coordinator (a conductor) ↔ agents talking directly (a jazz group) |
| Specialisation | What is each agent's focused role and toolset? | One narrow job per agent ↔ broader generalists |
| Collaboration | How do agents share information and build on each other's work? | Output of one becomes input of the next ↔ ongoing discussion |
| Coordination | Who decides the order of work? | A workflow you define (a classical score) ↔ agents figure it out (improvisation) |

These four aspects underpin every pattern ahead. We start with the simplest and most common one.

## 4.3 Lab: the supervisor–worker pattern

Your first multi-agent pattern, and the most common one in production. One agent coordinates; specialist agents do the work.

In the **supervisor–worker** pattern, one agent acts as the coordinator. It receives the request, decides which specialists to call, delegates the work, and combines their results into one response. The workers focus on their tasks and report back to the supervisor.

#### A story in three versions

You're building a market-research assistant. An investor asks: *"Should I invest in electric vehicle companies?"*

1. 1 Version 1: one agent It scans recent news, analyses stock performance, checks social media sentiment, reads analyst reports and compares competitors. About five minutes per question. Fine for a few questions a day. Then your manager says it must handle hundreds of questions an hour.
2. 2 Version 2: three agents in parallel A **news agent** scans EV news, a **financial agent** analyses stock performance, a **sentiment agent** checks social media. The tasks are independent, so they run at the same time: ideally about three times faster. It works! But the investor now gets three separate answers:

##### News agent

"Several large automakers announced new battery plants. One EV start-up reported production delays."

##### Financial agent

"EV stocks are up this quarter on average. Valuations of pure-play EV makers are high; one is burning cash fast."

##### Sentiment agent

"Social media sentiment is mixed. Retail investors are bullish; charging infrastructure is a common worry."

The investor stares at this wall of unconnected facts and asks: *"So… should I invest or not?"* Each agent did its job perfectly, but nobody **synthesised** the information into a recommendation.

1. 3 Version 3: add a supervisor The supervisor receives the question and thinks: *"This person needs news context, financial analysis and market sentiment. I have three workers for exactly those."* It calls all three at once, rephrasing the question for each, then weaves their answers into one recommendation.

{{diagram:4}}

*All communication goes through the supervisor. Workers do specialised tasks and report back; they never talk to each other (the red ✕s). Each worker gets a question rephrased for its speciality.*

All three workers run at the same time. Two minutes later the supervisor has every perspective and answers with one recommendation, something like: *"The EV sector shows strong growth, but valuations are high and some companies face production problems. Established makers look steadier than newer entrants. With a high risk tolerance the sector looks promising; if you prefer stability, wait for valuations to settle."* One coherent answer, and the investor can decide.

##### Workers stay independent

The news agent doesn't care what the financial agent is doing. Each focuses on its expertise and reports back.

##### Debugging is straightforward

Wrong financial data? Check the financial agent. Old news? Check the news agent. The supervisor handles synthesis, not domain logic, so bugs stay isolated.

##### New skills are easy to add

Need regulatory analysis? Create a regulatory agent and tell the supervisor about it. Existing workers don't change.

Try it

##### Workers on their own vs with a supervisor

on Add a regulatory agent

> **Raw workers, no supervisor:** “So… should I invest or not?” 3 correct answers, no synthesis, no recommendation.

> **sentiment_agent:** Mixed sentiment. Retail investors bullish; institutions cautious; charging infrastructure is a common worry.

> **Supervisor:** Needs news, financials and sentiment. Calling 3 workers in one turn.

> **Tool calls:** news_agent · financial_agent · sentiment_agent (run concurrently)

> **Supervisor, final answer:** Growth is real, but valuations are high and some newer makers are struggling. Established manufacturers look steadier. High risk tolerance: the sector looks promising. Prefer stability: wait for valuations to settle. (Educational analysis, not financial advice.) With the regulatory agent ticked, the answer also says: “Incentive rules are shifting, which adds uncertainty.”

> **regulatory_agent** (when the regulatory agent is added): EV incentives continue in several markets, but subsidy rules are being revised; check the rules where you invest.

> Adding the regulatory agent changed one line: the supervisor's tool list. The other workers didn't change at all.

Ask: "Should I invest in EV companies?"

#### Run the notebook: `01_supervisor_worker.ipynb`

The notebook builds exactly this assistant with real data: Tavily web search for news and sentiment, and Yahoo Finance (through `yfinance`) for prices and fundamentals. Cell numbers on this page count code cells only, so they skip the notebook's text cells.

```python title="cell 1"
%pip install -q -r requirements.txt
```

```python title="cell 2: model"
import os
from strands.models.bedrock import BedrockModel

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
os.environ.setdefault("AWS_REGION", REGION)

model = BedrockModel(model_id=MODEL_ID, region_name=REGION)
print(f"Using {MODEL_ID} in {REGION}")
```

One `BedrockModel` object, shared by every agent in the notebook. All four notebooks start with this same cell.

##### Configure API keys

Set them in your shell before starting Jupyter (recommended), or uncomment the two lines in this cell:

```python title="cell 3"
# os.environ["TAVILY_API_KEY"] = "tvly-..."
# os.environ["ALPHA_VANTAGE_API_KEY"] = "..."

if not os.getenv("TAVILY_API_KEY"):
    print("⚠️  TAVILY_API_KEY not set — the news and sentiment agents cannot search the web.")
else:
    print("✓ TAVILY_API_KEY is configured")

if not os.getenv("ALPHA_VANTAGE_API_KEY"):
    print("ℹ️  ALPHA_VANTAGE_API_KEY not set — financial data comes from yfinance (free, no key).")
else:
    print("✓ ALPHA_VANTAGE_API_KEY is configured")
```

> **Keep keys out of notebooks you share:**
> An API key pasted into a cell travels with the notebook file. Prefer `export` in your shell, so the key lives only in your environment.

```python title="cell 4: imports"
import yfinance as yf
from strands import Agent, tool
from strands_tools.tavily import tavily_search
```

`tavily_search` is a ready-made tool from `strands-agents-tools`. It reads `TAVILY_API_KEY` from the environment and supports options such as `time_range` ("day", "week", "month", "year") and `max_results`.

##### Custom financial tools (Yahoo Finance)

```python title="cell 5"
def _num(value, money=False, pct=False):
    """Format numbers safely — Yahoo sometimes leaves fields empty."""
    if not isinstance(value, (int, float)):
        return "N/A"
    if pct:
        return f"{value * 100:.2f}%"
    return f"${value:,.2f}" if money else f"{value:,.2f}"

@tool
def get_stock_price(symbol: str) -> str:
    """Get the current stock price and key metrics using Yahoo Finance.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA', 'MSFT')
    """
    try:
        info = yf.Ticker(symbol).info
        return (
            f"Stock: {symbol}\n"
            f"Current Price: {_num(info.get('currentPrice') or info.get('regularMarketPrice'), money=True)}\n"
            f"Market Cap: {_num(info.get('marketCap'), money=True)}\n"
            f"P/E Ratio: {_num(info.get('trailingPE'))}\n"
            f"52 Week High: {_num(info.get('fiftyTwoWeekHigh'), money=True)}\n"
            f"52 Week Low: {_num(info.get('fiftyTwoWeekLow'), money=True)}\n"
            f"Average Volume: {_num(info.get('averageVolume'))}\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}"
        )
    except Exception as e:
        return f"Error fetching stock data for {symbol}: {e}"

@tool
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """Get historical stock price data.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        period: One of 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    try:
        hist = yf.Ticker(symbol).history(period=period)
        if hist.empty:
            return f"No historical data available for {symbol}"
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        change_pct = (end_price - start_price) / start_price * 100
        return (
            f"Historical Data for {symbol} ({period}):\n"
            f"Starting Price: ${start_price:.2f}\n"
            f"Ending Price: ${end_price:.2f}\n"
            f"Change: {change_pct:+.2f}%\n"
            f"Highest: ${hist['High'].max():.2f}\n"
            f"Lowest: ${hist['Low'].min():.2f}\n"
            f"Average Volume: {hist['Volume'].mean():,.0f}\n\n"
            f"Recent 5-day trend:\n{hist[['Close', 'Volume']].tail().to_string()}"
        )
    except Exception as e:
        return f"Error fetching historical data for {symbol}: {e}"

@tool
def get_company_financials(symbol: str) -> str:
    """Get company financial metrics: revenue, margins, growth and leverage.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    """
    try:
        info = yf.Ticker(symbol).info
        return (
            f"Financial Metrics for {symbol}:\n"
            f"Revenue: {_num(info.get('totalRevenue'), money=True)}\n"
            f"Revenue Growth: {_num(info.get('revenueGrowth'), pct=True)}\n"
            f"Gross Profit: {_num(info.get('grossProfits'), money=True)}\n"
            f"Profit Margin: {_num(info.get('profitMargins'), pct=True)}\n"
            f"Operating Margin: {_num(info.get('operatingMargins'), pct=True)}\n"
            f"EBITDA: {_num(info.get('ebitda'), money=True)}\n"
            f"Earnings Growth: {_num(info.get('earningsGrowth'), pct=True)}\n"
            f"Return on Equity: {_num(info.get('returnOnEquity'), pct=True)}\n"
            f"Debt to Equity: {_num(info.get('debtToEquity'))}\n"
            f"Free Cash Flow: {_num(info.get('freeCashflow'), money=True)}"
        )
    except Exception as e:
        return f"Error fetching financial data for {symbol}: {e}"

print(get_stock_price(symbol="AAPL"))  # tools are still plain functions you can call
```

1. a `_num(...)`: a defensive formatter Yahoo Finance sometimes leaves fields empty. Instead of crashing on `None`, the tool prints "N/A". The leading underscore marks it as a private helper, not a tool.
2. b Three focused `@tool` functions Current price and key metrics, price history over a period, and company fundamentals. Each returns a plain-text summary the model can read, and each catches errors and returns them as text so one failed lookup doesn't break the whole run.
3. c Test before you give it to an agent The last line calls a tool directly. A decorated tool is still a normal Python function, so you can check its output first.

```text title="outputillustrative numbers"
Stock: AAPL
Current Price: $…
Market Cap: $…
P/E Ratio: …
52 Week High: $…
52 Week Low: $…
Average Volume: …
Sector: Technology
Industry: Consumer Electronics
```

##### Optional: an Alpha Vantage tool

```python title="cell 6"
from alpha_vantage.timeseries import TimeSeries

@tool
def get_alpha_vantage_quote(symbol: str) -> str:
    """Get the latest stock quote from the Alpha Vantage API.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    """
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not key:
        return "ALPHA_VANTAGE_API_KEY is not set."
    ts = TimeSeries(key=key, output_format="pandas")
    data, _ = ts.get_quote_endpoint(symbol=symbol)
    return data.to_string()

financial_tools = [get_stock_price, get_stock_history, get_company_financials, tavily_search]
if os.getenv("ALPHA_VANTAGE_API_KEY"):
    financial_tools.append(get_alpha_vantage_quote)
```

Use this instead of, or alongside, Yahoo Finance if you have a key. Other data providers worth knowing include Polygon.io, Finnhub and Financial Modeling Prep. The financial agent's toolbox is built conditionally: the Alpha Vantage tool is only added when the key exists, so the agent never sees a tool that can't work.

##### The worker agents

```python title="cell 7"
news_agent = Agent(
    name="news_agent",
    description="Researches recent news and developments about companies and industries.",
    model=model,
    system_prompt="""You are a news research specialist. Search for recent news and developments about companies and industries.

When searching:
- Focus on recent news (use time_range='week' or 'month')
- Prefer reliable sources such as major news outlets
- Summarize key developments and trends
- Include specific facts, dates, and figures when available""",
    tools=[tavily_search],
    callback_handler=None,
)

financial_agent = Agent(
    name="financial_agent",
    description="Analyzes stock prices, price history, and company financial metrics.",
    model=model,
    system_prompt="""You are a financial analysis specialist. Analyze financial metrics, stock performance, and company valuations.

When analyzing:
- Use get_stock_price for current prices and key metrics
- Use get_stock_history for price trends
- Use get_company_financials for revenue, earnings, and growth
- Compare companies within the same sector and give specific numbers""",
    tools=financial_tools,
    callback_handler=None,
)

sentiment_agent = Agent(
    name="sentiment_agent",
    description="Analyzes market and investor sentiment from forums, social media, and commentary.",
    model=model,
    system_prompt="""You are a market sentiment analyst. Analyze market sentiment from social media, forums, and investor discussions.

When analyzing sentiment:
- Look for both bullish and bearish opinions
- Identify common concerns and excitement points
- Distinguish retail from institutional sentiment
- Summarize the overall market mood""",
    tools=[tavily_search],
    callback_handler=None,
)
print("✓ Worker agents created")
```

| Argument | What it does here |
| --- | --- |
| `name` | Becomes the tool name the supervisor sees: letters, digits, underscores or hyphens, like `news_agent`. |
| `description` | Becomes the tool description: how the supervisor knows when to call this worker. |
| `system_prompt` | The worker's job description, with concrete instructions about which tools to use and how. |
| `tools` | Each worker gets only the tools for its speciality. News and sentiment share Tavily search; finance gets the Yahoo Finance tools. |
| `callback_handler=None` | Silences the worker's own streaming output, so you only see the supervisor's answer instead of four voices talking at once. |

##### The supervisor agent

```python title="cell 8"
supervisor = Agent(
    name="research_supervisor",
    model=model,
    system_prompt="""You are a market research coordinator. When asked about investment opportunities:

1. Work out what information is needed
2. Delegate to the specialist agents:
   - news_agent: recent developments and industry news
   - financial_agent: financial metrics and performance data
   - sentiment_agent: market sentiment and investor opinions
3. Synthesize their responses into one balanced recommendation

This is educational analysis, not financial advice — say so briefly at the end.""",
    tools=[news_agent.as_tool(), financial_agent.as_tool(), sentiment_agent.as_tool()],
)
print("✓ Supervisor created")
```

`agent.as_tool()` wraps a worker so the supervisor can call it like any other tool. (Passing the agents directly in `tools=[...]` does the same thing; you'll see that in the next lab.) By default each call starts the worker from a clean slate, so one question's research doesn't leak into the next. The supervisor's prompt tells it how to delegate and how to synthesise, and it ends with a guardrail: this is education, not financial advice.

##### Run the multi-agent system

```python title="cell 9"
question = "Should I invest in electric vehicle companies?"
print(f"Question: {question}\n")

response = supervisor(question)
```

```text title="outputillustrative, shortened"
Question: Should I invest in electric vehicle companies?

I'll gather recent news, financial data and market sentiment, then combine them.
Tool #1: news_agent
Tool #2: financial_agent
Tool #3: sentiment_agent
```

Notice the three tool calls. Claude usually asks for all three workers in a single turn, and Strands runs tool calls from the same turn **concurrently** by default, so the three workers really do research in parallel. Your run will quote real, current figures from the live searches.

##### EV investment: a balanced view

**News:** large automakers keep expanding EV and battery capacity; some newer EV makers face production delays.

**Financials:** sector revenue is growing, but valuations of pure-play EV makers are high and several are not yet profitable.

**Sentiment:** retail investors are mostly bullish; institutional investors are cautious about valuations.

**Recommendation:** established manufacturers look steadier than newer entrants. With a high risk tolerance the sector looks promising; if you prefer stability, wait for valuations to normalise.

*This is educational analysis, not financial advice.*

##### Try different questions

```python title="cell 10"
questions = [
    "What's the outlook for renewable energy stocks?",
    "Is the semiconductor industry a good investment right now?",
]

for q in questions:
    print(f"\n{'=' * 80}\nQuestion: {q}\n{'=' * 80}")
    supervisor(q)
```

Same supervisor, same workers, different sectors. Nothing about the team is specific to EVs; the supervisor works out what each question needs.

##### Specialisation

Each worker has one job and the right tools for it.

##### Coordination

The supervisor decides whom to ask and combines the answers.

##### Modularity

Add a new worker without touching the others.

> **Making it production-ready:**
> Add retries and caching for API calls, respect rate limits, run asynchronously, and add tracing so you can see every call (Section 7).

#### The trade-offs of supervisor–worker

{{diagram:5}}

*Three costs of having one boss. Each has well-known fixes, which is why the pattern still dominates in production.*

1. 1 The supervisor is a **bottleneck** Every decision flows through one agent. In production you address this with **horizontal scaling** (run several supervisor instances), caching (repeated questions return instantly) and **prompt caching**. For high volume, add load balancing and asynchronous processing.
2. 2 It's a **single point of failure** If the supervisor crashes, the system stops. You need health checks, automatic restarts, and checkpoint management so the supervisor resumes from its last known state. For critical systems, run redundant supervisors with a **failover** mechanism.
3. 3 Workers can't collaborate directly If the sentiment agent discovers something the financial agent should know, it has to go through the supervisor. That's fine for simple workflows; for real negotiation you need collaborative communication, covered in 4.6.

> **Why it's still the favourite:**
> Most multi-agent systems don't need complex negotiation. They need clear accountability, simple communication and easy debugging. That's why supervisor–worker is the most common pattern in production.
