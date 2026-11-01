# Run the three tools in your browser

## Run the three tools in your browser

This is a line-for-line JavaScript port of `tools.py` and `generate_final_report()`. Everything the LLM would *base* its feedback on is computed here exactly as in Python. The only thing missing is the model's paragraph of prose. Answer a few questions, then build the report.

**INTERVIEWIQ** · tools only, no LLM session: 0 answers

Question

Candidate answer

Type an answer, or load one of the samples…

**Q1 · weak sample:** Um, I basically just, like, kept trying stuff until it worked, you know.

**Q2 · strong sample:** At my previous company a teammate wanted to rewrite our payments service. I was responsible for its uptime, so I listened to his reasons first, then I proposed we look at the incident data together. We agreed on a compromise and communicated it to the team. As a result the outcome was a 30% drop in incidents.

**Q3 · strong sample:** While working on our orders API we had a query regress to 4 seconds. My task was to fix it before the sale. I ran EXPLAIN ANALYZE, read the query plan, saw a sequential scan, added a composite index and removed an N+1 in the ORM. I added a cache for the hot path. As a result p95 went back to 40 ms.

**Q3 · weak sample:** I would actually just add more servers and literally restart the database, I mean that usually works.

**Q4 · strong sample:** At my last job we had a scraping problem. I had to protect the API. I implemented a token bucket per user stored in Redis, with a sliding window fallback, and returned 429 with Retry-After. This led to a 90% drop in abusive traffic.

**Q4 · weak sample:** Uh, you know, some kind of limit, sort of like blocking people who call too much.

**Q5 · strong sample:** When I was leading a migration, a dependency slipped two weeks. My job was to land it for quarter end. I decided to cut scope, prioritised the three critical tables, and communicated the plan to every stakeholder. We delivered on time and finished the rest the next sprint.

**Q5 · weak sample:** Basically we were, like, late, and um, it was kind of stressful but it got done.

> **Note:**
> Try this: type “I summarised the document and it was likely fine.” A naive `.count()` would find two fillers in that sentence (“um” inside *summarised* and *document*) plus a “like” inside *likely*. The word-boundary version finds zero.

Ask 1 · the agent

## The loop that decides when it's done

The question bank comes first, because `score_relevance` needs the expected keywords for each question:

**interview_bank.py** · questions are hard-coded on purpose

```pseudo title="interview_bank.py"
SET QUESTIONS = a fixed list of five questions, in this order
    each question has a category, the question text and expected_keywords
    // the keywords are what score_relevance looks for in the answer
```

```python reveal title="interview_bank.py · questions are hard-coded on purpose"
# The company's question bank. Hard-coded on purpose: in production an LLM may
# generate questions, but only inside categories the hiring team defines.
QUESTIONS = [
    {
        "category": "behavioural",
        "question": "Tell me about a time you debugged a really hard problem.",
        "expected_keywords": ["reproduce", "logs", "root cause", "fix", "test"],
    },
    {
        "category": "behavioural",
        "question": "Describe a situation where you disagreed with a teammate. How did you handle it?",
        "expected_keywords": ["communicat", "listen", "compromise", "data", "outcome"],
    },
    {
        "category": "technical",
        "question": "A query that used to take 50 ms now takes 4 seconds. Walk me through what you do.",
        "expected_keywords": ["explain", "index", "query plan", "n+1", "cache"],
    },
    {
        "category": "technical",
        "question": "How would you rate-limit a public API?",
        "expected_keywords": ["token bucket", "redis", "window", "429", "per user"],
    },
    {
        "category": "behavioural",
        "question": "Tell me about a deadline you nearly missed.",
        "expected_keywords": ["priorit", "stakeholder", "scope", "communicat", "deliver"],
    },
]
```

In production the questions might be LLM-generated, but always *inside* categories the company defines. For this build they're fixed so every candidate is measured on the same ground.

#### Tools the model can see: the schema

The model never sees your Python. It sees a JSON description of each tool: its name, a sentence about what it does, and the parameters it takes. The **description is how the model decides whether to call it**, so write it like documentation for a colleague.

