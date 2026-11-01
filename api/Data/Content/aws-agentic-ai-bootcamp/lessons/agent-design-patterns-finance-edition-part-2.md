# Agent design patterns — finance edition (part 2)

## Agent design patterns — finance edition (part 2)

#### 2.4 Lab 2C · Episodic memory: from today's chat to tomorrow's wisdom

In Lab 2B the notepad is binned when the session ends. Now we teach the agent to **write a journal entry before the notepad is binned**, file it in a cabinet that survives restarts, and **read the most relevant entries** the next time a client asks a similar question.

> **🧠 Analogy — the trader's end-of-day journal:**
> At 4 pm, before throwing away the notepad, a good trader writes one journal page: *what the market was doing, what we changed, what worked, what didn't, lessons*. The page is filed in a cabinet sorted by **meaning**, not by date. Next month, facing a similar market, she pulls the three most similar pages before deciding. That is the whole lab.

| Memory type | In a bank, it holds… |
| --- | --- |
| Working | Today's notepad: current allocation, the client's constraints, this session's reasoning |
| Episodic | The journal: past rebalancing sessions, what was proposed, what the client accepted or rejected |
| Semantic | The rulebook and facts: "max 75% in stocks", "Apple is a technology company", "USD/EUR is a currency pair", allowed order types |
| Procedural | The SOP checklist: fetch ratios → check news sentiment → check sector exposure → compare with targets → write recommendation with risk notes. Can come from the bank's documented processes (KYC review, underwriting steps) or be learned — *with controls, so the agent doesn't learn a bad habit*. |

##### The big picture: how your data travels

This is the map for the whole lab. Every box is a **variable** in the code; every arrow is **the line of code** that turns one into the next. Use the step-through below it — the map lights up as you go.

{{diagram:1}}

*Day 1 turns a chat into a journal page and files it on disk. Day 2 starts with an empty notepad, searches the cabinet by meaning, and pastes the best page into the new question. Long-term memory = retrieve, then paste into the prompt.*

🧪 Simulation · the key one

##### Step through the lab and watch every variable fill up

The trail below is a mini version of the map: **gold** = this step, **green** = already filled.

**1 · Read the notepad**

Variable now holds · `conversation_history`

The session lives in RAM and dies with the notebook. First we copy it into a clean Python list of (who, what) pairs.

```
all_items = await session_ptf_rebal.get_items()
# ...the loop from Lab 2B builds:
conversation_history.append((role, text))
```

```
[
  ("user", "Current Market Situation: volatility high, trend declining. Portfolio {stocks 0.70, bonds 0.20, cash 0.10} ..."),
  ("assistant", "### Current Portfolio Analysis ... target: stocks 50%, bonds 40%, cash 10% ..."),
  ("user", "In this case, I'm reducing equity to 50%, increasing bonds to 35% and cash to 15%."),
  ("assistant", "### Summary of Final Rebalanced Portfolio: stocks 50%, bonds 35%, cash 15% ...")
]
```

**2 · Flatten into one string**

A prompt is text, not a Python list. Each message becomes one fenced line; a blank line separates them.

```
conversation_history_string = "\n\n".join(
    [f'{role}: """{text}"""' for role, text in conversation_history]
)
```

Variable now holds · `conversation_history_string`

```
user: """Current Market Situation: ..."""

assistant: """### Current Portfolio Analysis ..."""

user: """In this case, I'm reducing equity to 50% ..."""

assistant: """### Summary of Final Rebalanced Portfolio ..."""
```

**3 · Fill the template**

The {conversation} slot receives the chat. Doubled braces {{ }} turn into single braces, giving the LLM a clean JSON example.

```
user_prompt = episodic_memory_prompt_template.format(
    conversation=conversation_history_string
)
```

Variable now holds · `user_prompt`

```
You will read a conversation between a user and a portfolio-rebalancing agent.
...
Return only valid JSON in this exact schema:
{                                      <- was {{ in the template
  "conversation_summary": string, ...
}                                      <- was }} in the template
Here is the conversation ...:
user: """Current Market Situation: ..."""   <- {conversation} was filled in
...
```

