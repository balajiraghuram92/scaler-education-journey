# Project: Smart Shop Assistant

## 12 Project: Smart Shop Assistant

Same `agent()` from Block 11 — we give it a face. Gradio has a ready-made **chat interface**, so this takes four lines:

```pseudo title="app.py"
DEFINE chat(message, history):   // Gradio passes in the new message and the chat so far
    RETURN agent(message)          // the same agent from Block 11

CREATE a chat window with chat as its function, titled "🛍️ Smart Shop Assistant"
RUN it with share on, so you also get a public link
```

> **Imported:**
> - `gradio` (as `gr`) third-party package, pip install gradio: builds the web chat page.
> - `agent` from `agent`, your own agent.py: the function from Block 11 that answers each message.

```python reveal title="app.py"
import gradio as gr
from agent import agent              # the function you just wrote

def chat(message, history):          # ① Gradio fills these two in for you
    return agent(message)

gr.ChatInterface(fn=chat, title="🛍️ Smart Shop Assistant").launch(share=True)  # ②
```

🔍 decoder

①

Gradio's chat box calls your function for you, handing it the user's new `message` and the chat `history` (a list of past turns). We only need the message today; *your homework hint:* pass `history` into the agent and it gains memory — exactly the trick from the memory section.

②

`ChatInterface` = a ready-made chat UI (bubbles, input box, send button) around any function. `share=True` = also give me a public link.

##### Run it

```pseudo title="bash — your project folder"
RUN pip install openai gradio python-dotenv   // install the packages, once
RUN python app.py   // start the app
// Gradio prints a local link and a public link. The public one is the shareable agent.
```

```python reveal
$ pip install openai gradio python-dotenv
$ python app.py

Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://shop-xyz.gradio.live   # ← your shareable agent!
```

bash — your project folder

**Ask a price question**

"How much are the pants?" — watch your terminal print `🔧 tool called: get_price(pants)`. Your agent used its tool!

**Then ask small talk**

"What's your return policy?" — no tool fires. It's *deciding*, not following a script.

**Record that contrast**

15 seconds: one tool question, one chat question, terminal visible. That's your LinkedIn clip.

#### Try the working agent 👇

A live, in-browser version with the real chat feel — typing dots, tool-call chips, the works. Watch *when* the 🔧 appears (and when it doesn't):

🛍️ **Smart Shop Assistant** live demo

Hi! I'm your shop assistant. Ask me the price of anything 🙂

**Another example prompt:** "Is the hat cheaper than the bag?"

**Shop bot replies:**

- **One item found:** The *item* are **₹price**. Anything else? 🙂
- **Several items:** *item*: **₹price** · *item*: **₹price** — So the **cheapest item** is the cheaper one!
- **Price question, unknown item:** 🔧 get_price(...) → unknown — Hmm, that item isn't in my shop. I've got shoes, hat, bag, shorts and pants!
- **No tool needed:** — no tool needed, answering directly — I'm your shop helper! Ask me any item's price and I'll look it up in the database. 🛍️

e.g. How much are the shoes?

**0** tool calls

**0** direct answers

⚙️ Simulated in-browser (keyword matching plays the "model") so it runs key-free. Your real `agent.py` lets GPT make that decision far more flexibly — same loop, same trace.

🏭 Industry spotlight · this IS how real agents work

##### One tool today → a toolbox tomorrow

Add tools for your database, email and calendar and this becomes a real assistant: "find my order, refund it, email the customer." Every production agent — coding agents included — is this exact loop with a bigger toolbox. You now own the core pattern.

Support bots Booking assistants Coding agents Ops automation

Block 13 · ~15 min · 📣 ship it

## 13 Ship your first agent to LinkedIn

"I built an AI *agent*" lands harder than "I built a chatbot" — because most people have no idea how simple the trick is. Post the clip, use this caption, and hit the big button below when you're live. 😄

You

Your Name

AI Engineering learner · now · 🌐

🤖 I built my first AI agent today — and it can actually *use a tool*. Ask it "how much are the shoes?" → it decides, on its own, to look up the price. Ask it anything else → it just chats. Nobody told it when to use the tool. It figured that out. That tiny decision (LLM + a tool + a loop) is the exact pattern behind Cursor, support bots, and every "AI agent" you've read about. It's so much simpler than it sounds. 🤯 Stack: Python + LangChain + one function + Gradio. Learning this hands-on with @Shivank Agrawal — an industry expert who builds real AI systems every day and makes it genuinely click. 🙌 Day 2 with @Scaler. What tool should I give my agent next? 👇 #AIEngineering #LLM #Agents #Python #BuildInPublic

👍 You and others💬 Comments↗ Repost

👉 Tag [linkedin.com/in/shivankagrawal](https://www.linkedin.com/in/shivankagrawal/) and @Scaler so we can reshare and boost your reach.

> **🔥:**
> **Two classes, two ships**
>
> You're officially "building in public." Recruiters notice consistency far more than one flashy post. Keep the streak alive.

Block 14 · ~10 min

**After clicking 🚀 I posted it!:** 🎉 Agent #1 is live. Welcome to building in public!

## 14 What you did & what's next

🧭

**3 ways to steer**

Prompting, RAG, fine-tuning — you'll mostly prompt.

🔗

**LangChain**

prompt | model | parser — chains you can snap together.

🤖

**Agents**

LLM + tool + loop. The model decides. You saw it.

🛍️

**You shipped**

A working tool-using agent, in public. 🎉

#### The road ahead (still hands-on)

→

**More tools (your homework)**

Add `check_stock(item)` or `apply_discount(item)` and watch the agent pick the right one. Post the clip!

→

**RAG — chat with your own PDFs**

The next big build: a model that answers from *your* documents.

→

**Multi-agent teams**

Several agents handing work to each other — once one agent feels easy.

> **📚:**
> **A note on theory**
>
> We're deliberately deferring the deep "how models are built" topics — attention, training, scaling — until you're comfortable building. They'll land as "*oh, that's why it works*" instead of abstract lecture.

#### Class 2 shipped 🎉

You wrote LangChain, built an agent that uses a tool on its own, and put it on the internet. Most people never get this far.

##### Before next class

Give your agent a SECOND tool and post a clip of it choosing between them.

AI Engineering · Class 2 — Hands-On: LangChain & Your First Agent Scaler Academy
