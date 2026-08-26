#!/usr/bin/env bash
set -Eeuo pipefail

API_IMAGE="${API_IMAGE:?API_IMAGE is required}"
APP_IMAGE="${APP_IMAGE:?APP_IMAGE is required}"
RUNNER_IMAGE="${RUNNER_IMAGE:-ghcr.io/balajiraghuram92/neuralascent-java-runner}"
IMAGE_TAG="${IMAGE_TAG:-release}"
API_REF="${API_REF:-}"
APP_REF="${APP_REF:-}"
RUNNER_REF="${RUNNER_REF:-}"
DOMAIN_NAME="${DOMAIN_NAME:-localhost}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"
ENV_FILE="${ENV_FILE:-/etc/studytracker/api.env}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-postgres:16-alpine}"
NETWORK_NAME="${NETWORK_NAME:-scaler-network}"
DATABASE_CONTAINER="${DATABASE_CONTAINER:-}"
API_CONTAINER="${API_CONTAINER:-studytracker-api}"
APP_CONTAINER="${APP_CONTAINER:-studytracker-app}"
DATA_VOLUME="${DATA_VOLUME:-scaler_postgres_data}"
MAVEN_CACHE_VOLUME="${MAVEN_CACHE_VOLUME:-}"
MAX_CONCURRENT_EXECUTIONS="${MAX_CONCURRENT_EXECUTIONS:-}"
CERT_DIR="${CERT_DIR:-/etc/letsencrypt}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/studytracker}"
BACKUP_S3_URI="${BACKUP_S3_URI:-}"
RESTORE_LATEST_BACKUP="${RESTORE_LATEST_BACKUP:-false}"
ALLOW_CREATE_DATABASE="${ALLOW_CREATE_DATABASE:-false}"
REGISTRY_HOST="${REGISTRY_HOST:-ghcr.io}"
REGISTRY_USERNAME="${REGISTRY_USERNAME:-balajiraghuram92}"
REGISTRY_TOKEN_FILE="${REGISTRY_TOKEN_FILE:-/etc/studytracker/ghcr-token}"
DEPLOY_LOCK_FILE="${DEPLOY_LOCK_FILE:-/var/lock/neuralascent-deploy.lock}"

log() {
    printf '[single-ec2-deploy] %s\n' "$*"
}

fail() {
    printf '[single-ec2-deploy] ERROR: %s\n' "$*" >&2
    exit 1
}

cleanup() {
    if [ -n "${DEPLOY_DOCKER_CONFIG:-}" ] && [ -d "${DEPLOY_DOCKER_CONFIG}" ]; then
        rm -rf "${DEPLOY_DOCKER_CONFIG}"
    fi
}

trap cleanup EXIT

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

env_value() {
    local key="$1"
    local value
    value="$(sed -n "s/^${key}=//p" "${ENV_FILE}" | tail -n 1)"
    [ -n "${value}" ] || fail "${key} is missing from ${ENV_FILE}"
    printf '%s' "${value}"
}

env_value_or_default() {
    local key="$1"
    local default_value="$2"
    local value
    value="$(sed -n "s/^${key}=//p" "${ENV_FILE}" | tail -n 1)"
    printf '%s' "${value:-${default_value}}"
}

env_has_value() {
    local key="$1"
    grep -Eq "^${key}=.+" "${ENV_FILE}"
}

wait_for_database() {
    local db_user db_name
    db_user="$(env_value_or_default POSTGRES_USER studyuser)"
    db_name="$(env_value_or_default POSTGRES_DB studytracker)"
    for attempt in $(seq 1 30); do
        if docker exec "${DATABASE_CONTAINER}" pg_isready -U "${db_user}" -d "${db_name}" >/dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    docker logs "${DATABASE_CONTAINER}" --tail 100 || true
    fail "PostgreSQL did not become ready."
}

wait_for_url() {
    local url="$1"
    local label="$2"
    for attempt in $(seq 1 30); do
        if curl -fsS "${url}" >/dev/null 2>&1; then
            log "${label} health check passed."
            return 0
        fi
        sleep 2
    done
    return 1
}

