# Agent design patterns — finance edition

## Agent design patterns — finance edition

You know the patterns. What's new here is **what they look like when money is on the line**, and the **code that builds each one** — six labs, each explained variable by variable.

⏭️ Already covered — we won't repeat

What tool use, working / episodic / semantic / procedural memory, RAG, guardrails, LLM-as-a-judge, sequential multi-agent orchestration and context management *are*. We use those words freely below and spend the time on finance knowledge and code.

| Pattern you know | Finance lab on this page |
| --- | --- |
| Tool use | 2A · Pull Apple's ratios from a financial-data API |
| Working memory | 2B · A rebalancing chat that remembers the portfolio |
| Episodic memory | 2C · The rebalancing agent writes a "journal" and reads it next time |
| Planning, ReAct, self-consistency | 2.5 · Trend detection, live price with ReAct (Lab 2D), earnings-surprise vote |
| LLM-as-a-judge (evaluator–optimizer) | 2E · A news agent whose work is checked by a second agent |
| Sequential orchestration | 2F · Retrieval → Analysis → Buy/Hold/Sell |

#### 2.1 Finance crash course: the three ratio families

Labs 2A and 2F feed financial ratios to agents. If you can't read the ratios, you can't tell whether the agent's conclusion is sensible — so let's learn them first.

> **🧠 Analogy — your friend wants you to invest in her café:**
> - **Profitability** — "Does the café actually keep money from each coffee it sells?"
> - **Valuation** — "Is the price she's asking for a share of the café fair, compared with what it earns?"
> - **Liquidity** — "Can it pay this month's milk supplier and rent from the cash in the till and bank?"

| Ratio | Formula (in words) | Read it as |
| --- | --- | --- |
| **Profitability — how efficiently it makes money** |  |  |
| Gross margin | (Revenue − cost of making the products) ÷ revenue | Of every $100 sold, what's left after production cost |
| Operating margin | Operating income ÷ revenue | …after also paying salaries, R&D, marketing |
| Net profit margin | Net income ÷ revenue | …after interest and tax too — the true profit per $100 |
| Return on assets (ROA) | Net income ÷ total assets | Profit per $1 of everything the company owns |
| Return on equity (ROE) | Net income ÷ shareholders' equity | Profit per $1 of the owners' money on the books |
| **Valuation — is the price tag reasonable?** |  |  |
| Price-to-earnings (P/E) | Share price ÷ EPS | Dollars you pay for $1 of yearly profit |
| Price-to-book (P/B) | Market value ÷ shareholders' equity | Price vs the accounting value of the company |
| Price-to-cash-flow / free-cash-flow | Market value ÷ operating (or free) cash flow | Like P/E, but using real cash instead of accounting profit |
| EV-to-EBITDA | (Market value + debt − cash) ÷ earnings before interest, tax, depreciation & amortisation | Price of the *whole* business vs its operating earnings |
| EV-to-sales | Enterprise value ÷ revenue | How many years of sales the whole business costs |
| **Liquidity — can it pay the bills due this year?** |  |  |
| Current ratio | Current assets ÷ current liabilities | Short-term resources per $1 of bills due within a year |
| Quick ratio | (Current assets − inventory) ÷ current liabilities | Same, counting only things that turn into cash fast |
| Cash ratio | Cash & equivalents ÷ current liabilities | The strictest test: cash alone vs the bills |
| Working capital | Current assets − current liabilities | An amount, not a ratio: the short-term cushion |

##### Apple through the ratio lens (values our agents fetched for fiscal 2025)

**Profitability** strong

Gross margin

46.9%

~$47 of every $100 sold is left after making the products.

Operating margin

32.0%

$32 left after running the whole company.

Net profit margin

26.9%

~$27 true profit per $100 of sales.

Return on assets

30.9%

31 cents of profit a year per $1 it owns.

Return on equity

171%

Looks impossible. It isn't — see the simulation below.

**Valuation** expensive

P/E

36.4

Investors pay ~$36 for each $1 of yearly profit.

P/B

55.3

Price is 55× book value — same small-equity effect as ROE.

EV / EBITDA

28.7

The whole business costs ~29 years of operating earnings.

EV / Sales

10.0

~10 years of revenue.

**Liquidity** below 1 — but read on

Current ratio

0.89

$0.89 of short-term assets per $1 of bills due this year.

Quick ratio

0.57

Same, without inventory.

Cash ratio

0.33

Cash alone covers 33 cents per $1.

🧪 Simulation

##### Why is Apple's ROE 171%? Shrink the denominator.

Profit stays fixed at **$100**. Now the company uses its cash to **buy back its own shares**, which shrinks shareholders' equity on the balance sheet. Drag the slider:

