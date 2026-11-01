# Mini-Project: Chat with your PDF

## 21 Mini-Project: Chat with your PDF

Time to ship. Upload any PDF — your resume, a research paper, an annual report, your college notes — and chat with it. Every answer cites the page it came from. This is the project that gets **"how did you build this?"** in your LinkedIn DMs.

#### The full app — 4 files

📄

**PDF in** user uploads

➜

✂️

**Chunk**~800 chars

➜

📍

**Embed + store** Chroma

➜

🔎

**Retrieve** top-3 chunks

➜

💬

**Chat** Gradio

##### Step 1 — Load the PDF & index it once

```pseudo title="pdf_chat.py · part 1"
DEFINE build_index(pdf_path):
    SET pages = read the PDF at pdf_path   // one document per page
    SET splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    SET chunks = splitter.split_documents(pages)   // each chunk keeps its page number
    SET embedder = HuggingFaceEmbeddings("all-MiniLM-L6-v2")
    SET db = Chroma.from_documents(chunks, embedder)   // kept in memory, not saved to disk
    RETURN db
```

> **Imported:**
> - `PyPDFLoader` from `langchain_community.document_loaders`, package langchain-community: reads a PDF and gives one document per page, with the page number in its metadata.
> - `RecursiveCharacterTextSplitter` from `langchain_text_splitters`, package langchain-text-splitters: cuts the pages into chunks of about 800 characters.
> - `HuggingFaceEmbeddings` from `langchain_huggingface`, package langchain-huggingface: the free local embedding model.
> - `Chroma` from `langchain_chroma`, package langchain-chroma: a vector store that holds the chunks and their vectors.

```python reveal title="pdf_chat.py · part 1"
# pip install langchain langchain-openai langchain-chroma langchain-huggingface \
#             langchain-community pypdf sentence-transformers gradio python-dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_index(pdf_path):
    pages    = PyPDFLoader(pdf_path).load()                    # ① read all pages
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks   = splitter.split_documents(pages)                # ② chunk them
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db       = Chroma.from_documents(chunks, embedder)         # ③ in-memory store
    return db
```

##### Step 2 — Answer with retrieval + citations

```pseudo title="pdf_chat.py · part 2"
LOAD the .env file into the environment   // load_dotenv()
CREATE model = ChatOpenAI("gpt-4o-mini", temperature 0)
CREATE prompt = a template that says to answer ONLY from the context, to say "I couldn't find that in the document" when the answer is missing, and to end with a Sources line
DEFINE ask(db, question):
    SET chunks = db.similarity_search(question, k=4)   // the 4 nearest chunks
    SET context = each chunk written as "[page N] text", joined with blank lines   // N is the stored page number + 1
    SET chain = prompt | model
    RETURN the text of chain.invoke(context, question)
```

> **Imported:**
> - `ChatOpenAI` from `langchain_openai`, package langchain-openai: the OpenAI chat model that writes the answer.
> - `ChatPromptTemplate` from `langchain_core.prompts`, package langchain-core: builds a prompt with named slots that get filled in.
> - `load_dotenv` from `dotenv`, package python-dotenv: copies the .env file into the environment.

```python reveal title="pdf_chat.py · part 2"
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are a helpful PDF assistant. Answer the question using ONLY the context below.
If the context doesn't contain the answer, say "I couldn't find that in the document."
After your answer, list the page numbers you used as: Sources: page X, page Y.

Context:
{context}

Question: {question}
""")

def ask(db, question):
    chunks  = db.similarity_search(question, k=4)
    context = "\n\n".join(
        f"[page {c.metadata['page']+1]}] {c.page_content}" for c in chunks)
    chain = prompt | model
    return chain.invoke({"context": context, "question": question}).content
```

##### Step 3 — Give it a face with Gradio

```pseudo title="pdf_chat.py · part 3"
SET state = {"db": None}   // keeps the index between messages
DEFINE upload(pdf):
    SET state["db"] = build_index(the uploaded file's name)   // re-index on every new PDF
    RETURN "PDF indexed! Ask me anything about it."
DEFINE chat(message, history):
    IF state["db"] is None THEN
        RETURN "Please upload a PDF first"
    RETURN ask(state["db"], message)
CREATE a page titled "Chat with your PDF" with a PDF upload box, a status line and a chat window
when a file is uploaded, CALL upload and show its result in the status line
RUN the page with share on   // creates a public link
```

