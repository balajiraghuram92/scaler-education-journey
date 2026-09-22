# Session Handoff — 2026-09-22

Read this whole file before doing anything else in a new conversation. It captures exact state,
pending work, and hard-won environment gotchas from the previous session so nothing has to be
re-discovered.

## How this project works (read this first if you're a fresh Claude session)

Per `CLAUDE.md` at the repo root: Claude may **only** directly edit `CLAUDE.md`, the memory
directory, `info/.notes/**`, and `exercises/**`. Everything else (`api/`, `app/`, `docker-compose.yml`,
etc.) must be changed by writing a copy-paste-ready prompt into `info/.notes/` for the user to run
through their Local LLM ("Gemini"), then independently re-verified — never trust a self-reported
"done" claim without re-checking it yourself (this discipline mattered enormously this session; see
"Hard lessons" below).

Claude has **direct shell access into the user's real WSL2 Ubuntu environment** via `wsl.exe` (see
"Environment facts" below) — this was discovered and used extensively this session for live
verification, not just relaying commands back and forth.

## Where things stand right now (top-level status)

### Fully done and independently verified this session
1. **Critical build crisis resolved**: `api/Data/JavaVerticalSeedData.cs` had a C# verbatim-string
   quote-escaping bug that broke the entire API build. Fixed and confirmed with a real, clean
   `docker compose build` (zero errors).
2. **Dynamic MCQ system**: fully migrated from static `app/src/data/lessonInteractions.js` to a
   real DB-backed schema (`mcq_questions`, `mcq_options`, `mcq_presentations`, `mcq_attempts`).
   Found and fixed a legacy-alias bug (`02-oop-classes-objects`/`03-oop2-encapsulation-inheritance`
   were pure JS-getter duplicates of two canonical lessons, causing 18 questions to silently vanish
   from every seed run). Final state: **1182 unique questions, 179 lesson groups, zero duplicates**,
   live-verified via real API calls: shuffled option order confirmed across repeated requests, attempt
   recording confirmed, idempotency (retry same presentation → no duplicate row) confirmed.
