#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"
MODE="${1:---dry-run}"

case "${MODE}" in
    --dry-run|--apply|--verify) ;;
    *)
        printf 'Usage: %s [--dry-run|--apply|--verify]\n' "$0" >&2
        exit 2
        ;;
esac

if [ "${MODE}" = "--apply" ] && [ "${CONFIRM_RECONCILE_APPLY:-}" != "yes" ]; then
    printf 'Reconciliation apply changes legacy mappings. Back up the database, then rerun with CONFIRM_RECONCILE_APPLY=yes.\n' >&2
    exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
    printf 'Missing %s. Run ./scripts/local-stack.sh first.\n' "${ENV_FILE}" >&2
    exit 1
fi

COMPOSE=(docker compose -f "${PROJECT_DIR}/docker-compose.yml" -f "${PROJECT_DIR}/docker-compose.dev.yml" --env-file "${ENV_FILE}")

for scope in fde java; do
    printf '[reconcile] scope=%s mode=%s\n' "${scope}" "${MODE}"
    "${COMPOSE[@]}" run --rm --no-deps api --reconcile-content --scope "${scope}" "${MODE}"
done
