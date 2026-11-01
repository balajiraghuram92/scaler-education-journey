# The Dabbawala Analogy + Mac Setup

> **Lesson resources · Lesson 5 · Dockerize everything:**
> - [Watch the Class 5 recording](https://www.scaler.com/meetings/i/ai-infused-learning-5/archive)
> - </> Browse the code (GitHub link coming soon)
> - [⬇ Download all](/downloads/ai-engineering/Class-5-AI-infusion.zip)

FUTURE WITH SHIVANK · STUDENT REVISION GUIDE

#### Dockerize Everything: ML → LLM → Agents

Everything from the masterclass, rebuilt for revision. Three real projects, every command decoded word by word, and one tiffin-delivery analogy you'll never forget. 🍱 Read it, run it, then test yourself at the bottom.

🔰 No prior Docker needed 💻 macOS (Apple Silicon ready) 🐳 Docker Desktop + Compose ✅ Battle-tested code 🧪 30 self-test questions

#### 📖 How to use this guide

This is a revision document, not a video transcript. It works best if you go through it three times, with your terminal open beside it.

**Pass 1 — Read** Skim top to bottom without typing anything. Goal: recognise the vocabulary. Image, container, volume, compose, service name.

**Pass 2 — Build** Rebuild all three projects from scratch, copying commands from here. Tick the self-check boxes as you go.

**Pass 3 — Recall** Close this page. Try the flashcards and interview questions at the bottom from memory. Whatever you miss, that's your revision list.

Every command block has a **Copy** button. Every command block is followed by a decoder that explains each flag — don't skip those, they're where the marks are.

PORT 0

## The Dabbawala Analogy + Mac Setup

**What you'll get:** a rock-solid mental model of Docker before you write a single command, plus a working setup on your Mac. By the end of Port 0 you should have run `hello-world` and be able to explain what actually happened.

#### Why Docker exists at all

You've said it, or you will: *"But it works on my machine!"* The code crashes on your teammate's laptop, crashes on staging, and let's not talk about production.

Mumbai's dabbawalas deliver 200,000 lunch boxes every single day with Six Sigma accuracy — without an app. How? They *standardised the packaging and the delivery system*. It doesn't matter where a tiffin comes from or where it's going; the system is identical. *Docker is the dabbawala system for software.*

In this guide you'll dockerize three real projects — a classic ML model, an LLM-powered RAG app, and a multi-agent system. Same skill, three difficulty levels.

> **⭐ The most important rule in this entire guide:**
> #### The Master Analogy — The Tiffin System 🍱
>
> Come back to this table every time a new term confuses you. If you memorise one thing from the whole session, memorise this:
>
> | Docker Concept | Tiffin World | One-line meaning |
> | --- | --- | --- |
> | **Dockerfile** | Recipe card 📝 | Step-by-step written instructions for how to prepare the meal. |
> | **Image** | Master tiffin (sealed, ready) 🍱 | The packed box produced from the recipe — frozen in time, ready to ship. |
> | **Container** | One delivered tiffin 🚚 | A running copy of the image. One image can produce a hundred tiffins. |
> | **Docker Hub** | Central kitchen / warehouse 🏭 | Where ready-made boxes for every recipe live — Python's, Ubuntu's, Redis's. |
> | **Port mapping** | The building's gate number 🚪 | The box lives in flat 8000 inside the building, but deliveries come through gate 8000 — `-p 8000:8000`. |
> | **Volume** | The steel box that comes back ♻️ | Delete the container, the data survives — like the reusable steel dabba. |
> | **docker compose** | Ordering a full thali 🍽️ | One order gets you dal, rice, sabzi, roti — all containers together. |
>
> **"An image is a photograph, not a mirror."** When you build an image, Docker takes a *photo* of your code at that moment. If you edit your code afterwards, the photo does NOT update by itself — you must take a new photo (rebuild). Forgetting this causes 90% of beginner confusion, so it's repeated throughout.

#### 🖼️ VM vs Docker — the one diagram to hold in your head

Picture two kinds of housing:

- **Virtual Machine = a standalone bungalow.** Every app gets an entire house: its own kitchen, bathroom, and security guard (a full operating system). Heavy, slow to start, expensive.
- **Docker = apartment flats.** One building (the host operating system's core) is shared, but every flat (container) has its own lock, its own belongings, its own privacy. Lightweight, starts in seconds.

**The punchline:** a VM takes minutes to boot; a container takes milliseconds. That's why at Swiggy/Zomato scale you don't run VMs — you run containers. Traffic spike? Open 50 new flats in seconds.

#### 💻 Mac setup — do this first

Open **Terminal** (press `Cmd + Space`, type "Terminal", press Enter). If the terminal is new to you: it's just a way to talk to your computer with text instead of clicks. You type a command, press Enter, the computer replies.

```pseudo title="Terminal — install & verify"
RUN brew install --cask docker   // install Docker Desktop (--cask = a full desktop app)
RUN docker --version   // check that Docker is installed
RUN docker compose version   // check that Compose is installed
RUN docker run hello-world   // download hello-world if needed, then run it as a container
```

```python reveal title="Terminal — install & verify"
brew install --cask docker

docker --version
docker compose version
docker run hello-world
```

Command decoder — what each piece means

- **brew** — Homebrew — the "app store for your terminal" on Mac. It downloads and installs software for you. No Homebrew? Download the .dmg from docker.com/products/docker-desktop instead.
- **--cask** — Tells brew this is a full desktop application (with an icon), not just a command-line tool.
- **docker --version** — Asks Docker "which version are you?" If it answers, Docker is installed correctly.
- **docker compose version** — Checks the second tool you'll use — Compose — which manages multiple containers at once. It comes bundled with Docker Desktop.
- **docker run hello-world** — "Run a container from the image called hello-world." Docker looks for it on your Mac, doesn't find it, downloads it from Docker Hub, and runs it. Your first tiffin, delivered from the central kitchen.

**⚠️ The step most people miss:** after installing, **open the Docker Desktop app once** (Cmd+Space → "Docker" → Enter). A whale 🐳 icon appears in the menu bar at the top of the screen. Docker commands only work while that whale is there — the app runs the Docker "engine" in the background. No whale = every command fails with *"Cannot connect to the Docker daemon"*. ("Daemon" is just an old Unix word for a background program.)

When `hello-world` prints *"Hello from Docker!"* — you have just pulled an image from Docker Hub and turned it into a running container. First tiffin delivered. 🎉

#### Two Mac traps to know before they hit you

##### Trap 1: Apple Silicon chips speak a different language

M-series Macs (M1/M2/M3/M4) use the **ARM64** chip architecture; most cloud servers use **AMD64 (x86)**. Think of it as two languages: an image "written in AMD64" may not run on an ARM Mac. Sometimes an image downloads fine but refuses to start, or prints a platform warning.

```pseudo title="The fix when you hit a platform error"
RUN <image-name> as a linux/amd64 container   // pretend to be an AMD64 machine; the Mac translates on the fly
```

```python reveal title="The fix when you hit a platform error"
docker run --platform linux/amd64 <image-name>
```

Command decoder

- **--platform linux/amd64** — "Pretend to be an AMD64 machine." Your Mac translates on the fly (via Rosetta). Like watching a dubbed movie — slightly slower, but it works.

##### Trap 2: zsh and the stuck `quote>` prompt

The Mac terminal uses a shell called **zsh**. If you paste a command that has a `#` comment at the end AND that comment contains an apostrophe (like *you'll*), zsh gets confused and shows `quote>`, waiting forever. **Fix: press Ctrl+C and re-type the command without the comment.** Remember this one — it saves ten minutes the first time it happens.

#### ✅ Self-check — Port 0

- Docker Desktop is running (whale 🐳 steady in my menu bar)
- `docker run hello-world` succeeded on my machine
- I can recite 3 mappings from the tiffin analogy without looking
- I can explain "an image is a photograph, not a mirror" to someone else
- I can say the difference between a VM and a container in one sentence

PORT 1

## Dockerize an ML Project — "QuickBite ETA" 🛵

**What you'll build:** a sklearn model (a food-delivery ETA predictor) served via FastAPI, packed into a container. This is where the **core fundamentals** live: Dockerfile anatomy, layers, caching, port mapping, .dockerignore.

#### The situation you're solving

Imagine you're an ML engineer at a Zomato-style startup. You've built a model that predicts *how many minutes until an order arrives* — distance, restaurant prep time, rider availability, rain as inputs; ETA as output.

The model runs beautifully on your laptop. Then DevOps says: *"Ship it to the server."* The server has Python 3.9; you have 3.12. Different sklearn version. Don't even ask about NumPy. Welcome to dependency hell 🔥 — and Docker is the air conditioning.

#### 📁 Project structure

Build the skeleton first:

```pseudo title="Terminal"
CREATE folder quickbite-eta, then move into it
CREATE empty files train.py, app.py, requirements.txt, Dockerfile and .dockerignore
```

```python reveal title="Terminal"
mkdir quickbite-eta && cd quickbite-eta
touch train.py app.py requirements.txt Dockerfile .dockerignore
```

Command decoder

- **mkdir** — "Make directory" — creates a new folder.
- **&&** — "Then" — run the next command only if the first one succeeded.
- **cd** — "Change directory" — step inside that folder.
- **touch** — Creates empty files with these names. You'll fill them in next.

```pseudo title="requirements.txt"
ADD scikit-learn at exactly version 1.5.2   // trains the model
ADD pandas at exactly version 2.2.3   // handles data tables
ADD fastapi at exactly version 0.115.6   // turns Python functions into a web API
ADD uvicorn at exactly version 0.34.0   // the web server that runs FastAPI
ADD joblib at exactly version 1.4.2   // saves and loads the model file
```

```python reveal title="requirements.txt"
scikit-learn==1.5.2
pandas==2.2.3
fastapi==0.115.6
uvicorn==0.34.0
joblib==1.4.2
```

**In plain words:** this file is your shopping list. Python doesn't come with these tools built in, so you list exactly which extra packages you need and *exactly which version* of each. **scikit-learn** trains the model, **pandas** handles data tables, **FastAPI** turns Python functions into a web API, **uvicorn** is the web server that actually runs FastAPI, and **joblib** saves/loads the trained model to a file. Pinning versions with `==` is like writing "1 cup of rice" in a recipe instead of "some rice" — you get the same dish every time.

#### 🤖 train.py — a 60-second model

```pseudo title="train.py"
SET the random seed to 42   // same random numbers on every run
SET n = 5000
CREATE a table df with n fake orders, each with:
    distance_km       a random number from 0.5 to 12
    prep_time_min     a random number from 5 to 30
    rider_available   a random 0 or 1
    is_raining        a random 0 or 1
SET eta_min = 8 + distance_km * 3 + prep_time_min * 0.7 + is_raining * 9 + (1 - rider_available) * 6 + random noise   // the "true" ETA
SET X = every column of df except eta_min
SET y = the eta_min column
CREATE a RandomForestRegressor with 60 trees and random_state 42, then train it on X and y
SAVE the model to eta_model.pkl
PRINT "Model saved: eta_model.pkl ✅"
```

> **Imported:**
> - `pandas` (as `pd`) third-party package `pandas`: builds the table of fake orders.
> - `numpy` (as `np`) third-party package `numpy`: makes the random numbers and the noise.
> - `joblib` third-party package `joblib`: saves the trained model to `eta_model.pkl`.
> - `RandomForestRegressor` from `sklearn.ensemble`, package scikit-learn: the model that learns the ETA pattern as an average of 60 trees.

```python reveal title="train.py"
import pandas as pd, numpy as np, joblib
from sklearn.ensemble import RandomForestRegressor

np.random.seed(42)
n = 5000
df = pd.DataFrame({
    "distance_km": np.random.uniform(0.5, 12, n),
    "prep_time_min": np.random.uniform(5, 30, n),
    "rider_available": np.random.randint(0, 2, n),
    "is_raining": np.random.randint(0, 2, n),
})
# ETA = base + distance*3 + prep + rain penalty + rider penalty + noise
df["eta_min"] = (8 + df.distance_km*3 + df.prep_time_min*0.7
                 + df.is_raining*9 + (1-df.rider_available)*6
                 + np.random.normal(0, 2, n))

X, y = df.drop(columns=["eta_min"]), df["eta_min"]
model = RandomForestRegressor(n_estimators=60, random_state=42).fit(X, y)
joblib.dump(model, "eta_model.pkl")
print("Model saved: eta_model.pkl ✅")
```

**In plain words:** you invent 5,000 fake food orders (so the demo is fast and needs no real dataset). For each order you compute a "true" delivery time with a simple formula: rain adds ~9 minutes, no rider available adds ~6, every km adds ~3. Then you train a RandomForest — think of it as *60 junior analysts each making a guess, and you take their average* — to learn that pattern. Finally `joblib.dump` saves the trained brain into a single file, `eta_model.pkl`, so the API can load it later without retraining. The `seed(42)` line means "use the same randomness every time" so your results match everyone else's.

#### 🚀 app.py — FastAPI serving

```pseudo title="app.py"
CREATE app = FastAPI titled "QuickBite ETA"
LOAD the model from eta_model.pkl   // once, when the server starts
DEFINE Order: distance_km and prep_time_min as numbers, rider_available and is_raining as whole numbers

DEFINE health():   // route GET /
    RETURN {"status": "QuickBite ETA is live 🛵"}

DEFINE predict(order: Order):   // route POST /predict
    SET X = the order as a one-row table
    SET eta = the model's prediction for X, rounded to 1 decimal place
    RETURN {"eta_minutes": eta, "message": "Your food arrives in {eta} min 🍔"}
```

> **Imported:**
> - `FastAPI` from `fastapi`: creates the web app that the routes are attached to.
> - `BaseModel` from `pydantic`: the base class for the `Order` form. It checks the type of each field.
> - `joblib` third-party package `joblib`: `joblib.load` reads the trained model back from `eta_model.pkl`.
> - `pandas` (as `pd`) third-party package `pandas`: turns the order into a one-row table for the model.

```python reveal title="app.py"
from fastapi import FastAPI
from pydantic import BaseModel
import joblib, pandas as pd

app = FastAPI(title="QuickBite ETA")
model = joblib.load("eta_model.pkl")

class Order(BaseModel):
    distance_km: float
    prep_time_min: float
    rider_available: int
    is_raining: int

@app.get("/")
def health():
    return {"status": "QuickBite ETA is live 🛵"}

@app.post("/predict")
def predict(order: Order):
    X = pd.DataFrame([order.model_dump()])
    eta = round(float(model.predict(X)[0]), 1)
    return {"eta_minutes": eta, "message": f"Your food arrives in {eta} min 🍔"}
```

**In plain words:** this file is the *counter window* of your shop. An "API" is just a way for programs to talk to each other over the network — you send a request, you get a response. FastAPI lets you say "when someone sends order details to the address `/predict`, run this Python function." The `Order` class is the order form: it declares exactly which fields a request must contain and their types — send text where a number belongs and FastAPI politely rejects it *for free*. At startup you load the saved model brain from `eta_model.pkl` once; then every request is: read form → ask model → return the answer as JSON (the universal "key: value" text format APIs speak). The `/` route is a health check — a doorbell to confirm the shop is open.

> **🔑 The caching trick — why requirements.txt goes first:**
> #### Dockerfile anatomy — learning to read the recipe
>
> This is the **most important block** in the guide. A Dockerfile is a plain text file (no extension!) with instructions Docker executes top to bottom to produce an image. Map every line to the tiffin analogy:
>
> ```pseudo title="Dockerfile"
> begin with the ready-made image python:3.12-slim   // Linux with Python 3.12 already installed
> SET the working folder to /app
> copy requirements.txt into /app   // first, so the pip layer can be cached
> RUN pip install -r requirements.txt   // no download cache kept, so the image stays smaller
> copy the whole project folder into /app   // skips anything listed in .dockerignore
> RUN python train.py   // train now, so eta_model.pkl is baked into the image
> document that the app listens on port 8000   // a label only, it opens nothing
> when a container starts, run uvicorn app:app on host 0.0.0.0, port 8000
> ```
>
> ```python reveal title="Dockerfile"
> # 1. Base image = rent a ready-made kitchen (from Docker Hub)
> FROM python:3.12-slim
>
> # 2. Set up your counter inside that kitchen
> WORKDIR /app
>
> # 3. Copy ONLY the shopping list first (caching trick — explained below)
> COPY requirements.txt .
> RUN pip install --no-cache-dir -r requirements.txt
>
> # 4. NOW copy the rest of your code
> COPY . .
>
> # 5. Train the model INSIDE the image (baked in at build time)
> RUN python train.py
>
> # 6. Declare which window the food comes out of (documentation)
> EXPOSE 8000
>
> # 7. What runs the moment the tiffin is opened
> CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
> ```
>
> Line-by-line decoder
>
> - **FROM python:3.12-slim** — Don't start from an empty computer — start from a ready-made image that already has Linux + Python 3.12 installed. "slim" = the lightweight version. Docker downloads it from Docker Hub automatically.
> - **WORKDIR /app** — "From now on, work inside the folder /app" (inside the container). Creates it if missing. Like choosing which counter you'll cook on.
> - **COPY requirements.txt .** — Copy one file from your Mac into the image. The `.` means "into the current folder" (which is /app because of WORKDIR).
> - **RUN pip install ...** — RUN executes a command *while building* the image. pip is Python's package installer; `-r requirements.txt` means "install everything on this list". `--no-cache-dir` tells pip not to keep downloaded files around — smaller image.
> - **COPY . .** — "Copy everything in the current folder on my Mac → into /app in the image." (Everything except what .dockerignore excludes.)
> - **RUN python train.py** — Trains the model during the build, so the finished image already contains eta_model.pkl. The container never needs to train anything.
> - **EXPOSE 8000** — A label saying "this app listens on port 8000". It's documentation — it doesn't open anything by itself (that's `-p`'s job later).
> - **CMD [...]** — The one command that runs when a container starts. Here: start the uvicorn web server, serving the `app` object from `app.py`. `--host 0.0.0.0` means "accept connections from outside the container, not just from inside" — without it, port mapping silently fails. A classic gotcha.
>
> Picture a stack of layers (like a stack of parathas 🫓). Docker turns each instruction into a **layer** and caches it. When you rebuild, Docker checks each layer top-down: "did anything this layer depends on change?" If not, it reuses the cached layer instantly. But the moment one layer changes, **every layer below it must rebuild too**.
>
> Now the logic clicks: if you did `COPY . .` first and installed dependencies after, then *every tiny code edit* would invalidate the copy layer — and force the slow 2-minute pip install to re-run below it. By copying only `requirements.txt` first, the pip layer only rebuilds when the shopping list itself changes.
>
> **The rule to remember:** if the shopping list hasn't changed, why go back to the store? Code changes daily; dependencies change monthly. *Rarely-changing things at the top, frequently-changing things at the bottom.* This one trick makes builds 10x faster.

#### 🙈 .dockerignore

```pseudo title=".dockerignore"
// COPY . . skips everything listed in this file
skip __pycache__/ folders and *.pyc files
skip venv/ and .venv/ folders
skip the .git/ folder
skip .env   // keeps secrets out of the image
skip *.ipynb notebooks
skip eta_model.pkl   // the image trains its own fresh copy
skip data/raw/ folder
```

```python reveal title=".dockerignore"
__pycache__/
*.pyc
venv/
.venv/
.git/
.env
*.ipynb
eta_model.pkl
data/raw/
```

**In plain words:** when Docker sees `COPY . .`, it grabs *everything* in the folder — unless it's listed here. Same idea as .gitignore. You exclude: Python's junk cache files, virtual environments (can be 500MB!), git history, secrets (.env), and notebooks. You also exclude `eta_model.pkl` — if you ever trained locally, you do NOT want that stale local file copied in; the image trains its own fresh copy in step 5. "Only the food goes into the tiffin — not your diary and house keys."

#### Milestone #1 — Build, run, predict

```pseudo title="Terminal — the big moment"
BUILD an image from the Dockerfile in this folder, tagged quickbite-eta:v1
SHOW all images on this machine
RUN a container in the background, port 8000 on my Mac to port 8000 inside, named eta-service
SEND a POST to localhost:8000/predict, with a JSON header and one order as the data
```

```python reveal title="Terminal — the big moment"
docker build -t quickbite-eta:v1 .

docker images

docker run -d -p 8000:8000 --name eta-service quickbite-eta:v1

curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"distance_km": 4.5, "prep_time_min": 15, "rider_available": 1, "is_raining": 1}'
```

Command decoder — slow down and read every line here

- **docker build** — "Follow the Dockerfile recipe and produce an image."
- **-t quickbite-eta:v1** — "Tag" — give the image a name and a version label (name:version). Without it you get an unmemorable ID like a7f3c9.
- **.** — The lonely dot means "the recipe and files are in THIS folder." Forgetting the dot is the #1 first-day error.
- **docker images** — List all images (master tiffins) stored on your machine.
- **docker run** — "Create and start a container from this image."
- **-d** — "Detached" — run in the background and give my terminal back. Without -d, the logs take over your terminal until you press Ctrl+C (which also stops the container!).
- **-p 8000:8000** — Port mapping, format **host:container** — "connect gate 8000 of my Mac to flat 8000 inside the container." Traffic to localhost:8000 gets forwarded inside.
- **--name eta-service** — A friendly name so you can say "eta-service" in later commands instead of a random ID.
- **curl** — A terminal tool for sending web requests — a browser without the window.
- **-X POST** — The request type. GET = "give me something", POST = "here's data, process it."
- **-H "Content-Type..."** — A header telling the server "the data I'm sending is JSON."
- **-d '{...}'** — The data itself — one order, as JSON. The backslash `\` at line ends just means "command continues on the next line."

The response comes back as `{"eta_minutes": 41.2, ...}`. Now open **http://localhost:8000/docs** in your browser: FastAPI auto-generates a clickable "Swagger" page where you can test the API with buttons instead of curl. Flip `is_raining` to 1 and watch the ETA climb. 🌧️

**Notice what you did NOT do on your Mac:** no Python environment, no pip install, no version checking. Everything lives inside the box. And this exact box will run on AWS, on a Windows laptop, anywhere — *identically*.

#### 🛠️ Peek inside the container + your everyday commands

```pseudo title="Terminal — daily-driver commands"
SHOW the running containers
SHOW all containers, including stopped ones   // -a
SHOW the logs of eta-service and follow new lines   // -f; Ctrl+C stops watching, not the container
RUN bash inside eta-service   // -it: an interactive terminal inside the container
STOP eta-service   // the container still exists and can be started again
remove eta-service   // the image is untouched
```

```python reveal title="Terminal — daily-driver commands"
docker ps
docker ps -a
docker logs -f eta-service
docker exec -it eta-service bash
docker stop eta-service
docker rm eta-service
```

Command decoder

- **docker ps** — List **running** containers only. Comes from "process status".
- **docker ps -a** — List ALL containers, including dead/exited ones. ⚠️ Memorise this: if a container crashed, plain `ps` hides it and you'll think it never existed. `-a` = "all".
- **docker logs -f eta-service** — Show everything the container has printed. `-f` = "follow" — keep streaming new lines live (Ctrl+C to stop watching; the container keeps running).
- **docker exec -it ... bash** — "Execute a command inside a running container." The command here is `bash` — a shell — so you get a terminal INSIDE the box. `-it` = interactive + terminal, i.e. "let me type." Try `ls` and `cat app.py` inside, then `exit` to come back out.
- **docker stop / rm** — stop = pause the delivery (container still exists, restartable). rm = remove the stopped container entirely. The image is untouched — you can always run a fresh one.

`docker exec` is the moment it clicks: you are standing inside a tiny, separate Linux world living inside your Mac.

#### The photograph rule in action — try this deliberately

Edit the message string in `app.py`, then restart the container. **Nothing changes.** Why? The container runs the image — the photograph — and the photo was taken before your edit. The fix is always:

```pseudo title="After ANY code edit"
BUILD a fresh image quickbite-eta:v1 from the current code
remove the old eta-service container, even if it is running   // rm -f
RUN a new container in the background, port 8000 to port 8000, named eta-service
```

```python reveal title="After ANY code edit"
docker build -t quickbite-eta:v1 .
docker rm -f eta-service
docker run -d -p 8000:8000 --name eta-service quickbite-eta:v1
```

Rebuild → remove old container (`rm -f` = force-remove even if running) → run fresh. Losing ten minutes to a stale image is a rite of passage. Do it once here on purpose and you'll never lose those ten minutes again.

#### ✅ Self-check — Port 1

- Image built: quickbite-eta shows up in `docker images`
- `/predict` works for me via both curl and Swagger
- I can explain layer caching in one sentence
- I stepped inside with `docker exec` and came back out
- I can answer: "I edited my code, why doesn't the container see it?"
- I can explain why `--host 0.0.0.0` is required in the CMD

PORT 2
