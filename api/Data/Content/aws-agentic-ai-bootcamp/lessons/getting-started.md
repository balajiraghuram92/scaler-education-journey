# Getting started

## Getting started

You write the code yourself. Build it bottom-up, the same way as Section 4: **data → tools → agents → orchestrator → main**. The survey file is given to you.

#### P5 Setup, folders & data

```bash title="Bash · one-time setup (macOS / Linux; Windows notes in the comments)"
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                   # Windows: copy .env.example .env  → then paste your OPENAI_API_KEY
```

```text title="Text · requirements.txt"
# NPS analyst in a box — install with:  pip install -r requirements.txt   (Python 3.11–3.13)
openai-agents>=0.4        # the OpenAI Agents SDK (Agent, Runner, function_tool, .as_tool) — brings openai + pydantic
pandas>=2.2               # every number: NPS, segments, revenue at risk
python-dotenv>=1.0        # reads OPENAI_API_KEY from .env
```

```text title="Text · .env.example"
# Copy this file to .env (same folder) and paste your key. Never commit .env.
OPENAI_API_KEY=sk-...

# Optional
# NPS_MODEL=gpt-4o                        # any model your key can use, e.g. gpt-4.1 or gpt-5-mini
# NPS_SURVEY_PATH=data/nps_survey.csv     # or point at your own survey CSV
```

nps-analyst-project/ ├── data/ │ └── nps_survey.csv # GIVEN: the 600 survey answers ├── nps_by_hand.py # Step 0: NPS in plain pandas, no LLM ├── try_tools.py # Step 1: every tool's numbers, no LLM ├── nps_insights_agent/ │ ├── config.py # NPS rules, house rules, assumptions, model name │ ├── tools/ # the HANDS — plain Python │ │ ├── survey_tools.py # overview, segments, revenue at risk, mismatches, callbacks │ │ ├── theme_tools.py # comments → themes (keyword rules) │ │ └── whatif_tools.py # "if we fix X": NPS points + rupees saved │ ├── agents/ # the BRAINS — 5 specialists + orchestrator │ ├── fact_check.py # the auditor │ └── main.py # command line: --trace --verbose --stream --log-dir --survey └── stretch/llm_theme_tagger.py # stretch goal: LLM tagging vs keyword rules

This is the suggested layout. Every file except `data/nps_survey.csv` is yours to write.

##### The data: data/nps_survey.csv

600 survey answers from July to September 2026 (200 a month); 536 of them have a written comment. One row is one customer's answer. The bank, the customers and their answers are fictional.

**Download it:** [nps_survey.csv](https://d2beiqkhq929f0.cloudfront.net/public_assets/assets/000/248/987/original/nps_survey.csv?1792931898) (64 KB). If it opens as text in your browser, right-click the link, choose "Save link as…" and save it as `data/nps_survey.csv`. Or run this from your project folder:

```bash title="Bash · download the survey into data/"
mkdir -p data
curl -L -o data/nps_survey.csv "https://d2beiqkhq929f0.cloudfront.net/public_assets/assets/000/248/987/original/nps_survey.csv?1792931898"
# Windows PowerShell: mkdir data; curl.exe -L -o data/nps_survey.csv "https://d2beiqkhq929f0.cloudfront.net/public_assets/assets/000/248/987/original/nps_survey.csv?1792931898"
```

| Column | What it holds | Example |
| --- | --- | --- |
| `response_id` | A unique id for the answer | R0001 |
| `date` | The day the customer answered | 2026-07-01 |
| `month` | The month of that day | 2026-07 |
| `product` | Savings Account, Credit Card or Wealth | Savings Account |
| `tenure` | How long they have banked with us: <1 yr, 1-3 yrs or 3+ yrs | 3+ yrs |
| `channel` | How they mostly bank: Mobile App, Branch or Call Centre | Branch |
| `score` | Answer to "How likely are you to recommend us?", 0 to 10 | 10 |
| `comment` | Answer to "Why did you give this score?" (can be blank) | Opening the account was smooth and fully online. |
| `annual_revenue_inr` | Yearly revenue the bank earns from this customer, in rupees | 12200 |

---

Own it

## Your project

#### P6 Milestones, stretch goals and rubric

| Milestone | Build | Done when… | Time |
| --- | --- | --- | --- |
| **M0 · Data** | venv, `nps_by_hand.py` | prints Overall NPS 18.5 and the three months | 30 min |
| **M1 · Hands** | config + the three tool files | `try_tools.py` prints every tool's result, and the numbers agree with `nps_by_hand.py` | 2 h |
| **M2 · One brain** | ScoreAnalystAgent alone with `Runner.run` | its scorecard copies every number exactly, with signs | 1 h |
| **M3 · The team** | the other four agents + orchestrator + `main.py` | `--trace` shows three CALLs before any OUTPUT | 2 h |
| **M4 · Trust** | `fact_check.py` | 3 runs: wording differs, fact check passes every time | 1 h |
| **M5 · Present** | the brief + one slide | you can defend which fix goes first, with both rankings | 1 h |

##### Stretch goals (pick two)

1. **LLM theme tagger** — tag each comment with an LLM that must pick from a fixed list of themes (a `Literal[...]` type), cache the tags to CSV, and compare the top themes with your keyword rules.
2. **A guardrail that blocks bad briefs** — if `fact_check` fails, send the brief back to the writer with the failed checks, at most twice.
3. **A label-aware fact check** — check each number next to its label (for example, the line that mentions 2026-08), not just anywhere in the brief.
4. **Close-the-loop drafts** — a new agent drafts a callback note per detractor; a human approves every note before anything is sent.
5. **Your own data** — any CSV with the same columns runs with `--survey`. Different segments? Edit `SEGMENT_COLUMNS`.
6. **A month-on-month view** — re-run on each month's slice and have the writer compare this brief with last month's.

##### Rubric (100 points)

| Criterion | What earns full marks | Points |
| --- | --- | --- |
| Correct numbers | fact check passes; signs and units right; no number the tools didn't produce | 25 |
| Finds the three hidden stories | what caused the drop · where the money at risk sits · a data-quality problem in the scores | 25 |
| Agent design | numbered steps, fixed sections and labels, grounding rules, exact keys in hand-offs | 20 |
| Parallel phase verified | `--trace` output included in the submission | 10 |
| Honest caveats | low samples, assumptions, alternative NPS numbers — all stated | 10 |
| Code quality | commented, plain functions testable without an LLM, no crashes on bad input | 10 |

---

Wrap-up

## What to remember

1. **NPS = % promoters − % detractors**, on all answers. 9–10 / 7–8 / 0–6. A score from −100 to +100, not a percentage.
2. **Small groups wobble.** Show the margin of error; never crown a 26-answer segment.
3. **Loud ≠ expensive.** Rank fixes by NPS points *and* by rupees at risk, and show the trade-off.
4. **Code computes, agents reason.** Every number, verdict and alert comes from Python or a table.
5. **Same skeleton as Section 4:** parallel analysis → dependent planning → synthesis, with a hand-off form between phases.
6. **Check the output with code.** A fact check after every run turns a demo into something you can send to a CEO.

Disclaimer

Future with Shivank Bank and its survey are fictional, generated for learning. The churn rates are illustrative assumptions.

**Future with Shivank** · AI Agents in Finance · Project: NPS analyst in a box Fictional bank, generated data, for learning only. Agent wording varies run to run; the numbers come from code.