backup_database() {
    local db_user db_name timestamp backup_name container_path host_path
    db_user="$(env_value_or_default POSTGRES_USER studyuser)"
    db_name="$(env_value_or_default POSTGRES_DB studytracker)"
    timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
    backup_name="${db_name}_${timestamp}_${IMAGE_TAG}.dump"
    container_path="/tmp/${backup_name}"
    host_path="${BACKUP_DIR}/${backup_name}"

    install -d -m 0700 "${BACKUP_DIR}"
    log "Creating pre-migration PostgreSQL backup ${backup_name}."
    docker exec "${DATABASE_CONTAINER}" pg_dump \
        -U "${db_user}" \
        -d "${db_name}" \
        -F c \
        -f "${container_path}"
    docker cp "${DATABASE_CONTAINER}:${container_path}" "${host_path}" >/dev/null
    docker exec "${DATABASE_CONTAINER}" rm -f "${container_path}"
    docker run --rm -v "${BACKUP_DIR}:/backups:ro" "${POSTGRES_IMAGE}" \
        pg_restore --list "/backups/${backup_name}" >/dev/null
    (
        cd "${BACKUP_DIR}"
        sha256sum "${backup_name}" > "${backup_name}.sha256"
    )

    if [ -n "${BACKUP_S3_URI}" ]; then
        require_command aws
        aws s3 cp "${host_path}" "${BACKUP_S3_URI%/}/${backup_name}"
        aws s3 cp "${host_path}.sha256" "${BACKUP_S3_URI%/}/${backup_name}.sha256"
    fi
}

restore_latest_backup() {
    [ "${RESTORE_LATEST_BACKUP}" = "true" ] || return 0
    [ -n "${BACKUP_S3_URI}" ] || fail "RESTORE_LATEST_BACKUP=true requires BACKUP_S3_URI."
    require_command aws

    local latest_key restore_path db_user db_name
    latest_key="$(aws s3 ls "${BACKUP_S3_URI%/}/" | awk '{print $4}' | grep '\.dump$' | sort | tail -n 1)"
    [ -n "${latest_key}" ] || fail "No PostgreSQL dump was found at ${BACKUP_S3_URI}."

    install -d -m 0700 "${BACKUP_DIR}"
    restore_path="${BACKUP_DIR}/${latest_key}"
    db_user="$(env_value_or_default POSTGRES_USER studyuser)"
    db_name="$(env_value_or_default POSTGRES_DB studytracker)"

    log "Restoring ${latest_key} into the newly created PostgreSQL container."
    aws s3 cp "${BACKUP_S3_URI%/}/${latest_key}" "${restore_path}"
    aws s3 cp "${BACKUP_S3_URI%/}/${latest_key}.sha256" "${restore_path}.sha256"
    (
        cd "${BACKUP_DIR}"
        sha256sum -c "${latest_key}.sha256"
    )
    docker run --rm -v "${BACKUP_DIR}:/backups:ro" "${POSTGRES_IMAGE}" \
        pg_restore --list "/backups/${latest_key}" >/dev/null
    docker cp "${restore_path}" "${DATABASE_CONTAINER}:/tmp/${latest_key}" >/dev/null
    docker exec "${DATABASE_CONTAINER}" pg_restore \
        -U "${db_user}" \
        -d "${db_name}" \
        --clean \
        --if-exists \
        --no-owner \
        --no-privileges \
        "/tmp/${latest_key}"
    docker exec "${DATABASE_CONTAINER}" rm -f "/tmp/${latest_key}"
}

database_is_empty() {
    local db_user db_name table_count
    db_user="$(env_value_or_default POSTGRES_USER studyuser)"
    db_name="$(env_value_or_default POSTGRES_DB studytracker)"
    table_count="$(docker exec "${DATABASE_CONTAINER}" psql \
        -U "${db_user}" \
        -d "${db_name}" \
        -tAc "SELECT count(*) FROM pg_tables WHERE schemaname = 'public';" | tr -d '[:space:]')"
    [ "${table_count:-0}" = "0" ]
}

start_api() {
    local image="$1"
    local runner_ref="${2:-}"
    local args=(
        run -d
        --name "${API_CONTAINER}"
        --network "${NETWORK_NAME}"
        --restart unless-stopped
        -p 127.0.0.1:5000:8080
        --add-host host.docker.internal:host-gateway
        --env-file "${ENV_FILE}"
        -e "ExerciseExecution__ExercisesRoot=/app/exercises"
        -e "ExerciseExecution__WorkspaceRoot=/tmp/studytracker-exercises"
        -e "ExerciseExecution__DockerEndpoint=unix:///var/run/docker.sock"
        -e "ExerciseExecution__MavenCacheVolume=${MAVEN_CACHE_VOLUME}"
        -e "ExerciseExecution__MaxConcurrentExecutions=${MAX_CONCURRENT_EXECUTIONS}"
        -v /var/run/docker.sock:/var/run/docker.sock
    )

    if [ -n "${runner_ref}" ]; then
        args+=( -e "ExerciseExecution__RunnerImage=${runner_ref}" )
    fi

    docker "${args[@]}" "${image}" >/dev/null
}

