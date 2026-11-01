# Your first 6 lines that talk to an AI

## 6 Your first 6 lines that talk to an AI

#### Step 0 — Get set up (do this once, ~10 min)

Before any code runs, three quick bits of plumbing. Don't worry — it's a one-time setup.

##### ① Install a code editor — Cursor or VS Code

You need one editor to write and run code. Both are free and work identically for this course — pick whichever you like:

> **🆚:**
> **Cursor vs VS Code — which one?**
>
> **VS Code** is the world's most popular editor (by Microsoft) — rock-solid and widely used. **Cursor** is built *on top of* VS Code with an AI assistant baked in. If you want AI help while coding, pick Cursor; if you want the classic standard, pick VS Code. *Either is totally fine — you only need one.*

a

**Download & install**

**Cursor:** go to `cursor.com` → Download.  **VS Code:** go to `code.visualstudio.com` → Download. Install like any normal app (Windows / Mac / Linux).

b

**Add the Python & Jupyter extensions**

Open your editor → click the *Extensions* icon on the left → search `Python` (by Microsoft) and `Jupyter` → Install both. (Same steps in Cursor and VS Code.)

c

**Open a notebook & pick the kernel**

Open a `.ipynb` file → click *Select Kernel* (top-right) → choose your Python environment. You run a cell with **Shift + Enter**.

##### ② Get your OpenAI API key

An API key is a secret password that lets your code use OpenAI's models (you pay only for what you use — cents for this class). Here's the flow, simulated — click through it:

🔑 OpenAI Platform platform.openai.com/api-keys

Sign in, add a little credit under *Billing*, then create a key:

+ Create new secret key

your key will appear here…

> **Watch out:**
> ⚠️ Copy it now — OpenAI shows a secret key only once. And never share it or commit it to GitHub.

🔁 Prefer free? You can skip this entirely and use **Ollama** (runs on your laptop, no key, same code) — we'll cover it next class.

##### ③ Put the key in a `.env` file (never in your code)

Create a file literally named `.env` in your project folder, and paste your key inside. Your code reads it from there — so the secret never appears in the code you share.

```pseudo title=".env"
// lines that start with # are comments and are ignored
SET OPENAI_API_KEY = your secret key   // one NAME=value line per setting
```

```python reveal title=".env"
# .env  — keep this file private! Add it to .gitignore
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

```pseudo title="load_key.py — read it in your code"
// one-time setup: pip install python-dotenv
CALL load_dotenv()   // read every KEY=value line in .env into the environment
```

> **Imported:**
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.

```python reveal title="load_key.py — read it in your code"
# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()                 # loads everything from .env

# now OpenAI() finds the key automatically — no key in your code 🎉
```

> **🔐:**
> **The one habit that saves careers**
>
> Add `.env` to your `.gitignore` so it's never uploaded to GitHub. Leaked keys get found by bots in minutes and can run up real bills. Secrets live in `.env`, never in code.

#### Now — the 6 lines that actually talk to the AI

With setup done, calling an LLM is just an **API call** — like fetching the weather, except the reply is intelligence. Here's the whole thing:

```pseudo title="first_call.py"
CALL load_dotenv()                // read .env into the environment
CREATE client = OpenAI()          // the client picks up the API key from the environment
SEND to client.chat.completions.create:
    model = "gpt-4o-mini"
    messages = [system: "You are a witty travel guide.", user: "Suggest one thing to do in Bangalore."]
PRINT the content of the first reply
```

> **Imported:**
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.
> - `OpenAI` from `openai`: the client class that sends requests to OpenAI's models.

```python reveal title="first_call.py"
# pip install python-dotenv
from dotenv import load_dotenv
# pip install openai
from openai import OpenAI
load_dotenv()                 # loads everything from .env

client = OpenAI()   # reads your API key from the environment

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a witty travel guide."},
        {"role": "user",   "content": "Suggest one thing to do in Bangalore."},
    ],
)
print(response.choices[0].message.content)

