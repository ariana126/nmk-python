#!/usr/bin/env bash
set -euo pipefail

# Postgres readiness is guaranteed by docker-compose's
# `depends_on: db: condition: service_healthy` — no wait loop needed here.
echo "[entrypoint] Running database migrations..."
alembic upgrade head

echo "[entrypoint] Starting: $*"
exec "$@"