Shareholders' equity: $500

500

> **⚠️ The lesson for agent builders:**
> A ratio is a fraction — always look at the denominator. Same with liquidity: in our run the agent said Apple's current ratio below 1 signals "potential liquidity issues". A human analyst would add that Apple generates very large operating cash flow every quarter and keeps big long-term investments, so a ratio under 1 is a deliberate choice, not distress. **The tool makes the numbers trustworthy; the interpretation is still the LLM's** — and it can be shallow. Ask for comparisons with peers and with the company's own history in your prompt.

- This is Apple territory: years of buybacks have shrunk equity so much that ROE looks enormous.
- Already far above a typical company's 10–20%. Nothing changed in the business — only the denominator.
- A normal-looking ROE.

Price-to-book has the same denominator (equity), which is why Apple's P/B is 55.

#### 2.2 Lab 2A · The ratio retriever (tool use)

**The request:** "Give me Apple's liquidity ratios for the latest fiscal year, and explain what each one means." We'll use **Finance Toolkit**, a Python library that pulls financial statements from the Financial Modeling Prep API and calculates dozens of ratios for you.

##### Step 1 — Imports and keys

```python title="Python · lab_2a_ratio_tool.py · step 1 (pip install openai-agents financetoolkit)"
import os
import pandas as pd
from financetoolkit import Toolkit
from agents import Agent, Runner, function_tool

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
FINANCIAL_MODELING_PREP_API_KEY = os.environ["FINANCIAL_MODELING_PREP_API_KEY"]
```

##### Step 2 — The tool: fetch everything, keep only what we need

```python title="Python · lab_2a_ratio_tool.py · step 2"
@function_tool
def get_company_fundamentals(ticker: str) -> dict[str, pd.DataFrame]:
    """Get profitability, valuation and liquidity ratios for a given ticker."""
    companies = Toolkit(
        [ticker], api_key=FINANCIAL_MODELING_PREP_API_KEY, start_date="2022-01-01"
    )
    ratios = companies.ratios.collect_all_ratios()     # ONE big table: rows = ratio names, columns = years

    # Our three "shopping lists"
    profitability_ratios_names = ["Return on Equity", "Return on Assets", "Gross Margin",
                                  "Operating Margin", "Net Profit Margin"]
    valuation_ratios_names = ["Price-to-Earnings", "Price-to-Book", "Price-to-Cash-Flow",
                              "Price-to-Free-Cash-Flow", "EV-to-EBITDA", "EV-to-Sales"]
    liquidity_ratios_names = ["Current Ratio", "Quick Ratio", "Cash Ratio", "Working Capital",
                              "Operating Cash Flow Ratio", "Operating Cash Flow to Sales Ratio",
                              "Short Term Coverage Ratio"]

    return {
        "profitability_ratios": ratios.loc[ratios.index.intersection(profitability_ratios_names)],
        "valuation_ratios":     ratios.loc[ratios.index.intersection(valuation_ratios_names)],
        "liquidity_ratios":     ratios.loc[ratios.index.intersection(liquidity_ratios_names)],
    }
```

1. `Toolkit([ticker], api_key=..., start_date="2022-01-01")` — "open an account for this list of tickers, from 2022 onwards". It takes a *list* even for one company, because it can compare many.
2. `collect_all_ratios()` returns one big DataFrame with dozens of rows (one per ratio) and one column per year.
3. The three `..._names` lists are our **shopping lists**: the rows we actually want.
4. `ratios.index.intersection(names)` — "which of my shopping-list names really exist as row labels in the table?" Names that don't exist are quietly dropped.
5. `ratios.loc[...]` then picks exactly those rows. Without the intersection, one misspelt name would crash `.loc` with a `KeyError`.
6. The tool returns a dictionary of three small tables. The SDK turns this into text for the LLM.

🧪 Simulation

##### Watch `.index.intersection()` + `.loc[]` pick rows

Your shopping list (green = found in the table, red = not found → dropped):

`ratios.index.intersection(list)` → 5 of 5 names found → `ratios.loc[...]` returns those **5 highlighted rows**.

Typo list example — Dropped: `Return on Equities`, `Current Ratios` — not a row label in the table. Without `.intersection()`, `ratios.loc[list]` would stop with a `KeyError`. With it, the typo is silently skipped — safe, but check your spelling!

> **💡 Pro tip:**
> The SDK converts whatever your tool returns into text. Small DataFrames print fine; for larger ones, return `df.round(3).to_dict()` so the LLM gets compact, clean numbers instead of a wide printed table.