start_app() {
    local image="$1"
    local app_env_file
    local status
    app_env_file="$(mktemp)"
    chmod 600 "${app_env_file}"
    printf 'API_KEY=%s\n' "$(env_value API_KEY)" > "${app_env_file}"

    local args=(
        run -d
        --name "${APP_CONTAINER}"
        --network "${NETWORK_NAME}"
        --restart unless-stopped
        -p 80:80
        --env-file "${app_env_file}"
        -e "DOMAIN_NAME=${DOMAIN_NAME}"
    )

    if [ "${DOMAIN_NAME}" != "localhost" ]; then
        args+=( -p 443:443 -v "${CERT_DIR}:${CERT_DIR}:ro" )
    fi

    if docker "${args[@]}" "${image}" >/dev/null; then
        status=0
    else
        status=$?
    fi
    rm -f "${app_env_file}"
    return "${status}"
}

verify_digest_ref() {
    local ref="$1"
    local label="$2"
    case "${ref}" in
        *@sha256:*) ;;
        *) fail "${label} must be pinned to an image digest." ;;
    esac
}

verify_image_digest_ref() {
    local ref="$1"
    local label="$2"
    local expected_image="$3"
    case "${ref}" in
        "${expected_image}"@sha256:*) ;;
        *) fail "${label} must reference ${expected_image} with an image digest." ;;
    esac
}

verify_host_image_platform() {
    local ref="$1"
    local label="$2"
    local expected_arch actual_platform

    case "$(uname -m)" in
        aarch64|arm64) expected_arch="arm64" ;;
        x86_64|amd64) expected_arch="amd64" ;;
        *) fail "Unsupported host architecture: $(uname -m)." ;;
    esac

    actual_platform="$(docker image inspect --format '{{.Os}}/{{.Architecture}}' "${ref}")"
    [ "${actual_platform}" = "linux/${expected_arch}" ] || \
        fail "${label} resolved to ${actual_platform}; expected linux/${expected_arch}."
}

require_command docker
require_command curl
require_command flock
[ -f "${ENV_FILE}" ] || fail "Missing environment file: ${ENV_FILE}"

MAVEN_CACHE_VOLUME="${MAVEN_CACHE_VOLUME:-$(env_value_or_default ExerciseExecution__MavenCacheVolume neuralascent-maven-cache)}"
MAX_CONCURRENT_EXECUTIONS="${MAX_CONCURRENT_EXECUTIONS:-$(env_value_or_default ExerciseExecution__MaxConcurrentExecutions 1)}"

[ -S /var/run/docker.sock ] || fail "Docker socket is unavailable on the deployment host."
docker info >/dev/null 2>&1 || fail "Docker daemon is unavailable on the deployment host."

install -d -m 0755 "$(dirname "${DEPLOY_LOCK_FILE}")"
exec 9>"${DEPLOY_LOCK_FILE}"
flock -n 9 || fail "Another Neuralascent deployment is already running."

env_value API_KEY >/dev/null

if ! env_has_value ConnectionStrings__DefaultConnection; then
    for required_key in DATABASE_HOST DATABASE_NAME DATABASE_USER DATABASE_PASSWORD; do
        env_value "${required_key}" >/dev/null
    done
fi

if env_has_value POSTGRES_PASSWORD && env_has_value DATABASE_PASSWORD; then
    [ "$(env_value POSTGRES_PASSWORD)" = "$(env_value DATABASE_PASSWORD)" ] || \
        fail "POSTGRES_PASSWORD and DATABASE_PASSWORD must match for the local PostgreSQL container."
fi

if [ -z "${API_REF}" ] || [ -z "${APP_REF}" ] || [ -z "${RUNNER_REF}" ]; then
    fail "API_REF, APP_REF, and RUNNER_REF digest references are required."
fi
api_ref="${API_REF}"
app_ref="${APP_REF}"
runner_ref="${RUNNER_REF}"
verify_digest_ref "${api_ref}" "API_REF"
verify_digest_ref "${app_ref}" "APP_REF"
verify_digest_ref "${runner_ref}" "RUNNER_REF"
verify_image_digest_ref "${api_ref}" "API_REF" "${API_IMAGE}"
verify_image_digest_ref "${app_ref}" "APP_REF" "${APP_IMAGE}"
verify_image_digest_ref "${runner_ref}" "RUNNER_REF" "${RUNNER_IMAGE}"