```pseudo title="agent.py"
LOAD .env, CREATE the Groq client, SET MODEL = "openai/gpt-oss-20b"
SET session_log = empty list   // one dict per evaluated answer
SET TOOL_SCHEMA and TOOL_FUNCTIONS = the tools the model may call, and the function that runs each one
SET SYSTEM_PROMPT = the InterviewIQ coach rules: call the three tools, base feedback only on their results
SET MAX_TOOL_ROUNDS = 5

DEFINE generate_final_report():
    IF session_log is empty THEN RETURN "No answers evaluated yet."
    FOR EACH entry in session_log, numbered from 1:
        ADD a line with its filler total, missing STAR parts and relevance
        ADD its relevance score to scores, and its missing STAR parts to gaps
        IF filler total is above 2 THEN ADD "filler words" to gaps
    IF scores is not empty THEN
        ADD average relevance, then the lowest-scoring question and the keywords it missed
    IF gaps is not empty THEN ADD gaps, most frequent first
    RETURN all lines joined into one text

DEFINE run_loop(messages, result_out):
    REPEAT up to MAX_TOOL_ROUNDS (5) times:
        ASK the model with messages and TOOL_SCHEMA
        IF the model requested no tools THEN RETURN its text   // done
        ADD its tool requests to messages
        FOR EACH tool request:
            CALL the matching function in TOOL_FUNCTIONS with its arguments
            IF result_out is given and the tool is not generate_final_report THEN store the result in result_out
            ADD the result to messages
    RETURN "Sorry - I couldn't finish evaluating that answer."

DEFINE run_turn(item, answer):
    SET messages = system prompt, then question, answer and expected keywords
    SET results = empty dict
    SET feedback = run_loop(messages, results)
    ADD question, category, answer, results and feedback to session_log
    RETURN feedback

DEFINE ask_agent(user_message):
    SET history = question, category and results of each session_log entry, as JSON
    CALL run_loop with the system prompt, history and the candidate's message
    RETURN the reply   // session_log is not changed

DEFINE ask_final_report():
    RETURN generate_final_report()
```

> **Imported:**
> - `json` Python standard library: writes the session history as JSON text and reads tool arguments back.
> - `os` Python standard library: reads `GROQ_API_KEY` from the environment.
> - `load_dotenv` from `dotenv`, package python-dotenv: copies the `.env` file into the environment.
> - `Groq` from `groq`: the client that sends requests to the model.
> - `detect_filler_words` from your `tools.py`: counts filler words, one of the three tools the model may call.
> - `check_star_structure` from your `tools.py`: checks which STAR parts the answer contains.
> - `score_relevance` from your `tools.py`: scores the answer against the expected keywords.

**agent.py** · ask 1 + ask 2 · the heart of the project

