# Take Trip Buddy to where your friends already chat

## Take Trip Buddy to where your friends already chat

#### T15 Feature · Ask Trip Buddy from Slack or WhatsApp

Nobody plans a trip in a Gradio tab. The plan happens in the group chat. The good news: `run_agent(text) → text` is already the whole brain. A chat app only needs a thin **adapter** that receives a message, calls `run_agent`, and sends the reply back. The database, notebook, tools and ReAct loop don't change at all.

{{diagram:1}}

*One brain, many front doors. Gradio, Slack and WhatsApp are just different ways to deliver `run_agent`'s text. This is the same idea as an MCP or A2A wrapper from Week 1: keep the agent, change the transport.*

> **Note:**
> 💡 Using the MCP version (script 10)?
>
> Its `run_agent` is `async`. Import it from `trip_10_mcp_agent` instead and call `asyncio.run(run_agent(text))` in the adapters below. Everything else stays the same.

|  | Slack | WhatsApp |
| --- | --- | --- |
| **Library** | `slack_bolt` | `flask` + `twilio` |
| **How messages arrive** | Socket Mode: your script opens a connection to Slack, so it runs on a laptop with no public URL | A webhook: Twilio POSTs each message to a public URL (ngrok while you develop) |
| **Keys in .env** | `SLACK_BOT_TOKEN` (xoxb-…), `SLACK_APP_TOKEN` (xapp-…) | none to receive; Twilio signs each request (check it, see below) |
| **Free to try** | Any workspace where you can create an app | Twilio's WhatsApp Sandbox: each friend joins once with a code word |
| **Watch out** | Reply in a thread so the channel stays readable | Twilio waits 15 s for the reply and a message holds 1,600 characters |

##### Option A · Slack

1. At api.slack.com/apps, **create an app** from scratch in your workspace.
2. **Socket Mode**: turn it on and create an app-level token with `connections:write`. That is `SLACK_APP_TOKEN`.
3. **OAuth & Permissions**: add the bot scopes `app_mentions:read`, `chat:write` and `im:history`, then install the app. The Bot User OAuth Token is `SLACK_BOT_TOKEN`.
4. **Event Subscriptions**: subscribe to the bot events `app_mention` and `message.im`. Under **App Home**, allow messages in the Messages tab.
5. Invite the bot to your trip channel with `/invite @Trip Buddy`, run `uv run slack_bot.py`, and ask it something.

```pseudo title="slack_bot.py (suggested, next to script 08)"
LOAD SLACK_BOT_TOKEN and SLACK_APP_TOKEN from .env
IMPORT run_agent from trip_08_full_agent   // builds the DB and notebook; does not start Gradio
CREATE app = Slack Bolt App with the bot token

ON a message that mentions @Trip Buddy in a channel:
    SET question = the text without the "@Trip Buddy" tag
    REPLY in the message's thread with run_agent(question)

ON a direct message to the bot:
    IF it was sent by a bot THEN ignore it   // never answer yourself
    REPLY with run_agent(text)

START Socket Mode with the app token   // runs until you press Ctrl+C
```

```python reveal title="Python · slack_bot.py (suggested)"
"""
slack_bot.py: ask Trip Buddy from Slack.

Run next to trip_08_full_agent.py:
    uv add slack-bolt
    uv run slack_bot.py
.env needs SLACK_BOT_TOKEN (xoxb-...) and SLACK_APP_TOKEN (xapp-...).
"""
import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

# Importing builds the database, the notebook and the tools.
# Gradio only starts under `if __name__ == "__main__"`, so it stays off here.
from trip_08_full_agent import run_agent

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("app_mention")
def on_mention(event, say):
    """Someone wrote @Trip Buddy in a channel: answer in that message's thread."""
    question = re.sub(r"<@[A-Z0-9]+>\s*", "", event["text"]).strip()   # drop the @mention tag
    say(text=run_agent(question), thread_ts=event.get("thread_ts", event["ts"]))

@app.event("message")
def on_direct_message(event, say):
    """A direct message to the bot. Ignore bot messages, including our own replies."""
    if event.get("channel_type") == "im" and not event.get("bot_id") and event.get("text"):
        say(text=run_agent(event["text"]))

if __name__ == "__main__":
    print("Trip Buddy is listening on Slack (Ctrl+C to stop)...")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

##### Option B · WhatsApp (Twilio Sandbox)

1. In the Twilio console, open **Messaging → Try it out → Send a WhatsApp message**. Each friend sends the sandbox's `join <code-word>` message to its number once.
2. Run `uv run whatsapp_bot.py` (port 5000), then `ngrok http 5000` in a second terminal.
3. In the sandbox settings, set **When a message comes in** to `https://<your-ngrok-id>.ngrok-free.app/whatsapp`, method POST.
4. Message the sandbox number: *"We are 4 friends with ₹12,000 each. Can we do Goa for 3 nights?"*

