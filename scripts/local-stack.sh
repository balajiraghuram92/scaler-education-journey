#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"
COMPOSE=(docker compose -f "${PROJECT_DIR}/docker-compose.yml" -f "${PROJECT_DIR}/docker-compose.dev.yml" --env-file "${ENV_FILE}")

log() {
    printf '[local-stack] %s\n' "$*"
}

random_hex() {
    od -An -N32 -tx1 /dev/urandom | tr -d ' \n'
}

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf '[local-stack] Required command not found: %s\n' "$1" >&2
        exit 1
    fi
}

require_command docker

if ! docker compose version >/dev/null 2>&1; then
    printf '[local-stack] Docker Compose v2 is required.\n' >&2
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    printf '[local-stack] Docker is installed but the daemon is unavailable. Start Docker Desktop or the Docker service.\n' >&2
    exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
    db_password="$(random_hex)"
    api_key="$(random_hex)"
    cat >"${ENV_FILE}" <<EOF
POSTGRES_DB=studytracker
POSTGRES_USER=studyuser
POSTGRES_PASSWORD=${db_password}
API_KEY=${api_key}
ASPNETCORE_ENVIRONMENT=Production
IMAGE_TAG=latest
EOF
    chmod 600 "${ENV_FILE}" 2>/dev/null || true
    log "Created a local .env with generated credentials."
fi

if grep -Eq 'your_secure_password_here|your_api_key_here' "${ENV_FILE}"; then
    printf '[local-stack] Replace placeholder credentials in %s before continuing.\n' "${ENV_FILE}" >&2
    exit 1
fi

log "Starting PostgreSQL and waiting for readiness."
"${COMPOSE[@]}" up -d --wait database

log "Building native images for the current host architecture."
"${COMPOSE[@]}" build --pull api app

log "Building the local Java exercise runner image."
EXERCISE_RUNNER_IMAGE="${EXERCISE_RUNNER_IMAGE:-neuralascent-java-runner:dev}" \
    "${PROJECT_DIR}/scripts/build-java-runner.sh"

log "Applying additive database migrations."
"${COMPOSE[@]}" run --rm --no-deps api --migrate

log "Applying idempotent reference-data seeds."
"${COMPOSE[@]}" run --rm --no-deps api --seed-reference-data

log "Starting the complete local stack."
"${COMPOSE[@]}" up -d --wait

log "Local stack is ready at http://localhost"
log "Use './scripts/reconcile-content.sh --dry-run' for legacy mapping review."