```python reveal title="agent.py · ask 1 + ask 2 · the heart of the project"
import json
import os

from dotenv import load_dotenv
from groq import Groq

from tools import detect_filler_words, check_star_structure, score_relevance

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"   # llama-3.3-70b-versatile is deprecated on Groq

# Session memory: one structured dict per evaluated answer.
# {"question", "category", "answer", "results": {tool_name: tool_output}, "feedback"}
session_log = []

TOOL_SCHEMA = [
    {"type": "function", "function": {
        "name": "detect_filler_words",
        "description": "Count filler words (um, uh, basically, you know ...) in the candidate's answer.",
        "parameters": {"type": "object",
                       "properties": {"answer": {"type": "string"}},
                       "required": ["answer"]}}},
    {"type": "function", "function": {
        "name": "check_star_structure",
        "description": "Check which parts of Situation, Task, Action, Result the answer contains.",
        "parameters": {"type": "object",
                       "properties": {"answer": {"type": "string"}},
                       "required": ["answer"]}}},
    {"type": "function", "function": {
        "name": "score_relevance",
        "description": "Score 0-100 for how many expected keywords the answer covers.",
        "parameters": {"type": "object",
                       "properties": {
                           "answer": {"type": "string"},
                           "expected_keywords": {"type": "array", "items": {"type": "string"}}},
                       "required": ["answer", "expected_keywords"]}}},
    {"type": "function", "function": {
        "name": "generate_final_report",
        "description": "Aggregate the whole session: average relevance, lowest-scoring question, weakest area.",
        "parameters": {"type": "object", "properties": {}}}},   # no arguments
]

def generate_final_report() -> str:
    if not session_log:
        return "No answers evaluated yet."
    lines, scores, gaps = [], [], {}
    for i, entry in enumerate(session_log, 1):
        r = entry["results"]
        fill = r.get("detect_filler_words", {})
        star = r.get("check_star_structure", {})
        rel = r.get("score_relevance", {})
        lines.append(f"Q{i}. {entry['question']}")
        lines.append(f"   fillers: {fill.get('total', '-')}  |  "
                     f"STAR missing: {', '.join(star.get('missing', [])) or 'none'}  |  "
                     f"relevance: {rel.get('score', '-')}/100")
        if "score" in rel:
            scores.append((rel["score"], i, entry))
        for part in star.get("missing", []):
            gaps[part] = gaps.get(part, 0) + 1
        if fill.get("total", 0) > 2:
            gaps["filler words"] = gaps.get("filler words", 0) + 1
    if scores:
        avg = sum(s for s, _, _ in scores) / len(scores)
        low_score, low_i, low = min(scores, key=lambda t: t[0])
        low_gaps = low["results"].get("check_star_structure", {}).get("missing", [])
        lines.append(f"\nAverage relevance: {avg:.0f}/100")
        lines.append(f"Lowest-scoring question: Q{low_i} ({low['category']}) at {low_score}/100")
        lines.append(f"Weakest area: {low['question']} "
                     f"- missed {', '.join(low['results']['score_relevance']['missed']) or 'nothing'}"
                     f"{'; STAR gaps: ' + ', '.join(low_gaps) if low_gaps else ''}")
    if gaps:
        ranked = sorted(gaps.items(), key=lambda kv: -kv[1])
        lines.append("Recurring gaps: " + ", ".join(f"{k} x{n}" for k, n in ranked))
    return "\n".join(lines)

TOOL_FUNCTIONS = {
    "detect_filler_words":   lambda a: detect_filler_words(a["answer"]),
    "check_star_structure":  lambda a: check_star_structure(a["answer"]),
    "score_relevance":       lambda a: score_relevance(a["answer"], a["expected_keywords"]),
    "generate_final_report": lambda a: generate_final_report(),
}

SYSTEM_PROMPT = """You are InterviewIQ, an encouraging AI mock-interview coach.
For every candidate answer:
- call detect_filler_words, check_star_structure and score_relevance
- base your feedback ONLY on what the tools return; never invent a score
- reply in 3-4 sentences: one thing that worked, one concrete fix
When asked about overall performance, use the session history you are given,
or call generate_final_report."""

MAX_TOOL_ROUNDS = 5

def run_loop(messages: list, result_out: dict | None = None) -> str:
    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMA, tool_choice="auto")
        msg = response.choices[0].message
        if not msg.tool_calls:                      # model is done: plain answer
            return msg.content
        messages.append({
            "role": "assistant", "content": msg.content or "",
            "tool_calls": [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name,
                                         "arguments": c.function.arguments}}
                           for c in msg.tool_calls]})
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = TOOL_FUNCTIONS[name](args)
            if result_out is not None and name != "generate_final_report":
                result_out[name] = result           # captured for session memory
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result)})
    return "Sorry - I couldn't finish evaluating that answer."

def run_turn(item: dict, answer: str) -> str:
    user_message = (f"Question: {item['question']}\n"
                    f"Candidate answer: {answer}\n"
                    f"Expected keywords: {item['expected_keywords']}\n"
                    "Evaluate this answer using the available tools, then give short feedback.")
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}]
    results = {}
    feedback = run_loop(messages, result_out=results)
    session_log.append({"question": item["question"], "category": item["category"],
                        "answer": answer, "results": results, "feedback": feedback})
    return feedback

def ask_agent(user_message: str) -> str:
    history = json.dumps([{k: e[k] for k in ("question", "category", "results")}
                          for e in session_log], indent=1)
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Session so far:\n{history}\n\n"
                                            f"Candidate asks: {user_message}"}]
    return run_loop(messages)

def ask_final_report() -> str:
    return generate_final_report()
```

1 **No parameters still needs a schema** `generate_final_report` declares `"properties": {}`. In plain Python you'd never write that, but without it the model doesn't know the function can be called with nothing.

2 **The dispatch table** `TOOL_FUNCTIONS` maps the name the model asks for to a `lambda` that unpacks its arguments. One dictionary lookup replaces an `if/elif` chain, and adding a tool is one line here plus one schema entry.

3 **`MAX_TOOL_ROUNDS = 5` is a seatbelt** A model that keeps calling tools forever is a real failure mode, and every round is a paid request. Cap it, and return something graceful when the cap is hit.

4 **Message order is part of the protocol** The assistant message carrying the `tool_calls` must go into `messages` *before* the tool results, and each result carries the `tool_call_id` it answers. Get either wrong and the provider rejects the next request.

5 **Memory stores what the tools said, not what the model said** `result_out` is filled inside the loop from the tool return values. The session log holds measured numbers. The model's paraphrase of them goes in `feedback`, next to them, never in place of them.