3. **Parking Lot exercises** (`generate-parking-ticket`, `display-parking-lot-capacity`): real
   `mvn test` run for both solution and starter variants. Solution passes 7/7 both; starter compiles
   but fails as expected (proving the TODO stubs aren't accidentally already-solved).
4. **Spring Boot sandbox runner image** (`runner/java-spring/Dockerfile`,
   `neuralascent-java-spring-runner:dev`): builds cleanly, real smoke test confirms Java 17 runs
   inside it.
5. **Exercise-grading Docker-socket permission bug (fix #1)**: found via a real live
   `POST /api/exercises/{id}/run` returning `503`. Root cause: this host runs rootless Podman: the
   host user is in the `docker` group, but rootless Podman doesn't propagate that group into
   containers, so the bind-mounted `/var/run/docker.sock` was unreachable from inside the `api`
   container. **Fixed, applied, and independently re-verified** — `docker-compose.yml` now uses
   `${EXERCISE_DOCKER_SOCKET_PATH:-/var/run/docker.sock}` + `group_add:
   ["${EXERCISE_DOCKER_SOCKET_GID:-0}"]`, and this machine's real `.env` points
   `EXERCISE_DOCKER_SOCKET_PATH` at `/run/user/1000/podman/podman.sock`. Confirmed live: `docker exec
   studytracker-api curl --unix-socket /var/run/docker.sock http://localhost/version` now returns real
   JSON. Also added missing exception logging in `ExerciseService.ExecuteAsync` (was silently
   swallowing the real error before this fix — that's exactly how bug #2 below was found so fast).

### In flight — the very next thing to do in a new session
**Exercise-grading bug #2 (NOT yet applied)**: pushing past bug #1 revealed the exercise-grading
pipeline has actually **never worked, for any exercise, ever** — `ExerciseWorkspaceBuilder.BuildAsync`
never copies any non-editable reference files (models, DTOs, exceptions, interfaces) into the Maven
workspace it builds; it only copies `pom.xml`, the test file, and the submitted editable files. A real
submission of `hotel-add-rooms`'s own reference solution returns a Maven **compilation failure** citing
missing classes (`Room`, `RoomRepository`, `UserNotFoundException`, etc.) that are simply never placed
in the workspace.

**The fix prompt is already written and committed**: `info/.notes/exercise-workspace-missing-nonEditable-files-fix-prompt.md`.
Next session should:
1. Confirm whether the user has run it through Gemini yet (ask, or `git log`/`git diff` to check).
2. If applied: independently re-verify exactly as the prompt's own verification section demands — real
   rebuild, real `--force-recreate`, real live POST of `hotel-add-rooms`'s solution (must return
   `passed:true`, `3/3`), real live POST of its starter (must NOT be `compilationFailure` anymore), and
   the same solution/starter check for a second exercise (`java-lld-generate-parking-ticket`) to prove
   the fix isn't accidentally specific to one file layout. Don't trust any "done" claim — re-run the
   checks yourself using the WSL shell access described below.
3. If not yet applied: remind the user to run it, or offer to walk through it together.

### Not yet started (explicitly deferred, in priority order the user asked for)
1. Finish exercise-grading verification (above).
2. Frontend UI (`PracticeQuestions.jsx`) — never opened in a real browser against the new dynamic MCQ
   API; only tested via raw `curl`.
3. Splitwise exercises (`splitwise-manage-group-members`, `splitwise-create-delete-group`) — genuinely
   Spring/JPA-based, not yet wired into the new `java-maven-spring` sandbox profile at all.
4. Phase B of the RAG ingestion pipeline (lessons prose extractor) — not started, deferred since early
   in the prior compacted session.
5. **User's explicit stated plan**: finish *all* of the above + verification on WSL2 first, **then**
   repeat the same deployment + verification pass on **EC2** (production), **then** finally return to
   the **AI Tutor Python work** (`ai-agent/` — hand-written by the user; Claude explains concepts only,
   never writes code or Local-LLM prompts for it — this is a standing memory rule, not new).

## Environment facts (hard-won this session — do not re-discover these)

- **Claude has direct shell access into the user's real WSL2 environment** via `wsl.exe` from the Bash
  tool (which itself runs in Git Bash/MINGW64 on the same physical Windows machine as the user,
  hostname `DESKTOP-15NDNUT`). The user's actual project clone is at
  `/home/rbalaji/scaler-education-journey` inside the `Ubuntu` WSL distro — **a separate git clone**
  from the Windows-side path Claude's file tools operate on
  (`C:\Users\coforge-rythmos\Documents\raghu\scaler-education-journey`). Always `git pull`/`git push`
  to sync between them; never assume a file written on one side is visible on the other without an
  explicit pull.
- **Always use a login shell**: `wsl.exe -d Ubuntu -- bash -lc "..."`, never plain `bash -c`. A
  non-login shell doesn't source the user's profile, which sets `DOCKER_HOST` to point at the real
  rootless Podman socket. Without `-lc`, `docker` commands silently talk to a completely different,
  empty, unused native Docker Engine install on the same box — this caused real confusion earlier in
  the session (containers appeared to not exist, `docker logs` said "no such container", etc.)
- **Always prefix with `MSYS_NO_PATHCONV=1`** when the command contains Unix-style absolute paths
  (like `/tmp/...`) that need to reach WSL unmangled: `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc
  "..."`. Without it, Git Bash's MSYS layer silently rewrites `/tmp/foo` into a Windows path before
  `wsl.exe` ever sees it, causing commands to silently no-op or operate on the wrong path. This was
  discovered the hard way — see "Hard lessons" below.
- **Avoid long, complex, multi-statement one-liners passed as inline strings through the
  Git-Bash→wsl.exe boundary** — variable expansion and quoting can silently corrupt (a `$WORK` var
  evaluated to empty mid-chain in one real incident here, though ultimately no damage occurred). Prefer
  writing an actual `.sh` script file (via the Write tool, targeting the UNC path
  `\\wsl.localhost\Ubuntu\tmp\something.sh`) and then running `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu --
  bash /tmp/something.sh`. Much more reliable.
- **`docker build -t name .` (bare, no compose) does NOT persist the image on this host.** This host's
  buildx driver is `docker-container` (a `buildx_buildkit_default` container handles builds), and a bare
  build without `--load` leaves the result only in the transient buildx cache — it's usable
  *immediately* after building (e.g. one `docker run` right after works) but **vanishes** later (this
  silently ate the Spring Boot runner image built and verified earlier in the session — it was gone by
  the time it was needed again). **Always pass `--load`** for any manual/local image build outside of
  `docker compose build` (compose's own build path handles this correctly by itself).
- **`/tmp` doesn't reliably bind-mount into rootless-Podman containers on this host** — a `docker run -v
  /tmp/foo:/workspace` silently mounts an empty directory. Use a path under `/home/rbalaji/...` instead
  for anything that needs to be bind-mounted into a container.
- **Rootless Podman won't let a plain user `rm -rf` files a container wrote as root** inside a
  bind-mounted host directory (UID mismatch across the user namespace) — leftover root-owned files may
  need `sudo rm -rf` from the user directly; Claude's shell access doesn't have passwordless sudo here.
- **The API's `x-api-key` middleware** (`api/Program.cs` ~line 494) gates every request except
  `/health`, `/swagger`, `OPTIONS`. The real value in this deployment's `.env` is literally the
  placeholder string `your_api_key_here` (not blank — the user left it as-is deliberately for local
  dev) — pass it verbatim as the `x-api-key` header for any manual `curl` testing.
- **Container/service names**: `studytracker-api`, `studytracker-postgres`/service name `database`,
  `studytracker-app`, `neuralascent-ai-agent`. DB user `studyuser`, DB name `studytracker` (both
  defaults, real values may differ if `.env` overrides them — check first).
- **Exercise submission API shape**: `POST /api/exercises/{exerciseId}/run` with body
  `{"files":[{"path":"...","content":"..."},...]}` — **only the editable files** declared in that
  exercise's `exercise.json` (`ExerciseSubmissionValidator` rejects anything else). Response shape is
  `ExerciseExecutionResponse` in `api/Models/ExerciseDtos.cs`.

## Hard lessons (read before repeating them)

1. **Never chain a destructive-looking command (`rm -rf $VAR`) through the Git-Bash→wsl.exe bridge
   without first verifying `$VAR` actually resolves correctly on the other side.** One incident this
   session had `rm -rf $WORK; mkdir -p $WORK` silently operate on an empty/wrong path due to variable
   corruption across the shell boundary — no actual damage occurred (confirmed by checking `git
   status`/`git log`/file counts immediately after), but it could have been very bad. When in doubt,
   echo the variable first in its own separate, verified command before using it in anything
   destructive.
2. **A "changes were done" claim from the user (relaying a Local-LLM's self-report) is not verification
   — it's a lead to go re-check.** Every single fix this session that was claimed "done" was
   independently re-verified by actually rebuilding, recreating containers, and hitting live endpoints
   — and real bugs were caught this way that a code-read alone would have missed (e.g., the
   `--load` image-persistence footgun, the missing-runner-image issue, and the deeper
   `ExerciseWorkspaceBuilder` bug were *only* found by insisting on a real live end-to-end submission,
   not by reading the diff and trusting it looked right).
3. **A 503/error with zero corresponding log line is a red flag, not a dead end.** The
   `ExerciseService.ExecuteAsync` logging gap (now fixed) made the first real bug invisible until Claude
   manually exec'd into the container and tested the Docker socket by hand. If a fix still doesn't work
   and the logs are silent, suspect a similar swallowed-exception pattern elsewhere before assuming the
   fix itself is wrong.

## Standing rules from memory / CLAUDE.md (unchanged, just restating for a fresh session)

- `ai-agent/` (the Python AI Tutor) is **hand-written by the user**. Claude explains concepts only —
  never writes code or Local-LLM prompts for it.
- AI-vertical *curriculum content* (a learning-vertical course about AI/LLM engineering topics) is
  **hand-authored by the user** — never generate seed-data/content prompts for it. AI-vertical
  *infrastructure* (actual chatbot/LLM plumbing in `api/`/`app/`) **is** in scope for the normal
  prompt workflow.
- Never modify an existing, already-wired, working exercise — only create new ones or fix ones the
  user explicitly flags as broken.