case "$(uname -m)" in
    aarch64|arm64) ;;
    *) fail "Production deployment requires an ARM64 host; found $(uname -m)." ;;
esac

if [ -f "${REGISTRY_TOKEN_FILE}" ]; then
    log "Authenticating to ${REGISTRY_HOST} with the protected read-only token."
    DEPLOY_DOCKER_CONFIG="$(mktemp -d)"
    export DOCKER_CONFIG="${DEPLOY_DOCKER_CONFIG}"
    docker login "${REGISTRY_HOST}" \
        --username "${REGISTRY_USERNAME}" \
        --password-stdin < "${REGISTRY_TOKEN_FILE}"
fi

log "Pulling immutable application and runner images for $(uname -m)."
docker pull "${runner_ref}"
docker pull "${api_ref}"
docker pull "${app_ref}"
docker pull "${POSTGRES_IMAGE}"
verify_host_image_platform "${runner_ref}" "Java runner image"
verify_host_image_platform "${api_ref}" "API image"
verify_host_image_platform "${app_ref}" "frontend image"

docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || docker network create "${NETWORK_NAME}" >/dev/null
if ! docker volume inspect "${DATA_VOLUME}" >/dev/null 2>&1; then
    docker volume create "${DATA_VOLUME}" >/dev/null
fi
if ! docker volume inspect "${MAVEN_CACHE_VOLUME}" >/dev/null 2>&1; then
    docker volume create "${MAVEN_CACHE_VOLUME}" >/dev/null
fi

if [ -z "${DATABASE_CONTAINER}" ]; then
    mapfile -t volume_containers < <(docker ps -a --filter "volume=${DATA_VOLUME}" --format '{{.Names}}')
    if [ "${#volume_containers[@]}" -gt 1 ]; then
        fail "Multiple containers use ${DATA_VOLUME}: ${volume_containers[*]}. Set DATABASE_CONTAINER explicitly after review."
    elif [ "${#volume_containers[@]}" -eq 1 ]; then
        DATABASE_CONTAINER="${volume_containers[0]}"
    elif docker container inspect studytracker-postgres >/dev/null 2>&1; then
        DATABASE_CONTAINER=studytracker-postgres
    elif docker container inspect studytracker-db >/dev/null 2>&1; then
        DATABASE_CONTAINER=studytracker-db
    else
        mapfile -t postgres_containers < <(docker ps -a --format '{{.Names}} {{.Image}}' | awk 'tolower($2) ~ /(postgres|postgis|timescale)/ {print $1}')
        if [ "${#postgres_containers[@]}" -gt 0 ]; then
            fail "Unrecognized PostgreSQL container(s): ${postgres_containers[*]}. Set DATABASE_CONTAINER explicitly after confirming the production database."
        fi
        mapfile -t suspicious_volumes < <(docker volume ls --format '{{.Name}}' | grep -Ei '(postgres|studytracker|pgdata)' | grep -Fvx "${DATA_VOLUME}" || true)
        if [ "${#suspicious_volumes[@]}" -gt 0 ]; then
            fail "Unrecognized database-like volume(s): ${suspicious_volumes[*]}. Review them before allowing a new database."
        fi
        [ "${ALLOW_CREATE_DATABASE}" = "true" ] || \
            fail "No recognized PostgreSQL container exists. Set ALLOW_CREATE_DATABASE=true only for an approved fresh or replacement host."
        DATABASE_CONTAINER=studytracker-postgres
    fi
fi

if docker container inspect "${DATABASE_CONTAINER}" >/dev/null 2>&1; then
    docker start "${DATABASE_CONTAINER}" >/dev/null 2>&1 || true
    if ! docker network inspect "${NETWORK_NAME}" --format '{{range .Containers}}{{println .Name}}{{end}}' | grep -Fxq "${DATABASE_CONTAINER}"; then
        docker network connect --alias database --alias studytracker-postgres \
            "${NETWORK_NAME}" "${DATABASE_CONTAINER}"
    fi
else
    for required_key in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD; do
        env_value "${required_key}" >/dev/null
    done
    log "Creating PostgreSQL with a persistent named volume."
    docker run -d \
        --name "${DATABASE_CONTAINER}" \
        --network "${NETWORK_NAME}" \
        --restart unless-stopped \
        --env-file "${ENV_FILE}" \
        -v "${DATA_VOLUME}:/var/lib/postgresql/data" \
        --health-cmd="pg_isready -U $(env_value POSTGRES_USER) -d $(env_value POSTGRES_DB)" \
        --health-interval=10s \
        --health-timeout=5s \
        --health-retries=5 \
        "${POSTGRES_IMAGE}" >/dev/null
