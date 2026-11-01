# You already did the hard part

> **Lesson resources · Lesson 2 · LangChain & your first agent:**
> - [Watch the Class 2 recording](https://www.scaler.com/meetings/i/ai-infused-learning-2-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Class-2-AI-infusion.zip)

AI **Engineering** · Class 2

Class 2 · 100% Hands-On · Build Your First Agent

#### Today your AI stops talking and starts *doing*.

Class 1: you talked to a model. Class 2: you give it **hands**. You'll meet LangChain, snap your first chain together, then build an **agent that decides — on its own — when to use a tool.** Watch it happen live on the right. 👉

**Hero chat (plays on load):**

- **Assistant:** The shoes are ₹799! Anything else? 🙂
- **Assistant:** I can look up any item's price — I decide when to check the database myself. 😎

🧭 3 ways to steer a model 🔗 LangChain, hands-on 🤖 A real tool-using agent 🎮 "Tool or No Tool?" game 📣 Ship agent #1 today

**Scaler Academy** — type along. Every code block has 📋 Copy; every demo is clickable.

🛍️ Smart Shop Assistant live

10-second recap

## ↺ You already did the hard part

Called an LLM with the OpenAI library system / user / assistant messages Key safely in `.env` Shipped a Summarizer + an LLM Arena

> **🛠️:**
> **Today's deal — minimal slides, maximum doing**
>
> Everything today is the *same OpenAI call you already know*, organised more cleverly. Keep your Class 1 folder open; we build directly on top of it.

Plan for today

## ⏱ Our Class 2 flight plan

0:00

**Recap + 3 ways to steer a model**

Warm-up, prompting vs RAG vs fine-tuning

0:15

**LangChain: the new words, in plain English**

Template · model · parser — what each one IS, before any code

0:35

**Build your first chain**

Snap-it-together builder, then the real code, line by line

1:00

**Memory**

Why models forget & how LangChain remembers — decoded

1:10

**Your first tiny agent**

One tool, line by line, + watch the message list grow

1:40

**🎮 "Tool or No Tool?" game**

Prove you can think like the agent

1:50

**Project: Smart Shop Assistant**

Chat UI + public link

2:15

**Ship it to LinkedIn**

Caption + post — today 🎉

2:25

**Wrap & what's next**

Homework + the road ahead (ends ~2:30)

Block 9 · ~5 min · the map

## 9 3 ways to make a model do what you want

Before we build: the entire field of AI engineering boils down to **three** ways of steering a pre-trained model. You'll live in the first, visit the second soon, and almost never need the third.

✍️

**1. Prompting**

Just *tell* it clearly. Free, instant, no training. **90% of real work lives here** — including everything today.

📚

**2. RAG**

Hand it *your* documents at question-time so it answers from real data. A coming class.

🎓

**3. Fine-tuning**

Actually re-train on examples. Powerful, costly, rarely needed. Reach for it last.

> **🧭:**
> **Why this matters today**
>
> Chains, tools, agents — it's all still **option 1, organised cleverly**. Nothing new to fear. Let's build.

Block 10 · ~35 min · hands-on

## 10 LangChain: snap it together

In Class 1 you called the API by hand — perfect for one call. The moment you want **reusable prompts, multi-step pipelines, and memory**, you'd be rebuilding the same plumbing forever. **LangChain is that plumbing, pre-built.**

> **🧰:**
> **One-line intuition**
>
> The raw OpenAI call is a Lego brick. LangChain is the box of connectors that snaps bricks into machines.

##### Install it

```pseudo title="bash"
RUN pip install langchain langchain-openai   // download the packages into your Python
```

```python reveal
$ pip install langchain langchain-openai
```

bash

#### First: the 3 new words, in plain English

LangChain code uses three names that look scary. They aren't. Read these *before* we touch code — each one is a thing you already understand:

ChatPromptTemplate **= a prompt with blanks**

A normal prompt where some parts are left as `{blanks}` to fill in later. Like a wedding-invite template: "Dear `{name}`, join us on `{date}`". Write once, reuse for every guest.

say it as: "my reusable prompt"

ChatOpenAI **= the model, in a LangChain wrapper**

The exact same GPT you called in Class 1 — just wrapped so it can snap onto other LangChain pieces. Same `model=`, same `temperature=`.

say it as: "the model"

StrOutputParser **= unwraps the answer**

The model doesn't return plain text — it returns a *package* (text + metadata like token counts). This piece opens the package and hands you just the string. ("Str" = string, i.e. plain text.)

say it as: "give me just the text"

> **🗣️:**
> **Why is it called "Chat"PromptTemplate?**
>
> Because it builds prompts in the **chat format you already know** from Class 1 — system / user / assistant messages. Same grammar, now reusable.

#### Feel a template (before coding one)

This is all a template is — blanks you fill. Pick values and watch the final prompt assemble. The dict you pass to LangChain (`{"tone": "witty", ...}`) is just "here's what goes in each blank":

Template:  Write a {tone} {length} post about {topic}

tone

length

topic

```
chain.invoke({"tone": "witty", "length": "short", "topic": "AI agents"})
→ final prompt sent to the model:
Write a witty short post about AI agents.
```

#### What does the model actually return? (the parser's job)

Here's the bit nobody explains. When the model replies, you don't get plain text — you get a **package called an `AIMessage`** with the text inside it, plus bookkeeping. Press the button to see the package, and what the parser does to it:

Live sim Open the package

why StrOutputParser exists

AIMessage ← the package

content: "Anthropic builds safe AI…"

tokens_used: 213

model: "gpt-4o-mini"

finish_reason: "stop"

➜ 🧹 parser ➜

"Anthropic builds safe AI…" just the text. ready to print, show in Gradio, or save.

📦 Ask the model → open the package

Without the parser you'd write `response.content` by hand every time (in Class 1 it was `response.choices[0].message.content` — remember that mouthful?). The parser does it for you, forever.

#### Now build the chain — literally

A chain is the three pieces joined by `|` (the pipe — read it as **"then"**): prompt *then* model *then* parser. Click the pieces in the right order, then run data through:

Live sim Chain builder

click pieces in order, then run

your chain assembles here… (hint: what comes first?)

**Chain builder hints (shown when a piece goes in the wrong slot):**

- The prompt comes first — it shapes the request.
- The model goes in the middle — it does the thinking.
- The parser comes last — it cleans the output into plain text.

**Chain builder run output:**

- 📝 prompt fills the blank → "Summarize this website: anthropic.com…"
- 🤖 model thinks… generates the summary
- 🧹 parser returns clean text → "Anthropic builds safe AI systems, including Claude…" ✅

#### The same chain, in real code — decoded line by line

Rebuilding your Class 1 summarizer the LangChain way. The numbered comments match the decoder below — nothing here is mystery code:

```pseudo title="summarizer_langchain.py"
LOAD every KEY=value line from .env into the environment
CREATE prompt = a reusable prompt with a {website} blank, asking for a short, friendly summary
CREATE model = the gpt-4o-mini chat model, with temperature 0.3   // focused, not wildly creative
CREATE parser = a step that keeps only the text of the reply
CREATE chain = prompt, then model, then parser

DEFINE summarize(url):
    SET page = fetch_website_contents(url)   // reuse the Class 1 scraper
    RUN chain with website = page
    RETURN the summary text

PRINT summarize(the anthropic.com URL)
```

> **Imported:**
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the same GPT model from Class 1, wrapped so LangChain can use it.
> - `ChatPromptTemplate` from `langchain_core.prompts`, package langchain-core: builds the reusable prompt with the `{website}` blank.
> - `StrOutputParser` from `langchain_core.output_parsers`, package langchain-core: opens the model's reply and keeps just the text.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file into the environment.
> - `fetch_website_contents` from `scraper`, your Class 1 file: gets the text of the website to summarize.

```python reveal title="summarizer_langchain.py"
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from scraper import fetch_website_contents   # reuse Class 1's scraper
load_dotenv()

prompt = ChatPromptTemplate.from_template(            # ①
    "Give a short, friendly summary of this website:\n\n{website}")

model  = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)   # ②

parser = StrOutputParser()                             # ③

chain = prompt | model | parser                        # ④

def summarize(url):
    return chain.invoke({"website": fetch_website_contents(url)})   # ⑤

print(summarize("https://anthropic.com"))
```

🔍 decoder — what each numbered line does

①

`from_template(...)` turns my text into a **reusable prompt**. The `{website}` part is the blank — it will be filled in later, just like the playground above.

②

The **same model from Class 1**, wrapped for LangChain. `temperature=0.3` = mostly focused (summaries shouldn't be wildly creative).

③

The **package-opener** you just saw in the animation: takes the model's `AIMessage` package, hands back plain text.

④

The pipe `|` means **"then"**. Read aloud: "the prompt, *then* the model, *then* the parser." Data flows left → right, exactly like the builder.

⑤

`invoke` means **"run it"**. The dict `{"website": ...}` says which blank gets what — the key `"website"` matches the `{website}` blank by name.

✨

**The unlock**

`chain` is now a **reusable building block**. New task? Swap the template. Different model? Swap line ②. Hindi summaries? Add one word to the prompt. That composability is LangChain's entire point.

#### Bonus piece — Memory (decoded too)

Class 1 truth: models forget everything between calls. The fix is simple — **re-send the old messages every time**. LangChain gives that a tidy home. Two tiny new words first:

HumanMessage / AIMessage **= labelled chat bubbles**

Just a way to store "the human said X" and "the AI replied Y" — the same user/assistant roles from Class 1, as Python objects.

MessagesPlaceholder **= a parking spot for history**

A blank in your prompt that holds *a list of past messages* instead of one word. "Insert the whole conversation so far, right here."

```pseudo title="memory_demo.py"
CREATE prompt = a system message "You are a friendly tutor.", then a history placeholder, then the human message "{question}"
CREATE chain = prompt, then model   // model is the ChatOpenAI from the summarizer above
SET history = [user says "My name is Aarav.", AI replies "Hi Aarav!"]
PRINT the content of chain run with history and question "What's my name?"
// in a chat, the history must be re-sent on every call. The model keeps nothing itself.
```

> **Imported:**
> - `ChatPromptTemplate` from `langchain_core.prompts`, package langchain-core: builds the prompt from a list of messages.
> - `MessagesPlaceholder` from `langchain_core.prompts`, package langchain-core: a slot that holds the whole past conversation.
> - `HumanMessage` from `langchain_core.messages`, package langchain-core: a stored user message, here "My name is Aarav."
> - `AIMessage` from `langchain_core.messages`, package langchain-core: a stored assistant reply, here "Hi Aarav!"

```python reveal title="memory_demo.py"
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly tutor."),     # ① personality, like Class 1
    MessagesPlaceholder("history"),              # ② past turns park here
    ("human", "{question}"),                     # ③ the new question
])
chain = prompt | model

history = [HumanMessage("My name is Aarav."), AIMessage("Hi Aarav!")]
print(chain.invoke({"history": history, "question": "What's my name?"}).content)
# → "Your name is Aarav."  ✅ it "remembered" — because WE re-sent the history
```

> **💡:**
> **De-mystify this for them**
>
> The model didn't magically remember. **We re-sent the old messages**, and the placeholder slotted them in. All "chatbot memory" everywhere is exactly this trick. (One thing: this invoke returns the *package* — that's why we wrote `.content`. Add `| parser` to the chain and you wouldn't need it. See how the pieces connect?)

> **🎙️:**
> **Speaker note**
>
> Run the summarizer live and change the template in front of them ("now make it snarky"). The target feeling: *"oh — it's just my Class 1 code, tidied up."*

Block 11 · ~30 min · the leap

## 11 Your first (tiny) agent

Everything so far *talks*. An **agent** is a model with a **tool** and the freedom to **decide when to use it**. We'll build the smallest one possible — a shop assistant with exactly one skill: looking up real prices.

agent = LLM + tool + loop

The model thinks "do I need a tool here?" → if yes, calls it → reads the result → answers. Nobody hard-codes *when*. **That decision is the entire difference between a chatbot and an agent.**

> **🧮:**
> **Why tools?**
>
> LLMs are great with language, terrible with facts they don't have — today's price, live stock, exact math. A tool lets the model *fetch truth* instead of guessing. Tools cure "confident but wrong."

#### Our shop's "database" (kept deliberately tiny)

👟 shoes — **₹799**

🧢 hat — **₹399**

🎒 bag — **₹1420**

🩳 shorts — **₹1299**

👖 pants — **₹1699**

##### Step 1 — the tool is just a Python function

```pseudo title="agent.py · part 1"
LOAD every KEY=value line from .env into the environment
CREATE client = the OpenAI connection, which reads the key from the environment
SET PRICES = shoes 799, hat 399, bag 1420, shorts 1299, pants 1699   // stands in for a database

DEFINE get_price(item):
    PRINT "tool called: get_price(item)"   // so you can see the tool run
    SET price = the PRICES entry for item in lowercase, or "unknown" if missing
    RETURN "₹" + price
```

> **Imported:**
> - `json` Python standard library: reads the model's tool request, which arrives as JSON text (used in part 3).
> - `OpenAI` from `openai`, package openai: the client that sends your messages to the model.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file into the environment.

```python reveal title="agent.py · part 1"
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()

PRICES = {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699}

def get_price(item):
    print(f"🔧 tool called: get_price({item})")     # so you SEE it happen
    return f"₹{PRICES.get(item.lower(), 'unknown')}"
```

Two tiny notes for the Python: `PRICES` is an ordinary dict standing in for a database, and `.get(item, 'unknown')` means "look it up, and if it's not there, say *unknown* instead of crashing." That's the entire tool — **any function you can write can become an agent's tool.**

##### Step 2 — describe the tool so the model knows it exists

The model can't see your Python. You hand it a **menu card describing the tool** — written as a dict (the nested braces look busy, but it's only four facts). Decoder below:

```pseudo title="agent.py · part 2"
SET tools = a list holding one tool card
    type: "function"
    name: "get_price"   // must match the Python function name
    description: "Get the price of a shop item the user asks about."   // the model reads this to decide when to use it
    parameters: one required text input called item
```

```python reveal title="agent.py · part 2"
tools = [{
    "type": "function",                                      # ①
    "function": {
        "name": "get_price",                                 # ②
        "description": "Get the price of a shop item the user asks about.",  # ③
        "parameters": {                                       # ④
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]
```

🔍 decoder — the menu card, four facts

①

**What kind of tool?** A function. (That's the only kind you'll use for a long time — just write this line as-is.)

②

**Its name** — must exactly match your Python function's name, so we can find it when the model asks for it.

③

**When to use it** — written for the *model* to read. This sentence is literally how the model decides whether to call your tool. Write it clearly!

④

**What inputs it needs** — one input called `item`, which is text (`"string"`), and it's `required`. That's all the nesting says.

> **✍️:**
> **The non-obvious insight**
>
> Line ③ is **prompt engineering in disguise**. A vague description ("does stuff with items") → the model misuses the tool. A clear one → it behaves. Your words steer the machine, even inside JSON.

##### Step 3 — the loop: think → maybe call tool → answer

```pseudo title="agent.py · part 3"
DEFINE agent(user_message):
    SET messages = [the user's message]
    ASK the model with messages and tools
    SET msg = the model's reply

    IF the model asked for a tool (msg.tool_calls) THEN
        ADD msg to messages
        FOR EACH call in msg.tool_calls:
            SET args = the call's arguments, decoded from JSON
            SET result = get_price(args["item"])   // our Python runs the tool, not the model
            ADD result to messages with role "tool"
        ASK the model again with all the messages
        SET msg = the new reply

    RETURN msg.content

PRINT agent("How much are the shoes?")       // the tool runs, the answer is ₹799
PRINT agent("Hi! What can you help with?")   // no tool, the model just chats
```

```python reveal title="agent.py · part 3"
def agent(user_message):
    messages = [{"role": "user", "content": user_message}]

    response = client.chat.completions.create(          # ① send message + tools menu
        model="gpt-4o-mini", messages=messages, tools=tools)
    msg = response.choices[0].message

    if msg.tool_calls:                                  # ② did it ask for a tool?
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)  # ③ read its request, run it
            result = get_price(args["item"])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        response = client.chat.completions.create(      # ④ send it all back → nice answer
            model="gpt-4o-mini", messages=messages)
        msg = response.choices[0].message

    return msg.content

print(agent("How much are the shoes?"))      # → tool fires → "₹799"
print(agent("Hi! What can you help with?"))   # → no tool → just chats
```

🔍 decoder — the loop, step by step

1

We send the user's message *plus our tools menu*. The model now knows a tool exists and may ask to use it.

2

`msg.tool_calls` = "did the model ask to run a tool?" If it did, this holds *which tool* and *with what input* — e.g. `get_price`, `item="shoes"`. If not, it's empty and we skip straight to the answer.

3

The model's request arrives as text, so `json.loads(...)` converts it into a Python dict we can read — then **we** run the real function. (Important: the model never runs code itself. It *asks*; your Python *does*.)

4

We append the tool's result to the conversation with `role: "tool"` (a third role, joining system/user/assistant!) and send everything back, so the model can write a friendly final answer using the real data.

#### Watch the conversation grow (this makes it click)

The whole agent is just **a list of messages getting longer**. Step through one question and watch each card get appended — this is exactly what your code's `messages.append(...)` lines do:

Live sim The messages list, live

"How much are the shoes?"

messages = [

]

Press ▶ to start. We begin with just the user's question.

**Card 1 · user:** "How much are the shoes?" — Step 1 — we start the list with the user's question, plus the tools menu on the side.

- **Card 2 · assistant (tool request):** → wants: get_price(item="shoes") — Step 2 — the model doesn't answer yet! It replies "please run get_price for shoes". We append that request to the list. (This is what msg.tool_calls holds.)
- **Card 3 · tool:** "₹799" — Step 3 — OUR Python runs get_price("shoes") and we append the result with the new role: "tool". The model never runs code — it asks, we do.
- **Card 4 · assistant (final):** "The shoes are ₹799! Anything else? 🙂" — Step 4 — we send the whole longer list back, and now the model writes a friendly answer using the real price. Done — that's one full agent loop!

✅ That's the entire agent: **a list that grows** — user → tool request → tool result → answer. Re-read the code; it will feel obvious now.

🤯

**`if msg.tool_calls` is the entire secret**

The model asked to run `get_price("shoes")` *on its own*. Give it ten tools and it picks among them. You now understand how Cursor, support bots, and every "AI agent" headline actually works — same pattern, bigger toolbox.

#### 🎮 Quick game: think like the agent

Before you trust the agent, prove you understand it. For each question, predict: **will the model call the tool or answer directly?** Get 5 in a row:

question 1 of 5

**Answer buttons:** 🔧 Calls the tool · 💬 Just answers

**Feedback after each answer:**

- **Q1 (Calls the tool):** A price question → the model needs real data → calls get_price("bag").
- **Q2 (Just answers):** Small talk — no facts needed. The model just answers.
- **Q3 (Calls the tool):** "Is the hat cheaper than the shorts?" — Comparing prices still needs the real numbers — it calls the tool (twice!).
- **Q4 (Just answers):** "What's the capital of France?" — Trick one! The model already knows this — our price tool can't help. No tool call.
- **Q5 (Calls the tool):** "I have ₹1500 — can I afford the pants?" — It must check the real price (₹1699) before answering. Tool call, then "not quite!"

**Final score:** 🏆 Perfect 5/5 — you think like an agent! · Final score: *N*/5 — solid! Replay for the streak?

> **🎙️:**
> **Speaker note**
>
> Play this as a class — hands up for tool vs chat before revealing. The "ooh" on question 4 (the trick one) is reliably the best moment of the session.

Block 12 · ~25 min · 🏁 THE BUILD
