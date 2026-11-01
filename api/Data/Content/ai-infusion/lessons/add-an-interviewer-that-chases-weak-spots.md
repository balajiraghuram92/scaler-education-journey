# Add an interviewer that chases weak spots

## Add an interviewer that chases weak spots

The evaluator judges answers. A second agent decides *what to ask next*. If the candidate fumbles a technical question, the interviewer stays in technical and asks another one to probe depth. It only moves on once the candidate answers well, or the category runs out of questions.

{{diagram:1}}

*Two agents, one shared memory. The interviewer never grades and the evaluator never chooses questions. Each has one job, and the session log is the only thing they pass between them.*

```pseudo title="interviewer_agent.py"
SET CATEGORIES = sorted, unique categories from QUESTIONS   // behavioural, technical
SET PASS_MARK = 60
SET INTERVIEWER_PROMPT = the rules for picking a category, ending in a one-word reply

DEFINE remaining(category, asked):
    RETURN the questions in that category that are not in asked

DEFINE choose_next_question(asked):
    IF every question has been asked THEN RETURN None
    SET history = category and relevance score of each session_log entry
    ASK the model for a category, with INTERVIEWER_PROMPT and history
    SET category = the reply, trimmed and in lower case
    IF the reply is not a known category or has no questions left THEN
        SET category = the first category that still has questions
    RETURN the first remaining question in that category
```

> **Imported:**
> - `json` Python standard library: turns the session history into JSON text for the model.
> - `agent` your own `agent.py`: shares the Groq client, `MODEL` and `session_log`.
> - `QUESTIONS` from `interview_bank`, your own file: used to list the categories and find unasked questions.

**interviewer_agent.py** · bonus · the second agent

```python reveal title="interviewer_agent.py · bonus · the second agent"
import json

import agent
from interview_bank import QUESTIONS

CATEGORIES = sorted({q["category"] for q in QUESTIONS})
PASS_MARK = 60

INTERVIEWER_PROMPT = f"""You are the interviewer. Choose the category of the NEXT question.
Rules:
- If the last answer scored below {PASS_MARK} and that category still has unasked
  questions, stay in the same category to probe depth.
- Otherwise move to a category the candidate has seen least.
Reply with exactly one word from: {", ".join(CATEGORIES)}"""

def remaining(category: str, asked: set) -> list:
    return [q for q in QUESTIONS if q["category"] == category and q["question"] not in asked]

def choose_next_question(asked: set) -> dict | None:
    if len(asked) == len(QUESTIONS):
        return None
    history = [{"category": e["category"],
                "score": e["results"].get("score_relevance", {}).get("score")}
               for e in agent.session_log]
    reply = agent.client.chat.completions.create(
        model=agent.MODEL,
        messages=[{"role": "system", "content": INTERVIEWER_PROMPT},
                  {"role": "user", "content": json.dumps(history)}],
    ).choices[0].message.content.strip().lower()
    # Never trust the hand-off blindly: validate, then fall back to any open category.
    category = reply if reply in CATEGORIES and remaining(reply, asked) else None
    if category is None:
        category = next(c for c in CATEGORIES if remaining(c, asked))
    return remaining(category, asked)[0]
```

```pseudo title="run_multi_agent.py"
SET asked = empty set
SET item = choose_next_question(asked)
WHILE item is not None:
    PRINT the item's category and question
    ASK the candidate for an answer
    PRINT the feedback from agent.run_turn(item, answer)   // the evaluator judges
    ADD the question to asked
    SET item = choose_next_question(asked)
PRINT agent.ask_final_report()
```

> **Imported:**
> - `agent` your own `agent.py`: the evaluator. Runs each answer and builds the final report.
> - `choose_next_question` from `interviewer_agent`, your own file: the interviewer agent that picks each next question.

**run_multi_agent.py** · bonus · python run_multi_agent.py

```python reveal title="run_multi_agent.py · bonus · python run_multi_agent.py"
import agent
from interviewer_agent import choose_next_question

asked = set()
while (item := choose_next_question(asked)) is not None:     # interviewer agent picks
    print(f"\n[{item['category']}] {item['question']}")
    answer = input("Your answer: ")
    print("Coach:", agent.run_turn(item, answer))              # evaluator agent judges
    asked.add(item["question"])

print("\n" + agent.ask_final_report())
```