6 **The model is named in one place** `llama-3.3-70b-versatile` was deprecated on Groq while the class ran. Swapping to `openai/gpt-oss-20b`, which has a generous free tier, is a one-line change. Other providers work too, but check their tool-call format, which can differ slightly.

#### One evaluated answer, request by request

1

#### Request 1 — system + user message

1 LLM call

Sends

System prompt, then question, answer and expected keywords. Plus `TOOL_SCHEMA`.

Model returns

No text. Three `tool_calls` in one message.

Payload

detect_filler_words check_star_structure score_relevance {"answer": "…", "expected_keywords": […]}

> **Note:**
> The model chose all three because the system prompt says “for every candidate answer, call…”. On a meta-question it would choose differently. That choice is what makes it an **agent** and not a script.

2

#### Your code runs the tools

0 LLM calls · microseconds

Looks up

`TOOL_FUNCTIONS[name]` for each call.

Runs

Plain Python. Deterministic. Free.

Appends

{"role": "tool", "tool_call_id": "call_…", "content": "{\"score\": 100, …}"}

3

#### Request 2 — the same messages, now with results

1 LLM call

Sends

Everything so far, including the three tool results.

Model returns

Text, no tool calls, so the loop exits.

Output

"Great job — you nailed the STAR structure and hit every key concept, with no fillers…"

> **Note:**
> Two requests per answer is the normal case. The loop allows five in case the model wants a second look, for example re-scoring after it notices something.

Ask 2 · memory

## A list that remembers, and arithmetic over it

Session memory here is a Python list. That was deliberate, to keep the build doable in two hours. It still has to be **structured**. Appending free text would make the final report impossible; appending one dict per answer makes it a loop.

session_log[1] = { "question": **"Describe a situation where you disagreed…"**, "category": "behavioural", "answer": "Um, basically I just, like, talked to him…", "results": { "detect_filler_words": {"total": **5**, "verdict": "needs improvement", …}, "check_star_structure": {"missing": [**"situation","task","action","result"**], …}, "score_relevance": {"score": **0**, "missed": [...], …} }, "feedback": *"You used a lot of filler words, which can distract…"* }

From that shape, the report is three lines of arithmetic. **Average relevance** is the mean of every `score`. The **lowest-scoring question** is a `min()`. The **weakest area** is the lowest-scoring question together with exactly what it missed, plus a tally of recurring gaps across *all* answers. That tally is what makes it “based on the complete session” rather than the last answer.

#### What the demo produced

Q1 · debugging

100fillers 0 · STAR complete

Q2 · disagreement

0fillers 3+ · STAR missing

Average

50out of 100

Weakest area

Handling disagreements with a teammate

Asked “what is my weakest area?” mid-session, the coach named the disagreement question and suggested how to restructure it. It could only do that because `ask_agent()` handed it the session log.

Production reality

**A module-level list is shared by every browser tab.** `session_log = []` lives once per Python process, so if two candidates use the Gradio app at the same time, their answers land in the same list and each sees the other's scores. That's fine for a single-user demo. For real users, key memory by session: Gradio's `gr.State` for per-tab state, or a database table keyed by `session_id`. The schema of each entry stays exactly the same.

Ask the room

“Should the final report be written by the LLM or by a Python function?”

The *numbers* by Python, always. Averages and minimums are not a judgement call. In this solution the report is pure code, and the model is free to *narrate* it when the candidate asks, by calling `generate_final_report` as a tool and explaining the result. The same split as everywhere else: code measures, the model talks.

Ask 3 · the interface

## Six components, three click handlers

Current question

`gr.Markdown`, advances after each submit

Answer box

`gr.Textbox`, cleared after submit

Feedback panel

appears once an answer is scored

Live scorecard

table rebuilt from `session_log`

Meta-question box

routes to `ask_agent()`

Final report

button → `generate_final_report()`

```pseudo title="app.py"
DEFINE format_scorecard():
    IF session_log is empty THEN RETURN "No answers scored yet."
    BUILD a Markdown table with one row per answer: question, relevance, fillers and STAR status
    RETURN the table as text

DEFINE show(i):
    RETURN "Question i+1 of N" in bold, followed by the question text

DEFINE on_submit(answer, q_index):
    IF q_index is past the last question THEN RETURN a "no more questions" message and the scorecard
    SET feedback = agent.run_turn(QUESTIONS[q_index], answer)
    SET next = q_index + 1
    SET display = show(next), or a "click Final report" message if the interview is over
    RETURN feedback, scorecard, next, display, and "" to clear the answer box

DEFINE ask_coach(message):
    RETURN agent.ask_agent(message)

DEFINE final_report():
    RETURN agent.ask_final_report() inside a code block

BUILD the page with gradio Blocks:
    show the title, a question-index state starting at 0, the first question, an answer box and a Submit button
    show a feedback box, the live scorecard, a meta-question box with an Ask button, and a Final report button
    when Submit is clicked, CALL on_submit with the answer and the question index
    when Ask is clicked, CALL ask_coach with the meta-question
    when Final report is clicked, CALL final_report
IF this file is run directly THEN start the demo
```