> **Imported:**
> - `gradio` (as `gr`) pip package gradio: builds the web page with the upload box, status line and chat window.

```python reveal title="pdf_chat.py · part 3"
import gradio as gr

state = {"db": None}                    # ① remember the index across turns

def upload(pdf):
    state["db"] = build_index(pdf.name)   # ② re-index whenever a new PDF arrives
    return "✅ PDF indexed! Ask me anything about it."

def chat(message, history):
    if state["db"] is None:
        return "Please upload a PDF first 📄"
    return ask(state["db"], message)

with gr.Blocks(title="📄 Chat with your PDF") as demo:
    gr.Markdown("## 📄 Chat with your PDF (powered by RAG)")
    pdf    = gr.File(label="Upload a PDF", file_types=[".pdf"])
    status = gr.Markdown()
    pdf.upload(upload, inputs=pdf, outputs=status)
    gr.ChatInterface(fn=chat)

demo.launch(share=True)                   # share=True → public link!
```

🔍 decoder · the 3 small choices that matter

①

`state` is a plain dict that survives across Gradio events. Without it, every chat message would re-index the PDF from scratch (slow!).

②

Re-indexing only on upload means typing is instant. This is the same indexing/querying split from Block 15.

③

We pass `page` from the chunk metadata into the prompt — that's how the model knows which page to cite. **Metadata is RAG's superpower.**

##### Run it

```pseudo title="bash — your project folder"
RUN python pdf_chat.py   // start the app
// Gradio then prints a local link and a public *.gradio.live link to share
```

```python reveal
$ python pdf_chat.py

Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://abcd12.gradio.live   # ← share this on LinkedIn!
```

bash — your project folder

**Upload *any* PDF**

Your resume, the Indian Constitution, your company's HR policy, last quarter's earnings call transcript. Anything text-based.

**Ask 3 questions**

One factual ("when was X founded?"), one summary ("what's the main argument?"), one tricky ("compare X and Y"). Notice the citations.

**Try a question that's NOT in the doc**

The answer should be *"I couldn't find that in the document."* — that's RAG **refusing to hallucinate**. Record this moment. It's the whole point.

#### Try the working version 👇

A live in-browser version with three pre-indexed sample documents — click a PDF, ask a question, see RAG retrieve the right chunk before answering:

📄 **Chat with your PDF** live demo

##### Pick a sample document

Ask anything about this doc...

⚙️ Simulated in-browser with a tiny semantic-matching layer so it runs key-free. Your real `pdf_chat.py` uses actual embeddings + GPT — same flow, same feel, larger brain.

🏭 Industry spotlight · this *is* the canonical AI product

##### You just built the most-shipped AI app of 2024–26

"Chat with [your docs / your PDF / your codebase / your Notion]" is the single most common AI feature on the market today — and almost all of them are this exact pattern with a fancier UI. ChatGPT's "Browse my files", Claude Projects, Cursor's `@codebase`, Glean, Notion AI — every one of them. You now own the recipe.

Notion AI Glean Claude Projects Cursor @docs Perplexity Spaces

Block 22 · ~10 min · 📣 ship it

##### Live sim · chat with a document

Document names: 📋 HR Policy · 💰 TCS Q3 Earnings · 📜 Indian Constitution (Part III)

On load: Indexed "<document name>" — 1 page, ~8 chunks. Ask me anything!

**📋 HR Policy · preview**

```text
Annual leave: 22 days/year for full-time employees, accrued monthly.
Sick leave: 12 days/year, no carry-forward.
Work from home: up to 2 days per week with manager approval.
Maternity leave: 26 weeks paid as per Indian law.
Paternity leave: 10 working days.
Reimbursements: internet ₹1500/month, mobile ₹800/month.
Notice period: 60 days for senior roles, 30 days for others.
Probation: 6 months. Probation extension requires HR approval.
```

**Try:** How many leaves do I get? · Can I work from home? · What is the notice period? · What is the maternity policy?

**Bot replies**

- Full-time employees get 22 days of annual leave (accrued monthly) plus 12 days of sick leave per year. Sources: page 1.
- Yes — up to 2 days per week with your manager's approval. Sources: page 1.
- 26 weeks of paid maternity leave, in line with Indian law. Sources: page 1.
- 10 working days of paternity leave. Sources: page 1.
- Notice period is 60 days for senior roles, 30 days for others. Sources: page 1.
- Internet: ₹1500/month. Mobile: ₹800/month. Sources: page 1.
- Internet reimbursement is ₹1500/month. Sources: page 1.
- Probation period is 6 months. Extensions require HR approval. Sources: page 1.

