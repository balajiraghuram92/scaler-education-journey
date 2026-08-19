#!/bin/sh

set -e

if [ "${DOMAIN_NAME}" = "localhost" ]; then
    echo "Starting Nginx in LOCAL HTTP mode"

    cp /etc/nginx/default.local.conf \
       /etc/nginx/conf.d/default.conf
else
    echo "Starting Nginx in PRODUCTION HTTPS mode for ${DOMAIN_NAME}"

    sed "s|\${DOMAIN_NAME}|${DOMAIN_NAME}|g" \
        /etc/nginx/default.conf.template \
        > /etc/nginx/conf.d/default.conf
fi

echo "Testing Nginx configuration..."
nginx -t

exec nginx -g "daemon off;"