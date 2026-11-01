# Dockerize an LLM Project — "ScalerGPT" RAG bot 📚

## Dockerize an LLM Project — "ScalerGPT" RAG bot 📚

**What you'll build:** a RAG chatbot (FastAPI + OpenAI API + ChromaDB). New concepts: **secrets/env vars, docker compose, volumes, multi-container networking, startup readiness**. This code is battle-tested — it includes fixes for two real bugs that show up every time.

#### What changes at level 2

This time the model isn't yours — it's OpenAI's. LLM projects bring three problems classic ML didn't have:

1️⃣ *Secrets* — bake your API key into the image and you've written your PIN on your ATM card. 2️⃣ *Multiple services* — an app plus a vector database. Two boxes, one order. 3️⃣ *State* — the database's data must survive even after its container dies.

The three solutions you'll learn here: *.env files, docker compose, and volumes.*

> **Analogy:**
> #### RAG in 60 seconds
>
> **RAG = Retrieval Augmented Generation** — an open-book exam for the LLM. Instead of answering from memory (where it hallucinates), the model is handed the relevant pages from *your* notes and told "answer using only this."
>
> - **Embedding:** turning text into a list of numbers such that similar meanings get similar numbers. It's how the machine "feels" that *"container"* and *"Docker box"* are related even though they share no words.
> - **Vector database (Chroma):** a library that stores those numbers and can instantly find "the 3 most similar passages to this question."
> - **The pipeline:** question → find relevant chunks (retrieve) → paste them into the prompt (augment) → let the LLM write the answer (generate).

#### 📁 Project structure

```pseudo title="Terminal"
CREATE folder scalergpt, then move into it
CREATE folder docs
CREATE empty files app.py, ingest.py, requirements.txt, Dockerfile, docker-compose.yml, .env.example, .dockerignore and .gitignore
```

```python reveal title="Terminal"
mkdir scalergpt && cd scalergpt
mkdir docs
touch app.py ingest.py requirements.txt Dockerfile docker-compose.yml .env.example .dockerignore .gitignore
```

```pseudo title="requirements.txt"
ADD fastapi at exactly version 0.115.6   // the web API
ADD uvicorn at exactly version 0.34.0   // the web server that runs it
ADD openai at exactly version 1.59.7   // talks to the OpenAI API
ADD chromadb-client at exactly version 0.6.3   // the thin client; the database runs in its own container
ADD python-dotenv at exactly version 1.0.1   // loads .env into the environment
```

```python reveal title="requirements.txt"
fastapi==0.115.6
uvicorn==0.34.0
openai==1.59.7
chromadb-client==0.6.3
python-dotenv==1.0.1
```

**In plain words:** note it's `chromadb-client` — the *thin client* — not the full `chromadb` package. The full package IS the database (heavy); the client just *talks* to a database running elsewhere. Since Chroma will live in its own container, your app only needs the phone, not the whole telephone exchange. This keeps the app image small — the #1 problem with LLM images is size. Drop some `.txt` or `.md` notes into `docs/` — they become the bot's knowledge.

#### Secrets 101 — the ATM PIN rule

**The golden rule:** *"Image = ATM card (safe to share). Env var = PIN (inject at runtime, never write it on the card)."*

An **environment variable** is a named value the operating system hands to a program when it starts — like a sticky note passed to the chef as they walk in, rather than printed in the recipe book everyone can read. A **.env file** is simply a text file of such notes, one per line.

```pseudo title=".env.example → copy to .env and add your real key"
// step 1: copy this file to .env, then paste your real key into .env
SET OPENAI_API_KEY to your real key   // a placeholder in this template; the real key lives only in .env
```

```python reveal title=".env.example → copy to .env and add your real key"
# Copy this file:  cp .env.example .env   — then paste your real key.
OPENAI_API_KEY=sk-paste-your-real-key-here
```

- No quotes, no spaces around the `=`. Get a key at platform.openai.com/api-keys. The whole demo costs less than one US cent.
- Add `.env` to BOTH `.dockerignore` AND `.gitignore`. You ship a safe `.env.example` template instead; each person copies it to `.env` locally.
- If you ever write `ENV OPENAI_API_KEY=sk-...` in a Dockerfile, anyone can read it back with `docker history`. This is a favourite interview question.

#### 🧠 app.py — RAG with a retry loop ✅ fixed version

This is the corrected code. The naive version crashes at startup — the next card explains exactly why, because that bug is the best lesson in the whole guide.