**4 · The LLM writes the journal page**

JSON mode makes the model return exactly the five keys. json.loads turns the text into a Python dictionary.

```
response = client.responses.create(model="gpt-4.1-mini",
    input=[{"role": "user", "content": user_prompt}],
    text={"format": {"type": "json_object"}})
episodic_memory = json.loads(response.output[0].content[0].text)
```

Variable now holds · `episodic_memory`

```
{
  "conversation_summary": "With high volatility and a declining market, the user cut equity from 70% to 50% ...",
  "portfolio_allocation_trajectory": "[{market: {volatility: high, trend: declining}, allocation: {stocks: 0.70, bonds: 0.20, cash: 0.10}}, ...]",
  "what_worked": "Progressive adjustments matched market conditions ...",
  "what_didnt_work": "Large shifts without discussing risk tolerance ...",
  "key_points": ["High vol + falling market justified cutting equity", "Consider risk profile and trading costs"]
}
```

**5 · Two versions of the same page**

The readable page gets embedded (searched by meaning). The plain fields become folder labels.

```
document_text = f"""Conversation Summary: {episodic_memory['conversation_summary']} ..."""
metadata_clean = {..., "key_points": " | ".join(episodic_memory["key_points"])}
```

Variable now holds · `document_text  +  metadata_clean`

```
document_text =
"Conversation Summary: With high volatility ...
 Portfolio Allocation Trajectory: [...]
 What Worked: ...
 What Didn't Work: ...
 Key Points: High vol + falling market ..., Consider risk profile ..."

metadata_clean = {
  "conversation_summary": "...", ...,
  "key_points": "High vol + falling market ... | Consider risk profile ..."   <- list became one string
}
```

**6 · Open the cabinet and the drawer**

Unlike the notepad, this lives on disk. The embedding function (the translator) is attached to the drawer, so everything filed here gets translated the same way.

```
persistent_client = chromadb.PersistentClient(path="./chroma_ptf_rebal")
collection = persistent_client.get_or_create_collection(
    "episodic_memory_ptf_rebal", embedding_function=embedding_function)
```

Variable now holds · `collection`

```
Collection(name="episodic_memory_ptf_rebal")   # empty drawer
stored in the folder ./chroma_ptf_rebal/ on disk
```

**7 · File the page**

Chroma calls the translator on document_text and stores vector + text + labels. Close the notebook, restart the laptop — it's still there.

```
collection.add(ids=["memory_1"], documents=[document_text], metadatas=[metadata_clean])
```

Variable now holds · `collection (now 1 page)`

```
id:        "memory_1"
embedding: [0.012, -0.034, 0.051, ...]   # 1,536 numbers, made automatically
document:  "Conversation Summary: With high volatility ..."
metadata:  {conversation_summary: ..., key_points: "... | ..."}
```

**8 · Next session: search by meaning**

The new question (low volatility, bullish) is translated with the same translator. Chroma returns the closest pages — outer list per question, inner list best-first.

```
episodic_memory_recap = collection.query(
    query_texts=[input_user_init], n_results=3)
```

Variable now holds · `episodic_memory_recap`

```
{
  "ids":       [["memory_1", "memory_7", "memory_3"]],
  "documents": [["Conversation Summary: With high volatility ...", "...", "..."]],
  "distances": [[0.21, 0.35, 0.48]],      # smaller = more similar
  "metadatas": [[{...}, {...}, {...}]]
}
```

**9 · Paste the lesson, run with a fresh notepad**

Empty notepad + yesterday's lesson inside the question = an agent that "remembers". That's long-term memory.

```
input_user_with_memory = input_user_init + f"""
Here are relevant insights from past rebalancing episodes. ...
{episodic_memory_recap['documents'][0][0]}
..."""
await Runner.run(portfolio_agent, input_user_with_memory, session=session_ptf_rebal_2)
```

Variable now holds · `input_user_with_memory`

```
Current Market Situation:
- Volatility Regime: low
- Market Trend: bullish
What rebalancing action should I take?
Here are relevant insights from past rebalancing episodes. Use them as guidance, not strict rules:
Conversation Summary: With high volatility and a declining market, the user cut equity ...
...
Argue your proposition using past rebalancing episodes if needed.
```