Production reality

**Validate every hand-off between agents.** The interviewer is asked for one word from a fixed list. Sometimes it will answer “Technical.” or “I'd suggest behavioural”, or name a category that has run out of questions. The code checks the reply against the allowed set and falls back deterministically. An agent's output is untrusted input to the next agent.

Judgement calls

## Six decisions people get wrong

| Decision | Tempting answer | What it should be |
| --- | --- | --- |
| **Who judges fillers & STAR** | Ask the LLM. It understands language better than a list. | A tool. The company's definition has to win, every time, auditably. The LLM's job is choosing tools and explaining results. |
| **Where to start building** | The UI, because it's what the client sees. | The tools, standalone. The UI is the last layer. Bugs found bottom-up cost seconds; bugs found top-down cost tokens and hours. |
| **What goes in memory** | The conversation transcript as one long string. | One dict per answer with the raw tool outputs. You can't average a paragraph. |
| **Counting fillers** | `text.count("um")` | Word-boundary regex. Substrings punish “summary”, “document”, “likely”. |
| **Relevance scoring** | Exact keyword match. | Stem substrings (`communicat`), and accept that it's a floor, not a ceiling. A brilliant answer in different words still scores low. That's the first thing to upgrade (embeddings). |
| **Vibe-coding** | One prompt: “build the whole project”. | One ask per prompt, and read the diff. You'll be reviewing AI-written code for the rest of your career, so start now. |

#### Where it goes next

- **Semantic relevance.** Embed the answer and a reference answer and use cosine similarity, so a strong answer in different words isn't scored zero. Keep keyword coverage alongside it as an explainable second signal.
- **Generated questions, bounded categories.** Let the model write questions, but only from categories and seniority levels the hiring team defines, and store the expected keywords it was graded against.
- **Per-user sessions.** `gr.State` or a `sessions` table keyed by id. Same entry schema.
- **Voice.** Speech-to-text in front of the same pipeline. The evaluator doesn't change; fillers just get more frequent.
- **LangChain or another framework.** Allowed and sensible. The session used plain Python so every moving part stayed visible.

Self-check

## Eight questions before you build it yourself

#### Why are the three evaluators tools instead of instructions in the system prompt?

Instructions are interpreted differently run to run. Tools are code: the same answer always gets the same count, and the definition can be reviewed and changed deliberately. That keeps the AI and the hiring team in the same ballpark.

#### What would break if you appended the tool results to `messages` before the assistant message that requested them?

The provider would reject the request. Each `role: "tool"` message has to answer a `tool_call_id` that appears in a preceding assistant message's `tool_calls`.

#### Why does `generate_final_report` need `"properties": {}`?

The schema is the model's only knowledge of the function. An explicit empty object tells it the function takes no arguments and can be called directly.

#### What does `MAX_TOOL_ROUNDS` protect against?

A model that keeps requesting tools without ever producing a final answer. That's an infinite loop of paid API calls. The cap bounds cost and latency.

#### Why store tool outputs in `session_log` rather than the feedback text?

The report needs numbers to average and compare. The model's prose may paraphrase or round. Store both, but aggregate only the measured values.

#### Two candidates use the deployed Gradio app at once. What goes wrong?

They share the module-level `session_log` and the scorecards mix. Use `gr.State` or a database keyed by session id.

#### In `memory_check.py`, which check could fail even when the code is correct?

The third one. It inspects the model's free-text reply for words like “disagree”. The first two check deterministic code and should never flake.

#### In the bonus, why validate the interviewer's one-word reply?

An agent's output is untrusted input to the next stage. It may add punctuation, change case, or pick an exhausted category. Check it against the allowed set and fall back deterministically.

AI Infusion · Class 7 — live project session. The problem was an AI-engineer take-home a company shared, solved live with Scaler's AI/ML team: Virat leading, Shijan presenting the brief and the solution walkthrough, Pulkit running the debugging room. The code on this page is a cleaned, runnable reconstruction of the walkthrough (checked against a stubbed model), not the official solution zip. Use that from the post-reads to compare.