```pseudo title="app.py"
CREATE app = FastAPI titled "ScalerGPT"
SET API_KEY = OPENAI_API_KEY from the environment, with spaces trimmed
IF API_KEY is empty OR starts with "sk-paste" THEN
    STOP with "OPENAI_API_KEY missing. Put a real key in .env"   // a clear message, not a traceback
CREATE llm = an OpenAI client that uses API_KEY
CREATE openai_ef = an embedding function (text-embedding-3-small) that uses API_KEY   // the thin client has no embedder of its own
SET CHROMA_HOST = the CHROMA_HOST setting, or localhost
SET CHROMA_PORT = the CHROMA_PORT setting as a number, or 8000

DEFINE connect_to_chroma():   // Chroma takes a few seconds to boot, so retry
    REPEAT up to 30 times:
        TRY:
            CONNECT to Chroma at CHROMA_HOST:CHROMA_PORT and send a heartbeat
            PRINT "Connected to chroma at CHROMA_HOST:CHROMA_PORT"
            RETURN the client
        ON ERROR:
            PRINT "Waiting for chroma (attempt N of 30)"
            WAIT 2 seconds
    STOP with "Could not reach chroma"

SET chroma = connect_to_chroma()
SET collection = get or create the "notes" collection, using openai_ef

DEFINE Question: query (text)

DEFINE health():   // route GET /
    RETURN status, the number of documents indexed, and the Chroma host and port

DEFINE ask(q: Question):   // route POST /ask
    IF the collection is empty THEN
        RETURN HTTP 400 with "No documents indexed. Run: docker compose exec app python ingest.py"
    Retrieve the 3 most similar chunks for the question   // step 1 of RAG
    Augment the system prompt with those chunks as CONTEXT   // step 2
    Generate the answer with gpt-4o-mini, using the system prompt and the question   // step 3
    RETURN the question, the answer, and how many chunks were used
```

> **Imported:**
> - `os` Python standard library: reads environment variables such as `OPENAI_API_KEY` with `os.getenv`.
> - `sys` Python standard library: `sys.exit` stops the program with a clear message when setup fails.
> - `time` Python standard library: `time.sleep` waits 2 seconds between attempts to reach Chroma.
> - `chromadb` third-party module, installed by the `chromadb-client` package in requirements.txt: the Chroma client that connects to the database container.
> - `embedding_functions` from `chromadb.utils`: builds the OpenAI embedder that turns text into numbers.
> - `FastAPI` from `fastapi`: creates the web app and its routes.
> - `HTTPException` from `fastapi`: returns an error response with a status code, such as 400.
> - `OpenAI` from `openai`: the client that sends requests to the OpenAI API.
> - `BaseModel` from `pydantic`: the base class for the `Question` form.

```python reveal title="app.py"
import os, sys, time
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="ScalerGPT")

# Fail LOUDLY and clearly if the key is missing - not with a cryptic traceback
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
if not API_KEY or API_KEY.startswith("sk-paste"):
    sys.exit("[ScalerGPT] OPENAI_API_KEY missing. Put a real key in .env")

llm = OpenAI(api_key=API_KEY)

# The thin client has no built-in embedder - we must supply one explicitly
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=API_KEY, model_name="text-embedding-3-small")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

def connect_to_chroma(retries=30, delay=2):
    # Chroma takes a few seconds to boot. depends_on only waits for its
    # container to START, not to be READY - so we knock politely and retry.
    for attempt in range(1, retries + 1):
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            client.heartbeat()
            print(f"[ScalerGPT] Connected to chroma at {CHROMA_HOST}:{CHROMA_PORT}", flush=True)
            return client
        except Exception as e:
            print(f"[ScalerGPT] Waiting for chroma ({attempt}/{retries}): {type(e).__name__}", flush=True)
            time.sleep(delay)
    sys.exit(f"[ScalerGPT] Could not reach chroma at {CHROMA_HOST}:{CHROMA_PORT}")

chroma = connect_to_chroma()
collection = chroma.get_or_create_collection(name="notes", embedding_function=openai_ef)

class Question(BaseModel):
    query: str

@app.get("/")
def health():
    return {"status": "ScalerGPT is live 📚", "docs_indexed": collection.count(),
            "chroma_host": CHROMA_HOST, "chroma_port": CHROMA_PORT}

@app.post("/ask")
def ask(q: Question):
    if collection.count() == 0:
        raise HTTPException(status_code=400,
            detail="No documents indexed. Run: docker compose exec app python ingest.py")
    # 1. RETRIEVE - find the 3 most relevant chunks
    hits = collection.query(query_texts=[q.query], n_results=3)
    documents = hits.get("documents") or [[]]
    context = "\n\n---\n\n".join(documents[0])
    # 2. AUGMENT - paste those chunks into the prompt
    system_prompt = ("You are ScalerGPT, a helpful teaching assistant. "
        "Answer using ONLY the context below. If it does not contain the answer, "
        f"say you don't know.\n\nCONTEXT:\n{context}")
    # 3. GENERATE - let the LLM write the final answer
    resp = llm.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": q.query}])
    return {"question": q.query, "answer": resp.choices[0].message.content,
            "sources_used": len(documents[0])}
```