fi

wait_for_database

if env_has_value ConnectionStrings__DefaultConnection; then
    configured_db_host="$(env_value ConnectionStrings__DefaultConnection | sed -n 's/.*Host=\([^;]*\).*/\1/p')"
else
    configured_db_host="$(env_value DATABASE_HOST)"
fi

if [ -n "${configured_db_host}" ]; then
    docker run --rm --network "${NETWORK_NAME}" \
        --add-host host.docker.internal:host-gateway \
        "${POSTGRES_IMAGE}" \
        getent hosts "${configured_db_host}" >/dev/null || \
        fail "DATABASE_HOST=${configured_db_host} is not resolvable on ${NETWORK_NAME}; review the existing database network aliases."
fi

if database_is_empty; then
    restore_latest_backup
fi

backup_database

log "Applying fail-fast schema migrations."
docker run --rm --network "${NETWORK_NAME}" \
    --add-host host.docker.internal:host-gateway \
    --env-file "${ENV_FILE}" "${api_ref}" --migrate

log "Applying idempotent reference-data seeds."
docker run --rm --network "${NETWORK_NAME}" \
    --add-host host.docker.internal:host-gateway \
    --env-file "${ENV_FILE}" "${api_ref}" --seed-reference-data

previous_api_image="$(docker container inspect --format '{{.Config.Image}}' "${API_CONTAINER}" 2>/dev/null || true)"
previous_app_image="$(docker container inspect --format '{{.Config.Image}}' "${APP_CONTAINER}" 2>/dev/null || true)"
previous_runner_ref="$(docker container inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "${API_CONTAINER}" 2>/dev/null | sed -n 's/^ExerciseExecution__RunnerImage=//p' | tail -n 1 || true)"

rollback() {
    local exit_code="${1:-1}"
    trap - ERR
    log "Deployment failed; restoring the previous application images."
    docker stop "${API_CONTAINER}" "${APP_CONTAINER}" >/dev/null 2>&1 || true
    docker rm "${API_CONTAINER}" "${APP_CONTAINER}" >/dev/null 2>&1 || true
    if [ -n "${previous_api_image}" ]; then
        start_api "${previous_api_image}" "${previous_runner_ref}" || true
    fi
    if [ -n "${previous_app_image}" ]; then
        start_app "${previous_app_image}" || true
    fi
    exit "${exit_code}"
}

trap 'rollback $?' ERR

if [ "${DOMAIN_NAME}" != "localhost" ] && [ ! -f "${CERT_DIR}/live/${DOMAIN_NAME}/fullchain.pem" ]; then
    [ -n "${LETSENCRYPT_EMAIL}" ] || fail "LETSENCRYPT_EMAIL is required for first-time TLS provisioning."
fi

docker stop "${APP_CONTAINER}" >/dev/null 2>&1 || true

if [ "${DOMAIN_NAME}" != "localhost" ]; then
    if [ ! -f "${CERT_DIR}/live/${DOMAIN_NAME}/fullchain.pem" ]; then
        log "Obtaining the initial TLS certificate for ${DOMAIN_NAME}."
        docker run --rm -p 80:80 \
            -v "${CERT_DIR}:${CERT_DIR}" \
            -v /var/lib/letsencrypt:/var/lib/letsencrypt \
            certbot/certbot certonly --standalone --non-interactive --agree-tos --no-eff-email \
            -m "${LETSENCRYPT_EMAIL}" -d "${DOMAIN_NAME}"
    else
        log "Checking whether the TLS certificate needs renewal."
        docker run --rm -p 80:80 \
            -v "${CERT_DIR}:${CERT_DIR}" \
            -v /var/lib/letsencrypt:/var/lib/letsencrypt \
            certbot/certbot renew --standalone --quiet
    fi
fi

docker stop "${API_CONTAINER}" >/dev/null 2>&1 || true
docker rm "${API_CONTAINER}" >/dev/null 2>&1 || true
docker rm "${APP_CONTAINER}" >/dev/null 2>&1 || true

start_api "${api_ref}" "${runner_ref}"
start_app "${app_ref}"

wait_for_url http://localhost:5000/health "API" || rollback 1
wait_for_url http://localhost/health "Frontend" || rollback 1

trap - ERR
docker image prune -f >/dev/null
log "Deployment ${IMAGE_TAG} completed successfully."