##### Now the code, one step at a time

**Step 1 · Start from Lab 2B's output.** We continue the same notebook, so `conversation_history` already exists — the list of `(role, text)` pairs we built from the notepad.

**Step 2 · Flatten the chat into one string.** An LLM prompt is one piece of text, not a Python list.

```python title="Python · lab_2c_episodic_memory.py · step 2"
# Original one-liner:
conversation_history_string = "\n\n".join([f'{elem[0]}: """{elem[1]}"""' for elem in conversation_history])

# Exactly the same thing, with friendlier names:
conversation_history_string = "\n\n".join(
    [f'{role}: """{text}"""' for role, text in conversation_history]
)
```

1. `elem` is one pair like `("user", "Current Market…")`, so `elem[0]` is the role and `elem[1]` is the text. Unpacking it as `role, text` is easier to read.
2. The `[ … for … in … ]` part (a list comprehension) builds one small string per message: `user: """Current Market…"""`. The triple quotes fence each message so the LLM sees exactly where one speaker stops.
3. `"\n\n".join(list)` glues those small strings into one, with a blank line between each.

# BEFORE: a list of pairs [("user", "Current Market Situation: ... What rebalancing action should I take?"), ("assistant", "### Current Portfolio Analysis ..."), ...] # AFTER: one string user: """Current Market Situation: ... What rebalancing action should I take?""" assistant: """### Current Portfolio Analysis ...""" user: """In this case, I'm reducing equity to 50% ..."""

**Step 3 · The prompt template** (shortened). It tells the LLM what a good journal page looks like.

```python title="Python · lab_2c_episodic_memory.py · step 3"
episodic_memory_prompt_template = """
You will read a conversation between a user and a portfolio-rebalancing agent.
Extract an episodic memory that will help the agent in future sessions.

OUTPUT FORMAT:
Return only valid JSON in this exact schema:
{{
  "conversation_summary": string,            // 3–5 sentences: market conditions, portfolio situation, actions taken
  "portfolio_allocation_trajectory": string, // how allocations changed, with the market situation each time
  "what_worked": string,                     // alignment with goals, risk management, clear decisions
  "what_didnt_work": string,                 // unclear strategy, over/under-reaction, concentration risk, data issues
  "key_points": ["string"]                   // the most important insights to keep for future sessions
}}

(… a few examples of GOOD and POOR summaries go here — few-shot …)

Here is the conversation between the user and the principal portfolio-rebalancing agent:
{conversation}
"""

user_prompt = episodic_memory_prompt_template.format(conversation=conversation_history_string)
```

> **⚠️ The curly-brace trap — read this twice:**
> `.format()` treats every `{something}` as a slot to fill. That's what we want for `{conversation}`. But the JSON example also has braces! Writing them **doubled** — `{{` and `}}` — tells `.format()` "this is a real brace, leave it alone". After formatting, `{{` becomes `{`.

# In the template # After .format(conversation=...) {{ { "conversation_summary": string, "conversation_summary": string, }} } {conversation} user: """Current Market Situation: ...""" (the whole chat)

💰 Finance corner — "portfolio_allocation_trajectory"

This is the most finance-specific field. It records *how the allocation moved and what the market was doing each time*, e.g. `[{market: {volatility: high, trend: declining}, allocation: {stocks: 0.70, bonds: 0.20, cash: 0.10}}, …]`. Next time the market looks similar, the agent can see what this client did then — that's case-based reasoning, the way experienced advisors think.

**Step 4 · Ask the LLM to write the journal page.**

```python title="Python · lab_2c_episodic_memory.py · step 4"
import json
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.responses.create(
    model="gpt-4.1-mini",
    input=[{"role": "user", "content": user_prompt}],
    text={"format": {"type": "json_object"}},              # JSON mode, as in Lab 1A
)
episodic_memory = json.loads(response.output[0].content[0].text)   # JSON text → Python dict
print(json.dumps(episodic_memory, indent=2))
```

