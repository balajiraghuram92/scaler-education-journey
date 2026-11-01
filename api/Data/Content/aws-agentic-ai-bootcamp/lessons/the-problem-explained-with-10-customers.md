# The problem, explained with 10 customers

Future with Shivank *· AI Agents in Finance · Project: NPS analyst*

> **Lesson resources · Scaler AWS AI Bootcamp · Week 1 · Project 2 of 2:**
> - [Watch Week 1 · session 1](https://www.scaler.com/meetings/i/ai-bootcamp-1/archive)
> - [Watch Week 1 · session 2](https://www.scaler.com/meetings/i/ai-bootcamp-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Future with Shivank · Hands-on project · Learner brief

#### NPS Analyst in a Box Promoters, passives, detractors — and a team of agents that turns 600 survey answers into a leadership brief

You built an "analyst in a box" for stocks. Now point the same design at the bank's own customers. Five specialist agents and a director read a Net Promoter Score survey, find **why** the score moved, put a **rupee value** on unhappy customers, decide **what to fix first**, and say **who to call back this week**. Every number is computed by plain Python; the agents only read, decide and explain.

🏦 **Future with Shivank Bank, Monday morning.** The Head of Customer Experience walks in: *"Our quarterly NPS dropped. The CEO asks on Thursday: how bad is it, why did it happen, how much money is at risk, and what are we doing about it? Last quarter two analysts spent three days reading comments in Excel. Can your agents do the first draft before lunch?"*

**600** survey answers, July–September 2026

**5 + 1** specialist agents plus a director

**3** hidden stories your agents must find

**~$0.20** per full run on gpt-4o

How to read the coloured boxes:

🧠 Analogy💰 Finance corner⚠️ Watch out⏭️ Already covered💡 Tip🧪 Simulation

⏭️ Same skeleton as Section 4

Tools return JSON and never crash · agents are `Agent(name, instructions, tools, model)` · the orchestrator calls specialists with `.as_tool()` · three phases (parallel → dependent → synthesis) · verdicts come from tables, not moods. If any of that feels new, re-read Section 4.2–4.6 first. This page spends its time on what is **new**: NPS, money at risk, text themes, what-if analysis and fact-checking the final brief.

---

Start here · the problem statement

## The problem, explained with 10 customers

##### The situation

Future with Shivank Bank asks every customer one question: *"On a scale of 0 to 10, how likely are you to recommend our bank to a friend?"* — and then *"Why did you give this score?"*

- 9–10 · Promoter happy, will recommend the bank
- 7–8 · Passive (neutral) okay, but would switch easily
- 0–6 · Detractor unhappy, likely to leave and complain

NPS = % promoters − % detractors # passives count in the total, but add nothing

##### A tiny example: 10 customers in September

| # | Score | Group | Comment | Product | Yearly revenue to bank |
| --- | --- | --- | --- | --- | --- |
| 1 | 10 | Promoter | "UPI is super quick" | Savings | ₹5,000 |
| 2 | 9 | Promoter | "My RM is very helpful" | Wealth | ₹2,00,000 |
| 3 | 9 | Promoter | "App is easy" | Savings | ₹4,000 |
| 4 | 8 | Passive | "Fine, but call centre wait is long" | Card | ₹10,000 |
| 5 | 7 | Passive | "Okay" | Savings | ₹3,000 |
| 6 | 4 | Detractor | "OTP not coming after the update" | Savings | ₹6,000 |
| 7 | 3 | Detractor | "Can't login since the update" | Card | ₹12,000 |
| 8 | 5 | Detractor | "OTP fails, moving my salary account" | Savings | ₹8,000 |
| 9 | 2 | Detractor | "New advisory fee, nobody explained it" | Wealth | **₹3,00,000** |
| 10 | 0 | Detractor | "Excellent service, love it!" | Savings | ₹7,000 |

🧪 Try it

**Default score, customer #10 as reported:** 3 promoters (30%) − 5 detractors (50%), with 2 passives in the total → NPS = **−20**

**Button “What if customer #10 meant 10, not 0?”:** 4 promoters (40%) − 4 detractors (40%), with 2 passives in the total → NPS = **0** — one misread answer moved the NPS by 20 points.

What if customer #10 meant 10, not 0?

**Getting that number takes one line of code.** The hard part is the four questions the CEO will ask next:

1. **How bad is it?** NPS fell from +30 last month to −20 in one month.
2. **Why?** Read the comments: three of the five detractors (#6, #7, #8) complain about OTP or login after the app update. That's the cause.
3. **How much money is at risk?** The three OTP customers bring ₹26,000 a year in total. The one fee complaint (#9) brings ₹3,00,000. *The loudest problem (OTP) is not the most expensive one (fees).*
4. **What do we do?** Fix OTP first — it moves the score the most. Phone customer #9 today — that one account is worth more than the other nine put together.

> **⚠️ The trap:**
> Customer #10 gave a 0 but wrote "Excellent service". They probably thought 0 meant best. If they meant 10, the NPS is **0, not −20**. A good analyst flags this — and doesn't silently change the score.

With 10 customers, you can do all of this in your head.

##### The real problem

The bank actually has **600 customers, 536 written comments and 3 months of data**. Last quarter, two analysts spent three days in Excel reading every comment, colour-coding topics, slicing scores by month, product and channel, working out the money at risk, and writing one page for the CEO. That's the job we hand to agents — one question per agent:

| Question | Agent | What it does in the 10-customer example |
| --- | --- | --- |
| **How bad is it?** | ScoreAnalystAgent | Calculates −20 and spots that September dropped |
| **Why?** | VoiceOfCustomerAgent | Reads comments, finds "OTP/login after update" in 3 of 5 detractors |
| **How much money?** | ChurnRiskAgent | Finds ₹3 lakh sits with one Wealth customer; flags #10 as a likely mistake |
| **What do we do?** | ActionPlannerAgent | Fix OTP first; call #9 today |
| **One page for the CEO** | ReportWriterAgent | Writes the brief with a RED / AMBER / GREEN alert |

Python does all the counting and maths, so the numbers are always exact. The agents do what Excel can't: read comments, decide where to look next, connect complaints to money, and write it up.

📋 **Problem statement for learners.** Future with Shivank Bank's NPS fell from +32 in July to −6.5 in September. Given 600 survey answers (score, comment, product, channel, revenue), build a team of AI agents that tells leadership: **how bad** the drop is, **why** it happened in customers' own words, **how much revenue** is at risk, and **what to fix first and who to call back** this week — on one page, with every number checked by code. The data: [nps_survey.csv](https://d2beiqkhq929f0.cloudfront.net/public_assets/assets/000/248/987/original/nps_survey.csv?1792931898) (600 answers).

---

Understand it

## What we are building, and why a bank cares

#### P1 The ask: four questions for Thursday

| The CEO's question | Who answers it | What they hand back |
| --- | --- | --- |
| **How bad is it?** | ScoreAnalystAgent | NPS with margin of error, monthly trend, best/worst segments, health verdict |
| **Why did it happen?** | VoiceOfCustomerAgent | Top themes in the comments, real quotes, root-cause hypotheses |
| **How much money is at risk?** | ChurnRiskAgent | Revenue at risk in ₹ lakh, risk verdict, data-quality warnings |
| **What are we doing about it?** | ActionPlannerAgent | Fix list ranked two ways (NPS points, rupees saved), who to call back this week |
| **One page, please.** | ReportWriterAgent | The NPS brief with a GREEN / AMBER / RED alert level |

> **Note:**
> 💡 Why agents, and not just a pandas script?
>
> If all you need is the number, pandas is enough — milestone M0 below is exactly that, about 20 lines. Agents earn their keep in the parts a script can't do alone: **reading** 500 comments, **choosing** where to drill down next ("September looks bad — which channel?"), **connecting** a complaint to a rupee figure, and **writing** it for a CEO. The design rule from Section 4 still holds: *code computes, agents reason.*

#### P2 Just-enough NPS (three ideas, nothing more)

Every NPS survey asks one question: *"How likely are you to recommend Future with Shivank Bank to a friend or colleague?"* on a 0–10 scale, usually followed by *"What is the main reason for your score?"*

##### Idea 1 · Three buckets

0 det

1 det

2 det

3 det

4 det

5 det

6 det

7 passive

8 passive

9 promoter

10 promoter

> **🧠 The new biryani place:**
> **Promoters (9–10)** post "must try!" in the family WhatsApp group. **Passives (7–8)** — also called *neutrals* — eat, pay and forget; they'd switch the moment a new place opens. **Detractors (0–6)** leave a one-star review and tell ten people. Notice how harsh the scale is: a 6 sounds fine, but a 6 is a detractor.

##### Idea 2 · One subtraction

NPS = % promoters − % detractors our survey: 268 promoters, 175 passives, 157 detractors (600 answers) 44.7% − 26.2% = +18.5

NPS runs from **−100** (everyone is a detractor) to **+100** (everyone is a promoter). It is a **score, not a percentage** — write "+18.5", never "18.5%". Passives add nothing to the top line, but they **are** in the total you divide by. Play with that below.

🧪 Simulation

##### Build an NPS — start from our survey

**Promoters (9–10)** 268 268

**Passives (7–8)** 175 175

**Detractors (0–6)** 157 157

**Button “+50 passives”:** Nobody new is unhappy, yet the NPS **fell**: passives add nothing to the top line but they grow the total you divide by.

**Button “10 detractors → passives”:** Each detractor who becomes a passive adds 100 ÷ (answers) points. 10 × 100 ÷ 600 ≈ **+1.7**. This is exactly the maths inside `estimate_fix_impact`.

**Button “10 detractors → promoters”:** Twice the gain (≈ **+3.3**): the customer stops counting against you *and* starts counting for you. Our what-if tool assumes the cautious version — detractors become passives, not promoters.

**Button “Reset to our survey”:** Our survey: 268 / 175 / 157 → +18.5, the number every tool and agent must agree on.

##### Idea 3 · Small groups wobble

The same NPS from 26 answers and from 600 answers are not equally trustworthy. Our tools attach a **95% margin of error** to every NPS: count each answer as +1, 0 or −1, and NPS is just their average × 100. With few answers that average wobbles. For example, a segment that scores +15 from only 26 answers has a margin of error of about **±31** points: its real score could be anything from −16 to +46.

> **🧠 Two innings:**
> Calling a 26-answer segment "our worst" is like dropping a batsman after two innings. The tools mark any segment with fewer than 30 answers `low_sample`, and the agents are told never to call it best or worst.

#### P3 NPS is a money number

The CX team is judged on NPS. The CFO is judged on revenue. Our project connects the two with one line of finance — **expected loss**, the same idea an insurance actuary uses:

revenue at risk = Σ (customer's yearly revenue × chance they leave this year) chance of leaving (an ASSUMPTION, set in config.py): promoter 3% · passive 10% · detractor 25%

💰 The finance corner: loud ≠ expensive

The group with the **most unhappy customers** is not always the group with the **most money at risk**, because yearly revenue per customer differs a lot between products. A dashboard that only counts complaints can send the bank to fix the wrong thing first. That is why the brief must show two rankings: *most complaints* and *most money*.

**1 lakh = ₹1,00,000. 100 lakh = 1 crore.** The tools report money in lakh so the LLM never has to count zeros.

> **⚠️ Assumptions, written down:**
> The 3% / 10% / 25% churn rates are a house assumption, not a fact. Real teams estimate them from history ("of last year's detractors, how many closed their account?"). The project puts them in `config.py`, echoes them in every revenue tool result, and the brief must list them under DATA CAVEATS. An assumption you can see is an assumption someone can challenge.

#### P4 The architecture: a CX insights team in code

| Agent | Human it replaces (the mechanical part only) | Its tools |
| --- | --- | --- |
| **ScoreAnalystAgent** | Analyst building the monthly NPS pivot tables | `get_nps_overview` `get_nps_by_segment` * |
| **VoiceOfCustomerAgent** | Analyst reading 500 comments and colour-coding cells | `get_comment_themes` |
| **ChurnRiskAgent** | Finance partner + data-quality reviewer — the sceptic | `get_revenue_at_risk` `find_score_comment_mismatches` `get_nps_by_segment` * |
| **ActionPlannerAgent** | CX lead turning findings into a fix list | `estimate_fix_impact` `get_callback_list` |
| **ReportWriterAgent** | Head of CX writing to leadership | none — pure synthesis |
| **OrchestratorAgent** | Director of CX assigning the work | the five agents above, each wrapped with `.as_tool()` |

{{diagram:1}}

*Three phases, same as Section 4. ① The three analysis agents don't need each other, so they run together. ② The planner needs the top themes, so it waits. ③ The writer needs everything. Then code — not an LLM — checks the brief.*

> **🧠 Hands, brains, manager — and an auditor:**
> **Tools are the hands** (pandas does the counting). **Agents are the brains** (they decide what to look at and explain it). **The orchestrator is the manager** (assigns, collects, never does the work itself). New in this project: **an auditor at the door**. Like the cashier who recounts the cash drawer at closing instead of trusting the sales log, `fact_check.py` re-computes the headline numbers and checks the brief quotes them correctly.

---

Build it