# now OpenAI() finds the key automatically — no key in your code 🎉
```

#### The 3 "roles" — the entire grammar of chat models

S

**system**

Sets the personality & rules — "You are a careful tutor. Never give the full answer." Written once, applies throughout.

U

**user**

What the human asks. The actual request.

A

**assistant**

The model's reply. To continue a chat, append it back and resend the whole list (remember: no memory!).

Live sim Anatomy of one API round-trip

press send → watch it travel

🧑‍💻

**Your app**

➜

🧠

**LLM model**

**Reply shown after you press send:** "Sip filter coffee on an MTR rooftop and watch the city wake up — Bangalore's best 10-minute holiday. ☕"

> **🔐:**
> **Golden rule**
>
> Never paste your API key into shared/public code — it's a password to your wallet. Keep it in a `.env` file or environment variable, on the server side only.

🏭 Industry spotlight · the model is swappable

##### Same code, different brains

Change one string — `"gpt-4o-mini"` → a Claude or open-source model — and your whole product runs on a different engine. There's even a **free, runs-on-your-laptop** option (Ollama) that uses this exact same code, just pointed at a local address. We'll meet it soon.

OpenAI · GPT Anthropic · Claude Google · Gemini Groq · Llama (free & fast) Ollama · free & local

#### Bonus: the *same* code on a free, blazing-fast model (Groq + Llama)

Don't want to add billing yet? **Groq** gives you a free API key and runs open models like Meta's **Llama** incredibly fast. Because Groq speaks the same "language" as OpenAI, you change just *two things* — the key and one line — and everything else stays identical:

```pseudo title="groq_call.py"
CALL load_dotenv()                          // read .env into the environment
SET api_key = environment variable GROQ_API_KEY
CREATE client = OpenAI(api_key, base_url)   // same client, pointed at the Groq server instead of OpenAI
SEND to client.chat.completions.create:
    model = "llama-3.3-70b-versatile"       // a free Llama model on Groq
    messages = [system: "You are a witty travel guide.", user: "Suggest one thing to do in Bangalore."]
PRINT the content of the first reply
```

> **Imported:**
> - `os` Python standard library: gives access to environment variables, here `GROQ_API_KEY`.
> - `OpenAI` from `openai`: the same client class as before, here pointed at Groq's address.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.

```python reveal title="groq_call.py"
# pip install openai   (yes — the same library!)
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# point the SAME client at Groq instead of OpenAI 👇
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",        # a free Llama model on Groq
    messages=[
        {"role": "system", "content": "You are a witty travel guide."},
        {"role": "user",   "content": "Suggest one thing to do in Bangalore."},
    ],
)
print(response.choices[0].message.content)
```

where to get the key

Sign up free at `console.groq.com` → *API Keys* → Create key, then add it to your `.env` as `GROQ_API_KEY=gsk_...`. **Notice how little changed** — just the key, the `base_url`, and the model name. The whole point of AI Engineering: the brain is swappable.

Block 7 · ~30 min · 🏁 THE BUILD

## 7 Mini-Project: AI Website Summarizer

Time to build. Our app: **give it any web page URL → it reads the page and hands you a clean summary.** The Reader's Digest of the internet. It's simple, genuinely useful, and exactly the kind of thing that makes a great first LinkedIn post.

#### How it works — the whole app in one picture

🔗

**URL** user pastes it

➜

🕷️

**Scrape** grab page text

➜

🧩

**Prompt** text + instructions

➜

🧠

**LLM** summarise

➜

📄

**Summary** shown in UI

Five boxes. That's a real AI product. Let's write each piece.

#### Step 1 — Grab the page text (the "scraper")

> **📦:**
> **Treat this one as a black box**
>
> You do **not** need to understand a single line below. This is plain web-scraping (not AI), and there's a library for it. All it does: *take a URL → return the page's readable text as a string.* That's it. Copy it, trust it, move on — the AI magic is in Step 2.

```pseudo title="scraper.py"
SET HEADERS = browser-style details such as User-Agent   // makes the request look like a normal browser
DEFINE fetch_website_contents(url):
    IF url does not start with http or https THEN
        SET url = url with "https" added in front   // the user forgot the scheme
    TRY
        Get the page at url, using HEADERS, waiting at most 15 seconds
        raise an error if the HTTP status shows a failure
    ON ERROR (any request problem)
        RETURN "Could not fetch the website. Error: " + the error
    SET soup = the page's HTML, parsed
    SET title = the page title, or "No title found"
    Remove the script, style, nav, footer, header, img and input tags
    SET text = all remaining text, one piece per line, trimmed
    RETURN "Title: " + title, then "Page contents:" and the text