##### Step 3 — The agent and the question

```python title="Python · lab_2a_ratio_tool.py · step 3"
fundamental_retrieval_agent = Agent(
    name="Fundamental Retrieval Agent",
    model="gpt-4o-mini",
    instructions="""
You are a Fundamental Retrieval Agent.
Tasks:
1) Call the fundamentals tool for the specified ticker.
2) Output the desired set of ratios.
""",
    tools=[get_company_fundamentals],
)

fundamental_results = await Runner.run(fundamental_retrieval_agent, """Proceed step by step:
1- List 3 liquidity ratios and explain their significance.
2- Provide Apple's values for the three listed liquidity ratios for the most
recent fiscal year, knowing that we are in 2026.
""")
print(fundamental_results.final_output)
```

1. The question is written as numbered steps — first explain, then fetch. Step-by-step requests give tidier, more complete answers.
2. `knowing that we are in 2026` tells the model today's year, so it picks the right "most recent fiscal year" instead of guessing from its training cutoff. Small line, big difference.

### Apple's Liquidity Ratios for the Most Recent Fiscal Year (2025) 1. Current Ratio: 0.8933 — a ratio below 1 suggests potential liquidity issues. 2. Quick Ratio: 0.5704 — … 3. Cash Ratio: 0.3302 — …

The figures are real (from the API). The comment "potential liquidity issues" is the LLM's own reading — exactly the shallow interpretation the warning above told you to question.

#### 2.3 Lab 2B · Working memory: a rebalancing chat that remembers

💰 Finance corner — rebalancing in 5 words

- **Asset allocation** — how the money is split: e.g. 70% stocks, 20% bonds, 10% cash.
- **Rebalancing** — buying and selling to move that split back to where it should be.
- **Volatility regime** — is the market calm (low) or jumpy (high) right now?
- **Market trend** — rising (bullish) or falling (declining / bearish)?
- **Defensive sectors** — Healthcare and Utilities: people still buy medicine and electricity in a recession, so these hold up better.

A typical rule set: *no sector above 35%* (avoid putting too many eggs in one basket) and *at least 30% in defensive sectors*.

🧪 Simulation

##### Be the rebalancing agent: check the rules, apply the trades

Edit any weight (%) or rule. The checker does what the agent's "reasoning steps" do.

Rule: max per sector (%)

35

Rule: min Healthcare + Utilities (%)

30

Agent's proposal: sell 8% Tech, buy 6% Healthcare + 2% Utilities. Client's tweak: exit Energy completely, put that 10% into Utilities ("I want stable dividends").

Rebalancing checker messages (default state, shown in order):

- ✗ Sector cap broken: Tech 40% > 35%
- ✗ Defensive too low: Healthcare + Utilities = 25% < 30%
- ✓ Weights add up to 100%
- ✓ No sector above 35%
- ✓ Defensive OK: Healthcare + Utilities = 30% ≥ 30%
- ✗ Weights add up to 105%, not 100%

Red tick = sector cap. Blue = defensive sectors.

##### Step 1 — The agent

```python title="Python · lab_2b_working_memory.py · step 1"
from agents import Agent, Runner, SQLiteSession

portfolio_agent = Agent(
    name="Portfolio Rebalancing Agent",
    model="gpt-4o-mini",
    instructions="""You are a Portfolio Rebalancing Agent for a professional investor.
Your goal is to propose clear, explainable rebalancing actions that keep the
portfolio aligned with the target risk/return profile and constraints.
Your role
- Analyze the current portfolio (weights, asset classes, sectors, factors, cash).
- Incorporate market regime information (volatility, trends, macro environment).
- Compare current allocation to:
  - Target allocation or risk budget (if provided),
  - Or to a reasonably diversified allocation based on the information you have.
- Propose specific rebalancing trades with approximate percentage changes and short rationales.
- Prioritize diversification, risk control, and alignment with the investor's objectives.
- Keep answers concise and structured, and state assumptions when information is missing.
- Treat the allocation provided in the user's prompt as the portfolio's current allocation.
Always explain your reasoning.""",
)
```

Two lines matter most in finance: **"state assumptions when information is missing"** (an advisor must say "I assumed you want capital protection" rather than silently guessing) and **"always explain your reasoning"** (every recommendation must be explainable to a client or a regulator).

##### Step 2 — Create the notepad (the session)

```python title="Python · lab_2b_working_memory.py · step 2"
session_ptf_rebal = SQLiteSession("conversation_ptf")    # a fresh notepad named "conversation_ptf"

# Same, but saved in a file so it survives a restart:
# session_ptf_rebal = SQLiteSession("conversation_ptf", "portfolio_sessions.db")
```

