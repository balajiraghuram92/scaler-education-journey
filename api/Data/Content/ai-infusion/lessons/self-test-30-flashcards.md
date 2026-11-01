# Self-test — 30 flashcards

## Self-test — 30 flashcards

Click a card to reveal the answer. Try to say your answer out loud *before* you click — recall is what builds memory, re-reading isn't. Anything you get wrong, go back to that Port.

What is the difference between an image and a container?An image is a sealed, read-only package built from a Dockerfile — the master tiffin. A container is a running instance of that image — one delivered tiffin. One image can produce many containers.click to reveal

You edited app.py and restarted the container. Nothing changed. Why?The container runs the image, and the image is a photograph taken at build time. Your edit isn't in it. Rebuild: `docker compose up -d --build` (or `docker build` + `rm -f` + `run`).click to reveal

In `-p 8080:8000`, which number is the container's?The right one. Format is **host:container**. Your Mac listens on 8080 and forwards to 8000 inside the container.click to reveal

Why must the CMD use `--host 0.0.0.0`?127.0.0.1 inside a container means "only accept traffic that originated inside this container." Port mapping then silently delivers nothing. 0.0.0.0 means "accept from any interface," which lets the mapped port work.click to reveal

Why does requirements.txt get copied before the rest of the code?Layer caching. Docker rebuilds a layer and everything below it when its inputs change. Dependencies change rarely, code changes constantly — so put the pip install above `COPY . .` and you skip the slow install on most rebuilds.click to reveal

What does EXPOSE actually do?Almost nothing at runtime — it's documentation/metadata saying "this app listens here." Actually publishing the port is `-p` or the compose `ports:` key.click to reveal

Difference between RUN and CMD?RUN executes at **build** time and its result is baked into a layer. CMD executes at **container start** and is the default process. A Dockerfile can have many RUNs and one effective CMD.click to reveal

Your container isn't in `docker ps`. What are the next two commands?`docker ps -a` to see it as Exited, then `docker logs <name>` to read why it died. `ps` hides the dead.click to reveal

What is a volume, and what does it survive?Docker-managed storage that lives outside the container's writable layer. It survives `stop`, `rm`, and `compose down`. It does NOT survive `compose down -v` or an explicit `docker volume rm`.click to reveal

Where do you put an API key, and where must you never put it?Put it in a `.env` file loaded at runtime via `env_file:`. Never `ENV KEY=...` in a Dockerfile — `docker history` exposes it — and never commit .env to git.click to reveal

The app says "connection refused" to chroma even though `depends_on` is set. Why?`depends_on` only waits for the container to **start**, not for the service inside to be **ready**. Fix with a retry loop in code, or a compose `healthcheck` + `condition: service_healthy`.click to reveal

Chroma is published as `"8001:8000"`. Which port does the app container use?8000 — the internal one. Containers on the same compose network talk flat-to-flat. 8001 is the street gate, useful only from your Mac.click to reveal

How does one container find another by name?Compose creates a private network and registers each service name in its DNS. `http://tools:7000` resolves to the tools container. No IPs, ever.click to reveal

A service in compose has no `ports:` key. Is that a bug?No — it's a security feature. Without published ports the service is unreachable from outside the Docker network. Only sibling containers can call it. Internal services should look exactly like this.click to reveal

What's the difference between `docker stop` and `docker rm`?`stop` halts a running container but keeps it (restartable, logs intact). `rm` deletes the container object. Neither touches the image.click to reveal

What does `docker compose down` delete, and what does it keep?Deletes containers and the network. Keeps images and named volumes. Add `-v` and the volumes go too.click to reveal

You edited .env but the container still uses the old value. Fix?Environment variables are read at container start. `docker compose up -d --force-recreate` to build fresh containers with the new values.click to reveal

What is .dockerignore for, and name three things that belong in it?It excludes files from the build context that `COPY . .` would otherwise pull in. Typical entries: `venv/`, `.git/`, `__pycache__/`, `.env`, notebooks, large raw data.click to reveal

VM vs container in one sentence?A VM virtualises the whole machine and ships an entire OS (bungalow); a container shares the host kernel and isolates only the process and its filesystem (flat). Minutes vs milliseconds to start.click to reveal

Why `chromadb-client` instead of `chromadb` in requirements?The full package includes the database engine itself — heavy. The thin client only talks to a Chroma running elsewhere (its own container). Smaller app image, cleaner separation.click to reveal

What are the three steps of RAG?Retrieve the most relevant chunks from a vector store, augment the prompt by pasting them in, generate the answer with the LLM constrained to that context.click to reveal

Why does the agent need Redis rather than a Python dict?A dict lives in the container's memory and dies with it. Containers restart constantly. Redis + a volume keeps conversation history across crashes, restarts, and redeploys — and lets you scale to multiple agent replicas.click to reveal

Describe the agent loop in one breath.Send conversation + tool menu to the LLM; if it returns no tool call, you're done; otherwise execute the requested tool, append the result to the conversation, and loop again — capped at N iterations so it can't spin forever.click to reveal

