# Agent Rules & Execution Policy

**1. Git Commit & Push Policy (STRICT):**
- The agent does **NOT** have permission to execute `git commit`, `git push`, or modifying git remote commands.
- The agent must **ONLY** explain the proposed changes and request the user to commit and push by providing the exact commit message and git commands.
- The user retains sole execution authority for committing and pushing to git repositories.

**2. Workflow Modification Policy (STRICT):**
- The agent does **NOT** have permission to make changes directly to any GitHub Actions workflow files (`.github/workflows/*`) in the workspace.
- The agent can **ONLY** suggest workflow changes, explain the rationale, and provide the exact YAML snippet for the user to review and apply manually.
- Workflow files must remain frozen and stable once deployed to prevent pipeline disruptions.

**3. Local WSL Docker Verification Workflow:**
- The local API, React app, and PostgreSQL database run inside the user's WSL Docker Compose environment. The agent should not assume that a Vite dev server can reach the authenticated API or reproduce the production proxy.
- For frontend changes that need browser verification, provide the user with the Docker commands below and ask them to run the commands in their WSL project shell. Then inspect the resulting `http://localhost/` page and container output together.
- Use the development Compose overlay so the API and app are built from the current workspace source:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d database
docker compose -f docker-compose.yml -f docker-compose.dev.yml build api app
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate api app
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

- After the user reports that the services are running, verify the API and website with:

```powershell
curl.exe http://localhost:5000/health
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=120 api
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=120 app
```

- For an API or database schema change, do not infer that migrations ran. Give the user the explicit migration command and wait for its output before testing the page:

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --migrate
```

- Never run `docker compose ... down -v` during ordinary UI work. It deletes the named PostgreSQL volume and can remove authored curriculum data and progress.
- Do not change backend, database, Java runner, or Docker infrastructure for the current Lesson 4 UI-only phase unless the user explicitly expands the scope.
