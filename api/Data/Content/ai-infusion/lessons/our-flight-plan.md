# Our flight plan

> **Lesson resources · Lesson 1 · Build & ship your first AI app:**
> - [Watch the Class 1 recording](https://www.scaler.com/meetings/i/ai-infused-learning-1-2/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Class-1-AI-infusion.zip)

AI **Engineering** · Class 1

Class 1 · Beginner Friendly · Build & Ship Today

#### By the end of *today*, you'll have shipped a *real* AI app.

No PhD. No math. No machine learning background. In one class you'll understand how AI *actually* works — and you'll build a real, shareable **AI Website Summarizer** — then post it on LinkedIn. Let's go.

🧠 How LLMs really work 🪄 The "fill-in-the-blank" trick 🛠️ Your first 6 lines of code 🎛️ A real Gradio app 🔎 AI Website Summarizer 📣 A LinkedIn post you're proud of

**The promise of Class 1**

You walk in curious. You walk out having **built and shared a working AI app** — ahead of 99% of people who only *talk* about AI.

**Scaler Academy**  —  everything below is interactive. **Click the simulators** as we go.

The plan for today

## ⏱ Our flight plan

We climb gently — a "wow" at every step, then we build. Timings are a guide; the ★ moment is when *you* ship.

0:00

**Why AI exploded right now**

70 years of AI, compressed — and why one person can suddenly build this

0:15

**What an LLM really is**

Super-autocomplete, tokens & temperature — with live simulators

0:40

**The trick behind the magic**

Self-supervision: how AI taught itself from the whole internet

0:55

**What can you actually build?**

Foundation & multimodal models + the 8 use-case categories

1:10

**Your first connection in code**

6 lines of Python that talk to an AI

1:30

**Project: AI Website Summarizer**

Build it, wrap it in Gradio, watch it work

2:00

**Publish to LinkedIn**

Screenshot, caption template, post — today

Block 1 · ~15 min · the hook

## 1 Why is AI suddenly everywhere?

AI is not new — it's **70 years old**. So why did it explode in *your* feed only recently? Two things changed, and they changed everything about what *you* can build.

1950s–2000s

**AI is a research lab thing**

Decades of slow progress. You needed a PhD, a university, and years to do anything useful.

2017

**The "Transformer" is invented**

A new model design that learns language astonishingly well. This is the engine inside GPT, Claude, Gemini.

Nov 2022

**ChatGPT launches**

The fastest-adopted product in history. Suddenly everyone can *talk* to AI.

Now → you

**Anyone can build on top of it**

The hardest part is done by giant labs. You just *call* their AI with a few lines of code. That's this class.

🤯

**The wow that defines our era**

Something that used to need **a team + 6 months + a data warehouse** can now be built by **one person in an afternoon** with an internet connection. That collapse in cost is why "AI Engineer" is one of the fastest-growing jobs on the planet — and why you're in the right room.

#### The two big shifts

> **🌐:**
> **1. The model is general-purpose**
>
> Old AI did *one* task (spam-or-not). Today's AI does *thousands* — write, summarise, translate, code, answer — all from the same model. One brain, endless uses.

> **🚪:**
> **2. The barrier to entry collapsed**
>
> You don't build the AI. You *use* it through a simple API — like ordering food through an app instead of running a kitchen. If you can call a function, you can build with AI.

> **🎙️:**
> **Speaker note**
>
> Make this personal: ask the room "what took you forever last week that an AI could've drafted in 30 seconds?" Everyone has an answer. *That* gap is the opportunity we're learning to fill.

Block 2 · ~25 min

## 2 What is an LLM, really?

LLM = **Large Language Model**. Strip the hype and it does exactly one thing, unbelievably well: **it predicts the next chunk of text.** Everything — chat, code, summaries — is built on that single trick.

> **⌨️:**
> **The "super-autocomplete" mental model**
>
> Your phone suggests the next word as you type. An LLM is that idea scaled up *a billion times* and trained on much of the internet — so its guesses are good enough to write essays, code and answers.

#### First: words become *tokens*

A model doesn't read letters or words — it reads **tokens** (pieces roughly ¾ of a word). It thinks in tokens and you pay per token, so let's *see* them. Type anything:

Live sim Tokenizer playground

type → watch it split into tokens

Your text

**Starting text in the box:** AI Engineering is surprisingly approachable!

**0** Tokens

**0** Characters

**$0** Cost @ $5/1M tok

Notice: common words = 1 token; rare/long words get chopped into pieces. **Rough rule: 1 token ≈ ¾ of a word ≈ 4 characters.**

##### But why *tokens* — why not just whole words, or single letters?

This is a clever engineering trade-off. The model needs a fixed list of "things it knows" (its **vocabulary**). Words and letters both fail at the extremes — tokens sit in the sweet spot:

❌ One token per word

There are *millions* of words across all languages, plus names, typos, slang & new words daily. The vocabulary would be impossibly huge — and it would freeze the first time it met a word it had never seen.

❌ One token per letter

Only ~100 symbols — tiny vocabulary — but now every sentence is hundreds of tokens long. Slow, expensive, and the model has to relearn spelling from scratch every time.

✅ Tokens (sub-words)

A vocabulary of ~100k common chunks. Frequent words stay whole; anything rare is built from pieces. Best of both: compact *and* it can spell out *any* word it's never seen.

Concrete example — a word the model probably never saw in training still works fine, because it's assembled from familiar pieces:

how a rare word gets built

`"unbelievableness"`  →  un believ able ness

Four known tokens, zero panic. Meanwhile `"the"`, `"cat"`, `"is"` are each a single token. That's why **tokens were chosen**: they let one fixed vocabulary handle every word in every language — even ones invented tomorrow.

> **💡:**
> **Why you'll feel this as an engineer**
>
> English is "cheap" (≈¾ word per token). Code, emojis, and many non-English scripts use *more* tokens per character — so the same sentence in Hindi or Tamil can cost noticeably more tokens than in English. Worth knowing when you price an app.

#### Then: it predicts the *next* token — over and over

Given the tokens so far, the model scores **every possible next token** with a probability, picks one, adds it, and repeats. That loop *is* "generating text".

> **🎲:**
> **Temperature = the creativity dial**
>
> **Low** → always pick the most likely word → focused & repeatable. **High** → sometimes pick surprising words → creative & varied. Drag the slider and watch the probabilities reshape:

Live sim Next-token & temperature

prompt: "I love building things in ___"

Temperature

**0.7** balanced

70

> **💡:**
> **This is a real engineering choice**
>
> A support bot wants *temperature ≈ 0.2* (consistent). A brainstorming tool wants *≈ 1.0* (varied). You'll set this on day one of any real project — including today's.

#### One more truth: the model has *no memory*

Between calls, an LLM forgets everything. Anything it should "know" in a conversation must be **re-sent every time**, inside a limited **context window** (measured in tokens). This one fact quietly explains a huge amount of AI engineering.

🔤

**Tokens, not words**

It reads, thinks & bills in tokens.

🎯

**Predicts next token**

All abilities emerge from this loop.

🌡️

**Temperature**

Low = focused, high = creative.

🪟

**No memory**

You resend context each time.

Block 3 · ~15 min · the "aha"

## 3 The trick that made all of this possible

Here's the part that makes people go "ohhh". How do you teach a machine language without an army of humans labelling billions of examples? You let it **play fill-in-the-blank with the entire internet.**

> **📚:**
> **The old way (slow & expensive)**
>
> Humans hand-label data: "this email = spam", "this review = positive". Accurate, but you need millions of labelled examples. Painfully slow.

> **🪄:**
> **The clever shortcut: self-supervision**
>
> Take any sentence from the web, *hide a word*, and ask the model to guess it. The answer is **already in the text** — so the internet becomes its own teacher. No humans needed. Trillions of free practice questions.

Try being the model for a second — guess the hidden word:

The barista handed me a hot cup of ______.

Pick the word you think fills the blank.

**If you pick "coffee":** ✅ Exactly! And to "know" that, the model quietly learned context, grammar & the world. **That's self-supervision.**

**If you pick "tea":** ☕ Reasonable! "tea" works too — the model learns there are *several* good answers, with different probabilities (remember temperature?).

**If you pick "bicycle" or "sadness":** 😅 Not quite — but every wrong guess is how the model *learns*. Billions of these and it gets scarily good.

🤯

**Why this changes everything**

You just did what the model does **billions of times**. To guess "coffee", it had to quietly learn grammar, context, what baristas do, what's hot, what fits in a cup… *Understanding emerges as a side-effect of getting really good at fill-in-the-blank.* That's the whole secret behind ChatGPT.

> **⚠️:**
> **Keep it honest (mention this)**
>
> Because it learned by predicting plausible text, an LLM can sometimes produce confident-sounding *wrong* answers — called **hallucinations**. A big part of our job as AI engineers is designing around that (e.g. feeding it real documents — we'll see that later). Trust, but verify.

Block 4 · ~15 min

## 4 So… what can you actually build?

First, a quick upgrade to your mental model. Modern AI isn't just about text anymore — it can also see, hear and speak. We call these **foundation models**: one giant general-purpose brain you adapt to many jobs.

#### Multimodal: models with more *senses*

📝 Text

🖼️ Images

🎤 Audio

🎬 Video

➜

🧠**Foundation Model**

➜

💬 An answer

🖌️ An image

🔊 A voice

📊 A report

Show it a photo of your fridge → get a recipe. Speak to it → it talks back. Same idea as text, more senses.

#### The 8 things people build with AI

Almost every AI product you've seen falls into one of these buckets. Find *your* idea here:

💻

**Coding**

Write, explain & fix code. The #1 use case today.

Copilot · Cursor

✍️

**Writing**

Emails, blogs, marketing copy, rewriting.

Jasper · Notion AI

🎨

**Image & Video**

Generate art, edit photos, make clips.

Midjourney

🎓

**Education**

Personal tutors that explain anything, your pace.

Khanmigo

💬

**Chatbots**

Support, sales & assistants that converse.

Intercom Fin

📥

**Info Aggregation**

Summarise & search across mountains of text.

★ today's project

🗂️

**Data Organization**

Tag, sort & structure messy information.

classification

⚙️

**Workflow / Agents**

AI that takes multi-step actions for you.

the frontier

🏭 Industry spotlight · same skill, different product

##### The pattern is always the same

A coding tool, a legal-doc reader, a Swiggy-order chatbot — under the hood they all do one thing: *connect to a model, give it the right context, get a useful answer, wrap it in a UI.* Learn that once (today) and every one of these 8 becomes buildable.

GitHub Copilot Harvey · legal Klarna · support Khan Academy · tutoring Perplexity · search

**Today we build a 📥 Info-Aggregation tool** — an AI Website Summarizer. Simple, genuinely useful, and very shareable.

Block 6 · ~20 min