```pseudo title="whatsapp_bot.py (suggested, next to script 08)"
IMPORT run_agent from trip_08_full_agent
CREATE app = Flask web app

ON POST /whatsapp:   // Twilio calls this for every incoming WhatsApp message
    IF the X-Twilio-Signature header is not valid THEN RETURN 403   // only Twilio may call
    SET question = the "Body" form field
    SET answer = run_agent(question), cut to 1,500 characters   // WhatsApp limit
    RETURN a TwiML reply containing answer   // Twilio sends it to the friend

START the app on port 5000   // expose it with: ngrok http 5000
```

```python reveal title="Python · whatsapp_bot.py (suggested)"
"""
whatsapp_bot.py: ask Trip Buddy on WhatsApp, through the Twilio Sandbox.

Run next to trip_08_full_agent.py:
    uv add flask twilio
    uv run whatsapp_bot.py          # then, in another terminal: ngrok http 5000
.env needs TWILIO_AUTH_TOKEN (to check that requests really come from Twilio).
"""
import os

from dotenv import load_dotenv
from flask import Flask, abort, request
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

from trip_08_full_agent import run_agent   # builds DB + notebook; Gradio stays off

app = Flask(__name__)
validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
MAX_CHARS = 1500   # a WhatsApp message via Twilio holds 1,600 characters

@app.post("/whatsapp")
def whatsapp():
    # Only Twilio can sign a request with your auth token. Behind ngrok, the URL
    # Twilio signed is the public https one, so rebuild it from the forwarded headers.
    url = request.url.replace("http://", "https://", 1) if request.headers.get("X-Forwarded-Proto") == "https" else request.url
    if not validator.validate(url, request.form, request.headers.get("X-Twilio-Signature", "")):
        abort(403)

    question = request.form.get("Body", "").strip()
    answer = run_agent(question) if question else "Ask me about a trip, or send: list"

    reply = MessagingResponse()
    reply.message(answer[:MAX_CHARS])
    return str(reply), 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(port=5000)
```

