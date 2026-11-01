# Dockerize an Agentic Project — "DeskBuddy" 🤖

## Dockerize an Agentic Project — "DeskBuddy" 🤖

**What you'll build:** a 3-container agentic system — an **agent service** (LLM + tool-calling loop), a **tools service** (separate microservice), and **Redis** (conversation memory). New concepts: microservice separation, private networking (no published port!), and one compose file running it all.

#### What an agent actually is

An agent is an LLM that doesn't just answer — it *does things*. It thinks, picks up a tool, checks the result, and keeps going.

Think of the architecture as an office: the *agent = the manager* (decides what needs doing), *tools = the departments* (they do the actual work), and *Redis = the office register* (remembers who said what).

Why three separate boxes? Because in production, the tools team is different from the agent team. You update the tools without touching the agent. That's *microservices* — and without Docker, microservices are just a slide in a deck.

> **Analogy:**
> #### What is Redis, in 30 seconds?
>
> Redis is a super-fast "sticky-note board" database: you store values under names (*key → value*) and read them back in microseconds. Here it remembers each conversation: key = the session ID, value = the message history. Why not a Python variable? Because containers die and restart — a variable dies with them. Redis in its own container (with a volume) means the agent can crash, restart, and still remember you. Someone already packed the Redis tiffin: you just write `image: redis:7-alpine`.

#### 📁 Structure + the tools service

```pseudo title="Terminal"
CREATE folder deskbuddy, then move into it
CREATE folders agent and tools
CREATE empty files docker-compose.yml and .env.example
CREATE empty files agent/app.py, agent/requirements.txt and agent/Dockerfile
CREATE empty files tools/app.py, tools/requirements.txt and tools/Dockerfile
```

```python reveal title="Terminal"
mkdir deskbuddy && cd deskbuddy
mkdir agent tools
touch docker-compose.yml .env.example
touch agent/app.py agent/requirements.txt agent/Dockerfile
touch tools/app.py tools/requirements.txt tools/Dockerfile
```

**In plain words:** two subfolders = two separate services, each with its OWN code, OWN requirements, OWN Dockerfile. This is the microservice idea made physically visible in the folder structure. Redis needs no folder — it's a ready-made image.

```pseudo title="tools/app.py — two simple tools"
CREATE app = FastAPI titled "DeskBuddy Tools"
DEFINE Calc: expression (text)

DEFINE calculator(c: Calc):   // route POST /calculator
    TRY:
        // demo only: eval can run any code, so use a safe expression parser in production
        RUN eval on c.expression, with no built-in names available
        RETURN {"result": the answer}
    ON ERROR:
        RETURN {"error": the error message as text}

DEFINE now():   // route GET /datetime
    RETURN {"now": the current date and time, as ISO text}
```

> **Imported:**
> - `FastAPI` from `fastapi`: creates the tools web app.
> - `BaseModel` from `pydantic`: the base class for `Calc`, the input that holds the expression.
> - `datetime` Python standard library: gives the current date and time for the clock endpoint.

```python reveal title="tools/app.py — two simple tools"
from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI(title="DeskBuddy Tools")

class Calc(BaseModel):
    expression: str

@app.post("/calculator")
def calculator(c: Calc):
    try:
        # demo only - never use eval in production!
        return {"result": eval(c.expression, {"__builtins__": {}})}
    except Exception as e:
        return {"error": str(e)}

@app.get("/datetime")
def now():
    return {"now": datetime.datetime.now().isoformat()}
```

**In plain words:** the tools service is just another tiny FastAPI app with two endpoints: a calculator (evaluates a math expression) and a clock. Nothing AI about it — it's a plain worker department. Why does an LLM need a calculator at all? Because LLMs predict text; they're famously unreliable at arithmetic. Giving them a calculator is like giving an eloquent manager an actual accountant. Its Dockerfile is the same 6 lines as always, ending in uvicorn on port 7000. **⚠️ Note the comment:** `eval` is fine for a classroom demo and dangerous in production — it can execute arbitrary code. In a real service you'd use a safe expression parser instead.

#### 🧠 The agent — the think → act → observe loop

