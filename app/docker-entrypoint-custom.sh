#!/bin/sh

set -e

DOMAIN_NAME="${DOMAIN_NAME:-localhost}"

if [ -n "${API_KEY:-}" ]; then
    case "${API_KEY}" in
        *[!A-Za-z0-9._~-]*)
            echo "API_KEY must contain only URL-safe token characters" >&2
            exit 1
            ;;
    esac
    escaped_api_key="$(printf '%s' "${API_KEY}" | sed 's/[&|]/\\&/g')"
else
    echo "WARNING: API_KEY is absent; using the legacy browser-provided header until the deployment workflow is upgraded" >&2
    escaped_api_key='$http_x_api_key'
fi
escaped_domain_name="$(printf '%s' "${DOMAIN_NAME}" | sed 's/[&|]/\\&/g')"

if [ "${DOMAIN_NAME}" = "localhost" ]; then
    echo "Starting Nginx in LOCAL HTTP mode"

    sed -e "s|\${API_KEY}|${escaped_api_key}|g" \
        /etc/nginx/default.local.conf \
        > /etc/nginx/conf.d/default.conf
else
    echo "Starting Nginx in PRODUCTION HTTPS mode for ${DOMAIN_NAME}"

    sed -e "s|\${DOMAIN_NAME}|${escaped_domain_name}|g" \
        -e "s|\${API_KEY}|${escaped_api_key}|g" \
        /etc/nginx/default.conf.template \
        > /etc/nginx/conf.d/default.conf
fi

echo "Testing Nginx configuration..."
nginx -t

exec nginx -g "daemon off;"
