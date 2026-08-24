# User Preferences & Workflow Rules

- **Build Execution Rule**: Never run build commands (`npm run build`, `dotnet build`, container builds, etc.) directly on the user's project. Instead, prompt the user with the exact command for them to execute manually on their side.
- **Docker Verification Rule**: Provide local-build Docker Compose commands for this project. Do not instruct the user to pull the published API image for verification, because it is not compatible with the user's target Linux platform. Use `docker-compose.yml` together with `docker-compose.dev.yml` to build the API locally before running database maintenance commands.
