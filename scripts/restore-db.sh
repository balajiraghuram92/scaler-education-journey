#!/usr/bin/env bash
set -euo pipefail

# Determine script and project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load .env variables if .env file exists
if [ -f "${PROJECT_DIR}/.env" ]; then
    echo "[INFO] Loading environment variables from ${PROJECT_DIR}/.env"
    set -o allexport
    # shellcheck disable=SC1091
    source "${PROJECT_DIR}/.env"
    set +o allexport
fi

# Environment variables with defaults
POSTGRES_DB="${POSTGRES_DB:-studytracker}"
POSTGRES_USER="${POSTGRES_USER:-studyuser}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-your_secure_password_here}"
S3_BUCKET="${S3_BUCKET:-scaler-studytracker-backups}"
S3_PREFIX="${S3_PREFIX:-database-backups}"

INPUT_TARGET="${1:-}"

TMP_DIR="$(mktemp -d)"
LOCAL_RESTORE_PATH=""

cleanup() {
    rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "=========================================="
echo "Starting PostgreSQL Database Restore from S3"
echo "Target Database: ${POSTGRES_DB}"
echo "=========================================="

if [ -z "${INPUT_TARGET}" ]; then
    echo "[INFO] No backup file specified. Fetching latest backup from s3://${S3_BUCKET}/${S3_PREFIX}/..."
    LATEST_KEY="$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" | sort | tail -n 1 | awk '{print $4}')"
    if [ -z "${LATEST_KEY}" ]; then
        echo "[ERROR] No backup files found in s3://${S3_BUCKET}/${S3_PREFIX}/" >&2
        exit 1
    fi
    S3_SOURCE="s3://${S3_BUCKET}/${S3_PREFIX}/${LATEST_KEY}"
    LOCAL_RESTORE_PATH="${TMP_DIR}/${LATEST_KEY}"
elif [[ "${INPUT_TARGET}" == s3://* ]]; then
    S3_SOURCE="${INPUT_TARGET}"
    FILENAME="$(basename "${INPUT_TARGET}")"
    LOCAL_RESTORE_PATH="${TMP_DIR}/${FILENAME}"
else
    FILENAME="$(basename "${INPUT_TARGET}")"
    S3_SOURCE="s3://${S3_BUCKET}/${S3_PREFIX}/${FILENAME}"
    LOCAL_RESTORE_PATH="${TMP_DIR}/${FILENAME}"
fi

echo "[INFO] Downloading backup from ${S3_SOURCE}..."
aws s3 cp "${S3_SOURCE}" "${LOCAL_RESTORE_PATH}"

if [ ! -f "${LOCAL_RESTORE_PATH}" ]; then
    echo "[ERROR] Failed to download backup file from ${S3_SOURCE}." >&2
    exit 1
fi

echo "[INFO] Restoring database ${POSTGRES_DB}..."

CONTAINER_ID="$(docker compose -f "${PROJECT_DIR}/docker-compose.yml" ps -q database 2>/dev/null || true)"

if [ -n "${CONTAINER_ID}" ]; then
    echo "[INFO] Performing pg_restore via Docker container ('database')..."
    cat "${LOCAL_RESTORE_PATH}" | docker compose -f "${PROJECT_DIR}/docker-compose.yml" exec -T \
        -e PGPASSWORD="${POSTGRES_PASSWORD}" \
        database pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists --no-owner --no-privileges || true
else
    echo "[INFO] Docker database container not detected. Performing direct pg_restore..."
    POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_restore -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists --no-owner --no-privileges "${LOCAL_RESTORE_PATH}" || true
fi

echo "[SUCCESS] Database restore process completed for ${POSTGRES_DB}."
