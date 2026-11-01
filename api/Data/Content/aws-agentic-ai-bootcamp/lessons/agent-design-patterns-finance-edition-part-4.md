# Agent design patterns — finance edition (part 4)

## Agent design patterns — finance edition (part 4)

#### 2.7 Lab 2F · Buy / Hold / Sell: three agents, one JSON baton

**The request:** "Give me a one-glance view on Apple: Buy, Hold or Sell — with the reasons and what would make you change your mind."

🧪 Simulation

##### Click each agent to see what it adds to the baton

**Agent 1 output** — Adds: raw numbers only. No opinions — that's the analyst's job.

```
{
  "ticker": "AAPL",
  "fundamentals": {
    "profitability_ratios": { "2025": { "Gross Margin": 0.4691, "Operating Margin": 0.3197,
        "Net Profit Margin": 0.2692, "Return on Assets": 0.3093, "Return on Equity": 1.7142 } },
    "valuation_ratios": { "2025": { "Price-to-Earnings": 36.418, "Price-to-Book": 55.3236,
        "Price-to-Cash-Flow": 36.5905, "Price-to-Free-Cash-Flow": 41.301,
        "EV-to-Sales": 9.9914, "EV-to-EBITDA": 28.7259 } }
  }
}
```

**Agent 2 output** — Keeps the numbers, adds ratings with evidence and a risk list.

```
{
  "ticker": "AAPL",
  "fundamentals": { ...copied from agent 1... },
  "analysis": {
    "Profitability": { "rating": "strong", "evidence": ["High and improving Gross Margins",
        "Strong Operating Margins above 30%", "Consistent Net Profit Margins around 25%"] },
    "valuation": { "rating": "expensive", "evidence": ["Rising P/E ratio from 21.25 to 41.16 in 3 years",
        "High Price-to-Book ratio indicating overvaluation", "EV-to-Sales increasing"] },
    "risks": ["Valuation risk due to high P/E and Price-to-Book ratios",
              "Margin sustainability risk",
              "Market competition impacting future growth"]   <- not from any ratio!
  }
}
```

**Agent 3 output** — Decides only from the analysis: a stance, three reasons, and three tripwires.

```
{
  "ticker": "AAPL",
  "stance": "HOLD",
  "summary": {
    "reasons": ["Strong profitability with improving Gross and Operating Margins.",
                "Consistent Net Profit Margins around 25% indicate solid earnings.",
                "While the valuations are high, the company's fundamental performance remains strong."],
    "watchlist": ["Decrease in valuation ratios such as P/E or Price-to-Book.",
                  "Sustained Net Profit Margin decline below 25%.",
                  "Market developments that could affect growth prospects."]
  }
}
```

**1 · Retrieval** calls the ratio tool; facts only

JSON

**2 · Analysis** rates profitability & valuation, lists risks

JSON

**3 · Decision** BUY / HOLD / SELL + watchlist

Each arrow is one line of code: the previous run's `.final_output` (a JSON string) becomes the next agent's input.

> **🧠 Analogy — a relay race:**
> Each runner does one leg and hands over a baton. Here the baton is a JSON string. Runner 1 must not interpret ("no interpretation" is in its instructions), runner 2 must not fetch data, runner 3 decides *only* from what it is handed. That separation is what makes the final decision auditable.

##### Step 1 — The tool (profitability + valuation only)

Same function as Lab 2A, but the liquidity list is gone: a long-term Buy/Hold/Sell call is about business quality and price, so we keep the context small and focused.

```python title="Python · lab_2f_buy_hold_sell.py · step 1"
@function_tool
def get_company_fundamentals(ticker: str) -> dict[str, pd.DataFrame]:
    """Get the profitability and valuation fundamental ratios for a given ticker."""
    companies = Toolkit([ticker], api_key=FINANCIAL_MODELING_PREP_API_KEY, start_date="2022-01-01")
    ratios = companies.ratios.collect_all_ratios()
    profitability_ratios_names = ["Return on Equity", "Return on Assets", "Gross Margin",
                                  "Operating Margin", "Net Profit Margin"]
    valuation_ratios_names = ["Price-to-Earnings", "Price-to-Book", "Price-to-Cash-Flow",
                              "Price-to-Free-Cash-Flow", "EV-to-EBITDA", "EV-to-Sales"]
    return {
        "profitability_ratios": ratios.loc[ratios.index.intersection(profitability_ratios_names)],
        "valuation_ratios":     ratios.loc[ratios.index.intersection(valuation_ratios_names)],
    }
```

##### Step 2 — Three agents, each with a JSON contract