> **Imported:**
> - `gradio` (as `gr`) Gradio package: builds the browser page from text boxes, buttons and Markdown areas.
> - `agent` your own `agent.py`: the evaluator. Runs each answer, answers meta-questions and builds the report.
> - `QUESTIONS` from `interview_bank`, your own file: the fixed question list, shown one at a time.

**app.py** · ask 3 · python app.py

````python reveal title="app.py · ask 3 · python app.py"
import gradio as gr

import agent
from interview_bank import QUESTIONS

def format_scorecard() -> str:
    if not agent.session_log:
        return "_No answers scored yet._"
    lines = ["| # | Question | Relevance | Fillers | STAR |", "|---|---|---|---|---|"]
    for i, e in enumerate(agent.session_log, 1):
        rel = e["results"].get("score_relevance", {}).get("score", "-")
        fill = e["results"].get("detect_filler_words", {}).get("total", "-")
        star = e["results"].get("check_star_structure", {})
        star_txt = "complete" if star.get("all_present") else "missing " + ", ".join(star.get("missing", ["-"]))
        lines.append(f"| {i} | {e['question'][:48]}... | {rel}/100 | {fill} | {star_txt} |")
    return "\n".join(lines)

def show(i: int) -> str:
    return f"**Question {i + 1} of {len(QUESTIONS)}** - {QUESTIONS[i]['question']}"

def on_submit(answer, q_index):
    if q_index >= len(QUESTIONS):
        return "No more questions - click **Final report**.", format_scorecard(), q_index, "Interview complete.", ""
    feedback = agent.run_turn(QUESTIONS[q_index], answer)
    nxt = q_index + 1
    display = show(nxt) if nxt < len(QUESTIONS) else "Interview complete - click **Final report**."
    return feedback, format_scorecard(), nxt, display, ""   # "" clears the answer box

def ask_coach(message):
    return agent.ask_agent(message)

def final_report():
    return f"```\n{agent.ask_final_report()}\n```"

with gr.Blocks(title="InterviewIQ") as demo:
    gr.Markdown("# InterviewIQ - AI mock interview coach")
    q_state = gr.State(0)
    question_display = gr.Markdown(show(0))
    answer_box = gr.Textbox(label="Your answer", lines=6)
    submit_btn = gr.Button("Submit answer", variant="primary")
    feedback_box = gr.Markdown()
    gr.Markdown("### Live scorecard")
    scorecard = gr.Markdown(format_scorecard())
    gr.Markdown("### Ask the coach")
    meta_box = gr.Textbox(label="e.g. How am I doing so far?")
    meta_btn = gr.Button("Ask")
    meta_reply = gr.Markdown()
    report_btn = gr.Button("Final report")
    report_box = gr.Markdown()

    submit_btn.click(on_submit, inputs=[answer_box, q_state],
                     outputs=[feedback_box, scorecard, q_state, question_display, answer_box])
    meta_btn.click(ask_coach, inputs=meta_box, outputs=meta_reply)
    report_btn.click(final_report, outputs=report_box)

if __name__ == "__main__":
    demo.launch()
````

1 **`gr.State(0)` holds the question index** The state value goes in as an input and comes back out as an output. That round trip is how a Gradio app remembers anything between clicks.

2 **Five outputs, five return values, in order** `on_submit` returns feedback, scorecard, next index, next question and `""`. That last empty string is what clears the answer box. The order has to match the `outputs=[…]` list exactly.

3 **Defensive `.get(…, "-")` everywhere** If the model skipped a tool on some turn, the scorecard shows a dash instead of raising `KeyError` and blanking the UI. A demo that crashes on a missing key is a failed demo.

#### The terminal version is not the same product

```pseudo title="main.py"
PRINT the "terminal mode" heading
FOR EACH question in QUESTIONS, numbered from 1:
    PRINT the question
    ASK the candidate for an answer, typed in the terminal
    PRINT the feedback from agent.run_turn(question, answer)
PRINT the "Final report" heading
PRINT agent.ask_final_report()   // runs once, after the last question
```