```pseudo title="agent/app.py — the heart of it"
CREATE r = a Redis connection, host from REDIS_HOST (default redis), port 6379, returning text instead of bytes
SET TOOLS_URL = the TOOLS_URL setting, or tools:7000 if it is not set

DEFINE chat(req):   // route POST /chat
    SET key = "history:" + the session_id
    LOAD every stored message for key from Redis, decoding each one   // the memory
    ADD the user's message to history
    REPEAT up to 5 times:   // the agent loop
        CALL the model (gpt-4o-mini) with history and the TOOL_DEFS menu
        SET msg = the model's reply
        IF msg has no tool calls THEN
            stop the loop   // no tool needed, so we are done
        ADD msg to history, leaving out empty fields
        FOR EACH tool call in msg:   // run each requested tool
            CALL call_tool with the tool's name and arguments
            ADD the tool's result to history as JSON
// the code ends with a comment: save the history back to Redis, then return the final answer
```

```python reveal title="agent/app.py — the heart of it"
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
TOOLS_URL = os.getenv("TOOLS_URL", "http://tools:7000")

@app.post("/chat")
def chat(req: Chat):
    key = f"history:{req.session_id}"
    history = [json.loads(m) for m in r.lrange(key, 0, -1)]   # load memory
    history.append({"role": "user", "content": req.message})

    for _ in range(5):                                  # the agent loop
        resp = llm.chat.completions.create(
            model="gpt-4o-mini", messages=history, tools=TOOL_DEFS)
        msg = resp.choices[0].message
        if not msg.tool_calls:                            # no tool needed?
            break                                         # then we're done
        history.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:                        # run each requested tool
            result = call_tool(tc.function.name, json.loads(tc.function.arguments))
            history.append({"role": "tool", "tool_call_id": tc.id,
                            "content": json.dumps(result)})

    # save memory back to redis, return final answer
```

**In plain words:** the loop is the whole magic of "agents", and it's just 10 lines. Each cycle: (1) show the LLM the full conversation plus a menu of available tools (`TOOL_DEFS` describes each tool's name and inputs — the menu card); (2) the LLM either answers in words — done, break — or replies "please run calculator with 23*47 for me"; (3) you actually call the tools service over HTTP, paste the result back into the conversation, and go around again so the LLM can see what happened. Max 5 laps so a confused model can't loop forever (a "safety fuse"). Memory: before the loop you load this session's history from Redis; after, you save it back — that's how a follow-up like "now double it" works.

**Look at the two addresses:** `http://tools:7000` and `host="redis"`. Again — service names, not IPs. By project 3 this should feel natural.

> **Analogy:**
> #### The full thali — 3-service compose
>
> ```pseudo title="docker-compose.yml"
> DEFINE services:
>     agent:
>         BUILD the image from ./agent
>         PUBLISH port 9000 on my Mac, port 9000 inside the container
>         LOAD .env as environment variables
>         SET TOOLS_URL to the tools service on port 7000, and REDIS_HOST to redis
>         START after tools and redis   // start order only, not readiness
>         RESTART unless stopped
>     tools:
>         BUILD the image from ./tools
>         PUBLISH no port   // nothing outside the private network can reach it
>         RESTART unless stopped
>     redis:
>         use the ready-made image redis:7-alpine
>         STORE its data in the volume agent_memory
> DEFINE volume agent_memory   // Docker creates and keeps it
> ```
>
> ```python reveal title="docker-compose.yml"
> services:
>   agent:
>     build: ./agent
>     ports:
>       - "9000:9000"
>     env_file: .env
>     environment:
>       - TOOLS_URL=http://tools:7000
>       - REDIS_HOST=redis
>     depends_on: [tools, redis]
>     restart: unless-stopped
>
>   tools:
>     build: ./tools
>     restart: unless-stopped
>     # NOTE: no ports! Explained below - this is the security gem
>
>   redis:
>     image: redis:7-alpine
>     volumes:
>       - agent_memory:/data
>     restart: unless-stopped
>
> volumes:
>   agent_memory:
> ```
>
> What's new here
>
> - **build: ./agent** — Each service builds from its own subfolder's Dockerfile. One compose file, two custom images, one ready-made.
> - **tools: (no ports!)** — The security gem. No `ports` section = no street gate = the outside world **cannot reach it at all**. Only fellow residents of the private network (the agent) can call it at `tools:7000`. Try `curl localhost:7000` from your Mac — connection refused, *by design*. "Never give internal departments a public entrance." One tiny omission; gold in interviews and in production.
> - **redis:7-alpine** — "alpine" = built on a tiny 5MB Linux. Whole Redis image ≈ 40MB.
> - **agent_memory volume** — Same trick as Chroma: conversation memory survives container death.
>
> Note what you did **not** need here: the retry-loop lesson doesn't bite, because the Redis client only connects when first used (lazily), and Redis boots in under a second. `restart: unless-stopped` is the seatbelt anyway.