Why cap the agent loop at 5 iterations?A confused model can call tools forever, burning tokens and money. The cap is a safety fuse — the same reasoning as a timeout or a circuit breaker.click to reveal

What does `restart: unless-stopped` buy you?Docker restarts the container automatically after a crash or a host reboot, but respects a deliberate `docker stop`. Cheap resilience for free.click to reveal

Two containers, same compose file. One says `localhost:8000` to reach the other. What happens?It fails. Inside a container, `localhost` is that container itself. You must use the other service's name as the hostname.click to reveal

What does `docker exec -it name bash` give you, and when do you use it?A shell inside a running container. Use it to inspect files, check env vars, or confirm what actually got copied in — the fastest way to answer "is my file even in there?"click to reveal

Your Mac says "port is already allocated". Two ways out?Find and stop whatever holds it (`lsof -i :8000`), or publish on a different host port: `-p 8080:8000`. The container side doesn't need to change.click to reveal

Why does an M-series Mac sometimes need `--platform linux/amd64`?Apple Silicon is ARM64; many published images are built for AMD64 only. The flag runs the image under emulation — slower, but it works when no ARM variant exists.click to reveal

One sentence: why does Docker matter for ML and AI work specifically?Because ML/AI stacks are dependency nightmares (CUDA, sklearn, torch, vector DBs) and multi-service by nature — Docker makes the whole stack reproducible and identical from laptop to EC2, which is the difference between a notebook and a product.click to reveal

#### Interview questions you can now answer

These come up in real ML/AI engineering interviews. If you can answer eight of these cleanly, this session did its job.

1. **Explain the Docker build cache and how you'd optimise a slow Dockerfile.** Talk about layers, ordering, `COPY requirements.txt` first, `--no-cache-dir`, and multi-stage builds.
2. **How do you handle secrets in a containerised app?** Runtime injection via env vars / secret managers, never `ENV` in the Dockerfile, `.env` in both ignore files, and `docker history` as the attack you're preventing.
3. **Your service depends on a database that takes 20s to boot. How do you handle startup ordering?** depends_on isn't enough; use healthchecks with `condition: service_healthy`, or application-level retry with backoff. Mention that retry-in-code is more portable across orchestrators.
4. **How do containers discover each other?** Compose/Kubernetes DNS by service name, internal ports, and why hardcoding IPs is wrong.
5. **Container vs VM — when would you still choose a VM?** Different kernel required, strong hardware-level isolation for untrusted workloads, or legacy OS dependencies.
6. **How do you persist state in a stateless system?** Volumes and external stores; containers are cattle, not pets.
7. **How would you make this compose stack production-ready?** Healthchecks, resource limits, non-root user, pinned image digests, logging driver, secrets manager, and moving to an orchestrator.
8. **What's in your image that shouldn't be?** Build tools, .git, credentials, test data, dev dependencies — and how multi-stage builds and .dockerignore fix it.
9. **How do you debug a container that exits immediately?** `ps -a` → `logs` → check the CMD → run it interactively with an overridden entrypoint.
10. **Why doesn't your internal service publish a port?** Attack surface. Only the edge service is reachable; everything else is on the private network.

#### 📚 Glossary — the vocabulary you're now expected to use

- **Image** — A read-only, layered package of your app plus everything it needs to run.
- **Container** — A running instance of an image, isolated from the host and from other containers.
- **Layer** — The filesystem diff produced by one Dockerfile instruction. Cached and reused across builds.
- **Build context** — The folder you pass to `docker build` (the lonely `.`). Everything in it, minus .dockerignore, is sent to the Docker engine.
- **Registry / Docker Hub** — The remote store where images are pushed and pulled from.
- **Tag** — The human-readable `name:version` label on an image.
- **Daemon** — The background engine that actually does the work. Docker Desktop starts it; the whale icon means it's alive.
- **Port publishing** — Mapping a host port to a container port so the outside world can reach in (`-p host:container`).
- **Volume** — Docker-managed storage that outlives containers. For anything you can't afford to lose.
- **Bind mount** — Mapping a host folder straight into a container. Great for live-reload in development, avoided in production.
- **Compose** — A tool that reads one YAML file and runs a whole multi-container application.
- **Service** — One entry in a compose file — and also the DNS name other containers use to reach it.
- **Healthcheck** — A command Docker runs periodically to decide whether a container is actually ready, not just started.
- **Multi-stage build** — Using one image to build and a second, smaller one to run — the standard way to shrink production images.
- **Orchestrator** — The system that runs containers across many machines (Kubernetes, ECS). Compose is the single-machine version of the same idea.

#### 🎬 The one line to remember

"Writing code is half the job. Making it run anywhere in the world — that's engineering. Docker is the box that carries your work to the world."

**Where to go next:** Kubernetes — for when you have 10,000 boxes to manage instead of three. Everything you learned here (images, ports, volumes, service names, readiness) maps directly onto it. You've already done the hard part. 🐳

Self-checks: **0**/0

Made with 🐳 for **Future with Shivank** · Dockerize Everything — Student Revision Guide · Tiffin analogy inspired by the Mumbai Dabbawalas' 130 years of Six Sigma