**In plain words:** at startup the app does three checks: (1) is the API key present? — if not, exit with a human-readable message instead of a scary traceback; (2) set up the *embedder* — the machine that converts text to numbers (the thin client doesn't include one, so you hand it OpenAI's); (3) **knock on Chroma's door politely** — try to connect, and if refused, wait 2 seconds and knock again, up to 30 times, printing progress so you can watch it in the logs. Then `/ask` is the three-step RAG dance: find the 3 most relevant passages, paste them into the instructions, let GPT write the answer. The `if count() == 0` guard gives a helpful "you forgot to ingest" message instead of a confusing empty answer.

You'll also need `ingest.py` — it reads every file in `docs/`, splits them into paragraph chunks, and loads them into Chroma, using the same retry pattern.

#### The bug that WILL bite you: started ≠ ready

Here's the exact sequence, because you will hit it:

1. You run `docker compose up -d`. Then `docker compose ps` shows… **only chroma**. The app has vanished.
2. Lesson 1: `ps` hides dead containers. `docker compose ps -a` reveals the app: **Exited (1)**.
3. Lesson 2: `docker compose logs app` shows the reason: *"Connection refused… Could not connect to a Chroma server."*
4. Lesson 3 (the real one): the compose file says `depends_on: chroma` — so why did it fail? Because **`depends_on` only waits for chroma's container to START, not for the database inside it to be READY.** Chroma needs a few seconds to boot. The app knocked immediately, got no answer, and gave up.

**Analogy:** the restaurant unlocked its door (container started) but the chef hasn't tied his apron yet (service not ready). If you shout your order at the locked kitchen and storm out, that's a crash. The retry loop in app.py is the polite customer who waits and knocks again. (The alternative fix — a compose `healthcheck` + `depends_on: condition: service_healthy` — is in the practice challenges.)