episodic_memory = { "conversation_summary": "Initially, with high volatility and a declining market, the user reduced equity from 70% to 50% ...", "portfolio_allocation_trajectory": "[{market: {volatility: high, trend: declining}, allocation: {stocks: 0.70, ...}}, ...]", "what_worked": "Progressive adjustments aligned well with market conditions ...", "what_didnt_work": "Sizable shifts without discussing the user's risk tolerance ...", "key_points": [ "High volatility + declining market justified cutting equity", "Rebalancing should consider risk profile and trading costs", ... ] ← a LIST }

**Step 5 · Prepare two versions of the same page.**

```python title="Python · lab_2c_episodic_memory.py · step 5"
# Version A: one readable text — this is what gets embedded and searched by meaning
document_text = f"""
Conversation Summary: {episodic_memory['conversation_summary']}
Portfolio Allocation Trajectory: {episodic_memory['portfolio_allocation_trajectory']}
What Worked: {episodic_memory['what_worked']}
What Didn't Work: {episodic_memory['what_didnt_work']}
Key Points: {', '.join(episodic_memory['key_points'])}
"""

# Version B: the same facts as separate fields — the labels on the folder
metadata_clean = {
    "conversation_summary": episodic_memory["conversation_summary"],
    "portfolio_allocation_trajectory": episodic_memory["portfolio_allocation_trajectory"],
    "what_worked": episodic_memory["what_worked"],
    "what_didnt_work": episodic_memory["what_didnt_work"],
    "key_points": " | ".join(episodic_memory["key_points"]),   # list → one string
}
```

1. `document_text` is the **journal page**. Chroma will turn it into a vector so it can be found by meaning.
2. `metadata_clean` holds the **labels on the folder**: the same facts as named fields, useful for filtering and for reading one field back without re-parsing the text.
3. `" | ".join(...)` — Chroma metadata is meant for simple values (text, numbers, true/false), so the `key_points` list is joined into one string like `"High vol… | Rebalancing should…"`.

**Step 6 · Open the filing cabinet.**

```python title="Python · lab_2c_episodic_memory.py · step 6 (pip install chromadb)"
import chromadb
from chromadb.utils import embedding_functions

# The translator: turns any text into a list of 1,536 numbers (a vector) that captures its meaning
embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small",
)

collection_name = "episodic_memory_ptf_rebal"                         # the drawer's name
persistent_client = chromadb.PersistentClient(path="./chroma_ptf_rebal")  # the cabinet, saved in a folder
collection = persistent_client.get_or_create_collection(               # open the drawer (create it if new)
    collection_name, embedding_function=embedding_function
)
```

> **🧠 Analogy — cabinet, drawer, translator:**
> `PersistentClient(path=…)` is the **filing cabinet**, stored in the folder `./chroma_ptf_rebal` on disk — unlike the RAM notepad, it survives restarts. A **collection** is one drawer in it. The **embedding function** is a translator that writes every page's meaning as numbers, so "jumpy falling market" and "high volatility, declining trend" end up close together. `get_or_create` means re-running the cell won't fail.

**Step 7 · File the page.**

```python title="Python · lab_2c_episodic_memory.py · step 7"
collection.add(
    ids=["memory_1"],               # a unique name for this page
    documents=[document_text],      # the text → Chroma embeds it automatically with our translator
    metadatas=[metadata_clean],     # the folder labels
)
```

Why lists? Because `add` can file many pages at once. Position 0 of each list belongs together: `ids[0]` ↔ `documents[0]` ↔ `metadatas[0]`.

> **Watch out:**
> ⚠️ Same id twice?
>
> Re-running `add` with `"memory_1"` again won't create a second page — Chroma skips the existing id (with a warning). For a real journal, give every session a unique id, e.g. `f"memory_{datetime.now():%Y%m%d_%H%M%S}"`, or use `collection.upsert(...)` to overwrite on purpose.

**Step 8 · Days later: a new question searches the cabinet.**

