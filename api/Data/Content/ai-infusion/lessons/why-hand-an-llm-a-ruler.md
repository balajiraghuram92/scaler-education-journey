# Why hand an LLM a ruler?

> **Lesson resources · Lesson 7 · The interview coach:**
> - [Watch the Class 7 recording](https://www.scaler.com/meetings/i/ai-infused-learning-7/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

AI Infusion · Class 7 · Live project session

#### The coach that *can't* be bluffed

A real AI-engineering take-home, solved live in one sitting. An interview coach that grades a candidate's written answers with deterministic tools, remembers the whole session, answers “how am I doing?” mid-interview, and ships behind a Gradio UI.

**Stack** Python · Groq · Gradio **Model** openai/gpt-oss-20b **Brief** a company's AI-engineer assignment **Scope** 11 milestones + 1 bonus

The hook

## Why hand an LLM a ruler?

Ask a model “does this answer contain filler words?” and it will tell you. Ask again and it may tell you something slightly different. Ask a different model and you get a different definition of “filler” altogether.

That is fine for a chatbot. It is not fine for a hiring screen. If a candidate is rejected because their answer was “padded,” the hiring team has to be able to say *what* padded means — and it has to mean the same thing on Monday as it did on Friday, for every candidate.

So the design splits the work cleanly. **Tools measure. The LLM explains.** Three plain Python functions — filler-word counting, STAR-structure detection, keyword relevance — produce numbers the company defined. The model decides *which* tool to call, reads the results, and turns them into encouraging, specific feedback. It never invents the score.

Ask the room

“The model can already spot filler words on its own. Why write `detect_filler_words()` at all?”

Because the model's understanding of “filler” and the company's can drift apart — and you can't see when they do. A hard-coded list keeps the AI and the hiring team **in the same ballpark**: it gives the same answer every run, it can be reviewed in a pull request, and when a candidate disputes a score you can point at the exact rule. That is what “deterministic” buys you here.

{{diagram:1}}

*Same answer, two designs. On the left the model is both the measuring instrument and the narrator, so the measurement wobbles. On the right the measurement is code the company owns, and the model is only asked to do what it is genuinely good at — explaining.*

The brief

## Screen out the people applying only for the package

The assignment came from a company hiring AI engineers, and the class solved it live instead of taking it home. The scenario: hiring teams drown in résumés, and many applicants aren't qualified — they saw a good opening or a good salary and clicked apply. Before a résumé reaches a human, a text-based AI interview should filter them.

Given a candidate's **written** answer to an interview question, the system must:

1. **Evaluate** the answer using a set of tools the agent chooses between.
2. **Give feedback** that is encouraging when the answer is good and specific about what to fix when it isn't.
3. **Remember** every question, answer and evaluation, so it can produce a final report and answer meta-questions like “how am I doing so far?”
4. Run behind a **browser interface**.

It is conversational, not voice — the candidate types. Questions come from a fixed bank, so the evaluation stays comparable across candidates.

#### One question, two answers

**Q2** behavioural **ASKED** “Describe a situation where you disagreed with a teammate. How did you handle it?”

At my previous company S a teammate wanted to rewrite our payments service. I was responsible T for its uptime, so I listened to his reasons first, then I proposed A we look at the incident data together. We agreed on a compromise — rewrite one module behind a flag — and communicated it to the team. As a result R the outcome was a 30% drop in incidents and no big-bang rewrite.

**SAME QUESTION** a weak answer

Um, basically I just, like, talked to him and, you know, it was kind of fine in the end R.

STAR cue  expected keyword  filler word

| Tool | Strong answer | Weak answer |
| --- | --- | --- |
| `detect_filler_words` | 0 · clean | 5 · needs improvement |
| `check_star_structure` | S T A R · all present | R only · missing S, T, A |
| `score_relevance` | 100 / 100 | 0 / 100 |

Notice “in the end” in the weak answer. It *is* one of the result cues — but the weak answer still has no situation, task or action, and it hits none of the expected keywords. The tools aren't fooled by one lucky phrase, because three of them vote on different properties.

Production reality

The filler-word tool exists for a specific failure: a candidate who doesn't know the answer pads it to *look* long. Length alone is a terrible proxy for quality — five sentences of “basically, you know, kind of” score as long as five sentences of substance. A filler count is the cheapest possible signal that separates the two.

The asks

## Four asks, one graded deliverable

| # | Ask | What “done” means |
| --- | --- | --- |
| 1 | **Tool-calling evaluator agent** | The agent decides which of three tools to call — `detect_filler_words`, `check_star_structure`, `score_relevance` (0–100) — interprets the structured results and writes short, encouraging feedback. |
| 2 | **Session memory → aggregated evaluation** | Every question, answer and tool result is kept. The final report computes the *average* relevance, the *lowest-scoring question* and the *weakest area* from the whole session — not just the last answer. Verified by `memory_check.py`. |
| 3 | **Working Gradio interface** | Current question, answer box, feedback panel, live scorecard, meta-question box, final-report button. Any UI framework is acceptable if you don't know Gradio. |
| 4 | **Bonus · multi-agent** not graded | A second *interviewer* agent picks the next question's category from the candidate's performance so far, then hands the question to the existing evaluator. |

Ask the room

“The final report has to name the weakest area. Can the LLM just “look back” at the conversation and decide?”

Only if the conversation still exists, and only if it holds something you can *aggregate*. Feedback prose can't be averaged. That is why ask 2 is about memory first and the report second: store the tool outputs — the numbers — and the report becomes arithmetic over a list.

Architecture

## One loop, one list, two front doors

Strip away the UI and the system is small: a function that loops between the model and the tools, and a list that remembers what the tools said.

{{diagram:2}}

*The solid arrows are one evaluated answer. The dashed arrow is the meta-question path: `ask_agent()` reads the whole session log and goes through the same loop, so the model can still call a tool (usually `generate_final_report`) while answering “how am I doing?”.*

#### The project folder

interview-iq/ ├── .env *# GROQ_API_KEY=… (never commit this)* ├── requirements.txt *# groq, gradio, python-dotenv* ├── tools.py *# ask 1 · the three deterministic tools* ├── interview_bank.py *# questions + expected keywords + category* ├── agent.py *# schemas, run_loop, session_log, report, ask_agent* ├── main.py *# terminal flow* ├── app.py *# ask 3 · Gradio UI* ├── memory_check.py *# ask 2 · verification script — written last* ├── interviewer_agent.py *# ask 4 · bonus* └── run_multi_agent.py *# ask 4 · bonus*

Separate files are not ceremony. When a tool call fails you go straight to `tools.py`; when the scorecard renders wrong you go straight to `app.py`. That is how the solution is laid out in industry, and it is why the session insisted on it.

The build order

## Wire nothing until it works alone

The most important instruction of the session wasn't about AI at all. It was about the order you build things in.

If you write three tools, plug them straight into the LLM and the output is wrong, you can't tell whether the tool is broken, the schema is wrong, or the model ignored you — and every attempt to find out burns API tokens. So the suggested approach is strictly bottom-up:

| Step | Build | Done when |
| --- | --- | --- |
| 1 | venv, `requirements.txt`, `.env`, one plain LLM call | The model answers “hello” — the key and provider config are proven before anything else exists. |
| 2 | The three tools as standalone functions | Each returns the dict you expect for a hand-written strong and weak answer. No LLM involved. |
| 3 | Wire tools into the evaluator loop | One complete evaluation runs end-to-end through `main.py`. |
| 4 | Session memory | Every evaluated answer, its scores and feedback are in `session_log` and still there later. |
| 5 | `generate_final_report()` | Average relevance, lowest-scoring question, weakest area — computed from the list. |
| 6 | `ask_agent()` for meta-questions | “How am I doing?” is answered from the full history, mid-interview. |
| 7 | `memory_check.py` | A deliberately weak answer is correctly named as the weakest area. |
| 8 | `app.py` | The whole workflow runs in the browser. The UI is the *last* layer. |

#### The same thing as graded milestones

| M | Milestone | Proof |
| --- | --- | --- |
| M1 | Environment setup — venv, install requirements, configure `.env` | `pip list` inside the venv |
| M2 | Basic LLM call without tools | a reply from the provider |
| M3 | `detect_filler_words` implemented and tested directly | `python tools.py` |
| M4 | `check_star_structure` implemented and tested directly | `python tools.py` |
| M5 | `score_relevance` implemented and tested directly | `python tools.py` |
| M6 | Tool-calling evaluator — all three tools in the loop | `python main.py` |
| M7 | Session memory | log persists across turns |
| M8 | Final report with real aggregation | average · lowest · weakest |
| M9 | Mid-session agent questions via `ask_agent()` | answers use full history |
| M10 | Memory verification | `python memory_check.py` |
| M11 | Gradio application | `python app.py` |
| M12 | bonus Multi-agent system | `python run_multi_agent.py` |

On vibe-coding it

Using an LLM to write the code was explicitly allowed. What wasn't recommended was asking for the whole project in one prompt. You get a large, confident, sometimes-broken codebase you can't debug. Prompt **one ask at a time** and check each piece against the step it's meant to satisfy. You still have to read what it gave you.

Ask 1 · the tools

## Three functions, each returning a dict

Every tool takes the raw answer and returns structured data, never a sentence. The model reads JSON reliably; the report needs numbers; the scorecard needs fields. A formatted string would serve none of them.

```pseudo title="tools.py"
SET FILLER_WORDS = a short fixed list ("um", "uh", "like", "basically" and so on)   // the company decides what counts as filler
SET STAR_SIGNALS = cue phrases for each STAR part: situation, task, action, result

DEFINE _count(phrase, text):
    // \b on both sides: "um" must not match "summary"
    RETURN how many times phrase appears as a whole word in text

DEFINE detect_filler_words(answer):
    SET text = answer in lower case
    SET found = count of each FILLER_WORDS entry in text
    keep only the words that appear at least once
    SET total = sum of the counts in found
    RETURN total, found, and verdict: "clean" if total is 2 or less, else "needs improvement"

DEFINE check_star_structure(answer):
    SET text = answer in lower case
    SET present = each STAR part that has at least one cue found in text
    SET missing = each STAR part that is not in present
    RETURN present, missing, and all_present (true when nothing is missing)

DEFINE score_relevance(answer, expected_keywords):
    SET text = answer in lower case
    // plain substring on purpose: "listen" should credit "listened"
    SET covered = each keyword found inside text
    SET missed = each keyword not found inside text
    SET score = share of keywords covered, times 100, rounded (0 if there are no keywords)
    RETURN score, covered, missed

IF this file is run directly THEN PRINT the three results for one weak answer
```

> **Imported:**
> - `re` Python standard library: regular expressions. Used to match whole words only, so “um” is not found inside “summary”.

**tools.py** · ask 1 · run it directly to test

```python reveal title="tools.py · ask 1 · run it directly to test"
import re

# Deliberately small and hard-coded: the company decides what counts as filler,
# not the model. Extend the list; never hand the definition to the LLM.
FILLER_WORDS = ["um", "uh", "like", "basically", "actually", "literally",
                "you know", "kind of", "sort of", "i mean"]

STAR_SIGNALS = {
    "situation": ["when i was", "at my previous", "in my previous", "while working",
                  "at my last", "we had a"],
    "task":      ["i needed to", "my task was", "i was responsible", "the goal was",
                  "i had to", "my job was"],
    "action":    ["i decided", "i implemented", "i built", "i led", "i created",
                  "i wrote", "i set up", "i proposed"],
    "result":    ["as a result", "this led to", "which led to", "we achieved",
                  "reduced", "improved", "in the end"],
}

def _count(phrase: str, text: str) -> int:
    # \b on both sides: "um" must not match "summary", "like" must not match "likely"
    return len(re.findall(r"\b" + re.escape(phrase) + r"\b", text))

def detect_filler_words(answer: str) -> dict:
    text = answer.lower()
    found = {w: _count(w, text) for w in FILLER_WORDS}
    found = {w: n for w, n in found.items() if n > 0}
    total = sum(found.values())
    return {
        "total": total,
        "found": found,
        "verdict": "clean" if total <= 2 else "needs improvement",
    }

def check_star_structure(answer: str) -> dict:
    text = answer.lower()
    present = [part for part, cues in STAR_SIGNALS.items()
               if any(_count(cue, text) for cue in cues)]
    missing = [part for part in STAR_SIGNALS if part not in present]
    return {"present": present, "missing": missing, "all_present": not missing}

def score_relevance(answer: str, expected_keywords: list) -> dict:
    text = answer.lower()
    # plain substring on purpose: "listen" should credit "listened"
    covered = [k for k in expected_keywords if k.lower() in text]
    missed = [k for k in expected_keywords if k.lower() not in text]
    score = round(len(covered) / len(expected_keywords) * 100) if expected_keywords else 0
    return {"score": score, "covered": covered, "missed": missed}

if __name__ == "__main__":
    # Step 2: prove every tool on its own before any LLM sees it.
    weak = "Um, basically I just, like, talked to him and you know it was fine."
    print(detect_filler_words(weak))
    print(check_star_structure(weak))
    print(score_relevance(weak, ["communicat", "listen", "compromise", "data"]))
```

1 **Lists are policy, and they are deliberately incomplete** The filler list and the STAR cue lists are non-exhaustive. Extend them as you find misses. The point is that a *person* extends them, in a reviewed change, not that the model improvises.

2 **The landmine: substring counting** The obvious version is `answer.lower().count("um")`. It counts the “um” in *summary*, *document* and *umbrella*, and the “like” in *likely*. A careful candidate gets penalised for vocabulary. Word boundaries (`\b`) fix it.

3 **A verdict, not just a count** `total ≤ 2` is “clean”. Everyone says “um” occasionally; the threshold encodes how much the company tolerates.

4 **Relevance uses substrings on purpose** Here the opposite choice is right: the keyword `listen` should credit “listened”, and `communicat` should credit both “communicated” and “communication”. Store stems in the bank and let the substring match do the rest.

5 **`all_present: not missing`** An empty list is falsy, so `not missing` is `True` exactly when nothing is missing. It's a small idiom that reads like the sentence it implements.

Try it