```

> **Imported:**
> - `requests` third-party package `requests`: sends the request that downloads the web page.
> - `BeautifulSoup` from `bs4`, package beautifulsoup4: parses the page's HTML so the code can read its title and text.

```python reveal title="scraper.py"
# pip install requests beautifulsoup4
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_website_contents(url):
    # add scheme if the user forgot it
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Could not fetch the website. Error: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string if soup.title else "No title found"

    for tag in soup(["script", "style", "nav", "footer", "header", "img", "input"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    return f"Title: {title}\n\nPage contents:\n{text}"
```

#### Step 2 — The brain (prompt + LLM call)

```pseudo title="summarizer.py"
CALL load_dotenv()                  // read .env into the environment
CREATE client = OpenAI()            // the client picks up the API key from the environment
SET system_prompt = the instructions: a short, friendly summary, ignore navigation menus, respond in markdown
DEFINE summarize(url):
    SET website = fetch_website_contents(url)
    SEND to client.chat.completions.create:
        model = "gpt-4o-mini"
        messages = [system: system_prompt, user: "Summarize this website:" + website]
    RETURN the content of the first reply
```

> **Imported:**
> - `OpenAI` from `openai`: the client class that sends requests to OpenAI's models.
> - `load_dotenv` from `dotenv`, package python-dotenv: reads the `.env` file and copies each line into the environment.
> - `fetch_website_contents` from `scraper`, your own file scraper.py: the function from Step 1 that returns the page text.

```python reveal title="summarizer.py"
from openai import OpenAI
from dotenv import load_dotenv
from scraper import fetch_website_contents

load_dotenv()          # <-- this reads your .env file
client = OpenAI()

system_prompt = """You analyze the contents of a website and
give a short, friendly summary. Ignore navigation menus.
Respond in markdown."""

def summarize(url):
    website = fetch_website_contents(url)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user",   "content": f"Summarize this website:\n\n{website}"},
        ],
    )
    return response.choices[0].message.content
```

> **🪄:**
> **The "wow" lever — change the personality**
>
> Edit one line of the `system_prompt` — "give a *snarky, humorous* summary" or "explain it to a 10-year-old" or "respond in Hindi" — and the whole app behaves differently. **That's prompt engineering, and you just learned it.** Try the personality buttons in the live demo below 👇

#### Step 3 — The face (Gradio = a web app in 4 lines)

Nobody will run your Python script. **Gradio turns your function into a shareable web app** — no HTML, no CSS, no JavaScript:

```pseudo title="app.py"
// one-time setup: pip install gradio
CREATE a web page with gr.Interface:
    fn = summarize                  // your function runs each time the user submits
    inputs = one text box labelled "Website URL"
    outputs = a Markdown box labelled "Summary"
    title = "🔎 AI Website Summarizer"
RUN launch with share on            // also creates a public link you can send to others
```

> **Imported:**
> - `gradio` (as `gr`) third-party package `gradio`: builds the web page and its input and output boxes from Python.
> - `summarize` from `summarizer`, your own file summarizer.py: the function that does the summarising.

```python reveal title="app.py"
# pip install gradio
import gradio as gr
from summarizer import summarize

gr.Interface(
    fn=summarize,                                  # your function
    inputs=gr.Textbox(label="Website URL"),
    outputs=gr.Markdown(label="Summary"),
    title="🔎 AI Website Summarizer",
).launch(share=True)   # share=True → a public link you can post! 🎉
```

#### Step 4 — Run it on your machine 👇

Save the three files (`scraper.py`, `summarizer.py`, `app.py`) and your `.env` in one folder. Then open the terminal in Cursor (*Terminal → New Terminal*) and run:

```pseudo title="bash — your project folder"
RUN pip install openai gradio requests beautifulsoup4 python-dotenv   // install everything you need, one time
RUN python app.py   // launch the app
// Gradio then prints two links: a local one (127.0.0.1, port 7860) and a public *.gradio.live one to share
```

```python reveal
# 1. install everything you need (one time)
$ pip install openai gradio requests beautifulsoup4 python-dotenv

# 2. launch the app
$ python app.py