#### Milestone #3 — The agent in action + memory proof

Split your terminal in two. Left: `docker compose logs -f`. Right: the curls. You'll watch requests ripple across three containers live.

```pseudo title="Terminal"
copy .env.example to .env   // real key inside, same as before
RUN docker compose up -d --build   // build if needed, then start all services
SHOW docker compose ps -a
SEND a POST to localhost:9000/chat, session "demo", asking "What is 23*47, and what time is it right now?"
SEND a second POST to localhost:9000/chat, same session "demo", asking "Now double that multiplication result"
SHOW the logs of all services, live   // docker compose logs -f
```

```python reveal title="Terminal"
cp .env.example .env         # real key inside, same as before
docker compose up -d --build
docker compose ps -a

curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "What is 23*47, and what time is it right now?"}'

curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "Now double that multiplication result"}'

docker compose logs -f
```

What to watch for

- **First curl** — A two-tool task on purpose: the agent must call BOTH calculator and clock, then compose one answer. Watch the loop go around twice in the logs.
- **Second curl** — Same session_id = same Redis key = the agent remembers 1081 from a minute ago and answers 2162. Change session_id to "other" and ask again — no memory. That's isolation per user, for free.
- **docker compose logs -f** — All three services' diaries interleaved, colour-coded by name. This is how you debug multi-service systems.

**The point:** three services, one command, real memory, proper isolation. And this exact compose file works unchanged on an EC2 instance — *same commands, same result*. That bridge from laptop to production is Docker's superpower.

#### ✅ Self-check — Port 3

- 3 containers running (`docker compose ps -a`)
- The agent answered using a tool call
- The memory demo worked — my follow-up used prior context
- I can explain why `curl localhost:7000` fails on purpose
- I can draw the 3-service architecture from memory on paper

PORT 4

## Cheatsheet, Golden Rules & Debugging

This is the section to keep open on a second screen while you work. Search the cheatsheet, follow the debug tree when something breaks, and re-read the golden rules before any interview.

#### 📋 The cheatsheet — search it

Filter commands… try: volume, logs, compose

| Command | What it does | Tiffin translation |
| --- | --- | --- |
| `docker build -t name:tag .` | Build an image from the Dockerfile here | Pack the master box from the recipe |
| `docker run -d -p 8000:8000 img` | Start a container, background, map ports | Deliver the tiffin, set the gate |
| `docker ps` / `docker ps -a` | Running containers / ALL incl. dead ones | Today's deliveries / the full register |
| `docker logs -f name` | Stream a container's output live | The box's diary |
| `docker exec -it name bash` | Open a shell inside a running container | Step inside the box |
| `docker images` | List all images on your machine | The shelf of master tiffins |
| `docker rm -f name` | Force-remove a container, even if running | Recall the delivery immediately |
| `docker compose up -d --build` | Rebuild if needed + start all services | Serve the thali (fresh) |
| `docker compose ps -a` | This project's containers, incl. exited | Which dishes made it, which didn't |
| `docker compose exec app CMD` | Run a one-off command in a live service | Ask the chef mid-service |
| `docker compose down` | Stop + delete containers (volumes safe) | Clear the thali, keep the steel boxes |
| `docker compose down -v` | …and delete volumes too ⚠️ data gone | Scrap the steel boxes |
| `docker compose logs -f` | All services' logs together | CCTV over the whole kitchen |
| `docker compose up -d --force-recreate` | Recreate containers (e.g. after .env edits) | Fresh boxes, same recipe |
| `docker volume ls` | List volumes on your machine | Count the steel dabbas in stock |
| `docker system df` | How much disk Docker is eating | Check the pantry weight |
| `docker system prune -a` | Delete unused images/containers (careful!) | Diwali deep-clean 🧹 |
| `docker run --platform linux/amd64` | The Mac ARM fix | Dubbing for another audience |
| `docker history image` | Show every layer + the command that made it | Read the recipe backwards (and find leaked secrets) |
| `lsof -i :8000` | Find which process is holding a port | Who's blocking the gate? |