**💰 TCS Q3 Earnings · preview**

```text
Revenue: ₹62,613 cr, up 4.0% YoY in constant currency.
Operating margin: 24.6%, up 50 bps QoQ.
Net profit: ₹12,380 cr.
TCV (Total Contract Value): $13.2 bn, highest in 7 quarters.
Headcount: 612,724 employees, net addition of 5,370 this quarter.
Attrition: 13.0% (LTM), down from 13.3%.
Cash and equivalents: ₹58,200 cr.
Dividend: ₹76/share interim declared.
BFSI segment grew 3.8%, retail 2.1%, manufacturing 5.9%.
```

**Try:** What was the revenue? · How was the operating margin? · What is the attrition rate? · How big is the latest TCV?

**Bot replies**

- Revenue was ₹62,613 cr, up 4.0% YoY in constant currency. Sources: page 1.
- Operating margin was 24.6%, up 50 basis points quarter-on-quarter. Sources: page 1.
- Net profit was ₹12,380 cr. Sources: page 1.
- TCV (Total Contract Value) hit $13.2 bn — the highest in 7 quarters. Sources: page 1.
- 612,724 employees, with a net addition of 5,370 this quarter. Sources: page 1.
- Attrition (LTM) was 13.0%, down from 13.3%. Sources: page 1.
- Interim dividend of ₹76 per share was declared. Sources: page 1.
- BFSI segment grew 3.8% this quarter. Sources: page 1.

**📜 Indian Constitution (Part III) · preview**

```text
Article 14: Equality before law — the State shall not deny equality to any person.
Article 15: Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth.
Article 19: Six fundamental freedoms — speech, assembly, association, movement, residence, profession.
Article 21: Right to life and personal liberty — no person shall be deprived except by procedure established by law.
Article 21A: Right to education for children aged 6-14.
Article 25: Freedom of conscience and free profession of religion.
Article 32: Right to constitutional remedies — Supreme Court can be approached for enforcement.
```

**Try:** What does Article 21 say? · Tell me about Article 19 · What is the right to education? · Which article covers religion?

**Bot replies**

- Article 14 guarantees equality before law — the State shall not deny equality to any person. Sources: page 1.
- Article 15 prohibits discrimination on grounds of religion, race, caste, sex or place of birth. Sources: page 1.
- Article 19 grants six fundamental freedoms: speech, assembly, association, movement, residence, and profession. Sources: page 1.
- Article 21 protects the right to life and personal liberty — no person shall be deprived except by procedure established by law. Sources: page 1.
- Article 32 is the right to constitutional remedies — citizens can approach the Supreme Court for enforcement of Fundamental Rights. Sources: page 1.
- Article 21A guarantees the right to education for children aged 6 to 14. Sources: page 1.
- Article 25 guarantees freedom of conscience and free profession of religion. Article 15 prohibits discrimination on grounds of religion. Sources: page 1.
- Article 19 grants freedom of speech as one of six fundamental freedoms. Sources: page 1.

**Not in the document:** I couldn't find that in the document. 🤷 (This is RAG *refusing to hallucinate* — exactly what we want.)

## 22 Ship it to LinkedIn — today

"I built a RAG system" is an instant credibility upgrade — most people who post about AI have never actually built one. The shipping ritual continues: clip, caption, post, reply.

#### The 3-step ship checklist (same as Class 1 & 2)

**Record a 20-second clip**

Upload your PDF on screen, ask 2 questions, show the *"I couldn't find that"* moment. That's the magic.

**Use the caption template below**

Fill in the blanks. Mention what PDF you tested with — specifics make it land.

**Post + reply for 1 hour**

Tag *#AIEngineering*, *#RAG*, *#100DaysOfCode*. Replying to every comment in the first hour is the algorithm's favourite signal.

#### Steal this caption

You

Your Name

AI Engineering learner · now · 🌐