> **Imported:**
> - `agent` your own `agent.py`: runs each answer through the evaluator and builds the final report.
> - `QUESTIONS` from `interview_bank`, your own file: the questions, asked in order.

```python reveal title="main.py · python main.py"
import agent
from interview_bank import QUESTIONS

# The CLI flow is strictly sequential: no meta questions mid-interview,
# and the final report prints automatically once the questions run out.
print("=== InterviewIQ (terminal mode) ===")
for i, item in enumerate(QUESTIONS, 1):
    print(f"\nQ{i}. {item['question']}")
    answer = input("Your answer: ")
    print("\nCoach:", agent.run_turn(item, answer))
    print("-" * 60)

print("\n=== Final report ===")
print(agent.ask_final_report())
```

|  | main.py · CLI | app.py · Gradio |
| --- | --- | --- |
| **Flow** | Strictly sequential. One input channel. | Any order. Several input boxes. |
| **Meta-questions** | Not possible mid-interview. | Any time, via the meta box. |
| **Final report** | Printed automatically after the last question. | On demand, even halfway through. |
| **Use it for** | Milestone 6: proving the agent end-to-end. | Milestone 11: the deliverable. |

Ask 2 · verification

## Prove the memory with a planted weak answer

`memory_check.py` is written last, once there is something to check. It feeds one strong answer and one deliberately weak answer, asks the agent about performance, and checks the weak answer was identified as the weakest area. It's a test with a known right answer, because you planted it.

```pseudo title="memory_check.py"
SET STRONG = a complete answer with situation, task, action and result
SET WEAK = a vague answer full of filler words
clear agent.session_log   // start from an empty session
RUN agent.run_turn on QUESTIONS[0] with STRONG   // should score high
RUN agent.run_turn on QUESTIONS[1] with WEAK     // planted: deliberately weak
SET report = agent.ask_final_report()
SET reply = agent.ask_agent("What is my weakest area so far?")
PRINT report, then reply
SET checks:
    report contains "Lowest-scoring question: Q2"
    the Q2 score is below the Q1 score
    reply contains disagree, teammate, q2 or "question 2" (ignoring case)
FOR EACH check: PRINT "PASS" if it is true, otherwise "FAIL"
```

> **Imported:**
> - `agent` your own `agent.py`: the module under test. Its session log and evaluator are used directly.
> - `QUESTIONS` from `interview_bank`, your own file: supplies the questions for the two planted answers.

**memory_check.py** · milestone 10 · python memory_check.py

```python reveal title="memory_check.py · milestone 10 · python memory_check.py"
import agent
from interview_bank import QUESTIONS

STRONG = ("When I was at my previous company, checkout failed for 2% of users. "
          "I was responsible for finding why. I decided to reproduce it locally, read the logs, "
          "found the root cause in a race condition, wrote a fix and a regression test. "
          "As a result failures dropped to zero.")
WEAK = "Um, basically I, like, just talked to him and, you know, it was kind of fine."

agent.session_log.clear()
agent.run_turn(QUESTIONS[0], STRONG)     # should score high
agent.run_turn(QUESTIONS[1], WEAK)       # deliberately weak

report = agent.ask_final_report()
reply = agent.ask_agent("What is my weakest area so far?")
print(report, "\n\nAgent says:", reply)

weak_q = QUESTIONS[1]["question"]
checks = {
    "report names Q2 as lowest-scoring": "Lowest-scoring question: Q2" in report,
    "Q2 scored below Q1": (agent.session_log[1]["results"]["score_relevance"]["score"]
                           < agent.session_log[0]["results"]["score_relevance"]["score"]),
    "agent's answer points at the disagreement question":
        any(w in reply.lower() for w in ("disagree", "teammate", "q2", "question 2")),
}
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + name)
```

*expected output (abridged)* Average relevance: **50/100** Lowest-scoring question: **Q2** (behavioural) at **0/100** Weakest area: Describe a situation where you disagreed with a teammate… Recurring gaps: situation x1, task x1, action x1, result x1, filler words x1 **PASS** report names Q2 as lowest-scoring **PASS** Q2 scored below Q1 **PASS** agent's answer points at the disagreement question

The first two checks are deterministic: they test code. The third tests the model, and it can occasionally fail on wording even when the memory is fine. Keep that distinction in mind when one of them goes red.

Ask 4 · bonus