#### The golden rules — read these before any interview

1. **The image is a photograph, not a mirror.** Edited a file? Rebuild: `docker compose up -d --build`.
2. **`ps` hides the dead.** Service missing? `ps -a`, then `logs <service>`.
3. **Started ≠ ready.** `depends_on` waits for the container, not the service inside. Retry in code or add a healthcheck.
4. **Internal ports for neighbours, published ports for visitors.** Container→container uses the internal port.
5. **Secrets are PINs.** .env + env_file at runtime; never ENV in a Dockerfile, never commit .env.
6. **.env changed? Recreate.** Env vars load at container start: `--force-recreate`.
7. **No `ports:` = no public entrance.** Internal services should stay internal.
8. **Rarely-changing layers on top.** That's the whole caching game.
9. **See `quote>` in zsh?** You pasted a # comment. Ctrl+C, re-run without it.

#### 🧭 The debug decision tree — follow it top to bottom

When something breaks, don't guess. Walk this:

Something is broken. │ ├─ Does docker ps show my container? │ ├─ NO → run docker ps -a (or compose ps -a) │ │ ├─ Status "Exited" → docker logs <name> ← the answer is in here │ │ │ ├─ "Connection refused" → started ≠ ready, or wrong port/host │ │ │ ├─ "KeyError / missing key" → .env not loaded → --force-recreate │ │ │ └─ Python traceback → your code, not Docker. Fix, then --build │ │ └─ Not listed at all → the build failed. Scroll up in the build output. │ └─ YES → keep going ↓ │ ├─ Can I reach it from my Mac (curl localhost:PORT)? │ ├─ NO → check three things, in order: │ │ 1. Is there a -p / ports: line at all? (no ports = private, by design) │ │ 2. Is the LEFT number the one I'm curling? (host:container) │ │ 3. Does the app bind to 0.0.0.0, not 127.0.0.1? │ └─ YES → keep going ↓ │ ├─ Can container A reach container B? │ ├─ NO → am I using the SERVICE NAME as host (not localhost)? │ │ am I using the INTERNAL port (not the published one)? │ │ are both services in the same compose file? │ └─ YES → keep going ↓ │ └─ Is my code change showing up? ├─ NO → you rebuilt? docker compose up -d --build │ edited .env? docker compose up -d --force-recreate └─ YES → it's a logic bug now. Congratulations, that's your job. 🙂

#### Top Mac errors and their fixes

1. **"Cannot connect to the Docker daemon"** → Docker Desktop isn't open. Launch it, wait for the whale.
2. **"port is already allocated"** → find the culprit with `lsof -i :8000`, or map another port: `-p 8080:8000`.
3. **App container missing from `ps`** → it crashed: `ps -a` then `logs app`.
4. **Platform warning (arm64/amd64)** → add `--platform linux/amd64`.
5. **Build very slow / disk full** → `docker system df`, then `docker system prune`.
6. **Edits not showing up** → rebuild: `up -d --build`.
7. **Stuck at `quote>`** → Ctrl+C, re-run without the trailing comment.

#### 🏋️ Practice challenges — do at least two

1. **Warm-up** — Push the QuickBite ETA image to Docker Hub (`docker tag` + `docker push`).
2. **Medium** — Replace ScalerGPT's retry loop with a compose `healthcheck` on chroma + `depends_on: condition: service_healthy`. Write two lines on which approach you'd pick and why.
3. **Hard** — Add a *weather* tool to DeskBuddy by updating ONLY the tools service — no agent rebuild. This proves you understood microservices.
4. **Boss level** — Multi-stage builds on all three projects; cut image sizes by 40%. Record before/after from `docker images`.
5. **Bonus** — Break something on purpose (wrong port, missing .env, edit without rebuild), then fix it using only the debug tree above. This is the fastest way to make the knowledge stick.

REVISE
