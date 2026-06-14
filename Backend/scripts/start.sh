#!/bin/sh
set -e
echo "=== Alembic migrations ==="
alembic upgrade head
echo "=== Starting FastAPI ==="
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers ${WORKERS:-2} \
    --loop uvloop \
    --access-log