# 3. Gradio prints two links:
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://a1b2c3.gradio.live   # ← share this!
```

bash — your project folder

**Open the local link**

Click `http://127.0.0.1:7860` — your app opens in the browser. This is your app running on *your* computer.

**Paste a URL and hit submit**

Try a blog or news site. In a second or two, the summary appears. 🎉 You just used your own AI app.

**Share the public link**

The `*.gradio.live` link works for anyone for ~72 hours — perfect to send a friend or screen-record for LinkedIn. (For a permanent home, deploy free to Hugging Face Spaces — a one-class topic for later.)

**Stop it anytime**

Press `Ctrl + C` in the terminal to shut the app down.

🐞 If you hit an error, 90% of the time it's a missing `pip install` or a key not loaded from `.env` — check those two first.

#### Try the working version right here

Below is a **live, in-browser version** of exactly that app. Pick a sample site (or paste your own text), choose a personality, and hit summarize:

🔎 **AI Website Summarizer** live demo

Pick a sample "website"

…or paste any article text

Paste a paragraph or article here and hit Summarize…

Personality (the system prompt)

Summary

Your summary will appear here…

⚙️ This demo summarizes *in your browser* (a simple method) so it runs with no API key. Your real `app.py` sends the text to GPT for a smarter summary — but the shape, the flow, and the personality switch are exactly what you see here.

**Sample "website" · 🚀 Startup site:**

NimbusPay — Payments that just work. NimbusPay is a payments platform built for small Indian businesses who are tired of clunky tools and hidden fees. Accept UPI, cards, and wallets with a single integration that takes ten minutes to set up. Our flat 1% fee means no surprises at the end of the month. NimbusPay also gives you a real-time dashboard so you can see every transaction as it happens. Over 12,000 shops already use NimbusPay to get paid faster. We just launched instant settlements, so your money reaches your bank account the same day instead of waiting three days. Sign up today and your first month is completely free.

**Sample "website" · 📰 News article:**

Governments race to regulate AI as adoption surges. Lawmakers around the world are scrambling to write rules for artificial intelligence as the technology spreads into hospitals, banks, and classrooms. Supporters say clear regulation will build public trust and prevent harm. Critics worry that heavy rules could slow innovation and hand an advantage to larger companies who can afford compliance. A new draft framework focuses on transparency, requiring companies to disclose when content is AI-generated. It also demands that high-risk systems, such as those used in hiring or medicine, be tested for bias before launch. Industry groups have asked for more time to adapt. The debate is expected to continue for years as the technology keeps evolving.

**Sample "website" · ✍️ Personal blog:**

My journey from teacher to AI engineer. Three years ago I had never written a line of Python. I was a high-school teacher who felt stuck and curious about the AI everyone kept talking about. I started small: one tiny project every weekend, even when they barely worked. The first thing I built was a tool that summarized news articles for my students. It was ugly, but it worked, and that little win changed everything. I kept shipping projects and sharing them online, and slowly people started noticing. Last month I started my first job as an AI engineer at a startup. The lesson I keep repeating to anyone who will listen: you do not need permission or a perfect plan, you just need to build small things often and share them.

**Personality, and the opening and closing lines each one gives the summary:**

| Personality | Opening line | Bottom-line label |
|---|---|---|
| 🙂 Friendly | Here's the gist, in plain English: | In short: |
| 😏 Snarky | Fine, I read it so you don't have to: | The honest TL;DR: |
| 🧒 Explain like I'm 5 | Okay, imagine I'm explaining this to a 10-year-old: | So basically: |
| 💼 Professional | Executive summary: | Bottom line: |

**When the box is empty:** Paste some text or pick a sample first.

**When the text is too short:** Hmm, that text was too short to summarize.

**Footer under every summary:** ↳ in your real app, GPT writes this — richer &amp; in full sentences

🏭 Industry spotlight · you just built a real product category

##### Summarization quietly runs the business world

Summarizing news, earnings calls, support threads, legal contracts, research papers, meeting transcripts — it's one of the most-used AI features in companies today. Swap "website" for "PDF", "email thread", or "YouTube transcript" and you've got a dozen more apps from the same code.

News digests Earnings-call summaries Meeting notes Contract review Research papers

Block 8 · ~15 min · 📣 ship it
