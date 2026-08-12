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

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILENAME="${POSTGRES_DB}_backup_${TIMESTAMP}.dump"
TMP_DIR="$(mktemp -d)"
LOCAL_BACKUP_PATH="${TMP_DIR}/${BACKUP_FILENAME}"

cleanup() {
    rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "=========================================="
echo "Starting PostgreSQL Database Backup to S3"
echo "Database: ${POSTGRES_DB}"
echo "Timestamp: ${TIMESTAMP}"
echo "=========================================="

# Check if Docker compose database container is active
CONTAINER_ID="$(docker compose -f "${PROJECT_DIR}/docker-compose.yml" ps -q database 2>/dev/null || true)"

if [ -n "${CONTAINER_ID}" ]; then
    echo "[INFO] Performing pg_dump via running Docker container ('database')..."
    docker compose -f "${PROJECT_DIR}/docker-compose.yml" exec -T \
        -e PGPASSWORD="${POSTGRES_PASSWORD}" \
        database pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -F c -b -v > "${LOCAL_BACKUP_PATH}"
else
    echo "[INFO] Docker database container not detected. Performing direct pg_dump..."
    POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -F c -b -v -f "${LOCAL_BACKUP_PATH}"
fi

if [ ! -s "${LOCAL_BACKUP_PATH}" ]; then
    echo "[ERROR] Backup file creation failed or produced an empty file." >&2
    exit 1
fi

FILE_SIZE="$(du -h "${LOCAL_BACKUP_PATH}" | cut -f1)"
echo "[INFO] Local backup created successfully: ${BACKUP_FILENAME} (${FILE_SIZE})"

S3_TARGET="s3://${S3_BUCKET}/${S3_PREFIX}/${BACKUP_FILENAME}"
echo "[INFO] Uploading backup to ${S3_TARGET}..."
aws s3 cp "${LOCAL_BACKUP_PATH}" "${S3_TARGET}"

echo "[SUCCESS] Database backup uploaded to S3 successfully: ${S3_TARGET}"