```python title="Python · lab_2f_buy_hold_sell.py · step 2"
MODEL = "gpt-4o-mini"

fundamental_retrieval_agent = Agent(
    name="Fundamental Retrieval Agent", model=MODEL, tools=[get_company_fundamentals],
    instructions="""
You are the Fundamental Retrieval Agent.
Tasks:
1) Call the fundamentals tool for the specified ticker.
2) Output ONLY valid JSON with this schema. Keep the output strictly factual: no interpretation.
{ "ticker": "...", "fundamentals": { ... } }   // raw numbers from tools
""",
)

fundamental_analysis_agent = Agent(
    name="Fundamental Analysis Agent", model=MODEL,
    instructions="""
You are the Fundamental Analysis Agent.
Input: JSON from the Retrieval Agent.
Tasks:
1) Interpret the fundamentals along 2 dimensions:
   - Profitability (profitability, margins, ROE)
   - Valuation (P/E, EV/Sales)
2) Identify 2-3 key risks (e.g., valuation risk, margin sustainability).
3) Output ONLY valid JSON with this schema:
{
  "ticker": "...",
  "fundamentals": { ... },          // keep from input
  "analysis": {
    "Profitability": { "rating": "strong|neutral|weak", "evidence": [string, ...] },
    "valuation": { "rating": "cheap|fair|expensive", "evidence": [string, ...] },
    "risks": [string, ...]
  }
}
Rules:
- Keep evidence short and specific.
""",
)

decision_agent = Agent(
    name="Decision Agent", model=MODEL,
    instructions="""
You are the Decision Agent.
Input: JSON from the Fundamental Analysis Agent.
Tasks: Based only on the input coming from the Fundamental Analysis Agent:
1) Produce a simple stance: BUY, HOLD, or SELL.
2) Provide 3 bullet reasons grounded in the analysis.
3) Provide a "watchlist" section: what metrics would change your stance.
Output ONLY valid JSON:
{ "ticker": "...", "stance": "BUY|HOLD|SELL",
  "summary": { "reasons": [string, string, string], "watchlist": [string, string, string] } }
""",
)
```

1. Each agent's instructions end with the **exact JSON shape** it must hand on — the contract between relay runners.
2. `"rating": "strong|neutral|weak"` means "pick one of these words". Fixed vocabularies keep the next agent's job simple.
3. The analysis agent copies `fundamentals` forward ("keep from input"), so the decision agent can still see the raw numbers.

##### Step 3 — The whole orchestration is three lines

```python title="Python · lab_2f_buy_hold_sell.py · step 3"
fundamental_results  = await Runner.run(fundamental_retrieval_agent, "Provide Apple fundamentals")
fundamental_analysis = await Runner.run(fundamental_analysis_agent, fundamental_results.final_output)
final_decision       = await Runner.run(decision_agent, fundamental_analysis.final_output)
print(final_decision.final_output)
```

Read it as a relay: the `.final_output` (a JSON string) of one run becomes the `input` of the next. No framework magic.

💰 Reading the verdict: HOLD

**Profitability: strong** (margins above 30%, net margin ~25–27%). **Valuation: expensive** — the analysis noted P/E climbing from about 21 to about 41 over three years, meaning the share price rose much faster than profits. Great business, pricey stock → **HOLD**: don't sell a winner, don't overpay to buy more.

The **watchlist** is the most useful part for a PM: tripwires that would flip the call — "P/E or price-to-book falls", "net profit margin drops below 25%". It turns a one-off opinion into a monitoring rule.

> **⚠️ Spot the leak:**
> One listed risk was "market competition impacting future growth". No ratio says that — the LLM added it from its own general knowledge. In a regulated memo every claim should trace to evidence. Fix: add "every risk must cite a ratio from the input" to the analysis instructions, or ground it with retrieved industry reports.

```python title="Python · a task guardrail on the final baton (optional add-on)"
import json

decision = json.loads(final_decision.final_output)            # crashes here = the agent broke the JSON contract
assert decision["stance"] in {"BUY", "HOLD", "SELL"}, "Unexpected stance!"
assert len(decision["summary"]["watchlist"]) == 3, "Watchlist must have 3 items"
```