> **⚠️ Before you share the bot with friends:**
> - **Keys stay in `.env`.** Slack and Twilio tokens are passwords; never paste them into code or the group chat.
> - **Check who is calling.** The WhatsApp webhook is a public URL; the Twilio signature check is what stops strangers from spending your OpenAI credits.
> - **Slow answers.** A long ReAct run can pass Twilio's 15-second limit. For real use, reply "Planning…" at once and send the answer later with Twilio's REST API.
> - **Phone numbers are personal data.** Don't log them, and don't store chats you don't need.
> - **The sandbox is for testing.** A real WhatsApp number needs a WhatsApp Business account (through Twilio or Meta's Cloud API) and approved templates for messages the bot starts.

> **🧠 Same chef, new delivery apps:**
> The kitchen (`run_agent`) doesn't care whether an order came from the dine-in counter (Gradio), Swiggy (Slack) or Zomato (WhatsApp). Each delivery app needs its own rider, the adapter, who picks up the order and drops off the food. You add front doors without touching the recipe.

---

Own it

## Your project

#### T16 Milestones, stretch goals and rubric

| Milestone | Build | Done when… | Time |
| --- | --- | --- | --- |
| **M0 · Data** | project set up, script 01 | the JOIN table prints 3 places, and "PARIS" returns `None` | 20 min |
| **M1 · Meaning** | scripts 02 and 03 | the mountains question finds the hills tip; the money search returns only money tips | 40 min |
| **M2 · Planner** | script 04 | you've caught at least one run where the LLM's Manali number is not 20866.67 | 30 min |
| **M3 · Grounded** | script 05 | the RAG answer warns about July rain and landslides; you can say which tip it came from | 30 min |
| **M4 · Pipeline** | script 07 | Goa comes back GO with ₹200 left, Manali NOT YET with one suggested change, and chain 1 never changes a tool number | 40 min |
| **M5 · Trip Buddy** | script 08 | "list" shows 10 places; Hampi for 5 friends, 2 nights is ₹4,300; the ₹8,000 question returns the six places from the simulation | 1 h |
| **M6 · MCP by hand** | the MCP server and script 09 | all 7 steps print; `people = 0` comes back with `isError: True` | 40 min |
| **M7 · Trip Buddy + MCP** | script 10 | the same answers as script 08, the terminal shows `[mcp] call_tool` lines, and `/plan Hampi 5 2 6000` says it fits | 1 h |
| **M8 · In the group chat** | T15: `slack_bot.py` or `whatsapp_bot.py` | a friend asks from Slack or WhatsApp and gets the same answer as in Gradio | 1 h |

##### Stretch goals (pick two)

1. **S1 · Port it to AWS**: swap `ChatOpenAI` for Strands' `BedrockModel` and the hand-written loop for `Agent(model, tools=[...])`, as in [Lesson 1](/chapter/aws-agentic-ai-bootcamp/w1-lesson-1-your-first-agent/why-a-plain-llm-isn-t-enough). Compare the tool trail.
2. **S2 · The 10% buffer**: make `compute_trip_cost` also return `total_with_buffer` (the notebook's 10% rule) and judge `within_budget` on it. The agent must never say "fits" when the tool says it doesn't.
3. **S3 · Keep the notebook**: use `chromadb.PersistentClient(path=...)` and a SQLite file instead of `:memory:`, so tips and prices survive a restart.
4. **S4 · Remember the conversation**: pass Gradio's `history` (or the Slack thread) into `run_agent`, so "and for 3 nights?" knows you still mean Goa.
5. **S5 · Remember the group**: add long-term memory ([Lesson 3](/chapter/aws-agentic-ai-bootcamp/w1-lesson-3-agents-that-remember/why-agents-need-memory)), so "we're vegetarian and hate long bus rides" shapes every later plan.
6. **S6 · Test the maths**: plain `assert` s on the two calculators (Goa 11800, Manali 20866.67, 1 friend still needs 1 room) that run without an LLM.
7. **S7 · Your own place**: add a destination to all three tables and two tips of your own, then ask Trip Buddy about it.
8. **S8 · Share the server**: add `trip_mcp_server.py` to Claude Desktop or VS Code as a stdio MCP server, and plan a trip from there.
9. **S9 · A notebook resource**: move the travel tips into the server too, as a `trips://tips/{topic}` resource, so every MCP host gets them.

##### Rubric (100 points)

| Criterion | What earns full marks | Points |
| --- | --- | --- |
| Correct numbers | every cost comes from a tool; rooms always rounded up; matches the calculator above | 25 |
| Grounded advice | season and packing advice comes from retrieved tips, and the answer shows which ones | 20 |
| Retrieval quality | the right shelf (`where`) for the question; sensible `n` | 15 |
| Agent design | clear tool docstrings, tools that return errors instead of crashing, a step limit; works from a chat app | 15 |
| Honest answers | says "over budget" when it is, and "I don't have prices for that" for unknown places | 15 |
| Code quality | commented, small functions, the maths testable without an LLM | 10 |

---

Wrap-up

## What to remember

1. **A database holds the facts.** Two tables and a `JOIN`; `?` placeholders keep lookups safe.
2. **Embeddings turn meaning into numbers.** Unit-length vectors make the dot product the cosine similarity.
3. **A vector database is a library with shelves.** Search by meaning, filter by metadata; `retrieve()` is the heart of RAG.
4. **RAG = retrieve → augment → generate.** The context is just text pasted into the prompt, and it makes the answer specific.
5. **LLMs are bad calculators.** 3 friends need 2 rooms. Give the model tools and let Python do the maths.
6. **The agent loop is small.** Ask, run the requested tools, send the results back, repeat until there are no tool calls.
7. **Pipeline or agent.** Fixed steps: chain them yourself (script 07). Steps that depend on the question: let the model choose tools (script 08).
8. **MCP makes tools portable.** Tools (the LLM picks), resources (the app reads), prompts (the user picks); any MCP host can use them, and results are data, not instructions.
9. **One brain, many front doors.** Gradio, Slack and WhatsApp are thin adapters around the same `run_agent`.

Disclaimer

Places, guesthouses and prices are illustrative, made up for learning. Check real weather, prices and travel advice before you book.

**Trip Buddy** · Scaler AWS AI Bootcamp · Week 2 · Project 1 Illustrative data, for learning only. LLM wording varies run to run; the numbers come from code.
