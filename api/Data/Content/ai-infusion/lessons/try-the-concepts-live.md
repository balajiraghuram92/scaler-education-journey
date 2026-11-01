# Try the concepts live

> **Lesson resources · Lesson 1 · simulators:**
> - [Watch the Class 1 recording](https://www.scaler.com/meetings/i/ai-infused-learning-1-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - ⬇ Download all (coming soon)

Class 1 · Interactive Simulators

## Try the concepts live

Five hands-on tools — one for each core idea from today's class. Click, drag, type, and see exactly what's happening under the hood.

🔤 Tokenizer 🌡️ Temperature 🔑 API Key 📤 API Round-trip 🪄 Self-Supervision 🔎 Summarizer

🔤 Simulator 1 of 6

## Tokenizer playground

LLMs don't read words — they read **tokens** (chunks roughly ¾ of a word). Type anything and watch it split. This is also how your API bill is calculated.

Live Tokenizer

type → watch it split into tokens

Your text

**Starting text in the box:** AI Engineering is surprisingly approachable!

**0** Tokens

**0** Characters

**$0** Cost @ $5/1M tok

Tip: common words = 1 token; rare or long words get chopped. **Rough rule: 1 token ≈ ¾ word ≈ 4 characters.** Try "unbelievableness" to see it split — then try "cat".

**Why tokens and not words?** A fixed vocabulary of ~100k sub-word chunks handles every word in every language — even ones invented tomorrow. A model trained on tokens can spell out `"ChatGPT"` even if it never saw that exact string in training. Example:  `"unbelievableness"` → un believ able ness

🌡️ Simulator 2 of 6

## Next-token & temperature

Given a prompt, the model scores every possible next token with a probability. **Temperature** reshapes those scores — low = focused and safe, high = creative and surprising. Drag the slider and see the probabilities shift.

Live Next-token probabilities

prompt: "I love building things in ___"

Temperature

**0.7** balanced

70

> **💡:**
> **This is a real engineering choice**
>
> A support chatbot → temperature ≈ 0.2 (consistent). A creative writing tool → temperature ≈ 1.0 (varied). You set this on day one of any real project.

🔑 Simulator 3 of 6

## Getting your API key

An API key is a secret password that lets your code use OpenAI's models. You pay only for what you use — cents for this class. Click through the flow:

🔑 OpenAI Platform platform.openai.com/api-keys

Sign in, add a little credit under *Billing*, then create a key:

+ Create new secret key

your key will appear here…

> **Watch out:**
> ⚠️ Copy it now — OpenAI shows a secret key only once. Never share it or commit it to GitHub.

Then create a `.env` file in your project folder: `OPENAI_API_KEY=sk-proj-xxxxxxxx…`

> **🔐:**
> **The one habit that saves careers**
>
> Add `.env` to your `.gitignore`. Leaked keys are found by bots in minutes and can rack up real bills.

📤 Simulator 4 of 6

## Anatomy of one API round-trip

When your code calls an LLM, it sends a request to a server and waits for a response — just like fetching the weather, except the reply is intelligence. Press send and watch the journey:

Live Anatomy of one API round-trip

press send → watch it travel

🧑‍💻

**Your app**

➜

🧠

**LLM model**

**Reply shown after you press send:** "Sip filter coffee on an MTR rooftop and watch the city wake up — Bangalore's best 10-minute holiday. ☕"

> **💡:**
> **The golden rule**
>
> Never paste your API key into code — it's a password to your wallet. Keep it in a `.env` file on the server side only.

🪄 Simulator 5 of 6

## Self-supervision: fill in the blank

This is how GPT learned — billions of times. A word is hidden; the model guesses. The answer is already in the text, so the internet becomes its own teacher. Try being the model:

The barista handed me a hot cup of ______.

Pick the word you think fills the blank.

**If you pick "coffee":** ✅ Exactly! And to "know" that, the model quietly learned context, grammar & the world. **That's self-supervision.**

**If you pick "tea":** ☕ Reasonable! "tea" works too — the model learns there are *several* plausible answers, each with a probability (remember temperature?).

**If you pick "bicycle" or "sadness":** 😅 Not quite — but every wrong guess is how the model *learns*. Billions of these corrections and it gets surprisingly good.

> **🤯:**
> **Why this is the whole secret**
>
> To guess "coffee", the model quietly learned grammar, context, what baristas do, and what fits in a cup. *Understanding emerges as a side-effect of getting very good at fill-in-the-blank.*

🔎 Simulator 6 of 6

## AI Website Summarizer — live demo

This is the app you built today. Pick a sample site (or paste your own text), choose a personality, and hit Summarize. Notice how changing the personality prompt completely changes the output — that's prompt engineering.

🔎 **AI Website Summarizer** live demo

Pick a sample "website"

…or paste any article text

Paste a paragraph or article here and hit Summarize…

Personality (the system prompt)

Summary

Your summary will appear here…

⚙️ This demo summarizes *in your browser* so it runs with no API key. Your real `app.py` sends the text to GPT for a smarter, full-sentence summary — but the shape and the personality switch are exactly what you see here.

**Sample "website" · 🚀 Startup site:**

NimbusPay — Payments that just work. NimbusPay is a payments platform built for small Indian businesses who are tired of clunky tools and hidden fees. Accept UPI, cards, and wallets with a single integration that takes ten minutes to set up. Our flat 1% fee means no surprises at the end of the month. NimbusPay also gives you a real-time dashboard so you can see every transaction as it happens. Over 12,000 shops already use NimbusPay to get paid faster. We just launched instant settlements, so your money reaches your bank account the same day instead of waiting three days. Sign up today and your first month is completely free.

**Sample "website" · 📰 News article:**

Governments race to regulate AI as adoption surges. Lawmakers around the world are scrambling to write rules for artificial intelligence as the technology spreads into hospitals, banks, and classrooms. Supporters say clear regulation will build public trust and prevent harm. Critics worry that heavy rules could slow innovation and hand an advantage to larger companies who can afford compliance. A new draft framework focuses on transparency, requiring companies to disclose when content is AI-generated. It also demands that high-risk systems, such as those used in hiring or medicine, be tested for bias before launch. Industry groups have asked for more time to adapt.

**Sample "website" · ✍️ Personal blog:**

My journey from teacher to AI engineer. Three years ago I had never written a line of Python. I was a high-school teacher who felt stuck and curious about the AI everyone kept talking about. I started small: one tiny project every weekend, even when they barely worked. The first thing I built was a tool that summarized news articles for my students. It was ugly, but it worked, and that little win changed everything. I kept shipping projects and sharing them online, and slowly people started noticing. Last month I started my first job as an AI engineer at a startup. The lesson: you do not need permission or a perfect plan — just build small things often and share them.

**Personality, and the opening and closing lines each one gives the summary:**

| Personality | Opening line | Bottom-line label |
|---|---|---|
| 🙂 Friendly | Here's the gist, in plain English: | In short: |
| 😏 Snarky | Fine, I read it so you don't have to: | The honest TL;DR: |
| 🧒 Like I'm 5 | Okay, imagine I'm explaining this to a 10-year-old: | So basically: |
| 💼 Professional | Executive summary: | Bottom line: |

**When the box is empty:** Paste some text or pick a sample first.

**When the text is too short:** Hmm, that text was too short to summarize.

**Footer under every summary:** ↳ in your real app, GPT writes this — richer &amp; in full sentences

AI Engineering · Class 1 — Interactive Simulators  ·  Scaler Academy