📄 I just built *"Chat with your PDF"* — and it actually *understands* the document. Upload any PDF (I tested with [your doc here]) and it answers questions from the real text, with page citations. If the answer isn't in the doc, it says so instead of making something up. 🤯 The trick is called **RAG** (Retrieval-Augmented Generation): 🔪 Chop the doc into chunks 📍 Turn each chunk into a vector (a "coordinate of meaning") 🔎 For every question, find the 3 nearest chunks 📋 Hand them to the LLM and let it answer from *real text* The most surprising thing? You can do **math on meaning**. *king − man + woman ≈ queen*. Once you see that, RAG stops feeling like magic and starts feeling like geometry. ✨ This is the same pattern behind Notion AI, Perplexity, Glean, and "Chat with your codebase" features in modern IDEs. Big confidence boost knowing I can clone the architecture in ~50 lines. Learning AI Engineering with @Shivank Agrawal at @Scaler — Day 3 done. The pace of going from *I've heard of LLMs* to *I can ship AI products* is genuinely wild. 👉 What PDF should I point it at next? Drop a suggestion in the comments. #AIEngineering #RAG #LLM #Python #BuildInPublic #100DaysOfCode

👍 You and others💬 Comments↗ Repost

👉 When you type "@Shivank Agrawal", pick [linkedin.com/in/shivankagrawal](https://www.linkedin.com/in/shivankagrawal/) so the tag links correctly. Tagging your instructor and Scaler boosts reach & lets us amplify your post.

> **🎙️:**
> **Speaker note · the post-class ritual**
>
> Same as before: **10 minutes in class** for everyone to post. Then "follow-and-like" round across the cohort. Three classes in, this is becoming muscle memory — and that's exactly the point.

#### Want a variation? Pick a flavour, swap the PDF

The recipe is the same; the data makes it interesting. Try one of these on your own:

📜**Chat with the Constitution**

Index the Indian Constitution PDF. Ask "what are the Fundamental Rights?" with citations.

data: indiacode.nic.in

📊**Chat with an earnings call**

Index TCS or Infosys' last quarterly transcript. Ask about margins, guidance, hiring.

data: investor relations sites

📚**Chat with your textbook**

Index a chapter. Ask exam-style questions. Suddenly: a personalised tutor.

data: your bookshelf

🧾**Chat with company HR policy**

Genuinely useful at your workplace. "How many leaves do I have left?" "What's the WFH policy?"

data: your HR portal

Block 23 · ~5 min · what's coming

## 23 Where this is going

RAG works. But the frontier is making it *smarter* — and that's where this course leads next.

#### 🤖 Agentic RAG — when retrieval becomes a decision

Today's RAG always retrieves. But sometimes you don't need to (small talk), and sometimes one retrieval isn't enough (multi-hop questions). **Agentic RAG** = combine Class 2's agent loop with Class 3's library. The agent *decides*: "do I need to look this up? Is what I found enough? Should I rewrite my query and try again?"

> **🔁:**
> **The loop you'll meet next class**
>
> *Query → retrieve → grade chunks → if bad, rewrite query, search again → if still bad, ask user for clarification → answer.* Same agent loop you built in Class 2, with the librarian (Class 3) as one of its tools.

#### 📈 Advanced RAG — the tricks the senior engineers use

✍️**HyDE**

Hypothetical Document Embeddings: have the LLM *imagine* what the answer would look like, then search for chunks that match the imagined answer. Counter-intuitive, works surprisingly well.

🪜**Step-back prompting**

Before searching, ask the LLM to generalize the question. "What's the formula for compound interest in this case?" → "What is compound interest?" → broader, better retrieval.

🕸️**Graph RAG**

Build a knowledge graph from your docs (entities + relationships). Now you can answer "who reports to X" by walking the graph, not just searching.

📊**RAG evaluation**

How do you measure if your RAG is good? Three metrics: *relevance*, *faithfulness*, *correctness*. We'll wire up a real eval pipeline.

🚀

**Where you are right now**

Three classes in, you've built a chatbot, an agent, and a RAG system. You understand the four pieces of every AI product — *model · prompt · tool · retrieval*. Almost everything ahead is recombining these four in cleverer ways. You're past the steep part of the curve.

📍

**Embeddings**

Text → vectors. Similar meaning = nearby.

✂️

**Chunking**

The unglamorous knob that decides quality.

🗂️

**Vector DB**

Three calls: add, query, delete.

🎯

**You shipped**

A real "Chat with your PDF" — on LinkedIn. 🎉

#### You shipped class 3 🎉

You now understand the four pieces of every modern AI product. Most people who claim to "know AI" don't know what you know.

##### For next class

Index a PDF that matters to *you* (your resume, your notes, your company policy) and bring 3 questions where your RAG surprised you — for better or worse. We'll use those to motivate Agentic RAG.

AI Engineering · Class 3 — RAG: Give Your AI Its Own Library Scaler Academy
