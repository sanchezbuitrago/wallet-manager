#!/bin/sh
set -e

if [ -z "${EVO_API_USER}" ] || [ -z "${EVO_API_PASSWORD}" ]; then
    echo "ERROR: EVO_API_USER y EVO_API_PASSWORD deben estar definidos"
    exit 1
fi

HASH=$(caddy hash-password --plaintext "${EVO_API_PASSWORD}")
sed -e "s|{{EVO_API_USER}}|${EVO_API_USER}|g" \
    -e "s|{{EVO_BASIC_AUTH_HASH}}|${HASH}|g" \
    /etc/caddy/Caddyfile.tmpl > /etc/caddy/Caddyfile

echo "Caddyfile generado con hash de contraseña"

exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