> **🧠 Analogy — the trader's desk notepad:**
> All day a trader scribbles open positions and the client's instructions on a notepad. At 4 pm the notepad goes in the bin. `SQLiteSession` is that notepad: by default it lives only in your computer's RAM and vanishes when the program stops. The name `"conversation_ptf"` is the label on the notepad, so you could keep several clients' notepads apart.

##### Step 3 — Two turns, same notepad

```python title="Python · lab_2b_working_memory.py · step 3"
input_user_1 = """Current Market Situation:
- Volatility Regime: high
- Market Trend: declining
Current Portfolio State:
- Portfolio: {"stocks": 0.70, "bonds": 0.20, "cash": 0.10}
What rebalancing action should I take?"""

output_1 = await Runner.run(
    starting_agent=portfolio_agent,
    input=input_user_1,
    session=session_ptf_rebal,      # read what's on the notepad, then write this turn onto it
)
print(output_1.final_output)        # suggests ~50% stocks / 40% bonds / 10% cash (defensive)

input_user_2 = "In this case, I'm reducing equity to 50%, increasing bonds to 35% and cash to 15%."
output_2 = await Runner.run(
    starting_agent=portfolio_agent,
    input=input_user_2,
    session=session_ptf_rebal,      # SAME notepad → the agent still knows the 70/20/10 starting point
)
print(output_2.final_output)
```

Notice `input_user_1` is a plain string, so its curly braces are just characters. Remember this — in Lab 2C, braces become special.

🧪 Simulation

##### What does the LLM actually receive on turn 2?

**user · turn 1:** Volatility high, trend declining. Portfolio: stocks 0.70, bonds 0.20, cash 0.10. What rebalancing action should I take?

**assistant · turn 1:** Assumption: capital preservation. Suggest stocks 50%, bonds 40%, cash 10% …

**user · turn 2:** In this case, I'm reducing equity to 50%, increasing bonds to 35% and cash to 15%.

With the session, the model sees all three messages. It knows you started at 70 / 20 / 10, so it can size the trades: **sell 20% stocks, buy 15% bonds, add 5% cash**.

Without the session, only turn 2 is sent. "In this case"? Reducing equity *from what*? The model must guess the starting portfolio — and may confidently invent one.

##### Step 4 — Read the notepad back (the part that confuses everyone)

Before we write any code, look at **what the session stores**. User messages and assistant messages are stored in *different shapes*:

all_items = [ { "role": "user", "content": "Current Market Situation: ..." }, ← a plain string { "role": "assistant", "content": [ { "type": "output_text", "text": "### Current Portfolio..." } ] }, ← a LIST of parts { "role": "user", "content": "In this case, I'm reducing..." }, { "role": "assistant", "content": [ { "type": "output_text", "text": "..." } ] }, ]

> **🧠 Analogy — letter vs envelope:**
> A user message is a **single letter**: read it directly. An assistant message is an **envelope** that can hold several pages (text, citations, …). To read it you open the envelope and take page 0's text: `content[0]["text"]`.

```python title="Python · lab_2b_working_memory.py · step 4 (simplified, same result)"
all_items = await session_ptf_rebal.get_items()    # everything on the notepad, oldest first
conversation_history = []                           # we'll fill this with (role, text) pairs

for i, msg in enumerate(all_items, 1):              # i counts 1, 2, 3 … (only for printing)
    role = msg.get("role", "unknown")               # "user" or "assistant"; tool-call items have no role
    content = msg.get("content", "")

    if role == "user":
        text = content                              # a letter: already a string
    elif role == "assistant":
        text = content[0]["text"]                   # an envelope: open it, take page 0's text
    else:
        continue                                    # skip tool calls and other item types

    print(f"{i}. {role}: {text}")
    print("--" * 50)
    conversation_history.append((role, text))       # save a clean (role, text) pair
```

1. `.get("role", "unknown")` is a safe lookup: if an item has no `"role"` key (tool calls don't), you get `"unknown"` instead of a crash.
2. `enumerate(all_items, 1)` gives you a counter `i` starting at 1 alongside each item — just for numbered printing.
3. `conversation_history` ends up as a simple list of pairs: `[("user", "Current Market…"), ("assistant", "### Current Portfolio…"), …]`. **This variable is the bridge into Lab 2C.**

💰 Why this matters on a trading desk

Without the session, turn 2 ("reduce equity to 50%") arrives with no starting point — the agent can't know you came from 70/20/10, can't size the trades, and might invent a starting portfolio. For a bank, "the assistant forgot what the client said two minutes ago" is not a UX bug; it is a wrong trade.