> **Analogy:**
> #### docker-compose.yml — the thali order system ✅ fixed version
>
> So far you ordered tiffins one at a time — `docker run` this, `docker run` that. Compose says: *write one menu, then just say "serve the thali."* The file format is YAML — a way of writing structured settings where **indentation shows what belongs to what**, like a neatly indented shopping list. (Careful: YAML is picky — use spaces, never tabs.)
>
> ```pseudo title="docker-compose.yml"
> DEFINE services:
>     app:
>         BUILD the image from this folder's Dockerfile
>         PUBLISH port 8000 on my Mac, port 8000 inside the container
>         LOAD .env as environment variables   // the key is injected at runtime, not baked in
>         SET CHROMA_HOST to chroma, and CHROMA_PORT to 8000   // the internal port
>         START after chroma   // start order only, not readiness
>         RESTART unless stopped
>     chroma:
>         use the ready-made image chromadb/chroma:0.6.3
>         PUBLISH port 8001 on my Mac, port 8000 inside the container   // only so you can reach it from your Mac for debugging
>         STORE its data in the volume chroma_data, at /chroma/chroma
>         RESTART unless stopped
> DEFINE volume chroma_data   // Docker creates and keeps it
> ```
>
> ```python reveal title="docker-compose.yml"
> services:
>   app:
>     build: .
>     container_name: scalergpt-app
>     ports:
>       - "8000:8000"
>     env_file: .env
>     environment:
>       - CHROMA_HOST=chroma
>       - CHROMA_PORT=8000     # INTERNAL port - see the port trap below!
>     depends_on:
>       - chroma
>     restart: unless-stopped
>
>   chroma:
>     image: chromadb/chroma:0.6.3
>     container_name: scalergpt-chroma
>     ports:
>       - "8001:8000"
>     volumes:
>       - chroma_data:/chroma/chroma
>     restart: unless-stopped
>
> volumes:
>   chroma_data:
> ```
>
> Line-by-line decoder
>
> - **services:** — The menu. Each entry below is one container you want.
> - **build: .** — "Build this service's image from the Dockerfile in this folder" (the app's Dockerfile is the same 6-liner as Port 1, minus the training step).
> - **image: chromadb/chroma:0.6.3** — Don't build — download this ready-made image from Docker Hub. You never write a Dockerfile for Chroma; someone already packed that tiffin.
> - **env_file: .env** — "At startup, hand this container all the sticky notes from .env" — the PIN gets injected at runtime, never baked into the image.
> - **environment:** — More sticky notes, written directly here (fine for non-secrets like hostnames).
> - **CHROMA_HOST=chroma** — Not an IP address — the **service name**! Compose creates a private network where every service is reachable by its name, like flats on an intercom. The app dials "chroma" and Docker connects the call.
> - **depends_on:** — "Start chroma before me." ⚠️ Start — not ready. That's why app.py retries.
> - **restart: unless-stopped** — "If I crash, bring me back automatically" — unless a human explicitly stopped me. A free safety net.
> - **volumes: (on chroma)** — "Mount the storage box named chroma_data at the path /chroma/chroma inside the container" — that's where Chroma keeps its data, so the data now lives OUTSIDE the disposable container.
> - **volumes: (bottom)** — Declares the storage box itself so Docker creates and tracks it.

#### The port trap: published vs internal

Look at chroma's line: `"8001:8000"`. Two different numbers — this is where everyone gets burned:

- Chroma listens on port **8000 inside its own container** (the flat number).
- You publish it as **8001 on the Mac** (the street gate) — only so YOU can poke it from outside for debugging, and because the app already took the Mac's 8000.
- The app container is **already inside the building** — it's a neighbour, not a street visitor. Neighbours use flat numbers. So the app must use `CHROMA_PORT=8000`.

**Setting `CHROMA_PORT=8001` is the single most common bug in this setup** — it produces "connection refused" and an exited app container. Say it twice: *containers talking to containers use INTERNAL ports. Only your Mac uses the published port.*

#### Milestone #2 — Serve the thali

```pseudo title="Terminal"
copy .env.example to .env   // then put your real key inside .env
RUN docker compose up -d --build   // build images if code changed, then start all services in the background
SHOW docker compose ps -a   // all services, including exited ones
SHOW docker compose logs for app
RUN python ingest.py inside the running app container   // docker compose exec: step into the live container
SEND a POST to localhost:8000/ask, with the question "What is Docker?" as JSON data
```

```python reveal title="Terminal"
cp .env.example .env         # then put your REAL key inside .env

docker compose up -d --build

docker compose ps -a
docker compose logs app

docker compose exec app python ingest.py

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Docker?"}'
```

Command decoder

- **docker compose up** — "Read docker-compose.yml and make reality match it" — create the network, the volume, and all containers, in dependency order.
- **-d** — Detached — background, same as before.
- **--build** — "Rebuild my images first if code changed." ⚠️ Make this a habit: after ANY file edit, `up -d --build`. Without it, Compose happily reuses the old photograph and your edit never arrives. This single mistake costs most people 15 minutes.
- **docker compose ps -a** — List this project's containers **including dead ones**. Expect both "Up". If app says "Exited", read its logs.
- **docker compose logs app** — The app's diary. You want to see: *[ScalerGPT] Connected to chroma at chroma:8000* — you may first see a few "Waiting for chroma (1/30)" lines. That's the retry loop doing its job!
- **docker compose exec app python ingest.py** — "Inside the already-running **app** container, execute `python ingest.py`." This is how you run one-off jobs (migrations, imports) in production — you don't start a new container, you step into the live one.

Then open **http://localhost:8000/docs** and ask questions from the Swagger UI. The test worth doing: ask *"What is the capital of France?"* — ScalerGPT says it doesn't know, because the answer isn't in your docs. **That's proof the answers are grounded in YOUR documents, not the model's memory.**

#### Milestone #2.5 — The volume magic trick

```pseudo title="Destroy everything. Data survives."
RUN docker compose down   // stop and remove the containers and network; volumes are kept
RUN docker compose up -d   // create brand-new containers
SEND a GET to localhost:8000/   // check that docs_indexed is still above 0
```

```python reveal title="Destroy everything. Data survives."
docker compose down
docker compose up -d
curl http://localhost:8000/
```

Command decoder

- **docker compose down** — The opposite of up: stop and DELETE all containers and the network. The thali is cleared. But volumes survive by default.
- **docker compose up -d** — Brand-new containers from scratch.
- **curl http://localhost:8000/** — `docs_indexed` is STILL > 0 — you never re-ingested, yet the data is there. It lives in the volume, not the container. ♻️
- **docker compose down -v** — Know it, don't run it casually: `-v` also deletes volumes. THIS is how you actually lose the data. The steel dabba goes to the scrapyard.

**The takeaway:** containers die all the time — deployments, crashes, scaling. Volumes are the steel box that comes back after every delivery. *Container = disposable. Volume = permanent.*

#### ✅ Self-check — Port 2

- Both services show "Up" in `docker compose ps -a`
- I ingested docs and got a grounded answer from `/ask`
- I proved the volume works: `down` → `up` → data still there
- I can explain why my API key must never go in the Dockerfile
- I can explain the difference between the published port and the internal port
- I can explain why `depends_on` alone didn't save me

PORT 3