```python title="Python · lab_2c_episodic_memory.py · step 8"
input_user_init = """Current Market Situation:
- Volatility Regime: low
- Market Trend: bullish
What rebalancing action should I take?"""

episodic_memory_recap = collection.query(
    query_texts=[input_user_init],   # a LIST: you could ask several questions at once
    n_results=3,                     # up to 3 closest pages per question
)
```

Chroma translates the question into a vector with the same translator, then returns the pages whose vectors are closest. The result's shape is where most people get lost:

episodic_memory_recap = { "ids": [ [ "memory_1", "memory_7", "memory_3" ] ], "documents": [ [ "Conversation Summary: ...", "Conversation Summary: ...", "..." ] ], "distances": [ [ 0.21, 0.35, 0.48 ] ], ← smaller = more similar "metadatas": [ [ {...}, {...}, {...} ] ], } outer list = one entry per question · inner list = matches, best first

🧪 Simulation

##### Decode `['documents'][q][r]` — click any cell

q=0 · "low vol, bullish — what now?"

q=1 · "client wants more dividends"

`episodic_memory_recap['documents'][0][0]` = the **best** matching page for question **0** ("low vol, bullish — what now?")

Its id: `episodic_memory_recap['ids'][0][0]` → `'memory_1'` · distance 0.21

This is the cell Lab 2C uses — first question, best match.

Imagine you passed **two** questions in `query_texts`. Each row is one question; each column is a match, best first.

**Step 9 · Paste the lesson into the new question and run with a fresh notepad.**

```python title="Python · lab_2c_episodic_memory.py · step 9"
session_ptf_rebal_2 = SQLiteSession("conversation_ptf_2")      # a brand-new, EMPTY notepad

input_user_with_memory = input_user_init + f"""
Here are relevant insights from past rebalancing episodes. Use them as guidance, not strict rules:
{episodic_memory_recap['documents'][0][0]}
Argue your proposition using past rebalancing episodes if needed.
"""

output_using_memory = await Runner.run(
    starting_agent=portfolio_agent,
    input=input_user_with_memory,
    session=session_ptf_rebal_2,
)
print(output_using_memory.final_output)
```

1. `episodic_memory_recap['documents'][0][0]` = "for my first (only) question, the best-matching journal page".
2. The `+` glues the old question and the memory block into one prompt: `input_user_with_memory`.
3. The session is **new and empty** — yet the agent knows yesterday's lesson, because we pasted it into the prompt. That is the entire trick of long-term memory.

💰 Why "guidance, not strict rules"?

Last time the market was *high-volatility and falling*; today it's *low-volatility and rising*. Copying last time's defensive moves would be wrong. The phrase tells the agent to learn from the pattern (e.g. "this client cares about risk control") without repeating the trade. Good advisors do exactly this.

> **💡 Making it production-ready:**
> - Use all top matches, not just one: `"\n---\n".join(episodic_memory_recap["documents"][0])`.
> - With only one page in the drawer, `n_results=3` simply returns that one page.
> - Write the journal page automatically when a session closes, with a unique id.

##### Variable cheat-sheet for Lab 2C

| Variable | Type | Lives in | What it holds |
| --- | --- | --- | --- |
| `session_ptf_rebal` | SQLiteSession | RAM | Today's notepad (gone on restart) |
| `conversation_history` | list of (role, text) | RAM | Clean copy of the chat |
| `conversation_history_string` | str | RAM | The chat as one text |
| `episodic_memory_prompt_template` | str with a `{conversation}` slot | RAM | Instructions for writing a journal page |
| `user_prompt` | str | RAM | Template with the chat filled in |
| `episodic_memory` | dict (5 keys) | RAM | The journal page as data |
| `document_text` | str | RAM → disk | The page as readable text (gets embedded) |
| `metadata_clean` | dict of str | RAM → disk | Folder labels |
| `collection` | Chroma collection | Disk `./chroma_ptf_rebal` | The drawer of all journal pages |
| `input_user_init` | str | RAM | The new day's question |
| `episodic_memory_recap` | dict of lists of lists | RAM | Search results, best first |
| `input_user_with_memory` | str | RAM | New question + best past page |
| `session_ptf_rebal_2` | SQLiteSession | RAM | The new, empty notepad |
