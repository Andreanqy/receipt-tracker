#!/bin/sh

set -e

echo "Waiting for postgres..."

while ! python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('db', 5432))" 2>/dev/null; do
    sleep 1
done

echo "PostgreSQL started!"

if [ $# -eq 0 ]; then
    echo "Running alembic migrations..."
    alembic upgrade head
    echo "Starting uvicorn server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    exec "$@"
fi