# User Preferences & Workflow Rules

- **Build & Run Execution Rule (STRICT)**: Never run build or execution commands (`npm run build`, `npm run dev`, `dotnet build`, `dotnet run`, container builds, etc.) directly on the user's project. Upon completion of every task, always supply the exact git commit, pull, build, and run commands so the user can execute and verify the changes locally on their system.
- **Docker Verification Rule**: Provide local-build Docker Compose commands for this project. Do not instruct the user to pull the published API image for verification, because it is not compatible with the user's target Linux platform. Use `docker-compose.yml` together with `docker-compose.dev.yml` to build the API locally before running database maintenance commands.