If a model ever wraps its JSON in a ``` code fence, `json.loads` fails. The robust fix is the one from Lab 2E: give the agent an `output_type` (a dataclass or Pydantic model) instead of describing JSON in words.

Disclaimer

Everything in this lab is for learning. It is not investment advice or a recommendation to buy or sell any security.

#### 2.8 Context and memory upkeep — the finance notes

You know context engineering. In a rebalancing step, a good context holds: the **current allocation**, **recent volatility** from the bank's database, **relevant past decisions** from long-term memory, and the **description of a pricing tool** — not ten years of trade history. Two framework behaviours worth knowing:

- **LlamaIndex** can flush short-term memory into long-term memory when chat history crosses a token threshold (e.g. 40K tokens), into three blocks: *static* (fixed facts like the client's mandate), *fact extraction* (facts pulled out of the chat) and *vector* (similarity search over past turns).
- **CrewAI** detects when the context overflows and either summarises it or stops with an error, depending on settings.

For long-term memory, two upkeep ideas: **hierarchical summaries** (detailed chats → daily summaries → an overall summary → a short client profile) and **forgetting**, where unused memories fade and recalled ones get stronger — modelled on the human forgetting curve.

🧪 Simulation

##### Memory strength over time — press "Recall" to reinforce a memory

Today is day 30

30

{{diagram:1}}

- Client: no Energy exposure
- High-volatility playbook: not created yet (day 3)
- One-off gold-ETF question: not created yet (day 9)

fade line → archive or forget

Each recall resets the memory to 100% and doubles how slowly it fades next time. Frequently used client preferences stay; one-off trivia fades out of retrieval.

Move the day slider past this memory's last recall (day `last recall`) first.

💰 Compliance note on client profiles

Memory frameworks can build a "user portrait" automatically. In finance, keep it **explicit and correctable** — "max 35% per sector, set by the client on 12 Oct" — never an inferred guess about the client's mood or personality. Suitability rules require you to show where every client preference came from, and let the client change it.

---

Wrap-up

## What to remember

1. **Pick models by data sensitivity first, reasoning depth second.** Confidential data pushes you to self-hosted open models; deep analysis pushes you to reasoning models.
2. **Valid JSON isn't usable JSON.** Name every key, type and unit — or use structured outputs.
3. **Tools make numbers trustworthy; interpretation is still the LLM's.** Know your ratios well enough to challenge it (ROE 171%, current ratio 0.89).
4. **Working memory = the session notepad.** Pass the same `session` every turn or the agent forgets the portfolio.
5. **Episodic memory = journal → cabinet → retrieve → paste into the prompt.** Follow the variables: `conversation_history` → string → prompt → `episodic_memory` → Chroma → `['documents'][0][0]`.
6. **Checks need limits and contracts.** A judge with a fixed form (`output_type`), a retry limit, and JSON contracts between agents make a system auditable.

#### Quiz Check yourself

Answer all six to see your score.

**1.** Apple's return on equity is 171%. What's the most likely reason?

- Apple is a very risky company
- Buybacks have made shareholders' equity small, so profit ÷ equity is huge
- The data API made an error
- Revenue doubled last year

> **Correct answer:** Buybacks have made shareholders' equity small, so profit ÷ equity is huge
> ROE = net income ÷ equity. Shrink the denominator and the ratio balloons — no change in the business needed.

**2.** Turn 2 of the rebalancing chat is run WITHOUT the session. What goes wrong?

- The agent doesn't know the 70/20/10 starting point, so it can't size the trades
- Nothing — the agent still remembers
- The API call fails with an error
- The answer is slower

> **Correct answer:** The agent doesn't know the 70/20/10 starting point, so it can't size the trades
> Each run only sees what you send. The session is what re-sends the earlier turns.

**3.** In episodic_memory_recap['documents'][0][0], what does the FIRST [0] pick?

- The best match
- The first memory ever stored
- The first word of the document
- The first question you passed in query_texts

> **Correct answer:** The first question you passed in query_texts
> Outer list = one entry per question. The second [0] then picks the best match for that question.

**4.** Why does the prompt template write {{ and }} around the JSON example?

- It's a typo
- JSON needs double braces
- So .format() leaves a literal { } instead of treating it as a slot
- To make the LLM think harder

> **Correct answer:** So .format() leaves a literal { } instead of treating it as a slot
> .format() fills every {name}. Doubling the braces escapes them; after formatting they become single braces.

**5.** With max_iteration = 4 and the check nbr_iterations > max_iteration, how many times can the news searcher run?

- 3
- 4
- 5
- Forever

> **Correct answer:** 5
> The first try plus 4 retries. The 5th failure makes the counter 5, and 5 > 4 stops the loop.

**6.** You must tag 50,000 public headlines with sentiment every hour. Best fit?

- A fast non-reasoning model or a FinBERT-style classifier
- A hosted reasoning model at high effort
- Fine-tune a 70B model first
- A multi-agent pipeline

> **Correct answer:** A fast non-reasoning model or a FinBERT-style classifier
> Public data, simple task, huge volume → fast and cheap. Save reasoning models for deep, multi-step analysis.

Score: **n / 6** — ready for Section 3.

Score: **n / 6** — revisit the sections you missed.

**Future with Shivank** · AI Agents in Finance · Sections 1 & 2 For learning only — nothing here is investment advice. Sample outputs vary run to run; prices, ratios and news are live.
