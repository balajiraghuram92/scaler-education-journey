# User Preferences & Workflow Rules

- **Build & Run Execution Rule (STRICT)**: Never run build or execution commands (`npm run build`, `npm run dev`, `dotnet build`, `dotnet run`, container builds, etc.) directly on the user's project. Upon completion of every task, always supply the exact git commit, pull, Docker build, and Docker run commands so the user can execute and verify the changes locally on their WSL2 / Linux system.
- **Docker-First Verification Rule (WSL2 / Linux / EC2 Parity)**: Always provide local-build Docker Compose commands using `docker-compose.yml` + `docker-compose.dev.yml`. Never instruct the user to run `dotnet` or `npm` directly on the host machine. This preserves parity with GitHub Actions CI/CD and ensures seamless future migration to Java/Spring Boot without altering CLI workflows.
- **Database Seeding in Docker**: When curriculum or database changes are made, instruct the user to build and run the database seeder container:
  `docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps api --seed-reference-data`
